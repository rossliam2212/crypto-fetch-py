from abc import ABC, abstractmethod
from typing import Optional

from crypto_fetch.api.api_client import BaseAPIClient


class Command(ABC):
    """Base class for all cli commands"""

    def __init__(self, client: Optional[BaseAPIClient] = None):
        """
        :param client: The API client to use for the command.
        """
        self.client = client

    def _validate(self) -> None:
        """
        Validates supplied command arguments. No-op by default; override to add validation.

        :raises CommandError: If an error occurs during validation.
        """
        pass

    def _setup(self) -> None:
        """
        Sets up resources required before execution (e.g. building the API client).
        Called by run() after _validate() and before _execute(). No-op by default.
        """
        pass

    @abstractmethod
    def _execute(self) -> None:
        """
        Executes the command.

        :raises CommandError: If an error occurs during execution.
        """
        pass

    def run(self) -> None:
        """
        Runs the command: validates, sets up, then executes.

        :raises CommandError: If any phase fails.
        """
        self._validate()
        self._setup()
        self._execute()
