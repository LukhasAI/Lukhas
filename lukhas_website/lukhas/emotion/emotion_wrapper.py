#!/usr/bin/env python3

"""
LUKHAS AI Emotion Wrapper
========================

Advanced emotion wrapper that integrates with memory and consciousness systems.
Provides budget-optimized emotion processing with memory integration.
"""

import logging
from typing import Any, Optional

from observability.matriz_decorators import instrument
from observability.matriz_emit import emit

logger = logging.getLogger(__name__)


class EmotionMemoryIntegration:
    """Integration layer between emotion processing and memory systems"""

    def __init__(self) -> None:
        self._memory_available = False
        self._consciousness_available = False
        self._memory_wrapper = None
        self._consciousness_wrapper = None

    @instrument("emotion_memory_init")
    def initialize_integrations(self) -> None:
        """Initialize integrations with memory and consciousness"""
        try:
            # Try to connect to memory system
            from memory import get_memory_wrapper

            self._memory_wrapper = get_memory_wrapper()
            self._memory_available = True
            emit({"ntype": "emotion_memory_connected", "state": {"status": "success"}})
        except (ImportError, Exception) as e:
            logger.debug(f"Memory integration unavailable: {e}")
            emit({"ntype": "emotion_memory_unavailable", "state": {"error": str(e)}})

        try:
            # Try to connect to consciousness system
            from consciousness import get_consciousness_wrapper

            self._consciousness_wrapper = get_consciousness_wrapper()
            self._consciousness_available = True
            emit(
                {
                    "ntype": "emotion_consciousness_connected",
                    "state": {"status": "success"},
                }
            )
        except (ImportError, Exception) as e:
            logger.debug(f"Consciousness integration unavailable: {e}")
            emit(
                {
                    "ntype": "emotion_consciousness_unavailable",
                    "state": {"error": str(e)},
                }
            )

    @instrument("emotion_store_memory")
    def store_emotional_memory(self, emotion_data: dict[str, Any]) -> bool:
        """Store emotional experience in memory system"""
        if not self._memory_available:
            emit(
                {
                    "ntype": "emotion_memory_store_skipped",
                    "state": {"reason": "memory_unavailable"},
                }
            )
            return False

        try:
            # Create memory fold for emotional experience
            memory_entry = {
                "type": "emotional_experience",
                "valence": emotion_data.get("valence", 0.0),
                "arousal": emotion_data.get("arousal", 0.0),
                "dominance": emotion_data.get("dominance", 0.0),
                "emotion": emotion_data.get("emotion", "neutral"),
                "context": emotion_data.get("context", {}),
                "timestamp": emotion_data.get("timestamp"),
            }

            # Store in memory system
            result = self._memory_wrapper.store_memory(
                content=memory_entry,
                memory_type="emotional",
                tags=["emotion", "vad", emotion_data.get("emotion", "neutral")],
            )

            emit(
                {
                    "ntype": "emotion_memory_stored",
                    "state": {
                        "emotion": emotion_data.get("emotion", "neutral"),
                        "success": result.get("success", False),
                    },
                }
            )

            return result.get("success", False)

        except Exception as e:
            logger.error(f"Failed to store emotional memory: {e}")
            emit({"ntype": "emotion_memory_store_error", "state": {"error": str(e)}})
            return False

    @instrument("emotion_recall_patterns")
    def recall_emotional_patterns(self, emotion_type: Optional[str] = None) -> list[dict[str, Any]]:
        """Recall similar emotional patterns from memory"""
        if not self._memory_available:
            emit(
                {
                    "ntype": "emotion_memory_recall_skipped",
                    "state": {"reason": "memory_unavailable"},
                }
            )
            return []

        try:
            # Query memory for emotional patterns
            query_tags = ["emotion", "vad"]
            if emotion_type:
                query_tags.append(emotion_type)

            memories = self._memory_wrapper.query_memories(tags=query_tags, limit=10, memory_type="emotional")

            patterns = []
            patterns = [
                m["content"]
                for m in memories.get("memories", [])
                if m.get("content", {}).get("type") == "emotional_experience"
            ]

            emit(
                {
                    "ntype": "emotion_patterns_recalled",
                    "state": {
                        "emotion_type": emotion_type,
                        "pattern_count": len(patterns),
                    },
                }
            )

            return patterns

        except Exception as e:
            logger.error(f"Failed to recall emotional patterns: {e}")
            emit({"ntype": "emotion_recall_error", "state": {"error": str(e)}})
            return []

    @instrument("emotion_consciousness_sync")
    def sync_with_consciousness(self, emotion_data: dict[str, Any]) -> dict[str, Any]:
        """Sync emotional state with consciousness system"""
        if not self._consciousness_available:
            emit(
                {
                    "ntype": "emotion_consciousness_sync_skipped",
                    "state": {"reason": "consciousness_unavailable"},
                }
            )
            return {"synced": False, "reason": "consciousness_unavailable"}

        try:
            # Send emotional state to consciousness
            consciousness_input = {
                "type": "emotional_update",
                "emotional_state": emotion_data,
                "priority": "normal",
            }

            result = self._consciousness_wrapper.process_awareness(consciousness_input)

            emit(
                {
                    "ntype": "emotion_consciousness_synced",
                    "state": {
                        "emotion": emotion_data.get("emotion", "neutral"),
                        "consciousness_response": result.get("status", "unknown"),
                    },
                }
            )

            return {
                "synced": True,
                "consciousness_response": result,
                "timestamp": emotion_data.get("timestamp"),
            }

        except Exception as e:
            logger.error(f"Failed to sync with consciousness: {e}")
            emit(
                {
                    "ntype": "emotion_consciousness_sync_error",
                    "state": {"error": str(e)},
                }
            )
            return {"synced": False, "error": str(e)}


class AdvancedEmotionWrapper:
    """
    Advanced emotion wrapper with memory and consciousness integration.
    Extends basic emotion processing with persistent memory and awareness.
    """

    def __init__(self) -> None:
        # Don't create a circular dependency - this IS the EmotionWrapper
        self._base_wrapper = None  # Not needed since this is the base
        self._integration = EmotionMemoryIntegration()
        self._initialized = False

    def _process_basic_emotion(self, input_data: str) -> dict[str, Any]:
        """Basic emotion processing - simplified but functional"""
        # Simple emotion detection based on keywords
        emotions = {
            "happy": ["great", "wonderful", "amazing", "fantastic", "love", "joy", "excited"],
            "sad": ["sad", "depressed", "down", "unhappy", "miserable", "awful"],
            "angry": ["angry", "mad", "furious", "rage", "hate", "annoyed"],
            "anxious": ["worried", "nervous", "anxious", "stressed", "concerned"],
            "calm": ["calm", "peaceful", "relaxed", "serene", "content"],
        }

        text = input_data.lower()
        detected_emotion = "neutral"
        confidence = 0.5

        for emotion, keywords in emotions.items():
            if any(keyword in text for keyword in keywords):
                detected_emotion = emotion
                confidence = 0.8
                break

        return {"emotion": detected_emotion, "confidence": confidence, "input": input_data, "processed": True}

    def _regulate_basic_mood(
        self, target_state: Optional[str] = None, hormone_context: Optional[dict[str, float]] = None
    ) -> dict[str, Any]:
        """Basic mood regulation - simplified but functional"""
        # Simple mood regulation simulation
        regulation_strategies = {
            "calm": ["breathing", "meditation", "relaxation"],
            "energetic": ["exercise", "movement", "stimulation"],
            "focused": ["concentration", "mindfulness", "clarity"],
            "happy": ["positive_thinking", "gratitude", "joy_induction"],
        }

        target = target_state or "calm"
        strategies = regulation_strategies.get(target, ["general_wellness"])

        return {
            "target_state": target,
            "strategies_applied": strategies,
            "regulation_success": True,
            "confidence": 0.7,
            "hormone_context": hormone_context or {},
        }

    @instrument("advanced_emotion_init")
    def initialize(self) -> bool:
        """Initialize advanced emotion processing with integrations"""
        try:
            # Initialize basic emotion functionality (now built-in)
            base_init = True  # Always succeeds since this IS the base
            if not base_init:
                return False

            # Initialize memory and consciousness integrations
            self._integration.initialize_integrations()

            self._initialized = True
            emit(
                {
                    "ntype": "advanced_emotion_initialized",
                    "state": {"status": "success"},
                }
            )
            return True

        except Exception as e:
            logger.error(f"Advanced emotion initialization failed: {e}")
            emit({"ntype": "advanced_emotion_init_error", "state": {"error": str(e)}})
            return False

    @instrument("advanced_emotion_process")
    def process_emotion_with_memory(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process emotion with memory integration and pattern learning"""
        if not self._initialized:
            self.initialize()

        try:
            # Basic emotion processing (now built-in)
            emotion_result = self._process_basic_emotion(input_data)

            # Recall similar patterns from memory
            current_emotion = emotion_result.get("emotion", "neutral")
            patterns = self._integration.recall_emotional_patterns(current_emotion)

            # Enhance emotion result with pattern analysis
            if patterns:
                emotion_result["pattern_match"] = True
                emotion_result["similar_patterns"] = len(patterns)
                emotion_result["pattern_confidence"] = min(1.0, len(patterns) / 5.0)
            else:
                emotion_result["pattern_match"] = False
                emotion_result["similar_patterns"] = 0
                emotion_result["pattern_confidence"] = 0.0

            # Store this emotional experience
            storage_success = self._integration.store_emotional_memory(emotion_result)
            emotion_result["memory_stored"] = storage_success

            # Sync with consciousness
            consciousness_sync = self._integration.sync_with_consciousness(emotion_result)
            emotion_result["consciousness_sync"] = consciousness_sync

            emit(
                {
                    "ntype": "advanced_emotion_processed",
                    "state": {
                        "emotion": current_emotion,
                        "patterns_found": len(patterns),
                        "memory_stored": storage_success,
                        "consciousness_synced": consciousness_sync.get("synced", False),
                    },
                }
            )

            return emotion_result

        except Exception as e:
            logger.error(f"Advanced emotion processing failed: {e}")
            emit({"ntype": "advanced_emotion_process_error", "state": {"error": str(e)}})
            return {"error": str(e), "emotion": "neutral"}

    @instrument("advanced_mood_regulate")
    def regulate_mood_with_learning(
        self,
        target_state: Optional[str] = None,
        hormone_context: Optional[dict[str, float]] = None,
    ) -> dict[str, Any]:
        """Regulate mood with learning from past successful regulations"""
        try:
            # Basic mood regulation (now built-in)
            regulation_result = self._regulate_basic_mood(target_state, hormone_context)

            # Recall past successful regulations
            if target_state:
                past_regulations = self._integration.recall_emotional_patterns(f"regulation_{target_state}")
                if past_regulations:
                    regulation_result["learned_patterns"] = len(past_regulations)
                    regulation_result["regulation_confidence"] = min(1.0, len(past_regulations) / 3.0)

            # Store regulation experience for future learning
            regulation_memory = {
                "type": "mood_regulation",
                "target_state": target_state,
                "hormone_context": hormone_context or {},
                "success": regulation_result.get("regulation_applied", False),
                "result": regulation_result,
            }

            self._integration.store_emotional_memory(regulation_memory)

            emit(
                {
                    "ntype": "advanced_mood_regulated",
                    "state": {
                        "target_state": target_state,
                        "success": regulation_result.get("regulation_applied", False),
                    },
                }
            )

            return regulation_result

        except Exception as e:
            logger.error(f"Advanced mood regulation failed: {e}")
            emit({"ntype": "advanced_mood_regulate_error", "state": {"error": str(e)}})
            return {"error": str(e), "regulation_applied": False}

    def get_emotional_insights(self) -> dict[str, Any]:
        """Get insights from emotional memory and patterns"""
        try:
            # Get recent emotional patterns
            patterns = self._integration.recall_emotional_patterns()

            if not patterns:
                return {
                    "total_experiences": 0,
                    "dominant_emotions": [],
                    "valence_trend": "neutral",
                    "insights": "Insufficient data for analysis",
                }

            # Analyze patterns
            emotions = [p.get("emotion", "neutral") for p in patterns]
            valences = [p.get("valence", 0.0) for p in patterns]

            # Find dominant emotions
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            dominant_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]

            # Calculate valence trend
            if len(valences) >= 2:
                recent_valence = sum(valences[-3:]) / len(valences[-3:])
                overall_valence = sum(valences) / len(valences)

                if recent_valence > overall_valence + 0.1:
                    valence_trend = "improving"
                elif recent_valence < overall_valence - 0.1:
                    valence_trend = "declining"
                else:
                    valence_trend = "stable"
            else:
                valence_trend = "insufficient_data"

            insights = {
                "total_experiences": len(patterns),
                "dominant_emotions": [{"emotion": e[0], "count": e[1]} for e in dominant_emotions],
                "valence_trend": valence_trend,
                "average_valence": sum(valences) / len(valences) if valences else 0.0,
                "emotional_range": max(valences) - min(valences) if valences else 0.0,
            }

            emit(
                {
                    "ntype": "emotional_insights_generated",
                    "state": {
                        "experience_count": len(patterns),
                        "dominant_emotion": (dominant_emotions[0][0] if dominant_emotions else "none"),
                    },
                }
            )

            return insights

        except Exception as e:
            logger.error(f"Failed to generate emotional insights: {e}")
            emit({"ntype": "emotional_insights_error", "state": {"error": str(e)}})
            return {"error": str(e)}


# Global instance
_advanced_emotion_wrapper = None


def get_advanced_emotion_wrapper() -> AdvancedEmotionWrapper:
    """Get the global advanced emotion wrapper instance"""
    global _advanced_emotion_wrapper
    if _advanced_emotion_wrapper is None:
        _advanced_emotion_wrapper = AdvancedEmotionWrapper()
    return _advanced_emotion_wrapper


# Export advanced interface
__all__ = [
    "AdvancedEmotionWrapper",
    "EmotionMemoryIntegration",
    "get_advanced_emotion_wrapper",
]
