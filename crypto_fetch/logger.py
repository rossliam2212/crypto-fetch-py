import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

from crypto_fetch.constants import CF_LOGGER

LEVEL_STYLES = {
    logging.DEBUG:   "cyan",
    logging.WARNING: "color(208)",
    logging.ERROR:   "red",
}

_stdout_console = Console(stderr=False)
_stderr_console = Console(stderr=True)


class RichLevelFormatter(logging.Formatter):
    """Formats log records in the format: [timestamp] [LEVEL] [file:line] message"""

    _plain = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        if record.levelno == logging.INFO:
            return record.getMessage()

        plain = self._plain.format(record)
        style = LEVEL_STYLES.get(record.levelno, "")
        text = Text(plain)
        level_tag = f"[{record.levelname}]"
        start = plain.index(level_tag)
        text.stylize(style, start, start + len(level_tag))
        return text.markup


class _RichHandler(RichHandler):
    def emit(self, record: logging.LogRecord) -> None:
        console = _stderr_console if record.levelno >= logging.ERROR else _stdout_console
        try:
            msg = self.format(record)
            console.print(msg, markup=True, highlight=False)
        except Exception:
            self.handleError(record)


def setup_logger(debug: bool = False) -> None:
    """
    Sets up the application logger.

    :param debug: Whether debug logging should be enabled or not.
    """
    logger = logging.getLogger(CF_LOGGER)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    if logger.handlers:
        return

    handler = _RichHandler(show_time=False, show_level=False, show_path=False)
    handler.setFormatter(RichLevelFormatter())
    logger.addHandler(handler)
    logger.debug(f"{CF_LOGGER} logger initialized")
