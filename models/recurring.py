"""Recurring Transaction model - Giao dịch định kỳ."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Date
from models.base import Base, TimestampMixin


class RecurringTransaction(Base, TimestampMixin):
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True)
    type = Column(String(20), nullable=False)  # income, expense
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="VND")
    description = Column(Text, nullable=True)
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    next_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Integer, default=1, nullable=False)
