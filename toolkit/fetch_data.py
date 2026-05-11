"""Download hourly + daily OHLCV from public sources into CSV files.

  Yahoo Finance chart API  - forex, metals, energy, indices
                             (hourly history is limited to about 2 years)
  Binance public klines    - crypto, hourly history for years

Usage:  python fetch_data.py EURUSD=X GC=F BTCUSDT
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

OUT = Path("data")
HEADERS = {"User-Agent": "Mozilla/5.0"}


def _get(url: str, tries: int = 4) -> bytes | None:
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30) as r:
                return r.read()
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def yahoo(ticker: str, interval: str = "1h", since: int | None = None) -> pd.DataFrame | None:
    q = {"interval": interval}
    q.update({"period1": since, "period2": int(time.time())} if since else {"range": "730d"})
    raw = _get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}?{urllib.parse.urlencode(q)}")
    if raw is None:
        return None
    result = json.loads(raw)["chart"]["result"]
    if not result or "timestamp" not in result[0]:
        return None
    quote = result[0]["indicators"]["quote"][0]
    index = pd.to_datetime(result[0]["timestamp"], unit="s", utc=True)
    df = pd.DataFrame({k: quote[k] for k in ("open", "high", "low", "close", "volume")}, index=index)
    return df.dropna(subset=["open", "close"]).fillna({"volume": 0})


def binance(symbol: str, interval: str = "1h", start_ms: int = 1672531200000) -> pd.DataFrame | None:
    rows, cursor = [], start_ms
    while True:
        qs = urllib.parse.urlencode({"symbol": symbol, "interval": interval, "startTime": cursor, "limit": 1000})
        raw = _get(f"https://api.binance.com/api/v3/klines?{qs}")
        batch = json.loads(raw) if raw else []
        if not batch:
            break
        rows += batch
        cursor = batch[-1][0] + 1
        if len(batch) < 1000:
            break
        time.sleep(0.12)
    if not rows:
        return None
    df = pd.DataFrame(rows).iloc[:, :6]
    df.columns = ["ts", "open", "high", "low", "close", "volume"]
    df.index = pd.to_datetime(df.pop("ts"), unit="ms", utc=True)
    return df.astype(float).iloc[:-1]          # last bar is still forming


def save(df: pd.DataFrame, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    df = df[~df.index.duplicated()].sort_index()
    df.index.name = "timestamp"
    df.to_csv(OUT / name)
    print(f"{name}: {len(df)} bars, {df.index[0].date()} -> {df.index[-1].date()}")


if __name__ == "__main__":
    for tk in sys.argv[1:] or ["GC=F"]:
        is_crypto = tk.endswith("USDT")
        h = binance(tk) if is_crypto else yahoo(tk, "1h")
        d = binance(tk, "1d") if is_crypto else yahoo(tk, "1d", since=1420070400)
        clean = tk.replace("=", "").replace("^", "")
        for df, suffix in ((h, "H1"), (d, "D1")):
            if df is None:
                print(f"{tk} {suffix}: download failed")
            else:
                save(df, f"{clean}_{suffix}.csv")
