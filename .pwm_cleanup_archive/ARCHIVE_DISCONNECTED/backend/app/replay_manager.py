"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : replay_manager.py                              │
│ DESCRIPTION : Manages symbolic memory replay queue (dreams)  │
│ TYPE        : Replay Engine                                  │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import json
from datetime import datetime
from pathlib import Path

REPLAY_QUEUE_PATH = "replay_queue.jsonl"


def add_replay_entry(user_id: int, interaction: str, context: str = "general"):
    """
    Add a symbolic interaction to the replay queue (future dream recall).
    """
    entry = {
        "user_id": user_id,
        "interaction": interaction,
        "context": context,
        "timestamp": str(datetime.utcnow()),
    }

    with open(REPLAY_QUEUE_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"🌀 Replay entry added for user {user_id}: {interaction}")


def get_replay_entries(user_id: int = None):
    """
    Load all (or filtered) symbolic replay entries.
    """
    entries = []
    if Path(REPLAY_QUEUE_PATH).exists():
        with open(REPLAY_QUEUE_PATH) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if user_id is None or entry["user_id"] == user_id:
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue
    return entries
