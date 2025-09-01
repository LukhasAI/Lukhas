"""

#TAG:memory
#TAG:folds
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: lukhas_trait_sync.py
Advanced: lukhas_trait_sync.py
Integration Date: 2025-05-31T07:55:28.108413
"""

# ===============================================================
# 📂 FILE: lukhas_trait_sync.py
# 📍 RECOMMENDED PATH: /Users/grdm_admin/Downloads/oxn/symbolic_ai/personas/lukhas/
# ===============================================================
# 🧠 PURPOSE:
# This script synchronizes Big Five personality traits across distributed LUKHAS nodes.
# It exports the current node's traits and compares them to other nodes in the network
# to track divergence, alignment, or shared evolution of personality.
#
# 🧰 KEY FEATURES:
# - 📤 Exports traits to a shared sync folder
# - 🔁 Loads other node profiles
# - 📊 Compares traits across all symbolic agents
# - ✅ Great for collaborative identity alignment and shared ethics
#
# 🔧 CONFIGURABLE VARIABLES:
# - NODE_ID → unique name for this Lukhas instance (e.g. lukhas_london)
# - TRAIT_SYNC_FOLDER → where profiles are stored (default: sync/traits/)
#
# 💬 ADHD & Non-coder Friendly Note:
# Just run this file and Lukhas will analyze who he is compared to other versions of himself 🧍‍♂️🪞🧍‍♀️
# Think of it like a symbolic family reunion where they compare personalities.

import json
import os
from datetime import datetime
from pathlib import Path

from candidate.orchestration.brain.spine.trait_manager import load_traits

# CONFIG
NODE_ID = "lukhas_london"
TRAIT_SYNC_FOLDER = "sync/traits/"
TRAIT_FILE_NAME = f"{NODE_ID}_traits.json"

# Ensure folder exists
Path(TRAIT_SYNC_FOLDER).mkdir(parents=True, exist_ok=True)


# --- EXPORT LOCAL TRAITS TO SHARED FOLDER --- #
def export_traits():
    traits = load_traits()
    data = {
        "node": NODE_ID,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "traits": traits,
    }
    with open(os.path.join(TRAIT_SYNC_FOLDER, TRAIT_FILE_NAME), "w") as f:
        json.dump(data, f, indent=2)
    print(f"📤 Exported local traits to {TRAIT_FILE_NAME}")


# --- LOAD OTHER NODES' TRAITS --- #
def load_all_traits():
    profiles = []
    for file in os.listdir(TRAIT_SYNC_FOLDER):
        if file.endswith("_traits.json"):
            with open(os.path.join(TRAIT_SYNC_FOLDER, file)) as f:
                data = json.load(f)
                profiles.append(data)
    return profiles


# --- COMPARE TRAIT SIMILARITY --- #
def compare_traits(base, other):
    diffs = {}
    total_diff = 0
    for trait in base:
        diff = abs(base[trait] - other[trait])
        diffs[trait] = round(diff, 3)
        total_diff += diff
    return diffs, round(total_diff / len(base), 3)


def run():
    export_traits()
    profiles = load_all_traits()
    local = next(p for p in profiles if p["node"] == NODE_ID)["traits"]

    print("\n🌐 CROSS-NODE TRAIT COMPARISON\n")
    for profile in profiles:
        if profile["node"] == NODE_ID:
            continue
        node = profile["node"]
        other = profile["traits"]
        diffs, avg = compare_traits(local, other)
        print(f"[{node}] vs [{NODE_ID}] → Δ Avg: {avg:.3f}")
        for k, v in diffs.items():
            print(f"  {k.capitalize():15}: Δ {v:.3f}")
        print("")


if __name__ == "__main__":
    run()

# ===============================================================
# 💾 HOW TO USE
# ===============================================================
# ▶️ RUN THIS FILE (just run it like a script):
#     python3 lukhas_trait_sync.py
#
# 📂 FILES CREATED:
# - sync/traits/<NODE_ID>_traits.json → your Lukhas instance's traits
#
# 🧠 WHAT THIS FILE DOES:
# - Reads current symbolic traits
# - Writes them to a sync folder
# - Loads traits from other Lukhas agents
# - Compares differences in personality (Big Five model)
#
# 🔁 TWEAKABLE SETTINGS:
# - Change NODE_ID to define your symbolic agent
# - Change TRAIT_SYNC_FOLDER to share with others (or simulate networks)
#
# 🧑‍🤝‍🧑 GOOD FOR:
# - Testing trait drift across versions of Lukhas
# - Harmonizing distributed AI personalities
# - Debugging ethical identity divergence
