import argparse
from datetime import date

from crypto_fetch.api_client import fetch_crypto_price_data
from crypto_fetch.api_client import fetch_crypto_price
from crypto_fetch.formatter import format_price_output
from crypto_fetch.formatter import format_convert_output

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

    args = parser.parse_args()
        
    if args.command == "price":
        # convert ticker input to a list
        tickers = [t.strip().upper() for t in args.tickers.split(",")]
        # convert to comma-separated str
        tickers_str = ",".join(tickers)

        print(f"FETCHING PRICE DATA FOR TICKER(S): {tickers_str}")
        print(f"DATE: {date.today().strftime("%A, %B %d, %Y")}\n")

        data = fetch_crypto_price_data(tickers_str, args.currency)

        # print formatted output
        print(format_price_output(data, args.currency, args.verbose))

    elif args.command == "convert":
        amount_to_convert = args.amount
        ticker = args.ticker

        print("CONVERTING...")

        price = fetch_crypto_price(ticker, args.currency)
        converted_amount = amount_to_convert * price
        print(format_convert_output(ticker, args.currency, amount_to_convert, converted_amount))
