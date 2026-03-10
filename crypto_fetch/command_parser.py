import argparse
import logging
import sys
import yaml  # type: ignore
from colorama import just_fix_windows_console # type: ignore
from datetime import datetime
from typing import List

from crypto_fetch.api_client import APIConfig
from crypto_fetch.api_client import BaseAPIClient
from crypto_fetch.api_client import CoinMarketCapAPIClient
from crypto_fetch.api_client import CoinGeckoAPIClient
from crypto_fetch.formatter import format_price_output
from crypto_fetch.formatter import format_convert_output
from crypto_fetch.constants import *
from crypto_fetch.logger import setup_logger
from crypto_fetch.config import (
    init_api_config_file,
    get_default_fiat_currency,
    get_default_api_provider,
    get_api_provider_config,
    load_api_config_from_file,
    save_api_config_to_file,
    CONFIG_FILE,
    DEFAULT_CONFIG
)
from crypto_fetch.config_validator import validate_config

logger = logging.getLogger(CF_LOGGER)

def main():
    """
    crypto-fetch entry point

    Usage:
    - price command
        $ crypto-fetch price XRP 
        $ crypto-fetch price BTC,XLM -c USD
        $ crypto-fetch price hbar --currency aud

    - convert command
        $ crypto-fetch convert 50 -t BTC
        $ crypto-fetch convert 1000 --ticker XRP --currency CAD

    - config command
        $ crypto-fetch config init
    """
    just_fix_windows_console()

    parser = argparse.ArgumentParser(prog="crypto-fetch", description="A command line tool to fetch cryptocurrency prices")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--version", action='version', version=f"%(prog)s {CF_VERSION}")

    subparser = parser.add_subparsers(dest="command", required=True)
    _setup_price_command(subparser)
    _setup_convert_command(subparser)
    _setup_config_command(subparser)

    args: argparse.Namespace = parser.parse_args()
    args = _validate_parsed_commands(args)
    if args is None: # config command exit
        return

    client = _create_api_client(args)
    try:
        if args.command == CMD_PRICE:
            _handle_price_command(args, client)
        elif args.command == CMD_CONVERT:
            _handle_convert_command(args, client)
    except Exception as ex:
        logger.error(f"{args.command} command failed. Error: {ex}")

def _setup_price_command(subparser: argparse._SubParsersAction) -> None:
    """
    Sets up the price command.
    
    :param subparser: The subparser to add the price command to.
    """
    price_parser = subparser.add_parser(CMD_PRICE, help="Fetch the price of a cryptocurrency")
    price_parser.add_argument("tickers", help="Comma-separated tickers (e.g. BTC,XRP)")
    price_parser.add_argument("-c", "--currency", default=None, help="Currency (default: EUR)")
    price_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    price_parser.add_argument("-d", "--date", action="store_true", help="Display the date/time in the output")
    price_parser.add_argument("-p", "--provider", choices=[PROVIDER_COINMARKETCAP, PROVIDER_COINGECKO], default=None, help="Choose API provider (default: coinmarketcap)")

def _setup_convert_command(subparser: argparse._SubParsersAction) -> None:
    """
    Sets up the convert command.
    
    :param subparser: The subparser to add the convert command to.
    """
    convert_parser = subparser.add_parser(CMD_CONVERT, help="Convert crypto to fiat")
    convert_parser.add_argument("amount", type=_validate_positive_amount, help="Amount to convert")
    convert_parser.add_argument("-t", "--ticker", required=True, help="Target cryptocurrency")
    convert_parser.add_argument("-c", "--currency", default=None, help="Currency (default: EUR)")
    convert_parser.add_argument("-d", "--date", action="store_true", help="Display the date/time in the output")
    convert_parser.add_argument("-p", "--provider", choices=[PROVIDER_COINMARKETCAP, PROVIDER_COINGECKO], default=None, help="Choose API provider (default: coinmarketcap)")
    convert_parser.add_argument("-f", "--file", help="Portfolio file (#TODO)")

def _setup_config_command(subparser: argparse._SubParsersAction) -> None:
    """
    Sets up the config command.
    
    :param subparser: The subparser to add the config command to.
    """
    config_parser = subparser.add_parser(CMD_CONFIG, help="Manage configuration")
    config_parser.add_argument("action", choices=[CMD_CONFIG_INIT, CMD_CONFIG_VALIDATE, CMD_CONFIG_RECREATE], help="Config action")

def _handle_price_command(args: argparse.Namespace, client: BaseAPIClient):
    """
    Handles the price command.

    :param args: The command line args.
    :param client: The API client.
    """
    tickers = args.tickers.split(",")
    
    logger.info(f"FETCHING PRICE DATA FOR TICKER(S): {_add_dollar_symbol_to_tickers(tickers)}...")
    if args.date:
        logger.info(f"Timestamp: {_get_date()}")

    data = client.fetch_multiple_price_data(args.tickers, args.currency)
    logger.info(format_price_output(data, args.currency, client.config.base_url, args.verbose))

def _handle_convert_command(args: argparse.Namespace, client: BaseAPIClient):
    """
    Handles the convert command.

    :param args: The command line args.
    :param client: The API client.
    """
    logger.info(f"CONVERTING {args.amount} ${args.ticker} to {args.currency}...")
    if args.date:
        logger.info(f"Timestamp: {_get_date()}")

    price: float = client.fetch_single_price_data(args.ticker, args.currency)
    converted_amount: float = args.amount * price
    logger.info(format_convert_output(args.ticker, args.currency, args.amount, converted_amount))

def _validate_parsed_commands(args: argparse.Namespace) -> argparse.Namespace:
    """
    Validates the parsed arguments. 
    Handles the config command if supplied.

    :param args: The command line args.
    :return: The validated command line args.
    """
    # enable debug logs 
    setup_logger(args.debug)
    logger.debug("Debug logs enabled")

    logger.debug(f"Validating parsed arguments...")

    # handle config command & initialization
    if args.command == CMD_CONFIG:
        _handle_config_command_action(args.action)
        return None
    
    # validate currency or get default
    if args.currency is None:
        args.currency = get_default_fiat_currency()
        logger.debug(f"Fiat currency not specified. Using default: '{args.currency}'")
    args.currency = _validate_currency(args.currency)

    # validate provider or get default
    if args.provider is None:
        args.provider = get_default_api_provider()
        logger.debug(f"API provider not specified. Using default: '{args.provider}'")
    args.provider = _validate_provider(args.provider)
    
    # prepare for price/convert command 
    if args.command == CMD_PRICE:
        tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
        if not tickers:
            raise argparse.ArgumentTypeError(f"No valid tickers provided. Got: {tickers}")
        
        _validate_tickers(tickers)
        args.tickers = ",".join(tickers)
    elif args.command == CMD_CONVERT:
        args.ticker = args.ticker.strip().upper()
        _validate_tickers([args.ticker])
    
    return args

def _handle_config_command_action(action: str) -> None:
    if action == CMD_CONFIG_INIT:
        init_api_config_file()
    elif action == CMD_CONFIG_VALIDATE:
        exit_code = _validate_config_file()
        import sys
        sys.exit(exit_code)
    elif action == CMD_CONFIG_RECREATE:
        _recreate_config_file()

def _create_api_client(args: argparse.Namespace) -> BaseAPIClient:
    """
    Creates an API client based on the provider.

    :param args: The command line args.

    :return: the API client.
    """
    if args.provider == PROVIDER_COINGECKO:
        return CoinGeckoAPIClient(_create_api_config(PROVIDER_COINGECKO))
    return CoinMarketCapAPIClient(_create_api_config(PROVIDER_COINMARKETCAP))

def _validate_positive_amount(value: str) -> float:
    """
    Validates the amount supplied for the convert command is positive.

    :param value: The amount supplied to the convert command.

    :return: the amount supplied converted to a float.
    """
    try:
        amount = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid amount: '{value}' is not a number")
    
    if amount <= 0:
        raise argparse.ArgumentTypeError(f"Amount must be positive. Received: '{amount}'")
    return amount

def _validate_provider(value: str) -> str:
    """
    Validates the supplied API provider.
    
    :param value: The API provider name.
    
    :return: The validated provider name.
    :raises argparse.ArgumentTypeError: if the validation fails.
    """
    logger.debug(f"Validating provider: '{value.lower()}'")
    provider = value.lower()

    if provider not in [PROVIDER_COINMARKETCAP, PROVIDER_COINGECKO]:
        raise argparse.ArgumentTypeError(f"Unknown/Unsupported provider. Received: '{provider}'")
    return provider

def _validate_currency(value: str) -> str:
    """
    Validates the supplied fiat currency symbol.

    :param value: The fiat currency symbol.

    :return: The validated fiat currency symbol.
    :raises argparse.ArgumentTypeError: if the validation fails.
    """
    logger.debug(f"Validating fiat currency: '{value.upper()}'")
    currency = value.upper()

    if currency not in CURRENCY_SYMBOL_MAP:
        raise argparse.ArgumentTypeError(f"Unknown/Unsupported currency. Received '{currency}'")
    return currency

def _validate_tickers(tickers: List[str]) -> None:
    """
    Validates the supplied cryptocurrency tickers.
    
    :param tickers: List of ticker symbols.
    
    :raises argparse.ArgumentTypeError: if any ticker is invalid.
    """
    logger.debug(f"Validing supplied crypto tickers: {tickers}")
    invalid_tickers = [t for t in tickers if t not in SUPPORTED_CRYPTO_TICKERS]
    
    if invalid_tickers:
        raise argparse.ArgumentTypeError(f"Unknown/Unsupported ticker(s). Received: {', '.join(invalid_tickers)}")

def _create_api_config(provider: str) -> APIConfig:
    """
    Creates API configuration from config file.

    :param provider: The provider name.
    :return: the API configuration.
    """
    logger.debug(f"Creating API client for provider: '{provider}'")
    config = get_api_provider_config(provider)
    
    return APIConfig(
        name=config.get(CONFIG_KEY_PROVIDER_NAME, provider),
        base_url=config.get(CONFIG_KEY_PROVIDER_BASE_URL, ""),
        price_endpoint=config.get(CONFIG_KEY_PROVIDER_PRICE_EP, ""),
    )

def _get_date() -> str:
    """
    Gets the current date/time in the following format: 2025-07-29 21:07:00.

    :return: The current date/time as a str.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _add_dollar_symbol_to_tickers(tickers: List[str]) -> str:
    """
    Prefixes each ticker symbol in a given list with a '$'.

    :param tickers: The list of tickers symbols.

    :return: A comma separated str of tickers with the '$' prefix.
    """
    return ",".join(f"${ticker}" for ticker in tickers)


def _validate_config_file() -> int:
    """Validates the configuration file and reports errors.
    
    :returns: 0 if valid, 1 if invalid
    """
    # Load config directly without fallback to defaults
    if not CONFIG_FILE.exists():
        logger.error("Config file not found. Run 'crypto-fetch config init' to create")
        return 1
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            
        if config is None or not isinstance(config, dict):
            logger.error("Config file is empty or invalid ❌")
            logger.info("Run 'crypto-fetch config recreate' to restore defaults")
            return 1
    except yaml.YAMLError as ex:
        logger.error(f"Config file has YAML syntax errors: {ex} ❌")
        logger.info("Run 'crypto-fetch config recreate' to restore defaults")
        return 1
    except Exception as ex:
        logger.error(f"Failed to read config file: {ex} ❌")
        return 1
    
    # Validate the loaded config
    errors = validate_config(config)
    
    if not errors:
        logger.info("API config is valid ✅")
        return 0
    
    logger.error("API config validation failed ❌")
    for error in errors:
        logger.error(f"  - {error}")
    
    logger.info("\nRun 'crypto-fetch config recreate' to restore defaults")
    return 1

def _recreate_config_file() -> None:
    """Recreates the config file with defaults."""
    logger.info("Recreating config file with defaults...")
    save_api_config_to_file(DEFAULT_CONFIG)
    logger.info(f"Config file recreated at: '{CONFIG_FILE}' ✅")
    logger.info("*** Remember to add your API keys ***")