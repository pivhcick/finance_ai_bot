"""
Репозиторий для работы с базой данных.
Реализует паттерн Repository для абстракции работы с БД.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from src.database.models import Base, User, Signal
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Database:
    """Класс для управления подключением к БД"""

    def __init__(self, database_url: str):
        """
        Инициализация подключения к БД

        Args:
            database_url: URL подключения к базе данных
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        logger.info(f"Database connection initialized: {database_url.split('@')[0]}")

    def create_tables(self) -> None:
        """Создание всех таблиц в БД"""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")

    def get_session(self) -> Session:
        """
        Получение сессии БД

        Returns:
            Session: Сессия SQLAlchemy
        """
        return self.SessionLocal()


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, db: Database):
        """
        Инициализация репозитория

        Args:
            db: Объект Database
        """
        self.db = db

    def create_user(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: str
    ) -> User:
        """
        Создание нового пользователя

        Args:
            telegram_id: Telegram ID пользователя
            username: Username пользователя
            first_name: Имя пользователя

        Returns:
            User: Созданный пользователь
        """
        session = self.db.get_session()
        try:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                subscribed=False,
                subscription_type='all'
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Created new user: {telegram_id} ({username})")
            return user
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            raise
        finally:
            session.close()

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Получение пользователя по Telegram ID

        Args:
            telegram_id: Telegram ID пользователя

        Returns:
            Optional[User]: Пользователь или None
        """
        session = self.db.get_session()
        try:
            stmt = select(User).where(User.telegram_id == telegram_id)
            user = session.execute(stmt).scalar_one_or_none()
            return user
        except Exception as e:
            logger.error(f"Error getting user by telegram_id: {e}")
            raise
        finally:
            session.close()

    def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: str
    ) -> User:
        """
        Получение существующего или создание нового пользователя

        Args:
            telegram_id: Telegram ID пользователя
            username: Username пользователя
            first_name: Имя пользователя

        Returns:
            User: Пользователь
        """
        user = self.get_user_by_telegram_id(telegram_id)
        if user:
            return user
        return self.create_user(telegram_id, username, first_name)

    def update_subscription_status(
        self,
        telegram_id: int,
        subscribed: bool,
        subscription_type: str = 'all'
    ) -> Optional[User]:
        """
        Обновление статуса подписки пользователя

        Args:
            telegram_id: Telegram ID пользователя
            subscribed: Статус подписки
            subscription_type: Тип подписки ('all', 'crypto', 'stocks', 'etf')

        Returns:
            Optional[User]: Обновленный пользователь или None
        """
        session = self.db.get_session()
        try:
            stmt = select(User).where(User.telegram_id == telegram_id)
            user = session.execute(stmt).scalar_one_or_none()

            if user:
                user.subscribed = subscribed
                user.subscription_type = subscription_type
                user.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(user)
                logger.info(f"Updated subscription for user {telegram_id}: subscribed={subscribed}")
                return user
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating subscription: {e}")
            raise
        finally:
            session.close()

    def get_all_subscribed_users(self) -> List[User]:
        """
        Получение всех подписанных пользователей

        Returns:
            List[User]: Список подписанных пользователей
        """
        session = self.db.get_session()
        try:
            stmt = select(User).where(User.subscribed == True)
            result = session.execute(stmt).scalars().all()
            return list(result)
        except Exception as e:
            logger.error(f"Error getting subscribed users: {e}")
            raise
        finally:
            session.close()

    def get_subscribed_users_count(self) -> int:
        """
        Получение количества подписанных пользователей

        Returns:
            int: Количество подписанных пользователей
        """
        session = self.db.get_session()
        try:
            stmt = select(User).where(User.subscribed == True)
            result = session.execute(stmt).scalars().all()
            return len(list(result))
        except Exception as e:
            logger.error(f"Error getting subscribed users count: {e}")
            raise
        finally:
            session.close()


class SignalRepository:
    """Репозиторий для работы с сигналами"""

    def __init__(self, db: Database):
        """
        Инициализация репозитория

        Args:
            db: Объект Database
        """
        self.db = db

    def create_signal(
        self,
        symbol: str,
        asset_type: str,
        signal_type: str,
        price: float,
        confidence: int,
        indicators_data: dict,
        stop_loss: float,
        take_profit_1: float,
        take_profit_2: Optional[float],
        max_hold_days: int
    ) -> Signal:
        """
        Создание нового сигнала

        Args:
            symbol: Символ актива
            asset_type: Тип актива ('crypto', 'stock', 'etf')
            signal_type: Тип сигнала ('BUY', 'SELL')
            price: Цена
            confidence: Уверенность (60-100)
            indicators_data: Данные индикаторов
            stop_loss: Стоп-лосс
            take_profit_1: Первая цель
            take_profit_2: Вторая цель
            max_hold_days: Максимальное время удержания

        Returns:
            Signal: Созданный сигнал
        """
        session = self.db.get_session()
        try:
            signal = Signal(
                symbol=symbol,
                asset_type=asset_type,
                signal_type=signal_type,
                price=price,
                confidence=confidence,
                indicators_data=indicators_data,
                stop_loss=stop_loss,
                take_profit_1=take_profit_1,
                take_profit_2=take_profit_2,
                max_hold_days=max_hold_days
            )
            session.add(signal)
            session.commit()
            session.refresh(signal)
            logger.info(f"Created new signal: {symbol} {signal_type} at ${price}")
            return signal
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating signal: {e}")
            raise
        finally:
            session.close()

    def get_unsent_signals(self) -> List[Signal]:
        """
        Получение неотправленных сигналов

        Returns:
            List[Signal]: Список неотправленных сигналов
        """
        session = self.db.get_session()
        try:
            stmt = select(Signal).where(
                Signal.sent_to_users == False,
                Signal.is_active == True
            )
            result = session.execute(stmt).scalars().all()
            return list(result)
        except Exception as e:
            logger.error(f"Error getting unsent signals: {e}")
            raise
        finally:
            session.close()

    def mark_signal_as_sent(self, signal_id: int) -> None:
        """
        Пометить сигнал как отправленный

        Args:
            signal_id: ID сигнала
        """
        session = self.db.get_session()
        try:
            stmt = select(Signal).where(Signal.id == signal_id)
            signal = session.execute(stmt).scalar_one_or_none()

            if signal:
                signal.sent_to_users = True
                session.commit()
                logger.info(f"Signal {signal_id} marked as sent")
        except Exception as e:
            session.rollback()
            logger.error(f"Error marking signal as sent: {e}")
            raise
        finally:
            session.close()


# Глобальные объекты для использования в приложении
db = Database(Config.DATABASE_URL)
user_repository = UserRepository(db)
signal_repository = SignalRepository(db)


def init_database() -> None:
    """Инициализация базы данных (создание таблиц)"""
    db.create_tables()
    logger.info("Database initialized successfully")
