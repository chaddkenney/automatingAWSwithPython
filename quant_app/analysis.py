"""Portfolio-level math: market values, weights vs target, unrealized P/L, drift."""
from __future__ import annotations

from dataclasses import dataclass

from quant_app.config import Config
from quant_app.holdings import Holding


@dataclass
class PositionAnalysis:
    ticker: str
    shares: float
    price: float
    market_value: float
    cost_basis_total: float
    unrealized_pl: float
    unrealized_pl_pct: float
    current_weight: float
    target_weight: float
    drift_pct: float  # current_weight - target_weight, in percentage points


@dataclass
class PortfolioSummary:
    total_value: float
    total_cost_basis: float
    total_unrealized_pl: float
    total_unrealized_pl_pct: float


def analyze_portfolio(
    holdings: list[Holding], prices: dict[str, float], config: Config
) -> tuple[list[PositionAnalysis], PortfolioSummary]:
    market_values = {h.ticker: h.shares * prices[h.ticker] for h in holdings}
    total_value = sum(market_values.values())

    positions = []
    for h in holdings:
        price = prices[h.ticker]
        market_value = market_values[h.ticker]
        cost_basis_total = h.shares * h.cost_basis
        unrealized_pl = market_value - cost_basis_total
        unrealized_pl_pct = (
            (unrealized_pl / cost_basis_total * 100) if cost_basis_total else 0.0
        )
        current_weight = market_value / total_value if total_value else 0.0
        target_weight = config.target_weight(h.ticker)

        positions.append(
            PositionAnalysis(
                ticker=h.ticker,
                shares=h.shares,
                price=price,
                market_value=market_value,
                cost_basis_total=cost_basis_total,
                unrealized_pl=unrealized_pl,
                unrealized_pl_pct=unrealized_pl_pct,
                current_weight=current_weight,
                target_weight=target_weight,
                drift_pct=(current_weight - target_weight) * 100,
            )
        )

    total_cost_basis = sum(p.cost_basis_total for p in positions)
    total_unrealized_pl = total_value - total_cost_basis
    total_unrealized_pl_pct = (
        (total_unrealized_pl / total_cost_basis * 100) if total_cost_basis else 0.0
    )

    summary = PortfolioSummary(
        total_value=total_value,
        total_cost_basis=total_cost_basis,
        total_unrealized_pl=total_unrealized_pl,
        total_unrealized_pl_pct=total_unrealized_pl_pct,
    )

    return positions, summary
