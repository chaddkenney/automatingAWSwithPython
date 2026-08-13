"""Daily entrypoint: load holdings/config, fetch prices, analyze, decide, report."""
from __future__ import annotations

import argparse

from quant_app.pipeline import compute_daily
from quant_app.report import render_console, write_report


def run(holdings_path: str, config_path: str, reports_dir: str) -> None:
    result = compute_daily(holdings_path, config_path)

    render_console(result.positions, result.indicators, result.decisions, result.summary)
    out_path = write_report(
        reports_dir,
        result.report_date,
        result.positions,
        result.indicators,
        result.decisions,
        result.summary,
    )
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
