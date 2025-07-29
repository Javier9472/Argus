import logging
import os
from config import constants

os.makedirs(os.path.dirname(constants.LOG_PATH), exist_ok=True)

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(constants.LOG_PATH)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, constants.LOG_LEVEL.upper(), logging.INFO))

        if constants.LOG_LEVEL.upper() == "DEBUG":
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger