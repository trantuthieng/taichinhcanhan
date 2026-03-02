"""Dashboard page - Trang tổng quan."""

import streamlit as st
from datetime import datetime

from services.report_service import ReportService
from services.account_service import AccountService
from services.savings_service import SavingsService
from services.budget_service import BudgetService
from services.goal_service import GoalService
from ui.components import metric_card, section_header, empty_state
from ui.charts import income_expense_bar, expense_pie, cashflow_line, account_balance_donut
from utils.formatters import format_currency, short_amount
from utils.helpers import get_current_month_range


def render_dashboard():
    """Render trang tổng quan."""
    user_id = st.session_state["user_id"]
    now = datetime.now()
    start, end = get_current_month_range()

    st.markdown(f"## 📊 Tổng quan tháng {now.month}/{now.year}")

    # ===== METRIC CARDS =====
    summary = ReportService.get_income_expense_summary(user_id, start, end)
    accounts = ReportService.get_account_balances(user_id)
    total_balance = sum(a["balance"] for a in accounts if a["currency"] == "VND")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Thu nhập", short_amount(summary["income"]), card_type="income")
    with c2:
        metric_card("Chi tiêu", short_amount(summary["expense"]), card_type="expense")
    with c3:
        metric_card("Tiết kiệm ròng", short_amount(summary["net"]),
                     delta=f"{summary['net']/max(summary['income'],1)*100:.0f}% thu nhập",
                     card_type="balance")
    with c4:
        metric_card("Tổng tài sản", short_amount(total_balance), card_type="savings")

    st.markdown("---")

    # ===== BIỂU ĐỒ =====
    col_left, col_right = st.columns(2)

    with col_left:
        section_header("Xu hướng thu chi", "📈")
        trend = ReportService.get_monthly_trend(user_id, 6)
        if trend:
            st.plotly_chart(income_expense_bar(trend), use_container_width=True)
        else:
            empty_state("Chưa có dữ liệu giao dịch", "📊")

    with col_right:
        section_header("Chi tiêu theo danh mục", "🍕")
        cat_data = ReportService.get_expense_by_category(user_id, start, end)
        if cat_data:
            st.plotly_chart(expense_pie(cat_data), use_container_width=True)
        else:
            empty_state("Chưa có chi tiêu tháng này", "🍕")

    st.markdown("---")

    # ===== DÒNG TIỀN & TÀI SẢN =====
    col_a, col_b = st.columns(2)

    with col_a:
        section_header("Dòng tiền ròng", "💹")
        if trend:
            st.plotly_chart(cashflow_line(trend), use_container_width=True)

    with col_b:
        section_header("Phân bổ tài sản", "🏦")
        if accounts:
            st.plotly_chart(account_balance_donut(accounts), use_container_width=True)
        else:
            empty_state("Chưa có tài khoản", "🏦")

    st.markdown("---")

    # ===== NGÂN SÁCH & MỤC TIÊU =====
    col_x, col_y = st.columns(2)

    with col_x:
        section_header("Ngân sách tháng này", "📋")
        budgets = BudgetService.get_budgets(user_id, now.month, now.year)
        if budgets:
            for b in budgets[:5]:
                label = b["budget"].category.name if b["budget"].category_id else "Tổng chi tiêu"
                pct = b["percentage"]
                color = "🟢" if pct < 70 else "🟡" if pct < 90 else "🔴"
                st.markdown(f"{color} **{label}**: {format_currency(b['spent'])} / {format_currency(b['budget'].amount)} ({pct}%)")
        else:
            empty_state("Chưa thiết lập ngân sách", "📋")

    with col_y:
        section_header("Mục tiêu tiết kiệm", "🎯")
        goals = GoalService.get_goals(user_id, "active")
        if goals:
            for g in goals[:5]:
                pct = g["percentage"]
                icon = "✅" if pct >= 100 else "🔵"
                st.markdown(f"{icon} **{g['goal'].name}**: {pct}% ({format_currency(g['goal'].current_amount)} / {format_currency(g['goal'].target_amount)})")
        else:
            empty_state("Chưa có mục tiêu", "🎯")
