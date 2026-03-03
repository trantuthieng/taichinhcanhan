"""Dashboard – Trang tổng quan."""

import streamlit as st
from datetime import datetime

from services.report_service import ReportService
from services.account_service import AccountService
from services.budget_service import BudgetService
from services.goal_service import GoalService
from services.stock_service import StockService
from services.gold_service import GoldService
from services.fx_service import FxService
from ui.components import page_header, empty_state, progress_bar, color_for_pct
from ui.charts import (
    income_expense_bar, expense_pie, cashflow_line, account_balance_donut,
)
from utils.formatters import format_currency, short_amount
from utils.helpers import get_current_month_range


def render_dashboard():
    """Render trang tổng quan."""
    user_id = st.session_state["user_id"]
    now = datetime.now()
    start, end = get_current_month_range()

    page_header("Tổng quan", "📊", f"Tháng {now.month}/{now.year}")

    # ── Check new user ──
    accounts_list = AccountService.get_accounts(user_id)
    if not accounts_list:
        _welcome(user_id)
        return

    # ── Quick actions ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("➕ Giao dịch", use_container_width=True):
            st.session_state["current_page"] = "transactions"
            st.rerun()
    with c2:
        if st.button("🏦 Tài khoản", use_container_width=True):
            st.session_state["current_page"] = "accounts"
            st.rerun()
    with c3:
        if st.button("📋 Ngân sách", use_container_width=True):
            st.session_state["current_page"] = "budgets"
            st.rerun()
    with c4:
        if st.button("📉 Báo cáo", use_container_width=True):
            st.session_state["current_page"] = "reports"
            st.rerun()

    st.markdown("")

    # ── Metrics ──
    summary = ReportService.get_income_expense_summary(user_id, start, end)
    accounts = ReportService.get_account_balances(user_id)

    total_vnd = sum(a["balance"] for a in accounts if a["currency"] == "VND")
    total_fx = sum(
        (FxService.convert_to_vnd(a["balance"], a["currency"]) or 0)
        for a in accounts if a["currency"] != "VND" and a["balance"] > 0
    )
    total_gold = GoldService.get_total_gold_value(user_id)
    stock_info = StockService.get_total_portfolio_value(user_id)
    total_stock = stock_info.get("total_market_value", 0)
    total_assets = total_vnd + total_fx + total_gold + total_stock

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Thu nhập", short_amount(summary["income"]),
              f"+{short_amount(summary['income'])} tháng này")
    m2.metric("Chi tiêu", short_amount(summary["expense"]),
              f"-{short_amount(summary['expense'])} tháng này")
    m3.metric("Tiết kiệm ròng", short_amount(summary["net"]))
    m4.metric("Tổng tài sản", short_amount(total_assets))

    st.markdown("")

    # ── Charts row 1 ──
    left, right = st.columns(2)
    with left:
        st.markdown("**📈 Xu hướng thu chi**")
        trend = ReportService.get_monthly_trend(user_id, 6)
        if trend:
            st.plotly_chart(income_expense_bar(trend), use_container_width=True,
                            config={"displayModeBar": False})
        else:
            empty_state("Chưa có dữ liệu giao dịch", "📊")

    with right:
        st.markdown("**🍕 Chi tiêu theo danh mục**")
        cat_data = ReportService.get_expense_by_category(user_id, start, end)
        if cat_data:
            st.plotly_chart(expense_pie(cat_data), use_container_width=True,
                            config={"displayModeBar": False})
        else:
            empty_state("Chưa có chi tiêu tháng này", "🍕")

    # ── Charts row 2 ──
    left2, right2 = st.columns(2)
    with left2:
        st.markdown("**💹 Dòng tiền ròng**")
        if trend:
            st.plotly_chart(cashflow_line(trend), use_container_width=True,
                            config={"displayModeBar": False})
        else:
            empty_state("Chưa có dữ liệu", "💹")

    with right2:
        st.markdown("**🏦 Phân bổ tài sản**")
        if accounts:
            st.plotly_chart(account_balance_donut(accounts), use_container_width=True,
                            config={"displayModeBar": False})
        else:
            empty_state("Chưa có tài khoản", "🏦")

    st.markdown("")

    # ── Budget & Goal summaries ──
    col_b, col_g = st.columns(2)

    with col_b:
        st.markdown("**📋 Ngân sách tháng này**")
        budgets = BudgetService.get_budgets(user_id, now.month, now.year)
        if budgets:
            for b in budgets[:5]:
                label = b["budget"].category.name if b["budget"].category_id else "Tổng chi tiêu"
                pct = b["percentage"]
                col_l, col_r = st.columns([4, 1])
                with col_l:
                    st.caption(label)
                    progress_bar(pct, 100, color_for_pct(pct))
                with col_r:
                    st.markdown(f"<div style='text-align:right; font-size:0.85rem; "
                                f"padding-top:0.8rem;'>{pct:.0f}%</div>", unsafe_allow_html=True)
        else:
            empty_state("Chưa thiết lập ngân sách", "📋")

    with col_g:
        st.markdown("**🎯 Mục tiêu tiết kiệm**")
        goals = GoalService.get_goals(user_id, "active")
        if goals:
            for g in goals[:5]:
                pct = g["percentage"]
                col_l, col_r = st.columns([4, 1])
                with col_l:
                    st.caption(g["goal"].name)
                    progress_bar(pct, 100, "#00cec9" if pct >= 100 else "#6C5CE7")
                with col_r:
                    st.markdown(f"<div style='text-align:right; font-size:0.85rem; "
                                f"padding-top:0.8rem;'>{pct:.0f}%</div>", unsafe_allow_html=True)
        else:
            empty_state("Chưa có mục tiêu", "🎯")

    # ── Stock portfolio (nếu có) ──
    portfolio = StockService.get_portfolio_summary(user_id)
    if portfolio:
        st.markdown("")
        st.markdown("**📈 Danh mục chứng khoán**")
        cols = st.columns(min(len(portfolio), 4))
        for idx, s in enumerate(portfolio[:4]):
            with cols[idx]:
                pnl_color = "#00cec9" if s["profit_pct"] >= 0 else "#ff6b6b"
                st.metric(
                    s["ticker"],
                    format_currency(s["current_price"]),
                    f"{s['profit_pct']:+.1f}%",
                )


def _welcome(user_id):
    """Render hướng dẫn bắt đầu cho người dùng mới."""
    st.markdown(
        """
        <div class="welcome-card">
            <div style="font-size:2.5rem; margin-bottom:0.3rem;">🎉</div>
            <h3 style="color:#E8E8F0; margin:0;">Chào mừng bạn!</h3>
            <p style="color:#a0a0b8; font-size:0.9rem; margin-top:0.4rem;">
                Bắt đầu quản lý tài chính với 3 bước đơn giản
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**Bước 1**\n\nTạo tài khoản (ví, ngân hàng...)")
        if st.button("🏦 Tạo tài khoản", use_container_width=True, key="w_acc"):
            st.session_state["current_page"] = "accounts"
            st.rerun()
    with c2:
        st.info("**Bước 2**\n\nKiểm tra danh mục thu chi")
        if st.button("📂 Xem danh mục", use_container_width=True, key="w_cat"):
            st.session_state["current_page"] = "categories"
            st.rerun()
    with c3:
        st.info("**Bước 3**\n\nGhi chép giao dịch đầu tiên")
        if st.button("💳 Thêm giao dịch", use_container_width=True, key="w_txn"):
            st.session_state["current_page"] = "transactions"
            st.rerun()
