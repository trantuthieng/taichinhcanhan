"""Styles - CSS tùy chỉnh cho giao diện dark glassmorphism."""


def inject_custom_css():
    """Inject CSS tùy chỉnh vào Streamlit."""
    import streamlit as st

    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ===== ROOT VARIABLES ===== */
    :root {
        --bg-primary: #0F0F1A;
        --bg-card: rgba(26, 26, 46, 0.7);
        --bg-card-hover: rgba(38, 38, 62, 0.8);
        --border-glass: rgba(108, 92, 231, 0.2);
        --accent-purple: #6C5CE7;
        --accent-blue: #74b9ff;
        --accent-green: #00cec9;
        --accent-red: #ff6b6b;
        --accent-orange: #fdcb6e;
        --accent-pink: #e84393;
        --text-primary: #E8E8F0;
        --text-secondary: #a0a0b8;
        --text-muted: #6c6c8a;
        --shadow-glow: 0 0 30px rgba(108, 92, 231, 0.15);
        --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* ===== GLOBAL ===== */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }

    /* ===== GLASSMORPHISM CARDS ===== */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: var(--shadow-card);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-card:hover {
        background: var(--bg-card-hover);
        border-color: rgba(108, 92, 231, 0.4);
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow), var(--shadow-card);
    }

    /* ===== METRIC CARDS ===== */
    .metric-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 1.2rem 1rem;
        text-align: center;
        margin-bottom: 0.75rem;
        box-shadow: var(--shadow-card);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-glow), var(--shadow-card);
    }
    .metric-card.income::before { background: linear-gradient(90deg, #00cec9, #55efc4); }
    .metric-card.expense::before { background: linear-gradient(90deg, #ff6b6b, #ee5a24); }
    .metric-card.balance::before { background: linear-gradient(90deg, #6C5CE7, #a29bfe); }
    .metric-card.savings::before { background: linear-gradient(90deg, #fdcb6e, #f39c12); }
    .metric-card.stock::before { background: linear-gradient(90deg, #74b9ff, #0984e3); }

    .metric-card .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 0.3rem;
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.2rem;
    }
    .metric-card .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0.15rem 0;
    }
    .metric-card .metric-delta {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.2rem;
    }
    .metric-card .metric-delta.positive { color: var(--accent-green); }
    .metric-card .metric-delta.negative { color: var(--accent-red); }

    /* ===== ACCOUNT CARDS ===== */
    .account-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 1.1rem;
        margin-bottom: 0.6rem;
        box-shadow: var(--shadow-card);
        border-left: 3px solid var(--accent-purple);
        transition: all 0.3s ease;
    }
    .account-card:hover {
        border-left-color: var(--accent-blue);
        transform: translateX(4px);
    }
    .account-card .acc-name {
        font-weight: 600;
        font-size: 1rem;
        color: var(--text-primary);
    }
    .account-card .acc-balance {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--accent-blue);
        margin-top: 0.2rem;
    }
    .account-card .acc-type {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 0.15rem;
    }

    /* ===== TRANSACTION LIST ===== */
    .tx-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.85rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.4rem;
        background: var(--bg-card);
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }
    .tx-item:hover {
        border-color: var(--border-glass);
        background: var(--bg-card-hover);
    }
    .tx-item .tx-info { flex: 1; }
    .tx-item .tx-info strong { color: var(--text-primary); }
    .tx-item .tx-cat {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 0.15rem;
    }
    .tx-item .tx-amount {
        font-weight: 700;
        white-space: nowrap;
        font-size: 0.95rem;
    }
    .tx-item .tx-amount.income { color: var(--accent-green); }
    .tx-item .tx-amount.expense { color: var(--accent-red); }

    /* ===== STOCK CARDS ===== */
    .stock-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 0.6rem;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
    }
    .stock-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }
    .stock-ticker {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--accent-blue);
    }
    .stock-name {
        font-size: 0.78rem;
        color: var(--text-muted);
    }
    .stock-price {
        font-size: 1.15rem;
        font-weight: 700;
    }
    .stock-change {
        font-size: 0.82rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 6px;
        display: inline-block;
    }
    .stock-change.up {
        color: var(--accent-green);
        background: rgba(0, 206, 201, 0.12);
    }
    .stock-change.down {
        color: var(--accent-red);
        background: rgba(255, 107, 107, 0.12);
    }
    .stock-change.neutral {
        color: var(--accent-orange);
        background: rgba(253, 203, 110, 0.12);
    }

    /* ===== PROGRESS BAR ===== */
    .progress-container {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        overflow: hidden;
        height: 8px;
        margin: 0.5rem 0;
    }
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .progress-bar.safe { background: linear-gradient(90deg, #00cec9, #55efc4); }
    .progress-bar.warning { background: linear-gradient(90deg, #fdcb6e, #f39c12); }
    .progress-bar.danger { background: linear-gradient(90deg, #ff6b6b, #ee5a24); }

    /* ===== BADGES ===== */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-active { background: rgba(0, 206, 201, 0.15); color: #00cec9; }
    .badge-completed { background: rgba(108, 92, 231, 0.15); color: #a29bfe; }
    .badge-cancelled { background: rgba(255, 107, 107, 0.15); color: #ff6b6b; }
    .badge-matured { background: rgba(253, 203, 110, 0.15); color: #fdcb6e; }

    /* ===== SECTION HEADER ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-glass);
    }
    .section-header .sh-icon { font-size: 1.3rem; }
    .section-header .sh-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* ===== EMPTY STATE ===== */
    .empty-state {
        text-align: center;
        padding: 2.5rem 1rem;
        color: var(--text-muted);
        background: var(--bg-card);
        border-radius: 16px;
        border: 1px dashed var(--border-glass);
    }
    .empty-state .es-icon { font-size: 2.5rem; margin-bottom: 0.5rem; opacity: 0.6; }
    .empty-state p { margin: 0; font-size: 0.9rem; }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        min-width: 260px !important;
        background: linear-gradient(180deg, #0F0F1A 0%, #16162a 50%, #1A1A2E 100%) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: var(--text-primary);
    }

    .sidebar-header {
        text-align: center;
        padding: 1.2rem 0.5rem 0.8rem;
    }
    .sidebar-header .logo { font-size: 2.2rem; margin-bottom: 0.3rem; }
    .sidebar-header .app-name {
        font-weight: 700;
        font-size: 1.15rem;
        background: linear-gradient(135deg, #6C5CE7, #a29bfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sidebar-header .welcome {
        color: var(--text-muted);
        font-size: 0.82rem;
        margin-top: 0.2rem;
    }

    /* nav items */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.6rem 0.9rem;
        border-radius: 10px;
        margin-bottom: 0.15rem;
        cursor: pointer;
        transition: all 0.2s ease;
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
        text-decoration: none;
    }
    .nav-item:hover {
        background: rgba(108, 92, 231, 0.12);
        color: var(--text-primary);
    }
    .nav-item.active {
        background: linear-gradient(135deg, rgba(108, 92, 231, 0.25), rgba(162, 155, 254, 0.15));
        color: #a29bfe;
        font-weight: 600;
        border-left: 3px solid var(--accent-purple);
    }
    .nav-item .nav-icon { font-size: 1.1rem; width: 1.5rem; text-align: center; }

    /* ===== BUTTONS ===== */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid var(--border-glass) !important;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(108, 92, 231, 0.3);
        border-color: var(--accent-purple) !important;
    }

    /* ===== FORM INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {
        border-radius: 10px !important;
        border-color: var(--border-glass) !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: var(--bg-card);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid var(--border-glass);
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1.2rem;
        font-size: 0.88rem;
        font-weight: 500;
        border-radius: 8px;
        color: var(--text-secondary);
    }
    .stTabs [aria-selected="true"] {
        background: rgba(108, 92, 231, 0.2) !important;
        color: var(--accent-purple) !important;
    }

    /* ===== DATA TABLES ===== */
    .stDataFrame, .stTable {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ===== DIVIDER ===== */
    hr {
        border: none;
        border-top: 1px solid var(--border-glass);
        margin: 1.2rem 0;
    }

    /* ===== PAGE TITLE ===== */
    .page-title {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 1.5rem;
    }
    .page-title .pt-icon { font-size: 1.8rem; }
    .page-title .pt-text {
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--text-primary), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .page-title .pt-sub {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-left: auto;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(108, 92, 231, 0.3); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(108, 92, 231, 0.5); }

    /* ===== HIDE STREAMLIT DEFAULTS ===== */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ===== MOBILE ===== */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        .metric-card .metric-value { font-size: 1.3rem; }
        .metric-card { padding: 0.9rem 0.7rem; }
        [data-testid="stSidebar"] { min-width: 220px !important; }
    }

    /* ===== ANIMATIONS ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeInUp 0.5s ease forwards;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

