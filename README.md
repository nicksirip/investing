# Investing

A collection of investment positioning guides for common macro and geopolitical scenarios, along with custom ThinkScript studies and scans for the [Thinkorswim](https://www.schwab.com/trading/thinkorswim) trading platform.

---

## Repository Structure

```
investing/
├── python/             # Python scripts for SEC filing analysis
├── scenarios/          # Scenario-based investment positioning guides
└── think-or-swim/      # Custom ThinkScript studies and scan columns
```

---

## Scenarios

Each guide provides a practical framework for adjusting portfolio exposure as a given macro or geopolitical event unfolds. Guides include a risk spectrum, key indicators to monitor, sector playbooks, ETF toolkits, hedging strategies, scenario-based positioning tables, and portfolio sizing guidelines.

| File | Description |
|------|-------------|
| [ai-bubble-positioning-guide.md](scenarios/ai-bubble-positioning-guide.md) | Portfolio positioning through the inflation and deflation of an AI valuation bubble |
| [deflation-positioning-guide.md](scenarios/deflation-positioning-guide.md) | Portfolio positioning through a deflationary or Japan-style lost-decade environment of falling prices, near-zero rates, and prolonged balance sheet deleveraging |
| [fed-rate-cut-positioning-guide.md](scenarios/fed-rate-cut-positioning-guide.md) | Portfolio positioning through a Federal Reserve rate-cutting cycle or extended low-rate environment — from the first cut through near-zero rates, QE accommodation, and eventual normalization |
| [fed-rate-hike-positioning-guide.md](scenarios/fed-rate-hike-positioning-guide.md) | Portfolio positioning through a Federal Reserve rate hiking cycle to combat inflation — from initial tightening through peak restrictive policy and eventual pivot |
| [global-trade-war-positioning-guide.md](scenarios/global-trade-war-positioning-guide.md) | Exposure adjustments as broad tariff escalation across multiple trading partners disrupts global supply chains and fragments the rules-based trading system |
| [global-world-war-positioning-guide.md](scenarios/global-world-war-positioning-guide.md) | Portfolio positioning through a multi-theater global armed conflict between major world powers — from escalating proxy conflicts through full wartime mobilization and capital preservation |
| [holding-cash-positioning-guide.md](scenarios/holding-cash-positioning-guide.md) | Tax-efficient framework for parking capital and systematically deploying it as buying opportunities emerge |
| [iran-conflict-positioning-guide.md](scenarios/iran-conflict-positioning-guide.md) | Exposure adjustments as US/Israel–Iran tensions escalate or de-escalate, with focus on Strait of Hormuz oil supply risk |
| [monthly-cash-income-guide.md](scenarios/monthly-cash-income-guide.md) | A practical, tax-efficient framework for structuring a portfolio to generate reliable monthly cash income sufficient to cover living expenses |
| [mortgage-lender-collapse-positioning-guide.md](scenarios/mortgage-lender-collapse-positioning-guide.md) | Positioning as stress in the mortgage lending sector escalates toward systemic lender failures and housing market contagion |
| [pandemic-positioning-guide.md](scenarios/pandemic-positioning-guide.md) | Portfolio positioning through a global pandemic or public health crisis — from early outbreak detection through peak disruption and recovery |
| [private-credit-collapse-positioning-guide.md](scenarios/private-credit-collapse-positioning-guide.md) | Positioning as stress in the private credit market escalates from rising loan defaults and NAV erosion toward systemic illiquidity, BDC dividend cuts, and leveraged finance contagion |
| [russia-nato-conflict-positioning-guide.md](scenarios/russia-nato-conflict-positioning-guide.md) | Exposure adjustments as Russia/NATO tensions escalate or de-escalate, with focus on European energy security, defense spending, and commodity supply disruptions |
| [stagflation-positioning-guide.md](scenarios/stagflation-positioning-guide.md) | Portfolio positioning through a stagflationary environment of persistently high inflation combined with stagnant or negative economic growth |
| [us-bank-failure-positioning-guide.md](scenarios/us-bank-failure-positioning-guide.md) | Positioning as stress in the US banking system escalates or stabilizes |
| [us-china-conflict-positioning-guide.md](scenarios/us-china-conflict-positioning-guide.md) | Exposure adjustments as tensions between the United States and China escalate or de-escalate |
| [us-debt-crisis-positioning-guide.md](scenarios/us-debt-crisis-positioning-guide.md) | Positioning through US sovereign debt stress — from debt ceiling brinkmanship through credit rating downgrade and Treasury market dysfunction |
| [us-recession-positioning-guide.md](scenarios/us-recession-positioning-guide.md) | Portfolio positioning through the US economic cycle from slowdown through recession and recovery |

---

## Python Scripts

Utility scripts for analyzing SEC filings and institutional holdings data.

| File | Description |
|------|-------------|
| [13f_summary.py](python/13f_summary.py) | Parses SEC EDGAR 13F-HR filings to produce ranked tables of the top 50 institutional filers by AUM, top 10 holdings by aggregated market value, and top 10 buys/sells by net dollar change. Supports live EDGAR downloads or local SEC DERA quarterly zip files. Outputs console tables and CSV files. |

**Dependencies:** `requests`, `lxml`, `pandas`, `python-dateutil`

```bash
pip install requests lxml pandas python-dateutil
```

**Usage:**

```bash
# Live EDGAR download (edit USER_AGENT in script with your contact info first)
python python/13f_summary.py

# Local SEC DERA zip (single quarter)
python python/13f_summary.py --zip /path/to/current_quarter_form13f.zip

# Two-quarter comparison for buy/sell analysis
python python/13f_summary.py --prior-zip /path/to/prior_quarter.zip \
                              --zip       /path/to/current_quarter.zip

# Sample fixtures (included for dev/testing)
python python/13f_summary.py --zip python/fixtures/sample_13f.zip
```

---

## Thinkorswim ThinkScript

Custom studies and scan columns for use in the [Thinkorswim](https://www.schwab.com/trading/thinkorswim) platform. Most studies build on the built-in `Ray` indicator (which measures bull/bear power) and combine it with moving average signals to generate buy/sell scan criteria.

| File | Description |
|------|-------------|
| [bid_ask_separation_col.thinkscript](think-or-swim/bid_ask_separation_col.thinkscript) | Scan column showing the bid/ask spread as a measure of liquidity |
| [long_down_wick_study.thinkscript](think-or-swim/long_down_wick_study.thinkscript) | Study that highlights candles with long lower wicks (potential reversal signal) |
| [long_up_wick_study.thinkscript](think-or-swim/long_up_wick_study.thinkscript) | Study that highlights candles with long upper wicks (potential reversal signal) |
| [obv_trend_col.thinkscript](think-or-swim/obv_trend_col.thinkscript) | Scan column showing the On-Balance Volume (OBV) trend direction |
| [price_profile_rsi_volume_direction_study.thinkscript](think-or-swim/price_profile_rsi_volume_direction_study.thinkscript) | Study combining rolling volume profile, RSI regime shifts, and relative volume confirmation to identify potential bullish or bearish directional changes |
| [ray_direction_column.thinkscript](think-or-swim/ray_direction_column.thinkscript) | Scan column showing the current Ray indicator direction |
| [ray_ma_study.thinkscript](think-or-swim/ray_ma_study.thinkscript) | Study that plots a moving average of the Ray bear/bull power values |
| [rsi_col.thinkscript](think-or-swim/rsi_col.thinkscript) | Watchlist column displaying the current RSI value with red text when overbought (≥ 70) and green text when oversold (≤ 30) |
| [rsi_raybearpower_range.thinkscript](think-or-swim/rsi_raybearpower_range.thinkscript) | Scan combining RSI range filters with Ray bear power thresholds |
| [trade_hunter_study.thinkscript](think-or-swim/trade_hunter_study.thinkscript) | Composite study that signals potential buy/sell entries using Ray bear power crossovers, moving average crossovers, and moving average directional changes |
| [volume_study_enhanced.thinkscript](think-or-swim/volume_study_enhanced.thinkscript) | Volume-pane study that plots volume histogram + moving average, with user-selectable price-basis direction coloring (Close/Open/High/Low/HL2/HLC3/OHLC4): up = RGB(0,255,0), down = RGB(255,0,0), neutral = RGB(255,255,255) |
| [volume_spike_col.thinkscript](think-or-swim/volume_spike_col.thinkscript) | Scan column that flags abnormal volume spikes relative to a historical average |

---

> **Disclaimer:** All content in this repository is for informational and educational purposes only. The author is not a financial advisor, and nothing here constitutes financial advice or a recommendation to buy or sell any security. All investments involve risk, including the potential loss of principal. Past performance is not indicative of future results. Always do your own research and due diligence, and consult a qualified financial advisor before making any investment decisions.
