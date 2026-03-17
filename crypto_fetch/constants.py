from colorama import Fore, Style # type: ignore
from typing import Final, List

# =========================================================================================================
# Application Configuration
# =========================================================================================================
CF_NAME: Final[str] = "crypto-fetch"
CF_VERSION: Final[str] = "1.0.0"
CF_LOGGER: Final[str] = "crypto_fetch"

PROVIDER_COINMARKETCAP: Final[str] = "coinmarketcap"
PROVIDER_COINGECKO: Final[str] = "coingecko"
PROVIDERS_SUPPORTED = [PROVIDER_COINMARKETCAP, PROVIDER_COINGECKO] 

# =========================================================================================================
# Config Key Configuration
# =========================================================================================================
CONFIG_HEADER_DEFAULTS: Final[str] = "defaults"
CONFIG_HEADER_API_KEYS: Final[str] = "api_keys"

CONFIG_KEY_PROVIDER_NAME: Final[str] = "name"
CONFIG_KEY_PROVIDER_ENV_VAR: Final[str] = "env_var"
CONFIG_KEY_PROVIDER_BASE_URL: Final[str] = "base_url"
CONFIG_KEY_PROVIDER_PRICE_EP: Final[str] = "price_ep"
REQUIRED_PROVIDER_CONFIG_KEYS: Final[List[str]] = [
    CONFIG_KEY_PROVIDER_NAME, 
    CONFIG_KEY_PROVIDER_ENV_VAR, 
    CONFIG_KEY_PROVIDER_BASE_URL, 
    CONFIG_KEY_PROVIDER_PRICE_EP
]
CONFIG_KEY_DEFAULTS_CURRENCY: Final[str] = "currency"
CONFIG_KEY_DEFAULTS_API_TIMEOUT: Final[str] = "api_timeout"
CONFIG_KEY_DEFAULTS_API_PROVIDER: Final[str] = "api_provider"

CONFIG_DEFAULTS_CURRENCY: Final[str] = "EUR"
CONFIG_DEFAULTS_API_TIMEOUT: Final[int] = 10

# =========================================================================================================
# Command Configuration
# =========================================================================================================
CMD_PRICE: Final[str] = "price"
CMD_CONVERT: Final[str] = "convert"
CMD_PORTFOLIO: Final[str] = "portfolio"
CMD_CONFIG: Final[str] = "config"
CMD_CONFIG_INIT: Final[str] = "init"
CMD_CONFIG_VALIDATE: Final[str] = "validate"
CMD_CONFIG_RECREATE: Final[str] = "recreate"

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

SUPPORTED_CRYPTO_TICKERS = {
    "BTC", "ETH", "XRP", "BNB", "SOL", "ADA", "DOGE", "DOT", 
    "MATIC", "LTC", "AVAX", "LINK", "UNI", "XLM", "ATOM", 
    "HBAR", "ALGO", "VET", "ICP", "FIL"
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
# Formatting / Display Configuration
# =========================================================================================================
PRECISION_HIGH: Final[int] = 2
PRECISION_MEDIUM: Final[int] = 1
PRECISION_LOW: Final[int] = 0

RED_OUTPUT = Fore.RED
GREEN_OUTPUT = Fore.GREEN
BOLD_OUTPUT = Style.BRIGHT
RESET_OUTPUT = Style.RESET_ALL
