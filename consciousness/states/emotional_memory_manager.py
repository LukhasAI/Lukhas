"""

#TAG:consciousness
#TAG:states
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - EMOTIONAL MEMORY MANAGER
║ Memory management with emotional tagging and modulation
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: emotional_memory_manager.py
║ Path: lukhas/memory/emotional_memory_manager.py
║ Version: 1.0.0 | Created: 2025-07-26
║ Authors: LUKHAS AI Architecture Team
╠══════════════════════════════════════════════════════════════════════════════════
║ TODO: Update to use unified tier system and user identity
║ - Add user_id parameter to all public methods
║ - Use @require_identity decorator for tier validation
║ - Add consent checking for emotional data access
║ - Implement tier-based feature restrictions
║ - See emotional_memory_manager_unified.py for reference implementation
╚══════════════════════════════════════════════════════════════════════════════════
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_manager import BaseMemoryManager


class EmotionalMemoryManager(BaseMemoryManager):
    """
    Memory manager with emotional tagging and modulation.

    Extends BaseMemoryManager with:
    - Emotional state tracking
    - Memory-emotion integration
    - Emotional intensity modulation
    - Valence and arousal tracking
    - Emotion-based memory retrieval
    """

    def __init__(
        self, config: Optional[Dict[str, Any]] = None, base_path: Optional[Path] = None
    ):
        """Initialize emotional memory manager."""
        super().__init__(config, base_path)

        # Emotional configuration
        self.emotion_config = {
            "default_valence": 0.5,
            "default_arousal": 0.5,
            "default_intensity": 0.5,
            "emotion_decay_rate": 0.1,
            "integration_threshold": 0.7,
            **self.config.get("emotion", {}),
        }

        # Emotional state tracking
        self.emotional_states: Dict[str, Dict[str, Any]] = {}
        self.emotion_history: List[Dict[str, Any]] = []

        # Primary emotions mapping
        self.primary_emotions = {
            "joy": {"valence": 0.9, "arousal": 0.7},
            "sadness": {"valence": 0.2, "arousal": 0.3},
            "anger": {"valence": 0.1, "arousal": 0.9},
            "fear": {"valence": 0.2, "arousal": 0.8},
            "surprise": {"valence": 0.5, "arousal": 0.9},
            "disgust": {"valence": 0.1, "arousal": 0.6},
            "trust": {"valence": 0.8, "arousal": 0.4},
            "anticipation": {"valence": 0.7, "arousal": 0.6},
        }

        self.logger.info(
            "EmotionalMemoryManager initialized", emotion_config=self.emotion_config
        )

    async def store(
        self,
        memory_data: Dict[str, Any],
        memory_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store memory with emotional tagging.

        Analyzes content for emotional significance and tags accordingly.
        """
        # Generate ID if not provided
        if not memory_id:
            memory_id = self.generate_memory_id("emem")

        try:
            # Extract or infer emotional state
            emotional_state = self._extract_emotional_state(memory_data, metadata)
            self.emotional_states[memory_id] = emotional_state

            # Calculate emotional significance
            significance = self._calculate_emotional_significance(emotional_state)

            # Prepare enhanced metadata
            enhanced_metadata = {
                **(metadata or {}),
                "emotional_state": emotional_state,
                "emotional_significance": significance,
                "emotional_tags": self._generate_emotional_tags(emotional_state),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            # Package memory with emotional data
            memory_package = {
                "data": memory_data,
                "metadata": enhanced_metadata,
                "emotion": {
                    "state": emotional_state,
                    "significance": significance,
                    "modulation_history": [],
                },
            }

            # Save to disk
            self._save_to_disk(memory_id, memory_package)

            # Update index
            self._update_index(memory_id, enhanced_metadata)

            # Update emotion history
            self._update_emotion_history(memory_id, emotional_state)

            self.logger.info(
                "Emotional memory stored",
                memory_id=memory_id,
                primary_emotion=emotional_state.get("primary_emotion"),
                significance=significance,
            )

            return {
                "status": "success",
                "memory_id": memory_id,
                "emotional_state": emotional_state,
                "significance": significance,
            }

        except Exception as e:
            self.logger.error(
                "Failed to store emotional memory", memory_id=memory_id, error=str(e)
            )
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def retrieve(
        self, memory_id: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve memory with emotional context.

        Applies emotional modulation based on current context.
        """
        try:
            # Load memory package
            memory_package = self._load_from_disk(memory_id)

            # Get current emotional state
            emotional_state = self.emotional_states.get(
                memory_id, memory_package["emotion"]["state"]
            )

            # Apply emotional modulation if context provided
            if context and context.get("current_emotion"):
                modulated_data = self._modulate_memory_by_emotion(
                    memory_package["data"], emotional_state, context["current_emotion"]
                )
            else:
                modulated_data = memory_package["data"]

            # Apply emotion decay
            decayed_state = self._apply_emotion_decay(emotional_state)
            self.emotional_states[memory_id] = decayed_state

            self.logger.info(
                "Emotional memory retrieved",
                memory_id=memory_id,
                emotion_intensity=decayed_state.get("intensity"),
            )

            return {
                "status": "success",
                "data": modulated_data,
                "metadata": {
                    **memory_package["metadata"],
                    "current_emotional_state": decayed_state,
                    "modulation_applied": context is not None,
                },
            }

        except FileNotFoundError:
            self.logger.error("Memory not found", memory_id=memory_id)
            return {"status": "error", "error": f"Memory not found: {memory_id}"}
        except Exception as e:
            self.logger.error(
                "Failed to retrieve emotional memory", memory_id=memory_id, error=str(e)
            )
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def update(
        self, memory_id: str, updates: Dict[str, Any], merge: bool = True
    ) -> Dict[str, Any]:
        """Update memory with emotional re-evaluation."""
        try:
            # Retrieve current state
            current = await self.retrieve(memory_id)
            if current["status"] == "error":
                return current

            # Update data
            if merge:
                updated_data = {**current["data"], **updates}
            else:
                updated_data = updates

            # Re-evaluate emotional state
            new_emotional_state = self._extract_emotional_state(
                updated_data, current["metadata"]
            )

            # Blend with existing emotional state
            blended_state = self._blend_emotional_states(
                self.emotional_states.get(memory_id, {}), new_emotional_state
            )

            # Store updated memory
            result = await self.store(
                updated_data,
                memory_id,
                {
                    **current["metadata"],
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            self.logger.info(
                "Emotional memory updated",
                memory_id=memory_id,
                emotion_change=self._calculate_emotion_change(
                    self.emotional_states.get(memory_id, {}), blended_state
                ),
            )

            return result

        except Exception as e:
            self.logger.error(
                "Failed to update emotional memory", memory_id=memory_id, error=str(e)
            )
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def delete(self, memory_id: str, soft_delete: bool = True) -> Dict[str, Any]:
        """Delete memory with emotional cleanup."""
        try:
            # Clean up emotional states
            if memory_id in self.emotional_states:
                del self.emotional_states[memory_id]

            if soft_delete:
                # Mark as deleted in index
                if memory_id in self._memory_index:
                    self._memory_index[memory_id]["deleted"] = True
                    self._memory_index[memory_id]["deleted_at"] = datetime.now(
                        timezone.utc
                    ).isoformat()
                    self._save_index()
            else:
                # Remove from disk
                file_path = self.base_path / f"{memory_id}.json"
                if file_path.exists():
                    file_path.unlink()

                # Remove from index
                if memory_id in self._memory_index:
                    del self._memory_index[memory_id]
                    self._save_index()

            self.logger.info(
                "Emotional memory deleted", memory_id=memory_id, soft_delete=soft_delete
            )

            return {"status": "success"}

        except Exception as e:
            self.logger.error(
                "Failed to delete emotional memory", memory_id=memory_id, error=str(e)
            )
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def search(
        self, criteria: Dict[str, Any], limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories with emotional filtering.

        Supports emotion-based search criteria.
        """
        results = []

        # Extract emotion-specific criteria
        emotion_filter = criteria.pop("emotion", None)
        min_intensity = criteria.pop("min_intensity", 0.0)
        valence_range = criteria.pop("valence_range", None)
        arousal_range = criteria.pop("arousal_range", None)

        for memory_id, index_data in self._memory_index.items():
            # Skip deleted memories
            if index_data.get("deleted", False):
                continue

            # Load emotional state
            emotional_state = index_data.get("emotional_state", {})

            # Apply emotion filters
            if (
                emotion_filter
                and emotional_state.get("primary_emotion") != emotion_filter
            ):
                continue

            if emotional_state.get("intensity", 0) < min_intensity:
                continue

            if valence_range:
                valence = emotional_state.get("valence", 0.5)
                if not (valence_range[0] <= valence <= valence_range[1]):
                    continue

            if arousal_range:
                arousal = emotional_state.get("arousal", 0.5)
                if not (arousal_range[0] <= arousal <= arousal_range[1]):
                    continue

            # Load and check other criteria
            try:
                memory_data = self._load_from_disk(memory_id)
                if self._matches_criteria(memory_data["data"], criteria):
                    results.append(
                        {
                            "memory_id": memory_id,
                            "data": memory_data["data"],
                            "emotional_state": emotional_state,
                            "metadata": index_data,
                        }
                    )
            except Exception as e:
                self.logger.warning(
                    "Failed to load memory during search",
                    memory_id=memory_id,
                    error=str(e),
                )

        # Sort by emotional significance if no limit specified
        if not limit:
            results.sort(
                key=lambda x: x["metadata"].get("emotional_significance", 0),
                reverse=True,
            )

        # Apply limit
        if limit and len(results) > limit:
            results = results[:limit]

        return results

    # === Emotional-specific methods ===

    async def get_emotional_context(self, memory_id: str) -> Dict[str, Any]:
        """Get detailed emotional context for a memory."""
        try:
            memory = await self.retrieve(memory_id)
            if memory["status"] == "error":
                return memory

            emotional_state = self.emotional_states.get(memory_id, {})

            return {
                "status": "success",
                "memory_id": memory_id,
                "emotional_context": {
                    "current_state": emotional_state,
                    "primary_emotion": emotional_state.get("primary_emotion"),
                    "secondary_emotions": emotional_state.get("secondary_emotions", []),
                    "valence": emotional_state.get("valence", 0.5),
                    "arousal": emotional_state.get("arousal", 0.5),
                    "intensity": emotional_state.get("intensity", 0.5),
                    "tags": emotional_state.get("tags", []),
                },
            }

        except Exception as e:
            self.logger.error(
                "Failed to get emotional context", memory_id=memory_id, error=str(e)
            )
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def update_emotional_state(
        self, memory_id: str, new_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update the emotional state of a memory."""
        try:
            # Verify memory exists
            memory = await self.retrieve(memory_id)
            if memory["status"] == "error":
                return memory

            # Update emotional state
            self.emotional_states[memory_id] = {
                **self.emotional_states.get(memory_id, {}),
                **new_state,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

            # Update in metadata
            self._update_index(
                memory_id, {"emotional_state": self.emotional_states[memory_id]}
            )

            self.logger.info(
                "Emotional state updated",
                memory_id=memory_id,
                new_emotion=new_state.get("primary_emotion"),
            )

            return {
                "status": "success",
                "memory_id": memory_id,
                "updated_state": self.emotional_states[memory_id],
            }

        except Exception as e:
            self.logger.error(
                "Failed to update emotional state", memory_id=memory_id, error=str(e)
            )
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    # === Private helper methods ===

    def _extract_emotional_state(
        self, memory_data: Dict[str, Any], metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract or infer emotional state from memory data."""
        # Check if emotional state is explicitly provided
        if metadata and "emotional_state" in metadata:
            return metadata["emotional_state"]

        # Simple emotion detection based on keywords
        text_content = str(memory_data)
        detected_emotions = []

        emotion_keywords = {
            "joy": ["happy", "joy", "excited", "delighted", "pleased"],
            "sadness": ["sad", "unhappy", "depressed", "melancholy", "grief"],
            "anger": ["angry", "furious", "mad", "irritated", "annoyed"],
            "fear": ["afraid", "scared", "terrified", "anxious", "worried"],
            "surprise": ["surprised", "amazed", "astonished", "shocked"],
            "disgust": ["disgusted", "revolted", "repulsed", "sick"],
            "trust": ["trust", "confident", "secure", "safe"],
            "anticipation": ["anticipate", "expect", "hope", "look forward"],
        }

        # Detect emotions based on keywords
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_content.lower() for keyword in keywords):
                detected_emotions.append(emotion)

        # Default to neutral if no emotions detected
        if not detected_emotions:
            primary_emotion = "neutral"
            valence = 0.5
            arousal = 0.5
        else:
            primary_emotion = detected_emotions[0]
            emotion_profile = self.primary_emotions.get(
                primary_emotion, {"valence": 0.5, "arousal": 0.5}
            )
            valence = emotion_profile["valence"]
            arousal = emotion_profile["arousal"]

        return {
            "primary_emotion": primary_emotion,
            "secondary_emotions": (
                detected_emotions[1:] if len(detected_emotions) > 1 else []
            ),
            "valence": valence,
            "arousal": arousal,
            "intensity": 0.5
            + (0.1 * len(detected_emotions)),  # More emotions = higher intensity
            "stability": 0.8,
            "tags": detected_emotions,
        }

    def _calculate_emotional_significance(
        self, emotional_state: Dict[str, Any]
    ) -> float:
        """Calculate emotional significance score."""
        intensity = emotional_state.get("intensity", 0.5)
        arousal = emotional_state.get("arousal", 0.5)
        valence_extremity = abs(emotional_state.get("valence", 0.5) - 0.5) * 2

        # Significance based on intensity, arousal, and valence extremity
        significance = intensity * 0.4 + arousal * 0.3 + valence_extremity * 0.3

        return min(1.0, significance)

    def _generate_emotional_tags(self, emotional_state: Dict[str, Any]) -> List[str]:
        """Generate descriptive emotional tags."""
        tags = []

        # Primary emotion
        primary = emotional_state.get("primary_emotion")
        if primary:
            tags.append(primary)

        # Valence-based tags
        valence = emotional_state.get("valence", 0.5)
        if valence > 0.7:
            tags.append("positive")
        elif valence < 0.3:
            tags.append("negative")
        else:
            tags.append("neutral")

        # Arousal-based tags
        arousal = emotional_state.get("arousal", 0.5)
        if arousal > 0.7:
            tags.append("high_energy")
        elif arousal < 0.3:
            tags.append("low_energy")

        # Intensity-based tags
        intensity = emotional_state.get("intensity", 0.5)
        if intensity > 0.7:
            tags.append("intense")
        elif intensity < 0.3:
            tags.append("mild")

        return tags

    def _modulate_memory_by_emotion(
        self,
        memory_data: Dict[str, Any],
        memory_emotion: Dict[str, Any],
        current_emotion: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Modulate memory retrieval based on current emotional state."""
        # Simple modulation - enhance if emotions match
        memory_valence = memory_emotion.get("valence", 0.5)
        current_valence = current_emotion.get("valence", 0.5)

        # Calculate emotional congruence
        congruence = 1 - abs(memory_valence - current_valence)

        # Add modulation metadata
        modulated_data = memory_data.copy()
        modulated_data["_emotional_modulation"] = {
            "congruence": congruence,
            "enhanced": congruence > self.emotion_config["integration_threshold"],
            "memory_emotion": memory_emotion.get("primary_emotion"),
            "current_emotion": current_emotion.get("primary_emotion"),
        }

        return modulated_data

    def _apply_emotion_decay(self, emotional_state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply decay to emotional intensity over time."""
        decayed_state = emotional_state.copy()

        # Reduce intensity
        current_intensity = decayed_state.get("intensity", 0.5)
        decay_rate = self.emotion_config["emotion_decay_rate"]
        new_intensity = max(0.1, current_intensity - decay_rate)

        decayed_state["intensity"] = new_intensity

        # Move valence and arousal toward neutral
        decayed_state["valence"] = decayed_state.get("valence", 0.5) * 0.9 + 0.5 * 0.1
        decayed_state["arousal"] = decayed_state.get("arousal", 0.5) * 0.9 + 0.5 * 0.1

        return decayed_state

    def _blend_emotional_states(
        self, state1: Dict[str, Any], state2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Blend two emotional states."""
        # Weight by intensity
        intensity1 = state1.get("intensity", 0.5)
        intensity2 = state2.get("intensity", 0.5)
        total_intensity = intensity1 + intensity2

        if total_intensity == 0:
            weight1 = weight2 = 0.5
        else:
            weight1 = intensity1 / total_intensity
            weight2 = intensity2 / total_intensity

        return {
            "primary_emotion": (
                state2.get("primary_emotion")
                if intensity2 > intensity1
                else state1.get("primary_emotion")
            ),
            "secondary_emotions": list(
                set(
                    state1.get("secondary_emotions", [])
                    + state2.get("secondary_emotions", [])
                )
            ),
            "valence": state1.get("valence", 0.5) * weight1
            + state2.get("valence", 0.5) * weight2,
            "arousal": state1.get("arousal", 0.5) * weight1
            + state2.get("arousal", 0.5) * weight2,
            "intensity": (intensity1 + intensity2) / 2,
            "stability": min(
                state1.get("stability", 0.8), state2.get("stability", 0.8)
            ),
        }

    def _calculate_emotion_change(
        self, old_state: Dict[str, Any], new_state: Dict[str, Any]
    ) -> float:
        """Calculate magnitude of emotional change."""
        if not old_state or not new_state:
            return 0.0

        valence_change = abs(
            old_state.get("valence", 0.5) - new_state.get("valence", 0.5)
        )
        arousal_change = abs(
            old_state.get("arousal", 0.5) - new_state.get("arousal", 0.5)
        )
        intensity_change = abs(
            old_state.get("intensity", 0.5) - new_state.get("intensity", 0.5)
        )

        return (valence_change + arousal_change + intensity_change) / 3

    def _update_emotion_history(
        self, memory_id: str, emotional_state: Dict[str, Any]
    ) -> None:
        """Update emotion history tracking."""
        self.emotion_history.append(
            {
                "memory_id": memory_id,
                "emotional_state": emotional_state,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Keep only recent history (last 100 entries)
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]

    def _matches_criteria(self, data: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if data matches search criteria."""
        for key, value in criteria.items():
            if key not in data:
                return False
            if data[key] != value:
                return False
        return True

    async def get_statistics(self) -> Dict[str, Any]:
        """Get emotional memory statistics."""
        base_stats = await super().get_statistics()

        # Calculate emotion distribution
        emotion_counts = {}
        total_intensity = 0.0
        total_valence = 0.0
        total_arousal = 0.0

        for state in self.emotional_states.values():
            emotion = state.get("primary_emotion", "unknown")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_intensity += state.get("intensity", 0)
            total_valence += state.get("valence", 0)
            total_arousal += state.get("arousal", 0)

        num_emotional_memories = len(self.emotional_states)

        # Add emotional-specific stats
        emotional_stats = {
            **base_stats,
            "emotional_memories": num_emotional_memories,
            "emotion_distribution": emotion_counts,
            "average_intensity": (
                total_intensity / num_emotional_memories
                if num_emotional_memories > 0
                else 0
            ),
            "average_valence": (
                total_valence / num_emotional_memories
                if num_emotional_memories > 0
                else 0
            ),
            "average_arousal": (
                total_arousal / num_emotional_memories
                if num_emotional_memories > 0
                else 0
            ),
            "emotion_history_length": len(self.emotion_history),
        }

        return emotional_stats
