"""Savings schemas."""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date


class SavingsDepositCreate(BaseModel):
    bank_name: str
    principal_amount: float
    currency: str = "VND"
    open_date: date
    term_months: int
    interest_rate: float
    interest_type: str = "maturity"
    compound_interest: bool = False
    auto_renew: bool = False
    tax_rate: float = 0.0
    fee: float = 0.0
    notes: Optional[str] = None
    account_id: Optional[int] = None

    @field_validator("principal_amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Số tiền gốc phải lớn hơn 0")
        return v

    @field_validator("term_months")
    @classmethod
    def term_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Kỳ hạn phải lớn hơn 0")
        return v

    @field_validator("interest_rate")
    @classmethod
    def rate_valid(cls, v: float) -> float:
        if v < 0 or v > 100:
            raise ValueError("Lãi suất phải từ 0 đến 100%")
        return v

    @field_validator("interest_type")
    @classmethod
    def type_valid(cls, v: str) -> str:
        if v not in ("prepaid", "monthly", "maturity"):
            raise ValueError("Hình thức trả lãi không hợp lệ")
        return v


class SavingsDepositUpdate(BaseModel):
    status: Optional[str] = None
    auto_renew: Optional[bool] = None
    notes: Optional[str] = None
