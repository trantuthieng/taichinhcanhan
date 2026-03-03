"""Accounts – Quản lý tài khoản."""

import streamlit as st
from services.account_service import AccountService
from schemas.account import AccountCreate, AccountUpdate, VALID_ACCOUNT_TYPES
from ui.components import page_header, empty_state
from utils.formatters import format_currency, ACCOUNT_TYPE_LABELS
from utils.constants import CURRENCIES, VN_BANKS, VN_EWALLETS


def render_accounts():
    user_id = st.session_state["user_id"]
    page_header("Tài khoản", "🏦")

    accounts = AccountService.get_accounts(user_id) or []

    # ── Metrics ──
    total = sum(a.balance for a in accounts if a.currency == "VND")
    active = sum(1 for a in accounts if a.is_active)
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng số dư (VND)", format_currency(total))
    c2.metric("Số tài khoản", len(accounts))
    c3.metric("Đang hoạt động", active)

    tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm mới"])

    # ── List ──
    with tab_list:
        if not accounts:
            empty_state("Chưa có tài khoản nào", "🏦")
        else:
            for acc in accounts:
                with st.expander(
                    f"{ACCOUNT_TYPE_LABELS.get(acc.account_type, acc.account_type)} – "
                    f"{acc.name}  |  {format_currency(acc.balance, acc.currency)}",
                    expanded=False,
                ):
                    col1, col2 = st.columns(2)
                    col1.write(f"**Loại:** {ACCOUNT_TYPE_LABELS.get(acc.account_type, acc.account_type)}")
                    col1.write(f"**Tiền tệ:** {acc.currency}")
                    col2.write(f"**Số dư:** {format_currency(acc.balance, acc.currency)}")
                    col2.write(f"**Trạng thái:** {'✅ Hoạt động' if acc.is_active else '❌ Đã đóng'}")
                    if acc.bank_name:
                        col1.write(f"**Ngân hàng:** {acc.bank_name}")
                    if acc.account_number:
                        col2.write(f"**Số TK:** {acc.account_number}")

                    # Edit / close
                    edit_col, close_col = st.columns(2)
                    with edit_col:
                        new_bal = st.number_input("Cập nhật số dư", value=acc.balance,
                                                  key=f"bal_{acc.id}", step=10000.0)
                        if st.button("💾 Lưu", key=f"save_{acc.id}"):
                            ok, msg = AccountService.adjust_balance(user_id, acc.id, new_bal)
                            st.success(msg) if ok else st.error(msg)
                            if ok:
                                st.rerun()
                    with close_col:
                        if acc.is_active:
                            if st.button("🔒 Đóng tài khoản", key=f"close_{acc.id}"):
                                ok, msg = AccountService.close_account(user_id, acc.id)
                                st.success(msg) if ok else st.error(msg)
                                if ok:
                                    st.rerun()

    # ── Add ──
    with tab_add:
        with st.form("add_account_form"):
            name = st.text_input("Tên tài khoản *", placeholder="Ví tiền mặt")

            type_options = list(VALID_ACCOUNT_TYPES)
            acc_type = st.selectbox(
                "Loại *",
                type_options,
                format_func=lambda x: ACCOUNT_TYPE_LABELS.get(x, x),
            )

            currency = st.selectbox("Tiền tệ", CURRENCIES, index=0)
            initial_balance = st.number_input("Số dư ban đầu", value=0.0, step=100000.0)

            bank_name = ""
            account_number = ""
            if acc_type == "bank":
                bank_name = st.selectbox("Ngân hàng", [""] + VN_BANKS)
                account_number = st.text_input("Số tài khoản")
            elif acc_type == "ewallet":
                bank_name = st.selectbox("Ví điện tử", [""] + VN_EWALLETS)

            desc = st.text_area("Ghi chú", height=80)

            if st.form_submit_button("✅ Tạo tài khoản", use_container_width=True):
                if not name.strip():
                    st.error("Vui lòng nhập tên tài khoản")
                else:
                    data = AccountCreate(
                        name=name.strip(),
                        account_type=acc_type,
                        currency=currency,
                        initial_balance=initial_balance,
                        description=desc.strip() or None,
                        bank_name=bank_name or None,
                        account_number=account_number.strip() or None,
                    )
                    ok, msg, _ = AccountService.create_account(user_id, data)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
