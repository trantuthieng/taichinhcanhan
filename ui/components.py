import streamlit as st
from utils.formatters import format_currency


def page_header(title: str, subtitle: str = "") -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def stat_card(label: str, value: float | int | str) -> None:
    if isinstance(value, (int, float)):
        st.metric(label, format_currency(value))
    else:
        st.metric(label, str(value))
