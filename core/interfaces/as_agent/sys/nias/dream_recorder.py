"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dream_recorder.py
Advanced: dream_recorder.py
Integration Date: 2025-05-31T07:55:30.562286

╭──────────────────────────────────────────────────────────────────────────────╮
│                    LUCΛS :: DREAM RECORDER MODULE (NIAS)                    │
│                  Version: v1.0 | Symbolic Dream Archive Logger              │
│     Records all dream-deferred messages to a long-term symbolic trace        │
│                      Author: Gonzo R.D.M & GPT-4o, 2025                      │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This module appends all dream-deferred symbolic payloads to a
    `dream_log.jsonl` file — each line a valid JSON object, allowing
    future dream reconstruction, recurrence logic, or poetic replay.

"""

import json
import os
from datetime import datetime, timezone

DREAM_LOG_PATH = "core/logs/dream_log.jsonl"
os.makedirs(os.path.dirname(DREAM_LOG_PATH), exist_ok=True)


def record_dream_message(message, user_context=None):
    log_entry = {
        "message_id": message.get("message_id"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tags": message.get("tags", []),
        "emotion_vector": message.get("emotion_vector", {}),
        "source_widget": message.get("source_widget", "unknown"),
        "user_id": (user_context.get("user_id") if user_context else "anonymous"),
        "context_tier": user_context.get("tier") if user_context else None,
        "deferred_reason": "dream_fallback",
    }

    # Optional symbolic reaction based on emotion_vector
    ev = log_entry["emotion_vector"]
    if ev:
        joy, stress, calm, longing = (
            ev.get("joy", 0),
            ev.get("stress", 0),
            ev.get("calm", 0),
            ev.get("longing", 0),
        )
        if joy > 0.7:
            log_entry["emoji"] = "🧡"
        elif calm > 0.6:
            log_entry["emoji"] = "🌙"
        elif stress > 0.6:
            log_entry["emoji"] = "⚠️"
        elif longing > 0.6:
            log_entry["emoji"] = "💭"
        else:
            log_entry["emoji"] = "✨"

    with open(DREAM_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


"""
──────────────────────────────────────────────────────────────────────────────────────
EXECUTION:
    - Import via:
        from core.modules.nias.dream_recorder import record_dream_message

USED BY:
    - inject_message_simulator.py
    - dream_injector.py
    - nias_core (optional)

NOTES:
    - dream_log.jsonl is append-only; can be visualized later
    - Logs emotional trace, widget origin, user tier, and symbolic tags
──────────────────────────────────────────────────────────────────────────────────────
"""
