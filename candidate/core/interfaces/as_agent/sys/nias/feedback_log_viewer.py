"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: feedback_log_viewer.py
Advanced: feedback_log_viewer.py
Integration Date: 2025-05-31T07:55:30.503626
"""


"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                    LUCΛS :: FEEDBACK LOG VIEWER (CLI)                        │
│              Version: v1.0 | View + Filter Symbolic Feedback Log             │
│               Author: Gonzo R.D.M & GPT-4o | 2025-04-16                       │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This tool reads symbolic feedback stored in feedback_log.jsonl and prints
    meaningful insight — such as emoji reactions, resonance scores, and notes.

    You may sort or filter by score, emoji, or keywords in future extensions.

"""

import json
from pathlib import Path

FEEDBACK_LOG_PATH = Path("core/logs/feedback_log.jsonl")


def view_feedback(limit=10, filter_emoji=None, min_score=None):
    if not FEEDBACK_LOG_PATH.exists():
        print("⚠️  No feedback log found.")
        return

    with open(FEEDBACK_LOG_PATH) as f:
        lines = f.readlines()[-limit:]

    filtered = []
    for line in lines:
        try:
            entry = json.loads(line.strip())
            if filter_emoji and entry.get("emoji") != filter_emoji:
                continue
            if min_score and entry.get("score", 0) < min_score:
                continue
            filtered.append(entry)
        except Exception as e:
            print("❌ Could not parse feedback entry:", e)

    if not filtered:
        print("⚠️ No feedback entries matched the filter.")
        return

    for entry in filtered:
        print(f"\n🧠 {entry['timestamp']} | Msg: {entry['message_id']} | User: {entry['user_id']}")
        print(f"   Score: {entry['score']} {entry.get('emoji', '')}")
        if entry.get("notes"):
            print(f"   Notes: {entry['notes']}")


if __name__ == "__main__":
    print("\n🧠 LUCΛS FEEDBACK VIEWER")
    print("──────────────────────────────────────────────")
    print("Sort or filter feedback logs symbolically.\n")

    try:
        limit_input = input("🔢 How many feedback entries? (default 10): ").strip()
        limit = int(limit_input) if limit_input else 10

        emoji_filter = input("🔘 Filter by emoji (e.g., 🌙, ⚠️, 🧡) or press ENTER to skip: ").strip() or None
        score_input = input("🔢 Minimum score (1–5) or press ENTER to skip: ").strip()
        score_filter = int(score_input) if score_input else None
    except Exception as e:
        print("⚠️ Invalid input:", e)
        emoji_filter = None
        score_filter = None
        limit = 10

    view_feedback(limit=limit, filter_emoji=emoji_filter, min_score=score_filter)

    # Ask to summarize emotion usage
    summarize = input("📊 Summarize emoji distribution? (y/N): ").strip().lower()
    if summarize == "y":
        emoji_count = {}
        for entry in filtered:
            emoji = entry.get("emoji", "")
            if emoji:
                emoji_count[emoji] = emoji_count.get(emoji, 0) + 1
        if emoji_count:
            print("\n📈 Symbolic Emoji Distribution:")
            for emoji, count in emoji_count.items():
                print(f"   {emoji}: {count}")
        else:
            print("🕊️ No emoji found in filtered feedback.")

"""
──────────────────────────────────────────────────────────────────────────────────────
USAGE:
    Run from root:
        python core/modules/nias/feedback_log_viewer.py

NOTES:
    - Extend with filters: by emoji, score, or keywords
    - Could visualize symbolic trust metrics in future
──────────────────────────────────────────────────────────────────────────────────────
"""
