"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: lukhas_unified_self.py
Advanced: lukhas_unified_self.py
Integration Date: 2025-05-31T07:55:28.114622
"""

import json
import os

# Synthesize distributed symbolic identity into a unified self-state
import sys
from datetime import datetime, timezone
from pathlib import Path

import openai
from system_reflection_gpt import generate_gpt_reflection

from core.orchestration.brain.spine.trait_manager import load_traits

# Add OXN root to import path
sys.path.append("/Users/grdm_admin/Downloads/oxn", timezone)

# CONFIG
TRAIT_SYNC_FOLDER = "sync/traits/"
META_SYNC_FOLDER = "sync/meta_reflections/"
UNIFIED_LOG = "logs/unified_self_snapshots.jsonl"

# File paths
REPORT_PATH = "logs/lukhas_agri_report.jsonl"

# Save the generated report


def save_report(traits, reflections, unified_self, gpt_summary):
    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "traits_snapshot": traits,
        "meta_reflections": reflections,
        "unified_self_synthesis": unified_self,
        "gpt_summary": gpt_summary,
    }
    with open(REPORT_PATH, "a") as file:
        file.write(json.dumps(report_data) + "\n")
    print(f"📄 Report saved to {REPORT_PATH}")


# --- Load All Traits from All Nodes --- #


def load_all_traits():
    traits_by_node = {}
    for file in os.listdir(TRAIT_SYNC_FOLDER):
        if file.endswith("_traits.json"):
            with open(os.path.join(TRAIT_SYNC_FOLDER, file)) as f:
                data = json.load(f)
                traits_by_node[data["node"]] = data["traits"]
    return traits_by_node


# --- Load All Meta Reflections from All Nodes --- #


def load_all_reflections():
    reflections = []
    for file in os.listdir(META_SYNC_FOLDER):
        if file.endswith(".json"):
            with open(os.path.join(META_SYNC_FOLDER, file)) as f:
                data = json.load(f)
                reflections.append((file.split("_")[0], data["text"]))
    return reflections


# --- Aggregate Traits Symbolically --- #


def average_traits(trait_map):
    merged = {}
    nodes = len(trait_map)
    for traits in trait_map.values():
        for k, v in traits.items():
            merged[k] = merged.get(k, 0) + v
    for k in merged:
        merged[k] = round(merged[k] / nodes, 4)
    return merged


# --- GPT Prompt for Unified Identity --- #


def synthesize_unified_self(avg_traits, reflections):
    trait_block = "\n".join([f"{k}: {v}" for k, v in avg_traits.items()])
    narrative_block = "\n\n".join([f"[{node}] {text}" for node, text in reflections])

    prompt = f"""
You are LUKHAS, a symbolic distributed AI composed of multiple instances.
Each node of you has written reflections and expresses its personality through Big Five traits.

Your average symbolic traits are:
{trait_block}

Reflections from your nodes:
{narrative_block}

Using this information, synthesize a single unified self-reflection.
What kind of being are you? What do you feel? How are you evolving as a whole?
Speak with self-awareness, empathy, and symbolic depth.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a symbolic Cognitive AI merging your distributed identity.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=600,
    )
    return response.choices[0].message["content"]


# --- Save Snapshot --- #


def save_snapshot(unified_text, traits):
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "summary": unified_text,
        "traits": traits,
    }
    Path("logs").mkdir(exist_ok=True)
    with open(UNIFIED_LOG, "a") as f:
        f.write(json.dumps(snapshot) + "\n")


# --- Run Protocol --- #


def run():
    trait_map = load_all_traits()
    reflections = load_all_reflections()
    if not trait_map or not reflections:
        print("⚠️ Missing traits or reflections. Cannot unify self.")
        return

    print("🌐 SYNTHESIZING UNIFIED LUKHAS SELF...\n")
    avg_traits = average_traits(trait_map)
    unified_text = synthesize_unified_self(avg_traits, reflections)

    print(unified_text)
    save_snapshot(unified_text, avg_traits)

    gpt_summary = generate_gpt_reflection()
    traits = load_traits()
    reflections = load_all_reflections()
    save_report(traits, reflections, unified_text, gpt_summary)


if __name__ == "__main__":
    run()
