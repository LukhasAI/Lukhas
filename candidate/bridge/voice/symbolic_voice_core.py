import json
import os
import subprocess
import sys

import requests

from candidate.core.common import get_logger

# Configure logging
logger = get_logger(__name__)

API_KEY = os.getenv("VOICE_SYSTEMS_API_KEY", "")
LUKHAS = {
    "name": "Lukhas",
    "persona": "Symbolic AGI Voice",
    "voice_id": os.getenv("LUKHAS_VOICE_ID", ""),
}

VOICES = {
    "lukhas_core": {
        "id": os.getenv("LUKHAS_CORE_VOICE_ID", ""),  # Original Lukhas voice
        "style": "default",
    },
    "dream_lukhas": {
        "id": os.getenv("DREAM_LUCAS_VOICE_ID", ""),  # Quiet, crackling fire intimacy
        "style": "narration",
    },
    "guardian_lukhas": {
        "id": os.getenv("GUARDIAN_LUCAS_VOICE_ID", ""),  # Strong, noble, protector
        "style": "news",
    },
    "reflective_lukhas": {
        "id": os.getenv("REFLECTIVE_LUCAS_VOICE_ID", ""),  # British, melancholic, articulate
        "style": "conversational",
    },
}


def speak(text, traits=None):
    if not text:
        text = "Hello, Gonzo. I am Lukhas. Your symbolic voice interface."

    stability = 0.6
    similarity_boost = 0.8

    if traits:
        if traits.get("openness", 0) > 0.75:
            text = "🌌 " + text + " 🌌"
        if traits.get("conscientiousness", 0) > 0.8:
            stability += 0.2
        if traits.get("extraversion", 0) > 0.7:
            similarity_boost += 0.1
        if traits.get("agreeableness", 0) > 0.85:
            text = text.replace(".", " ❤️.")
        if traits.get("neuroticism", 0) > 0.5:
            stability -= 0.2

    voice_choice = "lukhas_core"

    if traits:
        if isinstance(traits, str):
            traits = {"mode": traits}
        elif isinstance(traits, dict) and "mode" not in traits:
            possible_mode = next(iter(traits.keys()))
            traits = {"mode": possible_mode}

    if traits:
        mode = traits.get("mode") if isinstance(traits, dict) else traits
        if isinstance(mode, str):
            mode = mode.lower()
            if mode in ["dream", "dreaming", "lucid"]:
                voice_choice = "dream_lukhas"
            elif mode in ["guardian", "protect", "shield"]:
                voice_choice = "guardian_lukhas"
            elif mode in ["reflect", "reflection", "ponder"]:
                voice_choice = "reflective_lukhas"

    selected_voice = VOICES[voice_choice]

    logger.info(f"🔊 Speaking: {text}")
    logger.info(f"🧠 Traits: {traits}")
    logger.info(f"🗣️ Selected voice: {voice_choice}")
    logger.info(f"🎛️ Voice config: stability={stability}, similarity={similarity_boost}")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice['id']}"

    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": selected_voice["style"],
        },
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    logger.info("📡 ElevenLabs API response status:", response.status_code)
    logger.info("📦 ElevenLabs response headers:", response.headers)

    logger.info("🧪 Content-Type:", response.headers.get("Content-Type"))
    logger.info("🧪 Response size:", len(response.content))

    if response.status_code == 200 and response.content:
        audio_file = "/tmp/cove-last.mp3"
        logger.info("✅ Writing audio file...")
        try:
            with open(audio_file, "wb") as f:
                f.write(response.content)
            logger.info(f"🔉 Audio saved at: {audio_file} ({len(response.content)} bytes)")

            script_path = "/tmp/play_last_audio.sh"
            with open(script_path, "w") as script:
                script.write(f"afplay {audio_file}\n")
            os.chmod(script_path, 0o755)

            if os.path.isfile(audio_file):
                try:
                    subprocess.run(["pbcopy"], input=audio_file.encode(), check=True)
                    logger.info("📋 Audio path copied to clipboard.")
                    logger.info("🚀 You can replay this with:", script_path)
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Failed to copy to clipboard: {e}")
                except FileNotFoundError:
                    logger.warning("⚠️ pbcopy command not found (macOS only)")
            else:
                logger.error("❌ Audio file was not created despite successful response.")
        except Exception as e:
            logger.error("❌ Error saving audio file:", e)
    else:
        logger.error("❌ Failed to generate audio.")
        logger.error("📡 Status code:", response.status_code)
        try:
            logger.error("📜 Response body:", response.json())
        except Exception:
            logger.error("📜 Raw response:", response.text)


if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "Hello, Gonzo."
    traits = {}

    if len(sys.argv) > 2:
        raw_arg = sys.argv[2]
        if raw_arg.startswith("{") and raw_arg.endswith("}"):
            try:
                traits = json.loads(raw_arg)
            except json.JSONDecodeError:
                traits = {}
        else:
            traits = {"mode": raw_arg}

    logger.info(f"🧪 Invoking speak with message='{message}' and traits={traits}")
    speak(message, traits)
