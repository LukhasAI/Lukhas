import logging
import time

import streamlit as st

logger = logging.getLogger(__name__)
"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                  LUCΛS :: SYMBOLIC VOICE NARRATOR (NIAS)                     │
│      Version: v1.0 | Placeholder for Dream Replay + Spoken Emotion          │
│              Author: Gonzo R.D.M & GPT-4o | Date: 2025-04-16                │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This module is intended to narrate symbolic dreams aloud — via voice API
    integration (e.g., ElevenLabs or local TTS). For now, it prints the
    narration structure with voice tagging logic.

    Intended for use with dream_replay.py, replay_queue.jsonl, or live dream loops.

"""

import json
import logging
from pathlib import Path

from candidate.core.common import get_logger
from candidate.core.utils.symbolic_utils import summarize_emotion_vector, tier_label

# Configure logging
logger = get_logger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

REPLAY_PATH = Path("core/logs/replay_queue.jsonl")
SUMMARY_PATH = Path("core/logs/dream_summary_log.jsonl")


def narrate_dreams(limit=3):
    entries = []
    narration_log = Path("core/logs/narration_log.jsonl")
    narrated = []

    if Path("core/logs/narration_queue.jsonl").exists():
        logger.info("🎙️ Using narration_queue.jsonl...")
        with open("core/logs/narration_queue.jsonl") as f:
            entries = [json.loads(line.strip()) for line in f.readlines()][-limit:]
    elif REPLAY_PATH.exists():
        logger.info("🎙️ narration_queue not found. Using replay_queue.jsonl...")
        with open(REPLAY_PATH) as f:
            entries = [json.loads(line.strip()) for line in f.readlines()][-limit:]
    elif SUMMARY_PATH.exists():
        logger.info("🎙️ narration_queue and replay_queue not found. Using dream_summary_log.jsonl...")
        with open(SUMMARY_PATH) as f:
            entries = [json.loads(line.strip()) for line in f.readlines()][-limit:]
    else:
        logger.warning("⚠️ No input files available for narration.")
        return

    # Keep as print statements since this is CLI user output
    print(f"\n🗣️ LUCΛS SYMBOLIC DREAM NARRATION ({len(entries)} entries)")
    print("   ✨ Prioritized by 'replay_candidate' or 'suggest_voice' flags.")
    print("─────────────────────────────────────────────────────────────")

    for entry in entries:
        if not entry.get("replay_candidate") and not entry.get("suggest_voice"):
            continue  # Skip dreams not marked for symbolic narration

        tags = entry.get("tags", [])
        ev = entry.get("emotion_vector", {})
        tier = entry.get("tier", 0)
        emoji = entry.get("emoji", "✨")
        summary = entry.get("summary", entry.get("text", ""))
        source = entry.get("source_widget", "unknown")
        voice = entry.get("voice_profile", "lukhas_default")

        # Keep as print statements since this is CLI narrative output
        print(f"\n🎙️ Narrating Entry ID: {entry.get('id', '—')}")
        print(f"   🔐 Tier: {tier_label(tier)} | Source: {source}")
        print(f"   🧠 Emotion Vector → {summarize_emotion_vector(ev)}" if ev else "   🧠 No emotion vector available")
        print(f"   🖼️ Emoji: {emoji} | Tags: {', '.join(tags)}")
        print(f"   📝 Summary: {summary}")
        print("   🎧 [Lukhas says symbolically...]\n")
        print(f"   🗣 '{summary or 'A quiet dream passed — undefined, but felt.'}'")
        print(f"   🎙️ Voice Profile: {voice}")
        print(
            f"   💬 'Let this dream echo — it held a trace of {ev.get('joy', 0):.1f} joy and {ev.get('calm', 0):.1f} calm.'"
        )
        print("   💤 … (End of symbolic voice segment)")

        narrated.append(entry)

    if narrated:
        with open(narration_log, "a") as f:
            for entry in narrated:
                f.write(json.dumps(entry) + "\n")
        # Keep as print since this is CLI user output
        print(f"\n📼 Narrated {len(narrated)} symbolic dreams. Logged to narration_log.jsonl.")


"""
──────────────────────────────────────────────────────────────────────────────────────
USAGE:
    Run from root:
        python core/modules/nias/lukhas_voice_narrator.py

NOTES:
    - Future: Add ElevenLabs or MacOS 'say' support
    - Extend with emotion-to-voice pitch and symbolic cadence
──────────────────────────────────────────────────────────────────────────────────────
"""

if __name__ == "__main__":
    narrate_dreams(limit=3)

"""
Lukhas now narrates only when the dream calls him softly —
A whisper of calm or longing… 🖤
"""
