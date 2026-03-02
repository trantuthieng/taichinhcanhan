"""Forex page - Tỷ giá ngoại tệ."""

import streamlit as st
from datetime import datetime

from services.fx_service import FxService
from ui.components import section_header, empty_state
from utils.formatters import format_currency, format_number
from utils.constants import CURRENCIES


def render_forex():
    """Render trang tỷ giá ngoại tệ."""
    user_id = st.session_state["user_id"]

    st.markdown("## 💱 Tỷ giá ngoại tệ")

    tab_rates, tab_convert = st.tabs(["📊 Bảng tỷ giá", "🔄 Quy đổi"])

    with tab_rates:
        _render_rates(user_id)

    with tab_convert:
        _render_converter(user_id)


def _render_rates(user_id: int):
    """Bảng tỷ giá."""
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Đồng bộ tỷ giá", use_container_width=True):
            with st.spinner("Đang cập nhật..."):
                ok, msg = FxService.sync_rates()
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.warning(msg)

    rates = FxService.get_latest_rates()
    if not rates:
        empty_state("Chưa có dữ liệu tỷ giá. Nhấn 'Đồng bộ tỷ giá' để cập nhật.", "💱")
        return

    # Hiển thị bảng tỷ giá
    import pandas as pd
    rows = []
    for r in rates:
        rows.append({
            "Ngoại tệ": r.currency_code,
            "Mua TM": format_number(r.buy_cash, 2) if r.buy_cash else "-",
            "Mua CK": format_number(r.buy_transfer, 2) if r.buy_transfer else "-",
            "Bán": format_number(r.sell, 2) if r.sell else "-",
            "Nguồn": r.source or "",
            "Cập nhật": r.fetched_at.strftime("%H:%M %d/%m") if r.fetched_at else "",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Thông tin cập nhật
    if rates:
        last = max(r.fetched_at for r in rates if r.fetched_at)
        st.caption(f"🕐 Cập nhật lần cuối: {last.strftime('%H:%M:%S %d/%m/%Y')}")


def _render_converter(user_id: int):
    """Quy đổi ngoại tệ."""
    section_header("Quy đổi sang VND", "🔄")

    rates = FxService.get_latest_rates()
    available_currencies = [r.currency_code for r in rates] if rates else ["USD", "EUR", "JPY"]

    col1, col2 = st.columns(2)
    with col1:
        currency = st.selectbox("Ngoại tệ", available_currencies)
    with col2:
        amount = st.number_input("Số tiền", min_value=0.0, step=1.0, value=100.0)

    if st.button("💰 Quy đổi", use_container_width=True):
        result = FxService.convert_to_vnd(currency, amount)
        if result:
            st.success(f"**{format_number(amount, 2)} {currency}** = **{format_currency(result)}**")
        else:
            st.error(f"Không có tỷ giá cho {currency}. Hãy đồng bộ tỷ giá trước.")
