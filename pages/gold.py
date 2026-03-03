"""Gold – Vàng."""

import streamlit as st
from datetime import date

from services.gold_service import GoldService
from ui.components import page_header, empty_state
from utils.formatters import format_currency
from utils.constants import GOLD_TYPES


def render_gold():
    user_id = st.session_state["user_id"]
    page_header("Vàng", "🥇")

    tab_holdings, tab_prices, tab_add = st.tabs([
        "📊 Tài sản vàng", "💲 Giá vàng", "➕ Thêm vàng",
    ])

    # ── Holdings ──
    with tab_holdings:
        total_val = GoldService.get_total_gold_value(user_id)
        holdings_pnl = GoldService.get_holdings_with_pnl(user_id) or []

        c1, c2 = st.columns(2)
        c1.metric("Tổng giá trị vàng", format_currency(total_val))
        c2.metric("Số lô", len(holdings_pnl))

        if not holdings_pnl:
            empty_state("Chưa có vàng", "🥇")
        else:
            rows = []
            for h in holdings_pnl:
                holding = h["holding"]
                rows.append({
                    "Loại": holding.gold_type,
                    "SL": f"{holding.quantity} {holding.unit}",
                    "Giá mua": format_currency(holding.buy_price),
                    "Giá hiện tại": format_currency(h.get("current_price", 0)),
                    "Giá trị": format_currency(h.get("market_value", 0)),
                    "Lãi/Lỗ": format_currency(h.get("pnl", 0)),
                    "% Lãi/Lỗ": f"{h.get('pnl_pct', 0):+.1f}%",
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)

            # Delete
            with st.expander("🗑️ Xoá lô vàng"):
                h_options = {
                    f"{h['holding'].gold_type} – {h['holding'].quantity} {h['holding'].unit}": h["holding"].id
                    for h in holdings_pnl
                }
                sel = st.selectbox("Chọn lô", list(h_options.keys()))
                if st.button("Xoá", type="primary"):
                    ok, msg = GoldService.delete_holding(user_id, h_options[sel])
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        st.rerun()

    # ── Prices ──
    with tab_prices:
        prices = GoldService.get_latest_prices() or []
        if not prices:
            empty_state("Chưa có dữ liệu giá vàng", "💲")
            if st.button("🔄 Đồng bộ giá vàng"):
                result = GoldService.sync_prices()
                if result.success:
                    st.success(f"Đã cập nhật {len(result.data)} loại vàng")
                    st.rerun()
                else:
                    st.error(result.message)
        else:
            rows = [{
                "Loại": p["gold_type"],
                "Mua": format_currency(p.get("buy_price", 0)),
                "Bán": format_currency(p.get("sell_price", 0)),
                "Nguồn": p.get("source", ""),
            } for p in prices]
            st.dataframe(rows, use_container_width=True, hide_index=True)
            if st.button("🔄 Cập nhật giá"):
                result = GoldService.sync_prices()
                if result.success:
                    st.success("Đã cập nhật giá vàng")
                    st.rerun()
                else:
                    st.error(result.message)

    # ── Add ──
    with tab_add:
        with st.form("add_gold_form"):
            col1, col2 = st.columns(2)
            with col1:
                gold_type = st.selectbox("Loại vàng *", GOLD_TYPES)
                quantity = st.number_input("Số lượng *", min_value=0.0, step=0.1, value=1.0)
                unit = st.selectbox("Đơn vị", ["lượng", "chỉ"])
            with col2:
                buy_price = st.number_input("Giá mua (VND/đơn vị) *",
                                            min_value=0.0, step=100000.0)
                buy_dt = st.date_input("Ngày mua", value=date.today())

            notes = st.text_area("Ghi chú", height=60)

            if st.form_submit_button("✅ Thêm vàng", use_container_width=True):
                if quantity <= 0 or buy_price <= 0:
                    st.error("Số lượng và giá mua phải lớn hơn 0")
                else:
                    ok, msg = GoldService.add_holding(
                        user_id, gold_type, quantity, unit, buy_price,
                        buy_date=buy_dt, notes=notes.strip() or None,
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
