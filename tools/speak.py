# ===============================================================
# 📂 FILE: tools/speak.py
# 🧠 PURPOSE: CLI command to speak symbolically with tier checks, emotion style, and logging
# ===============================================================

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone

from edge_tts import Communicate

from core.compliance.tier_manager import get_user_tier

DEFAULT_VOICE = "en-US-AriaNeural"
LOG_PATH = "symbolic_output_log.jsonl"

EMOTION_VOICES = {
    "neutral": "en-US-AriaNeural",
    "gentle": "en-GB-SoniaNeural",
    "urgent": "en-US-GuyNeural",
    "narrator": "en-US-DavisNeural",
    "soft": "en-AU-NatashaNeural",
}


async def speak(text, voice=DEFAULT_VOICE, preview=False):
    communicate = Communicate(text=text, voice=voice)
    await communicate.save("lucas_output.mp3")
    if not preview:
        os.system(
            "afplay lucas_output.mp3"
        )
        # For macOS. Use another player for Linux/Win.


def log_output(text, tier, voice):
    entry = {
        "action": "voice",
        "text": text,
        "tier": tier,
        "voice": voice,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    print("\n🎤 LUCAS VOICE MODE — Speak With Intention")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    parser = argparse.ArgumentParser(
        description="🎤 Speak via symbolic voice system (Lucas voice)"
    )
    parser.add_argument(
        "text", type=str, nargs="+", help="The phrase Lucas should speak aloud."
    )
    parser.add_argument(
        "--emotion",
        type=str,
        default="neutral",
        help="Symbolic emotion voice (gentle, urgent, soft, narrator)",
    )
    parser.add_argument(
        "--preview", action="store_true", help="Preview voice without audio playback"
    )
    args = parser.parse_args()

    tier = get_user_tier()
    if tier < 2:
        print("⛔ You do not have permission to speak symbolically. Tier 2+ required.")
        return

    sentence = " ".join(args.text)
    voice = EMOTION_VOICES.get(args.emotion.lower(), DEFAULT_VOICE)

    print(f"🧠 Tier {tier} | 🎙️ Emotion: {args.emotion} | Voice: {voice}")
    print(f'💬 Lucas would say: "{sentence}"')
    if not args.preview:
        asyncio.run(speak(sentence, voice=voice, preview=False))
    log_output(sentence, tier, voice)
    print("📝 Logged to symbolic_output_log.jsonl\n")


if __name__ == "__main__":
    main()
