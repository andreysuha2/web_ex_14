from app.db import Base
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from contacts.models import Contact

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(250), unique=True)
    password: Mapped[str] = mapped_column(String)
    avatar: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    contacts: Mapped[List["Contact"]] = relationship(back_populates="user")
    tokens: Mapped[List["Token"]] = relationship(back_populates="user")
    confirmed_at: Mapped[bool] = mapped_column(DateTime, nullable=True)

class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), onupdate='CASCADE')
    user: Mapped["User"] = relationship(back_populates="tokens")
    