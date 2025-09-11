"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: replay_visualizer.py
Advanced: replay_visualizer.py
Integration Date: 2025-05-31T07:55:30.560819
"""
import time
import streamlit as st

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                   LUCΛS :: REPLAY VISUALIZER (SYMBOLIC CLI)                 │
│      Version: v1.0 | Display Symbolic Dream Replays with Emotional Data      │
│            Author: Gonzo R.D.M & GPT-4o | Date: 2025-04-16                   │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    Reads from replay_queue.jsonl and prints a symbolic, color-coded table of
    replay-worthy dreams, with emphasis on calm, tier, source, tags, and emoji.

    Future versions may support bar chart visualization, Streamlit UI,
    or voice-integrated replays.

"""

import json
from collections import Counter
from pathlib import Path

REPLAY_PATH = Path("core/logs/replay_queue.jsonl")

TIER_EMOJI = {"0": "🧪", "1": "🌱", "2": "🔮", "3": "🕊", "4": "🌀", "5": "👁️"}


def color_emotion(val, name):
    try:
        val = float(val)
        if name == "calm":
            return f"\033[96m{val}\033[0m" if val > 0.7 else f"{val}"
        elif name == "stress":
            return f"\033[91m{val}\033[0m" if val > 0.5 else f"{val}"
        elif name == "joy":
            return f"\033[92m{val}\033[0m" if val > 0.5 else f"{val}"
        else:
            return f"{val}"
    except BaseException:
        return val


def visualize_replays(limit=10):
    if not REPLAY_PATH.exists():
        print(f"⚠️ Replay queue not found. Creating placeholder at {REPLAY_PATH}")
        REPLAY_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPLAY_PATH.write_text("")

    with open(REPLAY_PATH) as f:
        raw_lines = f.readlines()

    lines = [line for line in raw_lines if line.strip().startswith("{")]

    print(f"\n🔁 SYMBOLIC DREAM REPLAY VISUALIZER ({len(lines)} entries)")
    print("─────────────────────────────────────────────────────────────")

    tag_counter = Counter()
    emoji_counter = Counter()

    for line in lines:
        try:
            dream = json.loads(line.strip())
            emoji = TIER_EMOJI.get(str(dream.get("tier")), "•")
            print(f"\n🌀 {dream.get('timestamp')} | ID: {dream.get('message_id')}")
            print(f"   Tier: {dream.get('tier')} {emoji} | Widget: {dream.get('source_widget')}")
            print(f"   Tags: {', '.join(dream.get('tags', [])}")
            ev = dream.get("emotion_vector", {})
            print(
                "   Emotions →",
                " | ".join(f"{k.capitalize()}: {color_emotion(v, k)}" for k, v in ev.items()},
            )
            print(f"   Emoji: {dream.get('emoji')} | Notes: {dream.get('notes')}")
            tag_counter.update(dream.get("tags", []))
            emoji = dream.get("emoji")
            if emoji:
                emoji_counter[emoji] += 1
        except Exception as e:
            print("❌ Could not parse dream entry:", e)

    print("\n🔖 Top Tags:", dict(tag_counter.most_common(5)))
    print("🌈 Emoji Distribution:", dict(emoji_counter.most_common(5)))


if __name__ == "__main__":
    visualize_replays(limit=10)