import streamlit as st

from services.goal_service import GoalService
from ui.components import page_header
from utils.formatters import format_currency


def render_goals() -> None:
    user_id = st.session_state["user_id"]
    page_header("Mục tiêu")

    goals = GoalService.get_goals(user_id)

    st.subheader("Danh sách")
    if not goals:
        st.info("Chưa có mục tiêu")
    else:
        for item in goals:
            goal = item["goal"]
            pct = float(item["percentage"])
            st.write(f"**{goal.name}** — {pct}%")
            st.progress(min(max(pct / 100.0, 0.0), 1.0))
            st.caption(f"{format_currency(goal.current_amount)} / {format_currency(goal.target_amount)}")
            col_a, col_b = st.columns([2, 1])
            add_amount = col_a.number_input("Đóng góp", min_value=0.0, step=10000.0, key=f"goal_amt_{goal.id}")
            if col_b.button("Nạp", key=f"goal_btn_{goal.id}"):
                ok, msg = GoalService.contribute(user_id, int(goal.id), float(add_amount))
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()
    st.subheader("Tạo mục tiêu mới")
    with st.form("new_goal_form"):
        name = st.text_input("Tên mục tiêu")
        target = st.number_input("Số tiền mục tiêu", min_value=100000.0, step=100000.0)
        if st.form_submit_button("Tạo", use_container_width=True):
            ok, msg = GoalService.create_goal(user_id, name.strip(), float(target))
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
