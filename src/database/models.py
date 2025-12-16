"""
Модели базы данных SQLAlchemy.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, Boolean, String, Integer, Float, DateTime, JSON, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Модель пользователя бота"""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    subscribed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    subscription_type: Mapped[str] = mapped_column(String(50), default='all', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"


class Signal(Base):
    """Модель торгового сигнала"""

    __tablename__ = 'signals'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'crypto', 'stock', 'etf'
    signal_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'BUY' or 'SELL'
    price: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False)  # 60-100
    indicators_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit_1: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit_2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_hold_days: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sent_to_users: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Signal(id={self.id}, symbol={self.symbol}, type={self.signal_type}, confidence={self.confidence})>"


class Position(Base):
    """
    Модель позиции пользователя (опционально, для будущего использования)
    """

    __tablename__ = 'positions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    signal_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='open', nullable=False)  # 'open', 'closed'
    pnl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Profit and Loss
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Position(id={self.id}, user_id={self.user_id}, signal_id={self.signal_id}, status={self.status})>"
