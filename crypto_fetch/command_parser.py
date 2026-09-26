import argparse
import logging

from crypto_fetch.api.api_client import APIConfig, BaseAPIClient
from crypto_fetch.api.cmc_api_client import CoinMarketCapAPIClient
from crypto_fetch.api.cg_api_client import CoinGeckoAPIClient
from crypto_fetch.config.config import get_api_provider_config
from crypto_fetch.commands.config_command import InitCommand, ValidateCommand, RecreateCommand
from crypto_fetch.constants import (
    CF_LOGGER, CF_VERSION,
    CMD_PRICE, CMD_CONVERT, CMD_CONFIG, CMD_PORTFOLIO,
    CMD_CONFIG_INIT, CMD_CONFIG_VALIDATE, CMD_CONFIG_RECREATE,
    CURRENCY_SYMBOL_MAP,
    PROVIDER_COINMARKETCAP, PROVIDER_COINGECKO,
    CONFIG_KEY_PROVIDER_NAME, CONFIG_KEY_PROVIDER_BASE_URL, CONFIG_KEY_PROVIDER_PRICE_EP,
)
from crypto_fetch.commands.convert_command import ConvertCommand
from crypto_fetch.exceptions import APIError, CryptoFetchError
from crypto_fetch.logger import setup_logger
from crypto_fetch.commands.portfolio_command import PortfolioCommand
from crypto_fetch.commands.price_command import PriceCommand

logger = logging.getLogger(CF_LOGGER)


def _parse_currency(value: str) -> str:
    """Argparse type callable — uppercases and validates a fiat currency code at parse time."""
    upper = value.upper()
    if upper not in CURRENCY_SYMBOL_MAP:
        raise argparse.ArgumentTypeError(
            f"Unknown currency '{upper}'. Supported: {', '.join(sorted(CURRENCY_SYMBOL_MAP))}"
        )
    return upper


def _parse_tickers(value: str) -> list:
    """Argparse type callable — splits a comma-separated ticker string into an uppercase list."""
    tickers = [t.strip().upper() for t in value.split(",") if t.strip()]
    if not tickers:
        raise argparse.ArgumentTypeError("No valid tickers provided")
    return tickers


def main():
    """
    crypto-fetch entry point
    """
    parser = argparse.ArgumentParser(
        prog="crypto-fetch",
        description="A command line tool to fetch cryptocurrency prices",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging (note: -d is used by --date on subcommands)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {CF_VERSION}")

    subparser = parser.add_subparsers(dest="command", required=True)
    _setup_price_command(subparser)
    _setup_convert_command(subparser)
    _setup_config_command(subparser)
    _setup_portfolio_command(subparser)

    args: argparse.Namespace = parser.parse_args()

    setup_logger(args.debug)
    logger.debug("Debug logs enabled")

    try:
        if args.command == CMD_PRICE:
            command = PriceCommand(
                client=None,
                tickers=args.tickers,
                currency=args.currency,
                provider=args.provider,
                verbose=args.verbose,
                show_date=args.date,
            )
            command._validate()
            command.client = _create_api_client(command.provider)
            command._execute()
        elif args.command == CMD_CONVERT:
            command = ConvertCommand(
                client=None,
                amount=args.amount,
                ticker=args.ticker,
                currency=args.currency,
                provider=args.provider,
                verbose=args.verbose,
                show_date=args.date,
            )
            command._validate()
            command.client = _create_api_client(command.provider)
            command._execute()
        elif args.command == CMD_CONFIG:
            if args.config_action == CMD_CONFIG_INIT:
                InitCommand(force=getattr(args, "force", False)).run()
            elif args.config_action == CMD_CONFIG_VALIDATE:
                ValidateCommand(path=getattr(args, "path", None)).run()
            elif args.config_action == CMD_CONFIG_RECREATE:
                RecreateCommand(force=getattr(args, "force", False)).run()
        elif args.command == CMD_PORTFOLIO:
            command = PortfolioCommand(
                client=None,
                portfolio_file=args.file,
                currency=args.currency,
                provider=args.provider,
                verbose=args.verbose,
                show_date=args.date,
            )
            command._validate()
            command.client = _create_api_client(command.provider)
            command._execute()
    except CryptoFetchError as ex:
        logger.error(f"'{args.command}' command failed. Error: {ex}")
    except Exception as ex:
        logger.debug("Unexpected error", exc_info=True)
        logger.error(f"Unexpected error: {ex}")


def _setup_price_command(subparser: argparse._SubParsersAction) -> None:
    """Sets up the price subcommand."""
    price_parser = subparser.add_parser(
        CMD_PRICE,
        help="Fetch the price of a cryptocurrency",
        epilog="Examples:\n  crypto-fetch price BTC\n  crypto-fetch price BTC,ETH -c USD -v\n  crypto-fetch price BTC -p coingecko",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    price_parser.add_argument("tickers", type=_parse_tickers, help="Comma-separated tickers e.g. BTC or BTC,ETH,XRP")
    price_parser.add_argument("-c", "--currency", type=_parse_currency, default=None, help="Fiat currency (default: from config)")
    _add_output_flags(price_parser)
    _add_provider_arg(price_parser)


def _setup_convert_command(subparser: argparse._SubParsersAction) -> None:
    """Sets up the convert subcommand."""
    convert_parser = subparser.add_parser(
        CMD_CONVERT,
        help="Convert a cryptocurrency amount to fiat",
        epilog="Examples:\n  crypto-fetch convert 1.5 -t BTC\n  crypto-fetch convert 100 -t ETH -c GBP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    convert_parser.add_argument("amount", type=float, help="Amount of cryptocurrency to convert")
    convert_parser.add_argument("-t", "--ticker", required=True, help="Cryptocurrency ticker e.g. BTC")
    convert_parser.add_argument("-c", "--currency", type=_parse_currency, default=None, help="Fiat currency (default: from config)")
    _add_output_flags(convert_parser)
    _add_provider_arg(convert_parser)


def _setup_config_command(subparser: argparse._SubParsersAction) -> None:
    """Sets up the config subcommand with nested sub-subparsers for each action."""
    config_parser = subparser.add_parser(CMD_CONFIG, help="Manage configuration")
    config_sub = config_parser.add_subparsers(dest="config_action", required=True)

    init_parser = config_sub.add_parser(CMD_CONFIG_INIT, help="Create a new config file")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing config file")

    validate_parser = config_sub.add_parser(CMD_CONFIG_VALIDATE, help="Validate the config file")
    validate_parser.add_argument("--path", default=None, metavar="PATH",
                                 help="Path to a config file to validate (default: ~/.crypto-fetch-py/config.yaml)")

    recreate_parser = config_sub.add_parser(CMD_CONFIG_RECREATE, help="Restore config file to defaults")
    recreate_parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")


def _setup_portfolio_command(subparser: argparse._SubParsersAction) -> None:
    """Sets up the portfolio subcommand."""
    portfolio_parser = subparser.add_parser(
        CMD_PORTFOLIO,
        help="Display portfolio holdings with live prices",
        epilog="Examples:\n  crypto-fetch portfolio portfolio.yaml\n  crypto-fetch portfolio holdings.yaml -c GBP -v",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    portfolio_parser.add_argument("file", help="Path to portfolio YAML or txt file")
    portfolio_parser.add_argument("-c", "--currency", type=_parse_currency, default=None, help="Fiat currency (default: from config)")
    _add_output_flags(portfolio_parser)
    _add_provider_arg(portfolio_parser)


def _add_output_flags(parser: argparse.ArgumentParser) -> None:
    """Adds shared output flags (-v/--verbose, -d/--date) to a subcommand parser."""
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("-d", "--date", action="store_true", help="Display the current timestamp in the output")


def _add_provider_arg(parser: argparse.ArgumentParser) -> None:
    """Adds the shared --provider argument to a subcommand parser."""
    parser.add_argument(
        "-p", "--provider",
        choices=[PROVIDER_COINMARKETCAP, PROVIDER_COINGECKO],
        default=None,
        help="API provider to use (default: from config)",
    )


def _create_api_client(provider: str) -> BaseAPIClient:
    """
    Creates the appropriate API client for an already-resolved provider name.

    :param provider: The resolved provider name.
    :return: The API client.
    :raises APIError: If the provider is not recognised.
    """
    if provider == PROVIDER_COINGECKO:
        return CoinGeckoAPIClient(_create_api_config(PROVIDER_COINGECKO))
    if provider == PROVIDER_COINMARKETCAP:
        return CoinMarketCapAPIClient(_create_api_config(PROVIDER_COINMARKETCAP))
    raise APIError(f"Unknown provider: '{provider}'")


def _create_api_config(provider: str) -> APIConfig:
    """
    Builds an APIConfig from the provider's configuration in the config file.

    :param provider: The provider name.
    :return: The APIConfig for the given provider.
    """
    logger.debug(f"Creating API client for provider: '{provider}'")
    config = get_api_provider_config(provider)

    return APIConfig(
        name=config.get(CONFIG_KEY_PROVIDER_NAME, provider),
        base_url=config.get(CONFIG_KEY_PROVIDER_BASE_URL, ""),
        price_endpoint=config.get(CONFIG_KEY_PROVIDER_PRICE_EP, ""),
    )
