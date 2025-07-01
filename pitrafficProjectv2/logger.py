# logger.py
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Ensure logs/ directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logger
logger = logging.getLogger("TrafficLogger")
logger.setLevel(logging.INFO)

log_file_path = os.path.join(LOG_DIR, "traffic_log.log")
handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=7)
handler.suffix = "%Y-%m-%d"
formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)

# Convenience method
def log(msg):
    logger.info(msg)

# Usage example: log("Starting traffic control")
