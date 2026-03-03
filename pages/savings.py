from datetime import date

import streamlit as st

from schemas.savings import SavingsDepositCreate
from services.savings_service import SavingsService
from ui.components import page_header
from utils.formatters import format_currency


def render_savings() -> None:
    user_id = st.session_state["user_id"]
    page_header("Tiết kiệm")

    total = SavingsService.get_total_savings(user_id)
    st.metric("Tổng gốc đang gửi", format_currency(total))

    deposits = SavingsService.get_deposits(user_id)
    if not deposits:
        st.info("Chưa có sổ tiết kiệm")
    else:
        rows = []
        for d in deposits:
            rows.append(
                {
                    "ID": int(d.id),
                    "Ngân hàng": d.bank_name,
                    "Gốc": format_currency(float(d.principal_amount or 0), d.currency),
                    "Lãi suất": f"{d.interest_rate}%",
                    "Kỳ hạn": f"{d.term_months} tháng",
                    "Trạng thái": d.status,
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)

    st.divider()
    with st.form("add_savings_form"):
        bank_name = st.text_input("Ngân hàng", value="Vietcombank")
        principal_amount = st.number_input("Tiền gửi", min_value=1000000.0, step=1000000.0)
        term_months = st.selectbox("Kỳ hạn", [1, 3, 6, 12, 24, 36])
        interest_rate = st.number_input("Lãi suất %/năm", min_value=0.1, step=0.1, value=5.5)
        if st.form_submit_button("Mở sổ", use_container_width=True):
            ok, msg, _ = SavingsService.create_deposit(
                user_id,
                SavingsDepositCreate(
                    bank_name=bank_name.strip(),
                    principal_amount=float(principal_amount),
                    open_date=date.today(),
                    term_months=int(term_months),
                    interest_rate=float(interest_rate),
                ),
            )
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
