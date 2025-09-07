"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: generate_payload_cli.py
Advanced: generate_payload_cli.py
Integration Date: 2025-05-31T07:55:30.549413
"""
from datetime import timezone

import streamlit as st

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                  LUCΛS :: SYMBOLIC PAYLOAD GENERATOR (CLI)                  │
│              Version: v1.0 | Interactive CLI for Crafting Test Payloads      │
│               Author: Gonzo R.D.M & GPT-4o | 2025-04-16                       │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This script interactively guides you through creating a symbolic message
    payload and saves it to the sample_payloads/ directory for use in
    inject_message_simulator.py, dream_injector.py, or validation tests.

"""

import json
from datetime import datetime
from pathlib import Path

DEST_DIR = Path("core/sample_payloads/", timezone)
DEST_DIR.mkdir(parents=True, exist_ok=True)


def generate_payload():
    print("\n🧠 LUCΛS SYMBOLIC PAYLOAD GENERATOR")
    print("────────────────────────────────────────────")

    message_id = input("Message ID (e.g., msg_2025_custom_01): ").strip()
    content = input("Symbolic Message Content: ").strip()
    tags = input("Comma-separated Tags (e.g., dream,focus,calm): ").strip().split(",")
    required_tier = int(input("Required Tier (0–5): ").strip())

    print("\n🎭 Enter Emotion Vector Values (0.0 to 1.0)")
    joy = float(input("→ Joy: "))
    stress = float(input("→ Stress: "))
    calm = float(input("→ Calm: "))
    longing = float(input("→ Longing: "))

    widget = input("Source Widget (e.g., intention_cube): ").strip()
    dream_fallback = input("Allow Dream Fallback? (y/n): ").strip().lower() == "y"
    allow_replay = input("Allow Replay? (y/n): ").strip().lower() == "y"

    payload = {
        "message_id": message_id,
        "content": content,
        "tags": [t.strip() for t in tags],
        "required_tier": required_tier,
        "emotion_vector": {
            "joy": joy,
            "stress": stress,
            "calm": calm,
            "longing": longing,
        },
        "source_widget": widget,
        "dream_fallback": dream_fallback,
        "allow_replay": allow_replay,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    file_path = DEST_DIR / f"{message_id}.json"
    with open(file_path, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\n✅ Payload saved to {file_path}")


if __name__ == "__main__":
    generate_payload()

"""
──────────────────────────────────────────────────────────────────────────────────────
USAGE:
    From project root, run:
        python core/modules/nias/generate_payload_cli.py

NOTES:
    - Payload will be saved inside core/sample_payloads/
    - You can validate or simulate it immediately
──────────────────────────────────────────────────────────────────────────────────────
"""
