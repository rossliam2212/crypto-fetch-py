from datetime import datetime
import logging
from typing import List

from crypto_fetch.constants import (
    CF_LOGGER,
    CURRENCY_SYMBOL_MAP,
    DATE_TIME_FORMAT,
    PROVIDERS_SUPPORTED,
    SUPPORTED_CRYPTO_TICKERS,
)
from crypto_fetch.exceptions import CommandError

logger = logging.getLogger(CF_LOGGER)


def validate_currency(value: str) -> str:
    """
    Validates the supplied fiat currency code.

    :param value: The fiat currency code.
    :return: The validated currency code, in uppercase.
    :raises CommandError: If the supplied currency is not supported.
    """
    logger.debug(f"Validating fiat currency: '{value.upper()}'")
    currency = value.upper()
    if currency not in CURRENCY_SYMBOL_MAP:
        raise CommandError(f"Unknown/Unsupported currency. Received '{currency}'")
    return currency


def validate_provider(value: str) -> str:
    """
    Validates the supplied API provider name.

    :param value: The API provider name.
    :return: The lowercased, validated provider name.
    :raises CommandError: If the supplied provider is not supported.
    """
    logger.debug(f"Validating provider: '{value.lower()}'")
    provider = value.lower()
    if provider not in PROVIDERS_SUPPORTED:
        raise CommandError(f"Unknown/Unsupported provider. Received: '{provider}'")
    return provider


def validate_tickers(tickers: List[str]) -> None:
    """
    Validates a list of cryptocurrency ticker symbols.

    :param tickers: List of uppercase ticker symbols (e.g. ['BTC', 'XRP']).
    :raises CommandError: If any ticker is not supported.
    """
    logger.debug(f"Validating supplied crypto tickers: {tickers}")
    invalid_tickers = [t for t in tickers if t not in SUPPORTED_CRYPTO_TICKERS]
    if invalid_tickers:
        raise CommandError(f"Unknown/Unsupported ticker(s). Received: {', '.join(invalid_tickers)}")


def get_timestamp() -> str:
    """
    Returns the current date and time in the format 'YYYY-MM-DD HH:MM:SS'.

    :return: the current timestamp.
    """
    return datetime.now().strftime(DATE_TIME_FORMAT)