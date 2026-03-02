"""Components - Các component UI tái sử dụng."""

import streamlit as st
from utils.formatters import format_currency, format_percentage, short_amount


def metric_card(label: str, value: str, delta: str = None, card_type: str = ""):
    """Hiển thị metric card với gradient."""
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card {card_type}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def account_card(name: str, balance: float, acc_type: str, currency: str = "VND"):
    """Card hiển thị tài khoản."""
    from utils.formatters import ACCOUNT_TYPE_LABELS
    type_label = ACCOUNT_TYPE_LABELS.get(acc_type, acc_type)
    st.markdown(
        f"""
        <div class="account-card">
            <div class="acc-name">{name}</div>
            <div class="acc-balance">{format_currency(balance, currency)}</div>
            <div class="acc-type">{type_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def transaction_item(description: str, amount: float, category: str, tx_type: str, date_str: str):
    """Hiển thị 1 giao dịch dạng list item."""
    amount_class = "income" if tx_type == "income" else "expense"
    sign = "+" if tx_type == "income" else "-"
    st.markdown(
        f"""
        <div class="tx-item">
            <div class="tx-info">
                <div><strong>{description or "Không ghi chú"}</strong></div>
                <div class="tx-cat">{category} • {date_str}</div>
            </div>
            <div class="tx-amount {amount_class}">{sign}{format_currency(amount)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar(percentage: float, label: str = ""):
    """Progress bar custom với màu theo mức độ."""
    pct = min(100, max(0, percentage))
    if pct >= 90:
        bar_class = "danger"
    elif pct >= 70:
        bar_class = "warning"
    else:
        bar_class = "safe"

    label_html = f"<small>{label}</small>" if label else ""
    st.markdown(
        f"""
        {label_html}
        <div class="progress-container">
            <div class="progress-bar {bar_class}" style="width: {pct}%"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str):
    """Hiển thị badge trạng thái."""
    badge_map = {
        "active": ("Đang hoạt động", "badge-active"),
        "completed": ("Hoàn thành", "badge-completed"),
        "cancelled": ("Đã hủy", "badge-cancelled"),
        "matured": ("Đã đáo hạn", "badge-matured"),
        "closed": ("Đã tất toán", "badge-cancelled"),
    }
    label, css_class = badge_map.get(status, (status, "badge-active"))
    st.markdown(f'<span class="badge {css_class}">{label}</span>', unsafe_allow_html=True)


def empty_state(message: str, icon: str = "📭"):
    """Hiển thị trạng thái trống."""
    st.markdown(
        f"""
        <div style="text-align:center; padding:2rem; color:#888;">
            <div style="font-size:3rem;">{icon}</div>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, icon: str = ""):
    """Header cho section."""
    st.markdown(f"### {icon} {title}" if icon else f"### {title}")


def confirm_dialog(key: str, message: str = "Bạn có chắc chắn?") -> bool:
    """Dialog xác nhận đơn giản dùng checkbox."""
    return st.checkbox(message, key=key)
