"""
+===========================================================================+
| MODULE: Dream Replay Cli                                            |
| DESCRIPTION: lukhas AI System Footer                               |
|                                                                         |
| FUNCTIONALITY: Functional programming with optimized algorithms     |
| IMPLEMENTATION: Error handling                                      |
| INTEGRATION: Multi-Platform AI Architecture                        |
+===========================================================================+

"Enhancing beauty while adding sophistication" - LUKHAS Systems 2025
"Enhancing beauty while adding sophistication" - lukhas Systems 2025


"""

LUKHAS AI System - Function Library
File: dream_replay_cli.py
Path: core/dreams/dream_replay_cli.py
Created: "2025-06-05 09:37:28"
Author: LUKHAS AI Team
Version: 1.0
This file is part of the LUKHAS AI (Logical Unified Knowledge Hyper-Adaptable System)
Advanced Cognitive Architecture for Artificial General Intelligence
Copyright (c) 2025 LUKHAS AI Research. All rights reserved.
Licensed under the LUKHAS Core License - see LICENSE.md for details.
lukhas AI System - Function Library
File: dream_replay_cli.py
Path: core/dreams/dream_replay_cli.py
Created: "2025-06-05 09:37:28"
Author: LUKHAS AI Team
Version: 1.0
This file is part of the LUKHAS AI (LUKHAS Universal Knowledge & Holistic AI System)
Advanced Cognitive Architecture for Artificial General Intelligence
Copyright (c) 2025 LUKHAS AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""

"""
+──────────────────────────────────────────────────────────────────────────────+
+──────────────────────────────────────────────────────────────────────────────+

DESCRIPTION:
    A simple CLI interface that calls dream_replay.py with symbolic filters:
    - Sort by dominant emotion
    - Filter by tag (e.g. "soothe", "replay")
    - Limit count
    - Only show replay-worthy dreams (score + emoji filtered)
    - Filter by suggest_voice flag (voice narration candidates)

"""

from core.modules.nias.dream_replay import replay_recent_dreams

def run_cli():
    print("\n🌙 LUCΛS Dream Replay CLI")
    print("\n🌙 LUClukhasS Dream Replay CLI")
    print("──────────────────────────────────────────────")

    try:
        limit = int(input("🔢 How many dreams to replay? (default 5): ").strip() or "5")
        tag_input = input("🔖 Filter by tag? (comma-separated, or ENTER to skip): ").strip()
        filter_tags = [t.strip() for t in tag_input.split(",")] if tag_input else None
        replay_only = input("🔁 Only replay candidates? (y/N): ").strip().lower() == "y"
        sort_axis = input("📊 Sort by emotion? (joy/stress/calm/longing) or ENTER to skip: ").strip().lower()
        sort_by = sort_axis if sort_axis in ["joy", "stress", "calm", "longing"] else None
        voice_suggested = input("🗣 Only dreams flagged for voice narration? (y/N): ").strip().lower() == "y"
    except Exception as e:
        print(f"⚠️ Input error: {e}")
        return

    replay_recent_dreams(
        limit=limit,
        filter_by_tag=filter_tags,
        only_replay_candidates=replay_only,
        sort_by_emotion=sort_by,
        voice_flagged_only=voice_suggested
    )

"""
──────────────────────────────────────────────────────────────────────────────────────
USAGE:
    Run from root:
        python core/modules/nias/dream_replay_cli.py

NOTES:
    - Symbolically aligned with replay queue and dream logs
    - Extend to trigger Λ_voice_narrator.py for each replay
    - Extend to trigger voice_narrator.py for each replay
──────────────────────────────────────────────────────────────────────────────────────
"""

if __name__ == "__main__":
    run_cli()








# Last Updated: 2025-06-05 09:37:28

# TECHNICAL IMPLEMENTATION: Neural network architectures with adaptive learning, Artificial intelligence with advanced cognitive modeling, Bioinformatics processing for pattern recognition
# LUKHAS Systems 2025 www.lukhas.ai 2025
# lukhas Systems 2025 www.lukhas.ai 2025
