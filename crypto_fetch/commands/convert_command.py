import logging

from crypto_fetch.api.api_client import BaseAPIClient
from crypto_fetch.api.formatter import format_convert_output
from crypto_fetch.commands.command import Command
from crypto_fetch.commands.command_utils import get_timestamp, validate_currency, validate_provider, validate_tickers
from crypto_fetch.config.config import get_default_api_provider, get_default_fiat_currency
from crypto_fetch.constants import CF_LOGGER
from crypto_fetch.exceptions import CommandError

logger = logging.getLogger(CF_LOGGER)


class ConvertCommand(Command):
    """Convert cryptocurrency to fiat currency."""

    def __init__(self, client: BaseAPIClient, amount: str, ticker: str, currency: str, show_date: bool, provider: str):
        super().__init__(client)
        self.amount_raw = amount
        self.amount_to_convert: float = 0.0
        self.ticker = ticker
        self.currency = currency
        self.provider = provider
        self.show_date = show_date

    def _validate(self) -> None:
        logger.debug(f"Validating parsed arguments for convert command")

        try:
            self.amount_to_convert = float(self.amount_raw)
        except ValueError:
            raise CommandError(f"Invalid amount: '{self.amount_raw}' is not a number")

        if self.amount_to_convert <= 0:
            raise CommandError(f"Amount must be positive. Received: '{self.amount_to_convert}'")

        if self.currency is None:
            self.currency = get_default_fiat_currency()
            logger.debug(f"Fiat currency not specified. Using default: '{self.currency}'")
        self.currency = validate_currency(self.currency)

        if self.provider is None:
            self.provider = get_default_api_provider()
            logger.debug(f"API provider not specified. Using default: '{self.provider}'")
        self.provider = validate_provider(self.provider)

        self.ticker = self.ticker.strip().upper()
        validate_tickers([self.ticker])

        logger.debug(f"Validated arguments successfully")


    def _execute(self) -> None:
        logger.debug(f"Executing convert command: amount='{self.amount_to_convert}', ticker='{self.ticker}', currency='{self.currency}'")
        logger.info(f"CONVERTING {self.amount_to_convert} ${self.ticker} to {self.currency}...")

        if self.show_date:
            logger.info(f"Timestamp: {get_timestamp()}")

        price: float = self.client.fetch_single_price_data(self.ticker, self.currency)

        converted_amount: float = self._calculate_conversion(price)
        logger.info(format_convert_output(self.ticker, self.currency, self.amount_to_convert, converted_amount))


    def _calculate_conversion(self, fetched_crypto_price: float) -> float:
        """
        Calculates conversion between supplied amount and the fetched crypto price.

        :param fetched_crypto_price: The fetched crypto price.
        :return: the conversion amount.
        """
        return self.amount_to_convert * fetched_crypto_price