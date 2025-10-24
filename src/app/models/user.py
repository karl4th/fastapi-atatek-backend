from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.app.db import Base


class User(Base):
    __tablename__ = 'users'

    """
    Пользователь системы.

    Связи:
    - role (Many-to-One) -> Role через `role_id`
    - address (Many-to-One) -> Address через `address_id`
    - page (Many-to-One) -> Page через `page_id`
    - created_tickets (One-to-Many) <- Ticket.created_by
    - answered_tickets (One-to-Many) <- Ticket.answered_by
    - page_moderations (One-to-Many) <- PageModerator.user_id
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(50), nullable=True)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1)
    address_id: Mapped[int] = mapped_column(ForeignKey("address.id", ondelete="SET NULL"), nullable=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="SET NULL"), nullable=True)

    phone: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)

    # relationships
    role = relationship("Role", back_populates="users")
    address = relationship("Address", back_populates="users")
    page = relationship("Page", back_populates="users")

    created_tickets = relationship("Ticket", back_populates="created_by_user", foreign_keys="Ticket.created_by")
    answered_tickets = relationship("Ticket", back_populates="answered_by_user", foreign_keys="Ticket.answered_by")

    created_tree = relationship("Tree", back_populates="created_by_user", foreign_keys="Tree.created_by")
    updated_tree = relationship("Tree", back_populates="updated_by_user", foreign_keys="Tree.updated_by")

    page_moderations = relationship("PageModerator", back_populates="user")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
