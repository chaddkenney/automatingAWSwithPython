"""Load the app's YAML config: target allocations and decision thresholds."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Thresholds:
    drift_pct: float
    rsi_overbought: float
    rsi_oversold: float
    drawdown_pct: float
    take_profit_pct: float


@dataclass
class Config:
    target_allocations: dict[str, float]
    thresholds: Thresholds

    def target_weight(self, ticker: str) -> float:
        return self.target_allocations.get(ticker, 0.0)


def load_config(path: str | Path) -> Config:
    path = Path(path)
    with path.open() as f:
        raw = yaml.safe_load(f)

    target_allocations = {
        ticker: float(weight)
        for ticker, weight in raw.get("target_allocations", {}).items()
    }
    total_weight = sum(target_allocations.values())
    if target_allocations and abs(total_weight - 1.0) > 0.01:
        raise ValueError(
            f"target_allocations in {path} must sum to 1.0, got {total_weight:.4f}"
        )

    thresholds = Thresholds(**raw["thresholds"])

    return Config(target_allocations=target_allocations, thresholds=thresholds)
