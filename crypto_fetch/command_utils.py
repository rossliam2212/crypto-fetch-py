from datetime import datetime
from typing import List
import logging

from crypto_fetch.constants import (
    CF_LOGGER, 
    CURRENCY_SYMBOL_MAP,
    PROVIDERS_SUPPORTED,
    SUPPORTED_CRYPTO_TICKERS
)

logger = logging.getLogger(CF_LOGGER)

def validate_currency(value: str) -> str:
    logger.debug(f"Validating fiat currency: '{value.upper()}'")
    currency = value.upper()
    if currency not in CURRENCY_SYMBOL_MAP:
        raise ValueError(f"Unknown/Unsupported currency. Received '{currency}'")
    return currency


def validate_provider(value: str) -> str:
    logger.debug(f"Validating provider: '{value.lower()}'")
    provider = value.lower()
    if provider not in PROVIDERS_SUPPORTED:
        raise ValueError(f"Unknown/Unsupported provider. Received: '{provider}'")
    return provider


def validate_tickers(tickers: List[str]) -> None:
    logger.debug(f"Validating supplied crypto tickers: {tickers}")
    invalid_tickers = [t for t in tickers if t not in SUPPORTED_CRYPTO_TICKERS]
    if invalid_tickers:
        raise ValueError(f"Unknown/Unsupported ticker(s). Received: {', '.join(invalid_tickers)}")


def get_timestamp() -> str:
    """
    Gets the current timestamp in the format: 2025-07-29 21:07:00.

    :return: The current timestamp as a str.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def file_exists(filepath) -> bool:
    """
    Checks if a file exists.
    """
    if not filepath.exists():
        raise FileNotFoundError("Config file not found. Run 'crypto-fetch config init' to create")
    return True