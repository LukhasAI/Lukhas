"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: replay_queue.py
Advanced: replay_queue.py
Integration Date: 2025-5-31T07:55:30.500061
"""

"""
+──────────────────────────────────────────────────────────────────────────────+
|                    LUCΛS :: REPLAY QUEUE BUILDER (NIAS)                      |
|         Version: v1.0 | Extracts 5⭐️ dream-aligned feedback candidates       |
|               Author: Gonzo R.D.M & GPT-4o | Date: 2025-4-16                |
+──────────────────────────────────────────────────────────────────────────────+

DESCRIPTION:
    This script scans `feedback_log.jsonl` for high-score feedback entries
    marked as replay_candidate = true. Each matching entry is added to a
    symbolic replay queue (append-only) for future reflection, dream replay,
    or emotional resonance sessions.

"""

import json
from pathlib import Path
from datetime import datetime

FEEDBACK_LOG_PATH = Path("core/logs/feedback_log.jsonl")
REPLAY_QUEUE_PATH = Path("core/logs/replay_queue.jsonl")
REPLAY_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

def build_replay_queue():
    if not FEEDBACK_LOG_PATH.exists():
        print("⚠️ No feedback log found.")
        return

    with open(FEEDBACK_LOG_PATH, "r") as f:
        feedback_entries = [json.loads(line.strip()) for line in f.readlines()]

    replay_entries = [
        entry for entry in feedback_entries
        if entry.get("replay_candidate", False) is True
    ]

    if not replay_entries:
        print("🔍 No replay-worthy feedback found.")
        return

    with open(REPLAY_QUEUE_PATH, "a") as f:
        for entry in replay_entries:
            f.write(json.dumps({
                "message_id": entry["message_id"],
                "timestamp": datetime.utcnow().isoformat(),
                "emoji": entry.get("emoji"),
                "score": entry.get("score"),
                "notes": entry.get("notes"),
                "user_id": entry.get("user_id"),
                "tier": entry.get("tier"),
                "origin": "feedback",
                "tags": entry.get("tags", []),
                "suggest_voice": entry.get("suggest_voice", False)
            }) + "\n")

    print(f"✅ Queued {len(replay_entries)} symbolic replay candidates to replay_queue.jsonl")

"""
──────────────────────────────────────────────────────────────────────────────────────
USAGE:
    From root:
        python core/modules/nias/replay_queue.py

NOTES:
    - You can filter or prioritize replay based on emoji, tier, or timestamp
    - Replay queue is append-only and lives at: core/logs/replay_queue.jsonl
    - Used by dream_replay, emotion recap, or future LUCΛS voice sessions
──────────────────────────────────────────────────────────────────────────────────────
"""

if __name__ == "__main__":
    build_replay_queue()
"""
