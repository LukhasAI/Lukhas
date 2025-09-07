
"""
╭────────────────────────────────────────────────────────╮
│ 🎙 MODULE      : voice_gateway.py                      │
│ 🧾 DESCRIPTION : Modular gateway for Lukhas' voice stack │
│ 🧬 TIER SUPPORT : 0-5                                   │
│ 🖋️ AUTHOR      : LUKHAS SYSTEMS                          │
│ 📅 UPDATED     : 2025-05-03                             │
╰────────────────────────────────────────────────────────╯
"""
import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime, timezone

# from edge_tts import Communicate  # TODO: Install or implement edge_tts

# Initialize logger
logger = logging.getLogger(__name__)

# Symbolic tier/narrator voice mapping (expand as needed)
VOICE_MAP = {
    "default": "en-US-AriaNeural",
    "narrator": "en-GB-RyanNeural",
    "tier_0": "en-US-GuyNeural",
    "tier_1": "en-GB-LibbyNeural",
    "tier_2": "en-US-DavisNeural",
    "tier_3": "en-US-JennyMultilingualNeural",
    "tier_4": "en-AU-WilliamNeural",
    "tier_5": "en-US-GuyNeural",
}

# Optional: import ElevenLabs when needed
try:
    from elevenlabs import generate, save, set_api_key
except ImportError:
    generate = save = set_api_key = None

CONFIG_PATH = os.path.expanduser("~/.lukhas_voice_config.json")


def load_config():
    default = {
        "engine": "edge",
        "voice": "en-US-AriaNeural",
        "debug": False,
        "log_output": True,
        "elevenlabs_api_key": None,
    }
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            user_cfg = json.load(f)
        default.update(user_cfg)
    return default


async def speak(
    text: str,
    tier: int = 0,
    narrator: bool = False,
    output_file: str = "output.mp3",
):
    cfg = load_config()
    engine = cfg["engine"]
    debug = cfg["debug"]
    log = cfg["log_output"]

    voice_key = "narrator" if narrator else f"tier_{tier}"
    voice = VOICE_MAP.get(voice_key, VOICE_MAP["default"])

    if engine == "edge":
        communicator = Communicate(text=text, voice=voice)
        await communicator.save(output_file)

    elif engine == "eleven" and generate:
        set_api_key(cfg.get("elevenlabs_api_key"))
        audio = generate(text=text, voice=voice)
        save(audio, output_file)
    else:
        logger.error(f"Engine '{engine}' not supported or not installed.")
        return

    if log:
        with open("voice_log.jsonl", "a") as logf:
            logf.write(
                json.dumps(
                    {
                        "text": text,
                        "engine": engine,
                        "voice": voice,
                        "tier": tier,
                        "narrator": narrator,
                    }
                )
                + "\n"
            )
        try:
            with open("core/logging/symbolic_output_log.jsonl", "a") as sym_log:
                sym_log.write(
                    json.dumps(
                        {
                            "type": "voice",
                            "text": text,
                            "engine": engine,
                            "voice": voice,
                            "tier": tier,
                            "narrator": narrator,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )
                    + "\n"
                )
        except Exception as e:
            logger.warning(f"Failed to log symbolic output: {e}")

    try:
        subprocess.run(["afplay", output_file], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to play audio: {e}")
    except FileNotFoundError:
        logger.warning("afplay command not found (macOS only)")

    if not debug:
        os.remove(output_file)


# 🧪 Test mode
if __name__ == "__main__":
    asyncio.run(
        speak(
            "This is Lukhas speaking symbolically as the narrator.",
            tier=3,
            narrator=True,
        )
    )
