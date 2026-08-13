"""Decision engine: combine indicators + portfolio analysis into a per-holding action."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from quant_app.analysis import PositionAnalysis
from quant_app.config import Thresholds
from quant_app.indicators import Indicators


class Action(str, Enum):
    SELL = "SELL"
    REBALANCE_TRIM = "REBALANCE_TRIM"
    REBALANCE_BUY = "REBALANCE_BUY"
    TRIM = "TRIM"
    BUY = "BUY"
    HOLD = "HOLD"


@dataclass
class Decision:
    ticker: str
    action: Action
    reasons: list[str] = field(default_factory=list)


def decide(
    position: PositionAnalysis, indicators: Indicators, thresholds: Thresholds
) -> Decision:
    reasons: list[str] = []

    # Trend context (informational, always recorded when data is available).
    if indicators.sma50 is not None and indicators.sma200 is not None:
        if indicators.sma50 < indicators.sma200 and indicators.price < indicators.sma200:
            reasons.append("Bearish trend: price and SMA50 below SMA200")
        elif indicators.sma50 > indicators.sma200 and indicators.price > indicators.sma200:
            reasons.append("Bullish trend: price and SMA50 above SMA200")

    stop_loss_triggered = (
        indicators.drawdown_from_high_pct <= -thresholds.drawdown_pct
    )
    if stop_loss_triggered:
        reasons.append(
            f"Down {indicators.drawdown_from_high_pct:.1f}% from 52-week high "
            f"(stop-loss threshold: -{thresholds.drawdown_pct:.1f}%) — review for exit"
        )

    overweight = position.drift_pct > thresholds.drift_pct
    underweight = position.drift_pct < -thresholds.drift_pct
    if overweight:
        reasons.append(
            f"Overweight target by {position.drift_pct:.1f}pp "
            f"({position.current_weight * 100:.1f}% vs {position.target_weight * 100:.1f}% target)"
        )
    elif underweight:
        reasons.append(
            f"Underweight target by {abs(position.drift_pct):.1f}pp "
            f"({position.current_weight * 100:.1f}% vs {position.target_weight * 100:.1f}% target)"
        )

    overbought = (
        indicators.rsi14 is not None and indicators.rsi14 >= thresholds.rsi_overbought
    )
    oversold = (
        indicators.rsi14 is not None and indicators.rsi14 <= thresholds.rsi_oversold
    )
    if overbought:
        reasons.append(f"RSI14 overbought at {indicators.rsi14:.0f}")
    elif oversold:
        reasons.append(f"RSI14 oversold at {indicators.rsi14:.0f}")

    take_profit = (
        position.unrealized_pl_pct >= thresholds.take_profit_pct and overbought
    )
    if take_profit:
        reasons.append(
            f"Up {position.unrealized_pl_pct:.1f}% with overbought RSI — take-profit candidate"
        )

    # Precedence: stop-loss > rebalance > momentum/take-profit > hold.
    if stop_loss_triggered:
        action = Action.SELL
    elif overweight:
        action = Action.REBALANCE_TRIM
    elif underweight:
        action = Action.REBALANCE_BUY
    elif take_profit or overbought:
        action = Action.TRIM
    elif oversold:
        action = Action.BUY
    else:
        action = Action.HOLD
        reasons.append("No signals triggered")

    return Decision(ticker=position.ticker, action=action, reasons=reasons)
