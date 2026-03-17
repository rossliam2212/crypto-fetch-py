from abc import ABC, abstractmethod
from typing import Any, Dict

from crypto_fetch.api_client import BaseAPIClient
from crypto_fetch.exceptions import CommandError


class Command(ABC):
    """Base class for all cli commands"""

    def __init__(self, client: BaseAPIClient = None):
        self.client = client

    @abstractmethod
    def validate(self) -> None:
        """
        Validate supplied command arguments.

        :raise CommandError: if an error occurs during validation.
        """
        pass
    
    @abstractmethod
    def execute(self) -> Any:
        """
        Executes the command.

        :raise CommandError: if an error occurs during execution.
        """
        pass

    def run(self) -> Any:
        self.validate()
        return self.execute()
