from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from typing import Any, Dict, Generic, TypeVar

import requests  # type: ignore

from crypto_fetch.config.config import get_api_key, get_default_api_timeout
from crypto_fetch.constants import CF_LOGGER
from crypto_fetch.exceptions import APIError

T = TypeVar('T')
logger = logging.getLogger(CF_LOGGER)


@dataclass
class APIConfig:
    """Config for API endpoints."""

    name: str
    base_url: str
    price_endpoint: str


class BaseAPIClient(ABC, Generic[T]):
    """Base class for API clients."""

    def __init__(self, config: APIConfig):
        """
        :param config: The API config.
        """
        self.config = config

    @abstractmethod
    def fetch_single_price_data(self, ticker: str, currency_code: str) -> float:
        """
        Fetches the price data for a single cryptocurrency.

        :param ticker: The ticker of the cryptocurrency.
        :param currency_code: The code of the fiat currency to fetch the data in.

        :return: The price of the cryptocurrency.
        :raises Exception: If an error occurs fetching the price data. 
        """
        pass

    @abstractmethod
    def fetch_multiple_price_data(self, tickers: str, currency_code: str) -> Dict[str, Dict[str, float]]:
        """
        Fetches the price data for multiple cryptocurrencies.

        :param tickers: The list of cryptocurrency tickers as a str.
        :param currency_code: The code of the fiat currency to fetch the data in.

        :return: A formatted dict containing the price data.
        :raises Exception: If an error occurs fetching the price data. 
        """
        pass

    @abstractmethod
    def _get_request_headers(self, api_key: str) -> Dict[str, str]:
        """
        Gets the headers for a request to the API.
        
        :param api_key: The API key.

        :return: A dict containing the request headers.
        """
        pass

    @abstractmethod
    def _get_request_params(self, tickers: str, currency_code: str) -> Dict[str, str]:
        """
        Gets the parameters for a request to the API.

        :param tickers: A single / comma-separated list of tickers as a str.
        :param currency_code: The fiat currency code.

        :return: A dict containing the request parameters.
        """
        pass

    @abstractmethod
    def _parse_json_response(self, data: Dict[str, Any], currency_code: str) -> T:
        """
        Parses the JSON response received from the API.

        :param data: The data received from the API.

        :return: The parsed data.
        """
        pass

    def _make_request(self, headers: Dict[str, str], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Makes a request to the API.

        :param headers: The request headers.
        :param params: The request parameters.

        :return: The JSON from the API.
        :raises APIError: If an error occurs fetching the response from the API.
        """
        try:
            request_url = f"{self.config.base_url}{self.config.price_endpoint}"
            logger.debug(f"Making request to: '{request_url}'")

            response_timeout = get_default_api_timeout()
            response: requests.Response = requests.get(
                url=request_url,
                headers=headers,
                params=params,
                timeout=response_timeout
            )

            if not response.ok:
                error_msg = response.json().get("status", {}).get("error_message")
                raise APIError(error_msg or f"API request failed with status {response.status_code}")
            
            logger.debug(f"Request was successful. Status code: {response.status_code}")
            return response.json()
        except Exception as ex:
            raise APIError(f"{str(ex)}") from ex

    def _get_api_key(self) -> str:
        """
        Gets the API key stored in the environment variable.

        :return: The API key.
        :raises APIError: If the API is not found.
        """
        logger.debug("Checking for API key...")
        api_key = get_api_key(self.config.name)

        if api_key is None:
            raise APIError(f"API key not found. Either add key to env variable or run: crypto-fetch config init")

        api_key = api_key.strip()
        if api_key.startswith('"') or api_key.startswith("'"):
            raise APIError(f"API key contains quotes. Remove quotes from API key in config file")
        
        self._validate_api_key_format(api_key)
        logger.debug("API key validation was successful")
        return api_key
        
    @abstractmethod
    def _validate_api_key_format(self, api_key: str):
        """
        Validates the API key ensuring it is in the correct format.
        
        :param api_key: The API key.
        """
        pass