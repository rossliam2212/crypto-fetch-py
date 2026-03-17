import logging
from pathlib import Path

import yaml  # type: ignore

from crypto_fetch.api_client import BaseAPIClient
from crypto_fetch.command import Command
from crypto_fetch.command_utils import validate_currency, validate_provider, validate_tickers
from crypto_fetch.config import get_default_api_provider, get_default_fiat_currency
from crypto_fetch.constants import CF_LOGGER
from crypto_fetch.exceptions import CommandError
from crypto_fetch.formatter import format_portfolio_output

logger = logging.getLogger(CF_LOGGER)


class PortfolioCommand(Command):
    """Display portfolio holdings with live prices."""

    def __init__(self, client: BaseAPIClient, portfolio_file: str, currency: str, provider: str):
        super().__init__(client)
        self.portfolio_file = Path(portfolio_file)
        self.currency = currency
        self.provider = provider
        self.holdings: dict[str, float] = {}

    def _validate(self) -> None:
        logger.debug(f"Validating parsed arguments for portfolio command")

        if not self.portfolio_file.exists():
            raise CommandError(f"Supplied portfolio file not found: '{self.portfolio_file}'")

        with open(self.portfolio_file, "r") as f:
            content = f.read()

        data = yaml.safe_load(content)

        if not isinstance(data, dict):
            # try parsing space-separated format: "TICKER amount" per line
            data = {}
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    logger.debug(f"Skipping line: {line}")
                    continue
                parts = line.split()
                if len(parts) != 2:
                    raise CommandError(f"Invalid line in portfolio file: '{line}'")
                data[parts[0]] = parts[1]

        if not data:
            raise CommandError("Portfolio file is empty")

        self.holdings = {k.upper(): float(v) for k, v in data.items()}
        logger.debug(f"Loaded holdings from file: '{self.portfolio_file}'. Holdings: {self.holdings}")
        validate_tickers(list(self.holdings.keys()))

        if self.currency is None:
            self.currency = get_default_fiat_currency()
            logger.debug(f"Fiat currency not specified. Using default: '{self.currency}'")
        self.currency = validate_currency(self.currency)

        if self.provider is None:
            self.provider = get_default_api_provider()
            logger.debug(f"API provider not specified. Using default: '{self.provider}'")
        self.provider = validate_provider(self.provider)

        logger.debug(f"Validated arguments successfully")

    def _execute(self) -> None:
        tickers = ",".join(self.holdings.keys())
        price_data = self.client.fetch_multiple_price_data(tickers, self.currency)

        missing = [t for t in self.holdings if t not in price_data]
        if missing:
            logger.warning(f"No price data returned for: {', '.join(missing)}")

        format_portfolio_output(self.holdings, price_data, self.currency)