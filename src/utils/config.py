"""
Конфигурация приложения.
Загрузка переменных окружения и настроек проекта.
"""

import os
from typing import List
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()


class Config:
    """Класс конфигурации приложения"""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')

    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./bot_database.db')

    # API Keys (опционально)
    BINANCE_API_KEY: str = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET: str = os.getenv('BINANCE_API_SECRET', '')

    # Settings
    ANALYSIS_INTERVAL_HOURS: int = int(os.getenv('ANALYSIS_INTERVAL_HOURS', '1'))
    MIN_CONFIDENCE: int = int(os.getenv('MIN_CONFIDENCE', '60'))
    TIMEZONE: str = os.getenv('TIMEZONE', 'UTC')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    # Assets to track
    CRYPTO_SYMBOLS: List[str] = os.getenv(
        'CRYPTO_SYMBOLS',
        'BTC-USD,ETH-USD,SOL-USD,DOGE-USD'
    ).split(',')

    STOCK_SYMBOLS: List[str] = os.getenv(
        'STOCK_SYMBOLS',
        'AAPL,TSLA,MSFT,NVDA,AMZN'
    ).split(',')

    ETF_SYMBOLS: List[str] = os.getenv(
        'ETF_SYMBOLS',
        'VTI,TQQQ,SPY,QQQ'
    ).split(',')

    @classmethod
    def validate(cls) -> bool:
        """
        Валидация критических настроек

        Returns:
            bool: True если все критические настройки заполнены
        """
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env файле")

        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL не установлен в .env файле")

        return True

    @classmethod
    def get_all_symbols(cls) -> List[str]:
        """
        Получить все отслеживаемые символы

        Returns:
            List[str]: Список всех символов
        """
        return cls.CRYPTO_SYMBOLS + cls.STOCK_SYMBOLS + cls.ETF_SYMBOLS


# Валидация конфигурации при импорте
Config.validate()
