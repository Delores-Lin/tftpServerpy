import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs")
    # 从内到外获取父目录，最终取得项目根目录，记录logs目录
os.makedirs(LOG_DIR, exist_ok=True)
    # 创建log文件夹

log_path = os.path.join(LOG_DIR, f"tftp_server.log")

logger = logging.getLogger("tftp")
logger.setLevel(logging.DEBUG)

# 彩色控制台
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG" :   "\33[37m",
        "INFO"  :   "\33[36m",
        "WARNING":  "\33[33m",
        "ERROR" :   "\33[31m",
        "CRITICAL": "\33[41;97m",
    }
    RESET = "\33[0m"
    
    # 格式化输出，以换行分割使得只有第一行染色，其他行颜色正常
    def format(self, record):
        base = super().format(record)
        if "\n" in base:
            first, rest = base.split("\n", 1)
            color = self.COLORS.get(record.levelname, "")
            return f"{color}{first}{self.RESET}\n{rest}"
        color = self.COLORS.get(record.levelname, "")
        return f"{color}{base}{self.RESET}"


if not logger.handlers:
    # 按时间轮转，保留一周的log
    fh = TimedRotatingFileHandler(
        log_path, 
        when = "midnight",
        interval = 1,
        backupCount=7,
        encoding="utf-8",
        utc = False
    )
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # 控制台中显示部分
    color_fmt = ColorFormatter(
        "%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(color_fmt)
    logger.addHandler(ch)