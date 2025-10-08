import pandas as pd
import yfinance as yf
from typing import Dict, List
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def fetch_ohlcv(ticker: str, years: int = 3, validate_data: bool = True) -> pd.DataFrame:
    """Fetch OHLCV data from Yahoo Finance"""
    try:
        logger.debug(f"Fetching data for {ticker}...")

        # Download data
        df = yf.download(
            ticker, 
            period=f"{years}y",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        # Handle multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        # Ensure we have the required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            logger.warning(f"Missing required columns for {ticker}")
            return pd.DataFrame()

        # Clean data
        df = df.dropna()

        # Basic validation
        if validate_data and not df.empty:
            # Remove rows with zero or negative prices
            df = df[df['Close'] > 0]
            df = df[df['High'] >= df['Low']]
            df = df[df['High'] >= df['Close']]
            df = df[df['Low'] <= df['Close']]

        if len(df) < 100:  # Need reasonable amount of data
            logger.warning(f"Insufficient data for {ticker}: {len(df)} rows")
            return pd.DataFrame()

        logger.debug(f"Successfully fetched {len(df)} rows for {ticker}")
        return df

    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def fetch_multiple_stocks(tickers: List[str], years: int = 3, max_workers: int = 5) -> Dict[str, pd.DataFrame]:
    """Fetch data for multiple stocks with parallel processing"""
    results = {}

    def fetch_single(ticker):
        return ticker, fetch_ohlcv(ticker, years)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {executor.submit(fetch_single, ticker): ticker for ticker in tickers}

        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                symbol, data = future.result(timeout=60)
                if not data.empty:
                    results[symbol] = data
                    logger.info(f"✅ {symbol}: {len(data)} rows")
                else:
                    logger.warning(f"❌ {symbol}: No data")
            except Exception as e:
                logger.error(f"❌ {symbol}: {e}")

    logger.info(f"Successfully fetched data for {len(results)}/{len(tickers)} stocks")
    return results

def validate_stock_data(df: pd.DataFrame, min_days: int = 100) -> bool:
    """Validate if stock data is sufficient for analysis"""
    if df.empty:
        return False

    # Check minimum trading days
    if len(df) < min_days:
        return False

    # Check for recent data (within last 60 days)
    if (datetime.now() - df.index[-1]).days > 60:
        return False

    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test data fetching
    test_data = fetch_ohlcv('RELIANCE.NS', years=2)
    print(f"Test data: {len(test_data)} rows" if not test_data.empty else "No data")
