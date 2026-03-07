from typing import Dict, Any, List
import logging

from crypto_fetch.constants import CF_LOGGER, PROVIDERS_SUPPORTED
from crypto_fetch.constants import CONFIG_HEADER_DEFAULTS, CONFIG_HEADER_API_KEYS
from crypto_fetch.constants import REQUIRED_PROVIDER_CONFIG_KEYS

logger = logging.getLogger(CF_LOGGER)

def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validates the configuration structure and values.
    
    :param config: The configuration dict to validate.
    :return: List of validation error messages, if any.
    """
    logger.debug(f"Validating API config file...")
    errors: List[str] = []
    
    # Check required top-level keys
    if CONFIG_HEADER_DEFAULTS not in config:
        errors.append("Missing 'defaults' section")
    
    if CONFIG_HEADER_API_KEYS not in config:
        errors.append("Missing 'api_keys' section")
    
    # Validate defaults section
    if CONFIG_HEADER_DEFAULTS in config:
        defaults = config[CONFIG_HEADER_DEFAULTS]
        _validate_defaults_section(defaults, errors)
    
    # Validate provider configs
    _validate_providers_section(config, errors)
    
    return errors

def _validate_defaults_section(defaults, errors: List[str]) -> None:
    if defaults is None:
        errors.append("'defaults' section is empty (null)")
        return
    
    if not isinstance(defaults, dict):
        errors.append(f"'defaults' section must be a dictionary, got {type(defaults).__name__}")
        return
    
    # Validate timeout
    timeout = defaults.get("api_timeout")
    if timeout is not None:
        if not isinstance(timeout, int):
            errors.append(f"Invalid timeout type: expected int. Got: {type(timeout).__name__}")
        elif timeout <= 0 or timeout > 300:
            errors.append(f"Invalid timeout value: {timeout} (must be 1-300)")
    
    # Validate currency
    currency = defaults.get("currency")
    if currency and not isinstance(currency, str):
        errors.append(f"Invalid currency type: expected str. Got: {type(currency).__name__}")
    
    # Validate provider
    provider = defaults.get("api_provider")
    if provider and provider not in PROVIDERS_SUPPORTED:
        errors.append(f"Invalid provider: {provider} (must be 'coinmarketcap' or 'coingecko')")

def _validate_providers_section(config: Dict[str, Any], errors: List[str]) -> None:
    for provider in PROVIDERS_SUPPORTED:
        if provider in config:
            provider_config = config[provider]
            
            if provider_config is None:
                errors.append(f"'{provider}' section is empty (null)")
                continue
            
            if not isinstance(provider_config, dict):
                errors.append(f"'{provider}' section must be a dictionary, got {type(provider_config).__name__}")
                continue
            
            for key in REQUIRED_PROVIDER_CONFIG_KEYS:
                if key not in provider_config:
                    errors.append(f"Missing '{key}' in {provider} config")
                elif not isinstance(provider_config[key], str):
                    errors.append(f"Invalid type for {provider}.{key}: expected str")