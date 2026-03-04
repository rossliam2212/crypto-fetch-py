import logging
import sys

class LogLevelFormatter(logging.Formatter):
    """Custom formatter that uses differnt formats based on log level"""
    def __init__(self, fmt_info: str, fmt_debug: str):
        super().__init__()
        self.fmt_info = logging.Formatter(fmt_info)
        self.fmt_debug = logging.Formatter(fmt_debug)

    def format(self, record):
        if record.levelno == logging.DEBUG or record.levelno == logging.ERROR:
            return self.fmt_debug.format(record)
        return self.fmt_info.format(record)

def setup_logger(debug: bool = False) -> logging.Logger:
    """
    Sets up the application logger.
    
    :param debug: Whether debug logging should be enabled or not.
    :return: the configured logger instance.
    """
    logger = logging.getLogger("crypto_fetch")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if debug else logging.INFO)

        formatter = LogLevelFormatter(
            fmt_info="%(message)s",
            fmt_debug="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger