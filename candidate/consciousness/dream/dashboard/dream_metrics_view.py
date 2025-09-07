from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any
from datetime import timezone
import streamlit as st


@dataclass
class DreamMetrics:
    drift_score_delta: float = 0.0
    symbolic_entropy: float = 0.0
    recall_hits: int = 0
    recall_misses: int = 0
    energy_consumption: float = 0.0
    timestamp: str = ""


class DreamMetricsView:
    """# ΛTAG: metrics_view
    Aggregates dream-related metrics for monitoring."""

    def __init__(self, timezone) -> None:
        self.totals = DreamMetrics(timestamp=datetime.now(timezone.utc).isoformat())

    def update_dream_metrics(self, drift_delta: float, entropy: float, energy: float) -> None:
        self.totals.drift_score_delta += drift_delta
        self.totals.symbolic_entropy += entropy
        self.totals.energy_consumption += energy
        self.totals.timestamp = datetime.now(timezone.utc).isoformat()

    def update_memory_metrics(self, hits: int, misses: int) -> None:
        self.totals.recall_hits += hits
        self.totals.recall_misses += misses
        self.totals.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self.totals)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


metrics_view = DreamMetricsView()


def main() -> None:
    parser = argparse.ArgumentParser(description="Dream metrics dashboard")
    parser.add_argument("--json", action="store_true", help="Output metrics as JSON")
    args = parser.parse_args()

    if args.json:
        print(metrics_view.to_json())
    else:
        data = metrics_view.to_dict()
        for k, v in data.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
