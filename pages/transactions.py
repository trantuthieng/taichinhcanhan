"""Transactions – Quản lý giao dịch."""

import streamlit as st
from datetime import datetime, timedelta

from services.transaction_service import TransactionService
from services.account_service import AccountService
from services.category_service import CategoryService
from schemas.transaction import TransactionCreate
from ui.components import page_header, empty_state
from utils.formatters import format_currency, format_date, TRANSACTION_TYPE_LABELS
from utils.helpers import get_current_month_range


def render_transactions():
    user_id = st.session_state["user_id"]
    page_header("Giao dịch", "💳")

    cat_service = CategoryService()

    tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm giao dịch"])

    # ── List ──
    with tab_list:
        start_default, end_default = get_current_month_range()

        # Filters
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            start_date = st.date_input("Từ ngày", value=start_default.date())
        with fc2:
            end_date = st.date_input("Đến ngày", value=end_default.date())
        with fc3:
            tx_types = ["Tất cả", "income", "expense", "transfer"]
            tx_filter = st.selectbox(
                "Loại",
                tx_types,
                format_func=lambda x: "Tất cả" if x == "Tất cả"
                else TRANSACTION_TYPE_LABELS.get(x, x),
            )
        with fc4:
            search = st.text_input("Tìm kiếm", placeholder="Mô tả...")

        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        tx_type_arg = None if tx_filter == "Tất cả" else tx_filter
        transactions = TransactionService.get_transactions(
            user_id, start_date=start_dt, end_date=end_dt,
            tx_type=tx_type_arg, search=search or None, limit=200,
        )

        if not transactions:
            empty_state("Không có giao dịch nào", "💳")
        else:
            # Summary
            total_in = sum(t.amount for t in transactions if t.type == "income")
            total_out = sum(t.amount for t in transactions if t.type == "expense")
            s1, s2, s3 = st.columns(3)
            s1.metric("Thu nhập", format_currency(total_in))
            s2.metric("Chi tiêu", format_currency(total_out))
            s3.metric("Số giao dịch", len(transactions))

            # Table
            cat_map = cat_service.get_category_map(user_id)
            rows = []
            for t in transactions:
                rows.append({
                    "Ngày": format_date(t.transaction_date),
                    "Loại": TRANSACTION_TYPE_LABELS.get(t.type, t.type),
                    "Số tiền": format_currency(t.amount, t.currency),
                    "Danh mục": cat_map.get(t.category_id, "—"),
                    "Mô tả": t.description or "",
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)

            # Delete section
            with st.expander("🗑️ Xoá giao dịch"):
                tx_options = {
                    f"#{t.id} – {format_date(t.transaction_date)} – "
                    f"{format_currency(t.amount)} – {t.description or ''}": t.id
                    for t in transactions[:50]
                }
                selected = st.selectbox("Chọn giao dịch", list(tx_options.keys()))
                if st.button("Xoá", type="primary"):
                    ok, msg = TransactionService.delete_transaction(user_id, tx_options[selected])
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        st.rerun()

    # ── Add ──
    with tab_add:
        accounts = AccountService.get_accounts(user_id) or []
        if not accounts:
            st.warning("Bạn cần tạo tài khoản trước khi thêm giao dịch.")
            if st.button("🏦 Tạo tài khoản ngay"):
                st.session_state["current_page"] = "accounts"
                st.rerun()
            return

        with st.form("add_tx_form"):
            col1, col2 = st.columns(2)
            with col1:
                tx_type = st.selectbox(
                    "Loại giao dịch *",
                    ["income", "expense", "transfer"],
                    format_func=lambda x: TRANSACTION_TYPE_LABELS.get(x, x),
                )
                account_id = st.selectbox(
                    "Tài khoản *",
                    [a.id for a in accounts],
                    format_func=lambda x: next(
                        (f"{a.name} ({a.currency})" for a in accounts if a.id == x), str(x)
                    ),
                )
                amount = st.number_input("Số tiền *", min_value=0.0, step=10000.0)

            with col2:
                tx_date = st.date_input("Ngày", value=datetime.now().date())

                # Category selection based on type
                if tx_type == "income":
                    categories = cat_service.get_income_categories(user_id)
                elif tx_type == "expense":
                    categories = cat_service.get_expense_categories(user_id)
                else:
                    categories = []

                cat_id = None
                if categories:
                    cat_id = st.selectbox(
                        "Danh mục",
                        [None] + [c.id for c in categories],
                        format_func=lambda x: "— Không chọn —" if x is None
                        else next((c.name for c in categories if c.id == x), ""),
                    )

                sub_id = None
                if cat_id:
                    subs = cat_service.get_subcategories(cat_id)
                    if subs:
                        sub_id = st.selectbox(
                            "Danh mục con",
                            [None] + [s.id for s in subs],
                            format_func=lambda x: "— Không chọn —" if x is None
                            else next((s.name for s in subs if s.id == x), ""),
                        )

            # Transfer destination
            to_account_id = None
            if tx_type == "transfer":
                other_accounts = [a for a in accounts if a.id != account_id]
                if other_accounts:
                    to_account_id = st.selectbox(
                        "Tài khoản đích *",
                        [a.id for a in other_accounts],
                        format_func=lambda x: next(
                            (f"{a.name} ({a.currency})" for a in other_accounts if a.id == x),
                            str(x),
                        ),
                    )

            description = st.text_input("Mô tả", placeholder="Mua sắm, ăn uống...")
            notes = st.text_area("Ghi chú", height=60)

            if st.form_submit_button("✅ Lưu giao dịch", use_container_width=True):
                if amount <= 0:
                    st.error("Số tiền phải lớn hơn 0")
                else:
                    acc_obj = next((a for a in accounts if a.id == account_id), None)
                    data = TransactionCreate(
                        account_id=account_id,
                        to_account_id=to_account_id,
                        category_id=cat_id,
                        subcategory_id=sub_id,
                        type=tx_type,
                        amount=amount,
                        currency=acc_obj.currency if acc_obj else "VND",
                        description=description.strip() or None,
                        notes=notes.strip() or None,
                        transaction_date=datetime.combine(tx_date, datetime.now().time()),
                    )
                    ok, msg, _ = TransactionService.create_transaction(user_id, data)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
