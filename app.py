import logging
import streamlit as st

from db.init_db import init_database
from db.seed import run_all_seeds
from ui.styles import inject_custom_css

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Tài chính cá nhân", page_icon="💸", layout="wide")

try:
    init_database()
    run_all_seeds()
except Exception as exc:
    logger.exception("Init error")
    st.warning(f"Khởi tạo dữ liệu gặp lỗi: {exc}")

inject_custom_css()

DEFAULTS = {
    "authenticated": False,
    "user_id": None,
    "username": None,
    "current_page": "dashboard",
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if not st.session_state["authenticated"]:
    from pages.login import render_login

    render_login()
    st.stop()

PAGES = {
    "dashboard": ("Tổng quan", "📊"),
    "accounts": ("Tài khoản", "🏦"),
    "transactions": ("Giao dịch", "💳"),
    "categories": ("Danh mục", "📂"),
    "budgets": ("Ngân sách", "📉"),
    "goals": ("Mục tiêu", "🎯"),
    "savings": ("Tiết kiệm", "🐖"),
    "stocks": ("Chứng khoán", "📈"),
    "gold": ("Vàng", "🥇"),
    "forex": ("Tỷ giá", "💱"),
    "reports": ("Báo cáo", "📑"),
    "settings": ("Cài đặt", "⚙️"),
}

with st.sidebar:
    st.markdown('<div class="app-title">FINANCE APP</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="muted">Xin chào, {st.session_state.get("username")}</div>', unsafe_allow_html=True)

    labels = [f"{icon} {name}" for _, (name, icon) in PAGES.items()]
    keys = list(PAGES.keys())
    current_index = keys.index(st.session_state.get("current_page", "dashboard")) if st.session_state.get("current_page", "dashboard") in keys else 0

    selected_label = st.radio("Điều hướng", labels, index=current_index, label_visibility="collapsed")
    selected_index = labels.index(selected_label)
    st.session_state["current_page"] = keys[selected_index]

    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.clear()
        st.rerun()

try:
    page = st.session_state["current_page"]

    if page == "dashboard":
        from pages.dashboard import render_dashboard

        render_dashboard()
    elif page == "accounts":
        from pages.accounts import render_accounts

        render_accounts()
    elif page == "transactions":
        from pages.transactions import render_transactions

        render_transactions()
    elif page == "categories":
        from pages.categories import render_categories

        render_categories()
    elif page == "budgets":
        from pages.budgets import render_budgets

        render_budgets()
    elif page == "goals":
        from pages.goals import render_goals

        render_goals()
    elif page == "savings":
        from pages.savings import render_savings

        render_savings()
    elif page == "stocks":
        from pages.stocks import render_stocks

        render_stocks()
    elif page == "gold":
        from pages.gold import render_gold

        render_gold()
    elif page == "forex":
        from pages.forex import render_forex

        render_forex()
    elif page == "reports":
        from pages.reports import render_reports

        render_reports()
    elif page == "settings":
        from pages.settings_page import render_settings

        render_settings()
except Exception as exc:
    logger.exception("Render page error")
    st.error(f"Lỗi hiển thị trang: {exc}")
