"""Transaction schemas."""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


VALID_TX_TYPES = ["income", "expense", "transfer", "adjustment"]


class TransactionCreate(BaseModel):
    account_id: int
    to_account_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    type: str
    amount: float
    currency: str = "VND"
    description: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    transaction_date: datetime

    @field_validator("type")
    @classmethod
    def type_valid(cls, v: str) -> str:
        if v not in VALID_TX_TYPES:
            raise ValueError(f"Loại giao dịch không hợp lệ: {v}")
        return v

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        return v


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    transaction_date: Optional[datetime] = None
