"""Components - Các component UI tái sử dụng (dark glassmorphism)."""

import streamlit as st
from utils.formatters import format_currency, format_percentage, short_amount


def metric_card(label: str, value: str, delta: str = None, card_type: str = "", icon: str = ""):
    """Hiển thị metric card glassmorphism."""
    icon_map = {
        "income": "💰", "expense": "💸", "balance": "📊",
        "savings": "🏦", "stock": "📈",
    }
    display_icon = icon or icon_map.get(card_type, "💎")

    delta_class = ""
    if delta:
        if delta.startswith("-") or "giảm" in delta.lower():
            delta_class = "negative"
        else:
            delta_class = "positive"

    delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card {card_type}">
            <div class="metric-icon">{display_icon}</div>
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
    type_icons = {
        "cash": "💵", "bank": "🏦", "ewallet": "📱",
        "forex": "💱", "gold": "🥇", "savings": "🏧", "other": "💼",
    }
    icon = type_icons.get(acc_type, "💼")
    st.markdown(
        f"""
        <div class="account-card">
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span style="font-size:1.3rem;">{icon}</span>
                <div>
                    <div class="acc-name">{name}</div>
                    <div class="acc-type">{type_label}</div>
                </div>
            </div>
            <div class="acc-balance">{format_currency(balance, currency)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def transaction_item(description: str, amount: float, category: str, tx_type: str, date_str: str):
    """Hiển thị 1 giao dịch dạng list item."""
    amount_class = "income" if tx_type == "income" else "expense"
    sign = "+" if tx_type == "income" else "-"
    icon = "📥" if tx_type == "income" else "📤"
    st.markdown(
        f"""
        <div class="tx-item">
            <div style="display:flex; align-items:center; gap:0.6rem;">
                <span style="font-size:1.1rem;">{icon}</span>
                <div class="tx-info">
                    <div><strong>{description or "Không ghi chú"}</strong></div>
                    <div class="tx-cat">{category} &bull; {date_str}</div>
                </div>
            </div>
            <div class="tx-amount {amount_class}">{sign}{format_currency(amount)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stock_card(ticker: str, name: str, price: float, change_pct: float,
               quantity: int, avg_price: float):
    """Card hiển thị mã chứng khoán đang nắm giữ."""
    change_class = "up" if change_pct > 0 else "down" if change_pct < 0 else "neutral"
    change_icon = "▲" if change_pct > 0 else "▼" if change_pct < 0 else "●"
    market_value = price * quantity
    profit = (price - avg_price) * quantity
    profit_pct = ((price - avg_price) / avg_price * 100) if avg_price > 0 else 0
    profit_class = "up" if profit >= 0 else "down"

    st.markdown(
        f"""
        <div class="stock-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <span class="stock-ticker">{ticker}</span>
                    <div class="stock-name">{name}</div>
                </div>
                <div style="text-align:right;">
                    <div class="stock-price" style="color: var(--text-primary);">{format_currency(price)}</div>
                    <span class="stock-change {change_class}">{change_icon} {abs(change_pct):.1f}%</span>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:0.7rem; padding-top:0.7rem; border-top:1px solid var(--border-glass);">
                <div>
                    <div style="color:var(--text-muted); font-size:0.72rem;">SL: {quantity:,} cp</div>
                    <div style="color:var(--text-muted); font-size:0.72rem;">Giá TB: {format_currency(avg_price)}</div>
                </div>
                <div style="text-align:right;">
                    <div style="color:var(--text-muted); font-size:0.72rem;">GT: {short_amount(market_value)}</div>
                    <div style="font-size:0.82rem; font-weight:600;" class="stock-change {profit_class}">
                        {'+' if profit >= 0 else ''}{short_amount(profit)} ({'+' if profit_pct >= 0 else ''}{profit_pct:.1f}%)
                    </div>
                </div>
            </div>
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

    label_html = f"<small style='color:var(--text-muted);'>{label}</small>" if label else ""
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
        <div class="empty-state">
            <div class="es-icon">{icon}</div>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, icon: str = ""):
    """Header cho section - glassmorphism style."""
    st.markdown(
        f"""
        <div class="section-header">
            <span class="sh-icon">{icon}</span>
            <span class="sh-title">{title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_title(title: str, icon: str = "", subtitle: str = ""):
    """Tiêu đề trang chính."""
    sub_html = f'<span class="pt-sub">{subtitle}</span>' if subtitle else ""
    st.markdown(
        f"""
        <div class="page-title">
            <span class="pt-icon">{icon}</span>
            <span class="pt-text">{title}</span>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def confirm_dialog(key: str, message: str = "Bạn có chắc chắn?") -> bool:
    """Dialog xác nhận đơn giản dùng checkbox."""
    return st.checkbox(message, key=key)
