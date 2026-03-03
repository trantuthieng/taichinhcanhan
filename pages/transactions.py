from datetime import date, datetime

import streamlit as st

from schemas.transaction import TransactionCreate
from services.account_service import AccountService
from services.category_service import CategoryService
from services.transaction_service import TransactionService
from ui.components import page_header
from utils.formatters import format_currency


def render_transactions() -> None:
    user_id = st.session_state["user_id"]
    page_header("Giao dịch")

    col1, col2, col3 = st.columns(3)
    start_date = col1.date_input("Từ ngày", value=date.today().replace(day=1), key="tx_start")
    end_date = col2.date_input("Đến ngày", value=date.today(), key="tx_end")
    tx_type = col3.selectbox("Loại", ["all", "income", "expense", "transfer"], key="tx_type")

    txs = TransactionService.get_transactions(
        user_id=user_id,
        start_date=datetime.combine(start_date, datetime.min.time()),
        end_date=datetime.combine(end_date, datetime.max.time()),
        tx_type=None if tx_type == "all" else tx_type,
        limit=200,
    )

    st.subheader("Lịch sử")
    if not txs:
        st.info("Không có giao dịch")
    else:
        rows = []
        for tx in txs:
            rows.append(
                {
                    "ID": int(tx.id),
                    "Ngày": tx.transaction_date.strftime("%d/%m/%Y"),
                    "Loại": tx.type,
                    "Số tiền": format_currency(float(tx.amount or 0), str(tx.currency or "VND")),
                    "Mô tả": tx.description or "",
                    "Account": int(tx.account_id),
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Thêm giao dịch")

    accounts = AccountService.get_accounts(user_id)
    if not accounts:
        st.warning("Bạn cần tạo tài khoản trước")
        return

    income_categories = CategoryService.get_income_categories(user_id)
    expense_categories = CategoryService.get_expense_categories(user_id)

    with st.form("create_tx_form", clear_on_submit=True):
        t1, t2 = st.columns(2)
        transaction_type = t1.selectbox("Loại giao dịch", ["income", "expense", "transfer"])
        amount = t2.number_input("Số tiền", min_value=1000.0, step=1000.0)

        source = st.selectbox("Tài khoản nguồn", accounts, format_func=lambda a: f"{a.name} ({format_currency(a.balance, a.currency)})")

        to_account = None
        category_id = None

        if transaction_type == "transfer":
            dest_options = [a for a in accounts if int(a.id) != int(source.id)]
            if dest_options:
                to_account = st.selectbox("Tài khoản đích", dest_options, format_func=lambda a: a.name)
            else:
                st.warning("Cần ít nhất 2 tài khoản để chuyển khoản")
        elif transaction_type == "income":
            if income_categories:
                cat = st.selectbox("Danh mục", income_categories, format_func=lambda c: c.name)
                category_id = int(cat.id)
        else:
            if expense_categories:
                cat = st.selectbox("Danh mục", expense_categories, format_func=lambda c: c.name)
                category_id = int(cat.id)

        description = st.text_input("Mô tả")
        transaction_date = st.date_input("Ngày", value=date.today())

        if st.form_submit_button("Lưu giao dịch", use_container_width=True):
            if transaction_type in ["income", "expense"] and category_id is None:
                st.error("Thiếu danh mục")
            elif transaction_type == "transfer" and not to_account:
                st.error("Thiếu tài khoản đích")
            else:
                ok, msg, _ = TransactionService.create_transaction(
                    user_id,
                    TransactionCreate(
                        account_id=int(source.id),
                        to_account_id=int(to_account.id) if to_account else None,
                        category_id=category_id,
                        type=transaction_type,
                        amount=float(amount),
                        description=description.strip() or None,
                        transaction_date=datetime.combine(transaction_date, datetime.min.time()),
                    ),
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
