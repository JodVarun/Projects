import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
from src.data_loader import load_prices, load_fundamentals, load_market_prices, NIFTY_50
from src.screener import screen_stocks
from src.optimizer import optimize_portfolio

# ── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quant Portfolio Engine | Nifty 50",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='12' fill='%23111827'/><text y='68' x='16' font-size='56' fill='%2310B981'>Q</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp {
        background-color: #0a0f1a;
    }

    /* Header */
    .engine-header {
        padding: 2rem 0 1.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 2rem;
    }
    .engine-header h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f0f2f5;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .engine-header p {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0.5rem 0 0 0;
        line-height: 1.6;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #111827 0%, #1a2332 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .metric-label {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f0f2f5;
    }
    .metric-value.positive { color: #10b981; }
    .metric-value.neutral { color: #f59e0b; }

    /* Section Headers */
    .section-header {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #4b5563;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        margin: 2rem 0 1rem 0;
    }

    /* Data Status */
    .data-status {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 1rem 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .status-dot.success { background: #10b981; box-shadow: 0 0 6px #10b98166; }
    .status-dot.cached  { background: #3b82f6; box-shadow: 0 0 6px #3b82f666; }
    .status-dot.warning { background: #f59e0b; box-shadow: 0 0 6px #f59e0b66; }
    .status-text {
        font-size: 0.8rem;
        color: #9ca3af;
    }
    .status-text strong { color: #d1d5db; font-weight: 600; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid rgba(255,255,255,0.04);
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #6b7280;
    }

    /* Preset buttons */
    .preset-btn {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 0.6rem 0.75rem;
        cursor: pointer;
        text-align: center;
        transition: border-color 0.2s;
    }
    .preset-btn:hover {
        border-color: #10b981;
    }
    .preset-btn-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #d1d5db;
    }
    .preset-btn-desc {
        font-size: 0.65rem;
        color: #6b7280;
        margin-top: 2px;
    }

    /* Explanation box */
    .explain-box {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.06);
        border-left: 3px solid #10b981;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
    }
    .explain-box p {
        font-size: 0.8rem;
        color: #9ca3af;
        line-height: 1.65;
        margin: 0;
    }
    .explain-box strong { color: #d1d5db; }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Expander */
    .streamlit-expanderHeader {
        font-size: 0.85rem;
        font-weight: 500;
        color: #9ca3af;
    }

    /* Table */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="engine-header">
    <h1>Multi-Factor Quantitative Portfolio Engine</h1>
</div>
""", unsafe_allow_html=True)


# ── Sidebar Controls ────────────────────────────────────────────────────────

# Preset strategy profiles
st.sidebar.markdown("## Strategy Profile")
preset = st.sidebar.selectbox(
    "Choose a strategy",
    ["Balanced", "Bargain Hunter", "Quality First", "Trend Rider", "Custom"],
    index=0,
    help="Balanced — Weighs all factors equally.\n\nBargain Hunter — Prioritises underpriced stocks.\n\nQuality First — Prioritises highly profitable companies.\n\nTrend Rider — Prioritises stocks that have been rising recently.\n\nCustom — Set your own weights below."
)

PRESETS = {
    "Balanced":       (1.0, 1.0, 1.0),
    "Bargain Hunter": (1.0, 0.3, 0.2),
    "Quality First":  (0.3, 1.0, 0.3),
    "Trend Rider":    (0.2, 0.3, 1.0),
    "Custom":         (1.0, 1.0, 1.0),
}
default_v, default_q, default_m = PRESETS[preset]

st.sidebar.markdown("---")
st.sidebar.markdown("## What to prioritise")
w_value = st.sidebar.slider(
    "Cheapness",
    0.0, 1.0, default_v, 0.1,
    help="How much do you care about buying cheap stocks? Higher means the engine favours companies whose stock price is low relative to their earnings (low P/E ratio).",
    disabled=(preset != "Custom")
)
w_quality = st.sidebar.slider(
    "Profitability",
    0.0, 1.0, default_q, 0.1,
    help="How much do you care about well-run companies? Higher means the engine favours companies that generate more profit from their assets (high Return on Equity).",
    disabled=(preset != "Custom")
)
w_momentum = st.sidebar.slider(
    "Recent trend",
    0.0, 1.0, default_m, 0.1,
    help="How much do you care about stocks that have been rising recently? Higher means the engine favours stocks whose price has gone up over the last 6 months.",
    disabled=(preset != "Custom")
)

st.sidebar.markdown("---")
st.sidebar.markdown("## Portfolio size")
top_n = st.sidebar.slider(
    "Number of stocks to hold",
    5, 20, 10, 1,
    help="How many stocks do you want in your final portfolio? Fewer stocks = more concentrated bets. More stocks = more diversified."
)
risk_free_rate = st.sidebar.number_input(
    "Risk-free rate",
    value=0.065,
    format="%.3f",
    help="The return you would get from a zero-risk investment like an Indian Government Bond (currently around 6.5%). The engine uses this as a baseline to judge whether stocks are worth the extra risk."
)

st.sidebar.markdown("---")
run_button = st.sidebar.button("Execute Optimization", type="primary", use_container_width=True)


# ── Main Pipeline ────────────────────────────────────────────────────────────
if run_button:

    # ── Phase 1: Data Acquisition ────────────────────────────────────────
    st.markdown('<div class="section-header">Phase 1 — Data Acquisition</div>', unsafe_allow_html=True)

    t0 = time.time()
    prices = load_prices(NIFTY_50)
    t_prices = time.time() - t0

    t0 = time.time()
    market_prices = load_market_prices("^NSEI")
    t_market = time.time() - t0

    t0 = time.time()
    fundamentals = load_fundamentals(NIFTY_50)
    t_fund = time.time() - t0

    # Determine cache status
    prices_cached = t_prices < 0.5
    market_cached = t_market < 0.5
    fund_cached = t_fund < 0.5

    # Status indicators
    def render_status(label, detail, elapsed, cached):
        dot_class = "cached" if cached else "success"
        source = "cached" if cached else f"downloaded in {elapsed:.1f}s"
        return f"""
        <div class="data-status">
            <span class="status-dot {dot_class}"></span>
            <span class="status-text"><strong>{label}</strong> — {detail} ({source})</span>
        </div>
        """

    st.markdown(
        render_status("Price History", f"{prices.shape[1]} assets, {prices.shape[0]} trading days from 2015", t_prices, prices_cached) +
        render_status("Market Index", "Nifty 50 (^NSEI) benchmark for CAPM", t_market, market_cached) +
        render_status("Fundamentals", f"P/E, ROE, D/E for {len(fundamentals)} tickers", t_fund, fund_cached),
        unsafe_allow_html=True
    )

    with st.expander("Inspect raw data (for advanced users)"):
        st.dataframe(fundamentals, use_container_width=True)


    # ── Phase 2: Factor Screening ────────────────────────────────────────
    st.markdown('<div class="section-header">Phase 2 — Picking the Best Stocks</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="explain-box">
        <p>The engine just scored every stock on three dimensions — <strong>Cheapness</strong> (is the price fair?),
        <strong>Profitability</strong> (does the company make good money?), and <strong>Recent Trend</strong> (is the stock price going up?).
        It then blended those scores using your chosen weights and picked the top performers. These survivors move on to the optimizer.</p>
    </div>
    """, unsafe_allow_html=True)

    top_tickers, df_ranked = screen_stocks(prices, fundamentals, w_value, w_quality, w_momentum, top_n)

    display_df = df_ranked[['P/E', 'ROE', 'Momentum', 'Value_Rank', 'Quality_Rank', 'Momentum_Rank', 'Score']].head(top_n).copy()
    display_df['Momentum'] = display_df['Momentum'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "—")
    display_df['ROE'] = display_df['ROE'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "—")
    display_df['P/E'] = display_df['P/E'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
    display_df['Score'] = display_df['Score'].apply(lambda x: f"{x:.3f}")
    display_df['Value_Rank'] = display_df['Value_Rank'].apply(lambda x: f"{x:.0%}")
    display_df['Quality_Rank'] = display_df['Quality_Rank'].apply(lambda x: f"{x:.0%}")
    display_df['Momentum_Rank'] = display_df['Momentum_Rank'].apply(lambda x: f"{x:.0%}")

    st.dataframe(display_df, use_container_width=True)


    # ── Phase 3: Portfolio Optimization ──────────────────────────────────
    st.markdown('<div class="section-header">Phase 3 — How Much to Invest in Each Stock</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="explain-box">
        <p>Now the engine decides the exact percentage of your money to put into each stock.
        It looks at how these stocks move together — if two stocks always rise and fall at the same time, it reduces exposure to avoid
        putting all your eggs in one basket. The goal: <strong>maximise your expected profit per unit of risk taken</strong>. No single stock can exceed 20% of your portfolio.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        weights, exp_ret, vol, sharpe = optimize_portfolio(prices, top_tickers, market_prices, risk_free_rate=risk_free_rate)

        # ── Metric Cards ──
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Projected Yearly Gain</div>
                <div class="metric-value positive">{exp_ret:.2%}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Risk (Price Swings)</div>
                <div class="metric-value neutral">{vol:.2%}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            sharpe_desc = 'Below average' if sharpe < 0.5 else 'Good' if sharpe < 1.0 else 'Excellent' if sharpe < 2.0 else 'Outstanding'
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Reward-to-Risk Score</div>
                <div class="metric-value">{sharpe:.2f} <span style="font-size:0.7rem;color:#6b7280;font-weight:400">({sharpe_desc})</span></div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("What do these numbers mean?"):
            st.markdown("""
            - **Projected Yearly Gain** — If you invested today and held for a year, the model estimates your portfolio would grow by this percentage. This is a statistical estimate, not a guarantee.
            - **Risk (Price Swings)** — How much the portfolio value is expected to fluctuate up and down over a year. Lower is calmer. A value of 20% means your portfolio could swing roughly +/-20% in a typical year.
            - **Reward-to-Risk Score (Sharpe Ratio)** — How much return you get for every unit of risk. Higher is better. Below 0.5 is below average, 0.5-1.0 is good, above 1.0 is excellent. Think of it as the "efficiency" of your portfolio.
            """)

        # ── Weights Visualisation ──
        weight_df = pd.DataFrame.from_dict(weights, orient='index', columns=['Weight'])
        weight_df = weight_df[weight_df['Weight'] > 0.001].reset_index()
        weight_df.columns = ['Ticker', 'Weight']
        weight_df = weight_df.sort_values('Weight', ascending=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        col_chart, col_table = st.columns([3, 2])

        with col_chart:
            fig = go.Figure(go.Bar(
                x=weight_df['Weight'],
                y=weight_df['Ticker'],
                orientation='h',
                marker=dict(
                    color=weight_df['Weight'],
                    colorscale=[[0, '#1e3a5f'], [0.5, '#10b981'], [1, '#34d399']],
                    line=dict(width=0),
                    cornerradius=4,
                ),
                text=weight_df['Weight'].apply(lambda w: f"{w:.1%}"),
                textposition='outside',
                textfont=dict(size=12, color='#9ca3af', family='Inter'),
            ))
            fig.update_layout(
                title=dict(text="Optimal Portfolio Allocation", font=dict(size=14, color='#d1d5db', family='Inter')),
                xaxis=dict(
                    tickformat='.0%',
                    range=[0, max(weight_df['Weight']) * 1.3],
                    gridcolor='rgba(255,255,255,0.03)',
                    tickfont=dict(color='#6b7280', family='Inter'),
                ),
                yaxis=dict(
                    tickfont=dict(size=12, color='#d1d5db', family='Inter'),
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=max(350, len(weight_df) * 45),
                margin=dict(l=10, r=60, t=50, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            fig_donut = go.Figure(go.Pie(
                labels=weight_df['Ticker'],
                values=weight_df['Weight'],
                hole=0.55,
                marker=dict(
                    colors=px.colors.sequential.Tealgrn[:len(weight_df)],
                    line=dict(color='#0a0f1a', width=2),
                ),
                textinfo='percent',
                textfont=dict(size=11, color='#d1d5db', family='Inter'),
                hoverinfo='label+percent+value',
            ))
            fig_donut.update_layout(
                title=dict(text="Weight Distribution", font=dict(size=14, color='#d1d5db', family='Inter')),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                height=350,
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_donut, use_container_width=True)


    except Exception as e:
        st.error(f"Optimization could not converge. This typically occurs when selected stocks have negative CAPM expected returns or insufficient price history. Details: {e}")


# ── Empty State ──────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 50vh;
        color: #374151;
        text-align: center;
    ">
        <div style="font-size: 2.5rem; font-weight: 700; color: #1f2937; margin-bottom: 0.5rem;">Configure & Execute</div>
        <div style="font-size: 0.9rem; color: #4b5563; max-width: 480px; line-height: 1.7;">
            Adjust factor weights and optimization parameters in the sidebar, then press <strong style="color:#10b981;">Execute Optimization</strong> to generate the optimal Max Sharpe portfolio.
        </div>
    </div>
    """, unsafe_allow_html=True)
