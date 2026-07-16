import pandas as pd
from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier

def optimize_portfolio(prices, top_tickers, market_prices, risk_free_rate=0.065):
    """
    Given price history and a list of selected tickers, calculates the optimal 
    weights for the Max Sharpe portfolio using Mean-Variance Optimization.
    """
    # Filter prices to only the selected tickers
    subset_prices = prices[top_tickers]
    
    # Align dates between subset_prices and market_prices
    subset_prices, market_prices = subset_prices.align(market_prices, join='inner', axis=0)
    
    # 1. Expected Returns (CAPM Return)
    mu = expected_returns.capm_return(subset_prices, market_prices=market_prices, risk_free_rate=risk_free_rate)
    
    # 2. Covariance Matrix (Ledoit-Wolf Shrinkage)
    S = risk_models.CovarianceShrinkage(subset_prices).ledoit_wolf()
    
    # 3. Efficient Frontier & Max Sharpe
    # Set weight bounds to prevent massive concentration (max 20% per stock)
    ef = EfficientFrontier(mu, S, weight_bounds=(0, 0.20))
    
    # Optimize for Max Sharpe using the Indian risk-free rate
    raw_weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
    
    # Clean up the weights (removes near-zero weights)
    cleaned_weights = ef.clean_weights()
    
    # Get performance metrics
    expected_return, volatility, sharpe = ef.portfolio_performance(risk_free_rate=risk_free_rate)
    
    return cleaned_weights, expected_return, volatility, sharpe

if __name__ == "__main__":
    from data_loader import load_prices, load_fundamentals, load_market_prices, NIFTY_50
    from screener import screen_stocks
    
    print("Testing Optimizer...")
    test_tickers = NIFTY_50[:15]
    prices = load_prices(test_tickers)
    fundamentals = load_fundamentals(test_tickers)
    market_prices = load_market_prices("^NSEI")
    
    top_tickers, _ = screen_stocks(prices, fundamentals, top_n=8)
    
    weights, exp_ret, vol, sharpe = optimize_portfolio(prices, top_tickers, market_prices)
    
    print("\nOptimal Weights:")
    for ticker, weight in weights.items():
        if weight > 0:
            print(f"{ticker}: {weight:.2%}")
            
    print(f"\nExpected Annual Return: {exp_ret:.2%}")
    print(f"Annual Volatility: {vol:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
