"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Module: snapshot_divergence_plot.py
Author: Jules 03
Date: 2025-07-18
Description: Provides a snapshot divergence visualizer.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

# LUKHAS_TAG: drift_visualization


def plot_snapshot_drift_overlay(
    dream_id: str,
    snapshot_dir="snapshots",
    redirect_log_path="dream/logs/redirect_log.jsonl",
    output_dir="trace/viz",
):
    """
    Plots snapshot drift overlay for a given dream.
    """
    snapshot_path = Path(snapshot_dir) / f"{dream_id}.json"
    if not snapshot_path.exists():
        print(f"Snapshot file not found at {snapshot_path}")
        return

    with open(snapshot_path) as f:
        snapshots = json.load(f)

    redirect_log_path = Path(redirect_log_path)
    if not redirect_log_path.exists():
        print(f"Redirect log file not found at {redirect_log_path}")
        redirects = []
    else:
        with open(redirect_log_path) as f:
            redirects = [json.loads(line) for line in f]

    timestamps = [snapshot["timestamp"] for snapshot in snapshots]
    drift_scores = [snapshot.get("drift_score", 0) for snapshot in snapshots]

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, drift_scores, label="Drift Score")
    plt.axhline(y=0.5, color="r", linestyle="--", label="Redirect Threshold")

    for redirect in redirects:
        if redirect["snapshot_id"] == dream_id:
            plt.axvline(
                x=redirect["timestamp"], color="r", linestyle="--", label="Redirect"
            )
            plt.text(
                redirect["timestamp"],
                redirect["drift_score"],
                redirect["severity"],
                color="red",
            )

    plt.xlabel("Time")
    plt.ylabel("Score")
    plt.title(f"Snapshot Drift Overlay for Dream {dream_id}")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path / f"{dream_id}_drift_overlay.svg")
    plt.show()
