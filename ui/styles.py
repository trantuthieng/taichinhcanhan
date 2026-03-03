import streamlit as st


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }
            .app-title {
                font-size: 1.2rem;
                font-weight: 700;
                margin-bottom: .5rem;
            }
            .muted {
                color: #888;
                font-size: .9rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

