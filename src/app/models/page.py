from datetime import datetime

from sqlalchemy import Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.app.db import Base


class Page(Base):
    __tablename__ = 'pages'

    """
    Страница (профиль) пользователя или сущности.

    Связи:
    - users (One-to-Many) <- User.page_id
    - moderators (One-to-Many) <- PageModerator.page_id
    - tree (Many-to-One) -> Tree через `tree_id`
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    tree_id: Mapped[int] = mapped_column(ForeignKey("tree.id"), nullable=False)

    bread1: Mapped[str] = mapped_column(String(255), nullable=False)
    bread2: Mapped[str] = mapped_column(String(255), nullable=False)
    bread3: Mapped[str] = mapped_column(String(255), nullable=False)

    main_gen: Mapped[int] = mapped_column(Integer, nullable=False)
    main_gen_child: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)
    
    # relationships
    users = relationship("User", back_populates="page")
    moderators = relationship("PageModerator", back_populates="page", cascade="all, delete-orphan")
    tree = relationship("Tree", back_populates="pages")

class PageModerator(Base):
    __tablename__ = 'page_moderator'

    """
    Связующая таблица модераторов страниц.

    Связи:
    - page (Many-to-One) -> Page через `page_id`
    - user (Many-to-One) -> User через `user_id`
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=True)
    
    # relationships
    page = relationship("Page", back_populates="moderators")
    user = relationship("User", back_populates="page_moderations")

