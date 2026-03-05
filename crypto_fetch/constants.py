from colorama import Fore, Style
from typing import Final

# =========================================================================================================
# Application Configuration
# =========================================================================================================
CF_NAME: Final[str] = "crypto-fetch"
CF_VERSION: Final[str] = "1.0.0"

# =========================================================================================================
# API Configuration
# =========================================================================================================
CMC_API_NAME: Final[str] = "coinmarketcap"
CMC_API_BASE: Final[str] = "https://pro-api.coinmarketcap.com/v1"
CMC_API_LATEST_EP: Final[str] = "/cryptocurrency/quotes/latest"
CMC_API_KEY_ENV_VAR: Final[str] = "COINMARKETCAP_API_KEY"

CG_API_NAME: Final[str] = "coingecko"
CG_API_BASE: Final[str] = "https://api.coingecko.com/api/v3/"
CG_API_LATEST_EP: Final[str] = "/simple/price"
CG_API_KEY_ENV_VAR: Final[str] = "COINGECKO_API_KEY"

# =========================================================================================================
# Currency Configuration (Map of all supported fiat currencies [code -> symbol])
# =========================================================================================================
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

CG_COIN_ID_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "XRP": "ripple",
        "BNB": "binancecoin",
        "SOL": "solana",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "DOT": "polkadot",
        "MATIC": "matic-network",
        "LTC": "litecoin",
        "AVAX": "avalanche-2",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "XLM": "stellar",
        "ATOM": "cosmos",
        "HBAR": "hedera-hashgraph",
        "ALGO": "algorand",
        "VET": "vechain",
        "ICP": "internet-computer",
        "FIL": "filecoin",
    }

# =========================================================================================================
# Display Configuration
# =========================================================================================================
RED_OUTPUT = Fore.RED
GREEN_OUTPUT = Fore.GREEN
BOLD_OUTPUT = Style.BRIGHT
RESET_OUTPUT = Style.RESET_ALL

# =========================================================================================================
# Formatting Configuration
# =========================================================================================================
PRECISION_HIGH: Final[int] = 2
PRECISION_MEDIUM: Final[int] = 1
PRECISION_LOW: Final[int] = 0