"""
════════════════════════════════════════════════════════════════════════════════
║ 🎤 LUKHAS AI - VOICE PERSONALITY
║ Personality layer for voice output customization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: voice_personality.py
║ Path: lukhas/core/voice_systems/voice_personality.py
║ Version: 1.0.0 | Created: 2025-06-20 | Modified: 2025-07-25
║ Authors: LUKHAS AI Voice Team | Codex
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ Generates personalized voice responses with emotional nuance.
╚═══════════════════════════════════════════════════════════════════════════════
"""

from typing import Dict, Any, Optional, List, Union
import logging
from datetime import datetime

from .voice_profiling import VoiceProfileManager, VoiceProfile

logger = logging.getLogger(__name__)

class VoicePersonalityIntegrator:
    """Integrates personality traits and emotional modulation into voice synthesis"""

    def __init__(self,
                profile_manager: VoiceProfileManager,
                config: Optional[Dict[str, Any]] = None):
        """Initialize voice personality integrator

        Args:
            profile_manager: Reference to voice profile manager
            config: Optional configuration parameters
        """
        self.profile_manager = profile_manager
        self.config = config or {}

        # Initialize personality state
        self.emotional_state = {
            "current_emotion": "neutral",
            "emotion_intensity": 0.5,
            "emotional_history": []
        }

        # Voice modulation parameters
        self.base_modulation = {
            "pitch": 1.0,
            "rate": 1.0,
            "volume": 1.0,
            "emphasis": 0.5
        }

        logger.info("Voice personality integrator initialized")

    def adapt_to_emotion(self,
                      emotion: str,
                      intensity: float = 0.5,
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Adapt voice modulation based on emotion

        Args:
            emotion: The target emotion to express
            intensity: Emotion intensity from 0.0 to 1.0
            context: Optional additional context

        Returns:
            Dict containing adapted voice modulation parameters
        """
        self._update_emotional_state(emotion, intensity)

        # Get base profile for this emotion
        profile = self._get_emotional_profile(emotion)
        modulation = dict(self.base_modulation)

        # Apply emotion-specific modulation
        if emotion == "joy":
            modulation["pitch"] *= 1.1
            modulation["rate"] *= 1.2
            modulation["emphasis"] *= 1.3
        elif emotion == "sadness":
            modulation["pitch"] *= 0.9
            modulation["rate"] *= 0.8
            modulation["emphasis"] *= 0.7
        elif emotion == "anger":
            modulation["volume"] *= 1.2
            modulation["emphasis"] *= 1.5
        elif emotion == "fear":
            modulation["pitch"] *= 1.2
            modulation["rate"] *= 1.3
            modulation["emphasis"] *= 0.8

        # Scale by intensity
        for param in ["pitch", "rate", "volume", "emphasis"]:
            delta = modulation[param] - self.base_modulation[param]
            modulation[param] = self.base_modulation[param] + (delta * intensity)

        return modulation

    def enhance_text_expression(self,
                            text: str,
                            emotion: str,
                            context: Optional[Dict[str, Any]] = None) -> str:
        """Enhance text for better emotional expression

        Args:
            text: Text to enhance
            emotion: Target emotion
            context: Optional additional context

        Returns:
            Enhanced text optimized for emotional expression
        """
        # Get profile for this emotion
        profile = self._get_emotional_profile(emotion)

        if not text or not emotion:
            return text

        # Add emotion-specific markers
        if emotion == "joy":
            text = f"[cheerfully] {text}"
        elif emotion == "sadness":
            text = f"[softly] {text}"
        elif emotion == "anger":
            text = f"[firmly] {text}"
        elif emotion == "fear":
            text = f"[anxiously] {text}"

        return text

    def _update_emotional_state(self, emotion: str, intensity: float) -> None:
        """Update internal emotional state tracking

        Args:
            emotion: Current emotion
            intensity: Emotion intensity
        """
        # Track emotion changes
        self.emotional_state["emotional_history"].append({
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": datetime.now().isoformat()
        })

        # Limit history length
        if len(self.emotional_state["emotional_history"]) > 100:
            self.emotional_state["emotional_history"].pop(0)

        self.emotional_state["current_emotion"] = emotion
        self.emotional_state["emotion_intensity"] = intensity

    def _get_emotional_profile(self, emotion: str) -> Optional[VoiceProfile]:
        """Get voice profile optimized for an emotion

        Args:
            emotion: Target emotion

        Returns:
            VoiceProfile if available, else None
        """
        return self.profile_manager.get_profile_for_emotion(emotion)

"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/core/voice_systems/test_voice_personality.py
║   - Coverage: N/A
║   - Linting: pylint N/A
║
║ MONITORING:
║   - Metrics: personality_hits
║   - Logs: voice_personality_logs
║   - Alerts: personality_errors
║
║ COMPLIANCE:
║   - Standards: N/A
║   - Ethics: Refer to LUKHAS Ethics Guidelines
║   - Safety: Refer to LUKHAS Safety Protocols
║
║ REFERENCES:
║   - Docs: docs/core/voice_systems/voice_personality.md
║   - Issues: github.com/lukhas-ai/lukhas/issues?label=voice_personality
║   - Wiki: N/A
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════════
"""
