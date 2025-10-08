#!/usr/bin/env python3
"""
Main orchestrator for Nifty 750 Trading Strategy System
Based on Timothy Knight's High-Probability Trade Setups
"""

import argparse
import logging
import json
import traceback
from pathlib import Path
from datetime import datetime
import pandas as pd
import os

# Import system modules
from src.universe import build_universe, get_liquid_subset
from src.data import fetch_multiple_stocks, validate_stock_data
from src.indicators import add_common_indicators, detect_pattern_conditions
from src.strategies.signals import StrategyScanner
from src.backtester import run_comprehensive_backtest
from src.report import render_html_report, create_csv_export, generate_summary_stats
from src.mailer import send_daily_trading_report, send_error_alert

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('trading_system.log')
    ]
)

logger = logging.getLogger(__name__)

class TradingSystemOrchestrator:
    """Main orchestrator for the trading system"""

    def __init__(self, mode: str = 'daily'):
        self.mode = mode
        self.output_dir = Path('out')
        self.output_dir.mkdir(exist_ok=True)

        logger.info(f"Initialized trading system in {mode} mode")

    def run_daily_analysis(self) -> dict:
        """Run complete daily trading analysis"""
        results = {
            'success': False,
            'signals': [],
            'summary': {},
            'backtest': {},
            'errors': []
        }

        try:
            # Step 1: Build stock universe
            logger.info("Building Nifty 750 universe...")
            universe = build_universe()

            if universe.empty:
                raise Exception("Failed to build stock universe")

            logger.info(f"Universe built: {len(universe)} stocks")

            # Step 2: Get liquid subset
            liquid_stocks = get_liquid_subset(universe, limit=20)  # Start with 20 for reliability
            stock_symbols = liquid_stocks['yahoo_symbol'].tolist()

            logger.info(f"Analyzing {len(stock_symbols)} liquid stocks...")

            # Step 3: Fetch market data
            logger.info("Fetching market data...")
            stock_data = fetch_multiple_stocks(stock_symbols, years=2, max_workers=3)

            if not stock_data:
                raise Exception("No stock data fetched")

            logger.info(f"Data fetched for {len(stock_data)} stocks")

            # Step 4: Add technical indicators
            logger.info("Calculating technical indicators...")
            enhanced_data = {}

            for symbol, df in stock_data.items():
                try:
                    if validate_stock_data(df, min_days=100):
                        # Add indicators
                        df_with_indicators = add_common_indicators(df)
                        df_enhanced = detect_pattern_conditions(df_with_indicators)
                        enhanced_data[symbol] = df_enhanced

                except Exception as e:
                    logger.warning(f"Error processing {symbol}: {e}")

            logger.info(f"Indicators calculated for {len(enhanced_data)} stocks")

            # Step 5: Run pattern detection
            logger.info("Scanning for trading signals...")
            scanner = StrategyScanner(max_workers=2)

            raw_signals = scanner.scan_multiple_stocks(enhanced_data)

            # Filter for high-quality signals
            filtered_signals = scanner.filter_signals(
                raw_signals,
                min_confidence=0.4,
                min_risk_reward=1.5,
                max_signals_per_stock=2
            )

            logger.info(f"Found {len(filtered_signals)} high-quality signals")

            # Step 6: Generate summary statistics
            summary = generate_summary_stats([s.to_dict() for s in filtered_signals])

            # Step 7: Run backtesting on a representative stock
            logger.info("Running backtest analysis...")
            backtest_results = {}

            try:
                if enhanced_data:
                    first_symbol = list(enhanced_data.keys())[0]
                    backtest_data = enhanced_data[first_symbol]

                    if len(backtest_data) > 100:
                        backtest_results = run_comprehensive_backtest(
                            backtest_data, 
                            first_symbol.replace('.NS', '')
                        )
                        logger.info("Backtest completed")

            except Exception as e:
                logger.error(f"Backtest error: {e}")

            # Step 8: Save results
            results['success'] = True
            results['signals'] = [s.to_dict() for s in filtered_signals]
            results['summary'] = summary
            results['backtest'] = backtest_results

            # Save to files
            self._save_results(results)

            return results

        except Exception as e:
            error_msg = f"Daily analysis failed: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())

            results['errors'].append(error_msg)
            return results

    def _save_results(self, results: dict):
        """Save analysis results to files"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Save JSON results
            json_file = self.output_dir / f'results_{timestamp}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"Results saved: {json_file}")

            # Save CSV of signals
            if results['signals']:
                csv_file = self.output_dir / f'signals_{timestamp}.csv'
                df_signals = pd.DataFrame(results['signals'])
                df_signals.to_csv(csv_file, index=False)
                logger.info(f"Signals CSV: {csv_file}")

                # Also save as latest
                latest_csv = self.output_dir / 'signals_latest.csv'
                df_signals.to_csv(latest_csv, index=False)

            # Save latest results
            latest_json = self.output_dir / 'results_latest.json'
            with open(latest_json, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def generate_and_send_report(self, results: dict) -> bool:
        """Generate HTML report and send via email"""
        try:
            logger.info("Generating and sending email report...")

            # Generate HTML report
            html_content = render_html_report(
                signals=results['signals'],
                summary=results['summary'],
                backtest_results=results.get('backtest')
            )

            # Save HTML report
            html_file = self.output_dir / 'daily_report.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"HTML report saved: {html_file}")

            # Create CSV export
            csv_file = None
            if results['signals']:
                csv_file = create_csv_export(results['signals'])

            # Send email
            success = send_daily_trading_report(html_content, csv_file)

            if success:
                logger.info("Email report sent successfully")
                return True
            else:
                logger.error("Failed to send email report")
                return False

        except Exception as e:
            error_msg = f"Report generation/sending failed: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())

            # Try to send error notification
            try:
                send_error_alert(error_msg)
                logger.info("Error alert sent")
            except Exception as alert_error:
                logger.error(f"Failed to send error alert: {alert_error}")

            return False

    def run(self):
        """Main execution method"""
        start_time = datetime.now()
        logger.info(f"Starting Nifty 750 Trading System - {start_time}")

        try:
            # Run analysis
            results = self.run_daily_analysis()

            if results['success']:
                logger.info("Analysis completed successfully")

                # Generate and send report
                report_sent = self.generate_and_send_report(results)

                # Final summary
                duration = datetime.now() - start_time
                logger.info(f"System execution completed in {duration}")
                logger.info(f"Signals found: {len(results['signals'])}")
                logger.info(f"Report sent: {'Yes' if report_sent else 'No'}")

                return 0  # Success

            else:
                logger.error("Analysis failed")

                # Send error alert
                error_details = "; ".join(results.get('errors', ['Unknown error']))
                send_error_alert(f"Analysis failed: {error_details}")

                return 1  # Failure

        except Exception as e:
            error_msg = f"System execution failed: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())

            try:
                send_error_alert(error_msg)
            except:
                pass  # Don't fail on alert failure

            return 1  # Failure

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Nifty 750 Trading Strategy System')

    parser.add_argument(
        '--mode',
        default='daily',
        choices=['daily', 'test'],
        help='Execution mode'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Skip email sending (for testing)'
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create and run orchestrator
    orchestrator = TradingSystemOrchestrator(args.mode)

    if args.mode == 'test':
        logger.info("Running in test mode")
        # Test basic functionality
        try:
            from src.universe import build_universe
            from src.data import fetch_ohlcv

            print("Testing universe building...")
            universe = build_universe()
            print(f"Universe: {len(universe)} stocks")

            print("Testing data fetch...")
            test_data = fetch_ohlcv('RELIANCE.NS', years=1)
            print(f"Data fetch: {len(test_data)} rows")

            print("Test completed successfully")
            return 0
        except Exception as e:
            print(f"Test failed: {e}")
            return 1

    else:
        # Normal daily mode
        return orchestrator.run()

if __name__ == "__main__":
    exit(main())
