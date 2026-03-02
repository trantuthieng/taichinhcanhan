"""Stock model - Nắm giữ chứng khoán."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Date
from models.base import Base, TimestampMixin, SoftDeleteMixin


class StockHolding(Base, TimestampMixin, SoftDeleteMixin):
    """Một lệnh mua cổ phiếu / chứng chỉ quỹ."""
    __tablename__ = "stock_holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    ticker = Column(String(20), nullable=False, index=True)     # VD: VNM, FPT, FUESSVFL
    name = Column(String(120), nullable=True)                    # Tên công ty / quỹ
    exchange = Column(String(20), nullable=True, default="HOSE") # HOSE, HNX, UPCOM
    quantity = Column(Float, nullable=False)                     # Số lượng CP
    avg_price = Column(Float, nullable=False)                    # Giá vốn trung bình
    current_price = Column(Float, nullable=True)                 # Giá thị trường (cập nhật thủ công)
    buy_date = Column(Date, nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<StockHolding(id={self.id}, ticker='{self.ticker}', qty={self.quantity})>"
