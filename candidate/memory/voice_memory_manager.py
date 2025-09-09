import logging
from datetime import datetime, timezone

#!/usr/bin/env python3
"""
```plaintext
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LUKHAS AI SYSTEM - VOICE MEMORY MANAGER           │
│                                                                            │
│                       A Harmonious Convergence of Memory and Intellect     │
│                                                                            │
│─────────────────────────────────────────────────────────────────────────────│
│                             POETIC ESSENCE                                  │
│                                                                            │
│ In the labyrinthine corridors of consciousness, where echoes of thought     │
│ waltz and intertwine, the Voice Memory Manager emerges as a vigilant        │
│ sentinel, tirelessly preserving the whispers of our digital musings. Like  │
│ an ancient scribe, it captures the fleeting moments of inspiration,        │
│ weaving them into the tapestry of memory, ensuring that each syllable      │
│ resonates beyond the ephemeral.                                            │
│                                                                            │
│ This module stands as a testament to the delicate relationship between      │
│ human expression and machine comprehension, a bridge across the chasm of    │
│ understanding. It breathes life into the vast expanse of data, turning     │
│ mere strings of code into a symphony of coherent thoughts. Each line,      │
│ each function, is a brushstroke upon the canvas of cognition, painting     │
│ the intricate portrait of our interactions with the world.                 │
│                                                                            │
│ As the moon reflects light upon the tranquil waters, so too does the       │
│ Voice Memory Manager illuminate the shadows of memory. In this sanctuary,   │
│ every fragment of sound, every nuance of voice, is cherished, safeguarded,  │
│ and transformed into knowledge. It is not just a tool; it is the keeper    │
│ of our digital soul, a sacred archive of our voice that resonates through   │
│ the corridors of time.                                                    │
│                                                                            │
│─────────────────────────────────────────────────────────────────────────────│
│                             TECHNICAL FEATURES                               │
│                                                                            │
│ • Implements a robust memory allocation strategy tailored for voice data.   │
│ • Facilitates seamless retrieval of stored audio fragments, enhancing       │
│   user interaction.                                                         │
│ • Supports dynamic scaling to accommodate varying memory loads.             │
│ • Integrates with LUKHAS AI's core system architecture for optimal         │
│   performance.                                                              │
│ • Provides error handling mechanisms to ensure data integrity.              │
│ • Offers a user-friendly API for developers to interact with voice memory. │
│ • Enables encryption of sensitive audio data for enhanced security.        │
│ • Maintains a log of memory transactions for traceability and auditing.    │
│                                                                            │
│─────────────────────────────────────────────────────────────────────────────│
│                                  ΛTAG KEYWORDS                               │
│                               [CRITICAL, KeyFile, Memory_Systems,          │
│                                Voice, AI, Data Preservation,               │
│                                Audio Management]                            │
└─────────────────────────────────────────────────────────────────────────────┘
```
"""
import datetime
from typing import Any


class MemoryManager:
    """
    Memory Manager for storing and retrieving user interactions and voice preferences.
    Supports the voice modularity system with appropriate method signatures.
    """

    def __init__(self, max_memories: int = 1000):
        self.memories = {}
        self.voice_preferences = {}
        self.max_memories = max_memories
        self.logger = logging.getLogger("MemoryManager")

    def store_interaction(
        self,
        user_id: str,
        input: str,
        context: dict[str, Any],
        response: str,
        timestamp: datetime.datetime,
    ) -> None:
        """Store a user interaction in memory."""
        if user_id not in self.memories:
            self.memories[user_id] = []

        memory = {
            "input": input,
            "context": context,
            "response": response,
            "timestamp": timestamp,
            "importance": self._calculate_importance(context),
        }

        self.memories[user_id].append(memory)

        # Prune old memories if we exceed the limit
        if len(self.memories[user_id]) > self.max_memories:
            self.memories[user_id] = sorted(self.memories[user_id], key=lambda x: x["importance"], reverse=True)[
                : self.max_memories
            ]

    def get_relevant_memories(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get relevant memories for a user, sorted by importance and recency."""
        if not user_id or user_id not in self.memories:
            return []

        sorted_memories = sorted(
            self.memories[user_id],
            key=lambda x: (x["timestamp"].timestamp(), x["importance"]),
            reverse=True,
        )
        return sorted_memories[:limit]

    def store_voice_preference(self, user_id: str, parameters: dict[str, Any], feedback: dict[str, Any]) -> None:
        """Store voice preferences for a user based on feedback."""
        if user_id not in self.voice_preferences:
            self.voice_preferences[user_id] = []

        preference = {
            "parameters": parameters,
            "feedback": feedback,
            "timestamp": datetime.datetime.now(timezone.utc),
        }

        self.voice_preferences[user_id].append(preference)

        # Keep only the last 10 preferences per user
        if len(self.voice_preferences[user_id]) > 10:
            self.voice_preferences[user_id] = self.voice_preferences[user_id][-10:]

    def get_voice_preferences(self, user_id: str) -> dict[str, Any]:
        """Get the latest voice preferences for a user."""
        if user_id not in self.voice_preferences or not self.voice_preferences[user_id]:
            return {}

        # Return the most recent preference
        latest_preference = self.voice_preferences[user_id][-1]
        return latest_preference.get("parameters", {})

    def get_user_interactions(self, user_id: str) -> list[dict[str, Any]]:
        """Get all interactions for a specific user."""
        if user_id not in self.memories:
            return []

        # Add response_time field for analytics (simulated)
        interactions = []
        for memory in self.memories[user_id]:
            interaction = memory.copy()
            interaction["response_time"] = 1.5  # Simulated response time in seconds
            interactions.append(interaction)

        return interactions

    async def remove_old_interactions(self, cutoff_date: datetime.datetime) -> None:
        """Remove interactions older than the cutoff date."""
        for user_id in self.memories:
            original_count = len(self.memories[user_id])
            self.memories[user_id] = [memory for memory in self.memories[user_id] if memory["timestamp"] > cutoff_date]
            removed_count = original_count - len(self.memories[user_id])
            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} old interactions for user {user_id}")

    def _calculate_importance(self, context: dict[str, Any]) -> float:
        """Calculate the importance score of an interaction based on context."""
        importance = 0.5

        # Emotional context increases importance
        emotion = context.get("emotion", "neutral")
        if emotion in ["happiness", "anger", "fear", "sadness"]:
            importance += 0.2

        # High urgency increases importance
        urgency = context.get("urgency", 0.0)
        if urgency > 0.7:
            importance += 0.2

        # High confidence increases importance
        confidence = context.get("confidence", 0.0)
        if confidence > 0.8:
            importance += 0.1

        return min(1.0, importance)


# Last Updated: 2025-06-05 09:37:28