"""Monte Carlo on a list of trade results (in R).

Reshuffling the same trades cannot change the final total, so it only tells
you about drawdowns and losing streaks. Resampling WITH replacement
(bootstrap) also shows how uncertain the total itself is, which is the
question I actually care about with ~100 trades.
"""
from __future__ import annotations

import numpy as np


def _max_drawdown(curve: np.ndarray) -> np.ndarray:
    # curve: (runs, trades) cumulative results
    peak = np.maximum.accumulate(np.concatenate([np.zeros((curve.shape[0], 1)), curve], axis=1), axis=1)
    full = np.concatenate([np.zeros((curve.shape[0], 1)), curve], axis=1)
    return (peak - full).max(axis=1)


def _longest_losing_streak(r: np.ndarray) -> np.ndarray:
    out = np.zeros(r.shape[0], dtype=int)
    cur = np.zeros(r.shape[0], dtype=int)
    for j in range(r.shape[1]):
        cur = np.where(r[:, j] <= 0, cur + 1, 0)
        out = np.maximum(out, cur)
    return out


def run(results: list[float], runs: int = 5000, seed: int = 42, bootstrap: bool = True) -> dict:
    r = np.asarray(results, dtype=float)
    if len(r) < 2:
        raise ValueError("need at least 2 trades")
    rng = np.random.default_rng(seed)
    if bootstrap:
        sims = rng.choice(r, size=(runs, len(r)), replace=True)
    else:
        sims = np.stack([rng.permutation(r) for _ in range(runs)])

    curve = sims.cumsum(axis=1)
    final = curve[:, -1]
    dd = _max_drawdown(curve)
    streak = _longest_losing_streak(sims)
    return {
        "median_final_r": float(np.median(final)),
        "p5_final_r": float(np.percentile(final, 5)),
        "p95_final_r": float(np.percentile(final, 95)),
        "prob_net_loss": float((final < 0).mean()),
        "p95_max_drawdown_r": float(np.percentile(dd, 95)),
        "p95_losing_streak": float(np.percentile(streak, 95)),
    }
