"""User schemas."""

from pydantic import BaseModel, field_validator
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str
    email: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Tên đăng nhập phải có ít nhất 3 ký tự")
        if not v.isalnum() and "_" not in v:
            raise ValueError("Tên đăng nhập chỉ gồm chữ, số và _")
        return v

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Mật khẩu mới phải có ít nhất 6 ký tự")
        return v
