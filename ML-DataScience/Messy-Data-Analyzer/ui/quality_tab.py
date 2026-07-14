"""
Data Quality Tab: Issue cards, AI reasoning, cleaning actions.
"""

import streamlit as st
import pandas as pd
from core.analyzer import AnalysisReport, analyze_dataset
from core.cleaner import get_cleaning_suggestions, apply_cleaning_action


SEVERITY_COLORS = {
    'critical': '#EF4444',
    'warning': '#F59E0B',
    'info': '#10B981',
}


def render_quality_tab(df: pd.DataFrame, report: AnalysisReport):
    """Render the data quality & cleaning tab."""

    # ── Quality Score Gauge ─────────────────────────────────────────
    score = report.quality_score
    score_color = "#10B981" if score >= 70 else ("#F59E0B" if score >= 40 else "#EF4444")
    score_label = "Excellent" if score >= 80 else ("Good" if score >= 60 else ("Needs Work" if score >= 40 else "Poor"))

    st.markdown(f"""
    <div style='text-align:center; padding:20px;'>
        <div style='display:inline-block; position:relative; width:160px; height:160px;'>
            <svg viewBox='0 0 36 36' style='width:160px; height:160px; transform:rotate(-90deg);'>
                <path d='M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831'
                    fill='none' stroke='#1A1D29' stroke-width='3'/>
                <path d='M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831'
                    fill='none' stroke='{score_color}' stroke-width='3'
                    stroke-dasharray='{score}, 100'
                    style='transition: stroke-dasharray 1s ease;'/>
            </svg>
            <div style='position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);'>
                <span style='font-size:2rem; font-weight:700; color:{score_color};'>{score}</span>
                <br><span style='font-size:0.78rem; color:#94A3B8; font-weight:500;'>{score_label}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not report.issues:
        st.success("No data quality issues detected. Your dataset looks clean.")
        return

    # ── Issue Summary ───────────────────────────────────────────────
    critical = sum(1 for i in report.issues if i.severity == 'critical')
    warnings = sum(1 for i in report.issues if i.severity == 'warning')
    infos = sum(1 for i in report.issues if i.severity == 'info')

    c1, c2, c3 = st.columns(3)
    c1.metric("Critical", critical)
    c2.metric("Warnings", warnings)
    c3.metric("Info", infos)

    st.markdown("---")

    # ── AI Cleaning Suggestions ─────────────────────────────────────
    api_key = st.session_state.get('groq_api_key', '')

    if api_key:
        if 'cleaning_actions' not in st.session_state:
            with st.spinner("AI is analyzing your data and generating cleaning suggestions..."):
                actions = get_cleaning_suggestions(df, report.issues, api_key)
                st.session_state['cleaning_actions'] = actions

        actions = st.session_state.get('cleaning_actions', [])

        if actions:
            st.markdown("#### AI Cleaning Suggestions")

            # Apply All button
            if st.button("Apply All Fixes", type="primary", use_container_width=True):
                current_df = st.session_state['dataframe'].copy()
                for action in actions:
                    try:
                        current_df = apply_cleaning_action(current_df, action)
                    except Exception:
                        pass
                st.session_state['dataframe'] = current_df
                st.session_state['report'] = analyze_dataset(current_df)
                if 'cleaning_actions' in st.session_state:
                    del st.session_state['cleaning_actions']
                st.rerun()

            st.markdown("")

            for idx, action in enumerate(actions):
                _render_action_card(df, action, idx)

    else:
        st.info("Enter your Groq API key in the sidebar to get AI-powered cleaning suggestions.")

    # ── Issue Cards (always shown) ──────────────────────────────────
    st.markdown("#### All Detected Issues")

    for issue in sorted(report.issues, key=lambda x: {'critical': 0, 'warning': 1, 'info': 2}.get(x.severity, 3)):
        sev_color = SEVERITY_COLORS.get(issue.severity, '#64748B')

        st.markdown(f"""
        <div style='background:#1A1D2940; border-left:3px solid {sev_color};
                    border-radius:8px; padding:14px 16px; margin-bottom:8px;'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-weight:600; color:#E2E8F0;'>
                    <span style='display:inline-block; width:8px; height:8px; border-radius:50%;
                                background:{sev_color}; margin-right:8px;'></span>
                    {issue.issue_type.replace('_',' ').title()}
                </span>
                <span style='color:#64748B; font-size:0.8rem;'>Column: <code>{issue.column}</code></span>
            </div>
            <p style='margin:6px 0 0; color:#94A3B8; font-size:0.88rem;'>{issue.description}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Download Cleaned Data ───────────────────────────────────────
    st.markdown("---")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Current Data as CSV",
        data=csv,
        file_name="cleaned_data.csv",
        mime="text/csv",
        use_container_width=True
    )


def _render_action_card(df, action, idx):
    """Render a single cleaning action card with reasoning."""
    show_reasoning = st.session_state.get('show_reasoning', True)

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{action.action.replace('_', ' ').title()}** → `{action.column}`")
            if show_reasoning:
                st.markdown(f"""
                <div style='background:#1E1B4B30; border-radius:6px; padding:10px; margin:6px 0;
                            border-left:2px solid #7C3AED;'>
                    <span style='color:#A78BFA; font-size:0.72rem; text-transform:uppercase;
                                letter-spacing:0.06em; font-weight:500;'>AI Reasoning</span><br>
                    <span style='color:#CBD5E1; font-size:0.85rem; line-height:1.5;'>{action.reasoning}</span>
                </div>
                """, unsafe_allow_html=True)
            st.caption(f"Affects {action.rows_affected:,} rows")
        with col2:
            if st.button("Apply", key=f"apply_{idx}", use_container_width=True):
                try:
                    new_df = apply_cleaning_action(st.session_state['dataframe'], action)
                    st.session_state['dataframe'] = new_df
                    st.session_state['report'] = analyze_dataset(new_df)
                    if 'cleaning_actions' in st.session_state:
                        del st.session_state['cleaning_actions']
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")
