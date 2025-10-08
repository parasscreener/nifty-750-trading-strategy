import pandas as pd
import numpy as np
from typing import List
from datetime import datetime
import logging
from .base import Signal, PatternStrategy

logger = logging.getLogger(__name__)

class GoldenCrossStrategy(PatternStrategy):
    """Golden Cross (EMA 50 crossing above EMA 200)"""

    def __init__(self):
        super().__init__("Golden_Cross", lookback_period=5)

    def scan(self, df: pd.DataFrame, symbol: str) -> List[Signal]:
        signals = []

        # Check if we have required columns
        if 'Close' not in df.columns or len(df) < 200:
            return signals

        try:
            # Calculate EMAs if not present
            if 'ema_50' not in df.columns:
                df['ema_50'] = df['Close'].ewm(span=50).mean()
            if 'ema_200' not in df.columns:
                df['ema_200'] = df['Close'].ewm(span=200).mean()

            for i in range(200, len(df)):  # Need 200 periods for EMA200
                # Check for golden cross
                if (df['ema_50'].iloc[i] > df['ema_200'].iloc[i] and 
                    df['ema_50'].iloc[i-1] <= df['ema_200'].iloc[i-1]):

                    current_price = df['Close'].iloc[i]
                    stop_loss = df['ema_50'].iloc[i] * 0.95  # 5% below 50 EMA

                    # Target based on recent range
                    target = current_price * 1.15  # 15% target

                    confidence = self.calculate_volume_confidence(df, i)

                    # Higher confidence if above 200 EMA
                    if current_price > df['ema_200'].iloc[i]:
                        confidence += 0.2

                    signal = Signal(
                        date=df.index[i],
                        symbol=symbol,
                        setup='Golden_Cross',
                        side='BUY',
                        entry=current_price,
                        stop=stop_loss,
                        target=target,
                        confidence=min(confidence, 1.0)
                    )

                    if self.validate_signal(signal):
                        signals.append(signal)

        except Exception as e:
            logger.error(f"Error in Golden Cross scan for {symbol}: {e}")

        return signals

class SimpleBreakoutStrategy(PatternStrategy):
    """Simple breakout above recent highs"""

    def __init__(self):
        super().__init__("Simple_Breakout", lookback_period=20)

    def scan(self, df: pd.DataFrame, symbol: str) -> List[Signal]:
        signals = []

        if len(df) < self.lookback_period * 2:
            return signals

        try:
            for i in range(self.lookback_period, len(df)):
                # Find recent high
                recent_high = df['High'].iloc[i-self.lookback_period:i].max()
                current_price = df['Close'].iloc[i]

                # Check for breakout
                if current_price > recent_high * 1.01:  # 1% above recent high
                    stop_loss = df['Low'].iloc[i-10:i].min() * 0.98
                    target = current_price + (current_price - stop_loss) * 2  # 1:2 R/R

                    confidence = self.calculate_volume_confidence(df, i)

                    signal = Signal(
                        date=df.index[i],
                        symbol=symbol,
                        setup='Simple_Breakout',
                        side='BUY',
                        entry=current_price,
                        stop=stop_loss,
                        target=target,
                        confidence=confidence
                    )

                    if self.validate_signal(signal):
                        signals.append(signal)

        except Exception as e:
            logger.error(f"Error in Simple Breakout scan for {symbol}: {e}")

        return signals

# Export strategy classes
ALL_STRATEGIES = [
    GoldenCrossStrategy,
    SimpleBreakoutStrategy
]
