"""Account model - Tài khoản tài chính."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from models.base import Base, TimestampMixin, SoftDeleteMixin


class Account(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    account_type = Column(String(20), nullable=False)  # cash, bank, ewallet, forex, gold, savings, other
    currency = Column(String(10), nullable=False, default="VND")
    balance = Column(Float, nullable=False, default=0.0)
    initial_balance = Column(Float, nullable=False, default=0.0)
    description = Column(Text, nullable=True)
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
    icon = Column(String(10), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, name='{self.name}', type='{self.account_type}')>"
