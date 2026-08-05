"""Fetch historical price data via yfinance, cached on disk once per day."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
HISTORY_PERIOD = "1y"  # enough for SMA200 + 52-week high/low


def _cache_path(ticker: str, as_of: date) -> Path:
    return CACHE_DIR / f"{ticker}_{as_of.isoformat()}.csv"


def get_price_history(ticker: str, as_of: date | None = None) -> pd.DataFrame:
    """Return a DataFrame of daily OHLCV for `ticker`, indexed by date.

    Cached to disk per (ticker, day) so re-running the app the same day
    doesn't refetch from Yahoo Finance.
    """
    as_of = as_of or date.today()
    cache_file = _cache_path(ticker, as_of)

    if cache_file.exists():
        return pd.read_csv(cache_file, index_col=0, parse_dates=True)

    history = yf.Ticker(ticker).history(period=HISTORY_PERIOD)
    if history.empty:
        raise ValueError(f"No price data returned for ticker '{ticker}'")

    CACHE_DIR.mkdir(exist_ok=True)
    history.to_csv(cache_file)
    return history


def get_current_price(ticker: str, as_of: date | None = None) -> float:
    history = get_price_history(ticker, as_of)
    return float(history["Close"].iloc[-1])
