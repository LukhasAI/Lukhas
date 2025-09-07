"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dream_stats.py
Advanced: dream_stats.py
Integration Date: 2025-05-31T07:55:28.210445
"""
import streamlit as st

"""
dream_stats.py
--------------
Provides summary statistics over symbolic dreams stored in dream_log.jsonl.
"""

import json
import os
from collections import defaultdict

LOG_PATH = "data/dream_log.jsonl"


def load_dreams():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


def summarize_dreams():
    dreams = load_dreams()
    if not dreams:
        return "No dreams to summarize."

    total = len(dreams)
    collapses = sum(1 for d in dreams if d.get("collapse_id"))
    resonance_vals = [d.get("resonance", 0.0) for d in dreams]
    avg_resonance = sum(resonance_vals) / len(resonance_vals) if resonance_vals else 0.0

    by_phase = defaultdict(int)
    for d in dreams:
        phase = d.get("phase", "unknown")
        by_phase[phase] += 1

    summary = {
        "total_dreams": total,
        "dreams_with_collapse": collapses,
        "average_resonance": round(avg_resonance, 3),
        "dreams_by_phase": dict(by_phase),
    }

    return summary


if __name__ == "__main__":
    from pprint import pprint

    pprint(summarize_dreams())
