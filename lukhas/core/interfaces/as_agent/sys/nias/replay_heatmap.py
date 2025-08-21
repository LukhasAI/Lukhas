"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: replay_heatmap.py
Advanced: replay_heatmap.py
Integration Date: 2025-05-31T07:55:30.530721
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                   LUCΛS :: DREAM REPLAY HEATMAP MODULE (v1.0)               │
│                      Subsystem: NIAS | Symbolic Replay Analysis             │
│                      Author: Gonzo R.D.M | April 2025                        │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This script visualizes dream replay activity from replay_queue.jsonl.
    It generates a symbolic heatmap showing the density of dreams by:
    - Tier Level
    - Emotion Vector
    - Source Widget or Tag Category

USAGE:
    Run via CLI:
        python core/modules/nias/replay_heatmap.py

NOTES:
    Requires:
        - replay_queue.jsonl (in core/logs/)
        - matplotlib + seaborn + pandas (for rendering)

"""

import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

LOG_PATH = "core/logs/replay_queue.jsonl"


def load_replay_data():
    if not os.path.exists(LOG_PATH):
        print("❌ replay_queue.jsonl not found.")
        return pd.DataFrame()

    with open(LOG_PATH) as f:
        lines = [json.loads(line) for line in f if line.strip()]

    data = []
    for entry in lines:
        data.append(
            {
                "tier": entry.get("tier", 0),
                "tag": entry.get("tags", ["untagged"])[0],
                "emotion": entry.get("emotion_vector", {}).get("primary", "neutral"),
            }
        )

    return pd.DataFrame(data)


def plot_heatmap(df):
    if df.empty:
        print("📭 No data to visualize.")
        return

    pivot = df.pivot_table(
        index="emotion", columns="tier", aggfunc="size", fill_value=0
    )

    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, cmap="coolwarm", linewidths=0.5)
    plt.title("🌙 LUCΛS Dream Replay Heatmap")
    plt.xlabel("User Tier")
    plt.ylabel("Primary Emotion")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    df = load_replay_data()
    plot_heatmap(df)
