import pandas as pd
import requests
from typing import List
import logging

logger = logging.getLogger(__name__)

# Fallback list of liquid Nifty stocks
FALLBACK_STOCKS = [
    'RELIANCE', 'HDFCBANK', 'BHARTIARTL', 'TCS', 'ICICIBANK', 
    'SBIN', 'BAJFINANCE', 'INFY', 'HINDUNILVR', 'LT',
    'MARUTI', 'ITC', 'KOTAKBANK', 'SUNPHARMA', 'HCLTECH',
    'AXISBANK', 'ULTRACEMCO', 'NTPC', 'BAJAJFINSV', 'ASIANPAINT',
    'NESTLEIND', 'WIPRO', 'TECHM', 'TITAN', 'POWERGRID',
    'ONGC', 'TATAMOTORS', 'DRREDDY', 'JSWSTEEL', 'GRASIM',
    'COALINDIA', 'BRITANNIA', 'DIVISLAB', 'EICHERMOT', 'SHRIRAMFIN',
    'TATASTEEL', 'APOLLOHOSP', 'PIDILITIND', 'BAJAJ-AUTO', 'HINDALCO',
    'CIPLA', 'BPCL', 'HEROMOTOCO', 'SBILIFE', 'INDUSINDBK'
]

def build_universe(cache_file="configs/universe_cache.csv", use_fallback=True) -> pd.DataFrame:
    """Build stock universe - simplified version that uses fallback stocks"""

    try:
        logger.info("Building stock universe using fallback list...")

        # Create universe DataFrame from fallback stocks
        universe = pd.DataFrame({
            'symbol': FALLBACK_STOCKS,
            'name': FALLBACK_STOCKS,  # Use symbol as name for simplicity
            'yahoo_symbol': [f"{symbol}.NS" for symbol in FALLBACK_STOCKS]
        })

        # Save to cache
        import os
        os.makedirs('configs', exist_ok=True)
        universe.to_csv(cache_file, index=False)

        logger.info(f"Successfully built universe with {len(universe)} stocks")
        return universe

    except Exception as e:
        logger.error(f"Error building universe: {e}")

        # Create minimal universe as last resort
        minimal_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
        universe = pd.DataFrame({
            'symbol': minimal_stocks,
            'name': minimal_stocks,
            'yahoo_symbol': [f"{symbol}.NS" for symbol in minimal_stocks]
        })

        return universe

def get_liquid_subset(universe: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    """Get most liquid subset for analysis"""
    return universe.head(limit)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    universe = build_universe()
    print(f"Universe built successfully: {len(universe)} stocks")
    print(universe.head())
