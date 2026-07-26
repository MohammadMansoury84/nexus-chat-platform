
import logging

class ConsoleHandler(logging.StreamHandler):
    def __init__(self, level: int = logging.DEBUG) -> None:
        super().__init__()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%m/%d/%Y %H:%M:%S",
        )
        self.setFormatter(formatter)
        self.setLevel(level)