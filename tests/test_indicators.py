import pandas as pd

from quant_app.indicators import (
    annualized_volatility,
    compute_indicators,
    rsi,
    sma,
)


def test_sma_averages_last_window_only():
    closes = pd.Series(range(1, 11))  # 1..10
    assert sma(closes, 5) == 8.0  # mean of 6,7,8,9,10


def test_sma_returns_none_when_not_enough_data():
    closes = pd.Series([1, 2, 3])
    assert sma(closes, 5) is None


def test_rsi_is_100_for_all_gains():
    closes = pd.Series(range(1, 20))  # strictly increasing
    assert rsi(closes, 14) == 100.0


def test_rsi_is_0_for_all_losses():
    closes = pd.Series(range(20, 1, -1))  # strictly decreasing
    assert rsi(closes, 14) == 0.0


def test_volatility_is_zero_for_flat_prices():
    closes = pd.Series([100.0] * 40)
    assert annualized_volatility(closes, 30) == 0.0


def test_compute_indicators_drawdown_from_high():
    closes = pd.Series([100.0] * 250 + [80.0])
    history = pd.DataFrame({"Close": closes})
    indicators = compute_indicators(history)

    assert indicators.price == 80.0
    assert indicators.high_52wk == 100.0
    assert indicators.drawdown_from_high_pct == -20.0
