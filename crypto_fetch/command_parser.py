import argparse
import logging
from colorama import just_fix_windows_console # type: ignore

from crypto_fetch.api_client import APIConfig, BaseAPIClient, CoinMarketCapAPIClient, CoinGeckoAPIClient
from crypto_fetch.constants import *
from crypto_fetch.logger import setup_logger
from crypto_fetch.config import get_api_provider_config
from crypto_fetch.price_command import PriceCommand
from crypto_fetch.convert_command import ConvertCommand
from crypto_fetch.config_command import ConfigCommand

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

    setup_logger(args.debug)
    logger.debug("Debug logs enabled")

    client = _create_api_client(args)
    try:
        if args.command == CMD_PRICE:
            command = PriceCommand(client, args.tickers, args.currency, args.provider, args.verbose, args.date)
            command.run()
        elif args.command == CMD_CONVERT:
            command = ConvertCommand(client, args.amount, args.ticker, args.currency, args.date, args.provider)
            command.run()
        elif args.command == CMD_CONFIG:
            command = ConfigCommand(args.action)
            command.run()
    except Exception as ex:
        logger.error(f"{args.command} command failed. Error: {ex}")


def _setup_price_command(subparser: argparse._SubParsersAction) -> None:
    price_parser = subparser.add_parser(CMD_PRICE, help="Fetch the price of a cryptocurrency")
    price_parser.add_argument("tickers", help="Comma-separated tickers (e.g. BTC,XRP)")
    price_parser.add_argument("-c", "--currency", default=None, help="Currency (default: EUR)")
    price_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    price_parser.add_argument("-d", "--date", action="store_true", help="Display the date/time in the output")
    price_parser.add_argument("-p", "--provider", choices=[PROVIDER_COINMARKETCAP, PROVIDER_COINGECKO], default=None, help="Choose API provider (default: coinmarketcap)")


def _setup_convert_command(subparser: argparse._SubParsersAction) -> None:
    convert_parser = subparser.add_parser(CMD_CONVERT, help="Convert crypto to fiat")
    convert_parser.add_argument("amount", help="Amount to convert")
    convert_parser.add_argument("-t", "--ticker", required=True, help="Target cryptocurrency")
    convert_parser.add_argument("-c", "--currency", default=None, help="Currency (default: EUR)")
    convert_parser.add_argument("-d", "--date", action="store_true", help="Display the date/time in the output")
    convert_parser.add_argument("-p", "--provider", choices=[PROVIDER_COINMARKETCAP, PROVIDER_COINGECKO], default=None, help="Choose API provider (default: coinmarketcap)")


def _setup_config_command(subparser: argparse._SubParsersAction) -> None:
    config_parser = subparser.add_parser(CMD_CONFIG, help="Manage configuration")
    config_parser.add_argument("action", choices=[CMD_CONFIG_INIT, CMD_CONFIG_VALIDATE, CMD_CONFIG_RECREATE], help="Config action")


def _setup_portfolio_command(subparser: argparse._SubParsersAction) -> None:
    portfolio_parser = subparser.add_parser(CMD_PORTFOLIO, help="Manage configuration")
    portfolio_parser.add_argument("-f", "--file", required=True, help="File containing the portfolio")
    portfolio_parser.add_argument("-o", "--output", required=False, action="store_true", help="Output file")


def _create_api_client(args: argparse.Namespace) -> BaseAPIClient:
    if args.command == CMD_CONFIG:
        return None

    provider = getattr(args, "provider", None) or PROVIDER_COINMARKETCAP
    if provider == PROVIDER_COINGECKO:
        return CoinGeckoAPIClient(_create_api_config(PROVIDER_COINGECKO))
    return CoinMarketCapAPIClient(_create_api_config(PROVIDER_COINMARKETCAP))


def _create_api_config(provider: str) -> APIConfig:
    logger.debug(f"Creating API client for provider: '{provider}'")
    config = get_api_provider_config(provider)
    return APIConfig(
        name=config.get(CONFIG_KEY_PROVIDER_NAME, provider),
        base_url=config.get(CONFIG_KEY_PROVIDER_BASE_URL, ""),
        price_endpoint=config.get(CONFIG_KEY_PROVIDER_PRICE_EP, ""),
    )