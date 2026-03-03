import streamlit as st

from schemas.account import AccountCreate
from services.account_service import AccountService
from ui.components import page_header
from utils.constants import ACCOUNT_TYPES
from utils.formatters import format_currency


def render_accounts() -> None:
    user_id = st.session_state["user_id"]
    page_header("Tài khoản")

    accounts = AccountService.get_accounts(user_id)

    left, right = st.columns([2, 1])
    with left:
        st.subheader("Danh sách")
        if not accounts:
            st.info("Chưa có tài khoản")
        else:
            rows = []
            for a in accounts:
                rows.append(
                    {
                        "ID": int(a.id),
                        "Tên": str(a.name),
                        "Loại": str(a.account_type),
                        "Tiền tệ": str(a.currency),
                        "Số dư": format_currency(float(a.balance or 0), str(a.currency or "VND")),
                        "Ngân hàng": str(a.bank_name or ""),
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Thêm tài khoản")
        with st.form("add_account_form", clear_on_submit=True):
            name = st.text_input("Tên")
            account_type = st.selectbox("Loại", ACCOUNT_TYPES)
            currency = st.selectbox("Tiền tệ", ["VND", "USD", "EUR"])
            initial_balance = st.number_input("Số dư ban đầu", min_value=0.0, step=10000.0)
            bank_name = st.text_input("Ngân hàng (tuỳ chọn)")
            account_number = st.text_input("Số tài khoản (tuỳ chọn)")

            if st.form_submit_button("Lưu", use_container_width=True):
                if not name.strip():
                    st.error("Tên không được trống")
                else:
                    ok, msg, _ = AccountService.create_account(
                        user_id,
                        AccountCreate(
                            name=name.strip(),
                            account_type=account_type,
                            currency=currency,
                            initial_balance=initial_balance,
                            bank_name=bank_name.strip() or None,
                            account_number=account_number.strip() or None,
                        ),
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
