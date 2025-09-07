import logging
from datetime import timezone
import streamlit as st
logger = logging.getLogger(__name__)
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ MODULE        : voice_personality.py                                      ║
║ DESCRIPTION   : Integrates personality components with voice synthesis    ║
║                 for emotionally resonant, creative, and adaptive voice    ║
║                 responses that reflect Lukhas' unique personality.         ║
║ TYPE          : Personality Integration        VERSION: v1.0.0            ║
║ AUTHOR        : LUKHAS SYSTEMS                  CREATED: 2025-05-08        ║
╚═══════════════════════════════════════════════════════════════════════════╝
DEPENDENCIES:
- LUKHAS_AGI_2.CORE.personality.creative_expressions
- LUKHAS_AGI_2.CORE.personality.personality_refiner
- LUKHAS_AGI_2.CORE.orchestration.emotional_oscillator
"""

import random
from datetime import datetime
from typing import Any, Optional

from core.common import get_logger

# Configure logging
logger = get_logger(__name__)

# Import personality components
try:
    from core.personality.creative_expressions import NeuroHaikuGenerator

    HAIKU_AVAILABLE = True
except ImportError:
    HAIKU_AVAILABLE = False
    logger.warning("NeuroHaikuGenerator not available. Some creative features will be disabled.")

try:
    from lukhas.orchestration.brain.personality.personality_refiner import (
        PersonalityRefiner,
    )

    PERSONALITY_REFINER_AVAILABLE = True
except ImportError:
    PERSONALITY_REFINER_AVAILABLE = False
    logger.warning("PersonalityRefiner not available. Adaptive personality features will be disabled.")

try:
    from lukhas.orchestration.brain.orchestration.emotional_oscillator import (
        EmotionalOscillator,
    )

    EMOTIONAL_OSC_AVAILABLE = True
except ImportError:
    EMOTIONAL_OSC_AVAILABLE = False
    logger.warning("EmotionalOscillator not available. Dynamic emotion modulation will be disabled.")


class VoicePersonalityCreativityEngine:
    """
    Integrates personality components with voice synthesis to create a more
    emotionally resonant, creative, and human-like voice experience.

    This class serves as a bridge between Lukhas' personality components and
    the voice synthesis system, allowing for:

    1. Dynamic emotional inflection based on context
    2. Creative expressions (haiku, metaphors, etc) interwoven with voice
    3. Personalized adaptation to user interaction patterns
    4. Dream-inspired voice modulations during reflective states
    """

    def __init__(self, core_interface=None, config: Optional[dict[str, Any]] = None):
        """
        Initialize the voice personality integration

        Args:
            core_interface: Interface to the LUKHAS core system
            config: Configuration dictionary
        """
        self.core = core_interface
        self.config = config or {}

        # Initialize personality components
        self.haiku_generator = None
        self.personality_refiner = None
        self.emotional_oscillator = None

        # Initialize available components
        self._init_components()

        # Track personality state
        self.current_mood = "neutral"
        self.personality_traits = {
            "creativity": 0.7,
            "formality": 0.5,
            "expressiveness": 0.6,
            "curiosity": 0.8,
            "humor": 0.6,
            "reflectiveness": 0.7,
        }

        # Adaptation parameters
        self.adaptation_rate = 0.05  # How quickly personality adapts
        self.personality_memory = []  # Track recent adaptations

        logger.info("Voice personality integration initialized")

    def _init_components(self):
        """Initialize available personality components"""
        # Initialize haiku generator if available
        if HAIKU_AVAILABLE and self.config.get("enable_creative_expressions", True):
            try:
                symbolic_db = None
                federated_model = None

                # Try to get these from core if available
                if self.core:
                    try:
                        symbolic_db = self.core.get_component("symbolic_db")
                        federated_model = self.core.get_component("federated_model")
                    except Exception as e:
                        logger.warning(f"Failed to get components from core: {e}")

                self.haiku_generator = NeuroHaikuGenerator(symbolic_db, federated_model)
                logger.info("NeuroHaikuGenerator initialized")
            except Exception as e:
                logger.error(f"Failed to initialize NeuroHaikuGenerator: {e}")

        # Initialize personality refiner if available
        if PERSONALITY_REFINER_AVAILABLE:
            try:
                self.personality_refiner = PersonalityRefiner()
                logger.info("PersonalityRefiner initialized")
            except Exception as e:
                logger.error(f"Failed to initialize PersonalityRefiner: {e}")

        # Initialize emotional oscillator if available
        if EMOTIONAL_OSC_AVAILABLE:
            try:
                self.emotional_oscillator = EmotionalOscillator()
                logger.info("EmotionalOscillator initialized")
            except Exception as e:
                logger.error(f"Failed to initialize EmotionalOscillator: {e}")

    async def enhance_voice_text(self, text: str, emotion: str, context: dict[str, Any]) -> str:
        """
        Enhance voice text with personality traits

        Args:
            text: Original text to enhance
            emotion: Current emotional state
            context: Additional context information

        Returns:
            Enhanced text
        """
        # Original text as fallback
        enhanced_text = text

        # Track if we should apply creative enhancements based on context
        should_enhance = self._should_enhance_text(text, emotion, context)

        if not should_enhance:
            return text

        # Apply creative enhancements if appropriate
        if self.haiku_generator and context.get("enable_creative", True):
            # Only apply creative enhancements in specific contexts
            if emotion in ["reflective", "calm"] and len(text.split()) > 10:
                # For reflective or calm states, potentially add haiku
                if random.random() < self.personality_traits["creativity"] * 0.3:
                    try:
                        haiku = self.haiku_generator.generate_haiku()
                        enhanced_text = f"{text}\n\n{haiku}"
                        logger.info("Added haiku to voice text")
                    except Exception as e:
                        logger.warning(f"Failed to generate haiku: {e}")

        # Apply personality-based text modifications
        enhanced_text = self._apply_personality_traits(enhanced_text, emotion)

        # Apply emotional oscillation if available
        if self.emotional_oscillator:
            try:
                oscillation = self.emotional_oscillator.get_current_state()
                intensity = oscillation.get("amplitude", 0.5)

                # Adjust text based on oscillation
                if intensity > 0.7 and emotion in ["excited", "urgent"]:
                    enhanced_text = self._add_emphasis(enhanced_text)
                elif intensity < 0.3 and emotion in ["calm", "reflective"]:
                    enhanced_text = self._add_pauses(enhanced_text)
            except Exception as e:
                logger.warning(f"Failed to apply emotional oscillation: {e}")

        # Update personality based on interaction
        self._update_personality_traits(context)

        return enhanced_text

    def get_voice_modulation(self, emotion: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Get voice modulation parameters based on personality and emotion

        Args:
            emotion: Current emotional state
            context: Additional context information

        Returns:
            Voice modulation parameters
        """
        # Base modulation parameters
        modulation = {
            "pitch_adjustment": 0.0,
            "rate_adjustment": 0.0,
            "volume_adjustment": 0.0,
            "expressiveness": 0.5,
            "emphasis_words": [],
        }

        # Apply personality-based modulation
        expressiveness = self.personality_traits["expressiveness"]
        modulation["expressiveness"] = expressiveness

        # Adjust based on emotional state
        if emotion == "excited":
            modulation["pitch_adjustment"] += 0.2 * expressiveness
            modulation["rate_adjustment"] += 0.15 * expressiveness
            modulation["volume_adjustment"] += 0.1 * expressiveness
        elif emotion == "reflective":
            modulation["pitch_adjustment"] -= 0.1 * expressiveness
            modulation["rate_adjustment"] -= 0.2 * expressiveness
            modulation["volume_adjustment"] -= 0.05 * expressiveness

        # Apply dream-like quality for reflective states
        if emotion == "dream" or context.get("in_dream_state", False):
            modulation["pitch_adjustment"] -= 0.3
            modulation["rate_adjustment"] -= 0.25
            modulation["reverb"] = 0.4
            modulation["echo"] = 0.2

        # Apply emotional oscillation if available
        if self.emotional_oscillator:
            try:
                oscillation = self.emotional_oscillator.get_current_state()
                modulation["pitch_adjustment"] += oscillation.get("phase", 0) * 0.1
                modulation["rate_adjustment"] += oscillation.get("frequency", 0) * 0.05
            except Exception as e:
                logger.warning(f"Failed to apply emotional oscillation: {e}")

        return modulation

    def adapt_to_interaction(self, interaction_data: dict[str, Any]):
        """
        Adapt personality traits based on interaction data

        Args:
            interaction_data: Data about the interaction
        """
        if not interaction_data:
            return

        # Update personality traits based on interaction
        if self.personality_refiner:
            try:
                refined_traits = self.personality_refiner.refine_traits(interaction_data)
                if refined_traits:
                    # Gradually adapt traits
                    for trait, value in refined_traits.items():
                        if trait in self.personality_traits:
                            current = self.personality_traits[trait]
                            self.personality_traits[trait] = (
                                current * (1 - self.adaptation_rate) + value * self.adaptation_rate
                            )

                    logger.debug(f"Adapted personality traits: {self.personality_traits}")
            except Exception as e:
                logger.warning(f"Failed to refine personality traits: {e}")

        # Record this adaptation
        self.personality_memory.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "traits": self.personality_traits.copy(),
                "interaction_type": interaction_data.get("type", "unknown"),
            }
        )

        # Keep memory bounded
        if len(self.personality_memory) > 100:
            self.personality_memory = self.personality_memory[-100:]

    def _should_enhance_text(self, text: str, emotion: str, context: dict[str, Any]) -> bool:
        """Determine if text should be enhanced with personality"""
        # Don't enhance short responses
        if len(text) < 20:
            return False

        # Don't enhance urgent or emergency messages
        if emotion == "urgent" or context.get("emergency", False):
            return False

        # Don't enhance pure functional responses
        functional_indicators = [
            "here's the result",
            "error occurred",
            "command executed",
        ]
        if any(indicator in text.lower() for indicator in functional_indicators):
            return False

        # Check user preferences if available
        return context.get("user_preferences", {}).get("enhanced_personality", True) is not False

    def _apply_personality_traits(self, text: str, emotion: str) -> str:
        """Apply personality traits to text"""
        # Apply creativity
        if self.personality_traits["creativity"] > 0.8:
            # Add metaphors or vivid descriptions
            pass

        # Apply formality adjustments
        if self.personality_traits["formality"] < 0.3 and len(text) > 50:
            # Make less formal
            text = text.replace("I would like to", "I'd like to")
            text = text.replace("I would", "I'd")
            text = text.replace("I will", "I'll")

        elif self.personality_traits["formality"] > 0.8:
            # Make more formal
            text = text.replace("I'd like to", "I would like to")
            text = text.replace("I'll", "I will")

        # Apply humor if appropriate
        if self.personality_traits["humor"] > 0.7 and emotion not in ["urgent", "sad"]:
            # Potentially add subtle humor
            pass

        return text

    def _add_emphasis(self, text: str) -> str:
        """Add emphasis to text for excited/urgent emotions"""
        words = text.split()
        if len(words) < 5:
            return text

        # Add emphasis to key words
        for i in range(len(words)):
            if len(words[i]) > 4 and random.random() < 0.2:
                words[i] = f"<emphasis>{words[i]}</emphasis>"

        return " ".join(words)

    def _add_pauses(self, text: str) -> str:
        """Add thoughtful pauses for calm/reflective emotions"""
        sentences = text.split(". ")
        if len(sentences) < 2:
            return text

        # Add pauses between some sentences
        for i in range(len(sentences) - 1):
            if random.random() < 0.3:
                sentences[i] = f"{sentences[i]}. <break time='0.7s'>"
            else:
                sentences[i] = f"{sentences[i]}."

        return " ".join(sentences)

    def _update_personality_traits(self, context: dict[str, Any]):
        """Update personality traits based on context"""
        # Apply small random variations to keep personality dynamic
        for trait in self.personality_traits:
            variation = (random.random() - 0.5) * 0.05  # Small random adjustment
            self.personality_traits[trait] = max(0.1, min(0.9, self.personality_traits[trait] + variation))