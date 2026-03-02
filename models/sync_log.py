"""Sync Log model - Log đồng bộ dữ liệu từ API."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime, timezone
from models.base import Base


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), nullable=False)
    scope = Column(String(30), nullable=False)  # exchange_rate, gold
    status = Column(String(20), nullable=False)  # success, error, fallback
    message = Column(Text, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
