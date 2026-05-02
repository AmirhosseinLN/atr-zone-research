"""Performance metrics computed from a list of per-trade results in R
(1R = the amount risked on the trade)."""
from __future__ import annotations

import math


def summarize(r: list[float]) -> dict:
    if not r:
        return {"trades": 0}
    wins = [x for x in r if x > 0]
    losses = [x for x in r if x <= 0]
    gross_win, gross_loss = sum(wins), -sum(losses)

    equity = peak = max_dd = 0.0
    streak = max_streak = 0
    for x in r:
        equity += x
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        streak = streak + 1 if x <= 0 else 0
        max_streak = max(max_streak, streak)

    return {
        "trades": len(r),
        "win_rate": len(wins) / len(r),
        "profit_factor": gross_win / gross_loss if gross_loss else math.inf,
        "expectancy_r": sum(r) / len(r),
        "net_r": sum(r),
        "max_drawdown_r": max_dd,
        "max_losing_streak": max_streak,
        # share of net profit that came from the single best trade
        "best_trade_share": (max(wins) / sum(r)) if wins and sum(r) > 0 else float("nan"),
    }


def print_summary(m: dict, title: str = "Results") -> None:
    if not m.get("trades"):
        print(f"{title}: no trades")
        return
    print(f"\n{title}")
    print("-" * len(title))
    print(f"trades            {m['trades']}")
    print(f"win rate          {m['win_rate']:.1%}")
    print(f"profit factor     {m['profit_factor']:.2f}")
    print(f"expectancy        {m['expectancy_r']:+.3f} R")
    print(f"net               {m['net_r']:+.1f} R")
    print(f"max drawdown      {m['max_drawdown_r']:.1f} R")
    print(f"losing streak     {m['max_losing_streak']}")
