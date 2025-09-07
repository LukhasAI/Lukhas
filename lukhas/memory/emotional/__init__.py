"""
LUKHAS AI Emotional Memory Module
Emotional memory management and processing
Trinity Framework: ⚛️🧠🛡️

This module consolidates emotional memory functionality from various locations.
"""
from typing import List
from typing import Dict
import time
import streamlit as st

import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EmotionalMemoryManager:
    """
    Unified emotional memory manager.
    Consolidates functionality from various emotional memory implementations.
    """

    def __init__(self) -> None:
        self.emotional_memories: list[dict] = []
        self.emotion_patterns: dict[str, list] = {}
        self.memory_folds: list[dict] = []
        self.max_folds = 1000  # Maximum memory folds
        self.emotional_threshold = 0.5  # Threshold for emotional significance

        logger.info("EmotionalMemoryManager initialized")
        logger.info(f"Max folds: {self.max_folds}, Emotional threshold: {self.emotional_threshold}")

    def store_emotional_memory(
        self,
        content: Any,
        emotion_type: str,
        intensity: float,
        context: Optional[dict] = None,
    ) -> str:
        """
        Store an emotional memory.

        Args:
            content: Memory content
            emotion_type: Type of emotion (joy, sadness, anger, fear, etc.)
            intensity: Emotional intensity (0.0 to 1.0)
            context: Optional context information

        Returns:
            Memory ID
        """
        memory_id = f"EM_{datetime.now(timezone.utc).timestamp()}_{len(self.emotional_memories)}"

        memory = {
            "id": memory_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": content,
            "emotion_type": emotion_type,
            "intensity": intensity,
            "context": context or {},
            "accessed_count": 0,
            "decay_rate": 0.01,  # How fast the memory fades
        }

        self.emotional_memories.append(memory)

        # Update emotion patterns
        if emotion_type not in self.emotion_patterns:
            self.emotion_patterns[emotion_type] = []
        self.emotion_patterns[emotion_type].append(memory_id)

        # Create memory fold if intensity is significant
        if intensity >= self.emotional_threshold:
            self._create_memory_fold(memory)

        logger.debug(f"Stored emotional memory: {memory_id} ({emotion_type}, intensity: {intensity})")

        return memory_id

    def retrieve_emotional_memory(self, memory_id: str) -> Optional[dict]:
        """
        Retrieve an emotional memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory data or None if not found
        """
        for memory in self.emotional_memories:
            if memory["id"] == memory_id:
                memory["accessed_count"] += 1
                return memory.copy()

        return None

    def get_memories_by_emotion(self, emotion_type: str) -> list[dict]:
        """
        Get all memories associated with a specific emotion.

        Args:
            emotion_type: Type of emotion

        Returns:
            List of memories
        """
        memory_ids = self.emotion_patterns.get(emotion_type, [])
        memories = []

        for memory_id in memory_ids:
            memory = self.retrieve_emotional_memory(memory_id)
            if memory:
                memories.append(memory)

        return memories

    def get_recent_emotional_state(self, window_size: int = 10) -> dict[str, float]:
        """
        Get recent emotional state based on recent memories.

        Args:
            window_size: Number of recent memories to consider

        Returns:
            Dictionary of emotion types and their average intensities
        """
        recent_memories = (
            self.emotional_memories[-window_size:]
            if len(self.emotional_memories) > window_size
            else self.emotional_memories
        )

        emotional_state = {}
        emotion_counts = {}

        for memory in recent_memories:
            emotion = memory["emotion_type"]
            intensity = memory["intensity"]

            if emotion not in emotional_state:
                emotional_state[emotion] = 0
                emotion_counts[emotion] = 0

            emotional_state[emotion] += intensity
            emotion_counts[emotion] += 1

        # Calculate averages
        for emotion in emotional_state:
            if emotion_counts[emotion] > 0:
                emotional_state[emotion] /= emotion_counts[emotion]

        return emotional_state

    def _create_memory_fold(self, memory: dict) -> None:
        """
        Create a memory fold for significant emotional memories.

        Args:
            memory: Memory to fold
        """
        if len(self.memory_folds) >= self.max_folds:
            # Remove oldest fold if at maximum
            self.memory_folds.pop(0)

        fold = {
            "memory_id": memory["id"],
            "timestamp": memory["timestamp"],
            "emotion_type": memory["emotion_type"],
            "intensity": memory["intensity"],
            "fold_index": len(self.memory_folds),
            "causal_links": [],  # Links to other related memories
        }

        # Find causal links to recent memories with similar emotions
        for recent_fold in self.memory_folds[-5:]:
            if recent_fold["emotion_type"] == fold["emotion_type"]:
                fold["causal_links"].append(recent_fold["memory_id"])

        self.memory_folds.append(fold)
        logger.debug(f"Created memory fold {fold['fold_index']} for memory {memory['id']}")

    def consolidate_memories(self, time_window: float = 86400.0) -> dict[str, Any]:
        """
        Consolidate emotional memories within a time window.

        Args:
            time_window: Time window in seconds (default 24 hours)

        Returns:
            Consolidation summary
        """
        current_time = datetime.now(timezone.utc)
        consolidated = {
            "patterns": {},
            "dominant_emotions": [],
            "memory_count": 0,
            "fold_count": len(self.memory_folds),
        }

        for memory in self.emotional_memories:
            memory_time = datetime.fromisoformat(memory["timestamp"])
            time_diff = (current_time - memory_time).total_seconds()

            if time_diff <= time_window:
                emotion = memory["emotion_type"]

                if emotion not in consolidated["patterns"]:
                    consolidated["patterns"][emotion] = {
                        "count": 0,
                        "total_intensity": 0,
                        "peak_intensity": 0,
                    }

                pattern = consolidated["patterns"][emotion]
                pattern["count"] += 1
                pattern["total_intensity"] += memory["intensity"]
                pattern["peak_intensity"] = max(pattern["peak_intensity"], memory["intensity"])

                consolidated["memory_count"] += 1

        # Calculate averages and find dominant emotions
        for emotion, pattern in consolidated["patterns"].items():
            if pattern["count"] > 0:
                pattern["average_intensity"] = pattern["total_intensity"] / pattern["count"]

                consolidated["dominant_emotions"].append(
                    {
                        "emotion": emotion,
                        "strength": pattern["average_intensity"],
                        "frequency": pattern["count"],
                    }
                )

        # Sort by strength
        consolidated["dominant_emotions"].sort(key=lambda x: x["strength"], reverse=True)

        return consolidated

    def apply_emotional_decay(self, decay_factor: float = 0.99) -> None:
        """
        Apply decay to emotional memories over time.

        Args:
            decay_factor: Factor to reduce intensity (0.0 to 1.0)
        """
        for memory in self.emotional_memories:
            # Reduce intensity based on decay
            memory["intensity"] *= decay_factor

            # Remove memories that have decayed too much
            if memory["intensity"] < 0.01:
                self.emotional_memories.remove(memory)

                # Clean up emotion patterns
                emotion_type = memory["emotion_type"]
                if emotion_type in self.emotion_patterns and memory["id"] in self.emotion_patterns[emotion_type]:
                    self.emotion_patterns[emotion_type].remove(memory["id"])


# Global instance for convenience
_emotional_memory_manager = None


def get_emotional_memory_manager() -> EmotionalMemoryManager:
    """Get or create the global emotional memory manager."""
    global _emotional_memory_manager
    if _emotional_memory_manager is None:
        _emotional_memory_manager = EmotionalMemoryManager()
    return _emotional_memory_manager


# Convenience functions
def store_emotion(content: Any, emotion: str, intensity: float, context: Optional[dict] = None) -> str:
    """Store an emotional memory."""
    manager = get_emotional_memory_manager()
    return manager.store_emotional_memory(content, emotion, intensity, context)


def get_emotional_state() -> dict[str, float]:
    """Get current emotional state."""
    manager = get_emotional_memory_manager()
    return manager.get_recent_emotional_state()


# Export public interface
__all__ = [
    "EmotionalMemoryManager",
    "get_emotional_memory_manager",
    "get_emotional_state",
    "store_emotion",
]
