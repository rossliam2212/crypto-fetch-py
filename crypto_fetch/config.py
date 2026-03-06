import os
import logging
import yaml # type: ignore
from pathlib import Path
from typing import Optional, Dict, Any

from crypto_fetch.constants import CF_LOGGER

CONFIG_DIR = Path.home() / ".crypto-fetch-py"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "api_keys": {
        "coinmarketcap": "",
        "coingecko": ""
    },
    "defaults": {
        "currency": "EUR",
        "api_provider": "coinmarketcap",
        "api_timeout": 10
    },
    "coinmarketcap": {
        "name": "coinmarketcap",
        "env_var": "COINMARKETCAP_API_KEY",
        "base_url": "https://pro-api.coinmarketcap.com/v1",
        "price_ep": "/cryptocurrency/quotes/latest"
    },
    "coingecko": {
        "name": "coingecko",
        "env_var": "COINGECKO_API_KEY",
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
    Loads the YAML config file.
    Converts the YAML input from the config file into a dict[str, Any].
    
    :return: the loaded config file or the deafult.
    """
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or DEFAULT_CONFIG
        
    return DEFAULT_CONFIG.copy()

def get_api_key(provider: str, env_var: str) -> Optional[str]:
    """
    Gets the API key from the config file or env variable.
    
    :param provider: The provider to get the API key for.
    :param env_var: The env variable the API key may be set.

    :return: the api key or None.
    """
    # check env variable first
    api_key = os.getenv(env_var)
    if api_key:
        logger.debug(f"Found API key for '{provider}' in env variable '{env_var}'")
        return api_key.strip()
    
    # check config file second
    config = load_api_config_from_file()
    api_key = config.get("api_keys", {}).get(provider, "")

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
    return config.get("defaults", {}).get("currency", "EUR")

def get_default_api_timeout() -> int:
    """
    Gets the default API timeout from config.
    
    :return: timeout in seconds.
    """
    config = load_api_config_from_file()
    return config.get("defaults", {}).get("api_timeout", 10)

def get_default_api_provider() -> str:
    """
    Gets the default API provider from config.
    
    :return: provider name.
    """
    config = load_api_config_from_file()
    return config.get("defaults", {}).get("api_provider", "coinmarketcap")

def get_api_provider_config(provider: str) -> Dict[str, str]:
    """
    Gets the provider configuration from config file.
    
    :param provider: The provider name.

    :return: Supplied or default provider configuration as a dict.
    """
    config = load_api_config_from_file()
    provider_config = config.get(provider, {})
    
    if not provider_config:
        logger.warning(f"No config found for provider '{provider}'. Using defaults")
        return DEFAULT_CONFIG.get(provider, {})
    
    # Strip trailing commas from values
    sanitized = {k: v.rstrip(',') if isinstance(v, str) else v for k, v in provider_config.items()}
    
    logger.debug(f"Loaded config: {sanitized}")
    return sanitized