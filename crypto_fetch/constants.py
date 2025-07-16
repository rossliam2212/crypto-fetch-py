# Base CMC API
API_BASE = "https://pro-api.coinmarketcap.com/v1"

# Environment var CMC API is expected
API_KEY_ENV_VAR = "COINMARKETCAP_API_KEY"

DEFAULT_FIAT = "EUR"

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