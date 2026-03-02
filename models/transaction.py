"""Transaction model - Giao dịch thu chi."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from models.base import Base, TimestampMixin, SoftDeleteMixin


class Transaction(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # Cho chuyển khoản
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True)
    type = Column(String(20), nullable=False, index=True)  # income, expense, transfer, adjustment
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="VND")
    description = Column(Text, nullable=True)
    tags = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="completed")  # completed, pending, cancelled
    fingerprint = Column(String(64), nullable=True, index=True)  # Chống trùng
    transaction_date = Column(DateTime, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, type='{self.type}', amount={self.amount})>"
