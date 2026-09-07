import logging
import os


def configure():
    match os.getenv("LOG_LEVEL"):
        case "debug":
            log_level = logging.DEBUG
        case "warning":
            log_level = logging.WARNING
        case "error":
            log_level = logging.ERROR
        case _:
            log_level = logging.INFO

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=log_level
    )
