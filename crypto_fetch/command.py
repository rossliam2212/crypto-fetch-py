from abc import ABC, abstractmethod

from crypto_fetch.api_client import BaseAPIClient


class Command(ABC):
    """Base class for all cli commands"""

    def __init__(self, client: BaseAPIClient = None):
        self.client = client

    @abstractmethod
    def _validate(self) -> None:
        """
        Validate supplied command arguments.

        :raise CommandError: if an error occurs during validation.
        """
        pass

    @abstractmethod
    def _execute(self) -> None:
        """
        Executes the command.

        :raise CommandError: if an error occurs during execution.
        """
        pass

    def run(self) -> None:
        self._validate()
        self._execute()
