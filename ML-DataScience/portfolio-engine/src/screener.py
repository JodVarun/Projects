import pandas as pd
import numpy as np

def screen_stocks(prices, fundamentals, w_value=1.0, w_quality=1.0, w_momentum=1.0, top_n=10):
    """
    Ranks stocks based on Value (P/E), Quality (ROE), and Momentum (6mo return).
    """
    # Ensure we only use tickers present in both prices and fundamentals
    valid_tickers = prices.columns.intersection(fundamentals.index)
    prices = prices[valid_tickers]
    df = fundamentals.loc[valid_tickers].copy()

    # 1. Calculate Momentum (6-month return)
    # Approx 126 trading days in 6 months
    if len(prices) > 126:
        price_today = prices.iloc[-1]
        price_6mo_ago = prices.iloc[-126]
        momentum = (price_today / price_6mo_ago) - 1
    elif len(prices) > 1:
        # Fallback if not enough data
        momentum = (prices.iloc[-1] / prices.iloc[0]) - 1
    else:
        # If no prices available
        momentum = pd.Series(0, index=valid_tickers)

    # 2. Merge fundamentals with momentum
    df['Momentum'] = momentum

    # Clean data (drop rows where all factors are NaN, but keep partials)
    # Actually, we can fill NaN with the median of the column or drop them.
    # The PDF suggests expecting 70-85% usable. We will fill NaNs with median 
    # to avoid throwing away stocks entirely just because one field is missing,
    # or we can drop stocks that have no P/E or ROE. Let's drop completely missing.
    
    # 3. Rank factors
    # Value: lower P/E is better. We rank ascending=False so lower P/E gets higher score (closer to 1.0)
    # Note: Negative P/E (earnings loss) is usually bad, but a simple rank will put them highest.
    # To be safe, we can set negative P/E to NaN or large positive before ranking.
    pe_cleaned = df['P/E'].copy()
    pe_cleaned[pe_cleaned < 0] = np.nan
    
    value_rank = pe_cleaned.rank(pct=True, ascending=False, na_option='bottom')
    quality_rank = df['ROE'].rank(pct=True, ascending=True, na_option='bottom')
    momentum_rank = df['Momentum'].rank(pct=True, ascending=True, na_option='bottom')
    
    # Normalize weights so they sum to 1 (optional, but good practice)
    total_weight = w_value + w_quality + w_momentum
    if total_weight == 0:
        total_weight = 1 # Prevent division by zero
        
    w_v = w_value / total_weight
    w_q = w_quality / total_weight
    w_m = w_momentum / total_weight

    # 4. Blended Score
    df['Value_Rank'] = value_rank
    df['Quality_Rank'] = quality_rank
    df['Momentum_Rank'] = momentum_rank
    
    df['Score'] = (w_v * value_rank) + (w_q * quality_rank) + (w_m * momentum_rank)
    
    # Sort descending
    df_sorted = df.sort_values(by='Score', ascending=False)
    
    # Return top N tickers and the sorted dataframe
    top_tickers = df_sorted.head(top_n).index.tolist()
    return top_tickers, df_sorted

if __name__ == "__main__":
    from data_loader import load_prices, load_fundamentals, NIFTY_50
    print("Testing Screener...")
    test_tickers = NIFTY_50[:20]
    prices = load_prices(test_tickers)
    fundamentals = load_fundamentals(test_tickers)
    
    top_tickers, df_ranked = screen_stocks(prices, fundamentals)
    print("\nTop Tickers:")
    print(top_tickers)
    print("\nRanked DataFrame:")
    print(df_ranked[['P/E', 'ROE', 'Momentum', 'Score']].head(10))
