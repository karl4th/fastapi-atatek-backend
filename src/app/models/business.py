from datetime import datetime

from sqlalchemy import Integer, String, DateTime, func, Float, JSON, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.app.db import Base


class Tariff(Base):
    __tablename__ = 'tariffs'

    """
    Тариф подписки.

    Связи:
    - subscriptions (One-to-Many) <- UserSubscription.tariff_id
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    settings: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<Tariff {self.name}>"
    
    # relationships
    subscriptions = relationship("UserSubscription", back_populates="tariff", cascade="all, delete-orphan")

class UserSubscription(Base):
    __tablename__ = 'subscriptions'

    """
    Подписка пользователя на тариф.

    Связи:
    - tariff (Many-to-One) -> Tariff через `tariff_id`
    - user (Many-to-One) -> User через `user_id`
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"))

    personal_settings: Mapped[dict] = mapped_column(JSON, nullable=False)

    start_date: Mapped[datetime]
    end_date: Mapped[datetime]

    is_active: Mapped[bool]

    # relationships
    tariff = relationship("Tariff", back_populates="subscriptions")
    user = relationship("User", back_populates="subscriptions")