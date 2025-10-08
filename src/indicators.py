import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def add_common_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add common technical indicators to OHLCV data"""
    try:
        data = df.copy()

        # Ensure we have the required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
            logger.error(f"Missing required columns. Available: {data.columns.tolist()}")
            return data

        # Simple Moving Averages
        data['sma_20'] = data['Close'].rolling(window=20).mean()
        data['sma_50'] = data['Close'].rolling(window=50).mean()
        data['sma_200'] = data['Close'].rolling(window=200).mean()

        # Exponential Moving Averages
        data['ema_20'] = data['Close'].ewm(span=20).mean()
        data['ema_50'] = data['Close'].ewm(span=50).mean()
        data['ema_200'] = data['Close'].ewm(span=200).mean()

        # RSI (simple implementation)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))

        # Volume indicators
        data['volume_sma20'] = data['Volume'].rolling(window=20).mean()
        data['volume_ratio'] = data['Volume'] / data['volume_sma20']

        # Price position relative to moving averages
        data['price_above_sma20'] = (data['Close'] > data['sma_20']).astype(int)
        data['price_above_sma50'] = (data['Close'] > data['sma_50']).astype(int)

        # Volatility (simple)
        data['volatility'] = data['Close'].pct_change().rolling(window=20).std()

        logger.debug(f"Added indicators to data")
        return data

    except Exception as e:
        logger.error(f"Error adding indicators: {e}")
        return df

def detect_pattern_conditions(df: pd.DataFrame) -> pd.DataFrame:
    """Add pattern detection helper conditions"""
    try:
        data = df.copy()

        # Golden Cross and Death Cross
        if 'ema_50' in data.columns and 'ema_200' in data.columns:
            data['golden_cross'] = ((data['ema_50'] > data['ema_200']) & 
                                   (data['ema_50'].shift(1) <= data['ema_200'].shift(1)))
            data['death_cross'] = ((data['ema_50'] < data['ema_200']) & 
                                  (data['ema_50'].shift(1) >= data['ema_200'].shift(1)))

        # Volume surge
        if 'volume_ratio' in data.columns:
            data['volume_surge'] = data['volume_ratio'] > 2.0
            data['volume_dry'] = data['volume_ratio'] < 0.5

        # RSI conditions
        if 'rsi' in data.columns:
            data['rsi_oversold'] = data['rsi'] < 30
            data['rsi_overbought'] = data['rsi'] > 70

        # Price action patterns
        data['higher_high'] = data['High'] > data['High'].shift(1)
        data['higher_low'] = data['Low'] > data['Low'].shift(1)

        return data

    except Exception as e:
        logger.error(f"Error detecting pattern conditions: {e}")
        return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test with sample data
    import yfinance as yf
    test_data = yf.download('RELIANCE.NS', period='1y', progress=False)

    if not test_data.empty:
        enhanced_data = add_common_indicators(test_data)
        pattern_data = detect_pattern_conditions(enhanced_data)
        print(f"✅ Indicators test successful - added {len(enhanced_data.columns) - len(test_data.columns)} columns")
    else:
        print("❌ No test data available")
