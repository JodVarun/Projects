"""
Overview Tab: Dataset summary, KPIs, data preview, column info.
"""

import streamlit as st
import pandas as pd
from core.analyzer import AnalysisReport


def render_overview_tab(df: pd.DataFrame, report: AnalysisReport):
    """Render the dataset overview dashboard."""

    # ── KPI Cards ───────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(_kpi_card("Rows", f"{report.total_rows:,}", "#7C3AED"), unsafe_allow_html=True)
    with k2:
        st.markdown(_kpi_card("Columns", f"{report.total_columns}", "#06B6D4"), unsafe_allow_html=True)
    with k3:
        score_color = "#10B981" if report.quality_score >= 70 else ("#F59E0B" if report.quality_score >= 40 else "#EF4444")
        st.markdown(_kpi_card("Quality Score", f"{report.quality_score}/100", score_color), unsafe_allow_html=True)
    with k4:
        st.markdown(_kpi_card("Memory", f"{report.memory_usage_mb} MB", "#EC4899"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick Stats Row ─────────────────────────────────────────────
    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Missing Values", f"{report.total_missing:,}",
                  delta=f"{(report.total_missing/(report.total_rows*report.total_columns)*100):.1f}% of cells" if report.total_rows > 0 else "0%",
                  delta_color="inverse")
    with s2:
        st.metric("Duplicate Rows", f"{report.duplicate_rows:,}",
                  delta=f"{(report.duplicate_rows/report.total_rows*100):.1f}%" if report.total_rows > 0 else "0%",
                  delta_color="inverse")
    with s3:
        st.metric("Issues Found", f"{len(report.issues)}",
                  delta="Critical" if any(i.severity == 'critical' for i in report.issues) else "None critical",
                  delta_color="inverse" if any(i.severity == 'critical' for i in report.issues) else "normal")

    st.markdown("---")

    # ── Data Preview ────────────────────────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("#### Data Preview")
        max_rows = st.session_state.get('max_rows', 20)
        st.dataframe(df.head(max_rows), use_container_width=True, height=400)

    with col_right:
        st.markdown("#### Column Info")
        col_info_data = []
        for col in df.columns:
            col_info_data.append({
                "Column": col,
                "Type": _type_badge(str(df[col].dtype)),
                "Non-Null": f"{df[col].count():,}",
                "Unique": f"{df[col].nunique():,}",
            })
        st.dataframe(pd.DataFrame(col_info_data), use_container_width=True, height=400, hide_index=True)

    # ── Summary Statistics ──────────────────────────────────────────
    if report.summary_stats is not None:
        with st.expander("Summary Statistics", expanded=False):
            st.dataframe(report.summary_stats, use_container_width=True)


def _kpi_card(title: str, value: str, color: str) -> str:
    return f"""
    <div style='background: linear-gradient(135deg, {color}12, {color}06);
                border: 1px solid {color}25; border-radius: 10px;
                padding: 20px; text-align: center;'>
        <p style='margin:0; color:#94A3B8; font-size:0.75rem; text-transform:uppercase;
                  letter-spacing:0.06em; font-weight:500;'>{title}</p>
        <p style='margin:6px 0 0; color:{color}; font-size:1.8rem; font-weight:700;
                  letter-spacing:-0.02em;'>{value}</p>
    </div>
    """


def _type_badge(dtype: str) -> str:
    if 'int' in dtype or 'float' in dtype:
        return dtype
    elif 'object' in dtype:
        return "text"
    elif 'datetime' in dtype:
        return "date"
    elif 'bool' in dtype:
        return "bool"
    return dtype
