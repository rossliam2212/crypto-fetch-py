import logging
from pathlib import Path
from typing import Optional

import yaml  # type: ignore

from crypto_fetch.commands.command import Command
from crypto_fetch.config.config import CONFIG_FILE_PATH, DEFAULT_API_CONFIG, save_api_config_to_file
from crypto_fetch.config.config_validator import validate_config
from crypto_fetch.constants import CF_LOGGER
from crypto_fetch.exceptions import ConfigError

logger = logging.getLogger(CF_LOGGER)


class InitCommand(Command):
    """Create the config file with default values."""

    def __init__(self, force: bool = False):
        """
        :param force: If True, overwrites an existing config file without prompting.
        """
        super().__init__(client=None)
        self.force = force

    def _execute(self) -> None:
        if CONFIG_FILE_PATH.exists() and not self.force:
            logger.info(f"Config file already exists at: '{CONFIG_FILE_PATH}'. Use --force to overwrite")
            return
        save_api_config_to_file(DEFAULT_API_CONFIG)
        logger.info(f"Config file created at: '{CONFIG_FILE_PATH}'")
        logger.info("Edit this file to add your API keys and set defaults")


class ValidateCommand(Command):
    """Validate the config file."""

    def __init__(self, path: Optional[str] = None):
        """
        :param path: Optional path to a config file to validate. Defaults to the standard config path.
        """
        super().__init__(client=None)
        self.path = path

    def _execute(self) -> None:
        target = Path(self.path) if self.path else CONFIG_FILE_PATH
        if not target.exists():
            raise ConfigError(f"Config file not found at '{target}'. Run 'crypto-fetch config init' to create")
        try:
            with open(target, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            if config is None or not isinstance(config, dict):
                logger.error("Config file is empty or invalid")
                raise ConfigError("Config file is empty or invalid")
        except yaml.YAMLError as ex:
            logger.error(f"Config file has YAML syntax errors: {ex}")
            raise ConfigError(
                f"Config file has YAML syntax errors: {ex}. Run 'crypto-fetch config recreate' to restore defaults")

        errors = validate_config(config)
        if not errors:
            logger.info("API config is valid ✅")
        else:
            logger.error("API config validation failed ❌")
            for error in errors:
                logger.error(f"  - {error}")
            raise ConfigError("Run 'crypto-fetch config recreate' to restore defaults")


class RecreateCommand(Command):
    """Restore the config file to its default values."""

    def __init__(self, force: bool = False):
        """
        :param force: If True, skips the confirmation prompt.
        """
        super().__init__(client=None)
        self.force = force

    def _execute(self) -> None:
        if not self.force:
            confirm = input("This will overwrite your existing config. Continue? [y/N]: ").strip().lower()
            if confirm != "y":
                logger.info("Recreate cancelled")
                return
        save_api_config_to_file(DEFAULT_API_CONFIG)
        logger.info(f"Config file recreated at: '{CONFIG_FILE_PATH}' ✅")
        logger.info("*** Remember to add your API keys ***")
