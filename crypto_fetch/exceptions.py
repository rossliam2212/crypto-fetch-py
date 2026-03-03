class APIError(Exception):
    """Exception for API related errors."""

    def __init__(self, message: str):
        """
        Constructs an APIKeyError exception.

        :param message: The exception message.
        """
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message
