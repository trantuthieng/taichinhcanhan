"""Global CSS styles for a modern, clean, and distinct look. V2."""

import streamlit as st


def inject_custom_css():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

            /* Global Font & Theme */
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }
            
            /* Remove standard Streamlit padding/margins for a tighter look */
            .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            
            /* Header cleanup */
            header[data-testid="stHeader"] {
                background: transparent;
            }
            #MainMenu, footer, [data-testid="stToolbar"] {
                visibility: hidden;
            }
            [data-testid="stSidebarNav"] {
                display: none;
            }

            /* ─── CUSTOM CARD COMPONENT ─── */
            .custom-card {
                background-color: #1E1E2E;
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                border: 1px solid #2B2B40;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            
            /* ─── METRIC CARDS ─── */
            div[data-testid="stMetric"] {
                background-color: #1E1E2E;
                padding: 1rem;
                border-radius: 10px;
                border: 1px solid #2B2B40;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            div[data-testid="stMetricLabel"] {
                font-size: 0.85rem;
                color: #A0A0B0;
                font-weight: 500;
            }
            div[data-testid="stMetricValue"] {
                font-size: 1.5rem;
                color: #FFFFFF;
                font-weight: 600;
            }
            div[data-testid="stMetricDelta"] {
                font-size: 0.8rem;
            }

            /* ─── SIDEBAR STYLING ─── */
            section[data-testid="stSidebar"] {
                background-color: #13131F;
                border-right: 1px solid #2B2B40;
            }
            
            /* Clean up sidebar buttons */
            .stButton button {
                background-color: transparent;
                border: none;
                color: #A0A0B0;
                text-align: left;
                padding-left: 0.5rem;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            .stButton button:hover {
                color: #FFFFFF;
                background-color: #2B2B40;
                border-radius: 6px;
                border: none;
            }
            .stButton button:focus {
                color: #FFFFFF;
                border: none;
                box-shadow: none;
            }
            
            /* Active Nav Indicator */
            .nav-active {
                background-color: #6C5CE7;
                color: white;
                padding: 0.5rem 0.75rem;
                border-radius: 6px;
                margin-bottom: 0.5rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                box-shadow: 0 4px 12px rgba(108, 92, 231, 0.25);
            }
            
            /* Sidebar Headers */
            div[data-testid="stCaptionContainer"] {
                color: #6C6C8A;
                font-weight: 700;
                letter-spacing: 0.05em;
                margin-top: 1rem;
                margin-bottom: 0.25rem;
                font-size: 0.75rem;
                text-transform: uppercase;
            }

            /* ─── DATAFRAME CLEANUP ─── */
            div[data-testid="stDataFrame"] {
                border: 1px solid #2B2B40;
                border-radius: 8px;
                overflow: hidden;
            }
            
            /* ─── TABS ─── */
            .stTabs [data-baseweb="tab-list"] {
                gap: 1rem;
                border-bottom: 1px solid #2B2B40;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: transparent;
                border-radius: 4px;
                color: #A0A0B0;
                padding: 0.5rem 1rem;
            }
            .stTabs [aria-selected="true"] {
                background-color: #2B2B40;
                color: #FFFFFF;
                font-weight: 600;
            }
            
             /* ─── EXPANDERS ─── */
            .streamlit-expanderHeader {
                background-color: #1E1E2E;
                color: #E0E0E0;
                border-radius: 8px;
                border: 1px solid #2B2B40;
            }
            .streamlit-expanderContent {
                background-color: #181825;
                border-radius: 0 0 8px 8px;
                border: 1px solid #2B2B40;
                border-top: none;
                padding: 1rem;
            }

        </style>
        """,
        unsafe_allow_html=True,
    )

