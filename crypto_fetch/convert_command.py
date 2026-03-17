import argparse
from typing import Any, Dict, List
import logging

from crypto_fetch.api_client import BaseAPIClient
from crypto_fetch.command import Command
from crypto_fetch.command_utils import validate_currency, validate_provider, validate_tickers, get_timestamp
from crypto_fetch.constants import CF_LOGGER
from crypto_fetch.config import get_default_fiat_currency, get_default_api_provider
from crypto_fetch.exceptions import CommandError
from crypto_fetch.formatter import format_convert_output

logger = logging.getLogger(CF_LOGGER)

class ConvertCommand(Command):
    """Convert cryptocurrency to fiat currency."""

    def __init__(self, client: BaseAPIClient, amount: str, ticker: str, currency: str, show_date: bool, provider: str):
        super().__init__(client)
        self.amount_to_convert_str = amount
        self.amount_to_convert: float = 0.0
        self.ticker = ticker
        self.currency = currency
        self.provider = provider
        self.show_date = show_date

    def validate(self) -> None:
        logger.debug(f"Validating parsed arguments for convert command")

        try:
            self.amount_to_convert = float(self.amount_to_convert_str)
        except ValueError:
            raise CommandError(f"Invalid amount: '{self.amount_to_convert_str}' is not a number")

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

    def execute(self) -> Any:
        logger.info(f"CONVERTING {self.amount_to_convert} ${self.ticker} to {self.currency}...")
        if self.show_date:
            logger.info(f"Timestamp: {get_timestamp()}")

        price: float = self.client.fetch_single_price_data(self.ticker, self.currency)

        converted_amount: float = self.amount_to_convert * price
        logger.info(format_convert_output(self.ticker, self.currency, self.amount_to_convert, converted_amount))