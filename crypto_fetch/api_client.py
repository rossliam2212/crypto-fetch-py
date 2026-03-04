import os
import logging
import requests
from typing import Dict, Any, TypeVar, Generic
from dataclasses import dataclass
from abc import ABC, abstractmethod

from crypto_fetch.exceptions import APIError
from crypto_fetch.config import get_api_key
from crypto_fetch.config import CONFIG_FILE

T = TypeVar('T')
logger = logging.getLogger("crypto_fetch")

@dataclass
class APIConfig:
    """Config for API endpoints."""

    name: str
    base_url: str
    latest_endpoint: str
    api_key_env_var: str

# =========================================================================================================
# BaseAPIClient
# =========================================================================================================
class BaseAPIClient(ABC, Generic[T]):
    """Base class for API clients."""

    def __init__(self, config: APIConfig):
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

        :return: A dict containing the requst headers.
        """
        pass

    @abstractmethod
    def _get_request_params(self, tickers: str, currency_code: str) -> Dict[str, str]:
        """
        Gets the paramters for a request to the API.

        :param tickers: A single / comma-separted list of tickers as a str.
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
        Makes a requst to the API.

        :param headers: The request headers.
        :param params: The request parameters.

        :return: The JSON from the API.
        :raises APIError: If an error occurs fetching the response from the API.
        """
        try:
            request_url = f"{self.config.base_url}{self.config.latest_endpoint}"
            logger.debug(f"Making request to: '{request_url}'")

            response: requests.Response = requests.get(
                url=request_url,
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                error_msg = response.json().get("status", {}).get("error_message", "Unknown API error")
                raise APIError(error_msg)
            
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
        api_key = get_api_key(self.config.name, self.config.api_key_env_var)
        if api_key:
            return api_key.strip()

        raise APIError(f"API key not found. Please set '{self.config.api_key_env_var}' " 
                       f"env variable or add key to '{CONFIG_FILE}'")

# =========================================================================================================
# CoinMarketCapAPIClient
# =========================================================================================================
class CoinMarketCapAPIClient(BaseAPIClient[Dict[str, Dict[str, float]]]):
    """Impl of the BaseAPIClient class for the CoinMarketCap API."""

    def fetch_single_price_data(self, ticker: str, currency_code: str) -> float:
        try:
            logger.debug(f"Fetching price data for ticker: '{ticker}'")

            api_key: str = self._get_api_key()
            headers: Dict[str, str] = self._get_request_headers(api_key)
            params: Dict[str, str] = self._get_request_params(ticker, currency_code)

            data = self._make_request(headers, params)
            return data['data'][ticker]['quote'][currency_code.upper()]['price']
        except Exception as ex:
            raise Exception(f"{str(ex)}")

    def fetch_multiple_price_data(self, tickers: str, currency_code: str) -> Dict[str, Dict[str, float]]:
        try:
            logger.debug(f"Fetching price data for tickers: '{tickers}'")

            api_key: str = self._get_api_key()
            headers: Dict[str, str] = self._get_request_headers(api_key)
            params: Dict[str, str] = self._get_request_params(tickers, currency_code)

            data = self._make_request(headers, params)
            return self._parse_json_response(data, currency_code)
        except Exception as ex:
            raise Exception(f"{str(ex)}")
        

    def _get_request_headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key
        }
    
    def _get_request_params(self, tickers: str, currency_code: str) -> Dict[str, str]:
        return {
            "symbol": tickers,
            "convert": currency_code.upper()
        }
    
    def _parse_json_response(self, data: Dict[str, Any], currency_code: str) -> Dict[str, Dict[str, float]]:
        result: Dict[str, Dict[str, float]] = {}
        raw_data: Dict[str, Any] = data.get("data", {})
        currency_code: str = currency_code.upper()

        for ticker, data in raw_data.items():
            quote: Dict[str, Any] = data.get("quote", {}).get(currency_code, {})
        
            result[ticker] = {
                "price": float(quote.get("price", 0)),
                "1h_change": float(quote.get("percent_change_1h", 0)),
                "24h_change": float(quote.get("percent_change_24h", 0)),
                "7d_change": float(quote.get("percent_change_7d", 0)),
                "market_cap": float(quote.get("market_cap", 0)),
                "24h_volume": float(quote.get("volume_24h", 0)),
        }
        return result
    
# =========================================================================================================
# CoinGeckoAPIClient
# =========================================================================================================
class CoinGeckoAPIClient(BaseAPIClient[Dict[str, Dict[str, float]]]):
    """Impl of the BaseAPIClient class for the CoinGecko API."""
    
    def fetch_single_price_data(self, ticker: str, currency_code: str) -> float:
        pass

    def fetch_multiple_price_data(self, tickers: str, currency_code: str) -> Dict[str, Dict[str, float]]:
        pass
        

    def _get_request_headers(self, api_key: str) -> Dict[str, str]:
        pass
    
    def _get_request_params(self, tickers: str, currency_code: str) -> Dict[str, str]:
        pass
    
    def _parse_json_response(self, data: Dict[str, Any], currency_code: str) -> Dict[str, Dict[str, float]]:
        pass