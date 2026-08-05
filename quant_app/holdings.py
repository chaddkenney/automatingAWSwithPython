"""Load and validate the manually-maintained holdings CSV."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class Holding:
    ticker: str
    shares: float
    cost_basis: float  # price paid per share
    purchase_date: date


def load_holdings(path: str | Path) -> list[Holding]:
    path = Path(path)
    holdings = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        required = {"ticker", "shares", "cost_basis", "purchase_date"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

        for row in reader:
            holdings.append(
                Holding(
                    ticker=row["ticker"].strip().upper(),
                    shares=float(row["shares"]),
                    cost_basis=float(row["cost_basis"]),
                    purchase_date=date.fromisoformat(row["purchase_date"].strip()),
                )
            )

    if not holdings:
        raise ValueError(f"{path} contains no holdings")

    return holdings
