"""User Settings model - Cài đặt người dùng."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from models.base import Base, TimestampMixin


class UserSetting(Base, TimestampMixin):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
