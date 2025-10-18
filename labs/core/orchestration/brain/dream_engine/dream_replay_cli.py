"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dream_replay_cli.py
Advanced: dream_replay_cli.py
Integration Date: 2025-05-31T07:55:28.268667
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                  LUCΛS :: DREAM REPLAY CLI WRAPPER (NIAS)                   │
│       Version: v1.0 | Terminal Interface for Filtered Dream Replays         │
│             Author: Gonzo R.D.M & GPT-4o | Date: 2025-04-16                 │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    A simple CLI interface that calls dream_replay.py with symbolic filters:
    - Sort by dominant emotion
    - Filter by tag (e.g. "soothe", "replay")
    - Limit count
    - Only show replay-worthy dreams (score + emoji filtered)
    - Filter by suggest_voice flag (voice narration candidates)

"""


from core.modules.nias.__init__ import replay_recent_dreams


def run_cli():
    print("\n🌙 LUCΛS Dream Replay CLI")
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
        voice_flagged_only=voice_suggested,
    )


"""
──────────────────────────────────────────────────────────────────────────────────────
USAGE:
    Run from root:
        python core/modules/nias/dream_replay_cli.py

NOTES:
    - Symbolically aligned with replay queue and dream logs
    - Extend to trigger lukhas_voice_narrator.py for each replay
──────────────────────────────────────────────────────────────────────────────────────
"""

if __name__ == "__main__":
    run_cli()
