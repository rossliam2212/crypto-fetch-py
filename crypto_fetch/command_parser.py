import argparse
import logging
from colorama import just_fix_windows_console
from datetime import datetime
from typing import List

from crypto_fetch.api_client import APIConfig
from crypto_fetch.api_client import BaseAPIClient
from crypto_fetch.api_client import CoinMarketCapAPIClient
from crypto_fetch.api_client import CoinGeckoAPIClient
from crypto_fetch.formatter import format_price_output
from crypto_fetch.formatter import format_convert_output
from crypto_fetch.constants import CMC_API_NAME
from crypto_fetch.constants import CMC_API_BASE
from crypto_fetch.constants import CMC_API_LATEST_EP
from crypto_fetch.constants import CMC_API_KEY_ENV_VAR
from crypto_fetch.constants import CG_API_NAME
from crypto_fetch.constants import CG_API_BASE
from crypto_fetch.constants import CG_API_LATEST_EP
from crypto_fetch.constants import CG_API_KEY_ENV_VAR
from crypto_fetch.constants import CF_VERSION
from crypto_fetch.constants import CURRENCY_SYMBOL_MAP
from crypto_fetch.logger import setup_logger
from crypto_fetch.config import init_config, get_default_fiat_currency, get_default_provider

logger = logging.getLogger("crypto_fetch")

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

    setup_logger(args.debug)
    logger.debug("Debugs logs enabled")

    if args.command == "config":
        if args.action == "init":
            init_config()
        return

    client = _create_api_client(args)

    try:
        if args.command == "price":
            _handle_price_command(args, client)
        elif args.command == "convert":
            _handle_convert_command(args, client)
    except Exception as ex:
        logger.error(f"{str(ex)}... {ex.args}")

def _setup_price_command(subparser: argparse._SubParsersAction) -> None:
    """
    Sets up the price command.
    
    :param subparser: The subparser to add the price command to.
    """
    price_parser = subparser.add_parser("price", help="Fetch the price of a cryptocurrency")
    price_parser.add_argument("tickers", help="Comma-separated tickers (e.g. BTC,XRP)")
    price_parser.add_argument("-c", "--currency", default=None, help="Currency (default: EUR)")
    price_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    price_parser.add_argument("-d", "--date", action="store_true", help="Display the date/time in the output")
    price_parser.add_argument("-p", "--provider", choices=["coinmarketcap", "coingecko"], default=None, help="Choose API provider (default: coinmarketcap)")

def _setup_convert_command(subparser: argparse._SubParsersAction) -> None:
    """
    Sets up the convert command.
    
    :param subparser: The subparser to add the convert command to.
    """
    convert_parser = subparser.add_parser("convert", help="Convert crypto to fiat")
    convert_parser.add_argument("amount", type=_validate_positive_amount, help="Amount to convert")
    convert_parser.add_argument("-t", "--ticker", required=True, help="Target cryptocurrency")
    convert_parser.add_argument("-c", "--currency", default=None, help="Currency (default: EUR)")
    convert_parser.add_argument("-d", "--date", action="store_true", help="Display the date/time in the output")
    convert_parser.add_argument("-p", "--provider", choices=["coinmarketcap", "coingecko"], default="coinmarketcap", help="Choose API provider (default: coinmarketcap)")
    convert_parser.add_argument("-f", "--file", help="Portfolio file (#TODO)")

def _setup_config_command(subparser: argparse._SubParsersAction) -> None:
    """
    Sets up the config command.
    
    :param subparser: The subparser to add the config command to.
    """
    config_parser = subparser.add_parser("config", help="Initialize config file")
    config_parser.add_argument("action", choices=["init"], help="Config action")

def _handle_price_command(args: argparse.Namespace, client: BaseAPIClient):
    """
    Handles the price command.

    :param args: The command line args.
    :param client: The API client.
    """
    tickers: List[str] = [t.strip().upper() for t in args.tickers.split(",")]
    tickers_str: str = ",".join(tickers) # convert to comma-separated str
    currency: str = _get_fiat_currency(args)

    logger.info(f"FETCHING PRICE DATA FOR TICKER(S): {_add_dollar_symbol_to_tickers(tickers)}...")
    if args.date:
        logger.info(f"Timestamp: {_get_date()}")

    data = client.fetch_multiple_price_data(tickers_str, currency)
    logger.info(format_price_output(data, currency, client.config.base_url, args.verbose))

def _handle_convert_command(args: argparse.Namespace, client: BaseAPIClient):
    """
    Handles the convert command.

    :param args: The command line args.
    :param client: The API client.
    """
    amount_to_convert: float = args.amount
    ticker: str = args.ticker.upper()
    currency: str = _get_fiat_currency(args)

    logger.info(f"CONVERTING {amount_to_convert} ${ticker} to {currency}...")
    if args.date:
        logger.info(f"Timestamp: {_get_date()}")

    price: float = client.fetch_single_price_data(ticker, currency)
    converted_amount: float = amount_to_convert * price
    logger.info(format_convert_output(ticker, currency, amount_to_convert, converted_amount))

def _create_api_client(args: argparse.Namespace) -> BaseAPIClient:
    """
    Creates an API client based on the provider.

    :param provider: The API provider name.

    :return: the API client.
    """
    provider = _get_api_provider(args)

    if provider == CG_API_NAME:
        return CoinGeckoAPIClient(_create_cg_config())
    return CoinMarketCapAPIClient(_create_cmc_config())

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
        raise argparse.ArgumentTypeError(f"Amount must be positive. Supplied: '{amount}'")
    return amount

def _get_api_provider(args: argparse.Namespace) -> str:
    """
    Gets the API provider from args or config default.
    
    :param args: The command line args.
    
    :return: The validated API provider name.
    """
    if args.provider is None:
        logger.debug(f"API provider not specified. Using default")
        provider = get_default_provider()
    else:
        provider = args.provider

    provider: str = _validate_provider(provider)
    return provider

def _validate_provider(value: str) -> str:
    """
    Validates the supplied API provider.
    
    :param value: The API provider name.
    
    :return: The validated provider name.
    :raises argparse.ArgumentTypeError: if the validation fails.
    """
    logger.debug(f"Validating provider: '{value.lower()}'")
    provider = value.lower()

    if provider not in [CMC_API_NAME, CG_API_NAME]:
        raise argparse.ArgumentTypeError(f"Unknown/Unsupported provider supplied: '{provider}'")
    return provider

def _get_fiat_currency(args: argparse.Namespace) -> str:
    """
    Gets the fiat currency from args or config default.
    
    :param args: The command line args.
    
    :return: The validated fiat currency code.
    """
    if args.currency is None:
        logger.debug(f"Fiat currency not specified. Using default")
        args.currency = get_default_fiat_currency()

    currency: str = _validate_currency(args.currency)
    return currency

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
        raise argparse.ArgumentTypeError(f"Unknown/Unsupported currency supplied: '{currency}'")
    return currency

def _create_cmc_config() -> APIConfig:
    """
    Creates the default CoinMarketCap API configuration.

    :return: the default CoinMarketCap API configuration.
    """
    return APIConfig(
        name=CMC_API_NAME,
        base_url=CMC_API_BASE,
        latest_endpoint=CMC_API_LATEST_EP,
        api_key_env_var=CMC_API_KEY_ENV_VAR,
    )

def _create_cg_config() -> APIConfig:
    """
    Creates the default CoinGecko API configuration.

    :return: the default CoinGecko API configuration.
    """
    return APIConfig(
        name=CG_API_NAME,
        base_url=CG_API_BASE,
        latest_endpoint=CG_API_LATEST_EP,
        api_key_env_var=CG_API_KEY_ENV_VAR,
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