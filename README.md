# Investing

A collection of investment positioning guides for common macro and geopolitical scenarios, along with custom ThinkScript studies and scans for the [Thinkorswim](https://www.schwab.com/trading/thinkorswim) trading platform.

---

## Repository Structure

```
investing/
├── scenarios/          # Scenario-based investment positioning guides
└── think-or-swim/      # Custom ThinkScript studies and scan columns
```

---

## Scenarios

Each guide provides a practical framework for adjusting portfolio exposure as a given macro or geopolitical event unfolds. Guides include a risk spectrum, key indicators to monitor, sector playbooks, ETF toolkits, hedging strategies, scenario-based positioning tables, and portfolio sizing guidelines.

| File | Description |
|------|-------------|
| [ai-bubble-positioning-guide.md](scenarios/ai-bubble-positioning-guide.md) | Portfolio positioning through the inflation and deflation of an AI valuation bubble |
| [holding-cash-positioning-guide.md](scenarios/holding-cash-positioning-guide.md) | Tax-efficient framework for parking capital and systematically deploying it as buying opportunities emerge |
| [iran-conflict-general-guide.md](scenarios/iran-conflict-general-guide.md) | Exposure adjustments as US/Israel–Iran tensions escalate or de-escalate, with focus on Strait of Hormuz oil supply risk |
| [mortgage-lender-collapse-positioning-guide.md](scenarios/mortgage-lender-collapse-positioning-guide.md) | Positioning as stress in the mortgage lending sector escalates toward systemic lender failures and housing market contagion |
| [us-bank-failure-positioning-guide.md](scenarios/us-bank-failure-positioning-guide.md) | Positioning as stress in the US banking system escalates or stabilizes |
| [us-china-conflict-positioning-guide.md](scenarios/us-china-conflict-positioning-guide.md) | Exposure adjustments as tensions between the United States and China escalate or de-escalate |
| [us-recession-positioning-guide.md](scenarios/us-recession-positioning-guide.md) | Portfolio positioning through the US economic cycle from slowdown through recession and recovery |

---

## Thinkorswim ThinkScript

Custom studies and scan columns for use in the [Thinkorswim](https://www.schwab.com/trading/thinkorswim) platform. Most studies build on the built-in `Ray` indicator (which measures bull/bear power) and combine it with moving average signals to generate buy/sell scan criteria.

| File | Description |
|------|-------------|
| [bid_ask_separation_col.thinkscript](think-or-swim/bid_ask_separation_col.thinkscript) | Scan column showing the bid/ask spread as a measure of liquidity |
| [long_down_wick_study.thinkscript](think-or-swim/long_down_wick_study.thinkscript) | Study that highlights candles with long lower wicks (potential reversal signal) |
| [long_up_wick_study.thinkscript](think-or-swim/long_up_wick_study.thinkscript) | Study that highlights candles with long upper wicks (potential reversal signal) |
| [obv_trend_col.thinkscript](think-or-swim/obv_trend_col.thinkscript) | Scan column showing the On-Balance Volume (OBV) trend direction |
| [ray_direction_column.thinkscript](think-or-swim/ray_direction_column.thinkscript) | Scan column showing the current Ray indicator direction |
| [ray_ma_study.thinkscript](think-or-swim/ray_ma_study.thinkscript) | Study that plots a moving average of the Ray bear/bull power values |
| [rsi_raybearpower_range.thinkscript](think-or-swim/rsi_raybearpower_range.thinkscript) | Scan combining RSI range filters with Ray bear power thresholds |
| [trade_hunter_study.thinkscript](think-or-swim/trade_hunter_study.thinkscript) | Composite study that signals potential buy/sell entries using Ray bear power crossovers, moving average crossovers, and moving average directional changes |
| [volume_spike_col.thinkscript](think-or-swim/volume_spike_col.thinkscript) | Scan column that flags abnormal volume spikes relative to a historical average |

---

> **Disclaimer:** All content in this repository is for informational purposes only and does not constitute financial advice. Always conduct your own due diligence and consult a qualified financial advisor before making investment decisions.
