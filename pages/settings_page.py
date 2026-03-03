import streamlit as st

from services.auth_service import AuthService
from services.settings_service import SettingsService
from ui.components import page_header


def render_settings() -> None:
    user_id = st.session_state["user_id"]
    page_header("Cài đặt")

    settings = SettingsService.get_all_settings(user_id)

    with st.form("settings_form"):
        fx_auto_sync = st.toggle("Tự động cập nhật tỷ giá", value=settings.get("fx_auto_sync", "true") == "true")
        gold_auto_sync = st.toggle("Tự động cập nhật giá vàng", value=settings.get("gold_auto_sync", "true") == "true")
        if st.form_submit_button("Lưu cài đặt", use_container_width=True):
            ok = SettingsService.bulk_update(
                user_id,
                {
                    "fx_auto_sync": str(fx_auto_sync).lower(),
                    "gold_auto_sync": str(gold_auto_sync).lower(),
                },
            )
            if ok:
                st.success("Đã lưu")
            else:
                st.error("Không lưu được")

    st.divider()
    st.subheader("Đổi mật khẩu")
    with st.form("change_pw"):
        old_password = st.text_input("Mật khẩu cũ", type="password")
        new_password = st.text_input("Mật khẩu mới", type="password")
        if st.form_submit_button("Đổi mật khẩu"):
            ok, msg = AuthService.change_password(user_id, old_password, new_password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
