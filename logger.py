import logging
from datetime import datetime as dt
from pathlib import Path

LOGS_DIR = "logs"
dir = Path(LOGS_DIR)
dir.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

handler = logging.FileHandler(
    (str(dir) + "/log_" + dt.now().strftime("%Y%m%d") + ".log"),
    encoding="utf-8",
    mode="a",
)
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(fmt=formatter)
logger.addHandler(hdlr=handler)
