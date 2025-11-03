"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: feedback_loop.py
Advanced: feedback_loop.py
Integration Date: 2025-05-31T07:55:30.563779

╭──────────────────────────────────────────────────────────────────────────────╮
│                       LUCΛS :: FEEDBACK LOOP MODULE                          │
│               Version: v1.0 | Symbolic Response + Resonance Tracker          │
│            Author: Gonzo R.D.M & GPT-4o | Date: 2025-04-16                   │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This module captures user feedback for symbolic messages.
    It tracks perceived emotional impact, usefulness, clarity, and symbolic resonance.
    Results are logged to a symbolic feedback ledger for future tuning and trust metrics.

"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

FEEDBACK_LOG_PATH = Path("core/logs/feedback_log.jsonl")
FEEDBACK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def record_feedback(message_id, user_id, score, notes=None, emoji=None, user_context=None):
    """
    Store a symbolic feedback event with tier-safe attributes.

    Args:
        message_id (str): ID of the symbolic message
        user_id (str): symbolic user reference
        score (int): numeric feedback (1–5)
        notes (str, optional): optional reflection or reaction
        emoji (str, optional): optional symbolic reaction 🧠💡🖤🌙⚠️

    Stores symbolic feedback and auto-qualifies:
    - High-score dream feedback as replay candidates
    - Tier and consent-aware feedback trace
    - Emotional feedback aligned with dream-source detection
    """
    log_entry = {
        "message_id": message_id,
        "user_id": user_id,
        "score": score,
        "emoji": emoji,
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        # Symbolic logic: enrich with optional flags
        "replay_candidate": (score == 5 and emoji in ["🧡", "🌙"]),
        "from_dream": "dream" in (notes.lower() if notes else ""),
        "tier": (user_context.get("tier") if user_context else None),  # if passed
    }

    with open(FEEDBACK_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


"""
──────────────────────────────────────────────────────────────────────────────────────
USAGE:
    from core.modules.nias.feedback_loop import record_feedback

    record_feedback(
        message_id="msg_2025_001",
        user_id="user_001",
        score=4,
        notes="Felt deeply understood.",
        emoji="🖤"
    )

NOTES:
    - You may later filter or replay high-score symbolic messages
    - Can be connected to trust scoring, dream quality, or ABAS tuning
──────────────────────────────────────────────────────────────────────────────────────
"""

if __name__ == "__main__":
    print("\n🧠 LUCΛS :: FEEDBACK LOOP TEST")
    print("──────────────────────────────────────────────")

    try:
        message_id = input("📩 Enter symbolic message ID: ").strip()
        user_id = input("🧑 Enter user ID: ").strip()
        score = int(input("🔢 Score (1–5): ").strip())
        emoji = input("🔘 Emoji (optional): ").strip() or None
        notes = input("📝 Notes (optional): ").strip() or None
        tier = input("🔐 User Tier (optional): ").strip()
        user_context = {"tier": int(tier)} if tier else None

        record_feedback(
            message_id=message_id,
            user_id=user_id,
            score=score,
            emoji=emoji,
            notes=notes,
            user_context=user_context,
        )
        print("✅ Symbolic feedback recorded.")

    except Exception as e:
        print("⚠️ Error recording feedback:", e)
