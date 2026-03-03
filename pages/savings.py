"""Savings – Sổ tiết kiệm."""

import streamlit as st
from datetime import date

from services.savings_service import SavingsService
from services.account_service import AccountService
from schemas.savings import SavingsDepositCreate
from ui.components import page_header, empty_state, progress_bar
from utils.formatters import format_currency, format_date, DEPOSIT_STATUS_LABELS
from utils.constants import SAVINGS_TERMS, INTEREST_PAYMENT_METHODS, VN_BANKS, CURRENCIES


def render_savings():
    user_id = st.session_state["user_id"]
    page_header("Tiết kiệm", "🏧")

    tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Gửi tiết kiệm"])

    # ── List ──
    with tab_list:
        deposits = SavingsService.get_deposits(user_id) or []
        total = SavingsService.get_total_savings(user_id)

        c1, c2, c3 = st.columns(3)
        c1.metric("Tổng tiết kiệm", format_currency(total))
        c2.metric("Số sổ", len(deposits))
        c3.metric("Đang hoạt động", sum(1 for d in deposits if d.status == "active"))

        if not deposits:
            empty_state("Chưa có sổ tiết kiệm", "🏧")
        else:
            for d in deposits:
                detail = SavingsService.get_deposit_detail(d.id)
                status_label = DEPOSIT_STATUS_LABELS.get(d.status, d.status)
                badge = "🟢" if d.status == "active" else ("🔵" if d.status == "matured" else "⚫")

                with st.expander(
                    f"{badge} {d.bank_name} – {format_currency(d.principal_amount, d.currency)} "
                    f"– {d.interest_rate}%/năm – {status_label}"
                ):
                    col1, col2 = st.columns(2)
                    col1.write(f"**Gốc:** {format_currency(d.principal_amount, d.currency)}")
                    col1.write(f"**Lãi suất:** {d.interest_rate}%/năm")
                    col1.write(f"**Kỳ hạn:** {d.term_months} tháng")
                    col2.write(f"**Ngày gửi:** {format_date(d.open_date)}")
                    col2.write(f"**Đáo hạn:** {format_date(d.maturity_date)}")
                    col2.write(f"**Trạng thái:** {status_label}")

                    if detail:
                        interest = detail.get("interest", {})
                        st.info(
                            f"💰 Lãi dự kiến: **{format_currency(interest.get('net_interest', 0))}** "
                            f"| Tổng nhận: **{format_currency(interest.get('total_at_maturity', 0))}**"
                        )
                        if detail.get("days_remaining") is not None and detail["days_remaining"] > 0:
                            st.caption(f"Còn {detail['days_remaining']} ngày đến đáo hạn")

                    if d.status == "active":
                        bc1, bc2 = st.columns(2)
                        with bc1:
                            if st.button("🔒 Tất toán", key=f"close_{d.id}"):
                                ok, msg = SavingsService.close_deposit(user_id, d.id, early=True)
                                st.success(msg) if ok else st.error(msg)
                                if ok:
                                    st.rerun()
                        with bc2:
                            if st.button("🔄 Tái tục", key=f"renew_{d.id}"):
                                ok, msg = SavingsService.renew_deposit(user_id, d.id)
                                st.success(msg) if ok else st.error(msg)
                                if ok:
                                    st.rerun()

    # ── Add ──
    with tab_add:
        with st.form("add_savings_form"):
            col1, col2 = st.columns(2)
            with col1:
                bank = st.selectbox("Ngân hàng *", VN_BANKS)
                principal = st.number_input("Số tiền gửi *", min_value=0.0, step=1000000.0)
                currency = st.selectbox("Tiền tệ", CURRENCIES, index=0)
                open_dt = st.date_input("Ngày gửi", value=date.today())

            with col2:
                term = st.selectbox("Kỳ hạn (tháng) *", SAVINGS_TERMS, index=5)
                rate = st.number_input("Lãi suất (%/năm) *", min_value=0.0,
                                       max_value=30.0, step=0.1, value=5.0)
                int_type = st.selectbox(
                    "Hình thức trả lãi",
                    list(INTEREST_PAYMENT_METHODS.keys()),
                    format_func=lambda x: INTEREST_PAYMENT_METHODS[x],
                )
                auto_renew = st.checkbox("Tự động tái tục")

            notes = st.text_area("Ghi chú", height=60)

            if st.form_submit_button("✅ Gửi tiết kiệm", use_container_width=True):
                if principal <= 0:
                    st.error("Số tiền phải lớn hơn 0")
                elif rate <= 0:
                    st.error("Lãi suất phải lớn hơn 0")
                else:
                    data = SavingsDepositCreate(
                        bank_name=bank,
                        principal_amount=principal,
                        currency=currency,
                        open_date=open_dt,
                        term_months=term,
                        interest_rate=rate,
                        interest_type=int_type,
                        auto_renew=auto_renew,
                        notes=notes.strip() or None,
                    )
                    ok, msg, _ = SavingsService.create_deposit(user_id, data)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
