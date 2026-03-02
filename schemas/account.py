"""Account schemas."""

from pydantic import BaseModel, field_validator
from typing import Optional


VALID_ACCOUNT_TYPES = ["cash", "bank", "ewallet", "forex", "gold", "savings", "other"]


class AccountCreate(BaseModel):
    name: str
    account_type: str
    currency: str = "VND"
    initial_balance: float = 0.0
    description: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    icon: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tên tài khoản không được trống")
        return v

    @field_validator("account_type")
    @classmethod
    def type_valid(cls, v: str) -> str:
        if v not in VALID_ACCOUNT_TYPES:
            raise ValueError(f"Loại tài khoản không hợp lệ. Chọn: {', '.join(VALID_ACCOUNT_TYPES)}")
        return v

    @field_validator("initial_balance")
    @classmethod
    def balance_valid(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Số dư ban đầu không được âm")
        return v


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    is_active: Optional[int] = None
    icon: Optional[str] = None
    balance: Optional[float] = None
