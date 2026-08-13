"""Local web dashboard: view today's portfolio actions and past reports in a browser."""
from __future__ import annotations

import re
from pathlib import Path

from flask import Flask, abort, render_template

from quant_app.pipeline import compute_daily
from quant_app.report import sorted_by_priority
from quant_app.rules import Action

BADGE_CLASS = {
    Action.SELL: "badge-critical",
    Action.TRIM: "badge-serious",
    Action.REBALANCE_TRIM: "badge-serious",
    Action.REBALANCE_BUY: "badge-warning",
    Action.BUY: "badge-good",
    Action.HOLD: "badge-neutral",
}

REPORT_FILENAME_RE = re.compile(r"^report_\d{4}-\d{2}-\d{2}\.md$")


def create_app(
    holdings_path: str = "config/holdings.csv",
    config_path: str = "config/config.yaml",
    reports_dir: str = "reports",
) -> Flask:
    app = Flask(__name__)
    reports_path = Path(reports_dir)

    @app.route("/")
    def dashboard():
        try:
            result = compute_daily(holdings_path, config_path)
        except Exception as exc:  # noqa: BLE001 - surface any load/fetch failure to the page
            return render_template("error.html", active="dashboard", message=str(exc)), 500

        actionable_count = sum(
            1 for d in result.decisions.values() if d.action != Action.HOLD
        )
        return render_template(
            "dashboard.html",
            active="dashboard",
            result=result,
            sorted_positions=sorted_by_priority(result.positions, result.decisions),
            badge_class=BADGE_CLASS,
            actionable_count=actionable_count,
        )

    @app.route("/history")
    def history():
        reports_path.mkdir(parents=True, exist_ok=True)
        filenames = sorted(
            (p.name for p in reports_path.glob("report_*.md")), reverse=True
        )
        return render_template("history.html", active="history", reports=filenames)

    @app.route("/history/<filename>")
    def history_detail(filename: str):
        if not REPORT_FILENAME_RE.match(filename):
            abort(404)
        file_path = reports_path / filename
        if not file_path.is_file():
            abort(404)
        return render_template(
            "history_detail.html",
            active="history",
            filename=filename,
            content=file_path.read_text(),
        )

    return app


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run the portfolio quant web dashboard.")
    parser.add_argument("--holdings", default="config/holdings.csv")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    app = create_app(args.holdings, args.config, args.reports_dir)
    app.run(host="127.0.0.1", port=args.port, debug=False)


if __name__ == "__main__":
    main()
