import logging

logger = logging.getLogger(__name__)
"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                        LUCΛS :: Dream Voice Pipeline                         │
│               Module: dream_voice_pipeline.py | Tier: 3+                     │
│   Links symbolic dream entries to voice playback using narration queues     │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This pipeline connects dream logs, narration controllers, and emotional feedback
    to produce a symbolic narration loop through Lukhas' voice.

    It pulls from:
    • narration_queue.jsonl (from dream_narrator_queue.py)
    • dream_summary_log.jsonl (optional fallback)
    • lukhas_user_config.json for tier settings
    • symbolic_utils for tier labeling and emoji formatting

    Outputs narration to:
    • Terminal preview
    • Voice module simulation (e.g. lukhas_voice_narrator.py)

    Future:
    • ElevenLabs integration or TTS module
    • Emotion-aware voice profile routing
"""

import logging

from lukhas.core.common import get_logger
from lukhas.core.interfaces.as_agent.sys.nias.narration_controller import (
    fetch_narration_entries,
    filter_narration_queue,
    load_user_settings,
)
from lukhas.core.modules.nias.__init__ import narrate_dreams

# Configure logging
logger = get_logger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def run_dream_voice_pipeline():
    user_settings = load_user_settings()
    tier = user_settings.get("tier", 0)

    # Keep as print since this is CLI user output
    print(f"🔐 LUKHAS TIER LEVEL: {tier} — Checking narration queue...\n")

    narration_entries = fetch_narration_entries()
    filtered = filter_narration_queue(narration_entries, tier)

    if not filtered:
        # Keep as print since this is CLI user output
        print("🌙 No narration-ready entries found.")
        return

    # Keep as print since this is CLI user output
    print(f"🎙 Narrating {len(filtered)} symbolic entries...")
    for entry in filtered:
        narrate_dreams([entry])


if __name__ == "__main__":
    run_dream_voice_pipeline()

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│ USAGE:                                                                       │
│   python core/modules/nias/dream_voice_pipeline.py                          │
│ OUTPUT:                                                                      │
│   Narrates all valid dreams from narration_queue.jsonl                      │
│   Tier-filtered + emotionally symbolic output                               │
╰──────────────────────────────────────────────────────────────────────────────╯
"""
