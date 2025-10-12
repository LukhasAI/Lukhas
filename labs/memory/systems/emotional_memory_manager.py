from datetime import timezone

"""
Enhanced memory manager for creativity and dream systems.
Provides emotional modulation capabilities for memory processing.

DEPRECATED: This module is deprecated and will be removed in v2.0.0.
Please use lukhas.memory.EmotionalMemoryManager instead.
"""
import warnings
from typing import Any, Optional

warnings.warn(
    "lukhas.memory.systems.emotional_memory_manager is deprecated and will be removed in v2.0.0. "
    "Please use lukhas.memory.EmotionalMemoryManager instead. "
    "The new implementation provides enhanced emotional state tracking and memory-emotion integration.",
    DeprecationWarning,
    stacklevel=2,
)


class EmotionalModulator:
    """
    Provides emotional modulation capabilities for memory and creative processes.

    This class handles emotional state adjustments, memory emotion mapping,
    and integration with the broader creative system.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the emotional modulator.

        Args:
            config: Configuration dictionary for the modulator
        """
        self.config = config or {}
        self.emotional_state = {}
        self.memory_contexts = {}
        self.modulation_history = []

    def modulate_emotion(
        self, emotion_data: dict[str, Any], context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Modulate emotional data based on context and history.

        Args:
            emotion_data: Current emotional state data
            context: Optional context for modulation

        Returns:
            Modulated emotional state
        """
        if not emotion_data:
            return self._default_emotional_state()

        modulated = emotion_data.copy()

        # Apply context-based adjustments
        if context:
            # Adjust based on memory context
            if context.get("memory_type") == "dream":
                modulated["intensity"] = modulated.get("intensity", 0.5) * 1.2
            elif context.get("memory_type") == "creative":
                modulated["creativity"] = modulated.get("creativity", 0.5) * 1.1

        # Store in history for future reference
        self.modulation_history.append(
            {
                "original": emotion_data,
                "modulated": modulated,
                "context": context,
                "timestamp": self._get_timestamp(),
            }
        )

        return modulated

    def integrate_memory_emotion(self, memory_data: dict[str, Any], emotion_data: dict[str, Any]) -> dict[str, Any]:
        """
        Integrate memory data with emotional information.

        Args:
            memory_data: Memory information to integrate
            emotion_data: Emotional state data

        Returns:
            Integrated memory-emotion data
        """
        integrated = {
            "lukhas.memory": memory_data,
            "emotion": emotion_data,
            "integration_score": self._calculate_integration_score(memory_data, emotion_data),
            "enhanced_memory": self._enhance_memory_with_emotion(memory_data, emotion_data),
        }

        return integrated

    def get_emotional_context(self, memory_id: str) -> dict[str, Any]:
        """
        Get emotional context for a specific memory.

        Args:
            memory_id: Identifier for the memory

        Returns:
            Emotional context data
        """
        return self.memory_contexts.get(memory_id, self._default_emotional_state())

    def update_emotional_state(self, new_state: dict[str, Any]) -> None:
        """
        Update the current emotional state.

        Args:
            new_state: New emotional state data
        """
        self.emotional_state.update(new_state)

    def _default_emotional_state(self) -> dict[str, Any]:
        """Return default emotional state."""
        return {
            "valence": 0.5,
            "arousal": 0.5,
            "intensity": 0.5,
            "creativity": 0.5,
            "stability": 0.8,
        }

    def _calculate_integration_score(self, memory_data: dict[str, Any], emotion_data: dict[str, Any]) -> float:
        """Calculate integration score between memory and emotion."""
        # Simple scoring based on overlap and compatibility
        score = 0.5

        if memory_data.get("emotional_tags") and emotion_data.get("primary_emotion"):
            if emotion_data["primary_emotion"] in memory_data["emotional_tags"]:
                score += 0.3

        if memory_data.get("intensity") and emotion_data.get("intensity"):
            intensity_diff = abs(memory_data["intensity"] - emotion_data["intensity"])
            score += max(0, 0.2 - intensity_diff)

        return min(1.0, score)

    def _enhance_memory_with_emotion(self, memory_data: dict[str, Any], emotion_data: dict[str, Any]) -> dict[str, Any]:
        """Enhance memory data with emotional information."""
        enhanced = memory_data.copy()

        # Add emotional enhancement
        enhanced["emotional_enhancement"] = {
            "primary_emotion": emotion_data.get("primary_emotion"),
            "emotional_intensity": emotion_data.get("intensity", 0.5),
            "emotional_valence": emotion_data.get("valence", 0.5),
            "enhancement_timestamp": self._get_timestamp(),
        }

        return enhanced

    def _get_timestamp(self) -> str:
        """Get current timestamp for logging."""
        import datetime

        return datetime.datetime.now(timezone.utc).isoformat()
