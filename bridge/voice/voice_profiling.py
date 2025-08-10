"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: voice_profiling.py
Advanced: voice_profiling.py
Integration Date: 2025-05-31T07:55:27.760932
"""

# 📄 MODULE: voice_profiling.py
# 🔎 PURPOSE: Advanced voice profiling for personalized and adaptive speech synthesis
# 🛠️ VERSION: v1.0.0 • 📅 CREATED: 2025-05-08 • ✍️ AUTHOR: LUKHAS AGI
import copy
import json
import logging
import os
import random
import uuid
from datetime import datetime
from typing import Any, Optional


class VoiceProfile:
    """
    A voice profile that defines voice characteristics and evolves over time.

    Voice profiles store:
    - Base voice parameters (pitch, rate, volume)
    - Advanced modulation parameters (articulation, expressiveness)
    - Provider-specific optimizations
    - Usage statistics and adaptation data
    """

    def __init__(self, profile_id: str, name: str, parameters: dict[str, Any] = None):
        self.id = profile_id
        self.name = name
        self.parameters = parameters or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.usage_count = 0
        self.feedback_history = []
        self.evolution_history = []

        # Provider-specific parameters
        self.provider_parameters = {
            "elevenlabs": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "voice_id": None,
            },
            "coqui": {"speed": 1.0, "noise": 0.667, "voice_id": None},
            "edge_tts": {"pitch": "+0Hz", "rate": "+0%", "voice_id": None},
        }

        # Emotion-specific adjustments
        self.emotion_adjustments = {
            "happiness": {
                "base_pitch": 0.2,
                "base_rate": 0.1,
                "expressiveness": 0.2,
            },
            "sadness": {
                "base_pitch": -0.2,
                "base_rate": -0.1,
                "expressiveness": -0.1,
            },
            "anger": {
                "base_pitch": 0.1,
                "base_rate": 0.3,
                "expressiveness": 0.3,
            },
            "fear": {
                "base_pitch": 0.3,
                "base_rate": 0.2,
                "expressiveness": -0.1,
            },
            "surprise": {
                "base_pitch": 0.3,
                "base_rate": 0.0,
                "expressiveness": 0.2,
            },
            "neutral": {
                "base_pitch": 0.0,
                "base_rate": 0.0,
                "expressiveness": 0.0,
            },
        }

        # Ensure we have all required parameters
        self._ensure_default_parameters()

    def _ensure_default_parameters(self) -> None:
        """Ensure all required parameters are present."""
        default_params = {
            "base_pitch": 0.0,  # Base pitch adjustment (-1.0 to 1.0)
            "base_rate": 1.0,  # Base speech rate (0.5 to 2.0)
            "base_volume": 0.0,  # Base volume adjustment (-1.0 to 1.0)
            "timbre_brightness": 0.0,  # Voice timbre brightness (-1.0 to 1.0)
            "expressiveness": 0.5,  # Overall expressiveness (0.0 to 1.0)
            "articulation": 0.5,  # Clarity of articulation (0.0 to 1.0)
            "breathiness": 0.2,  # Amount of breathiness (0.0 to 1.0)
            "warmth": 0.5,  # Voice warmth characteristic (0.0 to 1.0)
        }

        for key, value in default_params.items():
            if key not in self.parameters:
                self.parameters[key] = value

    def get_parameters_for_emotion(
        self, emotion: Optional[str] = None
    ) -> dict[str, Any]:
        """Get parameters adjusted for a specific emotion."""
        # Start with base parameters
        result = copy.deepcopy(self.parameters)

        # Apply emotion adjustments if applicable
        if emotion and emotion.lower() in self.emotion_adjustments:
            adjustments = self.emotion_adjustments[emotion.lower()]
            for key, adjustment in adjustments.items():
                if key in result:
                    result[key] = max(-1.0, min(1.0, result[key] + adjustment))

        return result

    def get_provider_parameters(
        self, provider: str, emotion: Optional[str] = None
    ) -> dict[str, Any]:
        """Get provider-specific parameters, adjusted for emotion if needed."""
        if provider not in self.provider_parameters:
            return {}

        # Get base provider parameters
        result = copy.deepcopy(self.provider_parameters[provider])

        # Apply provider-specific emotion adjustments
        # This could be expanded for more sophisticated behavior
        if emotion and provider == "elevenlabs":
            if emotion.lower() == "happiness":
                result["stability"] = max(0.1, result["stability"] - 0.1)
            elif emotion.lower() == "sadness":
                result["stability"] = min(0.9, result["stability"] + 0.1)

        return result

    def add_feedback(self, feedback: dict[str, Any]) -> None:
        """Add user feedback to the profile."""
        self.feedback_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "score": feedback.get("score", 0.0),
                "text": feedback.get("text", ""),
            }
        )
        self.updated_at = datetime.now().isoformat()

    def record_usage(self, context: dict[str, Any]) -> None:
        """Record profile usage with context."""
        self.usage_count += 1
        self.updated_at = datetime.now().isoformat()

    def evolve(self, direction: str = "auto") -> dict[str, Any]:
        """
        Evolve the profile based on feedback and usage patterns.

        Args:
            direction: Direction to evolve ("auto", "warmer", "clearer", "expressive")

        Returns:
            Dictionary of changes made
        """
        changes = {}

        if direction == "auto":
            # Use feedback to determine direction
            recent_feedback = (
                self.feedback_history[-5:] if self.feedback_history else []
            )
            avg_score = sum(f.get("score", 0) for f in recent_feedback) / max(
                len(recent_feedback), 1
            )

            if avg_score < 0.4:
                # Poor feedback, try significant changes
                directions = ["warmer", "clearer", "expressive"]
                direction = random.choice(directions)
            else:
                # Good feedback, make subtle refinements
                direction = "refine"

        # Apply changes based on direction
        if direction == "warmer":
            self.parameters["warmth"] = min(1.0, self.parameters["warmth"] + 0.1)
            self.parameters["breathiness"] = min(
                1.0, self.parameters["breathiness"] + 0.05
            )
            self.parameters["base_pitch"] = max(
                -1.0, self.parameters["base_pitch"] - 0.05
            )
            changes = {
                "warmth": "+0.1",
                "breathiness": "+0.05",
                "base_pitch": "-0.05",
            }

        elif direction == "clearer":
            self.parameters["articulation"] = min(
                1.0, self.parameters["articulation"] + 0.1
            )
            self.parameters["breathiness"] = max(
                0.0, self.parameters["breathiness"] - 0.05
            )
            changes = {"articulation": "+0.1", "breathiness": "-0.05"}

        elif direction == "expressive":
            self.parameters["expressiveness"] = min(
                1.0, self.parameters["expressiveness"] + 0.1
            )
            self.parameters["timbre_brightness"] = min(
                1.0, self.parameters["timbre_brightness"] + 0.05
            )
            changes = {"expressiveness": "+0.1", "timbre_brightness": "+0.05"}

        elif direction == "refine":
            # Make subtle refinements based on usage patterns
            # This is simplified - a real implementation would analyze patterns more
            # deeply
            if self.usage_count > 50:
                # Slightly increase expressiveness for well-used profiles
                self.parameters["expressiveness"] = min(
                    1.0, self.parameters["expressiveness"] + 0.02
                )
                changes = {"expressiveness": "+0.02"}

        # Record evolution
        self.evolution_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "direction": direction,
                "changes": changes,
            }
        )

        self.updated_at = datetime.now().isoformat()
        return changes

    def to_dict(self) -> dict[str, Any]:
        """Convert profile to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "parameters": self.parameters,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "usage_count": self.usage_count,
            "provider_parameters": self.provider_parameters,
            "emotion_adjustments": self.emotion_adjustments,
            "feedback_history": self.feedback_history,
            "evolution_history": self.evolution_history,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "VoiceProfile":
        """Create a profile from dictionary data."""
        profile = VoiceProfile(
            profile_id=data.get("id"),
            name=data.get("name", "Unnamed"),
            parameters=data.get("parameters", {}),
        )

        profile.created_at = data.get("created_at", profile.created_at)
        profile.updated_at = data.get("updated_at", profile.updated_at)
        profile.usage_count = data.get("usage_count", 0)

        if "provider_parameters" in data:
            profile.provider_parameters = data["provider_parameters"]

        if "emotion_adjustments" in data:
            profile.emotion_adjustments = data["emotion_adjustments"]

        if "feedback_history" in data:
            profile.feedback_history = data["feedback_history"]

        if "evolution_history" in data:
            profile.evolution_history = data["evolution_history"]

        return profile


class VoiceProfileManager:
    """
    Manages voice profiles and their evolution over time.

    Features:
    - Profile creation, storage and retrieval
    - Context-aware profile selection
    - Profile evolution based on feedback
    """

    def __init__(self, agi_system=None):
        self.agi = agi_system
        self.logger = logging.getLogger("VoiceProfileManager")
        self.profiles = {}
        self.profiles_dir = os.path.join(os.path.dirname(__file__), "voice_profiles")

        # Create profiles directory if it doesn't exist
        os.makedirs(self.profiles_dir, exist_ok=True)

        # Load existing profiles
        self._load_profiles()

    def _load_profiles(self) -> None:
        """Load profiles from disk."""
        if not os.path.exists(self.profiles_dir):
            self.logger.warning(f"Profiles directory not found: {self.profiles_dir}")
            return

        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.profiles_dir, filename)) as file:
                        data = json.load(file)
                        profile = VoiceProfile.from_dict(data)
                        self.profiles[profile.id] = profile
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    self.logger.error(f"Error loading profile {filename}: {str(e)}")

        self.logger.info(f"Loaded {len(self.profiles)} voice profiles")

    def _save_profile(self, profile: VoiceProfile) -> bool:
        """Save profile to disk."""
        try:
            filename = os.path.join(self.profiles_dir, f"{profile.id}.json")
            with open(filename, "w") as file:
                json.dump(profile.to_dict(), file, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving profile {profile.id}: {str(e)}")
            return False

    def create_profile(self, name: str, parameters: dict[str, Any] = None) -> str:
        """Create a new voice profile."""
        profile_id = str(uuid.uuid4())
        profile = VoiceProfile(profile_id, name, parameters)

        self.profiles[profile_id] = profile
        self._save_profile(profile)

        self.logger.info(f"Created profile: {name} (ID: {profile_id})")
        return profile_id

    def get_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Get a profile by ID."""
        return self.profiles.get(profile_id)

    def list_profiles(self) -> list[dict[str, Any]]:
        """List all available profiles."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "usage_count": p.usage_count,
                "updated_at": p.updated_at,
            }
            for p in self.profiles.values()
        ]

    def select_profile_for_context(self, context: dict[str, Any]) -> str:
        """
        Intelligently select the best profile for a given context.

        Args:
            context: Dictionary with context information including:
                    - type (conversation, notification, etc.)
                    - emotion
                    - text_sample
                    - session_id

        Returns:
            ID of the selected profile
        """
        if not self.profiles:
            return None

        # For simplicity, this is a basic implementation
        # A more sophisticated approach would analyze the text and context

        context_type = context.get("type", "general")
        emotion = context.get("emotion")

        # Select based on context type
        if context_type == "notification":
            # Find a clear, articulate voice for notifications
            candidates = [
                p
                for p in self.profiles.values()
                if p.parameters.get("articulation", 0) > 0.7
            ]
        elif context_type == "conversation":
            # Find a warm, expressive voice for conversations
            candidates = [
                p
                for p in self.profiles.values()
                if p.parameters.get("warmth", 0) > 0.6
                and p.parameters.get("expressiveness", 0) > 0.6
            ]
        else:
            # For general purpose, prefer profiles with more usage
            candidates = sorted(
                self.profiles.values(),
                key=lambda p: p.usage_count,
                reverse=True,
            )[:3]

        # If no candidates match our criteria, use all profiles
        if not candidates:
            candidates = list(self.profiles.values())

        # If we have an emotion specified, prefer profiles with that emotion
        # adjustment defined
        if emotion and emotion.lower() in [
            "happiness",
            "sadness",
            "anger",
            "fear",
            "surprise",
            "neutral",
        ]:
            for profile in candidates:
                if emotion.lower() in profile.emotion_adjustments:
                    return profile.id

        # Otherwise select the first candidate
        return candidates[0].id if candidates else list(self.profiles.keys())[0]

    def record_usage(self, profile_id: str, context: dict[str, Any]) -> bool:
        """
        Record profile usage with context.

        Args:
            profile_id: ID of the used profile
            context: Dictionary with context information

        Returns:
            Success boolean
        """
        profile = self.get_profile(profile_id)
        if not profile:
            return False

        profile.record_usage(context)
        return self._save_profile(profile)

    def provide_feedback(
        self, profile_id: str, feedback: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Provide feedback on a profile and evolve it if appropriate.

        Args:
            profile_id: ID of the profile
            feedback: Dictionary with feedback data including:
                     - score (float)
                     - text (optional feedback text)

        Returns:
            Dictionary with result information
        """
        profile = self.get_profile(profile_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}

        # Add feedback
        profile.add_feedback(feedback)

        # Evolve profile if we have enough feedback
        should_evolve = (
            len(profile.feedback_history) % 5
        ) == 0  # Every 5 feedback entries
        changes = {}

        if should_evolve:
            changes = profile.evolve()

        # Save the updated profile
        self._save_profile(profile)

        return {
            "success": True,
            "evolved": should_evolve,
            "changes": changes if should_evolve else {},
        }

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile."""
        if profile_id not in self.profiles:
            return False

        # Remove from memory
        del self.profiles[profile_id]

        # Remove from disk
        try:
            os.remove(os.path.join(self.profiles_dir, f"{profile_id}.json"))
            return True
        except Exception as e:
            self.logger.error(f"Error deleting profile {profile_id}: {str(e)}")
            return False

    async def integrate_with_voice_system(
        self, profile_id: str, voice_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Integrate profile with voice system data"""
        profile = self.get_profile(profile_id)
        if not profile:
            return {"error": "Profile not found"}

        # Update provider parameters
        for provider, params in voice_data.get("provider_params", {}).items():
            if provider in profile.provider_parameters:
                profile.provider_parameters[provider].update(params)

        # Update emotion adjustments
        new_emotions = voice_data.get("emotion_adjustments", {})
        for emotion, adjustments in new_emotions.items():
            if emotion in profile.emotion_adjustments:
                profile.emotion_adjustments[emotion].update(adjustments)

        self._save_profile(profile)
        return {"success": True, "profile_id": profile_id}

    async def get_voice_system_parameters(self, profile_id: str) -> dict[str, Any]:
        """Get parameters formatted for voice system"""
        profile = self.get_profile(profile_id)
        if not profile:
            return {}

        return {
            "voice_params": profile.parameters,
            "emotion_adjustments": profile.emotion_adjustments,
            "provider_params": profile.provider_parameters,
        }
