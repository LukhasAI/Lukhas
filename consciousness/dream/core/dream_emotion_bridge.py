"""
Module: dream_emotion_bridge.py
Author: Jules 05
Date: 2024-07-15
Description: Provides bridge logic for dream-emotion replay triggers.
"""
from datetime import datetime

import json
from pathlib import Path

from memory.emotional import EmotionalMemory

REPLAY_QUEUE_PATH = Path("core/logs/replay_queue.jsonl")


class DreamEmotionBridge:
    """
    Provides bridge logic for dream-emotion replay triggers.
    """

    def __init__(self, emotional_memory: EmotionalMemory):
        """
        Initializes the DreamEmotionBridge.

        Args:
            emotional_memory (EmotionalMemory): The emotional memory system.
        """
        self.emotional_memory = emotional_memory

    def trigger_dream_replay_if_needed(self):
        """
        Triggers a dream replay if the current emotional state is a trigger.
        """
        current_emotional_state = self.emotional_memory.get_current_emotional_state()
        primary_emotion = current_emotional_state.get("primary_emotion")

        if self._is_trigger_emotion(primary_emotion):
            self._trigger_dream_replay(primary_emotion)

    def _is_trigger_emotion(self, emotion: str) -> bool:
        """
        Checks if the given emotion is a trigger for a dream replay.
        """
        # This is a simple implementation that can be expanded upon.
        trigger_emotions = ["sadness", "fear", "anger"]
        return emotion in trigger_emotions

    def _trigger_dream_replay(self, emotion: str):
        """
        Triggers a dream replay for the given emotion.
        """
        # This is a simple implementation that can be expanded upon.
        # It will simply add a new dream to the replay queue.
        if not REPLAY_QUEUE_PATH.exists():
            REPLAY_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
            REPLAY_QUEUE_PATH.touch()

        with open(REPLAY_QUEUE_PATH, "a") as f:
            f.write(
                json.dumps(
                    {
                        "message_id": "dream_replay_trigger",
                        "user_id": "system",
                        "score": 0,
                        "emoji": "🧠",
                        "notes": f"Dream replay triggered by emotion: {emotion}",
                        "timestamp": datetime.utcnow().isoformat(),
                        "source_widget": "DreamEmotionBridge",
                        "tier": 1,
                        "emotion_vector": {
                            "joy": 0,
                            "calm": 0,
                            "stress": 0,
                            "longing": 0,
                        },
                    }
                )
                + "\n"
            )