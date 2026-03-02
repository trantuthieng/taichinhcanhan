"""Reports page - Báo cáo tài chính."""

import streamlit as st
from datetime import datetime, date

from services.report_service import ReportService
from ui.components import section_header, empty_state
from ui.charts import (
    income_expense_bar, expense_pie, cashflow_line,
    daily_expense_bar, account_balance_donut,
)
from utils.formatters import format_currency
from utils.helpers import get_month_range, get_quarter_range, get_year_range


def render_reports():
    """Render trang báo cáo."""
    user_id = st.session_state["user_id"]
    now = datetime.now()

    st.markdown("## 📈 Báo cáo tài chính")

    tab_monthly, tab_charts, tab_export = st.tabs(["📊 Tổng hợp", "📈 Biểu đồ", "📥 Xuất file"])

    with tab_monthly:
        _render_summary(user_id, now)

    with tab_charts:
        _render_charts(user_id, now)

    with tab_export:
        _render_export(user_id, now)


def _render_summary(user_id: int, now: datetime):
    """Báo cáo tổng hợp."""
    # Chọn khoảng thời gian
    period = st.selectbox("Kỳ báo cáo", ["Tháng này", "Tháng trước", "Quý này", "Năm nay", "Tùy chọn"])

    if period == "Tháng này":
        start, end = get_month_range(now.year, now.month)
    elif period == "Tháng trước":
        m = now.month - 1 if now.month > 1 else 12
        y = now.year if now.month > 1 else now.year - 1
        start, end = get_month_range(y, m)
    elif period == "Quý này":
        q = (now.month - 1) // 3 + 1
        start, end = get_quarter_range(now.year, q)
    elif period == "Năm nay":
        start, end = get_year_range(now.year)
    else:
        col1, col2 = st.columns(2)
        with col1:
            sd = st.date_input("Từ ngày", value=date(now.year, now.month, 1), key="rpt_start")
        with col2:
            ed = st.date_input("Đến ngày", value=date.today(), key="rpt_end")
        start = datetime.combine(sd, datetime.min.time())
        end = datetime.combine(ed, datetime.max.time())

    # Thu chi tổng quan
    summary = ReportService.get_income_expense_summary(user_id, start, end)

    c1, c2, c3 = st.columns(3)
    c1.metric("💚 Thu nhập", format_currency(summary["income"]))
    c2.metric("❤️ Chi tiêu", format_currency(summary["expense"]))
    c3.metric("💙 Ròng", format_currency(summary["net"]))

    st.markdown("---")

    # Chi tiêu theo danh mục
    section_header("Chi tiêu theo danh mục", "🍕")
    cat_data = ReportService.get_expense_by_category(user_id, start, end)
    if cat_data:
        for item in cat_data:
            pct = item["total"] / max(summary["expense"], 1) * 100
            st.write(f"• **{item['category']}**: {format_currency(item['total'])} ({pct:.1f}%)")
    else:
        st.info("Chưa có dữ liệu chi tiêu")

    st.markdown("---")

    # Chi tiêu chi tiết theo danh mục con
    section_header("Chi tiết danh mục con", "📋")
    sub_data = ReportService.get_expense_by_subcategory(user_id, start, end)
    if sub_data:
        import pandas as pd
        df = pd.DataFrame(sub_data)
        df.columns = ["Nhóm", "Danh mục", "Số tiền"]
        df["Số tiền"] = df["Số tiền"].apply(lambda x: format_currency(x))
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Số dư tài khoản
    st.markdown("---")
    section_header("Số dư tài khoản", "🏦")
    accounts = ReportService.get_account_balances(user_id)
    if accounts:
        for a in accounts:
            st.write(f"• **{a['name']}** ({a['type']}): {format_currency(a['balance'], a['currency'])}")


def _render_charts(user_id: int, now: datetime):
    """Biểu đồ phân tích."""
    start, end = get_month_range(now.year, now.month)

    # Xu hướng thu chi
    section_header("Xu hướng 6 tháng", "📈")
    trend = ReportService.get_monthly_trend(user_id, 6)
    if trend:
        st.plotly_chart(income_expense_bar(trend), use_container_width=True)
        st.plotly_chart(cashflow_line(trend), use_container_width=True)
    else:
        empty_state("Chưa có dữ liệu", "📈")

    st.markdown("---")

    # Chi tiêu theo danh mục
    section_header("Chi tiêu tháng này", "🍕")
    cat_data = ReportService.get_expense_by_category(user_id, start, end)
    if cat_data:
        st.plotly_chart(expense_pie(cat_data), use_container_width=True)

    st.markdown("---")

    # Chi tiêu hàng ngày
    section_header("Chi tiêu hàng ngày", "📊")
    daily = ReportService.get_daily_expenses(user_id, start, end)
    if daily:
        st.plotly_chart(daily_expense_bar(daily), use_container_width=True)

    st.markdown("---")

    # Phân bổ tài sản
    section_header("Phân bổ tài sản", "🏦")
    accounts = ReportService.get_account_balances(user_id)
    if accounts:
        st.plotly_chart(account_balance_donut(accounts), use_container_width=True)


def _render_export(user_id: int, now: datetime):
    """Xuất file báo cáo."""
    section_header("Xuất dữ liệu", "📥")

    col1, col2 = st.columns(2)
    with col1:
        sd = st.date_input("Từ ngày", value=date(now.year, 1, 1), key="exp_start")
    with col2:
        ed = st.date_input("Đến ngày", value=date.today(), key="exp_end")

    start = datetime.combine(sd, datetime.min.time())
    end = datetime.combine(ed, datetime.max.time())

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📥 Xuất Excel", use_container_width=True):
            with st.spinner("Đang xuất..."):
                data = ReportService.export_transactions_excel(user_id, start, end)
                st.download_button(
                    "💾 Tải file Excel",
                    data=data,
                    file_name=f"giao_dich_{sd}_{ed}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

    with col_b:
        if st.button("📥 Xuất CSV", use_container_width=True):
            with st.spinner("Đang xuất..."):
                data = ReportService.export_transactions_csv(user_id, start, end)
                st.download_button(
                    "💾 Tải file CSV",
                    data=data,
                    file_name=f"giao_dich_{sd}_{ed}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
