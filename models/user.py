"""User model."""

from sqlalchemy import Column, Integer, String
from models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
