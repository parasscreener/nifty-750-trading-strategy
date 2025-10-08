from datetime import datetime
import pandas as pd
import logging
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)

def render_html_report(signals: List[Dict], summary: Dict[str, Any], backtest_results: Dict[str, Any] = None) -> str:
    """Render simple HTML email report"""
    try:
        now = datetime.now()
        report_date = now.strftime('%Y-%m-%d')
        report_time = now.strftime('%H:%M')

        # Create signals table
        signals_html = ""
        if signals:
            signals_html = "<h2>Today's Trading Signals</h2>"
            signals_html += "<table border='1' cellpadding='5' cellspacing='0'>"
            signals_html += "<tr><th>Symbol</th><th>Setup</th><th>Side</th><th>Entry</th><th>Target</th><th>Confidence</th></tr>"

            for signal in signals[:10]:
                symbols = signal.get('symbol', 'N/A')
                setup = signal.get('setup', 'N/A').replace('_', ' ')
                side = signal.get('side', 'N/A')
                entry = signal.get('entry', 0)
                target = signal.get('target', 0)
                confidence = signal.get('confidence', 0) * 100

                signals_html += f"<tr><td>{symbols}</td><td>{setup}</td><td>{side}</td>"
                signals_html += f"<td>{entry:.2f}</td><td>{target:.2f}</td><td>{confidence:.0f}%</td></tr>"

            signals_html += "</table>"
        else:
            signals_html = "<h2>No Signals Today</h2><p>No high-probability setups found in today's scan.</p>"

        # Create backtest section
        backtest_html = ""
        if backtest_results and backtest_results.get('benchmark'):
            bt = backtest_results['benchmark']
            backtest_html = "<h3>Performance Analysis</h3>"
            backtest_html += f"<p>Total Return: {bt.get('Return [%]', 0):.1f}% | "
            backtest_html += f"Sharpe Ratio: {bt.get('Sharpe Ratio', 0):.2f} | "
            backtest_html += f"Max Drawdown: {bt.get('Max. Drawdown [%]', 0):.1f}%</p>"

        # Complete HTML document
        html_content = f'''<html>
<head>
    <meta charset="utf-8">
    <title>Nifty 750 Trading Signals</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Nifty 750 Trading Signals</h1>
        <p>{report_date} • {report_time} IST</p>
    </div>

    <h2>Summary</h2>
    <p><strong>Total Signals:</strong> {summary.get('total_signals', 0)} | 
    <strong>Buy:</strong> {summary.get('buy_signals', 0)} | 
    <strong>Sell:</strong> {summary.get('sell_signals', 0)} |
    <strong>Avg Confidence:</strong> {summary.get('avg_confidence', 0)*100:.0f}%</p>

    {signals_html}

    {backtest_html}

    <hr>
    <p><em>This analysis is for educational purposes only and is not investment advice.</em></p>
    <p><em>Trading involves substantial risk of loss.</em></p>
</body>
</html>'''

        logger.info("Generated HTML report successfully")
        return html_content

    except Exception as e:
        logger.error(f"Error rendering report: {e}")
        return f"<html><body><h1>Report Generation Error</h1><p>{str(e)}</p></body></html>"

def create_csv_export(signals: List[Dict], filename: str = None) -> str:
    """Create CSV export of signals"""
    try:
        if not filename:
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"out/signals_{date_str}.csv"

        os.makedirs('out', exist_ok=True)

        if signals:
            df = pd.DataFrame(signals)
            df.to_csv(filename, index=False)
            logger.info(f"Created CSV export: {filename}")
        else:
            # Create empty CSV with headers
            with open(filename, 'w') as f:
                f.write("date,symbol,setup,side,entry,stop,target,confidence,risk_reward\n")
            logger.info(f"Created empty CSV: {filename}")

        return filename

    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return ""

def generate_summary_stats(signals: List[Dict]) -> Dict[str, Any]:
    """Generate summary statistics for signals"""
    if not signals:
        return {
            'total_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'avg_confidence': 0,
            'avg_risk_reward': 0
        }

    buy_signals = [s for s in signals if s.get('side') == 'BUY']
    sell_signals = [s for s in signals if s.get('side') == 'SELL']

    confidences = [s.get('confidence', 0) for s in signals]
    risk_rewards = [s.get('risk_reward', 0) for s in signals]

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    avg_risk_reward = sum(risk_rewards) / len(risk_rewards) if risk_rewards else 0

    return {
        'total_signals': len(signals),
        'buy_signals': len(buy_signals),
        'sell_signals': len(sell_signals),
        'avg_confidence': avg_confidence,
        'avg_risk_reward': avg_risk_reward
    }
