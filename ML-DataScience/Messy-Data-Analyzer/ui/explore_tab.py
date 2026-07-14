"""
Data Exploration Tab: Auto-charts, custom viz, correlation analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
from core.visualizer import create_overview_charts, create_custom_chart


def render_explore_tab(df: pd.DataFrame):
    """Render the data exploration tab."""

    # ── Auto-Generated Charts ───────────────────────────────────────
    st.markdown("#### Auto-Generated Insights")
    st.caption("Charts are automatically selected based on your data types.")

    charts = create_overview_charts(df)
    if not charts:
        st.info("No charts could be generated from this dataset.")
        return

    for i in range(0, len(charts), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(charts):
                chart = charts[i + j]
                with col:
                    with st.container(border=True):
                        st.plotly_chart(chart["figure"], use_container_width=True, key=f"auto_{i+j}")

    st.markdown("---")

    # ── Custom Chart Builder ────────────────────────────────────────
    st.markdown("#### Custom Chart Builder")

    builder_cols = st.columns([1, 1, 1, 1])
    with builder_cols[0]:
        x_col = st.selectbox("X-Axis", df.columns.tolist(), key="x_col")
    with builder_cols[1]:
        y_options = ["(none)"] + df.columns.tolist()
        y_col = st.selectbox("Y-Axis", y_options, key="y_col")
    with builder_cols[2]:
        chart_type = st.selectbox("Chart Type", ["bar", "scatter", "line", "box", "histogram"])
    with builder_cols[3]:
        st.markdown("<br>", unsafe_allow_html=True)
        build_btn = st.button("Build Chart", type="primary", use_container_width=True)

    if build_btn:
        y = y_col if y_col != "(none)" else None
        try:
            fig = create_custom_chart(df, x_col, y, chart_type)
            st.plotly_chart(fig, use_container_width=True, key="custom_chart")
        except Exception as e:
            st.error(f"Could not create chart: {str(e)}")

    st.markdown("---")

    # ── Column Deep Dive ────────────────────────────────────────────
    st.markdown("#### Column Deep Dive")
    selected_col = st.selectbox("Select a column to analyze", df.columns.tolist(), key="deep_dive_col")

    if selected_col:
        col_data = df[selected_col]
        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Non-null", f"{col_data.count():,}")
        with c2:
            st.metric("Unique Values", f"{col_data.nunique():,}")
        with c3:
            st.metric("Missing", f"{col_data.isnull().sum():,}")

        if pd.api.types.is_numeric_dtype(col_data):
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Mean", f"{col_data.mean():.2f}")
            s2.metric("Median", f"{col_data.median():.2f}")
            s3.metric("Std Dev", f"{col_data.std():.2f}")
            s4.metric("Range", f"{col_data.min():.0f} – {col_data.max():.0f}")

        # Value counts
        with st.expander("Value Distribution", expanded=True):
            vc = col_data.value_counts().head(20)
            st.bar_chart(vc)
