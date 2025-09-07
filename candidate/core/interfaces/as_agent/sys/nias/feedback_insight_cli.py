from typing import Optional
"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: feedback_insight_cli.py
Advanced: feedback_insight_cli.py
Integration Date: 2025-5-31T07:55:30.565384
"""
import time
import streamlit as st

"""
++
|                    LUCS :: FEEDBACK INSIGHT CLI (v1.0)                      |
|     Analyze symbolic feedback across score, emoji, and emotional tags       |
|        Author: Gonzo R.D.M | Linked to: feedback_log.jsonl & utils.py       |
++

Description:
    This CLI visualizes patterns in feedback_log.jsonl, such as emoji distribution,
    average score, replay flags, and symbolic user sentiment trends.

Usage:
    python core/modules/nias/feedback_insight_cli.py
"""

import argparse
import json
import os
from collections import Counter
from statistics import mean

FEEDBACK_LOG = "core/logs/feedback_log.jsonl"


def load_feedback():
    if not os.path.exists(FEEDBACK_LOG):
        print(" No feedback log found.")
        return []
    with open(FEEDBACK_LOG) as f:
        return [json.loads(line) for line in f if line.strip()]


def parse_args():
    parser = argparse.ArgumentParser(description="Symbolic Feedback CLI Insights")
    parser.add_argument(
        "--voice-flagged",
        action="store_true",
        help="Only show feedback with 'suggest_voice': true",
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=None,
        help="Filter feedback with score <= threshold",
    )
    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="Optional path to export filtered feedback as .jsonl",
    )
    return parser.parse_args()


def analyze_feedback(entries, args=None):
    if not entries:
        print(" No feedback entries available.")
        return

    if args:
        if args.voice_flagged:
            entries = [e for e in entries if e.get("suggest_voice")]
        if args.score_threshold is not None:
            entries = [e for e in entries if e.get("score", 999) <= args.score_threshold]

    scores = [e["score"] for e in entries if "score" in e]
    emojis = [e.get("emoji", "*") for e in entries]
    replay_candidates = sum(1 for e in entries if e.get("replay_candidate"))
    notes = [e["notes"] for e in entries if "notes" in e and e["notes"].strip()]

    print("\n Average Score:", round(mean(scores), 2))
    print(" Most Common Emojis:", Counter(emojis).most_common(5))
    print(f" Replay Candidates: {replay_candidates} / {len(entries}")

    print("\n Reflection Notes (Preview):")
    for note in notes[:5]:
        print(f"* {note}")

    if args and args.export:
        with open(args.export, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        print(f"\n Exported {len(entries} entries to {args.export}")


if __name__ == "__main__":
    args = parse_args()
    feedback_entries = load_feedback()
    analyze_feedback(feedback_entries, args)
# SYNTAX_ERROR_FIXED: ```