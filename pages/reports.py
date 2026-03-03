"""Reports – Báo cáo tài chính."""

import streamlit as st
from datetime import datetime, date, timedelta

from services.report_service import ReportService
from ui.components import page_header, empty_state
from ui.charts import (
    income_expense_bar, expense_pie, cashflow_line, daily_expense_bar,
)
from utils.formatters import format_currency


def render_reports():
    user_id = st.session_state["user_id"]
    page_header("Báo cáo tài chính", "📉")

    # ── Date range filter ──
    col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
    with col_f1:
        preset = st.selectbox("Khoảng thời gian", [
            "Tháng này", "Tháng trước", "Quý này", "Năm nay", "Tuỳ chọn",
        ])
    today = date.today()
    if preset == "Tháng này":
        start_dt = today.replace(day=1)
        end_dt = today
    elif preset == "Tháng trước":
        first = today.replace(day=1)
        end_dt = first - timedelta(days=1)
        start_dt = end_dt.replace(day=1)
    elif preset == "Quý này":
        q = (today.month - 1) // 3
        start_dt = date(today.year, q * 3 + 1, 1)
        end_dt = today
    elif preset == "Năm nay":
        start_dt = date(today.year, 1, 1)
        end_dt = today
    else:
        with col_f2:
            start_dt = st.date_input("Từ ngày", value=today.replace(day=1))
        with col_f3:
            end_dt = st.date_input("Đến ngày", value=today)

    start = datetime.combine(start_dt, datetime.min.time())
    end = datetime.combine(end_dt, datetime.max.time())

    st.divider()

    # ── Summary metrics ──
    summary = ReportService.get_income_expense_summary(user_id, start, end)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Thu nhập", format_currency(summary.get("income", 0)))
    c2.metric("Chi tiêu", format_currency(summary.get("expense", 0)))
    c3.metric("Chuyển khoản", format_currency(summary.get("transfer", 0)))
    net = summary.get("net", 0)
    c4.metric("Ròng", format_currency(net), "Dương" if net >= 0 else "Âm")

    # ── Tabs ──
    tab_trend, tab_cat, tab_daily, tab_export = st.tabs([
        "📈 Xu hướng", "📊 Theo danh mục", "📅 Theo ngày", "📤 Xuất file",
    ])

    # ── Monthly trend ──
    with tab_trend:
        trend = ReportService.get_monthly_trend(user_id, months=12)
        if not trend:
            empty_state("Chưa có dữ liệu xu hướng", "📈")
        else:
            st.plotly_chart(
                income_expense_bar(trend),
                use_container_width=True,
                config={"displayModeBar": False},
            )
            st.plotly_chart(
                cashflow_line(trend),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    # ── By category ──
    with tab_cat:
        cat_data = ReportService.get_expense_by_category(user_id, start, end)
        if not cat_data:
            empty_state("Chưa có dữ liệu theo danh mục", "📊")
        else:
            ch1, ch2 = st.columns([1, 1])
            with ch1:
                st.plotly_chart(
                    expense_pie(cat_data),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            with ch2:
                rows = [{
                    "Danh mục": d["category"],
                    "Số tiền": format_currency(d["total"]),
                } for d in sorted(cat_data, key=lambda x: x["total"], reverse=True)]
                st.dataframe(rows, use_container_width=True, hide_index=True)

            # Subcategory breakdown
            with st.expander("📋 Chi tiết danh mục con"):
                sub_data = ReportService.get_expense_by_subcategory(user_id, start, end)
                if sub_data:
                    sub_rows = [{
                        "Danh mục": d["category"],
                        "Danh mục con": d["subcategory"],
                        "Số tiền": format_currency(d["total"]),
                    } for d in sorted(sub_data, key=lambda x: x["total"], reverse=True)]
                    st.dataframe(sub_rows, use_container_width=True, hide_index=True)

    # ── Daily ──
    with tab_daily:
        daily = ReportService.get_daily_expenses(user_id, start, end)
        if not daily:
            empty_state("Chưa có dữ liệu theo ngày", "📅")
        else:
            st.plotly_chart(
                daily_expense_bar(daily),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    # ── Export ──
    with tab_export:
        st.markdown("**Xuất dữ liệu giao dịch**")
        st.caption(f"Khoảng thời gian: {start_dt.strftime('%d/%m/%Y')} – {end_dt.strftime('%d/%m/%Y')}")

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            try:
                excel_bytes = ReportService.export_transactions_excel(user_id, start, end)
                if excel_bytes:
                    st.download_button(
                        "📥 Tải Excel",
                        data=excel_bytes,
                        file_name=f"giao_dich_{start_dt}_{end_dt}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                else:
                    st.info("Không có dữ liệu để xuất")
            except Exception as e:
                st.error(f"Lỗi xuất Excel: {e}")

        with col_e2:
            try:
                csv_text = ReportService.export_transactions_csv(user_id, start, end)
                if csv_text:
                    st.download_button(
                        "📥 Tải CSV",
                        data=csv_text,
                        file_name=f"giao_dich_{start_dt}_{end_dt}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
                else:
                    st.info("Không có dữ liệu để xuất")
            except Exception as e:
                st.error(f"Lỗi xuất CSV: {e}")

        # Account balances
        with st.expander("🏦 Số dư tài khoản"):
            balances = ReportService.get_account_balances(user_id)
            if balances:
                rows = [{
                    "Tài khoản": b["name"],
                    "Loại": b["type"],
                    "Tiền tệ": b["currency"],
                    "Số dư": format_currency(b["balance"]),
                } for b in balances]
                st.dataframe(rows, use_container_width=True, hide_index=True)
