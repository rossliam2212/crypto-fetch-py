import logging

from crypto_fetch.api.api_client import APIConfig, BaseAPIClient
from crypto_fetch.api.cmc_api_client import CoinMarketCapAPIClient
from crypto_fetch.api.cg_api_client import CoinGeckoAPIClient
from crypto_fetch.config.config import get_api_provider_config
from crypto_fetch.constants import (
    CF_LOGGER,
    CONFIG_KEY_PROVIDER_NAME,
    CONFIG_KEY_PROVIDER_BASE_URL,
    CONFIG_KEY_PROVIDER_PRICE_EP,
    PROVIDER_COINMARKETCAP,
    PROVIDER_COINGECKO,
)
from crypto_fetch.exceptions import APIError

logger = logging.getLogger(CF_LOGGER)


def create_api_client(provider: str) -> BaseAPIClient:
    """
    Creates the appropriate API client for an already-resolved provider name.

    :param provider: The resolved provider name.
    :return: The API client.
    :raises APIError: If the provider is not recognised.
    """
    if provider == PROVIDER_COINGECKO:
        return CoinGeckoAPIClient(_create_api_config(PROVIDER_COINGECKO))
    if provider == PROVIDER_COINMARKETCAP:
        return CoinMarketCapAPIClient(_create_api_config(PROVIDER_COINMARKETCAP))
    raise APIError(f"Unknown provider: '{provider}'")


def _create_api_config(provider: str) -> APIConfig:
    """
    Builds an APIConfig from the provider's configuration in the config file.

    :param provider: The provider name.
    :return: The APIConfig for the given provider.
    """
    logger.debug(f"Creating API config for provider: '{provider}'")
    config = get_api_provider_config(provider)

    return APIConfig(
        name=config.get(CONFIG_KEY_PROVIDER_NAME, provider),
        base_url=config.get(CONFIG_KEY_PROVIDER_BASE_URL, ""),
        price_endpoint=config.get(CONFIG_KEY_PROVIDER_PRICE_EP, ""),
    )
