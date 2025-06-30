import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_filename():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"traffic_{date_str}.log")

def log(msg: str):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_msg = f"{timestamp} {msg}"
    print(full_msg)
    with open(get_log_filename(), "a") as f:
        f.write(full_msg + "\n")
