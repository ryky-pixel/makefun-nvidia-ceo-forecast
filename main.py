#!/usr/bin/env python3
"""make.fun polymarket-nvidia-ceo-forecast-01 entry.

Reads each case in the input dir (makefun/polymarket-case/v1 JSON) and writes
<id>.out with 5-quantile forecasts for the next `horizon_minutes` minutes.

Method: per-market random walk in logit(price) space.
  - sigma_y estimated from 1-minute logit differences over the last 24h
    (with a floor and a blend toward the full-history sigma).
  - median = last price, nudged by a damped short-term drift (last 4h trend,
    shrunk hard and capped) plus a small mean-reversion pull toward the
    trailing 24h mean.
  - quantiles = sigmoid(logit(median) + z * sigma_y * sqrt(h)), clamped.
Deterministic, offline, standard library only.
"""
import json
import math
import os
from pathlib import Path

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
QUANTILES = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.644854, -0.67449, 0.0, 0.67449, 1.644854]
EPS = 1e-6


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def logit(p):
    p = clamp(p, EPS, 1.0 - EPS)
    return math.log(p / (1.0 - p))


def sigmoid(y):
    if y >= 0:
        return 1.0 / (1.0 + math.exp(-y))
    e = math.exp(y)
    return e / (1.0 + e)


def price6(x):
    return round(clamp(x, 0.0, 1.0) * 1e6) / 1e6 + 0.0


def stdev(vals):
    n = len(vals)
    if n < 2:
        return 0.0
    mu = sum(vals) / n
    return math.sqrt(sum((v - mu) ** 2 for v in vals) / (n - 1))


def forecast_market(prices, horizon):
    if not prices:
        raise ValueError("market has no prices")
    x_last = clamp(prices[-1], 0.0, 1.0)

    # Horizon-scale volatility: non-overlapping 240-min logit diffs (1-min
    # diffs are inflated by bid-ask bounce), blended with 60-min diffs.
    # Fall back to shorter scales when history is short.
    ys = [logit(p) for p in prices]
    def scale_sigma(step):
        d = [ys[i] - ys[i - step] for i in range(step, len(ys), step)]
        return stdev(d) / math.sqrt(step) if len(d) >= 3 else None
    s240 = scale_sigma(240)
    s60 = scale_sigma(60)
    s1 = scale_sigma(1)
    parts = [s for s in (s240, s60) if s is not None]
    sigma_y = clamp(sum(parts) / len(parts) if parts else (s1 or 0.0), 0.02, 0.12)

    # Damped drift from last 4h (per-minute logit slope), shrunk 85%, capped.
    drift_per_min = 0.0
    if len(ys) > 240:
        slope = (ys[-1] - ys[-241]) / 240.0
        drift_per_min = clamp(slope * 0.15, -0.002, 0.002)

    # Small mean-reversion pull toward trailing 24h mean price (in logit space).
    tail = prices[-1440:] if len(prices) > 1440 else prices
    mean_price = sum(tail) / len(tail)
    pull = clamp((logit(mean_price) - logit(x_last)) * 0.02, -0.15, 0.15)

    y0 = logit(x_last) + pull
    rows = []
    for h in range(1, horizon + 1):
        center = y0 + drift_per_min * h
        width = sigma_y * math.sqrt(h)
        row = [price6(sigmoid(center + z * width)) for z in Z]
        # enforce non-decreasing (sigmoid is monotone; guards rounding)
        for j in range(1, 5):
            if row[j] < row[j - 1]:
                row[j] = row[j - 1]
        rows.append(row)
    return rows


def main():
    in_dir = Path(INPUT_DIR)
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(f for f in os.listdir(in_dir) if f.endswith(".in"))
    for fname in files:
        case_id = fname[:-3]
        with open(in_dir / fname, encoding="utf-8") as fh:
            c = json.load(fh)
        if c["quantiles"] != QUANTILES:
            raise ValueError(f"{fname} asks for quantiles {c['quantiles']}")
        horizon = int(c["horizon_minutes"])
        forecasts = [
            {"id": m["id"], "q": forecast_market(m["prices"], horizon)}
            for m in c["markets"]
        ]
        with open(out_dir / f"{case_id}.out", "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"forecasts": forecasts}) + "\n")


if __name__ == "__main__":
    main()
