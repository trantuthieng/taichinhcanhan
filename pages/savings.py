"""Savings page - Quản lý sổ tiết kiệm."""

import streamlit as st
from datetime import date, datetime

from services.savings_service import SavingsService
from ui.components import section_header, empty_state, status_badge, progress_bar
from utils.formatters import format_currency, format_date, format_percentage, DEPOSIT_STATUS_LABELS
from utils.constants import SAVINGS_TERMS, INTEREST_PAYMENT_METHODS, VN_BANKS


def render_savings():
    """Render trang tiết kiệm."""
    user_id = st.session_state["user_id"]

    st.markdown("## 🏧 Sổ tiết kiệm")

    tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Gửi mới"])

    with tab_list:
        _render_savings_list(user_id)

    with tab_add:
        _render_add_deposit(user_id)


def _render_savings_list(user_id: int):
    """Danh sách sổ tiết kiệm."""
    filter_status = st.selectbox("Trạng thái", ["active", "matured", "closed", "all"],
                                  format_func=lambda x: {"active": "Đang gửi", "matured": "Đã đáo hạn",
                                                         "closed": "Đã tất toán", "all": "Tất cả"}.get(x, x))

    status = filter_status if filter_status != "all" else None
    deposits = SavingsService.get_deposits(user_id, status)

    if not deposits:
        empty_state("Chưa có sổ tiết kiệm nào", "🏧")
        return

    # Tổng gửi tiết kiệm
    total_deposit = sum(d.principal for d in deposits if d.status == "active")
    st.info(f"💰 Tổng tiền gửi (đang hoạt động): **{format_currency(total_deposit)}**")

    # Cảnh báo sắp đáo hạn
    maturing = SavingsService.get_maturing_soon(user_id, days=7)
    if maturing:
        st.warning(f"⏰ Có {len(maturing)} sổ sắp đáo hạn trong 7 ngày tới!")

    for d in deposits:
        status_icon = {"active": "🟢", "matured": "🟡", "closed": "⚪"}.get(d.status, "⚪")
        interest_info = SavingsService.calculate_interest(d.id)
        expected = interest_info.get("expected_interest", 0) if interest_info else 0

        with st.expander(
            f"{status_icon} {d.bank_name} - {format_currency(d.principal)} - {d.interest_rate}%/năm",
            expanded=False,
        ):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Ngân hàng:** {d.bank_name}")
                st.write(f"**Gốc:** {format_currency(d.principal)}")
                st.write(f"**Lãi suất:** {d.interest_rate}%/năm")
                st.write(f"**Kỳ hạn:** {d.term_months} tháng")
                st.write(f"**Trả lãi:** {INTEREST_PAYMENT_METHODS.get(d.interest_payment, d.interest_payment)}")
            with c2:
                st.write(f"**Ngày gửi:** {format_date(d.start_date)}")
                st.write(f"**Ngày đáo hạn:** {format_date(d.maturity_date)}")
                st.write(f"**Trạng thái:** {DEPOSIT_STATUS_LABELS.get(d.status, d.status)}")
                st.write(f"**Lãi dự kiến:** {format_currency(expected)}")
                if d.notes:
                    st.write(f"**Ghi chú:** {d.notes}")

            if d.status == "active":
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("💰 Tất toán", key=f"close_dep_{d.id}"):
                        ok, msg = SavingsService.close_deposit(user_id, d.id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                with col_b:
                    if st.button("🔄 Đáo hạn tái gửi", key=f"renew_dep_{d.id}"):
                        ok, msg = SavingsService.renew_deposit(user_id, d.id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)


def _render_add_deposit(user_id: int):
    """Form thêm sổ tiết kiệm."""
    with st.form("add_deposit_form"):
        bank_name = st.selectbox("Ngân hàng *", VN_BANKS)
        principal = st.number_input("Số tiền gốc *", min_value=0.0, step=1000000.0, format="%.0f")
        interest_rate = st.number_input("Lãi suất (%/năm) *", min_value=0.0, max_value=20.0,
                                         step=0.1, value=5.0, format="%.2f")
        term_months = st.selectbox("Kỳ hạn (tháng) *", SAVINGS_TERMS)
        interest_payment = st.selectbox("Phương thức trả lãi",
                                         list(INTEREST_PAYMENT_METHODS.keys()),
                                         format_func=lambda x: INTEREST_PAYMENT_METHODS[x])
        start_date = st.date_input("Ngày gửi", value=date.today())
        is_compound = st.checkbox("Lãi kép (nhập gốc)", value=False)
        auto_renew = st.checkbox("Tự động tái gửi khi đáo hạn", value=True)
        notes = st.text_area("Ghi chú")

        if st.form_submit_button("✅ Tạo sổ tiết kiệm", use_container_width=True):
            if principal <= 0:
                st.error("Số tiền gốc phải lớn hơn 0")
            elif interest_rate <= 0:
                st.error("Lãi suất phải lớn hơn 0")
            else:
                from schemas.savings import SavingsDepositCreate
                data = SavingsDepositCreate(
                    bank_name=bank_name,
                    principal=principal,
                    interest_rate=interest_rate,
                    term_months=term_months,
                    interest_payment=interest_payment,
                    start_date=start_date,
                    is_compound=is_compound,
                    auto_renew=auto_renew,
                    notes=notes or None,
                )
                ok, msg = SavingsService.create_deposit(user_id, data)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
