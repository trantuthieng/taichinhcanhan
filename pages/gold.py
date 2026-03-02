"""Gold page - Giá vàng & quản lý vàng."""

import streamlit as st
from datetime import date

from services.gold_service import GoldService
from ui.components import section_header, empty_state
from utils.formatters import format_currency, format_number, format_weight
from utils.constants import GOLD_TYPES


def render_gold():
    """Render trang vàng."""
    user_id = st.session_state["user_id"]

    st.markdown("## 🥇 Vàng")

    tab_prices, tab_holdings, tab_add = st.tabs(["📊 Giá vàng", "💰 Vàng nắm giữ", "➕ Thêm vàng"])

    with tab_prices:
        _render_gold_prices(user_id)

    with tab_holdings:
        _render_gold_holdings(user_id)

    with tab_add:
        _render_add_holding(user_id)


def _render_gold_prices(user_id: int):
    """Bảng giá vàng."""
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Đồng bộ giá vàng", use_container_width=True):
            with st.spinner("Đang cập nhật..."):
                ok, msg = GoldService.sync_prices()
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.warning(msg)

    prices = GoldService.get_latest_prices()
    if not prices:
        empty_state("Chưa có dữ liệu giá vàng. Nhấn 'Đồng bộ giá vàng' để cập nhật.", "🥇")
        return

    import pandas as pd
    rows = []
    for p in prices:
        rows.append({
            "Loại vàng": p.gold_type,
            "Mua": format_currency(p.buy_price) if p.buy_price else "-",
            "Bán": format_currency(p.sell_price) if p.sell_price else "-",
            "Đơn vị": p.unit or "lượng",
            "Nguồn": p.source or "",
            "Cập nhật": p.fetched_at.strftime("%H:%M %d/%m") if p.fetched_at else "",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if prices:
        last = max(p.fetched_at for p in prices if p.fetched_at)
        st.caption(f"🕐 Cập nhật lần cuối: {last.strftime('%H:%M:%S %d/%m/%Y')}")


def _render_gold_holdings(user_id: int):
    """Danh sách vàng nắm giữ."""
    holdings = GoldService.get_holdings_with_pnl(user_id)

    if not holdings:
        empty_state("Chưa có vàng nắm giữ", "🥇")
        return

    total_value = sum(h.get("market_value", 0) for h in holdings)
    total_cost = sum(h.get("total_cost", 0) for h in holdings)
    total_pnl = total_value - total_cost

    c1, c2, c3 = st.columns(3)
    c1.metric("Giá trị thị trường", format_currency(total_value))
    c2.metric("Giá vốn", format_currency(total_cost))
    pnl_color = "🟢" if total_pnl >= 0 else "🔴"
    c3.metric(f"{pnl_color} Lãi/Lỗ", format_currency(total_pnl))

    st.markdown("---")

    for h in holdings:
        holding = h["holding"]
        pnl = h.get("pnl", 0)
        pnl_icon = "📈" if pnl >= 0 else "📉"

        with st.expander(
            f"{pnl_icon} {holding.gold_type} - {format_weight(holding.weight_gram)} - P&L: {format_currency(pnl)}",
            expanded=False,
        ):
            st.write(f"**Loại:** {holding.gold_type}")
            st.write(f"**Trọng lượng:** {format_weight(holding.weight_gram)} ({holding.weight_gram}g)")
            st.write(f"**Giá mua:** {format_currency(holding.buy_price)}")
            st.write(f"**Ngày mua:** {holding.buy_date.strftime('%d/%m/%Y') if holding.buy_date else '-'}")
            st.write(f"**Giá vốn:** {format_currency(h.get('total_cost', 0))}")
            st.write(f"**Giá trị hiện tại:** {format_currency(h.get('market_value', 0))}")
            st.write(f"**Lãi/Lỗ:** {format_currency(pnl)}")

            if st.button("🗑️ Bán / Xóa", key=f"del_gold_{holding.id}"):
                ok, msg = GoldService.delete_holding(user_id, holding.id)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


def _render_add_holding(user_id: int):
    """Form thêm vàng."""
    with st.form("add_gold_form"):
        gold_type = st.selectbox("Loại vàng *", GOLD_TYPES)
        weight = st.number_input("Trọng lượng (gram) *", min_value=0.0, step=0.375, value=37.5)
        buy_price = st.number_input("Giá mua (VND/lượng) *", min_value=0.0, step=100000.0, format="%.0f")
        buy_date = st.date_input("Ngày mua", value=date.today())
        notes = st.text_area("Ghi chú")

        if st.form_submit_button("✅ Thêm vàng", use_container_width=True):
            if weight <= 0:
                st.error("Trọng lượng phải lớn hơn 0")
            elif buy_price <= 0:
                st.error("Giá mua phải lớn hơn 0")
            else:
                ok, msg = GoldService.add_holding(
                    user_id, gold_type, weight, buy_price, buy_date, notes or None
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
