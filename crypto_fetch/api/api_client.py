import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, TypeVar

import requests  # type: ignore

from crypto_fetch.config.config import get_api_key, get_default_api_timeout
from crypto_fetch.constants import CF_LOGGER, CG_COIN_ID_MAP
from crypto_fetch.exceptions import APIError

T = TypeVar('T')
logger = logging.getLogger(CF_LOGGER)


@dataclass
class APIConfig:
    """Config for API endpoints."""

    name: str
    base_url: str
    price_endpoint: str

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
        except APIError:
            raise
        except Exception as ex:
            raise APIError(f"Failed to fetch price for '{ticker}: {ex}'") from ex

    def fetch_multiple_price_data(self, tickers: str, currency_code: str) -> Dict[str, Dict[str, float]]:
        try:
            logger.debug(f"Fetching price data for tickers: '{tickers}'")

            api_key: str = self._get_api_key()
            headers: Dict[str, str] = self._get_request_headers(api_key)
            params: Dict[str, str] = self._get_request_params(tickers, currency_code)

            data = self._make_request(headers, params)
            return self._parse_json_response(data, currency_code)
        except APIError:
            raise
        except Exception as ex:
            raise APIError(f"Failed to fetch price for '{tickers}: {ex}'") from ex
        

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
            logger.debug(f"Parsed JSON response for '{ticker}': '{quote}'")

            result[ticker] = {
                "price": float(quote.get("price", 0)),
                "1h_change": float(quote.get("percent_change_1h", 0)),
                "24h_change": float(quote.get("percent_change_24h", 0)),
                "7d_change": float(quote.get("percent_change_7d", 0)),
                "market_cap": float(quote.get("market_cap", 0)),
                "24h_volume": float(quote.get("volume_24h", 0)),
        }
        return result
    
    def _validate_api_key_format(self, api_key: str):
        # cmc key contains letters, numbers and hyphens (usually UUID format, 32 chars + 4 hyphens) 
        if len(api_key) < 32:
            raise APIError(f"Invalid {self.config.name} key. Too short: {len(api_key)} characters")

        if not re.match(r'^[a-zA-Z0-9-]+$', api_key):
            raise APIError(f"Invalid characters detected in {self.config.name} API key")


# =========================================================================================================
# CoinGeckoAPIClient
# =========================================================================================================
class CoinGeckoAPIClient(BaseAPIClient[Dict[str, Dict[str, float]]]):
    """Impl of the BaseAPIClient class for the CoinGecko API."""
    
    def fetch_single_price_data(self, ticker: str, currency_code: str) -> float:
        try:
            logger.debug(f"Fetching price data for ticker: '{ticker}'")

            api_key: str = self._get_api_key()
            coin_id: str = self._ticker_to_coin_id(ticker)
            headers: Dict[str, str] = self._get_request_headers(api_key)
            params: Dict[str, str] = self._get_request_params(coin_id, currency_code)

            data = self._make_request(headers, params)
            return data[coin_id][currency_code.lower()]
        except Exception as ex:
            raise Exception(f"{str(ex)}")

    def fetch_multiple_price_data(self, tickers: str, currency_code: str) -> Dict[str, Dict[str, float]]:
        try:
            logger.debug(f"Fetching price data for tickers: '{tickers}'")

            api_key: str = self._get_api_key()
            ticker_list = [t.strip() for t in tickers.split(",")]
            coin_ids = ",".join([self._ticker_to_coin_id(t) for t in ticker_list])
            headers: Dict[str, str] = self._get_request_headers(api_key)
            params: Dict[str, str] = self._get_request_params(coin_ids, currency_code)

            data = self._make_request(headers, params)
            return self._parse_json_response(data, currency_code, ticker_list)
        except Exception as ex:
            raise Exception(f"{str(ex)}")

    def _get_request_headers(self, api_key: str) -> Dict[str, str]:
        return {
            "accept": "application/json",
            "x_cg_demo_api_key": api_key
        }
    
    def _get_request_params(self, coin_ids: str, currency_code: str) -> Dict[str, str]:
        params = {
            "ids": coin_ids,
            "vs_currencies": currency_code.lower(),
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
        }
        return params
    
    def _parse_json_response(self, data: Dict[str, Any], currency_code: str, tickers: list) -> Dict[str, Dict[str, float]]:
        result: Dict[str, Dict[str, float]] = {}
        currency_lower = currency_code.lower()

        for ticker in tickers:
            coin_id = self._ticker_to_coin_id(ticker)
            coin_data = data.get(coin_id, {})
            logger.debug(f"Parsed JSON response for '{coin_id}': '{coin_data}'")
            
            result[ticker.upper()] = {
                "price": float(coin_data.get(currency_lower, 0)),
                # "1h_change": float(coin_data.get(f"{currency_lower}_1h_change", 0)),
                "24h_change": float(coin_data.get(f"{currency_lower}_24h_change", 0)),
                # "7d_change": float(coin_data.get(f"{currency_lower}_7d_change", 0)),
                "market_cap": float(coin_data.get(f"{currency_lower}_market_cap", 0)),
                "24h_volume": float(coin_data.get(f"{currency_lower}_24h_vol", 0)),
            }
        return result

    def _validate_api_key_format(self, api_key: str):
        # CG key format: CG-<24 alphanumeric characters>
        if not api_key.startswith("CG-"):
            raise APIError(f"Invalid {self.config.name} key. Must start with 'CG-'")
        
        if len(api_key) != 27:
            raise APIError(f"Invalid {self.config.name} key. Expected 27 characters, got {len(api_key)}")

        if not re.match(r'^CG-[a-zA-Z0-9]+$', api_key):
            raise APIError(f"Invalid characters detected in {self.config.name} API key")

    def _ticker_to_coin_id(self, ticker: str) -> str:
        ticker_upper = ticker.upper()
        coin_id = CG_COIN_ID_MAP.get(ticker_upper)

        if not coin_id:
            logger.warning(f"Ticker '{ticker}' not in mapping. Using lowercase as ID")
            return ticker.lower()

        return coin_id