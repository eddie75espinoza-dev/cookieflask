import os
import sys
from loguru import logger


log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

app_log_path = os.path.join(log_dir, "{{ cookiecutter.project_name }}.log")

logger.remove()

# Configuración
logger.add(
    app_log_path,
    level="DEBUG",
    backtrace=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    rotation="500 MB",
    retention=5,
    compression="gz",
)

# Consola
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
)
