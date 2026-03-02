"""Styles - CSS tùy chỉnh cho giao diện mobile-first."""


def inject_custom_css():
    """Inject CSS tùy chỉnh vào Streamlit."""
    import streamlit as st

    css = """
    <style>
    /* ===== MOBILE-FIRST RESPONSIVE ===== */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card.income {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .metric-card.expense {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    .metric-card.balance {
        background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
    }
    .metric-card.savings {
        background: linear-gradient(135deg, #F09819 0%, #EDDE5D 100%);
    }
    .metric-card .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0.25rem 0;
    }
    .metric-card .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    .metric-card .metric-delta {
        font-size: 0.75rem;
        opacity: 0.8;
    }

    /* Account cards */
    .account-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .account-card .acc-name {
        font-weight: 600;
        font-size: 1rem;
        color: #333;
    }
    .account-card .acc-balance {
        font-size: 1.2rem;
        font-weight: 700;
        color: #2196F3;
    }
    .account-card .acc-type {
        font-size: 0.8rem;
        color: #888;
    }

    /* Transaction list item */
    .tx-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .tx-item .tx-info {
        flex: 1;
    }
    .tx-item .tx-cat {
        font-size: 0.8rem;
        color: #888;
    }
    .tx-item .tx-amount {
        font-weight: 700;
        white-space: nowrap;
    }
    .tx-item .tx-amount.income {
        color: #11998e;
    }
    .tx-item .tx-amount.expense {
        color: #eb3349;
    }

    /* Progress bar custom */
    .progress-container {
        background: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        height: 10px;
        margin: 0.5rem 0;
    }
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    .progress-bar.safe { background: linear-gradient(90deg, #11998e, #38ef7d); }
    .progress-bar.warning { background: linear-gradient(90deg, #F09819, #EDDE5D); }
    .progress-bar.danger { background: linear-gradient(90deg, #eb3349, #f45c43); }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-active { background: #d4edda; color: #155724; }
    .badge-completed { background: #cce5ff; color: #004085; }
    .badge-cancelled { background: #f8d7da; color: #721c24; }
    .badge-matured { background: #fff3cd; color: #856404; }

    /* Sidebar tuning */
    [data-testid="stSidebar"] {
        min-width: 240px !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Data editor / table */
    .stDataFrame {
        font-size: 0.85rem;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        .metric-card .metric-value {
            font-size: 1.2rem;
        }
        [data-testid="stSidebar"] {
            min-width: 200px !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.4rem 0.6rem;
            font-size: 0.8rem;
        }
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #888; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #555; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
