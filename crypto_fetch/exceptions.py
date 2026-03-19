class CryptoFetchError(Exception):
    """Base exception for all crypto-fetch errors."""
    pass


class APIError(CryptoFetchError):
    """Exception for API related errors."""
    pass


class CommandError(CryptoFetchError):
    """Exception for Command related errors."""
    pass


class ConfigError(CryptoFetchError):
    """Exception for Config related errors."""
    pass