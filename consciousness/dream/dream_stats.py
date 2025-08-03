#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Dream Stats

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Module for dream stats functionality

For more information, visit: https://lukhas.ai
"""

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
    with open(LOG_PATH, "r", encoding="utf-8") as f:
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
        "dreams_by_phase": dict(by_phase)
    }

    return summary

if __name__ == "__main__":
    from pprint import pprint
    pprint(summarize_dreams())








# Last Updated: 2025-06-05 09:37:28
