from enum import Enum

from .logger import get_logger


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Log:
    def __init__(self) -> None:
        self.logger = get_logger()

    def debug(self, message: str, **kwargs):
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        self.logger.critical(message, **kwargs)


log = Log()
