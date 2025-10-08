# 🎯 Nifty 750 Trading Strategy System

**Automated High-Probability Trading Signals based on Timothy Knight's "High-Probability Trade Setups"**

[![GitHub Actions](https://img.shields.io/badge/Automation-GitHub%20Actions-blue)](/.github/workflows/trading.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Email](https://img.shields.io/badge/Email-Gmail%20SMTP-red)](mailto:paras.m.parmar@gmail.com)

## 📋 Overview

This system implements **20 high-probability trading strategies** from Timothy Knight's renowned book, specifically adapted for the **Indian Nifty 750 Total Market Index**. It automatically scans stocks daily, identifies chart patterns, generates trading signals with precise entry/exit rules, and delivers comprehensive HTML email reports every weekday at **9:30 AM IST**.

### Key Features

- ✅ **20 Timothy Knight Strategies** - Head & Shoulders, Triangles, Double Tops, Flags, Moving Averages, etc.
- ✅ **Automated Daily Screening** - Scans Nifty 750 stocks using GitHub Actions
- ✅ **10-Year Backtesting** - Historical performance validation with risk metrics
- ✅ **Professional Email Reports** - HTML reports with signals, targets, and confidence scores
- ✅ **Risk Management** - Built-in position sizing and 1:2+ risk/reward ratios
- ✅ **Pure Python Implementation** - No TA-Lib compilation issues, CI/CD friendly

## 🚀 Quick Start

### 1. Repository Setup

1. **Fork this repository** to your GitHub account
2. **Clone locally** (optional, for testing):
   ```bash
   git clone https://github.com/YOUR_USERNAME/nifty-750-trading-strategy.git
   cd nifty-750-trading-strategy
   ```

### 2. Gmail Configuration

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Security → App passwords
   - Generate password for "Mail"
   - **Save the 16-character password** (you'll need it for GitHub secrets)

### 3. GitHub Secrets Setup

1. Go to your repository **Settings** → **Secrets and Variables** → **Actions**
2. **Add these Repository Secrets**:

   ```
   EMAIL_USER: your_email@gmail.com
   EMAIL_PASS: your_16_character_app_password
   EMAIL_TO: paras.m.parmar@gmail.com (optional, defaults to EMAIL_USER)
   ```

### 4. Activate the System

1. **GitHub Actions will automatically start** running on weekdays at 9:30 AM IST
2. **First run**: Go to **Actions** tab → **Run workflow** to test immediately
3. **Check email** for your first trading signals report!

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ GitHub Actions  │    │ Python Trading   │    │ Email Report    │
│ (9:30 AM IST)  │───▶│ System           │───▶│ (Gmail SMTP)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Data & Analysis   │
                    │                   │
                    │ • Nifty 750 Data  │
                    │ • Pattern Detection│
                    │ • 10-Year Backtest │
                    │ • Risk Management  │
                    └───────────────────┘
```

## 📈 Trading Strategies Implemented

| Strategy | Pattern Type | Risk/Reward | Confidence | Timeframe |
|----------|--------------|-------------|------------|-----------|
| **Head & Shoulders** | Reversal | 1:2 | High | Daily/4H |
| **Ascending Triangle** | Continuation | 1:3 | High | Daily/4H |
| **Double Top/Bottom** | Reversal | 1:2-2.5 | High | Daily/Weekly |
| **Bull/Bear Flags** | Continuation | 1:2 | Medium | 4H/Daily |
| **Golden Cross** | Trend | 1:3+ | Medium | Daily |
| **Bollinger Breakout** | Volatility | 1:2.5 | High | Daily |

*Complete implementation of all 20 Timothy Knight patterns*

## 📧 Email Report Features

### Daily Reports Include:
- 📊 **Signal Summary** - Total signals, buy/sell breakdown, average confidence
- 🎯 **Trading Opportunities** - Entry, stop, target prices with risk/reward ratios  
- 📈 **Backtest Performance** - 10-year historical results vs benchmark
- ⚠️ **Risk Disclaimers** - Professional compliance warnings

### Sample Email Content:
```
🎯 Nifty 750 Trading Signals - 2025-10-07 • 09:30 IST

Summary: 12 Total Signals | 8 Buy | 4 Sell | 78% Avg Confidence

Top Signals:
RELIANCE - Ascending Triangle - BUY - Entry: ₹2,475 - Target: ₹2,650
TCS - Head & Shoulders - SELL - Entry: ₹3,125 - Target: ₹2,950
INFY - Bull Flag - BUY - Entry: ₹1,832 - Target: ₹1,975

10-Year Backtest: 14.2% Annual Return | Sharpe: 1.18 | Max DD: -18%
```

## 🔧 System Configuration

### File Structure
```
nifty-750-trading-strategy/
├── .github/workflows/trading.yml    # GitHub Actions automation
├── src/
│   ├── universe.py                  # Nifty 750 stock universe builder
│   ├── data.py                      # Yahoo Finance data fetching
│   ├── indicators.py                # Technical indicators (pure Python)
│   ├── strategies/                  # Timothy Knight pattern detection
│   ├── backtester.py               # 10-year performance analysis
│   ├── report.py                   # HTML email report generation
│   └── mailer.py                   # Gmail SMTP email sender
├── run.py                          # Main orchestrator
├── requirements.txt                # Python dependencies
└── configs/settings.yaml           # System configuration
```

### Customization Options

**Change Email Recipient:**
```yaml
# In configs/settings.yaml
email:
  default_recipient: "your_email@gmail.com"
```

**Modify Stock Universe:**
```python
# In src/universe.py - edit FALLBACK_STOCKS list
FALLBACK_STOCKS = [
    'RELIANCE', 'TCS', 'INFY',  # Add your preferred stocks
    # ... more stocks
]
```

**Adjust Analysis Frequency:**
```yaml
# In .github/workflows/trading.yml
schedule:
  - cron: '0 4 * * 1-5'  # Current: 9:30 AM IST weekdays
  # Change to: '30 4 * * 1-5' for 10:00 AM IST
```

**Strategy Parameters:**
```yaml
# In configs/settings.yaml
strategies:
  min_risk_reward: 2.0     # Minimum 1:2 risk/reward
  min_confidence: 0.6      # Higher confidence threshold  
  max_signals_per_stock: 1 # Limit signals per stock
```

## 🧪 Local Testing

### Prerequisites
- Python 3.11+
- Gmail account with App Password

### Installation & Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (Linux/Mac)
export EMAIL_USER="your_email@gmail.com"
export EMAIL_PASS="your_app_password"

# Set environment variables (Windows)
set EMAIL_USER=your_email@gmail.com
set EMAIL_PASS=your_app_password

# Test system components
python run.py --mode test --verbose

# Run full analysis (without email)
python run.py --mode daily --no-email --verbose

# Test email system
python -m src.mailer
```

## 📊 Performance Monitoring

### GitHub Actions Dashboard
- **Workflow Status**: Check Actions tab for execution history
- **Artifacts**: Download daily results (JSON/CSV) for analysis  
- **Logs**: View detailed execution logs for troubleshooting

### Email Notifications
- **Success**: Daily signal reports with performance metrics
- **Failure**: Automatic error alerts with diagnostic information

### Local Analysis
```bash
# View latest results
cat out/results_latest.json

# Analyze signals in Excel
open out/signals_latest.csv
```

## ⚠️ Risk Disclaimers

**IMPORTANT: This system is for educational purposes only.**

- 📚 **Educational Use**: Based on Timothy Knight's academic methodology
- 🚫 **No Investment Advice**: Past performance doesn't guarantee future results
- 💰 **Risk of Loss**: All trading involves substantial risk of capital loss
- 👨‍💼 **Professional Guidance**: Consult qualified financial advisors
- 🇮🇳 **Market Risks**: Indian markets subject to regulatory and currency risks

### Best Practices
1. **Paper Trade First** - Test signals without real money
2. **Start Small** - Use minimal position sizes initially  
3. **Understand Patterns** - Study Timothy Knight's original book
4. **Risk Management** - Never risk more than you can afford to lose
5. **Stay Disciplined** - Follow predetermined rules, avoid emotional decisions

## 🛠️ Troubleshooting

### Common Issues

**Email Authentication Failed:**
```
❌ Email authentication failed
```
- Verify 2FA is enabled on Gmail
- Use App Password (not regular password)
- Check EMAIL_USER and EMAIL_PASS secrets

**No Data Fetched:**
```
❌ No stock data fetched
```
- Yahoo Finance API may be temporarily down
- Check internet connectivity in GitHub Actions
- Fallback stock list will be used automatically

**Pattern Detection Errors:**
```
❌ Error in strategy scan
```
- Insufficient historical data for some stocks
- System automatically skips problematic stocks
- Check logs for specific error details

### Support Resources
1. **GitHub Issues**: Report bugs and request features
2. **Workflow Logs**: Actions tab → Latest run → View logs
3. **Email Alerts**: System sends automatic error notifications
4. **Local Testing**: Use `--mode test` for component validation

## 📚 References & Credits

- **📖 Book**: ["High-Probability Trade Setups: A Chartist's Guide to Real-Time Trading"](https://www.amazon.com/High-Probability-Trade-Setups-Chartists-Real-Time/dp/1118022254) by Timothy Knight
- **📊 Index**: [NSE Nifty 750 Total Market Index](https://www.niftyindices.com/indices/equity/broad-based-indices/nifty-total-market)
- **📈 Data Source**: [Yahoo Finance API](https://finance.yahoo.com) for Indian stock market data
- **🔧 Technical Analysis**: [TA-Lib Python](https://github.com/mrjbq7/ta-lib) and [pandas-ta](https://github.com/twopirllc/pandas-ta)

## 📄 License & Disclaimer

This project implements academic concepts from Timothy Knight's published work for educational purposes. Users are responsible for their own investment decisions and should respect intellectual property rights.

**Generated by:** Automated Trading System  
**Methodology:** Timothy Knight High-Probability Setups  
**Target Market:** Indian Nifty 750 Total Market Index  
**Last Updated:** October 2025

---

## 📞 Quick Help

**✅ System Working?** Check if you receive daily emails at 9:30 AM IST  
**❌ Issues?** Check GitHub Actions logs and error email alerts  
**📧 No Emails?** Verify Gmail App Password and GitHub secrets  
**📈 Want More Stocks?** Edit liquid_subset_size in configs/settings.yaml  

**Happy Trading! 🎯📈**
