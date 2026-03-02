"""Goals page - Mục tiêu tài chính."""

import streamlit as st
from datetime import date

from services.goal_service import GoalService
from ui.components import section_header, empty_state, status_badge, progress_bar
from ui.charts import goal_progress_bar
from utils.formatters import format_currency, GOAL_STATUS_LABELS


def render_goals():
    """Render trang mục tiêu."""
    user_id = st.session_state["user_id"]

    st.markdown("## 🎯 Mục tiêu tài chính")

    tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm mới"])

    with tab_list:
        _render_goals_list(user_id)

    with tab_add:
        _render_add_goal(user_id)


def _render_goals_list(user_id: int):
    """Danh sách mục tiêu."""
    filter_status = st.selectbox("Trạng thái", ["active", "completed", "cancelled", "all"],
                                  format_func=lambda x: {"active": "Đang thực hiện", "completed": "Hoàn thành",
                                                         "cancelled": "Đã hủy", "all": "Tất cả"}.get(x, x))

    status = filter_status if filter_status != "all" else None
    goals = GoalService.get_goals(user_id, status)

    if not goals:
        empty_state("Chưa có mục tiêu nào", "🎯")
        return

    # Biểu đồ tổng quan
    active_goals = [g for g in goals if g["goal"].status == "active"]
    if active_goals:
        section_header("Tiến độ tổng quan", "📊")
        st.plotly_chart(goal_progress_bar(active_goals), use_container_width=True)
        st.markdown("---")

    for g in goals:
        goal = g["goal"]
        pct = g["percentage"]
        remaining = g["remaining"]
        days_left = g["days_left"]
        daily = g["daily_needed"]

        status_icon = {"active": "🟢", "completed": "✅", "cancelled": "❌"}.get(goal.status, "⚪")

        with st.expander(
            f"{status_icon} {goal.name} - {pct}% ({format_currency(goal.current_amount)} / {format_currency(goal.target_amount)})",
            expanded=False,
        ):
            st.write(f"**Mục tiêu:** {format_currency(goal.target_amount)}")
            st.write(f"**Đã tích lũy:** {format_currency(goal.current_amount)}")
            st.write(f"**Còn thiếu:** {format_currency(remaining)}")
            progress_bar(pct, f"{pct}%")

            if days_left is not None:
                if days_left > 0:
                    st.write(f"**Hạn:** {goal.deadline.strftime('%d/%m/%Y')} (còn {days_left} ngày)")
                    if daily:
                        st.write(f"**Cần tiết kiệm:** {format_currency(daily)}/ngày")
                elif days_left == 0:
                    st.warning("⏰ Hôm nay là hạn chót!")
                else:
                    st.error(f"⏰ Quá hạn {abs(days_left)} ngày!")

            if goal.notes:
                st.write(f"**Ghi chú:** {goal.notes}")

            if goal.status == "active":
                col1, col2, col3 = st.columns(3)
                with col1:
                    with st.popover("💰 Thêm tiền"):
                        contrib = st.number_input("Số tiền", min_value=0.0, step=100000.0,
                                                   key=f"contrib_{goal.id}", format="%.0f")
                        if st.button("✅ Xác nhận", key=f"contrib_ok_{goal.id}"):
                            if contrib > 0:
                                ok, msg = GoalService.contribute(user_id, goal.id, contrib)
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                with col2:
                    with st.popover("✏️ Sửa"):
                        new_name = st.text_input("Tên", value=goal.name, key=f"gname_{goal.id}")
                        new_target = st.number_input("Mục tiêu", value=float(goal.target_amount),
                                                      key=f"gtarget_{goal.id}", format="%.0f")
                        new_date = st.date_input("Hạn", value=goal.deadline, key=f"gdate_{goal.id}") if goal.deadline else st.date_input("Hạn", key=f"gdate2_{goal.id}")
                        if st.button("💾 Lưu", key=f"gsave_{goal.id}"):
                            ok, msg = GoalService.update_goal(user_id, goal.id,
                                                               name=new_name, target_amount=new_target,
                                                               deadline=new_date)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                with col3:
                    if st.button("❌ Hủy", key=f"cancel_goal_{goal.id}"):
                        ok, msg = GoalService.cancel_goal(user_id, goal.id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)


def _render_add_goal(user_id: int):
    """Form thêm mục tiêu."""
    with st.form("add_goal_form"):
        name = st.text_input("Tên mục tiêu *", placeholder="VD: Mua xe, Du lịch, Quỹ khẩn cấp...")
        target_amount = st.number_input("Số tiền mục tiêu *", min_value=0.0, step=1000000.0, format="%.0f")
        current_amount = st.number_input("Đã tích lũy", min_value=0.0, step=100000.0, value=0.0, format="%.0f")
        target_date = st.date_input("Hạn hoàn thành (tuỳ chọn)", value=None)
        notes = st.text_area("Ghi chú")

        if st.form_submit_button("✅ Tạo mục tiêu", use_container_width=True):
            if not name.strip():
                st.error("Vui lòng nhập tên mục tiêu")
            elif target_amount <= 0:
                st.error("Số tiền mục tiêu phải lớn hơn 0")
            else:
                ok, msg = GoalService.create_goal(
                    user_id, name.strip(), target_amount, current_amount,
                    target_date, notes or None
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
