import os
import sys
from loguru import logger
from datetime import date
from dotenv import load_dotenv

load_dotenv()

log_dir = os.getenv("LOG_DIR")
log_file = os.getenv("LOG_FILE", "app.log")
os.makedirs(log_dir, exist_ok=True)

app_log_path = os.path.join(log_dir, f"{date.today()}-{log_file}")

logger.remove()

# Configuration
logger.add(
    app_log_path,
    level=os.getenv("LOG_LEVEL", "DEBUG"),
    backtrace=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
    rotation=os.getenv("LOG_MAX_MB", "100MB"),
    retention=int(os.getenv("LOG_BACKUP_COUNT", 5)),
    compression="gz",
)

# Console
logger.add(
    sys.stdout,
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
    colorize=False
)

logger.add(
    sys.stderr,
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
    colorize=False
)

# Configure standard logging to use loguru
import logging

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Interceptor logs of Flask/Werkzeug/Gunicorn
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Gunicorn configuration
for name in ["gunicorn", "gunicorn.access", "gunicorn.error", "werkzeug"]:
    gunicorn_logger = logging.getLogger(name)
    gunicorn_logger.handlers = [InterceptHandler()]