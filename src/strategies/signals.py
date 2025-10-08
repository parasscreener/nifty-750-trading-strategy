from typing import List, Dict
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import Signal
from .patterns import ALL_STRATEGIES

logger = logging.getLogger(__name__)

class StrategyScanner:
    """Main scanner that runs all trading strategies"""

    def __init__(self, max_workers: int = 3):
        self.strategies = [strategy() for strategy in ALL_STRATEGIES]
        self.max_workers = max_workers

        logger.info(f"Initialized scanner with {len(self.strategies)} strategies")
        for strategy in self.strategies:
            logger.info(f"  - {strategy.name}")

    def scan_single_stock(self, df: pd.DataFrame, symbol: str) -> List[Signal]:
        """Scan a single stock with all strategies"""
        all_signals = []

        # Clean symbol (remove .NS suffix if present)
        clean_symbol = symbol.replace('.NS', '').upper()

        for strategy in self.strategies:
            try:
                signals = strategy.scan(df, clean_symbol)
                all_signals.extend(signals)

                if signals:
                    logger.debug(f"{strategy.name} found {len(signals)} signals for {clean_symbol}")

            except Exception as e:
                logger.error(f"Error running {strategy.name} on {clean_symbol}: {e}")

        # Remove duplicate signals (same setup, date, symbol)
        unique_signals = []
        seen = set()

        for signal in all_signals:
            key = (signal.symbol, signal.setup, signal.date.date())
            if key not in seen:
                unique_signals.append(signal)
                seen.add(key)

        logger.info(f"Found {len(unique_signals)} unique signals for {clean_symbol}")
        return unique_signals

    def scan_multiple_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Scan multiple stocks in parallel"""
        all_signals = []

        def scan_single(symbol_data):
            symbol, df = symbol_data
            return self.scan_single_stock(df, symbol)

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(scan_single, (symbol, df)): symbol 
                for symbol, df in stock_data.items()
            }

            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    signals = future.result(timeout=60)
                    all_signals.extend(signals)

                    if signals:
                        logger.info(f"✅ {symbol}: {len(signals)} signals")
                    else:
                        logger.debug(f"⚪ {symbol}: No signals")

                except Exception as e:
                    logger.error(f"❌ {symbol}: Error scanning - {e}")

        # Sort signals by date (most recent first)
        all_signals.sort(key=lambda s: s.date, reverse=True)

        logger.info(f"Total signals found: {len(all_signals)}")
        return all_signals

    def filter_signals(self, signals: List[Signal], 
                      min_confidence: float = 0.5,
                      min_risk_reward: float = 1.5,
                      max_signals_per_stock: int = 2) -> List[Signal]:
        """Filter and prioritize signals"""
        # First filter by quality thresholds
        quality_signals = [
            s for s in signals 
            if s.confidence >= min_confidence and s.risk_reward >= min_risk_reward
        ]

        # Group by symbol and limit per stock
        symbol_groups = {}
        for signal in quality_signals:
            if signal.symbol not in symbol_groups:
                symbol_groups[signal.symbol] = []
            symbol_groups[signal.symbol].append(signal)

        # Sort each group by confidence and take top N
        final_signals = []
        for symbol, symbol_signals in symbol_groups.items():
            # Sort by confidence (descending) then by risk/reward (descending)
            symbol_signals.sort(key=lambda s: (s.confidence, s.risk_reward), reverse=True)
            final_signals.extend(symbol_signals[:max_signals_per_stock])

        # Final sort by confidence
        final_signals.sort(key=lambda s: s.confidence, reverse=True)

        logger.info(f"Filtered to {len(final_signals)} high-quality signals from {len(signals)} total")
        return final_signals

    def get_signal_summary(self, signals: List[Signal]) -> Dict:
        """Generate summary statistics of signals"""
        if not signals:
            return {
                'total_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'avg_confidence': 0,
                'avg_risk_reward': 0,
                'setups': {}
            }

        buy_signals = [s for s in signals if s.side == 'BUY']
        sell_signals = [s for s in signals if s.side == 'SELL']

        # Count by setup type
        setup_counts = {}
        for signal in signals:
            setup_counts[signal.setup] = setup_counts.get(signal.setup, 0) + 1

        return {
            'total_signals': len(signals),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'avg_confidence': sum(s.confidence for s in signals) / len(signals),
            'avg_risk_reward': sum(s.risk_reward for s in signals) / len(signals),
            'setups': setup_counts
        }
