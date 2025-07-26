from typing import Final

from crypto_fetch.api_client import APIConfig

# Base CMC API
CMC_API_BASE: Final[str] = "https://pro-api.coinmarketcap.com/v1"
CMC_API_LATEST_EP: Final[str] = "/cryptocurrency/quotes/latest"
# Environment var CMC API is expected
CMC_API_KEY_ENV_VAR: Final[str] = "COINMARKETCAP_API_KEY"

# Map of all supported fiat currencies [code -> symbol]
CURRENCY_SYMBOL_MAP = {
    "EUR": "€",
    "GBP": "£",
    "USD": "$",
    "CAD": "$",
    "AUD": "$",
    "NZD": "$",
    "HKD": "$",
    "CLP": "$",   # Chilean Peso
    "COP": "$",   # Colombian Peso
    "MXN": "$",   # Mexican Peso
    "CUP": "$",   # Cuban Peso
    "DOP": "$",   # Dominican Peso
    "CNY": "¥",   # Chinese Yuan
    "JPY": "¥",   # Japanese Yen
    "CHF": "Fr",  # Swiss Franc
    "NOK": "kr",  # Norwegian Krone
    "DKK": "kr",  # Danish Krone
    "SEK": " kr", # Swedish Krona
    "HUF": "Ft"   # Hungarian Forint
}

CURRENCY_CODE_ONLY_MAP = {
    "CHF": "Fr",  # Swiss Franc
    "NOK": "kr",  # Norwegian Krone
    "DKK": "kr",  # Danish Krone
    "SEK": " kr", # Swedish Krona
    "HUF": "Ft"   # Hungarian Forint
}