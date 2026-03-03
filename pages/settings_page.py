"""Settings – Cài đặt ứng dụng."""

import streamlit as st

from services.settings_service import SettingsService
from services.auth_service import AuthService
from ui.components import page_header
from utils.constants import CURRENCIES


def render_settings():
    user_id = st.session_state["user_id"]
    username = st.session_state.get("username", "")
    page_header("Cài đặt", "⚙️")

    settings = SettingsService.get_all_settings(user_id)

    tab_general, tab_sync, tab_pw, tab_about = st.tabs([
        "🌐 Chung", "🔄 Đồng bộ", "🔑 Mật khẩu", "ℹ️ Thông tin",
    ])

    # ── General ──
    with tab_general:
        with st.form("settings_general"):
            currency = st.selectbox(
                "Đơn vị tiền tệ mặc định",
                CURRENCIES,
                index=CURRENCIES.index(settings.get("currency", "VND")),
            )
            lang_options = ["vi", "en"]
            lang_labels = {"vi": "Tiếng Việt", "en": "English"}
            language = st.selectbox(
                "Ngôn ngữ",
                lang_options,
                index=lang_options.index(settings.get("language", "vi")),
                format_func=lambda x: lang_labels.get(x, x),
            )
            date_fmt_options = ["dd/mm/yyyy", "mm/dd/yyyy", "yyyy-mm-dd"]
            date_format = st.selectbox(
                "Định dạng ngày",
                date_fmt_options,
                index=date_fmt_options.index(settings.get("date_format", "dd/mm/yyyy")),
            )
            page_size = st.number_input(
                "Số bản ghi mỗi trang",
                min_value=10, max_value=100, step=10,
                value=int(settings.get("page_size", 20)),
            )

            if st.form_submit_button("💾 Lưu cài đặt", use_container_width=True):
                ok = SettingsService.bulk_update(user_id, {
                    "currency": currency,
                    "language": language,
                    "date_format": date_format,
                    "page_size": str(page_size),
                })
                st.success("Đã lưu cài đặt") if ok else st.error("Lỗi khi lưu")

    # ── Auto sync ──
    with tab_sync:
        with st.form("settings_sync"):
            fx_sync = st.toggle(
                "Tự động cập nhật tỷ giá",
                value=settings.get("fx_auto_sync", "true") == "true",
            )
            gold_sync = st.toggle(
                "Tự động cập nhật giá vàng",
                value=settings.get("gold_auto_sync", "true") == "true",
            )
            auto_backup = st.toggle(
                "Tự động sao lưu dữ liệu",
                value=settings.get("auto_backup", "true") == "true",
            )

            if st.form_submit_button("💾 Lưu", use_container_width=True):
                ok = SettingsService.bulk_update(user_id, {
                    "fx_auto_sync": "true" if fx_sync else "false",
                    "gold_auto_sync": "true" if gold_sync else "false",
                    "auto_backup": "true" if auto_backup else "false",
                })
                st.success("Đã lưu") if ok else st.error("Lỗi khi lưu")

    # ── Password ──
    with tab_pw:
        st.markdown(f"**Tài khoản:** {username}")
        with st.form("change_pw_form"):
            old_pw = st.text_input("Mật khẩu hiện tại", type="password")
            new_pw = st.text_input("Mật khẩu mới", type="password")
            confirm_pw = st.text_input("Nhập lại mật khẩu mới", type="password")

            if st.form_submit_button("🔑 Đổi mật khẩu", use_container_width=True):
                if not old_pw or not new_pw:
                    st.error("Vui lòng nhập đầy đủ thông tin")
                elif new_pw != confirm_pw:
                    st.error("Mật khẩu mới không khớp")
                elif len(new_pw) < 6:
                    st.error("Mật khẩu mới phải ít nhất 6 ký tự")
                else:
                    ok, msg = AuthService.change_password(user_id, old_pw, new_pw)
                    st.success(msg) if ok else st.error(msg)

    # ── About ──
    with tab_about:
        st.markdown("""
        ### 💰 Quản lý Tài chính Cá nhân
        **Phiên bản:** 2.0

        Ứng dụng quản lý tài chính cá nhân toàn diện:
        - 🏦 Quản lý tài khoản & số dư
        - 💳 Theo dõi thu chi hàng ngày
        - 📋 Ngân sách & mục tiêu tiết kiệm
        - 📈 Đầu tư chứng khoán, vàng
        - 💱 Cập nhật tỷ giá ngoại tệ
        - 📉 Báo cáo & phân tích chi tiết

        ---
        *Được phát triển với Streamlit & Python*
        """)
