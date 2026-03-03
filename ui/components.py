"""Reusable UI components."""

import streamlit as st


def page_header(title: str, icon: str = "", subtitle: str = ""):
    """Render page header."""
    left, right = st.columns([4, 1])
    with left:
        st.markdown(f"### {icon}  {title}" if icon else f"### {title}")
    if subtitle:
        with right:
            st.markdown(
                f"<div style='text-align:right; color:#6c6c8a; padding-top:0.6rem; "
                f"font-size:0.85rem;'>{subtitle}</div>",
                unsafe_allow_html=True,
            )


def empty_state(msg: str = "Chưa có dữ liệu", icon: str = "📭"):
    """Empty data placeholder."""
    st.markdown(
        f'<div class="empty-box"><div class="icon">{icon}</div>'
        f'<div class="msg">{msg}</div></div>',
        unsafe_allow_html=True,
    )


def progress_bar(value: float, max_val: float = 100, color: str = "#6C5CE7"):
    """Custom thin progress bar. value and max_val are the raw numbers."""
    pct = min(value / max_val * 100, 100) if max_val else 0
    st.markdown(
        f'<div class="progress-wrap">'
        f'<div class="progress-fill" style="width:{pct:.1f}%; background:{color};"></div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def color_for_pct(pct: float) -> str:
    """Return color based on budget usage percentage."""
    if pct < 70:
        return "#00cec9"
    if pct < 90:
        return "#fdcb6e"
    return "#ff6b6b"


def nav_to(page_key: str, nav_labels: dict):
    """Navigate to a page by setting session state and rerunning."""
    for label, key in nav_labels.items():
        if key == page_key:
            st.session_state["nav"] = label
            break
    st.rerun()
