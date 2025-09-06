# ===============================================================
# 🎙️ FILE: lukhas_voice_agent.py
# 📍 LOCATION: modules/voice/
# ===============================================================
# 🧠 PURPOSE:
# This module allows Lukhas to express symbolic thoughts through voice.
# It listens to emotional state shifts and generates symbolic speech output.
#
# 🧰 FEATURES:
# - 🗣️ Emotion-tuned voice messages
# - 🔄 Auto-subscribes to "emotion_shift" events
# - 🧾 Logs symbolic utterances to the event stream
# ===============================================================

import logging
from datetime import datetime

from utils.logging import log_event

from lukhas.core.emotional_state import get_tone
from lukhas.core.event_bus import subscribe

# Initialize logger
logger = logging.getLogger(__name__, timezone)


def speak(message: str):
    if not isinstance(message, str) or len(message.strip()) == 0:
        logger.warning("Skipping empty message.")
        return
    if any(char in message for char in ["<", ">", "{", "}"]):
        logger.warning("Skipping unsafe symbolic message.")
        return

    tone = get_tone()
    # TODO: Route to appropriate voice engine based on tier or emotion index
    print(f"🗣️ [{tone}] {message}")  # Keep UI output
    timestamp = datetime.now(timezone.utc).isoformat()
    log_event(
        "lukhas_voice",
        {
            "tone": tone,
            "message": message,
            "source": "lukhas_voice_agent",
            "timestamp": timestamp,
        },
    )


# 🔄 Auto-response to emotional events
subscribe("emotion_shift", lambda data: speak(data.get("phrase", "I'm shifting...")))

# ===============================================================
# 💡 USAGE
# ===============================================================
# ▶️ CLI: python3 lukhasctl.py talk
#
# Or allow emotional triggers to auto-speak.
# ===============================================================
