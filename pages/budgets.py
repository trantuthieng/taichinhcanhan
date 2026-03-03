"""Budgets – Ngân sách."""

import streamlit as st
from datetime import datetime

from services.budget_service import BudgetService
from services.category_service import CategoryService
from ui.components import page_header, empty_state, progress_bar, color_for_pct
from utils.formatters import format_currency


def render_budgets():
    user_id = st.session_state["user_id"]
    now = datetime.now()

    page_header("Ngân sách", "📋", f"Tháng {now.month}/{now.year}")

    cat_service = CategoryService()

    tab_view, tab_set = st.tabs(["📊 Theo dõi", "➕ Thiết lập"])

    # ── View ──
    with tab_view:
        month = now.month
        year = now.year

        col_m, col_y = st.columns(2)
        with col_m:
            month = st.selectbox("Tháng", range(1, 13), index=month - 1,
                                 format_func=lambda x: f"Tháng {x}")
        with col_y:
            year = st.number_input("Năm", min_value=2020, max_value=2030, value=year)

        budgets = BudgetService.get_budgets(user_id, month, year)

        if not budgets:
            empty_state("Chưa thiết lập ngân sách cho tháng này", "📋")
        else:
            total_spent = sum(b["spent"] for b in budgets)
            total_budget = sum(b["budget"].amount for b in budgets)
            over_count = sum(1 for b in budgets if b["is_over"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng ngân sách", format_currency(total_budget))
            c2.metric("Đã chi", format_currency(total_spent))
            c3.metric("Vượt ngân sách", f"{over_count} mục" if over_count else "Không có")

            st.markdown("")

            for b in budgets:
                label = b["budget"].category.name if b["budget"].category_id else "📌 Tổng chi tiêu"
                pct = b["percentage"]
                color = color_for_pct(pct)
                status = "🔴 Vượt!" if b["is_over"] else ("🟡 Cẩn thận" if pct >= 80 else "🟢 Ổn")

                col_l, col_r = st.columns([5, 1])
                with col_l:
                    st.markdown(f"**{label}** — {format_currency(b['spent'])} / "
                                f"{format_currency(b['budget'].amount)}")
                    progress_bar(pct, 100, color)
                with col_r:
                    st.markdown(f"<div style='text-align:center; padding-top:0.3rem;'>"
                                f"<span style='font-size:1.1rem;'>{pct:.0f}%</span><br>"
                                f"<span style='font-size:0.75rem;'>{status}</span></div>",
                                unsafe_allow_html=True)

                # Delete
                if st.button("🗑️ Xoá", key=f"del_bud_{b['budget'].id}"):
                    ok, msg = BudgetService.delete_budget(user_id, b["budget"].id)
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        st.rerun()

    # ── Set budget ──
    with tab_set:
        with st.form("set_budget_form"):
            categories = cat_service.get_expense_categories(user_id) or []
            cat_id = st.selectbox(
                "Danh mục",
                [None] + [c.id for c in categories],
                format_func=lambda x: "📌 Tổng chi tiêu" if x is None
                else next((c.name for c in categories if c.id == x), ""),
            )
            amount = st.number_input("Ngân sách (VND) *", min_value=0.0, step=100000.0)
            b_month = st.selectbox("Tháng", range(1, 13), index=now.month - 1,
                                   format_func=lambda x: f"Tháng {x}", key="b_month")
            b_year = st.number_input("Năm", min_value=2020, max_value=2030,
                                     value=now.year, key="b_year")
            notes = st.text_area("Ghi chú", height=60)

            if st.form_submit_button("✅ Lưu ngân sách", use_container_width=True):
                if amount <= 0:
                    st.error("Số tiền phải lớn hơn 0")
                else:
                    ok, msg = BudgetService.set_budget(
                        user_id, cat_id, amount, b_month, b_year, notes.strip() or None
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
