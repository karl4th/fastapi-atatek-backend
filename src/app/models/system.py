from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.app.db import Base


class Role(Base):
    __tablename__ = 'roles'

    """
    Роль пользователя.

    Связи:
    - users (One-to-Many) <- User.role_id
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<Role {self.name}>"

    # relationships
    users = relationship("User", back_populates="role")



class Address(Base):
    __tablename__ = 'address'

    """
    Адрес, связанный с пользователями.

    Связи:
    - users (One-to-Many) <- User.address_id
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    osm: Mapped[str] = mapped_column(nullable=False) 
    lat: Mapped[float] = mapped_column(nullable=False)
    lon: Mapped[float] = mapped_column(nullable=False)
    address_type: Mapped[str] = mapped_column(nullable=False) 
    name: Mapped[str] = mapped_column(nullable=False)
    display_name: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # relationships
    users = relationship("User", back_populates="address")
