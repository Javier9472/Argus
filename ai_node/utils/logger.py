import logging
from logging.handlers import TimedRotatingFileHandler
from config.settings import DATA_DIR

LOG_DIR = DATA_DIR / "log"
LOG_DIR.mkdir(exist_ok=True)

def get_logger(name):
    p = LOG_DIR / f"{name}.log"
    h = TimedRotatingFileHandler(p, when="midnight", backupCount=7)
    fmt = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    h.setFormatter(fmt)
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(h)
    return logger
