import os
import requests
from typing import Dict, Any

from crypto_fetch.constants import API_BASE
from crypto_fetch.constants import API_KEY_ENV_VAR
from crypto_fetch.constants import API_LATEST_EP
from crypto_fetch.exceptions import APIKeyError
from crypto_fetch.exceptions import APIResponseError

def fetch_crypto_price(ticker: str, currency_code: str) -> float:
    """
    Fetches the price data of a cryptocurrency.

    :param ticker: The ticker of the cryptocurrency to fetch.
    :param currency_code: The fiat currency to get the price in.

    :returns: The price of the cryptocurrency. 
    """
    try:
        api_key: str = _get_api_key()

        headers: Dict[str, str] = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key
        }
        params = {
            "symbol": ticker,
            "convert": currency_code.upper()
        }

        response: requests.Response = requests.get(
            f"{API_BASE}{API_LATEST_EP}",
            headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code != 200:
            error_msg = response.json().get("status", {}).get("error_message", "Unknown API error")
            raise APIResponseError(error_msg)
        
        data = response.json()
        
        price: float = data['data'][ticker]['quote'][currency_code]['price']
        return price
    except requests.exceptions.RequestException as ex:
        raise APIResponseError(f"{str(ex)}") from ex
    except Exception as ex:
        raise Exception(f"{str(ex)}") from ex

def fetch_crypto_price_data(tickers: list, currency: str) -> Dict[str, Dict[str, float]]:
    """
    Fetches the price data related to one or more cryptocurrencies.
    
    :param tickers: A list of cryptocurrency ticker symbol(s).
    :param currency: The fiat currency code to retriece the data in.

    :returns: The API response formatted as a dict.
    """
    try:
        api_key:str = _get_api_key()

        headers: Dict[str, str] = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key
        }
        params = {
            "symbol": tickers,
            "convert": currency.upper()
        }

        response: requests.Response = requests.get(
            f"{API_BASE}{API_LATEST_EP}",
            headers=headers,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            error_msg = response.json().get("status", {}).get("error_message", "Unknown API error")
            raise APIResponseError(error_msg)
        
        data = response.json()
        return _parse_json_response(data, currency)
    except requests.exceptions.RequestException as ex:
        raise APIResponseError(f"{str(ex)}") from ex
    except Exception as ex:
        raise Exception(f"{str(ex)}") from ex

def _get_api_key() -> str:
    """
    Gets the CMC API key stored in the 'COINMARKETCAP_API_KEY' environment variable.

    :returns: The CMC API key stored in the environment variable.
    """
    api_key: str = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        raise APIKeyError(f"Could not find CMC API key in the '{API_KEY_ENV_VAR}' env var")
    
    return api_key

def _parse_json_response(data: dict, currency: str) -> Dict[str, Dict[str, float]]:
    """
    Parse the JSON response received from the CMC API.

    :param data: The JSON response received from the API.
    :param currency: The fiat currency code the data is in.

    :returns: A formatted dict containing the response data.
    """
    result: Dict[str, Dict[str, float]] = {}
    raw_data: Dict[str, Any] = data.get("data", {})
    currency: str = currency.upper()

    for ticker, data in raw_data.items():
        quote: Dict[str, Any] = data.get("quote", {}).get(currency, {})
        
        result[ticker] = {
            "price": float(quote.get("price", 0)),
            "1h_change": float(quote.get("percent_change_1h", 0)),
            "24h_change": float(quote.get("percent_change_24h", 0)),
            "market_cap": float(quote.get("market_cap", 0)),
            "24h_volume": float(quote.get("volume_24h", 0)),
        }
    
    return result
