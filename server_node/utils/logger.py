# server_node/utils/logger.py
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from config import settings

def get_logger(name: str):
    log_path = Path(settings.LOG_DIR) / f"{name.lower()}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:      # evita duplicados
        return logger

    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    fmt = logging.Formatter(
        "%(asctime)s | %(processName)s | %(levelname)s | %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    file_h = TimedRotatingFileHandler(log_path, when="midnight", backupCount=7)
    file_h.setFormatter(fmt)
    logger.addHandler(file_h)

    if settings.LOG_LEVEL.upper() == "DEBUG":
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        logger.addHandler(console)

    return logger
