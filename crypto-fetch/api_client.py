import os
import requests

from .constants import API_BASE
from .constants import API_KEY_ENV_VAR
from .constants import DEFAULT_FIAT

def fetch_crypto_price(tickers, currency="EUR"):
    """
    Fetch the price of a cryptocurrency from the CMC API.
    If no fiat currency is speicifed, the default fiat is EUR (€).
    """
    api_key = _get_api_key()

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "d953ca60-947c-479d-8962-87c9d41a0487"
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
    Retrieve the CMC API key stored in the COINMARKETCAP_API_KEY environment variable.
    """
    api_key = os.getenv("COINMARKETCAP_API_KEY")

    # TODO Add error handling
    return api_key

def _parse_json_response(data, currency):
    """
    Parse the JSON response received from the CMC API.
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
