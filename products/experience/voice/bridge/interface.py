"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ MODULE        : voice_node.py                                             ║
║ DESCRIPTION   : Unified voice architecture for LUKHAS AGI that integrates  ║
║                 speech synthesis, voice profiling, emotional adaptation,  ║
║                 and voice safety in one cohesive node.                    ║
║ TYPE          : AGI Node Component             VERSION: v1.0.0            ║
║ AUTHOR        : LUKHAS SYSTEMS                  CREATED: 2025-05-08        ║
╚═══════════════════════════════════════════════════════════════════════════╝
DEPENDENCIES:
- LUKHAS_AGI_2.CORE.voice_profiling.VoiceProfileManager
- LUKHAS_AGI_2.CORE.voice_safety_guard.VoiceSafetyFilter
"""

import os
import random
import re
import time
import uuid
from typing import Any, Optional

from candidate.core.common import get_logger
# Import relevant components
from candidate.core.voice_profiling import VoiceProfile, VoiceProfileManager
from candidate.core.voice_safety_guard import VoiceSafetyFilter

# Import personality integration
try:
    from candidate.core.personality.voice_personality import \
        VoicePersonalityIntegrator

    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False
    logging.warning("Voice personality integration not available")

# Import memory helix for accent learning and word curiosity
try:
    from candidate.core.voice_memory_helix import VoiceMemoryHelix

    MEMORY_HELIX_AVAILABLE = True
except ImportError:
    MEMORY_HELIX_AVAILABLE = False
    logging.warning("Voice memory helix not available for accent learning")

# Try to import symbolic world for enhanced reasoning
try:
    from bio_symbolic.symbolic_world import SymbolicWorld

    SYMBOLIC_WORLD_AVAILABLE = True
except ImportError:
    SYMBOLIC_WORLD_AVAILABLE = False

# Configure logging
logger = get_logger(__name__)


class VoiceNode:
    """
    Unified voice processing node for LUKHAS AGI.

    This node integrates all voice-related functionality:
    - Voice synthesis and recognition
    - Profile management and adaptation
    - Emotional resonance and tone adaptation
    - Voice safety and compliance
    - Handoff orchestration between LUKHAS and other voice sources

    It follows the node architecture pattern for seamless integration with
    the LUKHAS core system.
    """

    def __init__(self, core_interface=None, config: dict[str, Any] = None):
        """
        Initialize the Voice Node with access to the core system

        Args:
            core_interface: Interface to the LUKHAS core system
            config: Configuration dictionary
        """
        self.core = core_interface
        self.config = config or {}

        # Initialize subcomponents
        self.profile_manager = VoiceProfileManager(core_interface)
        self.safety_filter = VoiceSafetyFilter(self.config.get("safety_config"))

        # Initialize personality integration
        self.personality_integrator = None
        if PERSONALITY_AVAILABLE and self.config.get("use_personality", True):
            try:
                self.personality_integrator = VoicePersonalityIntegrator(
                    core_interface, self.config.get("personality_config")
                )
                logger.info("Voice personality integration enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize personality integration: {e}")

        # Initialize memory helix for accent learning and word curiosity
        self.memory_helix = None
        if MEMORY_HELIX_AVAILABLE and self.config.get("use_memory_helix", True):
            try:
                self.memory_helix = VoiceMemoryHelix(
                    core_interface, self.config.get("memory_helix_config")
                )
                logger.info(
                    "Voice memory helix enabled for accent learning and word curiosity"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize memory helix: {e}")

        # Initialize optional symbolic reasoning
        self.symbolic_world = None
        if SYMBOLIC_WORLD_AVAILABLE and self.config.get("use_symbolic_reasoning", True):
            try:
                self.symbolic_world = SymbolicWorld()
                logger.info("Symbolic reasoning enabled for voice contextualization")
            except Exception as e:
                logger.warning(f"Failed to initialize symbolic reasoning: {e}")

        # Track active voice sessions and history
        self.active_sessions = {}
        self.voice_history = []
        self.max_history_size = 100
        self.last_used_profile = None
        self.default_voice_id = self.config.get("default_voice_id", "lukhas_main")

        # Voice provider configurations with enhanced options
        self.voice_providers = {
            "elevenlabs": {
                "api_key": os.environ.get("ELEVENLABS_API_KEY", ""),
                "enabled": self.config.get("enable_elevenlabs", True),
                "fallback_voice_id": "s0XGIcqmceN2l7kjsqoZ",  # Default ElevenLabs voice
                "model": "eleven_monolingual_v1",
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "speaker_boost": True,
            },
            "coqui": {
                "enabled": self.config.get("enable_coqui", False),
                "model": "tts_models/en/vctk/vits",
                "speed": 1.0,
                "noise": 0.667,
            },
            "edge_tts": {
                "enabled": True,  # Always available as fallback
                "voice": "en-US-GuyNeural",
            },
            "system_tts": {
                "enabled": True,  # Always available as fallback
            },
        }

        # Audio storage path
        self.audio_storage_path = os.path.join(os.getcwd(), "generated_audio")
        if not os.path.exists(self.audio_storage_path):
            os.makedirs(self.audio_storage_path)

        # Register with core if available
        if self.core:
            try:
                self.core.register_component("voice_node", self, self.process_message)

                # Subscribe to relevant events
                self.core.subscribe_to_events(
                    "user_interaction",
                    self.handle_interaction_event,
                    "voice_node",
                )

                # Subscribe to emotion events to adapt voice
                self.core.subscribe_to_events(
                    "emotion_change", self.handle_emotion_change, "voice_node"
                )

                logger.info("VoiceNode registered with core system")
            except Exception as e:
                logger.error(f"Failed to register VoiceNode with core: {e}")

    async def process_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """
        Process incoming messages directed to the voice node

        Args:
            message: The message to process

        Returns:
            Response message
        """
        message_type = message.get("type")

        if message_type == "voice_output":
            return await self.synthesize_voice(
                message.get("text", ""),
                message.get("profile_name"),
                message.get("emotion"),
                message.get("context", {}),
            )
        elif message_type == "voice_input":
            return await self.process_voice_input(
                message.get("audio_data"), message.get("context", {})
            )
        elif message_type == "voice_handoff":
            return await self.manage_voice_handoff(
                message.get("user_query", ""), message.get("context_state", {})
            )
        else:
            logger.warning(f"Unknown message type: {message_type}")
            return {
                "status": "error",
                "message": f"Unknown message type: {message_type}",
            }

    async def synthesize_voice(
        self,
        text: str,
        profile_name: Optional[str] = None,
        emotion: Optional[str] = None,
        actor: str = "Lukhas",
        voice_id: Optional[str] = None,
        context: dict[str, Any] = None,
        provider: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Synthesize voice output with the specified profile and emotion

        Args:
            text: Text to synthesize
            profile_name: Name of the voice profile to use (defaults to last used or default)
            emotion: Emotional tone override (if not specified, uses context)
            actor: Voice actor to use ("Lukhas" or "GPT")
            voice_id: Optional specific voice ID to use
            context: Additional context for synthesis
            provider: Optional specific provider to use

        Returns:
            Response with audio path or error
        """
        # Validate and process input
        if context is None:
            context = {}
        if not text.strip():
            text = "Hello, I am Lukhas."

        # Create synthesis ID for tracking
        synthesis_id = f"synth_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # Safety check first
        safety_result = self.safety_filter.check_content(text, context)
        if not safety_result["safe"]:
            logger.warning(f"Safety check failed: {safety_result['reason']}")
            return {
                "id": synthesis_id,
                "status": "rejected",
                "reason": safety_result["reason"],
                "alternative": safety_result.get("alternative_text"),
            }

        # Apply personality enhancement if available
        original_text = text
        if self.personality_integrator and context.get("enhance_personality", True):
            try:
                # Enhance text with personality
                text = await self.personality_integrator.enhance_voice_text(
                    text, emotion or "neutral", context
                )

                # Get voice modulation parameters
                personality_modulation = (
                    self.personality_integrator.get_voice_modulation(
                        emotion or "neutral", context
                    )
                )
                if personality_modulation:
                    # Store in context for use during synthesis
                    context["personality_modulation"] = personality_modulation

                # Record personality adaptation
                self.personality_integrator.adapt_to_interaction(
                    {
                        "type": "voice_synthesis",
                        "text_length": len(text),
                        "emotion": emotion,
                        "context": {
                            k: v
                            for k, v in context.items():
                            if isinstance(v, (str, int, float, bool)):
                        },
                    }
                )

                logger.debug("Text enhanced with personality")
            except Exception as e:
                logger.warning(f"Failed to apply personality enhancement: {e}")
                text = original_text  # Fallback to original

        # Apply memory helix for accent adaptation and word learning if available
        if self.memory_helix and not context.get("skip_memory_helix", False):
            try:
                # Detect new words for curiosity
                new_words = await self.memory_helix.detect_new_words(text)
                if new_words and context.get("enable_word_curiosity", True):
                    # Mark that we found new words - this could trigger curiosity in
                    # responses
                    context["new_words_detected"] = new_words

                # Check for accent-specific pronunciations
                accent_info = context.get(
                    "accent_info"
                ) or await self._detect_user_accent(context)
                if accent_info:
                    # Store accent info in context
                    context["accent_info"] = accent_info

                    # Apply accent-specific pronunciations if we should adapt
                    if context.get("adapt_to_accent", True):
                        text = await self._apply_accent_pronunciations(
                            text, accent_info
                        )

                # Check if we should be curious about pronunciation
                if random.random() < 0.15 and context.get(:
                    "enable_word_curiosity", True
                ):
                    curious_word = self.memory_helix.get_curious_word()
                    if curious_word:
                        context["curious_about_word"] = curious_word

                logger.debug("Applied memory helix for accent adaptation")
            except Exception as e:
                logger.warning(f"Failed to apply memory helix: {e}")

        # Apply symbolic reasoning to enhance context if available
        if self.symbolic_world and context:
            try:
                enhanced_context = self.symbolic_world.enhance_voice_context(
                    text, context
                )
                if enhanced_context:
                    context = enhanced_context
                    logger.debug("Context enhanced with symbolic reasoning")
            except Exception as e:
                logger.warning(f"Failed to apply symbolic reasoning: {e}")

        # Determine profile to use
        profile = None
        if profile_name:
            profile = self.profile_manager.get_profile(profile_name)
        elif self.last_used_profile:
            profile = self.last_used_profile
        else:
            # Get default profile
            profiles = self.profile_manager.list_profiles()
            if profiles:
                profile = profiles[0]

        if not profile:
            logger.warning("No voice profile available, creating default")
            profile_id = self.profile_manager.create_profile("Default", {})
            profile = self.profile_manager.get_profile(profile_id)

        # Determine emotional tone if not specified
        if not emotion and self.core:
            try:
                emotional_state = await self.core.get_emotional_state()
                emotion = emotional_state.get("emotion", "neutral")
            except Exception as e:
                logger.warning(f"Failed to get emotional state: {e}")
                emotion = "neutral"
                emotion = "neutral"

        # Default to neutral emotion
        emotion = emotion or "neutral"

        # Track this profile as last used
        self.last_used_profile = profile

        # Generate unique audio ID
        audio_id = f"lukhas_voice_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # Get voice parameters based on emotion and profile
        voice_params = self._get_voice_parameters(profile, emotion, actor)

        # Determine which provider to use
        selected_provider = provider or self._select_provider(context, emotion)

        # Map actor to voice ID if not specified
        if not voice_id:
            voice_id = self._map_actor_to_voice(actor, selected_provider)

        # Record in synthesis history
        synthesis_entry = {
            "id": synthesis_id,
            "text": text,
            "emotion": emotion,
            "actor": actor,
            "provider": selected_provider,
            "timestamp": time.time(),
            "parameters": voice_params,
        }

        self.voice_history.append(synthesis_entry)
        if len(self.voice_history) > self.max_history_size:
            self.voice_history = self.voice_history[-self.max_history_size:]

        # File path for audio output
        file_extension = "mp3" if selected_provider == "elevenlabs" else "wav"
        audio_path = os.path.join(
            self.audio_storage_path, f"{audio_id}.{file_extension}"
        )

        # Try synthesis with selected provider
        try:
            if (:
                selected_provider == "elevenlabs"
                and self.voice_providers["elevenlabs"]["enabled"]
            ):
                # This would call the actual ElevenLabs API
                # For now, simulate a successful synthesis
                self.voice_providers["elevenlabs"]

                # Generate audio file path

                logger.info(
                    f"Synthesized voice with ElevenLabs, profile {profile.name},"
                    emotion {emotion}"
                )
                synthesis_entry["status"] = "success"
                synthesis_entry["audio_path"] = audio_path
                synthesis_entry["audio_id"] = audio_id

            elif (:
                selected_provider == "coqui"
                and self.voice_providers["coqui"]["enabled"]
            ):
                # This would use Coqui TTS
                self.voice_providers["coqui"]

                logger.info(
                    f"Synthesized voice with Coqui TTS, profile {profile.name},
                    emotion {emotion}"
                )
                synthesis_entry["status"] = "success"
                synthesis_entry["audio_path"] = audio_path
                synthesis_entry["audio_id"] = audio_id

            elif (:
                selected_provider == "edge_tts"
                and self.voice_providers["edge_tts"]["enabled"]
            ):
                # This would use Edge TTS
                self.voice_providers["edge_tts"]

                logger.info(
                    f"Synthesized voice with Edge TTS, profile {profile.name},
                    emotion {emotion}"
                )
                synthesis_entry["status"] = "success"
                synthesis_entry["audio_path"] = audio_path
                synthesis_entry["audio_id"] = audio_id

            else:
                # Fallback to system TTS
                logger.info(
                    f"Synthesized voice with system TTS, profile {profile.name},
                    emotion {emotion}"
                )
                synthesis_entry["status"] = "success"
                synthesis_entry["audio_path"] = audio_path
                synthesis_entry["audio_id"] = audio_id
                synthesis_entry["provider"] = "system_tts"

        except Exception as e:
            # Handle failures with graceful fallback
            logger.error(f"{selected_provider} synthesis failed: {e}")

            # Try system TTS as final fallback
            try:
                # This would use system TTS
                logger.info(
                    f"Falling back to system TTS, profile {profile.name},
                    emotion {emotion}"
                )
                synthesis_entry["status"] = "success"
                synthesis_entry["audio_path"] = audio_path.replace(
                    file_extension, "wav"
                )
                synthesis_entry["audio_id"] = audio_id
                synthesis_entry["provider"] = "system_tts"
                synthesis_entry["fallback_reason"] = str(e)
            except Exception as e2:
                logger.error(f"System TTS fallback failed: {e2}")
                synthesis_entry["status"] = "error"
                synthesis_entry["message"] = (
                    f"All synthesis methods failed. Original error: {e},
                    Fallback error: {e2}"
                )
                return synthesis_entry

        return synthesis_entry

    async def process_voice_input(
        self, audio_data, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Process voice input and convert to text

        Args:
            audio_data: Audio data to process
            context: Additional context

        Returns:
            Response with transcribed text or error
        """
        # This would integrate with a speech recognition service
        # For now, return a placeholder
        if context is None:
            context = {}
        logger.info("Processing voice input")
        return {
            "status": "success",
            "text": "[Voice transcription would happen here]",
            "confidence": 0.95,
        }

    async def manage_voice_handoff(
        self, user_query: str, context_state: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        Orchestrate voice handoff between Lukhas and GPT

        Args:
            user_query: Latest user input
            context_state: Emotional score, urgency, etc.

        Returns:
            Handoff decision
        """
        if context_state is None:
            context_state = {}
        emotion = context_state.get("emotion", "neutral")
        intensity = context_state.get("intensity", 0)
        dst_urgency = context_state.get("DST_urgency", False)
        user_tier = context_state.get("user_tier", 1)

        # Logic matrix for handoff decisions
        if dst_urgency or intensity >= 7:
            return {"source": "Lukhas", "tone": "urgent", "handoff": False}
        if "dream" in user_query.lower() or emotion == "reflective":
            return {"source": "Lukhas", "tone": "calm", "handoff": False}
        if user_tier <= 2:
            return {"source": "GPT", "tone": "neutral", "handoff": True}

        return {"source": "Lukhas", "tone": emotion, "handoff": False}

    async def handle_interaction_event(self, event: dict[str, Any]) -> None:
        """
        Handle user interaction events to adapt voice profile and personality

        Args:
            event: The interaction event
        """
        if not event:
            return

        # Update personality integrator if available
        if self.personality_integrator:
            try:
                # Convert event to interaction data format
                interaction_data = {
                    "type": event.get("type", "unknown"),
                    "timestamp": event.get("timestamp", time.time()),
                    "user_id": event.get("user_id"),
                    "content_length": len(event.get("content", "")),
                    "emotion": event.get("emotion", "neutral"),
                    "context": event.get("context", {}),
                }

                # Adapt personality to this interaction
                self.personality_integrator.adapt_to_interaction(interaction_data)
                logger.debug("Personality adapted to interaction event")
            except Exception as e:
                logger.warning(f"Failed to adapt personality to interaction: {e}")

    async def handle_emotion_change(self, event: dict[str, Any]) -> None:
        """
        Handle emotion change events to adapt voice profile and personality

        Args:
            event: The emotion change event
        """
        if not event:
            return

        # Extract emotion data
        emotion = event.get("emotion", "neutral")
        intensity = event.get("intensity", 0.5)
        source = event.get("source", "unknown")

        # Update voice profile selection based on emotion
        if emotion in ["excited", "urgent"] and intensity > 0.7:
            # Use more expressive profiles for high intensity emotions
            profiles = self.profile_manager.list_profiles()
            expressive_profiles = [
                p for p in profiles if "expressive" in p.name.lower()
            ]

            if expressive_profiles:
                self.last_used_profile = expressive_profiles[0]
                logger.debug(f"Switched to expressive profile due to {emotion} emotion")

        # Update personality integrator if available
        if self.personality_integrator:
            try:
                # Convert event to interaction data format
                interaction_data = {
                    "type": "emotion_change",
                    "emotion": emotion,
                    "intensity": intensity,
                    "source": source,
                }

                # Adapt personality to this emotion change
                self.personality_integrator.adapt_to_interaction(interaction_data)
                logger.debug(f"Personality adapted to {emotion} emotion")
            except Exception as e:
                logger.warning(f"Failed to adapt personality to emotion change: {e}")

    def get_status(self) -> dict[str, Any]:
        """Get status of the voice node"""
        status = {
            "active": True,
            "profile_count": len(self.profile_manager.list_profiles()),
            "last_used_profile": (
                self.last_used_profile.name if self.last_used_profile else None
            ),
            "providers": {
                name: {"enabled": config["enabled"]}
                for name, config in self.voice_providers.items():
            },
        }

        # Add personality status if available
        if self.personality_integrator:
            try:
                status["personality"] = {
                    "active": True,
                    "traits": self.personality_integrator.personality_traits,
                }
            except Exception as e:
                logger.warning(f"Failed to get personality status: {e}")

        return status

    def _select_provider(self, context: Optional[dict[str, Any]], emotion: str) -> str:
        """
        Select the appropriate TTS provider based on context.

        Args:
            context: User context
            emotion: Emotional tone

        Returns:
            Provider name
        """
        # Default provider
        provider = "edge_tts"

        if not context:
            return provider

        # Check user tier if available
        user_tier = context.get("user_tier", 1)

        # Premium users get ElevenLabs
        if user_tier >= 3 and self.voice_providers["elevenlabs"]["enabled"]:
            provider = "elevenlabs"
        # Mid-tier users get Coqui
        elif user_tier >= 2 and self.voice_providers["coqui"]["enabled"]:
            provider = "coqui"

        # For certain emotional states, prefer higher quality TTS
        if emotion in ["dream", "reflective"]:
            # At least use Coqui for dream states
            if provider == "edge_tts" and self.voice_providers["coqui"]["enabled"]:
                provider = "coqui"

        return provider

    def _get_voice_parameters(:
        self, profile: VoiceProfile, emotion: str, actor: str
    ) -> dict[str, Any]:
        """
        Get voice parameters based on profile, emotion, and personality.

        Args:
            profile: Voice profile
            emotion: Emotional tone
            actor: Voice actor

        Returns:
            Voice parameters
        """
        # Base parameters
        params = {}

        # Add base parameters from profile
        if hasattr(profile, "parameters") and profile.parameters:
            params.update(profile.parameters)

        # Adjust for emotion
        if emotion == "calm":
            params["pitch"] = params.get("pitch", 0) - 0.2
            params["rate"] = params.get("rate", 1) * 0.9
            params["volume"] = params.get("volume", 1) * 0.9
        elif emotion == "excited":
            params["pitch"] = params.get("pitch", 0) + 0.3
            params["rate"] = params.get("rate", 1) * 1.15
            params["volume"] = params.get("volume", 1) * 1.2
        elif emotion == "urgent":
            params["pitch"] = params.get("pitch", 0) + 0.1
            params["rate"] = params.get("rate", 1) * 1.2
            params["volume"] = params.get("volume", 1) * 1.3
        elif emotion == "reflective":
            params["pitch"] = params.get("pitch", 0) - 0.1
            params["rate"] = params.get("rate", 1) * 0.85
            params["volume"] = params.get("volume", 1) * 0.8
        elif emotion == "dream":
            params["pitch"] = params.get("pitch", 0) - 0.3
            params["rate"] = params.get("rate", 1) * 0.8
            params["volume"] = params.get("volume", 1) * 0.7

        return params

    def _map_actor_to_voice(self, actor: str, provider: str) -> str:
        """
        Map actor to provider-specific voice ID.

        Args:
            actor: Actor name ('Lukhas' or 'GPT')
            provider: Voice provider

        Returns:
            Voice ID for the specified provider
        """
        # Default voice IDs
        voice_map = {
            "elevenlabs": {
                "Lukhas": "pNInz6obpgDQGcFmaJgB",  # Example voice ID
                "GPT": "EXAVITQu4vr4xnSDxMaL",  # Example voice ID
            },
            "edge_tts": {
                "Lukhas": "en-US-GuyNeural",
                "GPT": "en-US-AriaNeural",
            },
            "coqui": {"Lukhas": "p326", "GPT": "p225"},
        }

        # Get voice ID for the specified provider and actor
        provider_map = voice_map.get(provider, {})
        voice_id = provider_map.get(
            actor, provider_map.get("Lukhas", self.default_voice_id)
        )

        return voice_id

    async def _detect_user_accent(
        self, context: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        Detect the user's accent from context or audio if available.

        Args:
            context: Interaction context that may contain accent clues

        Returns:
            Accent information dictionary or None if not detected
        """
        # First check if user has a stored accent preference
        user_id = context.get("user_id")
        if user_id and self.core:
            try:
                user_preferences = await self.core.get_user_preferences(user_id)
                if user_preferences and "accent" in user_preferences:
                    logger.debug(f"Using stored accent preference for user {user_id}")
                    return user_preferences["accent"]
            except Exception as e:
                logger.warning(f"Failed to retrieve user accent preference: {e}")

        # Check for audio sample in context to detect accent
        audio_sample = context.get("audio_sample")
        if audio_sample and self.memory_helix:
            try:
                # Use memory helix's accent detection capability
                accent_info = await self.memory_helix.detect_accent(audio_sample)
                if accent_info and accent_info.get("confidence", 0) > 0.6:
                    logger.debug(f"Detected accent from audio: {accent_info['name']}")
                    return accent_info
            except Exception as e:
                logger.warning(f"Failed to detect accent from audio: {e}")

        # Try to infer from location data if available
        location = context.get("location") or context.get("user_location")
        if location:
            # Map location to likely accent (simplified)
            accent_map = {
                "US": {"name": "general_american", "region": "North America"},
                "UK": {
                    "name": "received_pronunciation",
                    "region": "United Kingdom",
                },
                "AU": {"name": "australian", "region": "Australia"},
                "CA": {"name": "canadian", "region": "Canada"},
                "IN": {"name": "indian", "region": "South Asia"},
                "SG": {"name": "singaporean", "region": "Southeast Asia"},
            }

            country_code = (
                location.get("country_code")
                if isinstance(location, dict):
                else str(location)[:2].upper():
            )
            if country_code in accent_map:
                logger.debug(
                    f"Inferred accent from location: {accent_map[country_code]['name']}"
                )
                return accent_map[country_code]

        # If no accent detected but we have a memory helix with accent data
        if (:
            self.memory_helix
            and hasattr(self.memory_helix, "accent_memory")
            and self.memory_helix.accent_memory
        ):
            # Use the most common accent in our memory
            accent_counts = {
                name: len(data.get("example_words", []))
                for name, data in self.memory_helix.accent_memory.items():
            }

            if accent_counts:
                most_common_accent = max(accent_counts.items(), key=lambda x: x[1])[0]
                accent_data = self.memory_helix.accent_memory[most_common_accent]
                logger.debug(
                    f"Using most common accent from memory: {most_common_accent}"
                )
                return {
                    "name": most_common_accent,
                    "region": accent_data.get("region", "unknown"),
                    "confidence": 0.5,  # Medium confidence as it's a fallback
                    "source": "memory_fallback",
                }

        # Fall back to a default if no accent detected
        logger.debug("No accent detected, using general_american default")
        return {
            "name": "general_american",
            "region": "North America",
            "confidence": 0.4,
            "source": "default",
        }

    async def _apply_accent_pronunciations(
        self, text: str, accent_info: dict[str, Any]
    ) -> str:
        """
        Apply accent-specific pronunciations to the text for more natural speech.

        Args:
            text: The text to modify with accent-specific pronunciations
            accent_info: Information about the detected accent

        Returns:
            Text modified with accent-specific pronunciations
        """
        if not self.memory_helix or not accent_info:
            return text

        # Get accent name
        accent_name = accent_info.get("name", "general_american")

        # Extract words from the text
        words = re.findall(r"\b[a-zA-Z\']+\b", text)
        if not words:
            return text

        # Track replacements to make
        replacements = []

        # Check each word for accent-specific pronunciations
        for word in words:
            original_word = word
            word_lower = word.lower()

            # Skip short words as they usually don't need pronunciation adaptation
            if len(word_lower) <= 3:
                continue

            # Get pronunciation for this word in this accent
            pronunciation = self.memory_helix.get_pronunciation_for_word(
                word_lower, accent_name
            )
            if not pronunciation:
                continue

            # Only apply if the pronunciation differs
            if pronunciation == word_lower:
                continue

            # Format the pronunciation based on the TTS provider we'll likely use
            provider = self._select_provider({"accent": accent_info}, "neutral")

            # Format for different TTS systems
            if provider == "elevenlabs":
                # ElevenLabs can handle SSML with phoneme tags
                replacement = f'<phoneme alphabet="ipa" ph="{pronunciation}">{original_word}</phoneme>'
            elif provider == "edge_tts":
                # Edge TTS can also handle SSML
                replacement = f'<phoneme alphabet="ipa" ph="{pronunciation}">{original_word}</phoneme>'
            else:
                # For other providers, use a simple text substitution approach
                # This is a simplification - real implementation would be more
                # sophisticated
                replacement = f"{original_word}({pronunciation})"

            # Add to replacements list
            replacements.append((original_word, replacement))

        # Apply replacements to the text
        modified_text = text
        for original, replacement in replacements:
            # Only replace whole words (not parts of words)
            modified_text = re.sub(
                r"\b" + re.escape(original) + r"\b", replacement, modified_text
            )

        # Log how many words were adapted
        if replacements:
            logger.debug(
                f"Applied {len(replacements)} accent-specific pronunciations for {accent_name} accent"
            )

        return modified_text
