import logging
from pathlib import Path

import yaml  # type: ignore

from crypto_fetch.api.api_client import BaseAPIClient
from crypto_fetch.api.formatter import format_portfolio_output
from crypto_fetch.commands.command import Command
from crypto_fetch.commands.command_utils import resolve_currency, resolve_provider, validate_tickers
from crypto_fetch.constants import CF_LOGGER
from crypto_fetch.exceptions import CommandError

logger = logging.getLogger(CF_LOGGER)


class PortfolioCommand(Command):
    """Display portfolio holdings with live prices."""

    def __init__(self, client: BaseAPIClient, portfolio_file: str, currency: str, provider: str):
        super().__init__(client)
        self.portfolio_file: Path = Path(portfolio_file)
        self.currency = currency
        self.provider = provider
        self.holdings: dict[str, float] = {}

    def _validate(self) -> None:
        logger.debug("Validating parsed arguments for portfolio command")

        if not self.portfolio_file.exists():
            raise CommandError(f"Supplied portfolio file not found: '{self.portfolio_file}'")

        self.holdings = self._load_holdings_file()
        logger.debug(f"Loaded {len(self.holdings)} holding(s) from '{self.portfolio_file}': {self.holdings}")
        validate_tickers(list(self.holdings.keys()))

        self.currency = resolve_currency(self.currency)
        self.provider = resolve_provider(self.provider)

        logger.debug("Arguments validated successfully")

    def _load_holdings_file(self) -> dict[str, float]:
        """
        Parses the supplied portfolio file (YAML/txt) into a map of [ticker -> amount].
        - YAML format: 'TICKER: amount'
        - txt format: 'TICKER amount'

        :return: Map of [ticker -> amount].
        :raises CommandError: If the file is empty / invalid.
        """
        logger.debug(f"Reading portfolio file: '{self.portfolio_file}'")
        with open(self.portfolio_file, "r") as f:
            content = f.read()

        data = yaml.safe_load(content)

        if not isinstance(data, dict):
            # If a txt file is supplied
            logger.debug("File is not YAML dict format, attempting plain-text parsing")
            data = {}
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    logger.debug(f"Skipping line: '{line}'")
                    continue
                # Format: 'TICKER amount'
                parts = line.split()
                if len(parts) != 2:
                    raise CommandError(f"Invalid line in portfolio file: '{line}'")
                data[parts[0]] = parts[1]

        if not data:
            raise CommandError("Portfolio file is empty")

        holdings = {}
        for k, v in data.items():
            try:
                holdings[k.upper()] = float(v)
            except (ValueError, TypeError):
                raise CommandError(f"Invalid amount for '{k}': '{v}' is not a number")
        return holdings

    def _execute(self) -> None:
        logger.debug(f"Fetching prices for {len(self.holdings)} holding(s) using provider '{self.provider}'")
        tickers = ",".join(self.holdings.keys())
        price_data = self.client.fetch_multiple_price_data(tickers, self.currency)

        missing = [t for t in self.holdings if t not in price_data]
        if missing:
            logger.warning(f"No price data returned for: {', '.join(missing)}")

        format_portfolio_output(self.holdings, price_data, self.currency)