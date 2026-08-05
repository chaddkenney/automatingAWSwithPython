"""Technical indicators computed from a daily OHLCV price series."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def sma(closes: pd.Series, window: int) -> float | None:
    """Simple moving average of the last `window` closes, or None if not enough data."""
    if len(closes) < window:
        return None
    return float(closes.tail(window).mean())


def rsi(closes: pd.Series, window: int = 14) -> float | None:
    """Wilder's RSI over the last `window` periods, or None if not enough data."""
    if len(closes) < window + 1:
        return None
    delta = closes.diff().dropna()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.tail(window).mean()
    avg_loss = losses.tail(window).mean()
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return float(100 - (100 / (1 + rs)))


def annualized_volatility(closes: pd.Series, window: int = 30) -> float | None:
    """Annualized stdev of daily returns over the trailing `window` days, as a percent."""
    if len(closes) < window + 1:
        return None
    daily_returns = closes.pct_change().dropna().tail(window)
    return float(daily_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR) * 100)


@dataclass
class Indicators:
    price: float
    sma50: float | None
    sma200: float | None
    rsi14: float | None
    high_52wk: float
    low_52wk: float
    drawdown_from_high_pct: float
    volatility_pct: float | None


def compute_indicators(history: pd.DataFrame) -> Indicators:
    closes = history["Close"]
    price = float(closes.iloc[-1])
    high_52wk = float(closes.max())
    low_52wk = float(closes.min())
    drawdown_from_high_pct = (price - high_52wk) / high_52wk * 100

    return Indicators(
        price=price,
        sma50=sma(closes, 50),
        sma200=sma(closes, 200),
        rsi14=rsi(closes, 14),
        high_52wk=high_52wk,
        low_52wk=low_52wk,
        drawdown_from_high_pct=drawdown_from_high_pct,
        volatility_pct=annualized_volatility(closes),
    )
