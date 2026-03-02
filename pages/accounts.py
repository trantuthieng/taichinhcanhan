"""Accounts page - Quản lý tài khoản."""

import streamlit as st
from services.account_service import AccountService
from schemas.account import AccountCreate, AccountUpdate
from ui.components import account_card, section_header, empty_state, page_title, metric_card
from utils.formatters import format_currency, short_amount, ACCOUNT_TYPE_LABELS
from utils.constants import ACCOUNT_TYPES, CURRENCIES


def render_accounts():
    """Render trang quản lý tài khoản."""
    user_id = st.session_state["user_id"]

    page_title("Tài khoản", "🏦", "Quản lý tài khoản & số dư")

    tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm mới"])

    with tab_list:
        accounts = AccountService.get_accounts(user_id)
        if not accounts:
            empty_state("Chưa có tài khoản nào. Hãy thêm tài khoản đầu tiên!", "🏦")
        else:
            # Summary metrics
            total_vnd = sum(a.balance for a in accounts if a.currency == "VND")
            total_accounts = len(accounts)
            active_accounts = len([a for a in accounts if a.is_active])
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                metric_card("Tổng số dư VND", short_amount(total_vnd), card_type="balance")
            with mc2:
                metric_card("Số tài khoản", str(total_accounts), card_type="savings", icon="🏦")
            with mc3:
                metric_card("Đang hoạt động", str(active_accounts), card_type="income", icon="✅")

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # Account cards
            section_header("Danh sách tài khoản", "📋")
            cols = st.columns(min(len(accounts), 3))
            for idx, acc in enumerate(accounts):
                with cols[idx % len(cols)]:
                    account_card(acc.name, acc.balance, acc.account_type, acc.currency)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # Detail expanders
            section_header("Chi tiết & Quản lý", "⚙️")
            for acc in accounts:
                with st.expander(f"{acc.name} - {format_currency(acc.balance, acc.currency)}", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Loại:** {ACCOUNT_TYPE_LABELS.get(acc.account_type, acc.account_type)}")
                        st.write(f"**Tiền tệ:** {acc.currency}")
                        st.write(f"**Số dư:** {format_currency(acc.balance, acc.currency)}")
                    with c2:
                        if acc.bank_name:
                            st.write(f"**Ngân hàng:** {acc.bank_name}")
                        if acc.account_number:
                            st.write(f"**Số TK:** {acc.account_number}")
                        if acc.description:
                            st.write(f"**Ghi chú:** {acc.description}")

                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        with st.popover("✏️ Sửa"):
                            new_name = st.text_input("Tên", value=acc.name, key=f"edit_name_{acc.id}")
                            new_balance = st.number_input("Số dư", value=float(acc.balance), key=f"edit_bal_{acc.id}")
                            new_desc = st.text_input("Ghi chú", value=acc.description or "", key=f"edit_notes_{acc.id}")
                            if st.button("💾 Lưu", key=f"save_{acc.id}"):
                                update_data = AccountUpdate(
                                    name=new_name,
                                    balance=new_balance,
                                    description=new_desc or None,
                                )
                                ok, msg = AccountService.update_account(user_id, acc.id, update_data)
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

                    with col_del:
                        if st.button("🗑️ Xóa", key=f"del_{acc.id}"):
                            ok, msg = AccountService.delete_account(user_id, acc.id)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

    with tab_add:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Thêm tài khoản mới", "➕")
        with st.form("add_account_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                name = st.text_input("Tên tài khoản *", placeholder="VD: Tiền mặt, Vietcombank...")
                acc_type = st.selectbox("Loại", ACCOUNT_TYPES, format_func=lambda x: ACCOUNT_TYPE_LABELS.get(x, x))
                currency = st.selectbox("Tiền tệ", CURRENCIES)
                balance = st.number_input("Số dư ban đầu", min_value=0.0, value=0.0, step=100000.0)
            with col_b:
                bank_name = st.text_input("Ngân hàng (tuỳ chọn)")
                account_number = st.text_input("Số tài khoản (tuỳ chọn)")
                notes = st.text_area("Ghi chú")

            if st.form_submit_button("✅ Tạo tài khoản", use_container_width=True):
                if not name.strip():
                    st.error("Vui lòng nhập tên tài khoản")
                else:
                    data = AccountCreate(
                        name=name.strip(),
                        account_type=acc_type,
                        currency=currency,
                        initial_balance=balance,
                        bank_name=bank_name or None,
                        account_number=account_number or None,
                        description=notes or None,
                    )
                    ok, msg, _id = AccountService.create_account(user_id, data)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)
