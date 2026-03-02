"""Forex page - Tỷ giá ngoại tệ."""

import streamlit as st
from datetime import datetime

from services.fx_service import FxService
from ui.components import section_header, empty_state, page_title
from utils.formatters import format_currency, format_number
from utils.constants import CURRENCIES


def render_forex():
    """Render trang tỷ giá ngoại tệ."""
    user_id = st.session_state["user_id"]

    page_title("Tỷ giá ngoại tệ", "💱", "Cập nhật realtime")

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
                result = FxService.sync_rates()
                if result.success:
                    st.success(result.message)
                    st.rerun()
                else:
                    st.warning(result.message)

    rates = FxService.get_latest_rates()
    if not rates:
        empty_state("Chưa có dữ liệu tỷ giá. Nhấn 'Đồng bộ tỷ giá' để cập nhật.", "💱")
        return

    # Hiển thị bảng tỷ giá
    import pandas as pd
    rows = []
    for r in rates:
        rows.append({
            "Ngoại tệ": r["currency_code"],
            "Mua TM": format_number(r["buy_rate"], 2) if r["buy_rate"] else "-",
            "Mua CK": format_number(r["transfer_rate"], 2) if r["transfer_rate"] else "-",
            "Bán": format_number(r["sell_rate"], 2) if r["sell_rate"] else "-",
            "Nguồn": r.get("source") or "",
            "Cập nhật": r["fetched_at"].strftime("%H:%M %d/%m") if r.get("fetched_at") else "",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Thông tin cập nhật
    if rates:
        fetched_times = [r["fetched_at"] for r in rates if r.get("fetched_at")]
        if fetched_times:
            last = max(fetched_times)
            st.caption(f"🕐 Cập nhật lần cuối: {last.strftime('%H:%M:%S %d/%m/%Y')}")


def _render_converter(user_id: int):
    """Quy đổi ngoại tệ."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_header("Quy đổi sang VND", "🔄")

    rates = FxService.get_latest_rates()
    available_currencies = [r["currency_code"] for r in rates] if rates else ["USD", "EUR", "JPY"]

    col1, col2 = st.columns(2)
    with col1:
        currency = st.selectbox("Ngoại tệ", available_currencies)
    with col2:
        amount = st.number_input("Số tiền", min_value=0.0, step=1.0, value=100.0)

    if st.button("💰 Quy đổi", use_container_width=True):
        result = FxService.convert_to_vnd(amount, currency)
        if result:
            st.success(f"**{format_number(amount, 2)} {currency}** = **{format_currency(result)}**")
        else:
            st.error(f"Không có tỷ giá cho {currency}. Hãy đồng bộ tỷ giá trước.")
    st.markdown('</div>', unsafe_allow_html=True)
