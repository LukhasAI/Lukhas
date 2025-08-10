"""
# ===========================================================================
# FILENAME: trace_log_viewer.py
# MODULE: core.interfaces.as_agent.sample_payloads.sample_playloads.trace_log_viewer
# DESCRIPTION: CLI tool to parse and print recent symbolic deliveries or dream deferrals.
# DEPENDENCIES: json, datetime, pathlib
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ===========================================================================
#ΛTRACE
"""
import json
from datetime import datetime
from pathlib import Path

DREAM_LOG_PATH = Path("core/logs/dream_log.jsonl")


def print_dream_log_summary(limit=10):
    if not DREAM_LOG_PATH.exists():
        print("⚠️  No dream log found at:", DREAM_LOG_PATH)
        return

    with open(DREAM_LOG_PATH, "r") as f:
        lines = f.readlines()[-limit:]

    print(f"\n🧠 Last {limit} Symbolic Dream Log Entries")
    print("─────────────────────────────────────────────────────────────")
    for line in lines:
        try:
            entry = json.loads(line.strip())
            print(f"🌀 {entry['timestamp']} | ID: {entry['message_id']}")
            print(f"    Tags: {', '.join(entry.get('tags', []))}")
            print(
                f"    Tier: {entry.get('context_tier', '?')} | Widget: {entry.get('source_widget', '?')}")
            emo = entry.get("emotion_vector", {})
            print(
                f"    Emotions -> Joy: {emo.get('joy', 0)} | Stress: {emo.get('stress', 0)} | Calm: {emo.get('calm', 0)} | Longing: {emo.get('longing', 0)}\n")
            emoji = entry.get("emoji")
            if emoji:
                print(f"    Symbolic Emoji -> {emoji}\n")
        except Exception as e:
            print("❌ Could not parse log entry:", e)


if __name__ == "__main__":
    print_dream_log_summary(limit=5)
# ===========================================================================
# FILENAME: trace_log_viewer.py
# VERSION: 1.0.0
# TIER SYSTEM: Tier 1-2 (Basic log viewing)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Dream log summary printing.
# FUNCTIONS: print_dream_log_summary.
# CLASSES: None.
# DECORATORS: None.
# DEPENDENCIES: json, datetime, pathlib.
# INTERFACES: None.
# ERROR HANDLING: try-except block in log parsing.
# LOGGING: None.
# AUTHENTICATION: None.
# HOW TO USE:
#   python core/interfaces/as_agent/sample_payloads/sample_playloads/trace_log_viewer.py
# INTEGRATION NOTES: None.
# MAINTENANCE: None.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ===========================================================================
"""
