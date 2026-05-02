# ATR Zone Research

Rule-based trading research on gold and other markets, from a first backtest to a live signal page.

I wanted a straight answer to a simple question: does a strategy built on support/resistance zones and volatility (ATR) have a real edge, or does it only look good on one lucky backtest? This repo is the record of how I went about answering it, version by version, including the mistakes I found along the way.

> **Note:** this is a showcase of the process and the results. The strategy rules, parameters and source are deliberately not published. Everything that is here (reports, screenshots, helper code) is meant to show how I work, not to be a recipe.

| Version | When | What changed |
|---|---|---|
| [v1](#v1--baseline-backtester) | May 2026 | Backtest engine, walk-forward, Monte Carlo, dashboard |
| [v2](#v2--long-history-validation) | May 2026 | 10 years of gold data, more markets, edge diagnostics |
| [v3](#v3--audit-recent-data-and-a-33-market-scan) | Oct 2026 | Found and fixed a look-ahead bug, re-tested on new data, scanned 33 markets |
| [v4](#v4--live-signal-page) | Oct 2026 | One-command live scanner that outputs entry, stop and target |

## v1 – Baseline backtester

The first working version, for XAUUSD and EURUSD:

- data download with a local cache, support/resistance zones from confirmed pivots, signal generation, and a trade simulator with trading costs
- performance metrics (profit factor, expectancy, drawdown, losing streaks) in units of risk (R)
- walk-forward windows and a Monte Carlo on the trade results
- a forward journal for paper-tracking signals, and a Streamlit dashboard

I made the execution assumptions deliberately pessimistic: entries happen on the next bar's open, costs are charged on every trade, and if the stop and the target are both touched inside one bar, the stop is assumed to have hit first.

## What I took from this

- A good backtest is where the work starts. One look-ahead bug was worth roughly a fifth of the reported profit.
- Choosing the best market or setting after the fact inflates results. Fixing the rules first and judging on later data is the only fair test.
- Edges are narrow. One market out of 33 held up, and that is a useful result, not a disappointing one.
- With a win rate around a third, the losing streaks are part of the strategy. Position size has to survive them.

## Not published

The strategy rules, parameter values, filters and the engine source are private. Reports have been edited to remove them. If you would like a walkthrough of how it works, I am happy to do that in conversation.

## Stack

Python (pandas, numpy), Streamlit, HTML/CSS/JavaScript with inline SVG for the reports, public data from Yahoo Finance and Binance.

## What is in this repo

```
docs/images/    screenshots of the reports
docs/reports/   the reports as HTML (open locally)
toolkit/        data download, performance metrics, Monte Carlo
CHANGELOG.md    version history
```

```bash
pip install -r requirements.txt
python toolkit/fetch_data.py GC=F        # downloads hourly + daily gold data into ./data
```

## Disclaimer

Research project. Nothing here is financial advice, and past results do not guarantee future ones.
