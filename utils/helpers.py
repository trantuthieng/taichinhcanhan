"""Helpers - Các hàm tiện ích."""

from datetime import datetime, date, timedelta
from typing import Optional, Tuple


def get_month_range(year: int, month: int) -> Tuple[datetime, datetime]:
    """Trả về (start, end) của tháng."""
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start, end


def get_quarter_range(year: int, quarter: int) -> Tuple[datetime, datetime]:
    """Trả về (start, end) của quý."""
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 3
    start = datetime(year, start_month, 1)
    if end_month > 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, end_month, 1)
    return start, end


def get_year_range(year: int) -> Tuple[datetime, datetime]:
    """Trả về (start, end) của năm."""
    return datetime(year, 1, 1), datetime(year + 1, 1, 1)


def get_current_month_range() -> Tuple[datetime, datetime]:
    """Trả về (start, end) của tháng hiện tại."""
    now = datetime.now()
    return get_month_range(now.year, now.month)


def get_last_n_months(n: int = 6) -> list:
    """Trả về danh sách (year, month) của n tháng gần nhất."""
    today = date.today()
    months = []
    for i in range(n):
        y = today.year
        m = today.month - i
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    return list(reversed(months))


def days_between(d1: date, d2: date) -> int:
    """Số ngày giữa 2 ngày."""
    return abs((d2 - d1).days)


def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """Chia an toàn, tránh division by zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def truncate_string(s: str, max_len: int = 50) -> str:
    """Cắt chuỗi nếu quá dài."""
    if not s:
        return ""
    if len(s) <= max_len:
        return s
    return s[:max_len - 3] + "..."


def parse_amount_input(text: str) -> Optional[float]:
    """Parse input số tiền từ người dùng, hỗ trợ nhiều format.
    Ví dụ: '1.234.567', '1,234,567', '1234567', '1.5M', '2.3B'
    """
    if not text:
        return None
    text = text.strip().upper()

    multiplier = 1
    if text.endswith("M"):
        multiplier = 1_000_000
        text = text[:-1]
    elif text.endswith("B"):
        multiplier = 1_000_000_000
        text = text[:-1]
    elif text.endswith("K"):
        multiplier = 1_000
        text = text[:-1]

    # Xử lý dấu phân cách
    # Nếu có cả dấu chấm và dấu phẩy, xác định đâu là phân cách hàng nghìn
    if "," in text and "." in text:
        # Vị trí cuối cùng
        last_comma = text.rfind(",")
        last_dot = text.rfind(".")
        if last_comma > last_dot:
            # Dấu phẩy là thập phân (kiểu VN): 1.234,56
            text = text.replace(".", "").replace(",", ".")
        else:
            # Dấu chấm là thập phân (kiểu US): 1,234.56
            text = text.replace(",", "")
    elif "," in text:
        # Chỉ dấu phẩy: 1,234,567 hoặc 1234,56
        parts = text.split(",")
        if len(parts[-1]) == 3 or len(parts) > 2:
            text = text.replace(",", "")
        else:
            text = text.replace(",", ".")
    elif "." in text:
        # Chỉ dấu chấm: 1.234.567 hoặc 1234.56
        parts = text.split(".")
        if len(parts[-1]) == 3 and len(parts) > 2:
            text = text.replace(".", "")
        # else: giữ nguyên (thập phân)

    try:
        return float(text) * multiplier
    except ValueError:
        return None
