from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, func, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.app.db import Base
from enum import Enum

class TicketType(Enum):
    add_data = "add_data"
    edit_data = "edit_data"

class TicketStatus(Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Ticket(Base):
    __tablename__ = "tickets"

    """
    Заявка на изменение/добавление данных.

    Связи:
    - created_by_user (Many-to-One) -> User через `created_by`
    - answered_by_user (Many-to-One) -> User через `answered_by`
    - add_data_items (One-to-Many) <- TicketAddData.ticket_id
    - edit_data_items (One-to-Many) <- TicketEditData.ticket_id
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_type: Mapped[str] = mapped_column(SQLEnum(TicketType), nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(TicketStatus), nullable=False)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    answered_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # relationships
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="created_tickets")
    answered_by_user = relationship("User", foreign_keys=[answered_by], back_populates="answered_tickets")
    add_data_items = relationship("TicketAddData", back_populates="ticket", cascade="all, delete-orphan")
    edit_data_items = relationship("TicketEditData", back_populates="ticket", cascade="all, delete-orphan")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)


class TicketAddData(Base):
    __tablename__ = "ticket_add_data"

    """
    Данные для заявки на добавление нового узла.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    
    # relationships
    ticket = relationship("Ticket", back_populates="add_data_items")
    parent_id: Mapped[int] = mapped_column(Integer, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)

class TicketEditData(Base):
    __tablename__ = "ticket_edit_data"

    """
    Данные для заявки на редактирование существующего узла.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)

    tree_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # relationships
    ticket = relationship("Ticket", back_populates="edit_data_items")
    new_name: Mapped[str] = mapped_column(String(255), nullable=False)
    new_bio: Mapped[str] = mapped_column(String(255), nullable=True)
    new_birth: Mapped[str] = mapped_column(String(255), nullable=True)
    new_death: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)
