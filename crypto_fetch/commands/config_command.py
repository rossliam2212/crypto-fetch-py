import logging

import yaml  # type: ignore

from crypto_fetch.commands.command import Command
from crypto_fetch.config.config import CONFIG_FILE_PATH, DEFAULT_API_CONFIG, init_api_config_file, save_api_config_to_file
from crypto_fetch.config.config_validator import validate_config
from crypto_fetch.constants import CF_LOGGER, CMD_CONFIG_INIT, CMD_CONFIG_RECREATE, CMD_CONFIG_VALIDATE
from crypto_fetch.exceptions import ConfigError

logger = logging.getLogger(CF_LOGGER)


class ConfigCommand(Command):
    """Manage config file"""

    def __init__(self, action: str):
        """
        :param action: The config action to perform (init, validate, recreate).
        """
        super().__init__(client=None)
        self.action = action


    def _validate(self) -> None:
        pass


    def _execute(self) -> None:
        logger.debug(f"Executing config action: '{self.action}'")
        if self.action == CMD_CONFIG_INIT:
            init_api_config_file()
        elif self.action == CMD_CONFIG_VALIDATE:
            self._handle_validate_action()
        elif self.action == CMD_CONFIG_RECREATE:
            self._handle_recreate_action()


    def _handle_validate_action(self) -> None:
        """
        Reads and validates the config file, logging any errors found.

        :raises ConfigError: If the file is missing, empty, has YAML errors, or fails validation.
        """
        if not CONFIG_FILE_PATH.exists():
            raise ConfigError("Config file not found. Run 'crypto-fetch config init' to create")
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
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
        """
        save_api_config_to_file(DEFAULT_API_CONFIG)
        logger.info(f"Config file recreated at: '{CONFIG_FILE_PATH}' ✅")
        logger.info("*** Remember to add your API keys ***")