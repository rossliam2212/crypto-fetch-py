class APIError(Exception):
    """Exception for API related errors."""

    def __init__(self, message: str):
        """
        Constructs an APIError exception.

        :param message: The exception message.
        """
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class CommandError(Exception):
    """Exception for Command related errors."""

    def __init__(self, message: str):
        """
        Constructs an CommandError exception.

        :param message: The exception message.
        """
        self.message = message
        super().__init__(message)


class ConfigError(Exception):
    """Exception for Config related errors."""

    def __init__(self, message: str):
        """
        Constructs an ConfigError exception.

        :param message: The exception message.
        """
        self.message = message
        super().__init__(message)