"""
Настройка логирования для приложения.
"""

import logging
import sys
from typing import Optional
from src.utils.config import Config


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Настройка и получение логгера

    Args:
        name: Имя логгера (обычно __name__ модуля)

    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name or __name__)

    # Если логгер уже настроен, возвращаем его
    if logger.handlers:
        return logger

    # Установка уровня логирования из конфига
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Создание обработчика для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Формат логов
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # Добавление обработчика к логгеру
    logger.addHandler(console_handler)

    # Предотвращение дублирования логов
    logger.propagate = False

    return logger


# Глобальный логгер для приложения
app_logger = setup_logger('finance_ai_bot')
