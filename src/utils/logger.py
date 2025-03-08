import os
import sys
import json
import logging
import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

LOG_DIR = Path("logs")
DEFAULT_LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
_config = None

class JsonSink:
    def __init__(self, file_path):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def write(self, message):
        record = message.record
        log_entry = {
            "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "level": record["level"].name,
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "process_id": record["process"].id,
            "thread_id": record["thread"].id
        }

        if record["extra"]:
            log_entry["extra"] = record["extra"]

        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

def _get_config():
    global _config

    if _config is None:
        try:
            from src.utils.config import get_config
            _config = get_config()
        except ImportError:
            class DefaultConfig:
                log_level = "INFO"
            _config = DefaultConfig()

    return _config

def setup_logger():
    LOG_DIR.mkdir(exist_ok=True)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"bot_{today}.log"
    json_log_file = LOG_DIR / f"bot_{today}.json"

    config = _get_config()
    log_level = os.getenv("LOG_LEVEL", config.log_level)

    logger.remove()

    logger.add(
        sys.stdout,
        format=DEFAULT_LOG_FORMAT,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    logger.add(
        log_file,
        format=DEFAULT_LOG_FORMAT,
        level=log_level,
        rotation="10 MB",
        retention=5,
        compression="zip",
        backtrace=True,
        diagnose=True
    )

    logger.add(
        JsonSink(str(json_log_file)),
        level=log_level,
        serialize=True
    )

    setup_standard_logging()

    logger.info(f"Sistema de logging inicializado (nível: {log_level})")

    return logger

def get_logger(name=None):
    return logger.bind(name=name)

class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

def setup_standard_logging():
    config = _get_config()
    log_level = os.getenv("LOG_LEVEL", config.log_level)

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for logger_name in ["discord", "asyncio"]:
        logging.getLogger(logger_name).setLevel(getattr(logging, log_level))
