from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class Signal:
    """Trading signal data class"""
    date: datetime
    symbol: str
    setup: str
    side: str  # 'BUY' or 'SELL'
    entry: float
    stop: float
    target: float
    confidence: float  # 0.0 to 1.0
    volume_ratio: Optional[float] = None
    atr: Optional[float] = None
    risk_reward: Optional[float] = None

    def __post_init__(self):
        """Calculate risk/reward ratio"""
        if self.risk_reward is None:
            if self.side == 'BUY':
                risk = abs(self.entry - self.stop)
                reward = abs(self.target - self.entry)
            else:  # SELL
                risk = abs(self.stop - self.entry)
                reward = abs(self.entry - self.target)

            self.risk_reward = reward / risk if risk > 0 else 0

    def to_dict(self) -> dict:
        """Convert to dictionary for export"""
        return {
            'date': self.date.strftime('%Y-%m-%d') if isinstance(self.date, datetime) else str(self.date),
            'symbol': self.symbol,
            'setup': self.setup,
            'side': self.side,
            'entry': round(self.entry, 2),
            'stop': round(self.stop, 2),
            'target': round(self.target, 2),
            'confidence': round(self.confidence, 3),
            'volume_ratio': round(self.volume_ratio, 2) if self.volume_ratio else None,
            'atr': round(self.atr, 2) if self.atr else None,
            'risk_reward': round(self.risk_reward, 2)
        }

class BaseStrategy:
    """Base class for all trading strategies"""

    def __init__(self, name: str):
        self.name = name
        self.min_risk_reward = 2.0  # Timothy Knight's minimum 1:2 ratio
        self.max_risk_percent = 0.02  # 2% risk per trade

    def scan(self, df: pd.DataFrame, symbol: str) -> List[Signal]:
        """Scan for trading opportunities"""
        raise NotImplementedError("Subclasses must implement scan method")

    def validate_signal(self, signal: Signal) -> bool:
        """Validate signal meets Timothy Knight's criteria"""
        # Check risk/reward ratio
        if signal.risk_reward < self.min_risk_reward:
            logger.debug(f"Signal rejected: R/R {signal.risk_reward:.2f} < {self.min_risk_reward}")
            return False

        # Check for reasonable price levels
        if signal.side == 'BUY':
            if signal.target <= signal.entry or signal.stop >= signal.entry:
                logger.debug("Signal rejected: Invalid BUY levels")
                return False
        else:  # SELL
            if signal.target >= signal.entry or signal.stop <= signal.entry:
                logger.debug("Signal rejected: Invalid SELL levels")
                return False

        # Check confidence threshold
        if signal.confidence < 0.3:
            logger.debug(f"Signal rejected: Low confidence {signal.confidence:.2f}")
            return False

        return True

    def calculate_volume_confidence(self, df: pd.DataFrame, index: int) -> float:
        """Calculate confidence based on volume analysis"""
        try:
            if index < 20 or 'Volume' not in df.columns:
                return 0.5  # Neutral confidence

            current_volume = df['Volume'].iloc[index]
            avg_volume = df['Volume'].iloc[index-20:index].mean()

            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

            # Higher volume = higher confidence
            if volume_ratio >= 2.0:
                confidence = 0.9
            elif volume_ratio >= 1.5:
                confidence = 0.8
            elif volume_ratio >= 1.2:
                confidence = 0.7
            elif volume_ratio >= 0.8:
                confidence = 0.6
            else:
                confidence = 0.4  # Low volume

            return min(confidence, 1.0)

        except Exception as e:
            logger.debug(f"Error calculating volume confidence: {e}")
            return 0.5

class PatternStrategy(BaseStrategy):
    """Base class for chart pattern strategies"""

    def __init__(self, name: str, lookback_period: int = 20):
        super().__init__(name)
        self.lookback_period = lookback_period
