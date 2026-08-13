"""Shared orchestration: load holdings/config, fetch prices, analyze, decide.

Used by both the CLI (quant_app.cli) and the web dashboard (quant_app.webapp)
so the two never compute results differently.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from quant_app.analysis import PortfolioSummary, PositionAnalysis, analyze_portfolio
from quant_app.config import load_config
from quant_app.data import get_price_history
from quant_app.holdings import load_holdings
from quant_app.indicators import Indicators, compute_indicators
from quant_app.rules import Decision, decide


@dataclass
class DailyResult:
    report_date: date
    positions: list[PositionAnalysis]
    indicators: dict[str, Indicators]
    decisions: dict[str, Decision]
    summary: PortfolioSummary


def compute_daily(
    holdings_path: str, config_path: str, as_of: date | None = None
) -> DailyResult:
    holdings = load_holdings(holdings_path)
    config = load_config(config_path)
    report_date = as_of or date.today()

    histories = {h.ticker: get_price_history(h.ticker, report_date) for h in holdings}
    indicators = {ticker: compute_indicators(hist) for ticker, hist in histories.items()}
    prices = {ticker: ind.price for ticker, ind in indicators.items()}

    positions, summary = analyze_portfolio(holdings, prices, config)
    decisions = {
        p.ticker: decide(p, indicators[p.ticker], config.thresholds) for p in positions
    }

    return DailyResult(
        report_date=report_date,
        positions=positions,
        indicators=indicators,
        decisions=decisions,
        summary=summary,
    )
