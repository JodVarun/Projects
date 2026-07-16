import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# Nifty 50 constituents (some common ones, we can use a subset for fast iteration)
NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HUL.NS", "SBI.NS", "ITC.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "BAJFINANCE.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "TITAN.NS", "BAJAJFINSV.NS", "SUNPHARMA.NS", "TATASTEEL.NS", "M&M.NS",
    "ULTRACEMCO.NS", "TATAMOTORS.NS", "NTPC.NS", "NESTLEIND.NS", "POWERGRID.NS",
    "WIPRO.NS", "HCLTECH.NS", "ONGC.NS", "JSWSTEEL.NS", "TECHM.NS",
    "GRASIM.NS", "INDUSINDBK.NS", "ADANIENT.NS", "ADANIPORTS.NS", "HINDALCO.NS",
    "DIVISLAB.NS", "SBILIFE.NS", "CIPLA.NS", "APOLLOHOSP.NS", "BAJAJ-AUTO.NS",
    "TATASTLLP.NS", "EICHERMOT.NS", "UPL.NS", "BRITANNIA.NS", "DRREDDY.NS",
    "HEROMOTOCO.NS", "COALINDIA.NS", "BPCL.NS", "HDFCLIFE.NS", "TATACONSUM.NS"
]

@st.cache_data(show_spinner="Downloading Historical Prices...")
def load_prices(tickers, start="2015-01-01"):
    """
    Fetch historical adjusted close prices for a list of tickers.
    Batched into a single call to avoid rate limits.
    """
    data = yf.download(tickers, start=start, progress=False)
    
    # If a single ticker is passed, yf returns a Series or simple DataFrame
    if isinstance(data.columns, pd.MultiIndex):
        # Prefer 'Close' to avoid missing 'Adj Close' for successful tickers
        prices = data['Close']
    else:
        prices = data

    # Drop any timezone info to keep the index simple
    if prices.index.tz is not None:
        prices.index = prices.index.tz_localize(None)

    # Handle missing data
    # 1. Forward fill to carry over prices for random missing days
    prices = prices.ffill()
    
    # 2. Drop tickers that have absolutely no data
    prices = prices.dropna(axis=1, how='all')
    
    # 3. Trim dataset to start after the youngest company's IPO (drop rows with any NaN)
    prices = prices.dropna(axis=0, how='any')

    return prices

@st.cache_data(show_spinner="Downloading Market Index...")
def load_market_prices(market_ticker="^NSEI", start="2015-01-01"):
    """Fetch market index prices for CAPM benchmark."""
    data = yf.download(market_ticker, start=start, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        market_prices = data['Close']
    else:
        market_prices = data['Close'] if 'Close' in data.columns else data.iloc[:, 0]
        
    if market_prices.index.tz is not None:
        market_prices.index = market_prices.index.tz_localize(None)
    
    # yf might return a DataFrame if multiple columns, ensure we return a Series
    if isinstance(market_prices, pd.DataFrame):
        market_prices = market_prices.iloc[:, 0]
        
    return market_prices.ffill().dropna()

@st.cache_data(show_spinner="Fetching Fundamentals (this takes a moment)...")
def load_fundamentals(tickers):
    """
    Loop through tickers to get P/E, ROE, and Debt-to-Equity.
    Gracefully handles missing data by returning NaN.
    """
    data = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            pe = info.get('trailingPE', np.nan)
            roe = info.get('returnOnEquity', np.nan)
            de = info.get('debtToEquity', np.nan)
            
            data.append({
                'Ticker': ticker,
                'P/E': pe,
                'ROE': roe,
                'D/E': de
            })
        except Exception as e:
            print(f"Failed to fetch fundamentals for {ticker}: {e}")
            data.append({
                'Ticker': ticker,
                'P/E': np.nan,
                'ROE': np.nan,
                'D/E': np.nan
            })
            
    df = pd.DataFrame(data).set_index('Ticker')
    return df

if __name__ == "__main__":
    # Test block for standalone execution
    print("Testing data loader with Nifty 50 subset...")
    test_tickers = NIFTY_50[:10]
    prices = load_prices(test_tickers)
    print("\nPrices:")
    print(prices.head())
    
    fundamentals = load_fundamentals(test_tickers)
    print("\nFundamentals:")
    print(fundamentals)
