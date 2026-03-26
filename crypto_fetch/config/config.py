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
    CONFIG_KEY_PROVIDER_BASE_URL,
    CONFIG_KEY_PROVIDER_NAME,
    CONFIG_KEY_PROVIDER_PRICE_EP,
    PROVIDER_COINMARKETCAP,
    PROVIDER_COINMARKETCAP_BASE_URL,
    PROVIDER_COINMARKETCAP_PRICE_EP,
    PROVIDER_COINGECKO,
    PROVIDER_COINGECKO_BASE_URL,
    PROVIDER_COINGECKO_PRICE_EP,
)

CONFIG_DIRECTORY_PATH: Path = Path.home() / ".crypto-fetch-py"
CONFIG_FILE_PATH: Path = CONFIG_DIRECTORY_PATH / "config.yaml"
DEFAULT_API_CONFIG: Dict[str, Any] = {
    CONFIG_HEADER_API_KEYS: {
        PROVIDER_COINMARKETCAP: "",
        PROVIDER_COINGECKO: ""
    },
    CONFIG_HEADER_DEFAULTS: {
        CONFIG_KEY_DEFAULTS_CURRENCY: CONFIG_DEFAULTS_CURRENCY,
        CONFIG_KEY_DEFAULTS_API_PROVIDER: PROVIDER_COINMARKETCAP,
        CONFIG_KEY_DEFAULTS_API_TIMEOUT: CONFIG_DEFAULTS_API_TIMEOUT
    },
    PROVIDER_COINMARKETCAP: {
        CONFIG_KEY_PROVIDER_NAME: PROVIDER_COINMARKETCAP,
        CONFIG_KEY_PROVIDER_BASE_URL: PROVIDER_COINMARKETCAP_BASE_URL,
        CONFIG_KEY_PROVIDER_PRICE_EP: PROVIDER_COINMARKETCAP_PRICE_EP
    },
    PROVIDER_COINGECKO: {
        CONFIG_KEY_PROVIDER_NAME: PROVIDER_COINGECKO,
        CONFIG_KEY_PROVIDER_BASE_URL: PROVIDER_COINGECKO_BASE_URL,
        CONFIG_KEY_PROVIDER_PRICE_EP: PROVIDER_COINGECKO_PRICE_EP
    }
}

logger = logging.getLogger(CF_LOGGER)


def init_api_config_file() -> None:
    """
    Initializes the config file with the defaults.

    :raises OSError: If the config directory or file cannot be created.
    """
    CONFIG_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE_PATH.exists():
        logger.info(f"Config file already exists at: '{CONFIG_FILE_PATH}'")
        return
    
    save_api_config_to_file(DEFAULT_API_CONFIG)
    logger.info(f"Created config file at: '{CONFIG_FILE_PATH}'")
    logger.info(f"Edit this file to add you API keys and set defaults")


def save_api_config_to_file(config: Dict[str, Any]) -> None:
    """
    Saves configuration to the config file.
    
    :param config: The configuration to save to the config file.
    """
    CONFIG_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)


def load_api_config_from_file() -> Dict[str, Any]:
    """
    Loads and returns the YAML config file, or defaults if missing/invalid.

    :return: the loaded config dict.
    """
    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if config is None or not isinstance(config, dict):
                    logger.warning("Config file is empty or invalid. Using defaults.")
                    return DEFAULT_API_CONFIG.copy()

                errors = validate_config(config)
                if errors:
                    logger.warning(f"Config has {len(errors)} issue(s). Run 'crypto-fetch config validate' for details")

                return config
        except yaml.YAMLError as ex:
            logger.error(f"API config file is corrupted: {ex}. Using defaults.")
        except Exception as ex:
            logger.error(f"Failed to load API config: {ex}. Using defaults.")
    return DEFAULT_API_CONFIG.copy()


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
        return DEFAULT_API_CONFIG.get(provider, {})
    
    logger.debug(f"Loaded API config: {provider_config}")
    return provider_config