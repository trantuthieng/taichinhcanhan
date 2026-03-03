import streamlit as st

from services.fx_service import FxService
from ui.components import page_header
from utils.formatters import format_currency


def render_forex() -> None:
    page_header("Tỷ giá")

    FxService.sync_rates()
    rates = FxService.get_latest_rates()

    if not rates:
        st.info("Không có dữ liệu tỷ giá")
        return

    st.dataframe(
        [
            {
                "Mã": r["currency_code"],
                "Mua": format_currency(float(r.get("buy_rate") or 0)),
                "Bán": format_currency(float(r.get("sell_rate") or 0)),
                "Nguồn": r.get("source") or "",
            }
            for r in rates
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    c1, c2 = st.columns(2)
    code = c1.selectbox("Ngoại tệ", [r["currency_code"] for r in rates])
    amount = c2.number_input("Số tiền", min_value=0.0, value=100.0)
    result = FxService.convert_to_vnd(float(amount), code)
    st.success(f"{amount} {code} = {format_currency(result)}")
