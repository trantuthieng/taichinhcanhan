"""Goals – Mục tiêu tiết kiệm."""

import streamlit as st
from datetime import date

from services.goal_service import GoalService
from ui.components import page_header, empty_state, progress_bar
from utils.formatters import format_currency


def render_goals():
    user_id = st.session_state["user_id"]
    page_header("Mục tiêu tiết kiệm", "🎯")

    tab_list, tab_add = st.tabs(["📋 Danh sách", "➕ Thêm mục tiêu"])

    # ── List ──
    with tab_list:
        status_filter = st.selectbox(
            "Trạng thái",
            [None, "active", "completed", "cancelled"],
            format_func=lambda x: {
                None: "Tất cả", "active": "🟢 Đang thực hiện",
                "completed": "✅ Hoàn thành", "cancelled": "❌ Đã huỷ",
            }.get(x, x),
        )
        goals = GoalService.get_goals(user_id, status_filter)

        if not goals:
            empty_state("Chưa có mục tiêu nào", "🎯")
        else:
            # Summary
            active_goals = [g for g in goals if g["goal"].status == "active"]
            total_target = sum(g["goal"].target_amount for g in active_goals)
            total_current = sum(g["goal"].current_amount for g in active_goals)
            c1, c2 = st.columns(2)
            c1.metric("Tổng mục tiêu", format_currency(total_target))
            c2.metric("Đã tích luỹ", format_currency(total_current))

            st.markdown("")

            for g in goals:
                goal = g["goal"]
                pct = g["percentage"]
                remaining = g["remaining"]
                days_left = g.get("days_left")
                daily = g.get("daily_needed")

                status_icon = {"active": "🟢", "completed": "✅", "cancelled": "❌"}.get(
                    goal.status, "⚪"
                )
                color = "#00cec9" if pct >= 100 else "#6C5CE7"

                with st.expander(
                    f"{status_icon} {goal.name} — {pct:.0f}% "
                    f"({format_currency(goal.current_amount)} / {format_currency(goal.target_amount)})"
                ):
                    progress_bar(pct, 100, color)

                    info_parts = [f"**Còn thiếu:** {format_currency(remaining)}"]
                    if days_left is not None:
                        info_parts.append(f"**Còn {days_left} ngày**")
                    if daily and daily > 0:
                        info_parts.append(f"Cần ~{format_currency(daily)}/ngày")
                    st.write(" | ".join(info_parts))

                    if goal.notes:
                        st.caption(goal.notes)

                    if goal.status == "active":
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            contrib = st.number_input("Số tiền góp",
                                                      min_value=0.0, step=100000.0,
                                                      key=f"contrib_{goal.id}")
                            if st.button("💰 Góp", key=f"do_contrib_{goal.id}"):
                                if contrib > 0:
                                    ok, msg = GoalService.contribute(user_id, goal.id, contrib)
                                    st.success(msg) if ok else st.error(msg)
                                    if ok:
                                        st.rerun()
                        with col_c:
                            if st.button("❌ Huỷ mục tiêu", key=f"cancel_{goal.id}"):
                                ok, msg = GoalService.cancel_goal(user_id, goal.id)
                                st.success(msg) if ok else st.error(msg)
                                if ok:
                                    st.rerun()

    # ── Add ──
    with tab_add:
        with st.form("add_goal_form"):
            name = st.text_input("Tên mục tiêu *", placeholder="Mua xe, du lịch...")
            target = st.number_input("Số tiền mục tiêu *", min_value=0.0, step=1000000.0)
            current = st.number_input("Số tiền đã có", min_value=0.0, step=100000.0, value=0.0)
            deadline = st.date_input("Hạn chót (tuỳ chọn)", value=None)
            notes = st.text_area("Ghi chú", height=60)

            if st.form_submit_button("✅ Tạo mục tiêu", use_container_width=True):
                if not name.strip():
                    st.error("Vui lòng nhập tên mục tiêu")
                elif target <= 0:
                    st.error("Số tiền mục tiêu phải lớn hơn 0")
                else:
                    ok, msg = GoalService.create_goal(
                        user_id, name.strip(), target, current,
                        target_date=deadline, notes=notes.strip() or None,
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
