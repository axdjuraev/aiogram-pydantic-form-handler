import logging
from typing import Optional


class ProxyLogger(logging.Logger):
    _DEFAULT_LOGGER_NAME = 'pydantic-base-aiogram'

    def __init__(self, *, logger: Optional[logging.Logger] = None, name: Optional[str] = None) -> None:
        self._logger = logger
        self._logger_name = name or self._DEFAULT_LOGGER_NAME

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(self._logger_name)

        return self._logger

    def isEnabledFor(self, level: int) -> bool:
        return self.logger.isEnabledFor(level)
    
    def log(self, *args, **kwargs) -> None:
        self.logger.log(*args, **kwargs)

    def _log(self, *args, **kwargs) -> None:
        self.logger._log(*args, **kwargs)

