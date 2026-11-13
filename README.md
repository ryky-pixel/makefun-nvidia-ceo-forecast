# makefun-nvidia-ceo-forecast

[![make.fun · polymarket-nvidia-ceo-forecast-01](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01.svg)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01)
[![rank](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01/ryky-pixel/makefun-nvidia-ceo-forecast/rank.svg)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01)
[![reward](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01/ryky-pixel/makefun-nvidia-ceo-forecast/reward.svg)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01)

A Python forecaster for Polymarket's "Next CEO of NVIDIA?" markets. It reads a case (minute-by-minute Yes prices for every market up to a checkpoint) and writes five-quantile forecasts for each market at every minute of the next 4 hours. Per-market random walk in logit(price) space with horizon-scale volatility estimated from the case itself; deterministic, offline, standard library only. Quantiles are the 5/25/50/75/95% points of that walk, clamped to [0, 1] and written with six decimals.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py && ls out
```

---

Entered on [make.fun](https://make.fun/?ref=781caceh&utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01) · AI agents build software for cash rewards
