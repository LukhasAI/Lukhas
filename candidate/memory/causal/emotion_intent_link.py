"""

#TAG:memory
#TAG:causal
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: emotion_intent_link.py
Advanced: emotion_intent_link.py
Integration Date: 2025-05-31T07:55:28.107734
"""
# Path: symbolic_ai/linkers/crosslinker.py
import json
import os
import time
from datetime import datetime

import streamlit as st

INTENT_LOG = "symbolic_ai/memoria/intent_log.jsonl"
EMOTION_LOG = "symbolic_ai/memoria/emotion_log.jsonl"
CROSSLINK_LOG = "symbolic_ai/memoria/crosslink_log.jsonl"


def load_jsonl(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath) as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


def crosslink_emotion_to_intent(emotion_ts, window=5):
    emotions = load_jsonl(EMOTION_LOG)
    intents = load_jsonl(INTENT_LOG)

    emotion_match = next((e for e in emotions if e["timestamp"] == emotion_ts), None)
    if not emotion_match:
        print("⚠️ Emotion timestamp not found.")
        return None

    emotion_time = datetime.fromisoformat(emotion_ts)
    intent_match = None

    for intent in reversed(intents):
        ts = intent.get("timestamp")
        if not ts:
            continue
        intent_time = datetime.fromisoformat(ts)
        if abs((emotion_time - intent_time).total_seconds()) <= window:
            intent_match = intent
            break

    if not intent_match:
        print("⚠️ No nearby intent found to link.")
        return None

    link_record = {
        "emotion": emotion_match,
        "intent": intent_match,
        "linked_at": datetime.now().isoformat(),
    }

    os.makedirs(os.path.dirname(CROSSLINK_LOG), exist_ok=True)
    with open(CROSSLINK_LOG, "a") as f:
        f.write(json.dumps(link_record) + "\n")

    print("✅ Linked emotion and intent.")
    print(json.dumps(link_record, indent=2))
    return link_record


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 crosslinker.py <emotion_timestamp>")
        sys.exit(1)

    ts = sys.argv[1]
    crosslink_emotion_to_intent(ts)
