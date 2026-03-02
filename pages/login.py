"""Login page - Đăng nhập."""

import streamlit as st
from services.auth_service import AuthService
from schemas.user import UserCreate
from config import settings


def render_login():
    """Render trang đăng nhập."""
    st.markdown(
        """
        <div style="text-align:center; margin-top:2rem;">
            <h1>💰 Quản lý Tài chính</h1>
            <p style="color:#888;">Đăng nhập để tiếp tục</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Tên đăng nhập", placeholder=settings.ADMIN_USERNAME)
                password = st.text_input("Mật khẩu", type="password", placeholder="••••••")
                submitted = st.form_submit_button("🔑 Đăng nhập", use_container_width=True)

                if submitted:
                    if not username or not password:
                        st.error("Vui lòng nhập đầy đủ thông tin")
                        return

                    success, user_data, message = AuthService.login(username, password)
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user_data
                        st.session_state["user_id"] = user_data["id"]
                        st.session_state["username"] = user_data["username"]
                        st.rerun()
                    else:
                        st.error(message)

        with tab_register:
            with st.form("register_form"):
                reg_username = st.text_input("Tên đăng nhập mới", placeholder="nguyenvana")
                reg_display_name = st.text_input("Tên hiển thị", placeholder="Nguyễn Văn A")
                reg_email = st.text_input("Email (tuỳ chọn)", placeholder="name@email.com")
                reg_password = st.text_input("Mật khẩu", type="password")
                reg_confirm_password = st.text_input("Xác nhận mật khẩu", type="password")
                reg_submit = st.form_submit_button("✅ Tạo tài khoản", use_container_width=True)

                if reg_submit:
                    if not reg_username or not reg_display_name or not reg_password:
                        st.error("Vui lòng nhập đầy đủ thông tin bắt buộc")
                        return

                    if reg_password != reg_confirm_password:
                        st.error("Mật khẩu xác nhận không khớp")
                        return

                    try:
                        user_input = UserCreate(
                            username=reg_username.strip(),
                            password=reg_password,
                            display_name=reg_display_name.strip(),
                            email=(reg_email.strip() or None),
                        )
                    except Exception as exc:
                        st.error(str(exc))
                        return

                    ok, msg = AuthService.create_user(
                        username=user_input.username,
                        password=user_input.password,
                        display_name=user_input.display_name,
                        email=user_input.email,
                    )
                    if ok:
                        st.success("Tạo tài khoản thành công. Bạn có thể đăng nhập ngay.")
                    else:
                        st.error(msg)

        st.markdown(
            '<p style="text-align:center; font-size:0.8rem; color:#aaa; margin-top:2rem;">'
            f"Tài khoản mặc định: {settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}</p>",
            unsafe_allow_html=True,
        )
