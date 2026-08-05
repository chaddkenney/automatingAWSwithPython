"""Daily entrypoint: load holdings/config, fetch prices, analyze, decide, report."""
from __future__ import annotations

import argparse
from datetime import date

from quant_app.analysis import analyze_portfolio
from quant_app.config import load_config
from quant_app.data import get_price_history
from quant_app.holdings import load_holdings
from quant_app.indicators import compute_indicators
from quant_app.report import render_console, write_report
from quant_app.rules import decide


def run(holdings_path: str, config_path: str, reports_dir: str) -> None:
    holdings = load_holdings(holdings_path)
    config = load_config(config_path)
    report_date = date.today()

    histories = {h.ticker: get_price_history(h.ticker, report_date) for h in holdings}
    indicators = {ticker: compute_indicators(hist) for ticker, hist in histories.items()}
    prices = {ticker: ind.price for ticker, ind in indicators.items()}

    positions, summary = analyze_portfolio(holdings, prices, config)
    decisions = {
        p.ticker: decide(p, indicators[p.ticker], config.thresholds) for p in positions
    }

    render_console(positions, indicators, decisions, summary)
    out_path = write_report(reports_dir, report_date, positions, indicators, decisions, summary)
    print(f"\nReport written to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the daily portfolio quant check.")
    parser.add_argument("--holdings", default="config/holdings.csv")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--reports-dir", default="reports")
    args = parser.parse_args()

    run(args.holdings, args.config, args.reports_dir)


if __name__ == "__main__":
    main()
