class APIKeyError(Exception):
    """ Exception for API key releated errors. """

    """
    Constructs an APIKeyError exception.

    :param message: The exception message.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message

class APIResponseError(Exception):
    """ Exception for API response related errors. """

    """
    Constructs an APIResponseError exception.

    :param message: The exception message.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message