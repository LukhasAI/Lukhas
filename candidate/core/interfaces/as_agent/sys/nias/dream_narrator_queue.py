"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dream_narrator_queue.py
Advanced: dream_narrator_queue.py
Integration Date: 2025-05-31T07:55:30.506963
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                   LUCΛS :: SYMBOLIC DREAM NARRATOR QUEUE (v1.0)             │
│        Extracts dream entries flagged for voice narration by LUCΛS          │
│    Author: Gonzo R.D.M | Linked to: dream_log.jsonl, lukhas_voice_narrator   │
╰──────────────────────────────────────────────────────────────────────────────╯

This module scans the dream_log.jsonl file for entries with `"suggest_voice": true`
and outputs them into a symbolic queue for narration.

It supports future integration with ElevenLabs, text-to-speech modules,
and scheduled voice playback.

Usage:
    python core/modules/nias/dream_narrator_queue.py
"""

import json
import os

DREAM_LOG_PATH = "core/logs/dream_log.jsonl"
NARRATION_QUEUE_PATH = "core/logs/narration_queue.jsonl"


def extract_narratable_dreams():
    if not os.path.exists(DREAM_LOG_PATH):
        print("🚫 No dream log found.")
        return

    with open(DREAM_LOG_PATH) as f:
        dreams = [json.loads(line) for line in f if line.strip()]

    narratable = []
    suggest_voice_count = 0
    replay_candidate_count = 0

    for dream in dreams:
        if dream.get("suggest_voice"):
            suggest_voice_count += 1
            dream.setdefault("tags", []).append("narration_flag")
            narratable.append(dream)
        elif dream.get("replay_candidate"):
            replay_candidate_count += 1
            dream.setdefault("tags", []).append("narration_flag")
            narratable.append(dream)

    if not narratable:
        print("📭 No dreams flagged for narration.")
        return

    with open(NARRATION_QUEUE_PATH, "w") as f:
        for dream in narratable:
            f.write(json.dumps(dream) + "\n")

    print(f"🎙 Queued {len(narratable)} dream(s) for narration → {NARRATION_QUEUE_PATH}")
    print(f"🗣 Narration Flag (suggest_voice): {suggest_voice_count}")
    print(f"🔁 Replay Candidate Flag: {replay_candidate_count}")


if __name__ == "__main__":
    extract_narratable_dreams()