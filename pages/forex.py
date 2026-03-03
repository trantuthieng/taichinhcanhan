"""Forex – Tỷ giá ngoại tệ."""

import streamlit as st
from services.fx_service import FxService
from ui.components import page_header, empty_state
from utils.formatters import format_currency
from utils.constants import CURRENCIES


def render_forex():
    user_id = st.session_state["user_id"]
    page_header("Tỷ giá ngoại tệ", "💱")

    tab_rates, tab_convert = st.tabs(["📋 Bảng tỷ giá", "🔄 Quy đổi"])

    # ── Rates table ──
    with tab_rates:
        rates = FxService.get_latest_rates() or []
        if not rates:
            empty_state("Chưa có dữ liệu tỷ giá", "💱")
            if st.button("🔄 Đồng bộ tỷ giá"):
                result = FxService.sync_rates()
                if result.success:
                    st.success(f"Đã cập nhật {len(result.data)} loại tiền")
                    st.rerun()
                else:
                    st.error(result.message)
        else:
            rows = [{
                "Tiền tệ": f"{r['currency_code']} – {r.get('currency_name', '')}",
                "Mua": format_currency(r.get("buy_rate", 0)),
                "Bán": format_currency(r.get("sell_rate", 0)),
                "Chuyển khoản": format_currency(r.get("transfer_rate", 0)),
                "Nguồn": r.get("source", ""),
            } for r in rates]
            st.dataframe(rows, use_container_width=True, hide_index=True)

            status = FxService.get_sync_status()
            if status:
                st.caption(
                    f"Nguồn: {status.get('provider', '')} | "
                    f"Trạng thái: {status.get('status', '')} | "
                    f"Lần cập nhật: {status.get('last_sync', 'N/A')}"
                )

            if st.button("🔄 Cập nhật tỷ giá"):
                result = FxService.sync_rates()
                if result.success:
                    st.success("Đã cập nhật tỷ giá")
                    st.rerun()
                else:
                    st.error(result.message)

    # ── Converter ──
    with tab_convert:
        st.markdown("**Quy đổi ngoại tệ sang VND**")
        col1, col2 = st.columns(2)
        with col1:
            fx_currencies = [c for c in CURRENCIES if c != "VND"]
            currency = st.selectbox("Tiền tệ", fx_currencies)
            amount = st.number_input("Số tiền", min_value=0.0, step=100.0, value=100.0)
        with col2:
            if st.button("Quy đổi", use_container_width=True):
                result = FxService.convert_to_vnd(amount, currency)
                if result:
                    st.metric(f"{amount:,.2f} {currency} =", format_currency(result))
                else:
                    st.warning(f"Chưa có tỷ giá cho {currency}")

            rate_info = FxService.get_rate(currency)
            if rate_info:
                st.caption(
                    f"Mua: {format_currency(rate_info.get('buy_rate', 0))} | "
                    f"Bán: {format_currency(rate_info.get('sell_rate', 0))}"
                )
