import os
import requests

from crypto_fetch.constants import API_BASE
from crypto_fetch.constants import API_KEY_ENV_VAR
from crypto_fetch.constants import API_LATEST_EP
from crypto_fetch.exceptions import APIKeyError
from crypto_fetch.exceptions import APIResponseError

def fetch_crypto_price(ticker, currency_code):
    """
    Fetches the price of a cryptocurrency.

    Args:
        - ticker (str): The ticker of the cryptocurrency to fetch.
        - currency_code (str): The fiat currency to get the price in.

    Returns:
        - The price of the cryptocurrency. 
    """
    try:
        api_key = _get_api_key()

        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key
        }
        params = {
            "symbol": ticker,
            "convert": currency_code.upper()
        }

        response = requests.get(
            f"{API_BASE}{API_LATEST_EP}",
            headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code != 200:
            error_msg = response.json().get("status", {}).get("error_message", "Unknown API error")
            raise APIResponseError(error_msg)
        
        data = response.json()
        
        price = data['data'][ticker]['quote'][currency_code]['price']
        return price
    except requests.exceptions.RequestException as ex:
        raise APIResponseError(f"{str(ex)}") from ex
    except Exception as ex:
        raise Exception(f"{str(ex)}") from ex

def fetch_crypto_price_data(tickers, currency):
    """
    Fetches the latest data related to one or more cryptocurrencies.
    
    Args:
        - tickers (list): A list of cryptocurrency ticker symbol(s).
        - currency (str): The fiat currency code to retriece the data in.

    Returns:
        - The API response formatted as a dict.
    """
    try:
        api_key = _get_api_key()

        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": api_key
        }
        params = {
            "symbol": tickers,
            "convert": currency.upper()
        }

        response = requests.get(
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

def _get_api_key():
    """
    Gets the CMC API key stored in the 'COINMARKETCAP_API_KEY' environment variable.

    Returns:
        - The CMC API key stored in the environment variable.
    """
    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        raise APIKeyError(f"Could not find CMC API key in the '{API_KEY_ENV_VAR}' env var")
    
    return api_key

def _parse_json_response(data, currency):
    """
    Parse the JSON response received from the CMC API.

    Args:
        - data (dict): The JSON response received from the API.
        - currency (str): The fiat currency code the data is in.

    Returns:
        - A formatted dict containing the response data.
    """
    result = {}
    raw_data = data.get("data", {})
    currency = currency.upper()

    for ticker, data in raw_data.items():
        quote = data.get("quote", {}).get(currency, {})
        
        result[ticker] = {
            "price": quote.get("price", 0),
            "1h_change": quote.get("percent_change_1h", 0),
            "24h_change": quote.get("percent_change_24h", 0),
            "market_cap": quote.get("market_cap", 0),
            "24h_volume": quote.get("volume_24h", 0),
        }
    
    return result
