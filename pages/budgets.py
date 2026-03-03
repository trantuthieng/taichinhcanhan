from datetime import date

import streamlit as st

from services.budget_service import BudgetService
from services.category_service import CategoryService
from ui.components import page_header
from utils.formatters import format_currency


def render_budgets() -> None:
    user_id = st.session_state["user_id"]
    page_header("Ngân sách")

    c1, c2 = st.columns(2)
    month = c1.selectbox("Tháng", list(range(1, 13)), index=date.today().month - 1)
    year = c2.selectbox("Năm", [2025, 2026, 2027, 2028], index=1)

    budgets = BudgetService.get_budgets(user_id, month, year)

    st.subheader("Tình hình")
    if not budgets:
        st.info("Chưa có ngân sách")
    else:
        rows = []
        for item in budgets:
            b = item["budget"]
            rows.append(
                {
                    "ID": int(b.id),
                    "Category": int(b.category_id) if b.category_id else "overall",
                    "Hạn mức": format_currency(float(b.amount or 0)),
                    "Đã chi": format_currency(float(item["spent"] or 0)),
                    "%": f"{item['percentage']}%",
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Thiết lập")
    expense_categories = CategoryService.get_expense_categories(user_id)

    with st.form("set_budget_form"):
        target = st.selectbox("Danh mục", expense_categories, format_func=lambda c: c.name) if expense_categories else None
        amount = st.number_input("Hạn mức", min_value=100000.0, step=100000.0)
        if st.form_submit_button("Lưu ngân sách", use_container_width=True):
            category_id = int(target.id) if target else None
            ok, msg = BudgetService.set_budget(user_id, category_id, float(amount), int(month), int(year))
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
