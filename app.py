"""
Quản lý Tài chính Cá nhân – Main Application
=============================================
Entry point cho ứng dụng Streamlit.
"""

import streamlit as st
import sys, os, logging
from config import settings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ───────── PAGE CONFIG ─────────
st.set_page_config(
    page_title="Quản lý Tài chính",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────── DATABASE ─────────
from db.init_db import init_database
from db.database import get_active_database_url, get_last_database_error
from db.seed import run_all_seeds

init_database()
run_all_seeds()

active_url = get_active_database_url()
if settings.DATABASE_URL.startswith(("postgresql", "postgres://")) and active_url.startswith("sqlite"):
    db_err = get_last_database_error()
    st.warning(
        "⚠️ Không kết nối được PostgreSQL – đang chạy SQLite fallback."
        + (f" ({db_err})" if db_err else "")
    )

# ───────── CSS ─────────
from ui.styles import inject_custom_css
inject_custom_css()

# ───────── SESSION DEFAULTS ─────────
_DEFAULTS = {
    "authenticated": False,
    "user": None,
    "user_id": None,
    "username": None,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ───────── AUTH ─────────
if not st.session_state["authenticated"]:
    from pages.login import render_login
    render_login()
    st.stop()

# ───────── NAVIGATION MAP ─────────
NAV = {
    "📊 Tổng quan": "dashboard",
    "🏦 Tài khoản": "accounts",
    "💳 Giao dịch": "transactions",
    "📂 Danh mục": "categories",
    "📈 Chứng khoán": "stocks",
    "🥇 Vàng": "gold",
    "💱 Tỷ giá": "forex",
    "🏧 Tiết kiệm": "savings",
    "📋 Ngân sách": "budgets",
    "🎯 Mục tiêu": "goals",
    "📉 Báo cáo": "reports",
    "⚙️ Cài đặt": "settings",
}

NAV_GROUPS = {
    "CHÍNH": ["📊 Tổng quan", "🏦 Tài khoản", "💳 Giao dịch", "📂 Danh mục"],
    "ĐẦU TƯ": ["📈 Chứng khoán", "🥇 Vàng", "💱 Tỷ giá"],
    "KẾ HOẠCH": ["🏧 Tiết kiệm", "📋 Ngân sách", "🎯 Mục tiêu"],
    "KHÁC": ["📉 Báo cáo", "⚙️ Cài đặt"],
}

# ───────── SIDEBAR ─────────
with st.sidebar:
    # Branding
    st.markdown(
        f"""
        <div style="text-align:center; padding:0.8rem 0;">
            <div style="font-size:2rem;">💰</div>
            <div style="font-weight:700; font-size:1.05rem;
                 background:linear-gradient(135deg,#6C5CE7,#a29bfe);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                Quản lý Tài chính
            </div>
            <div style="color:#6c6c8a; font-size:0.82rem; margin-top:0.15rem;">
                Xin chào, <span style="color:#a29bfe;">{st.session_state['username']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Determine current page
    current_page = st.session_state.get("current_page", "dashboard")
    # If a page set current_page directly, sync the nav widget
    if "nav" not in st.session_state:
        for lbl, key in NAV.items():
            if key == current_page:
                st.session_state["nav"] = lbl
                break

    # Nav groups
    for group_name, items in NAV_GROUPS.items():
        st.caption(group_name)
        for label in items:
            page_key = NAV[label]
            if page_key == current_page:
                st.markdown(f'<div class="nav-active">{label}</div>', unsafe_allow_html=True)
            else:
                if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state["current_page"] = page_key
                    st.rerun()

    st.divider()

    # Auto-sync FX & Gold
    from services.settings_service import SettingsService
    _user_settings = SettingsService.get_all_settings(st.session_state["user_id"])

    if _user_settings.get("fx_auto_sync") == "true" and "fx_synced" not in st.session_state:
        try:
            from services.fx_service import FxService
            FxService.sync_rates()
            st.session_state["fx_synced"] = True
        except Exception:
            pass

    if _user_settings.get("gold_auto_sync") == "true" and "gold_synced" not in st.session_state:
        try:
            from services.gold_service import GoldService
            GoldService.sync_prices()
            st.session_state["gold_synced"] = True
        except Exception:
            pass

    if st.button("🚪 Đăng xuất", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ───────── PAGE ROUTER ─────────
page = st.session_state.get("current_page", "dashboard")

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
elif page == "stocks":
    from pages.stocks import render_stocks
    render_stocks()
elif page == "gold":
    from pages.gold import render_gold
    render_gold()
elif page == "forex":
    from pages.forex import render_forex
    render_forex()
elif page == "savings":
    from pages.savings import render_savings
    render_savings()
elif page == "budgets":
    from pages.budgets import render_budgets
    render_budgets()
elif page == "goals":
    from pages.goals import render_goals
    render_goals()
elif page == "reports":
    from pages.reports import render_reports
    render_reports()
elif page == "settings":
    from pages.settings_page import render_settings
    render_settings()
