import logging
import sys

from crypto_fetch.constants import CF_LOGGER, CYAN, RED, ORANGE, RESET

LEVEL_COLORS = {
    logging.DEBUG:   CYAN,
    logging.WARNING: ORANGE,
    logging.ERROR:   RED,
}


class LogLevelFormatter(logging.Formatter):
    """Custom formatter that applies level-based colors and format."""

    def __init__(self, fmt_info: str, fmt_debug: str):
        """
        :param fmt_info: Format string for INFO level messages.
        :param fmt_debug: Format string for DEBUG, WARNING and ERROR level messages.
        """
        super().__init__()
        self.fmt_info = logging.Formatter(fmt_info)
        self.fmt_debug = logging.Formatter(fmt_debug)

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record, applying a level-based color to the level name.

        :param record: The log record to format.
        :return: The formatted log message string.
        """
        if record.levelno == logging.INFO:
            return self.fmt_info.format(record)
        return self._format_with_color(record)

    def _format_with_color(self, record: logging.LogRecord) -> str:
        """
        Formats a log record with a colorized level name.

        :param record: The log record to format.
        :return: The formatted log message string with a colored level name.
        """
        color = LEVEL_COLORS.get(record.levelno, "")
        original_levelname = record.levelname
        record.levelname = f"{color}[{record.levelname}]{RESET}"
        msg = self.fmt_debug.format(record)
        record.levelname = original_levelname
        return msg


def setup_logger(debug: bool = False) -> None:
    """
    Sets up the application logger.

    :param debug: Whether debug logging should be enabled or not.
    """
    logger = logging.getLogger(CF_LOGGER)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    if logger.handlers:
        return

    fmt = LogLevelFormatter(
        fmt_info="%(message)s",
        fmt_debug="[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    stdout_handler.addFilter(lambda r: r.levelno < logging.ERROR)
    stdout_handler.setFormatter(fmt)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(fmt)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
    logger.debug(f"{CF_LOGGER} logger initialized")
