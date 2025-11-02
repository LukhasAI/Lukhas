"""
Emotion Cycler
==============
Cycles emotional states to stabilize drift feedback loops.
"""

import logging
from typing import Optional

from memory.emotional import EmotionalMemory

# ΛTAG: codex, emotion, drift

log = logging.getLogger(__name__)


class EmotionCycler:
    """Cycle through a predefined set of emotions."""

    def __init__(self, emotional_memory: EmotionalMemory, cycle_map: Optional[list[str]] = None):
        self.emotional_memory = emotional_memory
        self.cycle_map = cycle_map or ["neutral", "curious", "joy", "reflective"]
        self.index = 0

    def next_emotion(self) -> str:
        emotion = self.cycle_map[self.index]
        self.index = (self.index + 1) % len(self.cycle_map)
        log.debug("Cycling emotion to %s", emotion)
        self.emotional_memory.process_experience(
            experience_content={"cycle": emotion},
            explicit_emotion_values={emotion: 0.5},
        )
        return emotion
