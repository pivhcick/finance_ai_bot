"""
Обработчики команд Telegram бота.
"""

from telegram import Update
from telegram.ext import ContextTypes
from src.bot.messages import Messages
from src.utils.logger import setup_logger
from src.database.repository import user_repository

logger = setup_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start

    Args:
        update: Объект обновления от Telegram
        context: Контекст выполнения
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")

    await update.message.reply_text(Messages.START)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /help

    Args:
        update: Объект обновления от Telegram
        context: Контекст выполнения
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) requested help")

    await update.message.reply_text(Messages.HELP)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /subscribe
    Подписка пользователя на рассылку сигналов

    Args:
        update: Объект обновления от Telegram
        context: Контекст выполнения
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) attempting to subscribe")

    try:
        # Получаем или создаем пользователя
        db_user = user_repository.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name or "Unknown"
        )

        # Проверяем, не подписан ли уже
        if db_user.subscribed:
            await update.message.reply_text(Messages.ALREADY_SUBSCRIBED)
            logger.info(f"User {user.id} is already subscribed")
            return

        # Подписываем пользователя
        user_repository.update_subscription_status(
            telegram_id=user.id,
            subscribed=True,
            subscription_type='all'
        )

        await update.message.reply_text(Messages.SUBSCRIBE_SUCCESS)
        logger.info(f"User {user.id} subscribed successfully")

    except Exception as e:
        logger.error(f"Error in subscribe_command: {e}", exc_info=True)
        await update.message.reply_text(Messages.ERROR)


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /unsubscribe
    Отписка пользователя от рассылки

    Args:
        update: Объект обновления от Telegram
        context: Контекст выполнения
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) attempting to unsubscribe")

    try:
        # Получаем пользователя из БД
        db_user = user_repository.get_user_by_telegram_id(user.id)

        if not db_user or not db_user.subscribed:
            await update.message.reply_text(Messages.NOT_SUBSCRIBED)
            logger.info(f"User {user.id} was not subscribed")
            return

        # Отписываем пользователя
        user_repository.update_subscription_status(
            telegram_id=user.id,
            subscribed=False
        )

        await update.message.reply_text(Messages.UNSUBSCRIBE_SUCCESS)
        logger.info(f"User {user.id} unsubscribed successfully")

    except Exception as e:
        logger.error(f"Error in unsubscribe_command: {e}", exc_info=True)
        await update.message.reply_text(Messages.ERROR)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /status
    Проверка статуса подписки пользователя

    Args:
        update: Объект обновления от Telegram
        context: Контекст выполнения
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) checking status")

    try:
        # Получаем пользователя из БД
        db_user = user_repository.get_user_by_telegram_id(user.id)

        if not db_user or not db_user.subscribed:
            await update.message.reply_text(Messages.STATUS_NOT_SUBSCRIBED)
            return

        # Формируем сообщение со статусом
        subscription_date = db_user.created_at.strftime('%d.%m.%Y')
        # TODO: В будущем добавить подсчет полученных сигналов
        signals_count = 0

        status_message = Messages.STATUS_SUBSCRIBED.format(
            subscription_date=subscription_date,
            signals_count=signals_count
        )

        await update.message.reply_text(status_message)
        logger.info(f"User {user.id} checked status: subscribed")

    except Exception as e:
        logger.error(f"Error in status_command: {e}", exc_info=True)
        await update.message.reply_text(Messages.ERROR)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик ошибок

    Args:
        update: Объект обновления от Telegram
        context: Контекст выполнения
    """
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(Messages.ERROR)
