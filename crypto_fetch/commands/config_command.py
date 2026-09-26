import logging
from pathlib import Path
from typing import Optional

import yaml  # type: ignore

from crypto_fetch.commands.command import Command
from crypto_fetch.config.config import CONFIG_FILE_PATH, DEFAULT_API_CONFIG, init_api_config_file, save_api_config_to_file
from crypto_fetch.config.config_validator import validate_config
from crypto_fetch.constants import CF_LOGGER, CMD_CONFIG_INIT, CMD_CONFIG_RECREATE, CMD_CONFIG_VALIDATE
from crypto_fetch.exceptions import ConfigError

logger = logging.getLogger(CF_LOGGER)


class ConfigCommand(Command):
    """Manage config file"""

    def __init__(self, action: str, force: bool = False, path: Optional[str] = None):
        """
        :param action: The config action to perform (init, validate, recreate).
        :param force: If True, skips confirmation checks (used by init and recreate).
        :param path: Optional path to a config file to validate (used by validate).
        """
        super().__init__(client=None)
        self.action = action
        self.force = force
        self.path = path


    def _execute(self) -> None:
        logger.debug(f"Executing config action: '{self.action}'")
        if self.action == CMD_CONFIG_INIT:
            self._handle_init_action()
        elif self.action == CMD_CONFIG_VALIDATE:
            self._handle_validate_action()
        elif self.action == CMD_CONFIG_RECREATE:
            self._handle_recreate_action()


    def _handle_init_action(self) -> None:
        """
        Creates the config file with default values.
        If the file already exists, skips unless --force is passed.
        """
        if CONFIG_FILE_PATH.exists() and not self.force:
            logger.info(f"Config file already exists at: '{CONFIG_FILE_PATH}'. Use --force to overwrite")
            return
        init_api_config_file()


    def _handle_validate_action(self) -> None:
        """
        Reads and validates the config file, logging any errors found.

        :raises ConfigError: If the file is missing, empty, has YAML errors, or fails validation.
        """
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


    def _handle_recreate_action(self) -> None:
        """
        Recreates the config file with default values.
        Skips confirmation if --force is passed.
        """
        if not self.force:
            confirm = input("This will overwrite your existing config. Continue? [y/N]: ").strip().lower()
            if confirm != "y":
                logger.info("Recreate cancelled")
                return
        save_api_config_to_file(DEFAULT_API_CONFIG)
        logger.info(f"Config file recreated at: '{CONFIG_FILE_PATH}' ✅")
        logger.info("*** Remember to add your API keys ***")