"""Login page - Đăng nhập."""

import streamlit as st
from services.auth_service import AuthService


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
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="admin")
            password = st.text_input("Mật khẩu", type="password", placeholder="••••••")
            submitted = st.form_submit_button("🔑 Đăng nhập", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Vui lòng nhập đầy đủ thông tin")
                    return

                success, result = AuthService.login(username, password)
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = result
                    st.session_state["user_id"] = result.id
                    st.session_state["username"] = result.username
                    st.rerun()
                else:
                    st.error(result)

        st.markdown(
            '<p style="text-align:center; font-size:0.8rem; color:#aaa; margin-top:2rem;">'
            "Tài khoản mặc định: admin / admin123</p>",
            unsafe_allow_html=True,
        )
