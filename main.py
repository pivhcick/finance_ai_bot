"""
Точка входа в приложение.
Запуск Telegram бота.
"""

import signal
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.bot import handlers
from src.database.repository import init_database

logger = setup_logger(__name__)


def main() -> None:
    """Основная функция запуска бота"""

    logger.info("Starting Trading Signals Bot...")

    try:
        # Инициализация базы данных
        logger.info("Initializing database...")
        init_database()

        # Создание приложения
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

        # Регистрация обработчиков команд
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        application.add_handler(CommandHandler("subscribe", handlers.subscribe_command))
        application.add_handler(CommandHandler("unsubscribe", handlers.unsubscribe_command))
        application.add_handler(CommandHandler("status", handlers.status_command))

        # Регистрация обработчика ошибок
        application.add_error_handler(handlers.error_handler)

        logger.info("Bot handlers registered successfully")

        # Graceful shutdown handler
        def shutdown_handler(sig, frame):
            logger.info("Shutting down gracefully...")
            sys.exit(0)

        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        # Запуск бота
        logger.info("Bot is starting to poll...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Fatal error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
