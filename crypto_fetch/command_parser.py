import argparse
from datetime import date
from typing import List

from crypto_fetch.api_client import APIConfig
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

    - convert convert
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

    # convert command
    convert_parser = subparser.add_parser("convert", help="Convert fiat to crypto")
    convert_parser.add_argument("amount", type=float, help="Amount to convert")
    convert_parser.add_argument("-t", "--ticker", required=True, help="Target cryptocurrency")
    convert_parser.add_argument("-c", "--currency", default="EUR", help="Currency (default: EUR)")
    convert_parser.add_argument("-f", "--file", help="Portfolio file (future feature)")

    args: argparse.Namespace = parser.parse_args()

    todays_date: str = date.today().strftime("%A, %B %d, %Y")

    cmc_api_config: APIConfig = APIConfig(
        base_url=CMC_API_BASE,
        latest_endpoint=CMC_API_LATEST_EP,
        api_key_env_var=CMC_API_KEY_ENV_VAR
    )
    client = CoinMarketCapAPIClient(cmc_api_config)
        
    if args.command == "price":
        # convert ticker input to a list
        tickers: List[str] = [t.strip().upper() for t in args.tickers.split(",")]
        # convert to comma-separated str
        tickers_str: str = ",".join(tickers)

        print(f"DATE: {todays_date}")
        print(f"FETCHING PRICE DATA FOR TICKER(S): {_add_dollar_symbol_to_tickers(tickers)}...\n")

        try:
            data = client.fetch_multiple_price_data(tickers_str, args.currency)
            # print formatted output
            print(format_price_output(data, args.currency, args.verbose))
        except Exception as ex:
            print(f"[ERROR] {str(ex)}")
    elif args.command == "convert":
        amount_to_convert: float = args.amount
        ticker: str = args.ticker.upper()

        print(f"DATE: {todays_date}")
        print("CONVERTING...\n")

        try:
            price: float = client.fetch_single_price_data(ticker, args.currency)
            converted_amount: float = amount_to_convert * price
            print(format_convert_output(ticker, args.currency, amount_to_convert, converted_amount))
        except Exception as ex:
            print(f"[ERROR] {str(ex)}")

def _add_dollar_symbol_to_tickers(tickers: List[str]) -> str:
    """
    Prefixes each ticker symbol in a given list with a '$'.

    :param tickers: The list of tickers symbols.

    :return: A comma separated string of tickers with the '$' prefix.
    """
    return ",".join(f"${ticker}" for ticker in tickers)
