"""Base model với các trường chung."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class cho tất cả models."""
    pass


class TimestampMixin:
    """Mixin cung cấp created_at và updated_at."""
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin cho soft delete."""
    is_deleted = Column(Integer, default=0, nullable=False)  # 0 = active, 1 = deleted
