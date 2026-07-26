import logging

from src.core.ConsoleHandler import ConsoleHandler
from src.core.CustomFileHandler import CustomFileHandler


class Logger(logging.Logger):

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.setLevel(logging.DEBUG)
        self.propagate = False

        self.addHandler(ConsoleHandler())
        self.addHandler(CustomFileHandler())

    def info(self, msg: str, **kwargs) -> None:
        self._custom_log(logging.INFO, msg, **kwargs)

    def debug(self, msg: str, **kwargs) -> None:
        self._custom_log(logging.DEBUG, msg, **kwargs)

    def warning(self, msg: str, **kwargs) -> None:
        self._custom_log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs) -> None:
        self._custom_log(logging.ERROR, msg, **kwargs)

    def critical(self, msg: str, **kwargs) -> None:
        self._custom_log(logging.CRITICAL, msg, **kwargs)

    def _custom_log(self,level: int,msg: str,**kwargs) -> None:

        if not self.isEnabledFor(level):
            return

        message = self.merge_msg_and_additional_info(msg,kwargs)

        self._log(level,message,())
        

    def get_additional_info(self,kwargs: dict) -> str:

        if not kwargs:
            return ""
        
    
        return " | ".join(
            f"{key}: {value}"
            for key, value in kwargs.items()
        )

    def merge_msg_and_additional_info(self,msg: str,kwargs: dict) -> str:

        additional_info = self.get_additional_info(kwargs)

        if additional_info == "":
            return msg
    
        return (
            f"{msg} | "
            f"{additional_info}"
        )