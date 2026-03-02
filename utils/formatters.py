"""Formatters - Định dạng tiền tệ, số, ngày giờ Việt Nam."""

from datetime import datetime, date
from typing import Optional, Union
import locale


def format_currency(amount: Union[int, float], currency: str = "VND", show_symbol: bool = True) -> str:
    """Định dạng tiền tệ Việt Nam.
    1234567.89 → '1.234.568 ₫' hoặc '1,234.57 $'
    """
    if amount is None:
        return "0 ₫" if currency == "VND" else "0"

    symbols = {"VND": "₫", "USD": "$", "EUR": "€", "JPY": "¥", "GBP": "£", "CNY": "¥", "KRW": "₩"}
    symbol = symbols.get(currency, currency)

    if currency == "VND":
        # VND: không thập phân, dấu chấm phân cách hàng nghìn
        val = int(round(amount))
        negative = val < 0
        val = abs(val)
        s = f"{val:,}".replace(",", ".")
        if negative:
            s = "-" + s
        return f"{s} {symbol}" if show_symbol else s
    else:
        # Ngoại tệ: 2 thập phân, dấu phẩy phân cách hàng nghìn
        negative = amount < 0
        val = abs(amount)
        s = f"{val:,.2f}"
        if negative:
            s = "-" + s
        return f"{symbol}{s}" if show_symbol else s


def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """Format số với dấu chấm phân cách hàng nghìn (kiểu VN)."""
    if value is None:
        return "0"
    if decimals == 0:
        s = f"{int(round(value)):,}".replace(",", ".")
    else:
        s = f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def format_date(dt: Optional[Union[datetime, date]], fmt: str = "dd/mm/yyyy") -> str:
    """Định dạng ngày."""
    if dt is None:
        return ""
    if fmt == "dd/mm/yyyy":
        return dt.strftime("%d/%m/%Y")
    elif fmt == "dd/mm/yyyy HH:MM":
        return dt.strftime("%d/%m/%Y %H:%M")
    elif fmt == "yyyy-mm-dd":
        return dt.strftime("%Y-%m-%d")
    return dt.strftime("%d/%m/%Y")


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format phần trăm."""
    if value is None:
        return "0%"
    return f"{value:.{decimals}f}%"


def format_weight(grams: float) -> str:
    """Format trọng lượng vàng."""
    if grams is None:
        return "0 chỉ"
    chi = grams / 3.75
    if chi >= 10:
        luong = chi / 10
        return f"{luong:.2f} lượng"
    return f"{chi:.2f} chỉ"


def short_amount(amount: float) -> str:
    """Rút gọn số tiền lớn: 1.5M, 2.3B."""
    if amount is None:
        return "0"
    abs_val = abs(amount)
    sign = "-" if amount < 0 else ""
    if abs_val >= 1_000_000_000:
        return f"{sign}{abs_val / 1_000_000_000:.1f}B"
    elif abs_val >= 1_000_000:
        return f"{sign}{abs_val / 1_000_000:.1f}M"
    elif abs_val >= 1_000:
        return f"{sign}{abs_val / 1_000:.1f}K"
    return f"{sign}{abs_val:,.0f}"


ACCOUNT_TYPE_LABELS = {
    "cash": "Tiền mặt",
    "bank": "Ngân hàng",
    "ewallet": "Ví điện tử",
    "forex": "Ngoại tệ",
    "gold": "Vàng",
    "savings": "Tiết kiệm",
    "other": "Khác",
}

TRANSACTION_TYPE_LABELS = {
    "income": "Thu nhập",
    "expense": "Chi tiêu",
    "transfer": "Chuyển khoản",
}

GOAL_STATUS_LABELS = {
    "active": "Đang thực hiện",
    "completed": "Hoàn thành",
    "cancelled": "Đã hủy",
}

DEPOSIT_STATUS_LABELS = {
    "active": "Đang gửi",
    "closed": "Đã tất toán",
    "matured": "Đã đáo hạn",
}
