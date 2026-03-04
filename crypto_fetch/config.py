import os
import logging
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

CONFIG_DIR = Path.home() / ".crypto-fetch-py"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "api_keys": {
        "coinmarketcap": ""
    },
    "defaults": {
        "currency": "EUR"
    }
}

logger = logging.getLogger("crypto_fetch")

def init_config() -> None:
    """
    Initializes the config file with the defaults.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        logger.info(f"Config file already exists at: '{CONFIG_FILE}'")
        return
    
    save_config(DEFAULT_CONFIG)
    logger.info(f"Created config file at: '{CONFIG_FILE}'")
    logger.info(f"Edit this file to add you API keys and set defaults")
    
def save_config(config: Dict[str, Any]) -> None:
    """
    Saves configuration to the config file.
    
    :param config: The configuration to save to the config file.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)

def load_config() -> Dict[str, Any]:
    """
    Loads the config file.
    
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
    config = load_config()
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
    config = load_config()
    return config.get("defaults", {}).get("currency", "EUR")