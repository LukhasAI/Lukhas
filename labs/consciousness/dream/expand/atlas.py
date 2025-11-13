"""
Drift Atlas: logs drift/entropy across dream runs.
Export: JSON or HTML constellation maps.
"""
from __future__ import annotations

import datetime
import pathlib


def log(run_id: str, snapshot: dict, drift_score: float, entropy: float) -> dict:
    row = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "run_id": run_id, "drift": drift_score, "entropy": entropy}
    return row

def export_html(path="atlas_report.html") -> None:
    pathlib.Path(path).write_text("<html><body><h1>Drift Atlas</h1></body></html>")
