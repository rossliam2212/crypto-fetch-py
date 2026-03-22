import logging
from typing import List

from crypto_fetch.api.api_client import BaseAPIClient
from crypto_fetch.api.formatter import format_price_output
from crypto_fetch.commands.command import Command
from crypto_fetch.commands.command_utils import get_timestamp, validate_currency, validate_provider, validate_tickers
from crypto_fetch.config.config import get_default_api_provider, get_default_fiat_currency
from crypto_fetch.constants import CF_LOGGER
from crypto_fetch.exceptions import CommandError

logger = logging.getLogger(CF_LOGGER)


class PriceCommand(Command):
    """Fetch cryptocurrency prices"""

    def __init__(self, client: BaseAPIClient, tickers: str, currency: str, provider: str, verbose: bool, show_date: bool = False):
        super().__init__(client)
        self.tickers = tickers
        self.ticker_list: List[str] = []
        self.currency = currency
        self.provider = provider
        self.verbose = verbose
        self.show_date = show_date

    def _validate(self) -> None:
        logger.debug(f"Validating parsed arguments for price command")

        if self.currency is None:
            self.currency = get_default_fiat_currency()
            logger.debug(f"Fiat currency not specified. Using default: '{self.currency}'")
        self.currency = validate_currency(self.currency)

        if self.provider is None:
            self.provider = get_default_api_provider()
            logger.debug(f"API provider not specified. Using default: '{self.provider}'")
        self.provider = validate_provider(self.provider)

        self.ticker_list = [t.strip().upper() for t in self.tickers.split(",") if t.strip()]
        if not self.ticker_list:
            raise CommandError(f"No valid tickers provided. Got: {self.tickers}")
        validate_tickers(self.ticker_list)

        logger.debug(f"Validated arguments successfully")
        
    
    def _execute(self) -> None:
        logger.debug(f"Executing price command for ticker(s): '{self.ticker_list}', currency: '{self.currency}'")
        logger.info(f"FETCHING PRICE DATA FOR TICKER(S): {','.join(f'${t}' for t in self.ticker_list)}...")

        if self.show_date:
            logger.info(f"Timestamp: {get_timestamp()}")
        data = self.client.fetch_multiple_price_data(",".join(self.ticker_list), self.currency)
        logger.info(format_price_output(data, self.currency, self.client.config.base_url, self.verbose))