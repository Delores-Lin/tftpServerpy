import logging
import os
from datetime import datetime

LOG_DIR = os.path(os.path.dirname(os.path.dirname(__file__)),"logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, f"tftp_server_{datetime.now():%Y-%m-%d}.log")

logger = logging.getLogger("tftp")
logger.set_level(logging.INFO)

if not logger.handlers:
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(messages)s"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)