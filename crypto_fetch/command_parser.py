import argparse
from datetime import datetime
from typing import List

from crypto_fetch.api_client import APIConfig
from crypto_fetch.api_client import BaseAPIClient
from crypto_fetch.api_client import CoinMarketCapAPIClient
from crypto_fetch.formatter import format_price_output
from crypto_fetch.formatter import format_convert_output
from crypto_fetch.constants import CMC_API_BASE
from crypto_fetch.constants import CMC_API_LATEST_EP
from crypto_fetch.constants import CMC_API_KEY_ENV_VAR

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
    parser = argparse.ArgumentParser(prog="crypto-fetch", description="A command line tool to fetch cryptocurrency prices")
    subparser = parser.add_subparsers(dest="command", required=True)

    # price subcommand
    price_parser = subparser.add_parser("price", help="Fetch the price of a cryptocurrency")
    price_parser.add_argument("tickers", help="Comma-separated tickers (e.g. BTC,XRP)")
    price_parser.add_argument("-c", "--currency", default="EUR", help="Currency (default: EUR)")
    price_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    price_parser.add_argument("-d", "--date", action="store_true", help="Display the date/time in the output")

    # convert command
    convert_parser = subparser.add_parser("convert", help="Convert fiat to crypto")
    convert_parser.add_argument("amount", type=float, help="Amount to convert")
    convert_parser.add_argument("-t", "--ticker", required=True, help="Target cryptocurrency")
    convert_parser.add_argument("-c", "--currency", default="EUR", help="Currency (default: EUR)")
    convert_parser.add_argument("-d", "--date", action="store_true", help="Display the date/time in the output")
    convert_parser.add_argument("-f", "--file", help="Portfolio file (future feature)")

    args: argparse.Namespace = parser.parse_args()

    cmc_api_config: APIConfig = APIConfig(
        base_url=CMC_API_BASE,
        latest_endpoint=CMC_API_LATEST_EP,
        api_key_env_var=CMC_API_KEY_ENV_VAR
    )
    client = CoinMarketCapAPIClient(cmc_api_config)

    try:
        if args.command == "price":
            _handle_price_command(args, client)
        elif args.command == "convert":
            _handle_convert_command(args, client)
    except Exception as ex:
        print(f"[ERROR] {str(ex)}")

def _handle_price_command(args: argparse.Namespace, client: BaseAPIClient):
    """
    Handles the price command.

    :param args: The command line args.
    :param client: The API client.
    """
    tickers: List[str] = [t.strip().upper() for t in args.tickers.split(",")]
    tickers_str: str = ",".join(tickers) # convert to comma-separated str

    print(f"FETCHING PRICE DATA FOR TICKER(S): {_add_dollar_symbol_to_tickers(tickers)}...")
    if args.date:
        print(f"Timestamp: {_get_date()}\n")

    data = client.fetch_multiple_price_data(tickers_str, args.currency)
    print(format_price_output(data, args.currency, args.verbose))

def _handle_convert_command(args: argparse.Namespace, client: BaseAPIClient):
    """
    Handles the convert command.

    :param args: The command line args.
    :param client: The API client.
    """
    amount_to_convert: float = args.amount
    ticker: str = args.ticker.upper()

    if args.date:
        print(f"Timestamp: {_get_date()}")

    price: float = client.fetch_single_price_data(ticker, args.currency)
    converted_amount: float = amount_to_convert * price
    print(format_convert_output(ticker, args.currency, amount_to_convert, converted_amount))

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
