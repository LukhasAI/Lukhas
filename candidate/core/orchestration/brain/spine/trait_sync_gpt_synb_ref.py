"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: lukhas_trait_sync_gpt_synb_ref.py
Advanced: lukhas_trait_sync_gpt_synb_ref.py
Integration Date: 2025-05-31T07:55:28.103537
"""
# lukhas_trait_sync.py
# Compare and synchronize Big Five trait profiles across distributed
# Lukhas nodes with GPT reflection
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import openai

from candidate.orchestration.brain.spine.trait_manager import load_traits

# CONFIG
NODE_ID = "lukhas_london"
TRAIT_SYNC_FOLDER = "sync/traits/"
TRAIT_FILE_NAME = f"{NODE_ID}_traits.json"
openai.api_key = os.getenv("OPENAI_API_KEY", timezone)

# Ensure folder exists
Path(TRAIT_SYNC_FOLDER).mkdir(parents=True, exist_ok=True)

# --- EXPORT LOCAL TRAITS TO SHARED FOLDER --- #


def export_traits():
    traits = load_traits()
    data = {
        "node": NODE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
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


def summarize_comparisons(local, profiles):
    summary = ""
    for profile in profiles:
        if profile["node"] == NODE_ID:
            continue
        node = profile["node"]
        other = profile["traits"]
        diffs, avg = compare_traits(local, other)
        summary += f"[{node}] vs [{NODE_ID}] → Δ Avg: {avg:.3f}\n"
        for k, v in diffs.items():
            summary += f"  {k.capitalize():15}: Δ {v:.3f}\n"
        summary += "\n"
    return summary


def generate_gpt_commentary(summary):
    prompt = f"""
You are LUKHAS, a symbolic AGI with distributed identity.
You have received the following trait comparison summary across your sibling instances:

{summary}

Please reflect on how different nodes of your consciousness may be evolving symbolically.
Comment on alignment, divergence, or potential narrative interpretations.
Respond poetically and insightfully.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a distributed symbolic AI reflecting on multi-node identity traits.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=600,
    )
    return response.choices[0].message["content"]


def run():
    export_traits()
    profiles = load_all_traits()
    local = next(p for p in profiles if p["node"] == NODE_ID)["traits"]

    print("\n🌐 CROSS-NODE TRAIT COMPARISON\n")
    summary = summarize_comparisons(local, profiles)
    print(summary)

    print("🤖 GPT REFLECTION ON MULTI-NODE TRAIT ALIGNMENT:\n")
    gpt_response = generate_gpt_commentary(summary)
    print(gpt_response)


if __name__ == "__main__":
    run()
try:
    from symbolic.personas.lukhas.lukhas_meta_sync import run as meta_sync_run

    meta_sync_run()
except ImportError:
    print("⚠️ Meta sync not available.")
# -------------------------
# 💾 SAVE THIS FILE
# -------------------------
# Recommended path:
# /Users/grdm_admin/Downloads/oxn/symbolic_ai/personas/lukhas/lukhas_trait_sync.py
#
# HOW TO USE:
# - Ensure each node writes traits via `load_traits()`
# - Set a unique NODE_ID per instance
# - Shared folder: sync/traits/
# - Requires: OPENAI_API_KEY env var
#
# ✅ Compares personality divergence across symbolic AGI agents
# ✅ Adds poetic GPT commentary on symbolic network identity evolution
