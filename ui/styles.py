"""Styles – CSS tối giản cho dark theme."""


def inject_custom_css():
    """Inject CSS vào Streamlit app."""
    import streamlit as st

    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ===== FONT ===== */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* ===== LAYOUT ===== */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #12121e 0%, #0d0d18 100%);
    }
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #a0a0b8 !important;
        text-align: left !important;
        padding: 0.45rem 0.8rem !important;
        font-size: 0.88rem !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(108, 92, 231, 0.12) !important;
        color: #E8E8F0 !important;
    }

    /* ===== METRIC CARDS ===== */
    [data-testid="stMetric"] {
        background: rgba(26, 26, 46, 0.65);
        border: 1px solid rgba(108, 92, 231, 0.12);
        border-radius: 12px;
        padding: 0.9rem 1rem;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6c6c8a !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }

    /* ===== CARDS ===== */
    .card {
        background: rgba(26, 26, 46, 0.65);
        border: 1px solid rgba(108, 92, 231, 0.12);
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.7rem;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        border-radius: 8px !important;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6C5CE7, #a29bfe) !important;
        border: none !important;
    }

    /* ===== FORM INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border-color: rgba(108, 92, 231, 0.2) !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-size: 0.88rem;
    }

    /* ===== DATAFRAME ===== */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* ===== PROGRESS BAR CUSTOM ===== */
    .progress-wrap {
        background: rgba(108, 92, 231, 0.08);
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
        margin: 0.25rem 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }

    /* ===== WELCOME / EMPTY STATE ===== */
    .welcome-card {
        background: linear-gradient(135deg, rgba(108, 92, 231, 0.12), rgba(0, 206, 201, 0.06));
        border: 1px solid rgba(108, 92, 231, 0.2);
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    .empty-box {
        text-align: center;
        padding: 2rem 1rem;
        color: #6c6c8a;
    }
    .empty-box .icon { font-size: 2.2rem; margin-bottom: 0.4rem; }
    .empty-box .msg { font-size: 0.9rem; }

    /* ===== NAV ACTIVE ITEM ===== */
    .nav-active {
        display: flex;
        align-items: center;
        padding: 0.45rem 0.8rem;
        border-radius: 8px;
        margin-bottom: 4px;
        font-size: 0.88rem;
        font-weight: 600;
        background: rgba(108, 92, 231, 0.18);
        color: #a29bfe;
        border-left: 3px solid #6C5CE7;
    }

    /* ===== HIDE DEFAULTS ===== */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* ===== MOBILE ===== */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

