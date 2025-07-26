import os
import requests
from typing import Dict, Any, List, Optional, Union, TypeVar, Generic
from dataclasses import dataclass
from abc import ABC, abstractmethod

from crypto_fetch.exceptions import APIKeyError
from crypto_fetch.exceptions import APIResponseError

# ==========================================
T = TypeVar('T')

@dataclass
class APIConfig:
    """Config for API endpoints"""

    base_url: str
    latest_endpoint: str
    api_key_env_var: str

class BaseAPIClient(ABC, Generic[T]):
    """Base class for API clients"""

    def __init__(self, config: APIConfig):
        self.config = config
        super().__init__()

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
        :raises APIResponseError: If an error occurs fetching the response form the API.
        """
        try:
            response: requests.Response = requests.get(
                f"{self.config.base_url}{self.config.latest_endpoint}",
                headers=headers,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                error_msg = response.json().get("status", {}).get("error_message", "Unknown API error")
                raise APIResponseError(error_msg)
            
            return response.json()
        except Exception as ex:
            raise APIResponseError(f"{str(ex)}") from ex

    def _get_api_key(self) -> str:
        """
        Gets the CMC API key stored in the 'COINMARKETCAP_API_KEY' environment variable.

        :return: The CMC API key stored in the environment variable.
        :raises APIKeyError: If the API is not found.
        """
        api_key = os.getenv(self.config.api_key_env_var)
        if not api_key:
            raise APIKeyError(f"Could not find API key in '{self.config.api_key_env_var}'")
        return api_key
    
class CoinMarketCapAPIClient(BaseAPIClient[Dict[str, Dict[str, float]]]):
    """Impl of the BaseAPIClient class for the CoinMarketCap API"""

    def fetch_single_price_data(self, ticker: str, currency_code: str) -> float:
        """
        Fetches the price data for a single cryptocurrency

        :param ticker: The ticker of the cryptocurrency.
        :param currency_code: The code of the fiat currency to fetch the data in.

        :return: The price of the cryptocurrency.
        :raises Exception: If an error occurs fetching the price data. 
        """
        try:
            api_key: str = self._get_api_key()
            headers: Dict[str, str] = {
                "Accepts": "application/json",
                "X-CMC_PRO_API_KEY": api_key
            }
            params = {
                "symbol": ticker,
                "convert": currency_code.upper()
            }

            data = self._make_request(headers, params)
            return data['data'][ticker]['quote'][currency_code.upper()]['price']
        except Exception as ex:
            raise Exception(f"{str(ex)}")

    def fetch_multiple_price_data(self, tickers: str, currency_code: str) -> Dict[str, Dict[str, float]]:
        """
        Fetches the price data for multiple cryptocurrencies.

        :param tickers: The list of cryptocurrency tickers as a str.
        :param currency_code: The code of the fiat currency to fetch the data in.

        :return: A formatted dict containing the price data.
        :raises Exception: If an error occurs fetching the price data. 
        """
        try:
            api_key: str = self._get_api_key()
            headers = {
                "Accepts": "application/json",
                "X-CMC_PRO_API_KEY": api_key
            }
            params = {
                "symbol": tickers,
                "convert": currency_code.upper()
            }
            data = self._make_request(headers, params)
            return self._parse_json_response(data, currency_code)
        except Exception as ex:
            raise Exception(f"{str(ex)}")
    
    def _parse_json_response(self, data: Dict[str, Any], currency_code: str) -> Dict[str, Dict[str, float]]:
        """
        Parses the JSON response received from the CMC API into a dict.

        :param data: The JSON reponse.
        :param currency_code: The code of the fiat currency (e.g. EUR).

        :return: The JSON response parsed as a dict.
        """
        result: Dict[str, Dict[str, float]] = {}
        raw_data: Dict[str, Any] = data.get("data", {})
        currency_code: str = currency_code.upper()

        for ticker, data in raw_data.items():
            quote: Dict[str, Any] = data.get("quote", {}).get(currency_code, {})
        
            result[ticker] = {
                "price": float(quote.get("price", 0)),
                "1h_change": float(quote.get("percent_change_1h", 0)),
                "24h_change": float(quote.get("percent_change_24h", 0)),
                "market_cap": float(quote.get("market_cap", 0)),
                "24h_volume": float(quote.get("volume_24h", 0)),
        }
        return result