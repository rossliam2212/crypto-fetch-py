import logging
from typing import Any, Dict, List

from crypto_fetch.constants import (
    CF_LOGGER,
    CONFIG_HEADER_API_KEYS,
    CONFIG_HEADER_DEFAULTS,
    PROVIDERS_SUPPORTED,
    REQUIRED_PROVIDER_CONFIG_KEYS,
)

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
    else:
        _validate_defaults_section(config[CONFIG_HEADER_DEFAULTS], errors)
    
    if CONFIG_HEADER_API_KEYS not in config:
        errors.append("Missing 'api_keys' section")

    _validate_providers_section(config, errors)

    return errors


def _validate_defaults_section(defaults_section: Dict[str, Any], errors: List[str]) -> None:
    """
    Validates the defaults section in the config file.

    :param defaults_section: The defaults dict to validate.
    :param errors: List of validation error messages.
    """
    if defaults_section is None:
        errors.append("'defaults' section is empty (null)")
        return
    
    if not isinstance(defaults_section, dict):
        errors.append(f"'defaults' section must be a dictionary, got {type(defaults_section).__name__}")
        return

    # Validate timeout
    timeout = defaults_section.get("api_timeout")
    if timeout is not None:
        if not isinstance(timeout, int):
            errors.append(f"Invalid timeout type: expected int. Got: {type(timeout).__name__}")
        elif timeout <= 0 or timeout > 300:
            errors.append(f"Invalid timeout value: {timeout} (must be 1-300)")
    
    # Validate currency
    currency = defaults_section.get("currency")
    if currency and not isinstance(currency, str):
        errors.append(f"Invalid currency type: expected str. Got: {type(currency).__name__}")
    
    # Validate provider
    provider = defaults_section.get("api_provider")
    if provider and provider not in PROVIDERS_SUPPORTED:
        errors.append(f"Invalid provider: {provider} (must be one of: {', '.join(PROVIDERS_SUPPORTED)})")


def _validate_providers_section(provider_section: Dict[str, Any], errors: List[str]) -> None:
    """
    Validates the provider section in the config file.

    :param provider_section: The configuration dict to validate.
    :param errors: List of validation error messages.
    """
    for provider in PROVIDERS_SUPPORTED:
        if provider in provider_section:
            provider_config = provider_section[provider]
            
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