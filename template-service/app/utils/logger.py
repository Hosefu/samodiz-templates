import os
import sys
from loguru import logger

def setup_logging():
    """
    Настраивает логирование с помощью loguru
    """
    # Получаем уровень логирования из переменной окружения или используем INFO по умолчанию
    log_level = os.getenv("TEMPLATE_SERVICE_LOG_LEVEL", "INFO").upper()
    
    # Удаляем стандартный обработчик
    logger.remove()
    
    # Добавляем обработчик для вывода в stdout с форматированием
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level=log_level,
        colorize=True
    )
    
    # Добавляем обработчик для записи в файл
    logger.add(
        "logs/template-service.log",
        rotation="10 MB",
        retention="3 days",
        level=log_level
    )
    
    logger.info(f"Logging initialized with level: {log_level}")