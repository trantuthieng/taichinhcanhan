"""Settings page - Cài đặt ứng dụng."""

import streamlit as st
import os

from services.settings_service import SettingsService
from services.auth_service import AuthService
from services.backup_service import BackupService
from services.fx_service import FxService
from services.gold_service import GoldService
from ui.components import section_header, empty_state


def render_settings():
    """Render trang cài đặt."""
    user_id = st.session_state["user_id"]

    st.markdown("## ⚙️ Cài đặt")

    tab_general, tab_password, tab_backup, tab_provider = st.tabs(
        ["🔧 Chung", "🔑 Mật khẩu", "💾 Sao lưu", "🌐 Nhà cung cấp"]
    )

    with tab_general:
        _render_general_settings(user_id)

    with tab_password:
        _render_change_password(user_id)

    with tab_backup:
        _render_backup(user_id)

    with tab_provider:
        _render_provider_status(user_id)


def _render_general_settings(user_id: int):
    """Cài đặt chung."""
    current = SettingsService.get_all_settings(user_id)

    with st.form("settings_form"):
        currency = st.selectbox("Đơn vị tiền tệ mặc định",
                                 ["VND", "USD", "EUR"],
                                 index=["VND", "USD", "EUR"].index(current.get("currency", "VND")))

        date_format = st.selectbox("Định dạng ngày",
                                    ["dd/mm/yyyy", "yyyy-mm-dd"],
                                    index=0 if current.get("date_format") == "dd/mm/yyyy" else 1)

        page_size = st.selectbox("Số bản ghi/trang",
                                  ["10", "20", "50", "100"],
                                  index=["10", "20", "50", "100"].index(current.get("page_size", "20")))

        auto_backup = st.checkbox("Tự động sao lưu", value=current.get("auto_backup") == "true")
        fx_auto = st.checkbox("Tự động cập nhật tỷ giá", value=current.get("fx_auto_sync") == "true")
        gold_auto = st.checkbox("Tự động cập nhật giá vàng", value=current.get("gold_auto_sync") == "true")

        if st.form_submit_button("💾 Lưu cài đặt", use_container_width=True):
            new_settings = {
                "currency": currency,
                "date_format": date_format,
                "page_size": page_size,
                "auto_backup": "true" if auto_backup else "false",
                "fx_auto_sync": "true" if fx_auto else "false",
                "gold_auto_sync": "true" if gold_auto else "false",
            }
            ok = SettingsService.bulk_update(user_id, new_settings)
            if ok:
                st.success("Đã lưu cài đặt")
            else:
                st.error("Lỗi khi lưu cài đặt")


def _render_change_password(user_id: int):
    """Đổi mật khẩu."""
    with st.form("change_pwd_form"):
        current_pwd = st.text_input("Mật khẩu hiện tại", type="password")
        new_pwd = st.text_input("Mật khẩu mới", type="password")
        confirm_pwd = st.text_input("Xác nhận mật khẩu mới", type="password")

        if st.form_submit_button("🔑 Đổi mật khẩu", use_container_width=True):
            if not current_pwd or not new_pwd:
                st.error("Vui lòng nhập đầy đủ")
            elif new_pwd != confirm_pwd:
                st.error("Mật khẩu mới không khớp")
            elif len(new_pwd) < 6:
                st.error("Mật khẩu mới ít nhất 6 ký tự")
            else:
                ok, msg = AuthService.change_password(user_id, current_pwd, new_pwd)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


def _render_backup(user_id: int):
    """Sao lưu & khôi phục."""
    section_header("Sao lưu", "💾")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Tạo bản sao lưu", use_container_width=True):
            with st.spinner("Đang sao lưu..."):
                ok, msg = BackupService.create_backup("manual")
                if ok:
                    st.success(f"Đã sao lưu: {os.path.basename(msg)}")
                else:
                    st.error(msg)

    with col2:
        db_path = BackupService.export_db()
        if os.path.exists(db_path):
            with open(db_path, "rb") as f:
                st.download_button(
                    "📥 Tải database",
                    data=f.read(),
                    file_name="finance.db",
                    mime="application/octet-stream",
                    use_container_width=True,
                )

    st.markdown("---")
    section_header("Danh sách bản sao lưu", "📋")
    backups = BackupService.list_backups()
    if backups:
        for b in backups:
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.write(f"📁 {b['name']} ({b['size_mb']} MB)")
            with col_b:
                st.write(b["date"].strftime("%d/%m/%Y %H:%M"))
            with col_c:
                if st.button("🔄 Khôi phục", key=f"restore_{b['name']}"):
                    ok, msg = BackupService.restore_backup(b["path"])
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
    else:
        empty_state("Chưa có bản sao lưu", "💾")


def _render_provider_status(user_id: int):
    """Trạng thái nhà cung cấp dữ liệu."""
    section_header("Trạng thái API", "🌐")

    # Token status
    from services.providers.token_manager import TokenManager
    tm = TokenManager()
    status = tm.get_token_status()

    for scope, info in status.items():
        if info.get("has_token"):
            remaining = info.get("remaining_seconds", 0)
            if remaining > 60:
                st.success(f"✅ **{scope}**: Token còn hạn ({remaining // 60} phút)")
            else:
                st.warning(f"⚠️ **{scope}**: Token sắp hết hạn ({remaining}s)")
        else:
            st.info(f"ℹ️ **{scope}**: Chưa có token")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Cập nhật tỷ giá", use_container_width=True):
            with st.spinner("Đang cập nhật..."):
                ok, msg = FxService.sync_rates()
                st.success(msg) if ok else st.warning(msg)

    with col2:
        if st.button("🔄 Cập nhật giá vàng", use_container_width=True):
            with st.spinner("Đang cập nhật..."):
                ok, msg = GoldService.sync_prices()
                st.success(msg) if ok else st.warning(msg)
