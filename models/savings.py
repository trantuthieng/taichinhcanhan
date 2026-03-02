"""Savings models - Tiền gửi tiết kiệm."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Date
from models.base import Base, TimestampMixin, SoftDeleteMixin


class SavingsDeposit(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "savings_deposits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    bank_name = Column(String(100), nullable=False)
    principal_amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="VND")
    open_date = Column(Date, nullable=False)
    term_months = Column(Integer, nullable=False)
    maturity_date = Column(Date, nullable=False)
    interest_rate = Column(Float, nullable=False)  # % năm
    interest_type = Column(String(20), nullable=False, default="maturity")  # prepaid, monthly, maturity
    compound_interest = Column(Integer, default=0, nullable=False)  # nhập gốc
    auto_renew = Column(Integer, default=0, nullable=False)
    status = Column(String(20), nullable=False, default="active")  # active, matured, closed, renewed
    tax_rate = Column(Float, default=0.0, nullable=False)  # thuế lãi tiết kiệm
    fee = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<SavingsDeposit(id={self.id}, bank='{self.bank_name}', amount={self.principal_amount})>"


class SavingsInterestEvent(Base, TimestampMixin):
    __tablename__ = "savings_interest_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    savings_id = Column(Integer, ForeignKey("savings_deposits.id"), nullable=False, index=True)
    event_type = Column(String(30), nullable=False)  # interest_payment, maturity, renewal, early_close
    amount = Column(Float, nullable=False)
    event_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
