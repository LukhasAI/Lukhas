#!/usr/bin/env python3

"""
LUKHAS AI Emotion Module
=======================

VAD affect processing, mood regulation, and emotional intelligence
for human-AI empathetic interactions.

Trinity Framework Component: 🧠 Consciousness
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

# Import configuration and feature flags
from lukhas.observability.matriz_decorators import instrument
from lukhas.observability.matriz_emit import emit

logger = logging.getLogger(__name__)

# Feature flag for emotion activation
EMOTION_ACTIVE = os.getenv("EMOTION_ACTIVE", "false").lower() == "true"

class EmotionWrapper:
    """
    Budget-optimized emotion processing wrapper with dry-run safety.

    Provides core emotion functions while staying within $1.00 budget:
    - VAD (Valence, Arousal, Dominance) affect processing
    - Mood regulation with hormone receptors
    - Empathy and emotional regulation subsystems
    - Feature flag control for safe operation
    """

    def __init__(self):
        self._initialized = False
        self._emotional_state = {
            "valence": 0.0,      # Positive/negative emotion (-1.0 to 1.0)
            "arousal": 0.0,      # Energy level (0.0 to 1.0)
            "dominance": 0.0,    # Control level (0.0 to 1.0)
            "mood": "neutral",
            "empathy_level": 0.5,
            "regulation_active": False
        }
        self._emotion_history = []

    @instrument("emotion_initialization")
    def initialize(self) -> bool:
        """Initialize emotion processing system"""
        try:
            if not EMOTION_ACTIVE:
                logger.info("Emotion module initialized in dry-run mode")
                emit({"ntype": "emotion_dry_run_init", "state": {"status": "safe_mode"}})
                self._initialized = True
                return True

            # Real initialization would happen here
            logger.info("Emotion module initialized in active mode")
            emit({"ntype": "emotion_active_init", "state": {"status": "active_mode"}})
            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"Emotion initialization failed: {e}")
            emit({"ntype": "emotion_init_error", "state": {"error": str(e)}})
            return False

    @instrument("emotion_process")
    def process_emotion(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process emotional input using VAD model

        Args:
            input_data: Dictionary containing text, context, or other emotional cues

        Returns:
            Dictionary with VAD scores and emotional analysis
        """
        if not self._initialized:
            self.initialize()

        try:
            if not EMOTION_ACTIVE:
                # Dry-run: return safe mock values
                result = {
                    "dry_run": True,
                    "valence": 0.0,
                    "arousal": 0.0,
                    "dominance": 0.0,
                    "emotion": "neutral",
                    "confidence": 0.5
                }
                emit({"ntype": "emotion_process_dry_run", "state": result})
                return result

            # Real emotion processing would integrate with candidate/emotion modules here
            result = self._analyze_vad_affect(input_data)
            emit({"ntype": "emotion_process_active", "state": {"input_keys": list(input_data.keys())}})
            return result

        except Exception as e:
            logger.error(f"Emotion processing failed: {e}")
            emit({"ntype": "emotion_process_error", "state": {"error": str(e)}})
            return {"error": str(e), "valence": 0.0, "arousal": 0.0, "dominance": 0.0}

    @instrument("emotion_regulate_mood")
    def regulate_mood(self, target_state: Optional[str] = None,
                     hormone_context: Optional[dict[str, float]] = None) -> dict[str, Any]:
        """
        Regulate mood with hormone receptor influence

        Args:
            target_state: Desired emotional state
            hormone_context: Hormone levels (cortisol, dopamine, serotonin, oxytocin)

        Returns:
            Mood regulation results and new emotional state
        """
        try:
            if not EMOTION_ACTIVE:
                # Dry-run: return safe regulation
                result = {
                    "dry_run": True,
                    "regulation_applied": False,
                    "mood": "neutral",
                    "hormone_influence": "none",
                    "stability": 1.0
                }
                emit({"ntype": "mood_regulate_dry_run", "state": result})
                return result

            # Real mood regulation would happen here
            result = self._apply_mood_regulation(target_state, hormone_context)
            emit({"ntype": "mood_regulate_active", "state": {"target": target_state}})
            return result

        except Exception as e:
            logger.error(f"Mood regulation failed: {e}")
            emit({"ntype": "mood_regulate_error", "state": {"error": str(e)}})
            return {"error": str(e), "regulation_applied": False}

    @instrument("emotion_track_valence")
    def track_valence(self, window_size: int = 10) -> dict[str, Any]:
        """
        Track valence trends over time

        Args:
            window_size: Number of recent emotions to analyze

        Returns:
            Valence tracking analysis and trends
        """
        try:
            if not EMOTION_ACTIVE:
                # Dry-run: return neutral tracking
                result = {
                    "dry_run": True,
                    "current_valence": 0.0,
                    "trend": "stable",
                    "variance": 0.0,
                    "window_size": window_size
                }
                emit({"ntype": "valence_track_dry_run", "state": result})
                return result

            # Real valence tracking
            result = self._analyze_valence_trends(window_size)
            emit({"ntype": "valence_track_active", "state": {"window_size": window_size}})
            return result

        except Exception as e:
            logger.error(f"Valence tracking failed: {e}")
            emit({"ntype": "valence_track_error", "state": {"error": str(e)}})
            return {"error": str(e), "current_valence": 0.0}

    def _analyze_vad_affect(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze VAD affect from input data (active mode only)"""
        # Simplified VAD analysis for budget efficiency
        text = input_data.get("text", "")

        # Basic sentiment analysis (would use more sophisticated methods in production)
        valence = self._calculate_valence(text)
        arousal = self._calculate_arousal(text)
        dominance = self._calculate_dominance(text)

        # Update emotional state
        self._emotional_state["valence"] = valence
        self._emotional_state["arousal"] = arousal
        self._emotional_state["dominance"] = dominance

        return {
            "valence": valence,
            "arousal": arousal,
            "dominance": dominance,
            "emotion": self._map_vad_to_emotion(valence, arousal, dominance),
            "confidence": 0.7,
            "timestamp": input_data.get("timestamp")
        }

    def _calculate_valence(self, text: str) -> float:
        """Calculate valence from text (simplified for budget)"""
        positive_words = ["good", "great", "excellent", "happy", "joy", "love", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "sad", "angry", "hate", "horrible"]

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        if len(words) == 0:
            return 0.0

        score = (positive_count - negative_count) / len(words)
        return max(-1.0, min(1.0, score * 5))  # Scale and clamp

    def _calculate_arousal(self, text: str) -> float:
        """Calculate arousal from text (simplified for budget)"""
        high_arousal_words = ["excited", "energetic", "thrilled", "intense", "passionate", "urgent"]

        words = text.lower().split()
        arousal_count = sum(1 for word in words if word in high_arousal_words)

        if len(words) == 0:
            return 0.5

        score = arousal_count / len(words)
        return min(1.0, score * 10 + 0.3)  # Scale with baseline

    def _calculate_dominance(self, text: str) -> float:
        """Calculate dominance from text (simplified for budget)"""
        dominant_words = ["control", "command", "lead", "decide", "strong", "confident"]
        submissive_words = ["follow", "weak", "uncertain", "confused", "helpless"]

        words = text.lower().split()
        dominant_count = sum(1 for word in words if word in dominant_words)
        submissive_count = sum(1 for word in words if word in submissive_words)

        if len(words) == 0:
            return 0.5

        score = (dominant_count - submissive_count) / len(words)
        return max(0.0, min(1.0, score * 5 + 0.5))

    def _map_vad_to_emotion(self, valence: float, arousal: float, dominance: float) -> str:
        """Map VAD scores to basic emotion categories"""
        if valence > 0.3:
            if arousal > 0.5:
                return "excited" if dominance > 0.5 else "happy"
            else:
                return "content" if dominance > 0.5 else "peaceful"
        elif valence < -0.3:
            if arousal > 0.5:
                return "angry" if dominance > 0.5 else "anxious"
            else:
                return "frustrated" if dominance > 0.5 else "sad"
        else:
            return "neutral"

    def _apply_mood_regulation(self, target_state: Optional[str],
                              hormone_context: Optional[dict[str, float]]) -> dict[str, Any]:
        """Apply mood regulation algorithms (active mode only)"""
        current_valence = self._emotional_state["valence"]
        regulation_applied = False

        if target_state == "positive" and current_valence < 0.2:
            # Apply positive mood regulation
            self._emotional_state["valence"] = min(1.0, current_valence + 0.3)
            regulation_applied = True
        elif target_state == "calm" and self._emotional_state["arousal"] > 0.7:
            # Apply calming regulation
            self._emotional_state["arousal"] = max(0.0, self._emotional_state["arousal"] - 0.4)
            regulation_applied = True

        # Hormone influence simulation
        hormone_influence = "none"
        if hormone_context:
            if hormone_context.get("serotonin", 0.5) > 0.7:
                self._emotional_state["valence"] += 0.1
                hormone_influence = "serotonin_boost"
            if hormone_context.get("cortisol", 0.5) > 0.7:
                self._emotional_state["arousal"] += 0.2
                hormone_influence = "cortisol_stress"

        return {
            "regulation_applied": regulation_applied,
            "mood": self._map_vad_to_emotion(
                self._emotional_state["valence"],
                self._emotional_state["arousal"],
                self._emotional_state["dominance"]
            ),
            "hormone_influence": hormone_influence,
            "new_valence": self._emotional_state["valence"],
            "stability": 0.8
        }

    def _analyze_valence_trends(self, window_size: int) -> dict[str, Any]:
        """Analyze valence trends over recent history (active mode only)"""
        if len(self._emotion_history) < 2:
            return {
                "current_valence": self._emotional_state["valence"],
                "trend": "insufficient_data",
                "variance": 0.0,
                "window_size": window_size
            }

        recent_valences = [entry["valence"] for entry in self._emotion_history[-window_size:]]
        current_valence = self._emotional_state["valence"]

        # Calculate trend
        if len(recent_valences) >= 2:
            trend_slope = (recent_valences[-1] - recent_valences[0]) / len(recent_valences)
            if trend_slope > 0.1:
                trend = "improving"
            elif trend_slope < -0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        # Calculate variance
        if len(recent_valences) > 1:
            mean_valence = sum(recent_valences) / len(recent_valences)
            variance = sum((v - mean_valence) ** 2 for v in recent_valences) / len(recent_valences)
        else:
            variance = 0.0

        return {
            "current_valence": current_valence,
            "trend": trend,
            "variance": variance,
            "window_size": len(recent_valences),
            "trend_slope": trend_slope if 'trend_slope' in locals() else 0.0
        }

    def get_emotional_state(self) -> dict[str, Any]:
        """Get current emotional state"""
        return self._emotional_state.copy()

    def get_feature_flag_status(self) -> dict[str, Any]:
        """Get emotion feature flag status"""
        return {
            "EMOTION_ACTIVE": EMOTION_ACTIVE,
            "dry_run_mode": not EMOTION_ACTIVE,
            "initialized": self._initialized
        }

# Global instance for module access
_emotion_wrapper = None

def get_emotion_wrapper() -> EmotionWrapper:
    """Get the global emotion wrapper instance"""
    global _emotion_wrapper
    if _emotion_wrapper is None:
        _emotion_wrapper = EmotionWrapper()
    return _emotion_wrapper

# Convenience functions for direct access
def process_emotion(input_data: dict[str, Any]) -> dict[str, Any]:
    """Process emotional input using VAD model"""
    return get_emotion_wrapper().process_emotion(input_data)

def regulate_mood(target_state: Optional[str] = None,
                 hormone_context: Optional[dict[str, float]] = None) -> dict[str, Any]:
    """Regulate mood with hormone receptor influence"""
    return get_emotion_wrapper().regulate_mood(target_state, hormone_context)

def track_valence(window_size: int = 10) -> dict[str, Any]:
    """Track valence trends over time"""
    return get_emotion_wrapper().track_valence(window_size)

# Export the main interface
__all__ = [
    "EmotionWrapper",
    "get_emotion_wrapper",
    "process_emotion",
    "regulate_mood",
    "track_valence",
    "EMOTION_ACTIVE"
]
