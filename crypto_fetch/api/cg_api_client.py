import logging
import re
from typing import Any, Dict

import requests  # type: ignore

from crypto_fetch.api.api_client import BaseAPIClient
from crypto_fetch.constants import CF_LOGGER, CG_COIN_ID_MAP
from crypto_fetch.exceptions import APIError

logger = logging.getLogger(CF_LOGGER)


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
        except APIError:
            raise
        except Exception as ex:
            raise APIError(f"Failed to fetch price for '{ticker}': {ex}") from ex

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
        except APIError:
            raise
        except Exception as ex:
            raise APIError(f"Failed to fetch prices for '{tickers}': {ex}") from ex

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

    def _parse_json_response(self, data: Dict[str, Any], currency_code: str, tickers: list) -> Dict[
        str, Dict[str, float]]:
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