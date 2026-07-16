import pandas as pd
import numpy as np


def run_backtest(prices, weights, market_prices, risk_free_rate=0.065, lookback_years=3):
    """
    Simulates how the optimized portfolio would have performed historically
    compared to the Nifty 50 benchmark.

    Args:
        prices: DataFrame of daily close prices for all tickers
        weights: dict of {ticker: weight} from the optimizer
        market_prices: Series of Nifty 50 index prices
        risk_free_rate: annual risk-free rate for Sharpe calculation
        lookback_years: how many years of history to backtest

    Returns:
        dict with backtest results including cumulative returns DataFrames and metrics
    """
    # Filter to tickers with non-zero weights
    active_tickers = [t for t, w in weights.items() if w > 0.001]
    active_weights = np.array([weights[t] for t in active_tickers])

    # Get subset of prices for active tickers
    portfolio_prices = prices[active_tickers].copy()

    # Align portfolio prices with market prices
    common_index = portfolio_prices.index.intersection(market_prices.index)
    portfolio_prices = portfolio_prices.loc[common_index]
    market = market_prices.loc[common_index]

    # Trim to lookback period
    cutoff_date = portfolio_prices.index[-1] - pd.DateOffset(years=lookback_years)
    portfolio_prices = portfolio_prices[portfolio_prices.index >= cutoff_date]
    market = market[market.index >= cutoff_date]

    # Calculate daily returns
    portfolio_daily_returns = portfolio_prices.pct_change().dropna()
    market_daily_returns = market.pct_change().dropna()

    # Align after pct_change
    common_idx = portfolio_daily_returns.index.intersection(market_daily_returns.index)
    portfolio_daily_returns = portfolio_daily_returns.loc[common_idx]
    market_daily_returns = market_daily_returns.loc[common_idx]

    # Weighted portfolio daily return
    weighted_returns = portfolio_daily_returns.values @ active_weights

    # Build cumulative return series (starting at 1.0 = 100%)
    portfolio_cumulative = pd.Series(
        (1 + weighted_returns).cumprod(),
        index=portfolio_daily_returns.index,
        name="Portfolio"
    )
    market_cumulative = pd.Series(
        (1 + market_daily_returns.values).cumprod(),
        index=market_daily_returns.index,
        name="Nifty 50"
    )

    # ── Portfolio Metrics ──
    trading_days = len(weighted_returns)
    years = trading_days / 252

    total_return = portfolio_cumulative.iloc[-1] - 1
    cagr = (portfolio_cumulative.iloc[-1]) ** (1 / years) - 1 if years > 0 else 0

    annual_vol = np.std(weighted_returns) * np.sqrt(252)
    sharpe = (cagr - risk_free_rate) / annual_vol if annual_vol > 0 else 0

    # Max drawdown
    running_max = portfolio_cumulative.cummax()
    drawdown = (portfolio_cumulative - running_max) / running_max
    max_drawdown = drawdown.min()

    # ── Benchmark Metrics ──
    bench_total_return = market_cumulative.iloc[-1] - 1
    bench_cagr = (market_cumulative.iloc[-1]) ** (1 / years) - 1 if years > 0 else 0
    bench_vol = np.std(market_daily_returns.values) * np.sqrt(252)

    bench_running_max = market_cumulative.cummax()
    bench_drawdown = (market_cumulative - bench_running_max) / bench_running_max
    bench_max_drawdown = bench_drawdown.min()

    # ── Build results ──
    cumulative_df = pd.DataFrame({
        "Portfolio": portfolio_cumulative,
        "Nifty 50": market_cumulative
    })

    return {
        "cumulative": cumulative_df,
        "drawdown": drawdown,
        "bench_drawdown": bench_drawdown,
        "metrics": {
            "total_return": total_return,
            "cagr": cagr,
            "annual_vol": annual_vol,
            "sharpe": sharpe,
            "max_drawdown": max_drawdown,
        },
        "bench_metrics": {
            "total_return": bench_total_return,
            "cagr": bench_cagr,
            "annual_vol": bench_vol,
            "max_drawdown": bench_max_drawdown,
        },
        "years": years,
        "trading_days": trading_days,
    }
