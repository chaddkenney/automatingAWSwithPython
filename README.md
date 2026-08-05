# automatingAWSwithPython

A daily portfolio quant app: tracks a manually-maintained list of stock/ETF
holdings, evaluates them against trend, momentum, drawdown, and
allocation-drift rules, and writes a Markdown report recommending an action
(BUY / TRIM / SELL / HOLD / REBALANCE) per holding. It does not place any
trades — it's an analysis and alerting tool.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configure

1. Edit `config/holdings.csv` with your actual positions:
   `ticker,shares,cost_basis,purchase_date`
2. Edit `config/config.yaml`:
   - `target_allocations`: your target weight per ticker (must sum to 1.0)
   - `thresholds`: how aggressive the rebalance/momentum/stop-loss signals are

## Run

```bash
python -m quant_app.cli
```

This prints a summary table to the console and writes
`reports/report_YYYY-MM-DD.md`. Prices are cached under `.cache/` for the
day so re-running doesn't re-hit Yahoo Finance.

Optional flags: `--holdings`, `--config`, `--reports-dir` to point at
different files.

## Run it daily

Add a cron entry to run after US market close (e.g. 5pm ET / 21:00 UTC on
weekdays):

```cron
0 21 * * 1-5 cd /path/to/automatingAWSwithPython && /path/to/venv/bin/python -m quant_app.cli >> reports/cli.log 2>&1
```

## Tests

```bash
pytest
```

## How the decision engine works

For each holding (`quant_app/rules.py`), signals are evaluated in this
priority order — the first one triggered sets the action, and all triggered
signals are listed as reasons:

1. **Stop-loss**: price down more than `drawdown_pct` from its 52-week high → `SELL` (flagged for manual review)
2. **Allocation drift**: current weight vs. target off by more than `drift_pct` → `REBALANCE_TRIM` / `REBALANCE_BUY`
3. **Momentum**: RSI14 overbought/oversold (and take-profit when overbought + large gain) → `TRIM` / `BUY`
4. Otherwise → `HOLD`

Trend context (SMA50 vs SMA200) is included as an informational reason but
doesn't drive the action by itself.

Not built yet, but straightforward to add later: email/Slack delivery of
the report, AWS deployment (Lambda + EventBridge), and brokerage API
integration for automatic position sync or order placement.
