from quant_app.analysis import PositionAnalysis
from quant_app.config import Thresholds
from quant_app.indicators import Indicators
from quant_app.rules import Action, decide

THRESHOLDS = Thresholds(
    drift_pct=5.0,
    rsi_overbought=70,
    rsi_oversold=30,
    drawdown_pct=15.0,
    take_profit_pct=20.0,
)


def _position(**overrides) -> PositionAnalysis:
    defaults = dict(
        ticker="XYZ",
        shares=10,
        price=100.0,
        market_value=1000.0,
        cost_basis_total=900.0,
        unrealized_pl=100.0,
        unrealized_pl_pct=11.1,
        current_weight=0.20,
        target_weight=0.20,
        drift_pct=0.0,
    )
    defaults.update(overrides)
    return PositionAnalysis(**defaults)


def _indicators(**overrides) -> Indicators:
    defaults = dict(
        price=100.0,
        sma50=None,
        sma200=None,
        rsi14=50.0,
        high_52wk=100.0,
        low_52wk=80.0,
        drawdown_from_high_pct=0.0,
        volatility_pct=None,
    )
    defaults.update(overrides)
    return Indicators(**defaults)


def test_stop_loss_takes_precedence_over_everything():
    position = _position(drift_pct=10.0)  # also overweight
    indicators = _indicators(drawdown_from_high_pct=-20.0, rsi14=80.0)  # also overbought

    decision = decide(position, indicators, THRESHOLDS)

    assert decision.action == Action.SELL
    assert any("stop-loss" in r.lower() for r in decision.reasons)


def test_overweight_triggers_rebalance_trim():
    position = _position(drift_pct=8.0)
    indicators = _indicators()

    decision = decide(position, indicators, THRESHOLDS)

    assert decision.action == Action.REBALANCE_TRIM


def test_underweight_triggers_rebalance_buy():
    position = _position(drift_pct=-8.0)
    indicators = _indicators()

    decision = decide(position, indicators, THRESHOLDS)

    assert decision.action == Action.REBALANCE_BUY


def test_overbought_rsi_triggers_trim():
    position = _position()
    indicators = _indicators(rsi14=75.0)

    decision = decide(position, indicators, THRESHOLDS)

    assert decision.action == Action.TRIM


def test_oversold_rsi_triggers_buy():
    position = _position()
    indicators = _indicators(rsi14=20.0)

    decision = decide(position, indicators, THRESHOLDS)

    assert decision.action == Action.BUY


def test_no_signals_triggers_hold():
    position = _position()
    indicators = _indicators()

    decision = decide(position, indicators, THRESHOLDS)

    assert decision.action == Action.HOLD
    assert "No signals triggered" in decision.reasons
