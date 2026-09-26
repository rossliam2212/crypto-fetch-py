import logging
from typing import List

from crypto_fetch.api.api_client import BaseAPIClient
from crypto_fetch.api.formatter import format_price_output, print_output
from crypto_fetch.commands.command import Command
from crypto_fetch.commands.command_utils import get_timestamp, resolve_currency, resolve_provider, validate_tickers
from crypto_fetch.constants import CF_LOGGER
from crypto_fetch.exceptions import CommandError

logger = logging.getLogger(CF_LOGGER)


class PriceCommand(Command):
    """Fetch cryptocurrency prices"""

    def __init__(self, client: BaseAPIClient, tickers: list, currency: str, provider: str, verbose: bool, show_date: bool = False):
        """
        :param client: The API client to use for fetching price data.
        :param tickers: List of uppercase ticker symbols (pre-parsed by argparse).
        :param currency: The fiat currency code to fetch prices in.
        :param provider: The API provider name.
        :param verbose: Whether to show detailed output.
        :param show_date: Whether to display the current timestamp in the output.
        """
        super().__init__(client)
        self.ticker_list: List[str] = tickers if tickers else []
        self.currency = currency
        self.provider = provider
        self.verbose = verbose
        self.show_date = show_date


    def _validate(self) -> None:
        logger.debug("Validating parsed arguments for price command")

        self.currency = resolve_currency(self.currency)
        self.provider = resolve_provider(self.provider)

        if not self.ticker_list:
            raise CommandError("No valid tickers provided")
        validate_tickers(self.ticker_list)

        logger.debug("Validated arguments successfully")
        
    
    def _execute(self) -> None:
        logger.debug(f"Executing price command for ticker(s): '{self.ticker_list}', currency: '{self.currency}'")
        logger.info(f"FETCHING PRICE DATA FOR TICKER(S): {','.join(f'${t}' for t in self.ticker_list)}...")

        if self.show_date:
            logger.info(f"Timestamp: {get_timestamp()}")
        data = self.client.fetch_multiple_price_data(",".join(self.ticker_list), self.currency)
        result = format_price_output(data, self.currency, self.client.config.base_url, self.verbose)
        if result:
            print_output(result)