from abc import ABC, abstractmethod

from crypto_fetch.api.api_client import BaseAPIClient


class Command(ABC):
    """Base class for all cli commands"""

    def __init__(self, client: BaseAPIClient = None):
        """
        :param client: The API client to use for the command.
        """
        self.client = client

    @abstractmethod
    def _validate(self) -> None:
        """
        Validates supplied command arguments.

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
