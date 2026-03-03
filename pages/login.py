import streamlit as st

from config import settings
from services.auth_service import AuthService


def render_login() -> None:
    st.title("Đăng nhập")
    st.caption("Nhập tài khoản để vào ứng dụng")

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Tên đăng nhập", value=settings.ADMIN_USERNAME)
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập", use_container_width=True)

        if submitted:
            ok, user_data, msg = AuthService.login(username, password)
            if ok and user_data:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user_data["id"]
                st.session_state["username"] = user_data["username"]
                st.session_state["current_page"] = "dashboard"
                st.rerun()
            else:
                st.error(msg)

    st.info(f"Tài khoản mặc định: {settings.ADMIN_USERNAME}")
