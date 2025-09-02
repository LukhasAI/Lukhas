"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: audio_exporter.py
Advanced: audio_exporter.py
Integration Date: 2025-05-31T07:55:31.349978
"""

"""
╭────────────────────────────────────────────────────────────╮
│  LUCΛS :: Audio Exporter                                   │
│  Prepares narrated dreams for export as audio (.mp3/.wav)  │
╰────────────────────────────────────────────────────────────╯

Future features:
- Integrate with ElevenLabs or pyttsx3 for TTS
- Save each dream narration with emotional metadata
- Enable symbolic filename generation
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import security utilities
try:
    from candidate.core.interfaces.voice.core.sayit import (
        SecurityError, get_env_var, safe_subprocess_run)
except ImportError:
    # Fallback for development

    def safe_subprocess_run(command, **kwargs):
        return subprocess.run(command, **kwargs)

    class SecurityError(Exception):
        pass

    def get_env_var(name, default=None, required=False):
        return os.getenv(name, default)


try:
    from elevenlabs.client import ElevenLabs
except ImportError:
    try:
        elevenlabs_enabled = True
    except ImportError as e:
        elevenlabs_enabled = False
        print(f"❌ ElevenLabs import failed: {e}")
else:
    elevenlabs_enabled = True

sys.path.append("/Users/grdm_admin/Developer/lukhas_core")

# Optional: ElevenLabs TTS integration
try:
    elevenlabs_enabled = True
except Exception as e:
    elevenlabs_enabled = False
    print(f"❌ ElevenLabs import failed: {e}")

ELEVENLABS_API_KEY = get_env_var("ELEVENLABS_API_KEY", "your_elevenlabs_api_key_here")
LUKHAS_VOICE_ID = "s0XGIcqmceN2l7kjsqoZ"

EXPORT_PATH = Path("exports/audio")
LOG_PATH = Path("core/logs/narration_log.jsonl")

EXPORT_PATH.mkdir(parents=True, exist_ok=True)

try:
    args
except NameError:

    class Args:
        mute = True

    args = Args()


def generate_filename(dream):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    tier = dream.get("tier", "T?")
    mood = "-".join(dream.get("tags", [])[:2]) or "symbolic"
    return f"{tier}_{mood}_{timestamp}.txt"


def export_as_text_narration():
    if not LOG_PATH.exists():
        print("❌ narration_log.jsonl not found.")
        return

    with open(LOG_PATH, encoding="utf-8") as f:
        logs = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"❌ Skipping malformed log line: {e}")

    print(f"🔁 Found {len(logs)} dreams in narration_log.jsonl")

    for entry in logs:
        filename = generate_filename(entry)
        filepath = EXPORT_PATH / filename
        with open(filepath, "w", encoding="utf-8") as out:
            out.write("🎙 LUCΛS VOICE EXPORT\n")
            out.write(f"Text: {entry['text']}\n")
            out.write(f"Tier: {entry.get('tier', '-')}\n")
            out.write(f"Emotion Vector: {entry.get('emotion_vector', {})}\n")
            out.write(f"Narrated At: {entry.get('narrated_at', '')}\n")

        if elevenlabs_enabled:
            try:
                print(
                    f"🧪 Attempting to generate audio for: {entry.get('message_id',"}
                                                                     'unknown_dream')}"
                )
                client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                audio_stream = client.text_to_speech.convert(
                    text=entry["text"],
                    voice_id=LUKHAS_VOICE_ID,
                    model_id="eleven_monolingual_v1",
                )

                audio_bytes = b"".join(audio_stream)

                audio_path = filepath.with_suffix(".mp3")

                if not audio_bytes:
                    print("❌ No audio returned from ElevenLabs.")
                else:
                    print("📦 Audio stream received and converted to bytes")

                    with open(audio_path, "wb") as f:
                        f.write(audio_bytes)
                    if "args" in globals() and not args.mute:
                        try:
                            # Use secure subprocess wrapper
                            safe_subprocess_run(["afplay", str(audio_path)], timeout=10)
                        except SecurityError as e:
                            print(f"⚠️ Audio playback failed: {e}")

                    if audio_path.exists() and audio_path.stat().st_size > 0:
                        print(f"🎧 Exported audio: {audio_path.name}")
                    else:
                        print(f"⚠️ Audio file created but appears empty: {audio_path}")

            except Exception as e:
                print(f"❌ ElevenLabs export failed for {entry['message_id']}: {e}")
                if not args.mute:
                    try:
                        # Use secure subprocess wrapper with input sanitization
                        clean_text = entry["text"].replace('"', '\\"')[
                            :200
                        ]  # Limit length and escape quotes
                        safe_subprocess_run(["say", clean_text], timeout=30)
                        print("🗣️ Fallback narration via macOS 'say' succeeded.")
                    except SecurityError as say_error:
                        print(f"⚠️ Fallback 'say' failed: {say_error}")
        else:
            print("⚠️ ElevenLabs not enabled — skipping audio generation.")

    print(f"✅ Exported {len(logs)} symbolic narrations as text/audio → {EXPORT_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export LUKHAS narrations as audio")
    parser.add_argument(
        "--mute", action="store_true", help="Mute autoplay after export"
    )
    args = parser.parse_args()

    print("🧠 Starting LUKHAS audio exporter...")
    export_as_text_narration()
    print("✅ Done.")
