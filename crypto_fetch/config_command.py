from typing import Any
import logging
import sys
import yaml  # type: ignore

from crypto_fetch.command import Command
from crypto_fetch.constants import CF_LOGGER, CMD_CONFIG_INIT, CMD_CONFIG_VALIDATE, CMD_CONFIG_RECREATE
from crypto_fetch.config import CONFIG_FILE, init_api_config_file, save_api_config_to_file, DEFAULT_CONFIG
from crypto_fetch.config_validator import validate_config
from crypto_fetch.exceptions import ConfigError

logger = logging.getLogger(CF_LOGGER)

class ConfigCommand(Command):
    """Manage config file"""

    def __init__(self, action: str):
        super().__init__(client=None)
        self.action = action

    def validate(self) -> None:
        pass

    def execute(self) -> Any:
        if self.action == CMD_CONFIG_INIT:
            init_api_config_file()
        elif self.action == CMD_CONFIG_VALIDATE:
            self._handle_validate_action()
        elif self.action == CMD_CONFIG_RECREATE:
            self._handle_recreate_action()


    def _handle_validate_action(self):
        if not CONFIG_FILE.exists():
            raise FileNotFoundError("Config file not found. Run 'crypto-fetch config init' to create")
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
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
            logger.info("Run 'crypto-fetch config recreate' to restore defaults")
            sys.exit(1)


    def _handle_recreate_action(self):
        save_api_config_to_file(DEFAULT_CONFIG)
        logger.info(f"Config file recreated at: '{CONFIG_FILE}' ✅")
        logger.info("*** Remember to add your API keys ***")