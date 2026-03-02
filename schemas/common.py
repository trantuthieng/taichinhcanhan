"""Common schemas - Base models."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema."""
    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 20


class DateRangeFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
