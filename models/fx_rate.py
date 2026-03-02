"""FX Rate model - Tỷ giá ngoại tệ."""

from sqlalchemy import Column, Integer, String, Float, DateTime
from models.base import Base, TimestampMixin


class FxRate(Base, TimestampMixin):
    __tablename__ = "fx_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_code = Column(String(10), nullable=False, index=True)
    currency_name = Column(String(50), nullable=True)
    buy_rate = Column(Float, nullable=True)
    sell_rate = Column(Float, nullable=True)
    transfer_rate = Column(Float, nullable=True)
    source = Column(String(50), nullable=False)  # vnappmob, vietcombank, manual
    fetched_at = Column(DateTime, nullable=False)
