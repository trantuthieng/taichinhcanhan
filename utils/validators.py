"""Validators - Validate input cho ứng dụng."""

import re
from datetime import datetime, date
from typing import Optional


def validate_amount(value) -> tuple:
    """Validate số tiền. Returns (is_valid, cleaned_value, error_msg)."""
    if value is None:
        return False, 0, "Số tiền không được để trống"
    try:
        # Hỗ trợ cả dấu chấm và dấu phẩy
        if isinstance(value, str):
            value = value.strip().replace(".", "").replace(",", ".")
        val = float(value)
        if val < 0:
            return False, 0, "Số tiền không được âm"
        if val > 999_999_999_999:
            return False, 0, "Số tiền quá lớn"
        return True, val, ""
    except (ValueError, TypeError):
        return False, 0, "Số tiền không hợp lệ"


def validate_required(value: str, field_name: str) -> tuple:
    """Validate trường bắt buộc."""
    if not value or not str(value).strip():
        return False, f"{field_name} không được để trống"
    return True, ""


def validate_username(username: str) -> tuple:
    """Validate tên đăng nhập."""
    if not username or len(username.strip()) < 3:
        return False, "Tên đăng nhập ít nhất 3 ký tự"
    if len(username) > 50:
        return False, "Tên đăng nhập tối đa 50 ký tự"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Tên đăng nhập chỉ chứa chữ cái, số và dấu gạch dưới"
    return True, ""


def validate_password(password: str) -> tuple:
    """Validate mật khẩu."""
    if not password or len(password) < 6:
        return False, "Mật khẩu ít nhất 6 ký tự"
    return True, ""


def validate_date_range(start: Optional[date], end: Optional[date]) -> tuple:
    """Validate khoảng thời gian."""
    if start and end and start > end:
        return False, "Ngày bắt đầu phải trước ngày kết thúc"
    return True, ""


def validate_interest_rate(rate: float) -> tuple:
    """Validate lãi suất (%)."""
    if rate < 0:
        return False, "Lãi suất không được âm"
    if rate > 100:
        return False, "Lãi suất không hợp lệ (> 100%)"
    return True, ""


def validate_month_year(month: int, year: int) -> tuple:
    """Validate tháng/năm."""
    if month < 1 or month > 12:
        return False, "Tháng không hợp lệ"
    if year < 2000 or year > 2100:
        return False, "Năm không hợp lệ"
    return True, ""
