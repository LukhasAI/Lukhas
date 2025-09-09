"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: voice_cultural_integration.py
Advanced: voice_cultural_integration.py
Integration Date: 2025-05-31T07:55:28.254343
"""
import builtins
import contextlib
import logging
import random
from typing import Any, Optional

from ..spine.accent_adapter import AccentAdapter
from ..spine.emotion_mapper_alt import LUKHAS

"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ MODULE        : voice_cultural_integration.py                             ║
║ DESCRIPTION   : Integrates the accent adapter module with the voice       ║
║                 memory helix and emotion mapping systems to enable        ║
║                 cultural curiosity, accent adaptation, and location       ║
║                 memory features.                                          ║
║ TYPE          : Integration Module           VERSION: v1.0.0              ║
║ AUTHOR        : LUKHAS SYSTEMS                  CREATED: 2025-05-09        ║
╚═══════════════════════════════════════════════════════════════════════════╝
DEPENDENCIES:
- accent_adapter.py
- voice_memory_helix.py
- emotion_mapper_alt.py
"""


logger = logging.getLogger("voice_cultural_integration")


class VoiceCulturalIntegrator:
    """
    Integrates accent adaptation, emotion mapping, and voice memory systems
    to provide holistic cultural awareness capabilities.
    """

    def __init__(self, core_interface=None, config: Optional[dict[str, Any]] = None):
        """
        Initialize the voice cultural integrator.

        Args:
            core_interface: Interface to core system
            config: Configuration parameters
        """
        self.config = config or {}
        self.core = core_interface

        # Initialize components or get references to them
        self.emotion_mapper = self._get_emotion_mapper()
        self.memory_helix = self._get_memory_helix()
        self.accent_adapter = AccentAdapter(
            emotion_mapper=self.emotion_mapper,
            memory_helix=self.memory_helix,
            config=self.config.get("accent_adapter", {}),
        )

        # Settings
        self.reminiscence_chance = self.config.get("reminiscence_chance", 0.2)
        self.cultural_learning_enabled = self.config.get("cultural_learning_enabled", True)

        logger.info("Voice Cultural Integrator initialized")

    def _get_emotion_mapper(self):
        """Get or create the emotion mapper."""
        if hasattr(self.core, "emotion_mapper"):
            return self.core.emotion_mapper

        # Create simple wrapper if we don't have direct reference

        class EmotionMapperWrapper:
            @property
            def emotions(self):
                return LUKHAS["emotions"]

            @property
            def baby_modes(self):
                return LUKHAS["baby_modes"]

        return EmotionMapperWrapper()

    def _get_memory_helix(self):
        """Get the memory helix from the core."""
        if hasattr(self.core, "memory_helix"):
            return self.core.memory_helix
        elif hasattr(self.core, "get_component"):
            try:
                return self.core.get_component("memory_helix")
            except BaseException:
                logger.warning("Could not get memory helix from core")
                return None
        return None

    async def process_cultural_context(self, user_text: str, user_id: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Process cultural context from user input and update the context.

        Args:
            user_text: Text from the user
            user_id: User identifier
            context: Existing context dictionary

        Returns:
            Updated context with cultural information
        """
        if not user_text:
            return context

        # Get user interaction history if available
        user_history = await self._get_user_history(user_id)

        # Detect cultural context
        cultural_context = self.accent_adapter.detect_cultural_context(user_text, user_history)
        context["cultural_context"] = cultural_context

        # Get appropriate voice mode
        voice_mode = self.accent_adapter.get_voice_mode_for_context(cultural_context)
        if voice_mode:
            context["voice_mode"] = voice_mode

        # Check for location mentions to build memory
        location = await self._extract_location(user_text, context)
        if location:
            context["detected_location"] = location

            # Record in accent adapter
            words_learned = []
            if self.memory_helix and hasattr(self.memory_helix, "detect_new_words"):
                with contextlib.suppress(builtins.BaseException):
                    words_learned = await self.memory_helix.detect_new_words(user_text)

            accent_detected = context.get("accent_info", {}).get("name") if context.get("accent_info") else None

            self.accent_adapter.remember_location(
                user_id=user_id,
                location=location,
                accent_detected=accent_detected,
                words_learned=words_learned,
            )

        return context

    async def _extract_location(self, text: str, context: dict[str, Any]) -> Optional[str]:
        """Extract location mentions from text."""
        # Simple extraction - in production, would use NER
        location_indicators = ["in ", "at ", "from ", "visiting ", "to "]

        # Check if location is already in context
        if context.get("location"):
            return context["location"]

        # Very simple location extraction
        for indicator in location_indicators:
            if indicator in text.lower():
                parts = text.lower().split(indicator)
                if len(parts) > 1:
                    location_phrase = parts[1].split()[0]
                    if len(location_phrase) > 3:  # Avoid tiny words
                        # Remove punctuation
                        import re

                        location = re.sub(r"[^\w\s]", "", location_phrase).strip()
                        if location:
                            return location

        return None

    async def _get_user_history(self, user_id: str) -> list[dict[str, Any]]:
        """Get user interaction history if available."""
        if self.core and hasattr(self.core, "get_user_history"):
            try:
                return await self.core.get_user_history(user_id, limit=10)
            except BaseException:
                logger.warning(f"Failed to get user history for {user_id}")

        return []

    async def generate_cultural_response(self, base_response: str, user_id: str, context: dict[str, Any]) -> str:
        """
        Enhance response with cultural awareness features like reminiscence.

        Args:
            base_response: Original response text
            user_id: User identifier
            context: Context with cultural information

        Returns:
            Enhanced response with cultural features
        """
        if not self.accent_adapter:
            return base_response

        updated_response = base_response

        # Generate reminiscence if appropriate
        should_reminisce = (
            # Random chance
            random.random() < self.reminiscence_chance
            and
            # Only if we have a location context
            ("detected_location" in context or "location" in context)
        )

        if should_reminisce:
            reminiscence = self.accent_adapter.generate_reminiscence(user_id, context)
            if reminiscence:
                # Add reminiscence as new paragraph
                updated_response = f"{updated_response}\n\n{reminiscence}"

        # Check if we should be curious about words
        cultural_context = context.get("cultural_context", "casual")

        # Extract unusual words (longer words are more likely to be interesting)
        words = [w for w in re.findall(r"\b[a-zA-Z\']+\b", context.get("user_text", "")) if len(w) > 5]

        for word in words:
            if self.accent_adapter.should_express_curiosity(word, cultural_context):
                curiosity_question = self.accent_adapter.generate_curiosity_question(word, cultural_context)

                # Add curiosity question
                updated_response = f"{updated_response}\n\n{curiosity_question}"

                # Only ask about one word at a time to be respectful
                self.accent_adapter.log_cultural_interaction(
                    user_id=user_id,
                    word=word,
                    cultural_context=cultural_context,
                )
                break

        return updated_response


# ─────────────────────────────────────────────────────────────────────────────
# 🔍 USAGE GUIDE (for voice_cultural_integration.py)
#
# 1. Initialize the integrator:
#       integrator = VoiceCulturalIntegrator(core_interface=core)
#
# 2. Process cultural context:
#       context = await integrator.process_cultural_context(user_text, user_id, context)
#
# 3. Generate culturally enhanced response:
#       enhanced_response = await integrator.generate_cultural_response(
#           base_response, user_id, context)
#
# END OF FILE
# ─────────────────────────────────────────────────────────────────────────────