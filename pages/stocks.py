import streamlit as st

from services.stock_service import StockService
from ui.components import page_header
from utils.formatters import format_currency


def render_stocks() -> None:
    user_id = st.session_state["user_id"]
    page_header("Chứng khoán")

    info = StockService.get_total_portfolio_value(user_id)
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng giá trị", format_currency(info.get("total_market_value", 0)))
    c2.metric("Lãi/Lỗ", format_currency(info.get("total_profit", 0)))
    c3.metric("Số mã", info.get("count", 0))

    holdings = StockService.get_holdings(user_id)
    if holdings:
        st.dataframe(
            [
                {
                    "ID": int(h.id),
                    "Mã": h.ticker,
                    "Khối lượng": float(h.quantity),
                    "Giá vốn": format_currency(float(h.avg_price or 0)),
                    "Giá thị trường": format_currency(float(h.current_price or 0)),
                }
                for h in holdings
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Chưa có cổ phiếu")

    st.divider()
    with st.form("add_stock_form"):
        ticker = st.text_input("Mã cổ phiếu").upper().strip()
        quantity = st.number_input("Khối lượng", min_value=1.0, step=1.0)
        avg_price = st.number_input("Giá mua", min_value=1000.0, step=1000.0)
        if st.form_submit_button("Thêm", use_container_width=True):
            ok, msg = StockService.add_holding(user_id, ticker, float(quantity), float(avg_price))
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
