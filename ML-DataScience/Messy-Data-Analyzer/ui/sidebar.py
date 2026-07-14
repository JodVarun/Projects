"""
Sidebar: API key, file upload, settings, sample datasets.
"""

import os
import streamlit as st
import pandas as pd
from pathlib import Path


SAMPLE_DIR = Path(__file__).parent.parent / "sample_data"


def render_sidebar():
    """Render the sidebar and return the loaded DataFrame (or None)."""
    with st.sidebar:
        # ── Logo & Title ────────────────────────────────────────────
        logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
        if logo_path.exists():
            st.image(str(logo_path), width=60)

        st.markdown("""
        <h1 style='margin:0; font-size:1.4rem; background: linear-gradient(135deg, #7C3AED, #06B6D4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing:-0.01em;'>
        Messy Data Analyzer</h1>
        <p style='color:#64748B; margin-top:2px; font-size:0.8rem;'>
        AI-powered data cleaning & analysis</p>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── API Key ─────────────────────────────────────────────────
        st.markdown("##### API Key")

        env_key = os.environ.get("GROQ_API_KEY", "")
        secrets_key = ""
        try:
            secrets_key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass

        default_key = env_key or secrets_key or ""

        if default_key and default_key != "your_groq_api_key_here":
            st.success("API key loaded from environment")
            api_key = default_key
        else:
            api_key = st.text_input(
                "Enter your Groq API key",
                type="password",
                placeholder="gsk_...",
                help="Get a free key at https://console.groq.com/"
            )

        if api_key:
            st.session_state['groq_api_key'] = api_key

        st.markdown("---")

        # ── Data Source ─────────────────────────────────────────────
        st.markdown("##### Load Data")

        source = st.radio(
            "Choose data source",
            ["Upload CSV", "Sample Dataset", "Kaggle Dataset"],
            label_visibility="collapsed"
        )

        df = None

        if source == "Upload CSV":
            uploaded = st.file_uploader(
                "Drop your CSV here",
                type=["csv", "xlsx", "xls"],
                help="Supports CSV and Excel files up to 200MB"
            )
            if uploaded:
                try:
                    if uploaded.name.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(uploaded)
                    else:
                        df = pd.read_csv(uploaded)
                    st.success(f"Loaded {len(df):,} rows × {len(df.columns)} cols")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")

        elif source == "Sample Dataset":
            samples = _get_sample_datasets()
            if samples:
                selected = st.selectbox("Choose a sample", list(samples.keys()))
                if st.button("Load Sample", use_container_width=True, type="primary"):
                    df = pd.read_csv(samples[selected])
                    st.success(f"Loaded '{selected}'")
            else:
                st.info("No sample datasets found in sample_data/")

        elif source == "Kaggle Dataset":
            st.markdown("""
            <div style='background:#1E1B4B; border-radius:8px; padding:12px; font-size:0.82rem;'>
            <b>Popular messy datasets:</b><br><br>
            <a href='https://www.kaggle.com/datasets/bhanupratapbiswas/cafe-sales-dirty-data-for-cleaning-training' target='_blank' style='color:#A78BFA;'>Cafe Sales (Dirty)</a><br>
            <a href='https://www.kaggle.com/datasets/rachittoshniwal/fifa-21-messy-raw-dataset-for-cleaning-exploring' target='_blank' style='color:#A78BFA;'>FIFA 21 (Messy)</a><br>
            <a href='https://www.kaggle.com/datasets/ahmedmohamed1997/retail-store-sales-dirty-for-data-cleaning' target='_blank' style='color:#A78BFA;'>Retail Sales (Dirty)</a><br>
            <br><span style='color:#64748B;'>Download from Kaggle, then upload above.</span>
            </div>
            """, unsafe_allow_html=True)

        if df is not None:
            st.session_state['dataframe'] = df

        st.markdown("---")

        # ── Settings ────────────────────────────────────────────────
        st.markdown("##### Settings")
        st.session_state['max_rows'] = st.slider("Preview rows", 5, 100, 20)
        st.session_state['show_reasoning'] = st.toggle("Show AI reasoning", value=True)

        st.markdown("---")
        st.markdown("""
        <div style='text-align:center; color:#475569; font-size:0.72rem;'>
        Built with Streamlit + Groq<br>
        <a href='https://console.groq.com/' style='color:#7C3AED;'>Groq Console</a>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.get('dataframe', None)


def _get_sample_datasets() -> dict:
    """Discover sample CSV files."""
    samples = {}
    if SAMPLE_DIR.exists():
        for f in sorted(SAMPLE_DIR.glob("*.csv")):
            name = f.stem.replace('_', ' ').title()
            samples[name] = str(f)
    return samples
