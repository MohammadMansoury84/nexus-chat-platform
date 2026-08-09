import logging


class CustomFileHandler(logging.FileHandler):
    def __init__(self):
        log_file = "logfile.log"
        super().__init__(log_file, encoding="UTF-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%m/%d/%Y %H:%M:%S",
        )
        self.setFormatter(formatter)
        self.setLevel(logging.INFO)
