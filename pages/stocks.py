"""Stocks – Danh mục chứng khoán."""

import streamlit as st
from datetime import date

from services.stock_service import StockService
from ui.components import page_header, empty_state
from ui.charts import stock_portfolio_chart, stock_profit_bar
from utils.formatters import format_currency


def render_stocks():
    user_id = st.session_state["user_id"]
    page_header("Chứng khoán", "📈")

    tab_portfolio, tab_add, tab_price = st.tabs([
        "📊 Danh mục", "➕ Thêm cổ phiếu", "💲 Cập nhật giá",
    ])

    # ── Portfolio ──
    with tab_portfolio:
        holdings = StockService.get_holdings(user_id) or []
        info = StockService.get_total_portfolio_value(user_id)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tổng giá trị", format_currency(info.get("total_market_value", 0)))
        c2.metric("Tổng vốn", format_currency(info.get("total_cost", 0)))
        profit = info.get("total_profit", 0)
        c3.metric("Lãi/Lỗ", format_currency(profit),
                  f"{info.get('profit_pct', 0):+.1f}%")
        c4.metric("Số mã", info.get("count", 0))

        if not holdings:
            empty_state("Chưa có cổ phiếu nào", "📈")
        else:
            # Table
            rows = []
            for h in holdings:
                mkt = (h.current_price or h.avg_price) * h.quantity
                cost = h.avg_price * h.quantity
                pnl = mkt - cost
                rows.append({
                    "Mã": h.ticker,
                    "Tên": h.name or "",
                    "SL": int(h.quantity),
                    "Giá TB": format_currency(h.avg_price),
                    "Giá hiện tại": format_currency(h.current_price or 0),
                    "GT thị trường": format_currency(mkt),
                    "Lãi/Lỗ": format_currency(pnl),
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)

            # Charts
            summary = StockService.get_portfolio_summary(user_id)
            if summary:
                ch1, ch2 = st.columns(2)
                with ch1:
                    st.markdown("**Phân bổ danh mục**")
                    st.plotly_chart(stock_portfolio_chart(summary),
                                   use_container_width=True,
                                   config={"displayModeBar": False})
                with ch2:
                    st.markdown("**Lãi/Lỗ theo mã**")
                    st.plotly_chart(stock_profit_bar(summary),
                                   use_container_width=True,
                                   config={"displayModeBar": False})

            # Delete
            with st.expander("🗑️ Xoá cổ phiếu"):
                h_options = {
                    f"{h.ticker} – {int(h.quantity)} cp – TB {format_currency(h.avg_price)}": h.id
                    for h in holdings
                }
                sel = st.selectbox("Chọn", list(h_options.keys()))
                if st.button("Xoá", type="primary"):
                    ok, msg = StockService.delete_holding(user_id, h_options[sel])
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        st.rerun()

    # ── Add ──
    with tab_add:
        with st.form("add_stock_form"):
            col1, col2 = st.columns(2)
            with col1:
                ticker = st.text_input("Mã CK *", placeholder="VNM, FPT...").upper()
                name = st.text_input("Tên công ty", placeholder="Vinamilk")
                exchange = st.selectbox("Sàn", ["HOSE", "HNX", "UPCOM"])
            with col2:
                qty = st.number_input("Số lượng *", min_value=0, step=100, value=0)
                avg_price = st.number_input("Giá trung bình *", min_value=0.0, step=100.0)
                current_price = st.number_input("Giá hiện tại", min_value=0.0, step=100.0)
                buy_dt = st.date_input("Ngày mua", value=date.today())

            notes = st.text_area("Ghi chú", height=60)

            if st.form_submit_button("✅ Thêm cổ phiếu", use_container_width=True):
                if not ticker.strip():
                    st.error("Vui lòng nhập mã chứng khoán")
                elif qty <= 0 or avg_price <= 0:
                    st.error("Số lượng và giá phải lớn hơn 0")
                else:
                    ok, msg = StockService.add_holding(
                        user_id, ticker.strip(), qty, avg_price,
                        name=name.strip() or None, exchange=exchange,
                        current_price=current_price or None,
                        buy_date=buy_dt, notes=notes.strip() or None,
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ── Update prices ──
    with tab_price:
        holdings = StockService.get_holdings(user_id) or []
        if not holdings:
            empty_state("Chưa có cổ phiếu", "💲")
        else:
            st.caption("Nhập giá hiện tại cho từng mã")
            with st.form("update_prices_form"):
                price_map = {}
                for h in holdings:
                    price_map[h.ticker] = st.number_input(
                        f"{h.ticker} (hiện: {format_currency(h.current_price or 0)})",
                        min_value=0.0, step=100.0,
                        value=float(h.current_price or 0),
                        key=f"price_{h.id}",
                    )
                if st.form_submit_button("💲 Cập nhật giá", use_container_width=True):
                    ok, msg = StockService.update_prices(user_id, price_map)
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        st.rerun()
