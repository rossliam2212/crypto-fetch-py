import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml  # type: ignore

from crypto_fetch.config.config_validator import validate_config
from crypto_fetch.constants import (
    CF_LOGGER,
    CONFIG_DEFAULTS_API_TIMEOUT,
    CONFIG_DEFAULTS_CURRENCY,
    CONFIG_HEADER_API_KEYS,
    CONFIG_HEADER_DEFAULTS,
    CONFIG_KEY_DEFAULTS_API_PROVIDER,
    CONFIG_KEY_DEFAULTS_API_TIMEOUT,
    CONFIG_KEY_DEFAULTS_CURRENCY,
    PROVIDER_COINMARKETCAP,
)

CONFIG_DIR = Path.home() / ".crypto-fetch-py"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "api_keys": {
        "coinmarketcap": "",
        "coingecko": ""
    },
    "defaults": {
        "currency": CONFIG_DEFAULTS_CURRENCY,
        "api_provider": PROVIDER_COINMARKETCAP,
        "api_timeout": CONFIG_DEFAULTS_API_TIMEOUT
    },
    "coinmarketcap": {
        "name": "coinmarketcap",
        "base_url": "https://pro-api.coinmarketcap.com/v1",
        "price_ep": "/cryptocurrency/quotes/latest"
    },
    "coingecko": {
        "name": "coingecko",
        "base_url": "https://api.coingecko.com/api/v3/",
        "price_ep": "/simple/price"
    }
}

logger = logging.getLogger(CF_LOGGER)


def init_api_config_file() -> None:
    """
    Initializes the config file with the defaults.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        logger.info(f"Config file already exists at: '{CONFIG_FILE}'")
        return
    
    save_api_config_to_file(DEFAULT_CONFIG)
    logger.info(f"Created config file at: '{CONFIG_FILE}'")
    logger.info(f"Edit this file to add you API keys and set defaults")


def save_api_config_to_file(config: Dict[str, Any]) -> None:
    """
    Saves configuration to the config file.
    
    :param config: The configuration to save to the config file.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)


def load_api_config_from_file() -> Dict[str, Any]:
    """
    Loads and returns the YAML config file, or defaults if missing/invalid.

    :return: the loaded config dict.
    """
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config is None or not isinstance(config, dict):
                    logger.warning("Config file is empty or invalid. Using defaults.")
                    return DEFAULT_CONFIG.copy()

                errors = validate_config(config)
                if errors:
                    logger.warning(f"Config has {len(errors)} issue(s). Run 'crypto-fetch config validate' for details")

                return config
        except yaml.YAMLError as ex:
            logger.error(f"API config file is corrupted: {ex}. Using defaults.")
            return DEFAULT_CONFIG.copy()
        except Exception as ex:
            logger.error(f"Failed to load API config: {ex}. Using defaults.")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def get_api_key(provider: str) -> Optional[str]:
    """
    Gets the API key from the config file.
    
    :param provider: The provider to get the API key for.

    :return: the api key or None.
    """
    config = load_api_config_from_file()
    api_key = config.get(CONFIG_HEADER_API_KEYS, {}).get(provider, "")

    if api_key and isinstance(api_key, str):
        logger.debug(f"Found API key for '{provider}' in config file")
        return api_key.strip()
    else:
        return None


def get_default_fiat_currency() -> str:
    """
    Gets the default currency set in the config file
    
    :return: the default currency.
    """
    config = load_api_config_from_file()
    return config.get(CONFIG_HEADER_DEFAULTS, {}).get(CONFIG_KEY_DEFAULTS_CURRENCY, CONFIG_DEFAULTS_CURRENCY)


def get_default_api_timeout() -> int:
    """
    Gets the default API timeout from config.
    
    :return: timeout in seconds.
    """
    config = load_api_config_from_file()
    return config.get(CONFIG_HEADER_DEFAULTS, {}).get(CONFIG_KEY_DEFAULTS_API_TIMEOUT, CONFIG_DEFAULTS_API_TIMEOUT)


def get_default_api_provider() -> str:
    """
    Gets the default API provider from config.
    
    :return: provider name.
    """
    config = load_api_config_from_file()
    return config.get(CONFIG_HEADER_DEFAULTS, {}).get(CONFIG_KEY_DEFAULTS_API_PROVIDER, PROVIDER_COINMARKETCAP)


def get_api_provider_config(provider: str) -> Dict[str, str]:
    """
    Gets the provider configuration from config file.
    
    :param provider: The provider name.

    :return: Supplied or default provider configuration as a dict.
    """
    config = load_api_config_from_file()
    provider_config = config.get(provider, {})
    
    if not provider_config:
        logger.warning(f"No API config found for provider '{provider}'. Using defaults")
        return DEFAULT_CONFIG.get(provider, {})
    
    logger.debug(f"Loaded API config: {provider_config}")
    return provider_config