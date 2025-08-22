"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

📄 MODULE      : dream_delivery_manager.py
📤 PURPOSE     : Delivers symbolic dream outputs through voice, screen, or feedback channels
🧠 CONTEXT     : Interprets tone, modulates delivery, routes through ethical filters
🎙️ OUTPUTS     : Voice (whisper, speaker), Email, UI, Apple Watch (future)
🛡️ ETHICS      : Uses lukhas_ethics_guard and voice_safety_guard
🛠️ VERSION     : v1.1.0 • 📅 CREATED: 2025-05-05 • ✍️ AUTHOR: LUKHAS AGI TEAM
"""

import logging
from datetime import datetime
from typing import Any, Optional

from lukhas.core.interfaces.voice.voice_emotional.context_aware_modular_voice import (
    VoiceModulator,
)

# Voice components
from .voice_parameter import VoiceParameter

try:
    from tools.documentation.memory_evolution.voice_synthesis import (
        VoiceSynthesisAdapter,
    )
except ImportError:
    # Create a placeholder if the module doesn't exist

    class VoiceSynthesisAdapter:

        def __init__(self, *args, **kwargs):
            pass

        def synthesize(self, *args, **kwargs):
            return "synthesized_audio"


try:
    from voice.safety.voice_safety_guard import VoiceSafetyFilter
except ImportError:
    # Create a placeholder if the module doesn't exist

    class VoiceSafetyFilter:

        def __init__(self, *args, **kwargs):
            pass

        def filter_content(self, *args, **kwargs):
            return True


# Ethics & safety
from ethics.ethics_guard import LegalComplianceAssistant

# Memory & emotion components
from lukhas.memory.adapters.creativity_adapter import EmotionalModulator

# from ..emotional_resonance import EmotionalOscillator

# Symbolic world and node system
try:
    from ..bio_symbolic.symbolic_world import SymbolicWorld

    SYMBOLIC_WORLD_AVAILABLE = True
except ImportError:
    SYMBOLIC_WORLD_AVAILABLE = False

# Configure logging
logger = logging.getLogger("DreamDeliveryManager")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class DreamDeliveryManager:
    """
    Manages the delivery of dream content through various outputs,
    with emotional modulation and ethical safeguards.

    Features:
    - Multi-channel output (voice, screen, notifications)
    - Emotional resonance integration
    - Symbolic world integration for content awareness
    - Memory-influenced voice modulation
    - Ethics and safety filters
    """

    def __init__(self, config=None):
        """
        Initialize the Dream Delivery Manager

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Initialize components
        self.ethics = LegalComplianceAssistant()
        self.safety_filter = VoiceSafetyFilter()

        # Emotion system initialization
        self.emotional_oscillator = EmotionalOscillator()

        # Initialize symbolic world if available
        self.symbolic_world = None
        if SYMBOLIC_WORLD_AVAILABLE and self.config.get("use_symbolic_world", True):
            try:
                self.symbolic_world = SymbolicWorld()
                logger.info("Symbolic world integration enabled")
            except Exception as e:
                logger.error(f"Failed to initialize symbolic world: {e}")

        # Initialize emotional modulator if we have memory manager
        self.emotional_modulator = None
        memory_manager = self.config.get("memory_manager")
        if memory_manager and self.emotional_oscillator:
            self.emotional_modulator = EmotionalModulator(
                self.emotional_oscillator, memory_manager, self.symbolic_world
            )
            logger.info("Emotional modulator initialized with memory integration")

        # Output channel settings
        self.output_channels = self.config.get("output_channels", ["voice", "screen"])

        # Voice synthesis settings
        self.voice_settings = self.config.get(
            "voice_settings",
            {
                "provider": "elevenlabs",
                "default_voice_id": "default",
                "memory_influenced": True,
                "symbolic_integration": SYMBOLIC_WORLD_AVAILABLE,
            },
        )

        # Record of delivered dream content
        self.delivery_history = []

    def deliver_dream(
        self,
        dream_content: dict[str, Any],
        channels: Optional[list[str]] = None,
        voice_style: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Deliver dream content through specified channels

        Args:
            dream_content: The dream content to deliver
            channels: Output channels to use (defaults to configured channels)
            voice_style: Optional voice style to use

        Returns:
            Dict with delivery status
        """
        if not channels:
            channels = self.output_channels

        # Extract information from dream content
        dream_id = dream_content.get(
            "dream_id", f"dream_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        dream_text = dream_content.get("content", "")
        dream_emotions = dream_content.get("emotional_context", {})
        intent = dream_content.get("intent", "share_dream")

        # Extract or determine personality vector
        if "personality_vector" in dream_content:
            personality_vector = dream_content["personality_vector"]
        else:
            # Default personality parameters if not provided
            personality_vector = {
                "openness": 0.8,
                "conscientiousness": 0.7,
                "extraversion": 0.6,
                "agreeableness": 0.75,
                "emotional_stability": 0.65,
                "symbolism_preference": 0.8,
            }

        # Create delivery context
        delivery_context = {
            "dream_id": dream_id,
            "timestamp": datetime.now().isoformat(),
            "channels": channels,
            "dream_emotions": dream_emotions,
            "dream_length": len(dream_text) if dream_text else 0,
            "intent": intent,
        }

        # Register the delivery in symbolic world if available
        if self.symbolic_world:
            self._register_in_symbolic_world(dream_content, delivery_context)

        # Deliver through each requested channel
        delivery_results = {}

        for channel in channels:
            if channel == "voice":
                delivery_results["voice"] = self._deliver_voice(
                    dream_text,
                    intent,
                    personality_vector,
                    dream_emotions,
                    voice_style,
                )
            elif channel == "screen":
                delivery_results["screen"] = self._deliver_screen(dream_content)
            elif channel == "email":
                delivery_results["email"] = self._deliver_email(dream_content)
            elif channel == "notification":
                delivery_results["notification"] = self._deliver_notification(
                    dream_content
                )

        # Update delivery history
        self.delivery_history.append(
            {
                "dream_id": dream_id,
                "timestamp": datetime.now().isoformat(),
                "channels": channels,
                "results": delivery_results,
            }
        )

        # Trim history if needed
        if len(self.delivery_history) > 100:
            self.delivery_history = self.delivery_history[-100:]

        return {
            "status": "delivered",
            "dream_id": dream_id,
            "channels_used": channels,
            "delivery_results": delivery_results,
        }

    def _deliver_voice(
        self,
        message: str,
        intent: str,
        personality_vector: dict[str, float],
        emotions: dict[str, Any] = None,
        voice_style: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Deliver content through voice with emotional modulation

        Args:
            message: The text to speak
            intent: Intent of the message
            personality_vector: Personality parameters
            emotions: Emotional context
            voice_style: Optional specific voice style

        Returns:
            Dict with voice delivery status
        """
        # Apply safety check
        region = self.config.get("region", "EU")
        if not self.safety_filter.is_safe(message, region=region):
            logger.warning(
                "[⚠️] Message flagged by safety guard. Voice delivery blocked."
            )
            return {
                "status": "blocked",
                "reason": "safety_filter",
                "message": "Voice output suppressed due to safety filter.",
            }

        # Determine emotional state from dream content or current system state
        if emotions:
            # Use emotions from dream content
            emotion_name = emotions.get("primary_emotion", "neutral")
            emotion_intensity = emotions.get("intensity", 0.5)
            emotion = {
                "name": emotion_name,
                "intensity": emotion_intensity,
                "valence": emotions.get("valence", 0.0),
                "arousal": emotions.get("arousal", 0.5),
            }
        else:
            # Use system's current emotional state
            emotion_result = analyze_emotional_state(message)
            emotion = {
                "name": emotion_result.get("emotion", "neutral"),
                "intensity": emotion_result.get("intensity", 0.5),
                "valence": emotion_result.get("valence", 0.0),
                "arousal": emotion_result.get("arousal", 0.5),
            }

        # Get voice parameters through emotional modulator if available
        voice_params = None
        if self.emotional_modulator:
            modulation_result = self.emotional_modulator.modulate_speech(
                message,
                context={
                    "intent": intent,
                    "personality_vector": personality_vector,
                },
            )

            # Convert modulation result to voice parameters
            voice_params = VoiceParameter(
                pitch=modulation_result.get("pitch_adjustment", 1.0),
                speed=modulation_result.get("speed_adjustment", 1.0),
                volume=1.0,
                timbre=modulation_result.get("timbre", 0.5),
                breathiness=modulation_result.get("breathiness", 0.2),
                articulation=modulation_result.get("articulation", 0.5),
                resonance=modulation_result.get("resonance", 0.5),
                inflection=modulation_result.get("inflection", 0.5),
            )

            # Use emotional modulator's determined style
            determined_voice_style = modulation_result.get("emotion", "neutral")

            # Use provided style if specified, otherwise use determined style
            selected_style = voice_style or determined_voice_style

        else:
            # Fallback to simple voice style selection
            voice_modulator = VoiceModulator({})
            context = {
                "intent": intent,
                "emotion": emotion,
                "personality_vector": personality_vector,
            }
            params = voice_modulator.determine_parameters(context)
            selected_style = voice_style or params.get("voice_id", "default")

            # Get basic voice parameters based on emotion
            voice_params = self._get_basic_voice_parameters(
                emotion["name"], emotion["intensity"]
            )

        # Apply symbolic relationship patterns if available
        if self.symbolic_world and emotion["name"] != "neutral":
            try:
                voice_params = self._enhance_voice_with_symbolic_patterns(
                    voice_params, emotion["name"], message
                )
                logger.debug(
                    f"Applied symbolic patterns to voice parameters for {emotion['name']}"
                )
            except Exception as e:
                logger.warning(f"Failed to apply symbolic patterns: {e}")

        # Log selected voice style
        logger.info(f"[🎙️ VOICE STYLE: {selected_style}]")

        # Call voice synthesis with parameters
        try:
            speak_text(
                message,
                style=selected_style,
                parameters=voice_params,
                voice_id=self.voice_settings.get("default_voice_id"),
                provider=self.voice_settings.get("provider"),
            )

            return {
                "status": "success",
                "emotion": emotion["name"],
                "style": selected_style,
                "parameters": voice_params.__dict__ if voice_params else {},
            }

        except Exception as e:
            logger.error(f"Error in voice synthesis: {e}")
            return {"status": "error", "error": str(e)}

    def _get_basic_voice_parameters(
        self, emotion: str, intensity: float
    ) -> VoiceParameter:
        """
        Get basic voice parameters based on emotion

        Args:
            emotion: Emotion name
            intensity: Emotion intensity (0-1)

        Returns:
            VoiceParameter object with appropriate settings
        """
        # Define base parameters for each emotion
        params_map = {
            "neutral": {
                "pitch": 1.0,
                "speed": 1.0,
                "volume": 1.0,
                "timbre": 0.5,
                "breathiness": 0.2,
                "articulation": 0.5,
                "resonance": 0.5,
                "inflection": 0.5,
            },
            "joy": {
                "pitch": 1.15,
                "speed": 1.1,
                "volume": 1.1,
                "timbre": 0.4,
                "breathiness": 0.15,
                "articulation": 0.7,
                "resonance": 0.7,
                "inflection": 0.8,
            },
            "happiness": {
                "pitch": 1.1,
                "speed": 1.05,
                "volume": 1.05,
                "timbre": 0.35,
                "breathiness": 0.2,
                "articulation": 0.65,
                "resonance": 0.65,
                "inflection": 0.7,
            },
            "sadness": {
                "pitch": 0.9,
                "speed": 0.85,
                "volume": 0.9,
                "timbre": 0.4,
                "breathiness": 0.5,
                "articulation": 0.45,
                "resonance": 0.55,
                "inflection": 0.4,
            },
            "fear": {
                "pitch": 1.1,
                "speed": 1.15,
                "volume": 0.95,
                "timbre": 0.6,
                "breathiness": 0.35,
                "articulation": 0.7,
                "resonance": 0.4,
                "inflection": 0.7,
            },
            "anger": {
                "pitch": 1.05,
                "speed": 1.1,
                "volume": 1.2,
                "timbre": 0.8,
                "breathiness": 0.1,
                "articulation": 0.8,
                "resonance": 0.65,
                "inflection": 0.7,
            },
            "thoughtful": {
                "pitch": 0.92,
                "speed": 0.85,
                "volume": 0.9,
                "timbre": 0.4,
                "breathiness": 0.45,
                "articulation": 0.75,
                "resonance": 0.7,
                "inflection": 0.55,
            },
            "curious": {
                "pitch": 1.05,
                "speed": 0.95,
                "volume": 0.95,
                "timbre": 0.45,
                "breathiness": 0.3,
                "articulation": 0.7,
                "resonance": 0.6,
                "inflection": 0.7,
            },
        }

        # Get parameters for the emotion, or default to neutral
        base_params = params_map.get(emotion.lower(), params_map["neutral"])

        # Adjust parameters based on intensity
        intensity_factor = 0.5 + (intensity * 0.5)  # Scale intensity influence

        # Calculate adjusted parameters
        adjusted_params = {}
        for param, value in base_params.items():
            neutral_value = params_map["neutral"][param]
            # Calculate adjustment - more intensity means further from neutral
            adjustment = (value - neutral_value) * intensity_factor
            adjusted_params[param] = neutral_value + adjustment

        # Create VoiceParameter object
        return VoiceParameter(
            pitch=adjusted_params["pitch"],
            speed=adjusted_params["speed"],
            volume=adjusted_params["volume"],
            timbre=adjusted_params["timbre"],
            breathiness=adjusted_params["breathiness"],
            articulation=adjusted_params["articulation"],
            resonance=adjusted_params["resonance"],
            inflection=adjusted_params["inflection"],
        )

    def _enhance_voice_with_symbolic_patterns(
        self, voice_params: VoiceParameter, emotion: str, text: str
    ) -> VoiceParameter:
        """
        Enhance voice parameters with patterns from symbolic world

        Args:
            voice_params: Base voice parameters
            emotion: Current emotion
            text: Text to analyze for content

        Returns:
            Enhanced voice parameters
        """
        if not self.symbolic_world:
            return voice_params

        try:
            # Check if we have a voice pattern for this emotion
            pattern_symbol_name = f"voice_pattern_{emotion.lower()}"
            if self.symbolic_world.symbol_exists(pattern_symbol_name):
                pattern_symbol = self.symbolic_world.get_symbol(pattern_symbol_name)

                # Get baseline parameters from pattern
                pitch_baseline = pattern_symbol.get_property("pitch_baseline")
                if pitch_baseline is not None:
                    voice_params.pitch = (
                        voice_params.pitch + pitch_baseline
                    ) / 2  # Average with existing

                speed_baseline = pattern_symbol.get_property("speed_baseline")
                if speed_baseline is not None:
                    voice_params.speed = (voice_params.speed + speed_baseline) / 2

                timbre_baseline = pattern_symbol.get_property("timbre_baseline")
                if timbre_baseline is not None:
                    voice_params.timbre = (voice_params.timbre + timbre_baseline) / 2

                breathiness_baseline = pattern_symbol.get_property(
                    "breathiness_baseline"
                )
                if breathiness_baseline is not None:
                    voice_params.breathiness = (
                        voice_params.breathiness + breathiness_baseline
                    ) / 2

                resonance_baseline = pattern_symbol.get_property("resonance_baseline")
                if resonance_baseline is not None:
                    voice_params.resonance = (
                        voice_params.resonance + resonance_baseline
                    ) / 2

                articulation_baseline = pattern_symbol.get_property(
                    "articulation_baseline"
                )
                if articulation_baseline is not None:
                    voice_params.articulation = (
                        voice_params.articulation + articulation_baseline
                    ) / 2

                inflection_baseline = pattern_symbol.get_property("inflection_baseline")
                if inflection_baseline is not None:
                    voice_params.inflection = (
                        voice_params.inflection + inflection_baseline
                    ) / 2

            # Find related emotions that might influence this emotion
            # This creates more nuanced emotional blending
            related_emotions = self._find_related_emotions(emotion)
            if related_emotions:
                # Blend with related emotions
                blend_factor = 0.3  # 30% influence from related emotions
                for rel_emotion, rel_strength in related_emotions:
                    rel_pattern_name = f"voice_pattern_{rel_emotion.lower()}"
                    if self.symbolic_world.symbol_exists(rel_pattern_name):
                        rel_pattern = self.symbolic_world.get_symbol(rel_pattern_name)

                        # Blend pitch
                        rel_pitch = rel_pattern.get_property("pitch_baseline")
                        if rel_pitch is not None:
                            influence = blend_factor * rel_strength
                            voice_params.pitch = (
                                voice_params.pitch * (1 - influence)
                                + rel_pitch * influence
                            )

                        # Blend other parameters similarly
                        # (Code condensed for brevity - would apply to all voice parameters)

            # Content-specific adjustments based on text
            if len(text) > 20:  # Only analyze substantial text
                # Simple keyword analysis for demonstration
                content_adjustment = self._analyze_text_for_voice_adjustments(text)

                # Apply content adjustment with a small weight
                content_weight = 0.2
                voice_params.inflection += (
                    content_adjustment.get("inflection_adjustment", 0) * content_weight
                )
                voice_params.speed += (
                    content_adjustment.get("speed_adjustment", 0) * content_weight
                )

                # Ensure parameters stay in valid ranges
                voice_params.pitch = max(0.5, min(1.5, voice_params.pitch))
                voice_params.speed = max(0.5, min(1.5, voice_params.speed))
                voice_params.timbre = max(0.0, min(1.0, voice_params.timbre))
                voice_params.breathiness = max(0.0, min(1.0, voice_params.breathiness))
                voice_params.articulation = max(
                    0.0, min(1.0, voice_params.articulation)
                )
                voice_params.resonance = max(0.0, min(1.0, voice_params.resonance))
                voice_params.inflection = max(0.0, min(1.0, voice_params.inflection))

        except Exception as e:
            logger.warning(f"Error enhancing voice with symbolic patterns: {e}")

        return voice_params

    def _find_related_emotions(self, emotion: str) -> list[tuple[str, float]]:
        """
        Find emotions related to the given emotion from symbolic world

        Args:
            emotion: Emotion to find relations for

        Returns:
            List of (related_emotion, strength) tuples
        """
        related = []

        if not self.symbolic_world:
            return related

        try:
            emotion_name = emotion.lower()
            symbol_name = f"emotion_{emotion_name}"

            if not self.symbolic_world.symbol_exists(symbol_name):
                return related

            # Get the emotion symbol
            emotion_symbol = self.symbolic_world.get_symbol(symbol_name)

            # Find related emotion symbols
            related_links = self.symbolic_world.get_links(
                emotion_symbol,
                relationship_types=[
                    "blends_with",
                    "transitions_to",
                    "resonates_with",
                ],
            )

            # Extract related emotions with strength
            for link in related_links:
                if link.relationship_type in [
                    "blends_with",
                    "transitions_to",
                    "resonates_with",
                ]:
                    target = link.target

                    # Check if target is an emotion symbol
                    if target.name.startswith("emotion_"):
                        rel_emotion = target.name[8:]  # Remove "emotion_" prefix
                        strength = link.properties.get("strength", 0.5)

                        related.append((rel_emotion, strength))

        except Exception as e:
            logger.warning(f"Error finding related emotions: {e}")

        return related

    def _analyze_text_for_voice_adjustments(self, text: str) -> dict[str, float]:
        """
        Analyze text content for voice parameter adjustments

        Args:
            text: Text to analyze

        Returns:
            Dict of parameter adjustments
        """
        # Simple keyword-based analysis
        adjustments = {
            "inflection_adjustment": 0.0,
            "speed_adjustment": 0.0,
            "timbre_adjustment": 0.0,
        }

        # Check for question marks - questions get more inflection
        question_count = text.count("?")
        if question_count > 0:
            adjustments["inflection_adjustment"] = min(question_count * 0.05, 0.2)

        # Check for exclamation points - exclamations get more volume and speed
        exclamation_count = text.count("!")
        if exclamation_count > 0:
            adjustments["speed_adjustment"] = min(exclamation_count * 0.05, 0.15)

        # Poetic or philosophical content - slower, more resonant
        philosophical_words = [
            "meaning",
            "purpose",
            "soul",
            "consciousness",
            "existential",
            "philosophy",
            "universe",
            "essence",
        ]
        if any(word in text.lower() for word in philosophical_words):
            adjustments["speed_adjustment"] -= 0.1

        # Technical content - more precise articulation
        technical_words = [
            "system",
            "algorithm",
            "analysis",
            "function",
            "technical",
            "process",
            "mechanism",
            "component",
        ]
        if any(word in text.lower() for word in technical_words):
            adjustments["timbre_adjustment"] += 0.05

        return adjustments

    def _deliver_screen(self, dream_content: dict[str, Any]) -> dict[str, Any]:
        """
        Deliver dream content to screen interface

        Args:
            dream_content: Dream content to display

        Returns:
            Dict with screen delivery status
        """
        # In a real implementation, this would integrate with UI components
        # For demonstration, we'll just return a success status
        logger.info("[📱 SCREEN] Delivered dream content to screen interface")

        return {
            "status": "success",
            "display_mode": dream_content.get("display_mode", "standard"),
        }

    def _deliver_email(self, dream_content: dict[str, Any]) -> dict[str, Any]:
        """
        Deliver dream content via email

        Args:
            dream_content: Dream content to send

        Returns:
            Dict with email delivery status
        """
        # In a real implementation, this would send an email
        # For demonstration, we'll just return a pending status
        logger.info("[📧 EMAIL] Dream content prepared for email delivery")

        return {"status": "pending", "scheduled": datetime.now().isoformat()}

    def _deliver_notification(self, dream_content: dict[str, Any]) -> dict[str, Any]:
        """
        Deliver dream content via notification

        Args:
            dream_content: Dream content for notification

        Returns:
            Dict with notification delivery status
        """
        # In a real implementation, this would send a notification
        # For demonstration, we'll just return a success status
        logger.info("[🔔 NOTIFICATION] Dream notification sent")

        return {"status": "success", "notification_type": "dream_insight"}

    def _register_in_symbolic_world(
        self, dream_content: dict[str, Any], delivery_context: dict[str, Any]
    ) -> None:
        """
        Register dream delivery in symbolic world for integrated awareness

        Args:
            dream_content: Dream content being delivered
            delivery_context: Context about the delivery
        """
        if not self.symbolic_world:
            return

        try:
            # Create symbol for this delivery event
            timestamp = datetime.now()
            delivery_id = f"dream_delivery_{timestamp.strftime('%Y%m%d_%H%M%S')}"

            # Extract dream attributes for symbolic representation
            dream_id = dream_content.get("dream_id", "unknown")
            emotional_context = dream_content.get("emotional_context", {})
            primary_emotion = emotional_context.get("primary_emotion", "neutral")

            # Create symbol for the delivery event
            delivery_properties = {
                "type": "dream_delivery",
                "timestamp": timestamp.isoformat(),
                "dream_id": dream_id,
                "channels": delivery_context.get("channels", []),
                "primary_emotion": primary_emotion,
                "emotional_intensity": emotional_context.get("intensity", 0.5),
            }

            delivery_symbol = self.symbolic_world.create_symbol(
                delivery_id, delivery_properties
            )

            # Link to dream symbol if it exists
            if self.symbolic_world.symbol_exists(dream_id):
                dream_symbol = self.symbolic_world.get_symbol(dream_id)
                self.symbolic_world.link_symbols(
                    delivery_symbol,
                    dream_symbol,
                    "delivers_content_of",
                    {"timestamp": timestamp.isoformat()},
                )

            # Link to emotion symbol if it exists
            emotion_symbol_name = f"emotion_{primary_emotion}"
            if self.symbolic_world.symbol_exists(emotion_symbol_name):
                emotion_symbol = self.symbolic_world.get_symbol(emotion_symbol_name)
                self.symbolic_world.link_symbols(
                    delivery_symbol,
                    emotion_symbol,
                    "expressed_with_emotion",
                    {"intensity": emotional_context.get("intensity", 0.5)},
                )

        except Exception as e:
            logger.warning(f"Error registering in symbolic world: {e}")


def modulate_voice_output(message, intent, personality_vector):
    """
    Legacy function for backward compatibility.
    Delegates to the DreamDeliveryManager.
    """
    # Create a manager instance
    manager = DreamDeliveryManager()

    # Get emotional state
    emotion = analyze_emotional_state(message)

    # Deliver through voice
    result = manager._deliver_voice(message, intent, personality_vector, emotion)

    if result["status"] == "success":
        return message
    else:
        return result.get("message", "Voice output failed.")
    result = manager._deliver_voice(message, intent, personality_vector, emotion)

    if result["status"] == "success":
        return message
    else:
        return result.get("message", "Voice output failed.")
