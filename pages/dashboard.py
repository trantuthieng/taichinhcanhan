from datetime import date, datetime

import streamlit as st

from services.account_service import AccountService
from services.report_service import ReportService
from services.transaction_service import TransactionService
from ui.components import page_header
from utils.formatters import format_currency


def render_dashboard() -> None:
    user_id = st.session_state["user_id"]
    today = date.today()
    start_month = today.replace(day=1)

    page_header("Tổng quan", "Bản mới tối giản, ưu tiên ổn định")

    total_by_currency = AccountService.get_total_balance(user_id)
    total_assets = float(sum(total_by_currency.values())) if isinstance(total_by_currency, dict) else 0.0

    summary = ReportService.get_income_expense_summary(
        user_id,
        datetime.combine(start_month, datetime.min.time()),
        datetime.combine(today, datetime.max.time()),
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng tài sản", format_currency(total_assets))
    c2.metric("Thu nhập tháng", format_currency(summary.get("income", 0.0)))
    c3.metric("Chi tiêu tháng", format_currency(summary.get("expense", 0.0)))

    st.subheader("Tài sản theo tiền tệ")
    if total_by_currency:
        st.dataframe(
            [{"Tiền tệ": k, "Số dư": format_currency(v, k)} for k, v in total_by_currency.items()],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Chưa có tài khoản")

    st.subheader("5 giao dịch gần nhất")
    txs = TransactionService.get_transactions(user_id, limit=5)
    if not txs:
        st.info("Chưa có giao dịch")
        return

    rows = []
    for tx in txs:
        rows.append(
            {
                "Ngày": tx.transaction_date.strftime("%d/%m/%Y %H:%M") if tx.transaction_date else "",
                "Loại": tx.type,
                "Số tiền": format_currency(tx.amount, tx.currency),
                "Mô tả": tx.description or "",
                "TK nguồn": tx.account_id,
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)
