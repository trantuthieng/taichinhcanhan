"""
Quản lý Tài chính Cá nhân - Main Application
=============================================
Entry point cho ứng dụng Streamlit.
Chạy: streamlit run app.py
"""

import streamlit as st
import sys
import os
import logging
from config import settings

# Thêm thư mục gốc vào sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Quản lý Tài chính",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== INIT DATABASE =====
from db.init_db import init_database
from db.database import get_active_database_url, get_last_database_error
from db.seed import run_all_seeds
init_database()
run_all_seeds()

active_db_url = get_active_database_url()
if settings.DATABASE_URL.startswith(("postgresql", "postgres://")) and active_db_url.startswith("sqlite"):
    db_error = get_last_database_error()
    detail = f"\nChi tiết: {db_error}" if db_error else ""
    st.warning(
        "⚠️ Không kết nối được Supabase/PostgreSQL nên app đang tạm chạy SQLite fallback. "
        f"Vui lòng kiểm tra lại DATABASE_URL trong Streamlit Secrets.{detail}",
        icon="⚠️",
    )

# ===== INJECT CSS =====
from ui.styles import inject_custom_css
inject_custom_css()

# ===== SESSION STATE DEFAULTS =====
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "dashboard"

# ===== AUTH CHECK =====
if not st.session_state["authenticated"]:
    from pages.login import render_login
    render_login()
    st.stop()

# ===== SIDEBAR NAVIGATION =====
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center; padding:1.2rem 0 0.8rem;">
            <div style="font-size:2.4rem; margin-bottom:0.2rem;">💰</div>
            <div style="font-weight:700; font-size:1.15rem;
                 background: linear-gradient(135deg, #6C5CE7, #a29bfe);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Quản lý Tài chính
            </div>
            <div style="color:#6c6c8a; font-size:0.85rem; margin-top:0.2rem;">
                Xin chào, <span style="color:#a29bfe;">{st.session_state['username']}</span> 👋
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    NAV_GROUPS = {
        "CHÍNH": {
            "📊 Tổng quan": "dashboard",
            "🏦 Tài khoản": "accounts",
            "💳 Giao dịch": "transactions",
            "📂 Danh mục": "categories",
        },
        "ĐẦU TƯ": {
            "📈 Chứng khoán": "stocks",
            "🥇 Vàng": "gold",
            "💱 Tỷ giá": "forex",
        },
        "KẾ HOẠCH": {
            "🏧 Tiết kiệm": "savings",
            "📋 Ngân sách": "budgets",
            "🎯 Mục tiêu": "goals",
        },
        "KHÁC": {
            "📉 Báo cáo": "reports",
            "⚙️ Cài đặt": "settings",
        },
    }

    # Build flat map for lookup
    ALL_PAGES = {}
    for items in NAV_GROUPS.values():
        ALL_PAGES.update(items)

    current = st.session_state.get("current_page", "dashboard")

    for group_name, items in NAV_GROUPS.items():
        st.markdown(
            f"<div style='color:#6c6c8a; font-size:0.7rem; font-weight:600; "
            f"letter-spacing:1.2px; padding:0.8rem 0.5rem 0.3rem; text-transform:uppercase;'>"
            f"{group_name}</div>",
            unsafe_allow_html=True,
        )
        for label, page_key in items.items():
            is_active = current == page_key
            if is_active:
                st.markdown(
                    f"""<div style="display:flex; align-items:center; gap:0.5rem; padding:0.55rem 0.9rem;
                        border-radius:10px; margin-bottom:2px; font-size:0.9rem; font-weight:600;
                        background:linear-gradient(135deg, rgba(108,92,231,0.25), rgba(162,155,254,0.15));
                        color:#a29bfe; border-left:3px solid #6C5CE7;">
                        {label}</div>""",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state["current_page"] = page_key
                    st.rerun()

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Auto-sync tỷ giá & giá vàng khi bật
    from services.settings_service import SettingsService
    user_settings = SettingsService.get_all_settings(st.session_state["user_id"])

    if user_settings.get("fx_auto_sync") == "true":
        from services.fx_service import FxService
        if "fx_synced" not in st.session_state:
            try:
                FxService.sync_rates()
                st.session_state["fx_synced"] = True
            except Exception:
                pass

    if user_settings.get("gold_auto_sync") == "true":
        from services.gold_service import GoldService
        if "gold_synced" not in st.session_state:
            try:
                GoldService.sync_prices()
                st.session_state["gold_synced"] = True
            except Exception:
                pass

    # Logout
    if st.button("🚪 Đăng xuất", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ===== RENDER PAGE =====
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
elif page == "stocks":
    from pages.stocks import render_stocks
    render_stocks()
elif page == "savings":
    from pages.savings import render_savings
    render_savings()
elif page == "forex":
    from pages.forex import render_forex
    render_forex()
elif page == "gold":
    from pages.gold import render_gold
    render_gold()
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
