"""Budgets page - Quản lý ngân sách."""

import streamlit as st
from datetime import datetime

from services.budget_service import BudgetService
from services.category_service import CategoryService
from ui.components import section_header, empty_state, progress_bar
from ui.charts import budget_gauge
from utils.formatters import format_currency
from utils.helpers import get_month_range


def render_budgets():
    """Render trang ngân sách."""
    user_id = st.session_state["user_id"]
    now = datetime.now()

    st.markdown("## 📋 Ngân sách")

    tab_view, tab_set = st.tabs(["📊 Theo dõi", "⚙️ Thiết lập"])

    with tab_view:
        _render_budget_tracking(user_id, now)

    with tab_set:
        _render_set_budget(user_id, now)


def _render_budget_tracking(user_id: int, now: datetime):
    """Theo dõi ngân sách."""
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("Tháng", range(1, 13), index=now.month - 1, key="bud_month")
    with col2:
        year = st.number_input("Năm", min_value=2020, max_value=2100, value=now.year, key="bud_year")

    budgets = BudgetService.get_budgets(user_id, month, year)

    if not budgets:
        empty_state("Chưa thiết lập ngân sách cho tháng này", "📋")
        return

    for b in budgets:
        budget_obj = b["budget"]
        label = "Tổng chi tiêu"
        if budget_obj.category_id:
            try:
                # Lấy tên category
                from db.database import get_session
                from models.category import Category
                session = get_session()
                cat = session.query(Category).get(budget_obj.category_id)
                label = cat.name if cat else f"Category #{budget_obj.category_id}"
                session.close()
            except Exception:
                label = f"Danh mục #{budget_obj.category_id}"

        spent = b["spent"]
        budget_amount = budget_obj.amount
        pct = b["percentage"]
        remaining = b["remaining"]

        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.markdown(f"**{label}**")
            progress_bar(pct, f"{format_currency(spent)} / {format_currency(budget_amount)} ({pct}%)")
        with col_b:
            if b["is_over"]:
                st.error(f"Vượt {format_currency(abs(remaining))}")
            else:
                st.success(f"Còn {format_currency(remaining)}")

        st.markdown("---")


def _render_set_budget(user_id: int, now: datetime):
    """Thiết lập ngân sách."""
    cat_service = CategoryService()
    categories = cat_service.get_categories(user_id)

    with st.form("set_budget_form"):
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox("Tháng", range(1, 13), index=now.month - 1, key="set_bud_month")
        with col2:
            year = st.number_input("Năm", min_value=2020, max_value=2100, value=now.year, key="set_bud_year")

        # Chọn category hoặc tổng
        cat_options = [(None, "📊 Tổng chi tiêu")] + [(c.id, c.name) for c in categories if c.type and c.type.startswith("expense")]
        selected_cat = st.selectbox(
            "Áp dụng cho",
            options=[x[0] for x in cat_options],
            format_func=lambda x: next((o[1] for o in cat_options if o[0] == x), ""),
        )

        amount = st.number_input("Hạn mức (VND)", min_value=0.0, step=500000.0, format="%.0f")
        notes = st.text_input("Ghi chú")

        if st.form_submit_button("✅ Lưu ngân sách", use_container_width=True):
            if amount <= 0:
                st.error("Hạn mức phải lớn hơn 0")
            else:
                ok, msg = BudgetService.set_budget(user_id, selected_cat, amount, month, year, notes or None)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # Danh sách ngân sách đã thiết lập
    st.markdown("---")
    section_header("Ngân sách đã thiết lập", "📋")
    budgets = BudgetService.get_budgets(user_id, now.month, now.year)
    if budgets:
        for b in budgets:
            budget_obj = b["budget"]
            col1, col2 = st.columns([4, 1])
            with col1:
                label = "Tổng chi tiêu" if not budget_obj.category_id else f"Danh mục #{budget_obj.category_id}"
                st.write(f"• {label}: {format_currency(budget_obj.amount)}")
            with col2:
                if st.button("🗑️", key=f"del_bud_{budget_obj.id}"):
                    ok, msg = BudgetService.delete_budget(user_id, budget_obj.id)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
