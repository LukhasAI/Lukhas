"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: voice_system_integrator.py
Advanced: voice_system_integrator.py
Integration Date: 2025-05-31T07:55:27.782698
"""

# 📄 MODULE: voice_system_integrator.py
# 🔎 PURPOSE: Integrated voice system combining voice profiling and synthesis
# 🛠️ VERSION: v1.0.0 • 📅 CREATED: 2025-05-08 • ✍️ AUTHOR: LUKHAS AGI

from typing import Dict, Any, Optional, List
import logging
import json
import os
from datetime import datetime

# Import voice systems
from voice.synthesis import VoiceSynthesis
from core.interfaces.voice.core.sayit import VoiceProfileManager, VoiceProfile

class VoiceSystemIntegrator:
    """
    Integrates voice profiling with voice synthesis for a cohesive voice system.
    This system provides:
    - Smart voice profile selection based on context
    - Automatic voice parameter application
    - Usage tracking and evolution
    - Provider-optimized voice settings
    """

    def __init__(self, agi_system=None):
        self.agi = agi_system
        self.logger = logging.getLogger("VoiceSystemIntegrator")

        # Initialize components
        self.voice_synthesis = VoiceSynthesis(agi_system)
        self.profile_manager = VoiceProfileManager(agi_system)

        # Track voice sessions for continuity
        self.active_sessions = {}

        # Create default profiles if none exist
        if not self.profile_manager.list_profiles():
            self._create_default_profiles()

    def _create_default_profiles(self) -> None:
        """Create default voice profiles if none exist."""
        self.logger.info("Creating default voice profiles")

        # Create a neutral profile
        self.profile_manager.create_profile("Neutral", {
            "base_pitch": 0.0,
            "base_rate": 1.0,
            "base_volume": 0.0,
            "timbre_brightness": 0.0,
            "expressiveness": 0.5,
            "articulation": 0.7,
            "breathiness": 0.2,
            "warmth": 0.5,
        })

        # Create a warm, emotive profile
        self.profile_manager.create_profile("Warm", {
            "base_pitch": -0.1,
            "base_rate": 0.95,
            "base_volume": 1.0,
            "timbre_brightness": -0.2,
            "expressiveness": 0.7,
            "articulation": 0.5,
            "breathiness": 0.3,
            "warmth": 0.8,
        })

        # Create a clear, articulate profile
        self.profile_manager.create_profile("Clear", {
            "base_pitch": 0.0,
            "base_rate": 1.05,
            "base_volume": 2.0,
            "timbre_brightness": 0.3,
            "expressiveness": 0.4,
            "articulation": 0.9,
            "breathiness": 0.1,
            "warmth": 0.4,
        })

        self.logger.info("Created 3 default voice profiles")

    def speak(self,
             text: str,
             emotion: Optional[str] = None,
             session_id: Optional[str] = None,
             context_type: str = "general",
             voice_id: Optional[str] = None,
             profile_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Speak text using the integrated voice system.

        Args:
            text: Text to synthesize
            emotion: Emotional tone (happiness, sadness, etc.)
            session_id: ID for continuous speech sessions
            context_type: Type of context (conversation, notification, etc.)
            voice_id: Specific TTS provider voice ID
            profile_id: Specific profile ID to use

        Returns:
            Result dictionary with synthesis details
        """
        # Build context for profile selection
        context = {
            "type": context_type,
            "emotion": emotion,
            "text_sample": text[:100],
            "session_id": session_id
        }

        # Select or continue with a profile
        if session_id and session_id in self.active_sessions:
            # Continue with the same profile for continuity
            profile_id = self.active_sessions[session_id]
        elif not profile_id:
            # Select a profile based on context if none specified
            profile_id = self.profile_manager.select_profile_for_context(context)

        # Get the selected profile
        profile = self.profile_manager.get_profile(profile_id) if profile_id else None

        # If we have a valid profile and session, store it for continuity
        if profile and session_id:
            self.active_sessions[session_id] = profile.id

        # Determine the best provider
        provider = self._select_provider(text, emotion, profile)

        # Get provider-specific parameters from the profile if available
        resonance_modifiers = {}
        if profile:
            provider_params = profile.get_provider_parameters(provider, emotion)

            # Convert provider params to resonance modifiers
            if provider == "elevenlabs":
                resonance_modifiers = {
                    "stability": provider_params.get("stability", 0.5),
                    "similarity_boost": provider_params.get("similarity_boost", 0.8)
                }
            elif provider == "coqui":
                resonance_modifiers = {
                    "speed": provider_params.get("speed", 1.0),
                    "noise": provider_params.get("noise", 0.667)
                }
            elif provider == "edge_tts":
                # These are already handled by the voice synthesis system
                pass

            # Use provider-specific voice ID if available
            if provider_params.get("voice_id") and not voice_id:
                voice_id = provider_params.get("voice_id")

        # Synthesize speech with all our parameters
        result = self.voice_synthesis.synthesize(
            text=text,
            emotion=emotion,
            voice_id=voice_id,
            resonance_modifiers=resonance_modifiers
        )

        # Record usage in profile
        if profile:
            usage_context = context.copy()
            usage_context["result"] = {
                "provider": result.get("provider"),
                "success": result.get("success", False)
            }
            self.profile_manager.record_usage(profile.id, usage_context)

        # Add profile info to result
        if profile:
            result["voice_profile"] = {
                "id": profile.id,
                "name": profile.name
            }

        return result

    def _select_provider(self, text: str, emotion: Optional[str], profile: Optional[VoiceProfile]) -> str:
        """Select the optimal TTS provider based on text, emotion and profile."""
        # Simple provider selection strategy
        # In a real implementation, this would be more sophisticated

        # Use emotion complexity to determine provider
        if emotion and emotion.lower() in ["sadness", "anger", "happiness"] and self._contains_complex_emotion(text):
            return "elevenlabs"

        # For longer text, Edge TTS is often more reliable
        if len(text) > 300:
            return "edge_tts"

        # Default to the configured provider in voice synthesis
        return self.voice_synthesis.provider

    def _contains_complex_emotion(self, text: str) -> bool:
        """Check if text suggests complex emotional expression."""
        # This is a simplified implementation
        emotion_indicators = [
            "!", "?!", "...", "😢", "😭", "😡", "😱", "😍", "❤️",
            "heartbroken", "devastated", "thrilled", "ecstatic",
            "furious", "terrified", "overjoyed"
        ]

        return any(indicator in text for indicator in emotion_indicators)

    def provide_feedback(self,
                       profile_id: str,
                       score: float,
                       feedback_text: str = "") -> Dict[str, Any]:
        """Provide feedback on a voice profile to evolve it."""
        feedback = {
            "score": score,
            "text": feedback_text,
            "timestamp": datetime.now().isoformat()
        }

        return self.profile_manager.provide_feedback(profile_id, feedback)

    def get_available_profiles(self) -> List[Dict[str, Any]]:
        """Get list of available voice profiles."""
        return self.profile_manager.list_profiles()

    def create_custom_profile(self,
                            name: str,
                            base_profile_id: Optional[str] = None,
                            parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a custom voice profile, optionally based on an existing one."""
        # If basing on existing profile, get its parameters
        initial_params = {}
        if base_profile_id:
            base_profile = self.profile_manager.get_profile(base_profile_id)
            if base_profile:
                initial_params = base_profile.parameters.copy()

        # Override with provided parameters
        if parameters:
            for key, value in parameters.items():
                initial_params[key] = value

        # Create the profile
        return self.profile_manager.create_profile(name, initial_params)

    def end_session(self, session_id: str) -> bool:
        """End a voice session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False