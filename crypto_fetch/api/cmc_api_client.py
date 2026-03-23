import logging
import re
from typing import Any, Dict

from crypto_fetch.api.api_client import BaseAPIClient
from crypto_fetch.constants import CF_LOGGER
from crypto_fetch.exceptions import APIError

logger = logging.getLogger(CF_LOGGER)


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
            raise APIError(f"Failed to fetch price for '{ticker}': {ex}") from ex

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
            raise APIError(f"Failed to fetch price for '{tickers}': {ex}") from ex

    def _get_request_headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Accept": "application/json",
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
        logger.debug(f"Validating API key format: '{api_key}'")
        if len(api_key) < 32:
            raise APIError(f"Invalid {self.config.name} key. Too short: {len(api_key)} characters")

        if not re.match(r'^[a-zA-Z0-9-]+$', api_key):
            raise APIError(f"Invalid characters detected in {self.config.name} API key")
