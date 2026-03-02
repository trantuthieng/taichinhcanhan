"""Stock tracking page - Theo dõi danh mục chứng khoán."""

import streamlit as st
from datetime import date, datetime

from services.stock_service import StockService
from services.account_service import AccountService
from ui.components import metric_card, section_header, empty_state, page_title, stock_card
from ui.charts import stock_portfolio_chart, stock_profit_bar
from utils.formatters import format_currency, short_amount


def render_stocks():
    """Render trang chứng khoán."""
    user_id = st.session_state["user_id"]

    page_title("Chứng khoán", "📈", "Theo dõi danh mục đầu tư")

    # ===== TỔNG QUAN DANH MỤC =====
    portfolio = StockService.get_portfolio_summary(user_id)
    totals = StockService.get_total_portfolio_value(user_id)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Tổng giá trị", short_amount(totals["total_market_value"]),
                     card_type="stock", icon="📊")
    with c2:
        metric_card("Tổng vốn", short_amount(totals["total_cost"]),
                     card_type="balance", icon="💰")
    with c3:
        profit_delta = f"{totals['profit_pct']:+.1f}%" if totals["total_cost"] else ""
        metric_card("Lãi / Lỗ", short_amount(totals["total_profit"]),
                     delta=profit_delta, card_type="income" if totals["total_profit"] >= 0 else "expense",
                     icon="📈" if totals["total_profit"] >= 0 else "📉")
    with c4:
        metric_card("Số mã", str(totals["count"]),
                     card_type="savings", icon="🏷️")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ===== TABS =====
    tab_portfolio, tab_add, tab_update_price = st.tabs([
        "📋 Danh mục", "➕ Thêm mã", "💲 Cập nhật giá"
    ])

    # ====== TAB DANH MỤC ======
    with tab_portfolio:
        if portfolio:
            # Biểu đồ
            ch1, ch2 = st.columns(2)
            with ch1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                section_header("Phân bổ danh mục", "🍩")
                chart_data = [{"ticker": s["ticker"], "market_value": s["market_value"]} for s in portfolio if s["market_value"] > 0]
                if chart_data:
                    st.plotly_chart(stock_portfolio_chart(chart_data), use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)
            with ch2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                section_header("Lãi / Lỗ từng mã", "📊")
                profit_data = [{"ticker": s["ticker"], "profit": s["profit"]} for s in portfolio]
                st.plotly_chart(stock_profit_bar(profit_data), use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # Stock cards
            section_header("Chi tiết từng mã", "🏷️")
            cols = st.columns(min(len(portfolio), 3))
            for idx, s in enumerate(portfolio):
                with cols[idx % len(cols)]:
                    stock_card(
                        ticker=s["ticker"],
                        name=s["name"],
                        price=s["current_price"],
                        change_pct=s["profit_pct"],
                        quantity=s["total_qty"],
                        avg_price=s["avg_price"],
                    )

            # Chi tiết bảng
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            section_header("Bảng chi tiết", "📑")
            import pandas as pd
            df = pd.DataFrame([
                {
                    "Mã": s["ticker"],
                    "Tên": s["name"],
                    "SL": f"{s['total_qty']:,.0f}",
                    "Giá vốn TB": format_currency(s["avg_price"]),
                    "Giá TT": format_currency(s["current_price"]),
                    "Giá trị TT": format_currency(s["market_value"]),
                    "Lãi/Lỗ": format_currency(s["profit"]),
                    "%": f"{s['profit_pct']:+.1f}%",
                }
                for s in portfolio
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Xoá
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            with st.expander("🗑️ Xoá khoản nắm giữ"):
                holdings = StockService.get_holdings(user_id)
                if holdings:
                    options = {f"{h.ticker} - {h.quantity} CP @ {format_currency(h.avg_price)} (ID {h.id})": h.id for h in holdings}
                    sel = st.selectbox("Chọn khoản để xoá", list(options.keys()))
                    if st.button("🗑️ Xoá", type="secondary"):
                        ok, msg = StockService.delete_holding(user_id, options[sel])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            empty_state("Chưa có mã chứng khoán nào. Thêm mã ở tab '➕ Thêm mã'.", "📈")

    # ====== TAB THÊM MÃ ======
    with tab_add:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Thêm khoản nắm giữ mới", "➕")

        with st.form("add_stock_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                ticker = st.text_input("Mã chứng khoán *", placeholder="VD: VNM, FPT").upper().strip()
                name = st.text_input("Tên công ty / quỹ", placeholder="Vinamilk")
                exchange = st.selectbox("Sàn", ["HOSE", "HNX", "UPCOM"])
                quantity = st.number_input("Số lượng CP *", min_value=1, value=100, step=100)
            with col_b:
                avg_price = st.number_input("Giá vốn TB (VNĐ) *", min_value=0, value=0, step=1000)
                current_price = st.number_input("Giá thị trường (VNĐ)", min_value=0, value=0, step=1000)
                buy_date_val = st.date_input("Ngày mua", value=date.today())
                notes = st.text_area("Ghi chú", placeholder="VD: Mua qua SSI, dài hạn...")

            submitted = st.form_submit_button("✅ Thêm vào danh mục", use_container_width=True)
            if submitted:
                if not ticker or avg_price <= 0:
                    st.error("Vui lòng nhập mã CK và giá vốn > 0")
                else:
                    ok, msg = StockService.add_holding(
                        user_id=user_id,
                        ticker=ticker,
                        quantity=quantity,
                        avg_price=avg_price,
                        name=name or None,
                        exchange=exchange,
                        current_price=current_price if current_price > 0 else None,
                        buy_date=buy_date_val,
                        notes=notes or None,
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)

    # ====== TAB CẬP NHẬT GIÁ ======
    with tab_update_price:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("Cập nhật giá thị trường", "💲")

        if portfolio:
            st.markdown(
                "<p style='color:#6c6c8a; font-size:0.85rem;'>"
                "Nhập giá thị trường hiện tại cho từng mã để cập nhật lãi/lỗ.</p>",
                unsafe_allow_html=True,
            )
            with st.form("update_prices_form"):
                price_map = {}
                for s in portfolio:
                    val = st.number_input(
                        f"{s['ticker']} — hiện: {format_currency(s['current_price'])}",
                        min_value=0,
                        value=int(s["current_price"]),
                        step=100,
                        key=f"price_{s['ticker']}",
                    )
                    if val > 0:
                        price_map[s["ticker"]] = val

                if st.form_submit_button("💲 Cập nhật giá", use_container_width=True):
                    if price_map:
                        ok, msg = StockService.update_prices(user_id, price_map)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Chưa có giá nào để cập nhật")
        else:
            empty_state("Chưa có mã chứng khoán nào", "💲")
        st.markdown('</div>', unsafe_allow_html=True)
