"""Transactions page - Quản lý giao dịch."""

import streamlit as st
from datetime import datetime, date, timedelta

from services.transaction_service import TransactionService
from services.account_service import AccountService
from services.category_service import CategoryService
from ui.components import transaction_item, section_header, empty_state
from utils.formatters import format_currency, format_date, TRANSACTION_TYPE_LABELS
from utils.helpers import get_current_month_range, get_month_range


def render_transactions():
    """Render trang giao dịch."""
    user_id = st.session_state["user_id"]

    st.markdown("## 💳 Giao dịch")

    tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm mới"])

    with tab_list:
        _render_transaction_list(user_id)

    with tab_add:
        _render_add_transaction(user_id)


def _render_transaction_list(user_id: int):
    """Danh sách giao dịch với filter."""
    now = datetime.now()

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_type = st.selectbox("Loại", ["Tất cả", "Thu nhập", "Chi tiêu", "Chuyển khoản"],
                                    key="tx_filter_type")
    with col_f2:
        start_date = st.date_input("Từ ngày", value=date(now.year, now.month, 1), key="tx_start")
    with col_f3:
        end_date = st.date_input("Đến ngày", value=date.today(), key="tx_end")

    type_map = {"Thu nhập": "income", "Chi tiêu": "expense", "Chuyển khoản": "transfer"}
    tx_type = type_map.get(filter_type)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    transactions = TransactionService.get_transactions(
        user_id, start=start_dt, end=end_dt, tx_type=tx_type, limit=100
    )

    if not transactions:
        empty_state("Không có giao dịch trong khoảng thời gian này", "📭")
        return

    # Summary
    total_in = sum(t.amount for t in transactions if t.type == "income")
    total_out = sum(t.amount for t in transactions if t.type == "expense")
    c1, c2, c3 = st.columns(3)
    c1.metric("Thu", format_currency(total_in))
    c2.metric("Chi", format_currency(total_out))
    c3.metric("Ròng", format_currency(total_in - total_out))

    st.markdown("---")

    # Load references
    from db.database import get_session
    from models.category import SubCategory
    from models.account import Account
    session = get_session()
    try:
        subcats = {s.id: s.name for s in session.query(SubCategory).all()}
        accs = {a.id: a.name for a in session.query(Account).filter(Account.user_id == user_id).all()}
    finally:
        session.close()

    for tx in transactions:
        cat_name = subcats.get(tx.category_id, "")
        acc_name = accs.get(tx.account_id, "")
        date_str = format_date(tx.transaction_date, "dd/mm/yyyy HH:MM")

        with st.expander(
            f"{'🟢' if tx.type == 'income' else '🔴' if tx.type == 'expense' else '🔄'} "
            f"{tx.description or cat_name} — {format_currency(tx.amount)} — {date_str}",
            expanded=False,
        ):
            st.write(f"**Loại:** {TRANSACTION_TYPE_LABELS.get(tx.type, tx.type)}")
            st.write(f"**Tài khoản:** {acc_name}")
            st.write(f"**Danh mục:** {cat_name}")
            if tx.description:
                st.write(f"**Mô tả:** {tx.description}")

            col_e, col_d = st.columns(2)
            with col_e:
                with st.popover("✏️ Sửa"):
                    new_amount = st.number_input("Số tiền", value=float(tx.amount), key=f"ed_amt_{tx.id}")
                    new_desc = st.text_input("Mô tả", value=tx.description or "", key=f"ed_desc_{tx.id}")
                    if st.button("💾 Lưu", key=f"ed_save_{tx.id}"):
                        from schemas.transaction import TransactionUpdate
                        upd = TransactionUpdate(amount=new_amount, description=new_desc)
                        ok, msg = TransactionService.update_transaction(user_id, tx.id, upd)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            with col_d:
                if st.button("🗑️ Xóa", key=f"del_tx_{tx.id}"):
                    ok, msg = TransactionService.delete_transaction(user_id, tx.id)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)


def _render_add_transaction(user_id: int):
    """Form thêm giao dịch mới."""
    accounts = AccountService.get_accounts(user_id)
    if not accounts:
        st.warning("Vui lòng tạo tài khoản trước khi thêm giao dịch.")
        return

    cat_service = CategoryService()
    category_map, subcategory_map = cat_service.get_category_map(user_id)

    with st.form("add_tx_form"):
        tx_type = st.selectbox("Loại giao dịch *", ["expense", "income", "transfer"],
                                format_func=lambda x: TRANSACTION_TYPE_LABELS.get(x, x))

        amount = st.number_input("Số tiền *", min_value=0.0, step=10000.0, format="%.0f")

        account_id = st.selectbox(
            "Tài khoản *",
            options=[a.id for a in accounts],
            format_func=lambda x: next((a.name for a in accounts if a.id == x), ""),
        )

        # Category selection
        cat_options = list(subcategory_map.keys())
        category_id = None
        if cat_options:
            selected_sub = st.selectbox(
                "Danh mục",
                options=cat_options,
                format_func=lambda x: subcategory_map.get(x, ""),
            )
            category_id = selected_sub

        to_account_id = None
        if tx_type == "transfer":
            other_accounts = [a for a in accounts if a.id != account_id]
            if other_accounts:
                to_account_id = st.selectbox(
                    "Chuyển đến",
                    options=[a.id for a in other_accounts],
                    format_func=lambda x: next((a.name for a in other_accounts if a.id == x), ""),
                )

        tx_date = st.date_input("Ngày", value=date.today())
        tx_time = st.time_input("Giờ", value=datetime.now().time())
        description = st.text_input("Mô tả / Ghi chú")

        if st.form_submit_button("✅ Thêm giao dịch", use_container_width=True):
            if amount <= 0:
                st.error("Số tiền phải lớn hơn 0")
            else:
                from schemas.transaction import TransactionCreate
                tx_datetime = datetime.combine(tx_date, tx_time)
                data = TransactionCreate(
                    type=tx_type,
                    amount=amount,
                    account_id=account_id,
                    to_account_id=to_account_id,
                    category_id=category_id,
                    transaction_date=tx_datetime,
                    description=description or None,
                )
                ok, msg = TransactionService.create_transaction(user_id, data)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
