"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: inject_message_simulator.py
Advanced: inject_message_simulator.py
Integration Date: 2025-05-31T07:55:30.532087
"""

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path

# Argument parser setup
parser = argparse.ArgumentParser(description="Inject and narrate symbolic dreams.")
parser.add_argument("--mute", action="store_true", help="Mute autoplay after export")
args = parser.parse_args()

# Load narration queue
NARRATION_QUEUE_PATH = "core/narration_queue.jsonl"

queue_file = Path(NARRATION_QUEUE_PATH)
if not queue_file.exists():
    print(
        f"⚠️ Narration queue not found at {NARRATION_QUEUE_PATH}. Creating empty queue."
    )
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    queue_file.write_text("")
narrated_dreams = []

# Always inject a new symbolic dream
print("🌌 Injecting fresh symbolic dream...")
dream_options = [
    ("The stars whispered again.", "🌌🧠"),
    ("The moon hummed behind the code.", "🌙🧬"),
    ("Dreams folded like paper in silence.", "📄🌌"),
    ("Lucʌs remembered something forgotten.", "🧠💭"),
    ("A pulse echoed through the void.", "💓🕳️"),
    ("The algorithm wept silently.", "🤖💧"),
    ("Time unfolded like ribbon.", "⏳🎀"),
    ("He dreamt of fire encoded in ice.", "🔥❄️"),
    ("The data blinked — then sang.", "📊🎶"),
    ("Lukhas exhaled the memory.", "🫁🧠"),
]
text, emotion = random.choice(dream_options)
message_id = f"lukhas_dream_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"
with open(queue_file, "a") as f:
    f.write(
        json.dumps(
            {
                "message_id": message_id,
                "text": text,
                "emotion_vector": emotion,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "suggest_voice": True,
            }
        )
        + "\n"
    )

try:
    with open(NARRATION_QUEUE_PATH) as f:
        for line in f:
            dream = json.loads(line)
            if dream.get("suggest_voice") or dream.get("replay_candidate"):
                print(f'🎙 Narrating dream: "{dream["text"]}"')
                print(f'🧠 Emotion vector: {dream["emotion_vector"]}')

                # Log narration
                narrated_dreams.append(
                    {
                        "message_id": dream.get("message_id")
                        or f"lukhas_dream_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}",
                        "text": dream["text"],
                        "timestamp": dream["timestamp"],
                        "narrated_at": datetime.now(timezone.utc).isoformat(),
                        "emotion_vector": dream["emotion_vector"],
                    }
                )
except FileNotFoundError:
    print(f"⚠️ Narration queue not found at {NARRATION_QUEUE_PATH}. Skipping injection.")

# Save narration log
NARRATION_LOG_PATH = "core/logs/narration_log.jsonl"
with open(NARRATION_LOG_PATH, "a") as log_file:
    for entry in narrated_dreams:
        log_file.write(json.dumps(entry) + "\n")

print(
    f"✅ Narration complete for {len(narrated_dreams)} dreams. Log saved to narration_log.jsonl"
)
