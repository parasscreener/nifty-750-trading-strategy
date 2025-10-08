import pandas as pd
import numpy as np
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def calculate_simple_returns(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate simple buy-and-hold returns"""
    try:
        if df.empty or len(df) < 2:
            return {}

        start_price = df['Close'].iloc[0]
        end_price = df['Close'].iloc[-1]
        total_return = (end_price - start_price) / start_price * 100

        years = len(df) / 252
        annualized_return = (1 + total_return/100) ** (1/years) - 1 if years > 0 else 0

        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100

        peak = df['Close'].expanding().max()
        drawdown = (df['Close'] - peak) / peak
        max_drawdown = drawdown.min() * 100

        sharpe_ratio = annualized_return / (volatility/100) if volatility > 0 else 0

        return {
            'Return [%]': round(total_return, 2),
            'Sharpe Ratio': round(sharpe_ratio, 2),
            'Max. Drawdown [%]': round(abs(max_drawdown), 2),
            'Period (Years)': round(years, 1)
        }

    except Exception as e:
        logger.error(f"Error calculating returns: {e}")
        return {}

def run_comprehensive_backtest(df: pd.DataFrame, symbol: str = "Unknown") -> Dict[str, Any]:
    """Run simplified backtest analysis"""
    logger.info(f"Running backtest for {symbol}...")

    benchmark = calculate_simple_returns(df)

    results = {
        'symbol': symbol,
        'benchmark': benchmark,
        'strategies': {"Buy_Hold": benchmark} if benchmark else {},
        'generated_at': datetime.now().isoformat()
    }

    return results
