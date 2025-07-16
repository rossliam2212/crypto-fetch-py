import argparse

from crypto_fetch.api_client import fetch_crypto_price
from crypto_fetch.formatter import format_price_output

def main():
    """
    crypto-fetch entry point
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

    args = parser.parse_args()
    
    if args.command == "price":
        tickers = [t.strip().upper() for t in args.tickers.split(",")]
        tickers_str = ",".join(tickers)
        print(f"FETCHING DATA FOR TICKER(S): {tickers_str}")

        data = fetch_crypto_price(tickers_str, args.currency)
        print(format_price_output(data, args.currency, args.verbose))

    elif args.command == "convert":
        print("convert command")
