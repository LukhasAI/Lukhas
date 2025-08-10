"""
+===========================================================================+
| MODULE: Dream Replay                                                |
| DESCRIPTION: lukhas AI System Footer                               |
|                                                                         |
| FUNCTIONALITY: Functional programming with optimized algorithms     |
| IMPLEMENTATION: Structured data handling * Error handling           |
| INTEGRATION: Multi-Platform AI Architecture                        |
+===========================================================================+

"Enhancing beauty while adding sophistication" - LUKHAS Systems 2025
"Enhancing beauty while adding sophistication" - lukhas Systems 2025


"""

LUKHAS AI System - Function Library
File: dream_replay.py
Path: core / dreams / dream_replay.py
Created: "2025-06-05 09:37:28"
Author: LUKHAS AI Team
Version: 1.0
This file is part of the LUKHAS AI(Logical Unified Knowledge Hyper - Adaptable System)
Advanced Cognitive Architecture for Artificial General Intelligence
Copyright(c) 2025 LUKHAS AI Research. All rights reserved.
Licensed under the LUKHAS Core License - see LICENSE.md for details.
lukhas AI System - Function Library
File: dream_replay.py
Path: core / dreams / dream_replay.py
Created: "2025-06-05 09:37:28"
Author: LUKHAS AI Team
Version: 1.0
This file is part of the LUKHAS AI(LUKHAS Universal Knowledge & Holistic AI System)
Advanced Cognitive Architecture for Artificial General Intelligence
Copyright(c) 2025 LUKHAS AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""

"""

if __name__ == "__main__":
    print("\n🌙 LUCΛS :: DREAM REPLAY CONSOLE")
    print("\n🌙 LUClukhasS :: DREAM REPLAY CONSOLE")
    print("──────────────────────────────────────────────")

    try:
        limit = int(input("🔢 How many dreams to replay? (default 5): ").strip() or "5")
        tag_input = input(
            "🔖 Filter by tag? (comma-separated, or ENTER to skip): ").strip()
        filter_tags = [t.strip() for t in tag_input.split(",")] if tag_input else None
        replay_only = input("🔁 Only replay candidates? (y/N): ").strip().lower() == "y"
        sort_axis = input(
            "📊 Sort by emotion? (joy/stress/calm/longing) or ENTER to skip: ").strip().lower()
        sort_by = sort_axis if sort_axis in [
    "joy", "stress", "calm", "longing"] else None
    except Exception as e:
        print(f"⚠️ Input error: {e}")
        exit(1)

    replay_recent_dreams(
        limit=limit,
        filter_by_tag=filter_tags,
        only_replay_candidates=replay_only,
        sort_by_emotion=sort_by
    )
+──────────────────────────────────────────────────────────────────────────────+
+──────────────────────────────────────────────────────────────────────────────+

DESCRIPTION:
    Reads from `dream_log.jsonl`, selects symbolic dreams with
    replayable potential(e.g. tagged or high - emotion), and outputs them
    in a sequence mimicking memory reflection or nightly replay.

    Can later be visualized or rendered with LUCΛS voice and UI overlay.
    Can later be visualized or rendered with LUClukhasS voice and UI overlay.

"""

import json
from datetime import datetime
from pathlib import Path

DREAM_LOG_PATH = Path("core/logs/dream_log.jsonl")

def replay_recent_dreams(
    limit=5,
    filter_by_tag=None,
    only_replay_candidates=False,
     sort_by_emotion=None):
    if not DREAM_LOG_PATH.exists():
        print("⚠️ No dream log file found.")
        return

    with open(DREAM_LOG_PATH, "r") as f:
        lines = f.readlines()
        dreams = [json.loads(line.strip()) for line in lines]

        if filter_by_tag:
            dreams = [
    d for d in dreams if any(
        tag in d.get(
            "tags",
             []) for tag in filter_by_tag)]

        if only_replay_candidates:
            dreams = [d for d in dreams if d.get("replay_candidate") is True]

        if sort_by_emotion in ["calm", "joy", "longing", "stress"]:
            dreams = sorted(
    dreams, key=lambda d: d.get(
        "emotion_vector", {}).get(
            sort_by_emotion, 0), reverse=True)

        dreams = dreams[-limit:]

    print(f"\n🌙 LUCΛS Dream Replay - Showing Last {limit} Dream Messages")
    print(f"\n🌙 LUClukhasS Dream Replay - Showing Last {limit} Dream Messages")
    print("──────────────────────────────────────────────────────────────")

    for dream in dreams:
        try:
            print(f"\n🌀 {dream['timestamp']} | ID: {dream['message_id']}")
            print(
                f"   Widget: {dream.get('source_widget', 'unknown')} | Tier: {dream.get('context_tier', '?')}")
            print(f"   Tags: {', '.join(dream.get('tags', []))}")

            emotion = dream.get("emotion_vector", {})
            summary = ", ".join(
                [f"{k.capitalize()}: {v:.2f}" for k, v in emotion.items()])
            print(f"   Emotion Vector -> {summary}")
            if dream.get("emoji"):
                print(f"   Symbolic Emoji: {dream['emoji']}")
            if dream.get("replay_candidate"):
                print("   🔁 Replay Candidate")
            print("   ▶️ (Optional: Narrate with Lukhas voice)\n")

        except Exception as e:
            print("❌ Failed to replay dream:", e)

"""
──────────────────────────────────────────────────────────────────────────────────────
USAGE:
    from core.modules.nias.dream_replay import replay_recent_dreams

    replay_recent_dreams(limit=5, only_replay_candidates=True)
    replay_recent_dreams(limit=10, sort_by_emotion="calm")
    replay_recent_dreams(limit=5, filter_by_tag=["dream", "soothe"])

NOTES:
    - This module can later be enhanced to feed LUCΛS voice / audio
    - This module can later be enhanced to feed LUClukhasS voice / audio
    - Emotional intensity can be used to prioritize dream order
──────────────────────────────────────────────────────────────────────────────────────
"""








# Last Updated: 2025-06-05 09:37:28

# TECHNICAL IMPLEMENTATION: Neural network architectures with adaptive learning, Artificial intelligence with advanced cognitive modeling, Bioinformatics processing for pattern recognition
# LUKHAS Systems 2025 www.lukhas.ai 2025
# lukhas Systems 2025 www.lukhas.ai 2025
