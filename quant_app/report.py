"""Render the daily portfolio report as Markdown and as a console table."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from rich.console import Console
from rich.table import Table

from quant_app.analysis import PositionAnalysis, PortfolioSummary
from quant_app.indicators import Indicators
from quant_app.rules import Action, Decision

# Lower number = higher priority in the report ordering.
_ACTION_PRIORITY = {
    Action.SELL: 0,
    Action.REBALANCE_TRIM: 1,
    Action.REBALANCE_BUY: 2,
    Action.TRIM: 3,
    Action.BUY: 4,
    Action.HOLD: 5,
}


def _sorted_rows(
    positions: list[PositionAnalysis], decisions: dict[str, Decision]
) -> list[PositionAnalysis]:
    return sorted(
        positions, key=lambda p: _ACTION_PRIORITY[decisions[p.ticker].action]
    )


def render_markdown(
    report_date: date,
    positions: list[PositionAnalysis],
    indicators: dict[str, Indicators],
    decisions: dict[str, Decision],
    summary: PortfolioSummary,
) -> str:
    lines = [
        f"# Portfolio Report — {report_date.isoformat()}",
        "",
        "## Summary",
        f"- Total value: ${summary.total_value:,.2f}",
        f"- Total cost basis: ${summary.total_cost_basis:,.2f}",
        f"- Unrealized P/L: ${summary.total_unrealized_pl:,.2f} "
        f"({summary.total_unrealized_pl_pct:+.1f}%)",
        "",
        "## Actions",
        "",
        "| Ticker | Action | Price | Weight (tgt) | P/L % | RSI14 | Reasons |",
        "|---|---|---|---|---|---|---|",
    ]

    for p in _sorted_rows(positions, decisions):
        ind = indicators[p.ticker]
        d = decisions[p.ticker]
        rsi_str = f"{ind.rsi14:.0f}" if ind.rsi14 is not None else "n/a"
        reasons = "; ".join(d.reasons)
        lines.append(
            f"| {p.ticker} | {d.action.value} | ${p.price:,.2f} | "
            f"{p.current_weight * 100:.1f}% ({p.target_weight * 100:.1f}%) | "
            f"{p.unrealized_pl_pct:+.1f}% | {rsi_str} | {reasons} |"
        )

    return "\n".join(lines) + "\n"


def render_console(
    positions: list[PositionAnalysis],
    indicators: dict[str, Indicators],
    decisions: dict[str, Decision],
    summary: PortfolioSummary,
) -> None:
    console = Console()
    console.print(
        f"Total value: ${summary.total_value:,.2f}  "
        f"P/L: ${summary.total_unrealized_pl:,.2f} ({summary.total_unrealized_pl_pct:+.1f}%)"
    )

    table = Table()
    for column in ("Ticker", "Action", "Price", "Weight (tgt)", "P/L %", "RSI14", "Reasons"):
        table.add_column(column)

    for p in _sorted_rows(positions, decisions):
        ind = indicators[p.ticker]
        d = decisions[p.ticker]
        rsi_str = f"{ind.rsi14:.0f}" if ind.rsi14 is not None else "n/a"
        table.add_row(
            p.ticker,
            d.action.value,
            f"${p.price:,.2f}",
            f"{p.current_weight * 100:.1f}% ({p.target_weight * 100:.1f}%)",
            f"{p.unrealized_pl_pct:+.1f}%",
            rsi_str,
            "; ".join(d.reasons),
        )

    console.print(table)


def write_report(
    report_dir: str | Path,
    report_date: date,
    positions: list[PositionAnalysis],
    indicators: dict[str, Indicators],
    decisions: dict[str, Decision],
    summary: PortfolioSummary,
) -> Path:
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    out_path = report_dir / f"report_{report_date.isoformat()}.md"
    out_path.write_text(
        render_markdown(report_date, positions, indicators, decisions, summary)
    )
    return out_path
