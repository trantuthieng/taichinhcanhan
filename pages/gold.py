import streamlit as st

from services.gold_service import GoldService
from ui.components import page_header
from utils.formatters import format_currency


def render_gold() -> None:
    user_id = st.session_state["user_id"]
    page_header("Vàng")

    total = GoldService.get_total_gold_value(user_id)
    st.metric("Tổng giá trị vàng", format_currency(total))

    holdings = GoldService.get_holdings_with_pnl(user_id)
    if holdings:
        st.dataframe(
            [
                {
                    "ID": int(item["holding"].id),
                    "Loại": item["holding"].gold_type,
                    "Số lượng": float(item["holding"].quantity),
                    "Giá vốn": format_currency(float(item["holding"].buy_price or 0)),
                    "Lãi/Lỗ": format_currency(float(item["pnl"] or 0)),
                }
                for item in holdings
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Chưa có nắm giữ vàng")

    st.divider()
    with st.form("add_gold_form"):
        gold_type = st.text_input("Loại vàng", value="SJC 1 lượng")
        quantity = st.number_input("Số lượng", min_value=0.1, step=0.1)
        unit = st.selectbox("Đơn vị", ["chỉ", "lượng"])
        buy_price = st.number_input("Giá mua", min_value=100000.0, step=100000.0)
        if st.form_submit_button("Thêm", use_container_width=True):
            ok, msg = GoldService.add_holding(user_id, gold_type.strip(), float(quantity), unit, float(buy_price))
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
