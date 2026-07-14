"""
Messy Data Analyzer — Main Application
AI-powered data cleaning & analysis with Streamlit + Groq.
"""

import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load .env file for API keys
load_dotenv()

# ── Page Config ─────────────────────────────────────────────────────
logo_path = Path(__file__).parent / "assets" / "logo.png"
st.set_page_config(
    page_title="Messy Data Analyzer",
    page_icon=str(logo_path) if logo_path.exists() else "M",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #1A1D29;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 28px;
        font-weight: 500;
        color: #94A3B8;
        font-size: 0.9rem;
        letter-spacing: 0.01em;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #7C3AED, #6D28D9);
        color: white;
    }

    /* Container borders */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border-color: #2D314830 !important;
        border-radius: 10px !important;
        background: #1A1D2940 !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        opacity: 0.7;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7C3AED, #6D28D9);
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        letter-spacing: 0.01em;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #8B5CF6, #7C3AED);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.25);
    }
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #2D3148;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #7C3AED;
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981, #059669);
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #7C3AED !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #E2E8F0;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    ::-webkit-scrollbar-track {
        background: #0E1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #2D3148;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #7C3AED;
    }

    /* Section headers */
    h3, h4 {
        letter-spacing: -0.01em;
    }
</style>
""", unsafe_allow_html=True)


# ── Import UI Modules ───────────────────────────────────────────────
from ui.sidebar import render_sidebar
from ui.overview_tab import render_overview_tab
from ui.quality_tab import render_quality_tab
from ui.explore_tab import render_explore_tab
from ui.chat_tab import render_chat_tab
from core.analyzer import analyze_dataset


# ── Sidebar (returns df or None) ────────────────────────────────────
df = render_sidebar()


# ── Main Content ────────────────────────────────────────────────────
if df is None:
    # Landing page
    st.markdown("""
    <div style='text-align:center; padding:80px 20px;'>
        <h1 style='background: linear-gradient(135deg, #7C3AED, #06B6D4);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size:2.8rem; margin:0 0 12px; letter-spacing:-0.02em;'>
            Messy Data Analyzer
        </h1>
        <p style='color:#94A3B8; font-size:1.1rem; max-width:560px; margin:0 auto 48px; line-height:1.6;'>
            Upload a messy CSV and let AI detect quality issues, clean your data
            with transparent reasoning, and answer your questions in plain English.
        </p>
        <div style='display:flex; justify-content:center; gap:48px; flex-wrap:wrap; max-width:800px; margin:0 auto;'>
            <div style='text-align:center; padding:24px 16px; min-width:150px;'>
                <div style='width:48px; height:48px; border-radius:12px; margin:0 auto 12px;
                            background: linear-gradient(135deg, #7C3AED20, #7C3AED08);
                            border: 1px solid #7C3AED30; display:flex; align-items:center;
                            justify-content:center;'>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
                </div>
                <p style='color:#E2E8F0; font-weight:600; margin:0 0 4px; font-size:0.95rem;'>Auto Analysis</p>
                <p style='color:#64748B; font-size:0.82rem; line-height:1.4;'>Detect missing values, outliers,<br>duplicates, and type issues</p>
            </div>
            <div style='text-align:center; padding:24px 16px; min-width:150px;'>
                <div style='width:48px; height:48px; border-radius:12px; margin:0 auto 12px;
                            background: linear-gradient(135deg, #06B6D420, #06B6D408);
                            border: 1px solid #06B6D430; display:flex; align-items:center;
                            justify-content:center;'>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#06B6D4" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                </div>
                <p style='color:#E2E8F0; font-weight:600; margin:0 0 4px; font-size:0.95rem;'>AI Reasoning</p>
                <p style='color:#64748B; font-size:0.82rem; line-height:1.4;'>Understand <em>why</em> each<br>cleaning action is suggested</p>
            </div>
            <div style='text-align:center; padding:24px 16px; min-width:150px;'>
                <div style='width:48px; height:48px; border-radius:12px; margin:0 auto 12px;
                            background: linear-gradient(135deg, #F59E0B20, #F59E0B08);
                            border: 1px solid #F59E0B30; display:flex; align-items:center;
                            justify-content:center;'>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                </div>
                <p style='color:#E2E8F0; font-weight:600; margin:0 0 4px; font-size:0.95rem;'>Ask Questions</p>
                <p style='color:#64748B; font-size:0.82rem; line-height:1.4;'>Chat with your data<br>in plain English</p>
            </div>
            <div style='text-align:center; padding:24px 16px; min-width:150px;'>
                <div style='width:48px; height:48px; border-radius:12px; margin:0 auto 12px;
                            background: linear-gradient(135deg, #10B98120, #10B98108);
                            border: 1px solid #10B98130; display:flex; align-items:center;
                            justify-content:center;'>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                </div>
                <p style='color:#E2E8F0; font-weight:600; margin:0 0 4px; font-size:0.95rem;'>Smart Charts</p>
                <p style='color:#64748B; font-size:0.82rem; line-height:1.4;'>Auto-generated visualizations<br>based on your data</p>
            </div>
        </div>
        <p style='color:#475569; margin-top:56px; font-size:0.85rem;'>
            Upload a CSV or choose a sample dataset from the sidebar to get started
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Analyze Data ────────────────────────────────────────────────
    if 'report' not in st.session_state or st.session_state.get('_last_df_id') != id(df):
        with st.spinner("Analyzing data quality..."):
            report = analyze_dataset(df)
            st.session_state['report'] = report
            st.session_state['_last_df_id'] = id(df)
    
    report = st.session_state['report']

    # ── Tab Navigation ──────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview",
        "Data Quality",
        "Explore",
        "AI Chat"
    ])

    with tab1:
        render_overview_tab(df, report)

    with tab2:
        render_quality_tab(df, report)

    with tab3:
        render_explore_tab(df)

    with tab4:
        render_chat_tab(df)
