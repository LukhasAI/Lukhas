#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Dream Mutator

Copyright (c) 2025 LUKHAS Cognitive AI Development Team
All rights reserved.

This file is part of the LUKHAS Cognitive system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Module for dream mutator functionality

For more information, visit: https://lukhas.ai
"""

# 📄 MODULE: dream_mutator.py
# 🔎 PURPOSE: Mutate symbolic dreams to simulate memory evolution or emotional reinterpretation
# 🛠️ VERSION: v1.0.0 • 📅 CREATED: 2025-04-30 • ✍️ AUTHOR: LUKHAS AI
# 🛠️ VERSION: v1.0.0 • 📅 CREATED: 2025-04-30 • ✍️ AUTHOR: LUKHAS AI

import json
import os
import random
from datetime import datetime, timezone

DREAM_LOG_PATH = "logs/dream_log.jsonl"


def load_latest_dream(path=DREAM_LOG_PATH):
    if not os.path.exists(path):
        print("❌ No dream log found.")
        return None
    with open(path, encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
        return lines[-1] if lines else None


def mutate_emotional_wave(original_wave):
    return [round(min(max(e + random.uniform(-0.3, 0.3), 0.0), 1.0), 2) for e in original_wave]


def mutate_dream(dream):
    mutated = dict(dream)
    mutated["dream_id"] = f"MUT_{dream['dream_id']}"
    mutated["created_at"] = datetime.now(timezone.utc).isoformat() + "Z"
    mutated["emotional_wave"] = mutate_emotional_wave(dream.get("emotional_wave", [0.5] * 5))
    mutated["mutation_of"] = dream["dream_id"]
    mutated["mutation_type"] = "emotional_wave_adjustment"
    return mutated


def save_mutated_dream(dream, path=DREAM_LOG_PATH):
    with open(path, "a", encoding="utf-8") as f:
        json.dump(dream, f)
        f.write("\n")


if __name__ == "__main__":
    original = load_latest_dream()
    if original:
        mutated = mutate_dream(original)
        save_mutated_dream(mutated)
        print(f"🌱 Dream mutated: {mutated['dream_id']} (from {original['dream_id']})")


# Last Updated: 2025-06-05 09:37:28
