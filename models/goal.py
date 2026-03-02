"""Savings Goal model - Mục tiêu tiết kiệm."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Date
from models.base import Base, TimestampMixin


class SavingsGoal(Base, TimestampMixin):
    __tablename__ = "savings_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, nullable=False, default=0.0)
    deadline = Column(Date, nullable=True)
    priority = Column(Integer, default=0, nullable=False)  # 0=normal, 1=high, 2=urgent
    status = Column(String(20), nullable=False, default="active")  # active, completed, cancelled
    goal_type = Column(String(30), nullable=False, default="general")  # general, emergency, investment
    notes = Column(Text, nullable=True)
