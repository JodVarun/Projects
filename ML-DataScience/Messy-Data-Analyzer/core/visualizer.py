"""
Auto-Visualization Engine
Generates relevant Plotly charts based on data types.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Consistent dark theme for all charts
CHART_TEMPLATE = "plotly_dark"
COLOR_PALETTE = ["#7C3AED", "#06B6D4", "#F59E0B", "#EF4444", "#10B981", "#EC4899", "#8B5CF6", "#14B8A6"]


def create_overview_charts(df: pd.DataFrame) -> list[dict]:
    """Generate a set of overview charts for the dataset."""
    charts = []

    # 1. Missing values heatmap
    missing_chart = create_missing_heatmap(df)
    if missing_chart:
        charts.append({"title": "Missing Values Map", "figure": missing_chart})

    # 2. Data type distribution
    dtype_chart = create_dtype_chart(df)
    charts.append({"title": "Column Types", "figure": dtype_chart})

    # 3. Numeric distributions
    num_cols = df.select_dtypes(include=[np.number]).columns[:6]
    if len(num_cols) > 0:
        dist_chart = create_distributions(df, num_cols.tolist())
        charts.append({"title": "Numeric Distributions", "figure": dist_chart})

    # 4. Correlation heatmap
    if len(num_cols) >= 2:
        corr_chart = create_correlation_heatmap(df)
        if corr_chart:
            charts.append({"title": "Correlation Matrix", "figure": corr_chart})

    # 5. Top categorical distributions
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols[:2]:
        if df[col].nunique() <= 20:
            cat_chart = create_categorical_chart(df, col)
            charts.append({"title": f"{col} Distribution", "figure": cat_chart})

    return charts


def create_missing_heatmap(df: pd.DataFrame):
    """Create a visual map of missing data."""
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) == 0:
        return None

    fig = go.Figure(go.Bar(
        x=missing.index.tolist(),
        y=missing.values.tolist(),
        marker_color=COLOR_PALETTE[3],
        marker_line_width=0,
        text=[f"{v} ({v/len(df)*100:.1f}%)" for v in missing.values],
        textposition='auto',
    ))
    fig.update_layout(
        template=CHART_TEMPLATE,
        title="Missing Values by Column",
        xaxis_title="Column",
        yaxis_title="Missing Count",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
    )
    return fig


def create_dtype_chart(df: pd.DataFrame):
    """Pie chart of column data types."""
    dtypes = df.dtypes.astype(str).value_counts()
    fig = go.Figure(go.Pie(
        labels=dtypes.index.tolist(),
        values=dtypes.values.tolist(),
        hole=0.5,
        marker_colors=COLOR_PALETTE[:len(dtypes)],
        textinfo='label+percent',
        textfont_size=12,
    ))
    fig.update_layout(
        template=CHART_TEMPLATE,
        title="Data Types",
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
        showlegend=False,
    )
    return fig


def create_distributions(df: pd.DataFrame, columns: list):
    """Histogram distributions for numeric columns."""
    n = len(columns)
    cols = min(n, 3)
    rows = (n + cols - 1) // cols
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=columns)

    for i, col in enumerate(columns):
        r = i // cols + 1
        c = i % cols + 1
        fig.add_trace(
            go.Histogram(
                x=df[col].dropna(),
                marker_color=COLOR_PALETTE[i % len(COLOR_PALETTE)],
                opacity=0.8,
                name=col,
                showlegend=False,
            ),
            row=r, col=c
        )

    fig.update_layout(
        template=CHART_TEMPLATE,
        height=300 * rows,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
    )
    return fig


def create_correlation_heatmap(df: pd.DataFrame):
    """Correlation heatmap for numeric columns."""
    num_df = df.select_dtypes(include=[np.number])
    if len(num_df.columns) < 2:
        return None

    corr = num_df.corr()
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale=[[0, '#7C3AED'], [0.5, '#0E1117'], [1, '#06B6D4']],
        text=np.round(corr.values, 2),
        texttemplate='%{text}',
        textfont={"size": 11},
    ))
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
    )
    return fig


def create_categorical_chart(df: pd.DataFrame, col: str):
    """Bar chart for categorical column."""
    counts = df[col].value_counts().head(15)
    fig = go.Figure(go.Bar(
        x=counts.values.tolist(),
        y=counts.index.tolist(),
        orientation='h',
        marker_color=COLOR_PALETTE[0],
        marker_line_width=0,
    ))
    fig.update_layout(
        template=CHART_TEMPLATE,
        title=f"Top values in '{col}'",
        height=max(300, len(counts) * 30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def create_custom_chart(df: pd.DataFrame, x_col: str, y_col: str = None, chart_type: str = "bar"):
    """Create a custom chart from user-selected columns."""
    if chart_type == "bar":
        if y_col:
            fig = px.bar(df, x=x_col, y=y_col, color_discrete_sequence=COLOR_PALETTE)
        else:
            counts = df[x_col].value_counts().head(20)
            fig = px.bar(x=counts.index, y=counts.values, color_discrete_sequence=COLOR_PALETTE)
    elif chart_type == "scatter" and y_col:
        fig = px.scatter(df, x=x_col, y=y_col, color_discrete_sequence=COLOR_PALETTE)
    elif chart_type == "line" and y_col:
        fig = px.line(df, x=x_col, y=y_col, color_discrete_sequence=COLOR_PALETTE)
    elif chart_type == "box":
        fig = px.box(df, y=x_col if not y_col else y_col, x=x_col if y_col else None,
                     color_discrete_sequence=COLOR_PALETTE)
    elif chart_type == "histogram":
        fig = px.histogram(df, x=x_col, color_discrete_sequence=COLOR_PALETTE)
    else:
        fig = px.bar(df[x_col].value_counts().head(20), color_discrete_sequence=COLOR_PALETTE)

    fig.update_layout(
        template=CHART_TEMPLATE,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E2E8F0'),
        height=450,
    )
    return fig
