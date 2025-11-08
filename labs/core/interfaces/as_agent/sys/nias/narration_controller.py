"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: narration_controller.py
Advanced: narration_controller.py
Integration Date: 2025-05-31T07:55:30.566718
"""
from __future__ import annotations

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                        LUCΛS :: Narration Controller                        │
│            Module: narration_controller.py | Tier 3+ | Version 1.0          │
│      Coordinates symbolic voice narration logic and replay permissions      │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This module routes symbolic dream entries to the correct voice handler,
    manages narrator queues, and applies replay/narration filters based on:
    - Tier permissions
    - Emotional priority
    - Consent & config from system_user_config.json

DEPENDENCIES:
    - voice_narrator.py
    - dream_narrator_queue.py
    - lukhas_user_config.json
"""

import json
from pathlib import Path

QUEUE_PATH = Path("core/logs/narration_queue.jsonl")
CONFIG_PATH = Path("core/utils/lukhas_user_config.json")


def load_user_settings():
    try:
        with open(CONFIG_PATH) as cfg:
            return json.load(cfg).get("lukhas_user_profile", {})
    except Exception:
        return {}


def filter_narration_queue(entries, tier_threshold=3):
    return [
        e
        for e in entries
        if e.get("tier", 0) >= tier_threshold and e.get("suggest_voice", False)
    ]


def fetch_narration_entries():
    if not QUEUE_PATH.exists():
        print("⚠️ No narration queue found.")
        return []

    with open(QUEUE_PATH) as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


def print_debug_narration_summary():
    """
    Prints a tier-filtered preview of narration-ready dreams.
    Intended for local debugging or CLI inspection only.
    """
    settings = load_user_settings()
    tier_limit = settings.get("tier", 0)

    entries = fetch_narration_entries()
    filtered = filter_narration_queue(entries, tier_limit)

    print(f"🔊 Narration-ready entries for Tier {tier_limit}: {len(filtered)}")
    for e in filtered:
        print(
            f" • ID: {e.get('id')} | Emoji: {e.get('emoji')} | Tags: {','.join(e.get('tags', []))}"
        )
        print(f"   📝 Summary: {e.get('summary', '-')}")
        print()

if __name__ == "__main__":
    print_debug_narration_summary()

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│ USAGE:                                                                       │
│   python core/modules/nias/narration_controller.py                          │
│ OUTPUT:                                                                      │
│   Narration entries filtered by tier + suggest_voice flag                   │
╰──────────────────────────────────────────────────────────────────────────────╯
"""