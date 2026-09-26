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

    @abstractmethod
    def _execute(self) -> None:
        """
        Executes the command.

        :raises CommandError: If an error occurs during execution.
        """
        pass

    def run(self) -> None:
        """
        Runs the command, validates it and executes it.

        :raises CommandError: If validation or execution fails.
        """
        self._validate()
        self._execute()
