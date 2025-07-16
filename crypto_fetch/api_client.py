import os
import requests

from crypto_fetch.constants import API_BASE
from crypto_fetch.constants import API_KEY_ENV_VAR

def fetch_crypto_price(tickers, currency):
    """
    Fetches the latest data related to one or more cryptocurrencies.

    Args:
        tickers: The cryptocurrency ticker symbols to fetch.
        currency: The fiat currency which the data will be in.

    Returns:
        The API response formatted as a dict.
    """
    api_key = _get_api_key()

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key
    }
    params = {
        "symbol": tickers,
        "convert": currency.upper()
    }

    try:
        response = requests.get(
            f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
            headers=headers,
            params=params,
            timeout=10
        )
        data = response.json()
        
        # TODO Add error handling
        return _parse_json_response(data, currency)
    except requests.exceptions.RequestException as e:
        raise APIResponseError(f"Network error: {str(e)}") from e

def _get_api_key():
    """
    Gets the CMC API key stored in the COINMARKETCAP_API_KEY environment variable.

    Returns:
        The CMC API key stored in the environment variable.
    """
    api_key = os.getenv("COINMARKETCAP_API_KEY")

    # TODO Add error handling
    return api_key

def _parse_json_response(data, currency):
    """
    Parse the JSON response received from the CMC API.

    Args:
        data: The JSON response received from the API.
        currency: The fiat currency the data is in.

    Returns:
        A formatted dict containing the response data.
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
