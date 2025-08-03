"""
════════════════════════════════════════════════════════════════════════════════
║ MODULE: dream_limiter.py
║ PATH: lukhas/creativity/dream_systems/dream_limiter.py
║ DESCRIPTION: Limit emotionally recursive dream sequences during replay.
║ VERSION: 1.0.0
║ ΛTAG: dream_limiter, affect_delta, driftScore
════════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from core.common import get_logger

logger = get_logger(__name__)


@dataclass
class DreamLimiterConfig:
    """Configuration for DreamLimiter."""

    window_size: int = 10
    recursion_threshold: float = 0.6


class DreamLimiter:
    """Ensure emotionally recursive loops don't dominate dream replay."""

    def __init__(self, config: Optional[DreamLimiterConfig] = None):
        self.config = config or DreamLimiterConfig()
        self.emotion_window: List[str] = []
        self.driftScore: float = 0.0  # ΛTAG: driftScore
        self.affect_delta: float = 0.0  # ΛTAG: affect_delta

    def _dominant_emotion(self, dream: Dict[str, Any]) -> Optional[str]:
        emotion_vector = dream.get("emotion_vector", {})
        if not emotion_vector:
            return None
        return max(emotion_vector, key=emotion_vector.get)

    def filter_dreams(self, dreams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter dreams to balance novelty vs. integration."""
        filtered: List[Dict[str, Any]] = []
        for dream in dreams:
            emotion = self._dominant_emotion(dream)
            if emotion:
                predicted_window = self.emotion_window + [emotion]
                count = predicted_window.count(emotion)
                ratio = count / len(predicted_window)
                self.driftScore = ratio
                self.affect_delta = max(self.affect_delta, ratio)
                if (
                    len(self.emotion_window) >= self.config.window_size - 1
                    and ratio > self.config.recursion_threshold
                ):
                    logger.debug(
                        "DreamLimiter skipped dream due to recursion: %s ratio=%.2f",
                        emotion,
                        ratio,
                    )
                    continue
                self.emotion_window = predicted_window[-self.config.window_size :]
            filtered.append(dream)
        return filtered