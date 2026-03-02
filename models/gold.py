"""Gold models - Giá vàng và nắm giữ vàng."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Date
from models.base import Base, TimestampMixin, SoftDeleteMixin


class GoldPrice(Base, TimestampMixin):
    __tablename__ = "gold_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    gold_type = Column(String(50), nullable=False, index=True)
    buy_price = Column(Float, nullable=True)
    sell_price = Column(Float, nullable=True)
    unit = Column(String(20), nullable=False, default="lượng")
    source = Column(String(50), nullable=False)
    fetched_at = Column(DateTime, nullable=False)


class GoldHolding(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "gold_holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    gold_type = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="lượng")
    buy_price = Column(Float, nullable=False)  # Giá vốn mỗi đơn vị
    buy_date = Column(Date, nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<GoldHolding(id={self.id}, type='{self.gold_type}', qty={self.quantity})>"
