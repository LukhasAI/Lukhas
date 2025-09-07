"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: voice_synthesis.py
Advanced: voice_synthesis.py
Integration Date: 2025-05-31T07:55:28.339501
"""
from typing import List
from typing import Dict
import time
import streamlit as st

import logging
import os
import tempfile
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

import requests

from candidate.core.common import get_logger

"""
Advanced Voice Synthesis Module

This module provides emotionally intelligent voice synthesis capabilities that adapt
to user context and interaction patterns. It implements Steve Jobs' principles of
elegant human-computer interaction with Sam Altman's vision for advanced AI capabilities.
"""


logger = get_logger(__name__)


class VoiceEmotion(Enum):
    """Emotional tones for voice synthesis"""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    SERIOUS = "serious"
    GENTLE = "gentle"
    EXCITED = "excited"
    CONCERNED = "concerned"
    PROFESSIONAL = "professional"


class VoiceProvider(Enum):
    """Available voice synthesis providers"""

    EDGE_TTS = "edge_tts"
    ELEVENLABS = "elevenlabs"
    COQUI = "coqui"
    SYSTEM = "system"  # OS-provided synthesis


class VoiceSynthesisProvider(ABC):
    """
    Abstract base class for voice synthesis providers.
    Each provider must implement the synthesize method.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.logger = logging.getLogger(f"VoiceSynthesis.{self.__class__.__name__}")
        self.config = config or {}

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        emotion: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Synthesize speech from text.

        Args:
            text: The text to convert to speech
            voice_id: The voice to use
            emotion: The emotion to convey
            params: Additional parameters for synthesis

        Returns:
            Dictionary with synthesis results including audio data
        """

    def is_available(self) -> bool:
        """
        Check if this provider is available for use.

        Returns:
            True if the provider is available, False otherwise
        """
        return True

    def get_default_voice_id(self) -> str:
        """
        Get the default voice ID for this provider.

        Returns:
            Default voice ID
        """
        return self.config.get("default_voice", "default")

    def _apply_emotion(self, params: dict[str, Any], emotion: str) -> dict[str, Any]:
        """
        Apply emotion-specific adjustments to synthesis parameters.

        Args:
            params: The base parameters
            emotion: The emotion to apply

        Returns:
            Updated parameters
        """
        emotion_mappings = {
            "happiness": {"pitch": 1.1, "speed": 1.05, "energy": 1.2},
            "sadness": {"pitch": 0.9, "speed": 0.95, "energy": 0.8},
            "anger": {"pitch": 1.05, "speed": 1.1, "energy": 1.3},
            "fear": {"pitch": 1.1, "speed": 1.15, "energy": 1.1},
            "surprise": {"pitch": 1.15, "speed": 1.0, "energy": 1.2},
            "neutral": {"pitch": 1.0, "speed": 1.0, "energy": 1.0},
        }

        if emotion and emotion in emotion_mappings:
            new_params = params.copy()
            for key, value in emotion_mappings[emotion].items():
                if key in new_params:
                    new_params[key] *= value
                else:
                    new_params[key] = value
            return new_params

        return params


class ElevenLabsProvider(VoiceSynthesisProvider):
    """
    Implements speech synthesis using ElevenLabs API.
    Provides high-quality, emotional TTS capabilities.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voice_cache = {}  # Cache of available voices

    def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        emotion: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Synthesize speech using ElevenLabs API.

        Args:
            text: The text to synthesize
            voice_id: ElevenLabs voice ID
            emotion: The emotion to convey
            params: Additional parameters

        Returns:
            Dictionary with synthesis results
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "ElevenLabs API key not configured",
            }

        # Set default values
        params = params or {}
        voice_id = voice_id or self.get_default_voice_id()

        # Apply emotional adjustments to parameters
        if emotion:
            params = self._apply_emotion(params, emotion)

        # Prepare request data
        url = f"{self.base_url}/text-to-speech/{voice_id}/stream"
        headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        data = {
            "text": text,
            "model_id": params.get("model_id", "eleven_monolingual_v1"),
            "voice_settings": {
                "stability": params.get("stability", 0.5),
                "similarity_boost": params.get("similarity", 0.75),
                "style": params.get("style", 0.0),
                "speaker_boost": params.get("speaker_boost", True),
            },
        }

        try:
            # Make API request
            response = requests.post(url, json=data, headers=headers, timeout=30)

            if response.status_code != 200:
                self.logger.error(f"ElevenLabs API error: {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "response": response.text,
                }

            # Process successful response
            audio_content = response.content

            return {
                "success": True,
                "audio_data": audio_content,
                "format": "mp3",
                "provider": "elevenlabs",
                "voice_id": voice_id,
                "text": text,
            }

        except requests.exceptions.Timeout:
            self.logger.error("Timeout while connecting to ElevenLabs API")
            return {"success": False, "error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"ElevenLabs API request error: {e!s}")
            return {"success": False, "error": f"Request error: {e!s}"}
        except Exception as e:
            self.logger.error(f"ElevenLabs synthesis error: {e!s}")
            return {"success": False, "error": str(e)}

    def is_available(self) -> bool:
        """Check if ElevenLabs API is configured and available"""
        return self.api_key is not None and len(self.api_key) > 0

    def get_available_voices(self) -> list[dict[str, Any]]:
        """
        Get list of available voices from ElevenLabs.

        Returns:
            List of voice dictionaries with id, name, etc.
        """
        if not self.is_available():
            return []

        # Check if we have cached results
        if self.voice_cache:
            return list(self.voice_cache.values())

        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}

            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code != 200:
                self.logger.error(f"Failed to get voices: {response.text}")
                return []

            data = response.json()
            voices = data.get("voices", [])

            # Cache results
            self.voice_cache = {voice["voice_id"]: voice for voice in voices}

            return voices

        except requests.exceptions.Timeout:
            self.logger.error("Timeout while fetching ElevenLabs voices")
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error while fetching ElevenLabs voices: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching ElevenLabs voices: {e}")
            return []

    def get_default_voice_id(self) -> str:
        """Get the default voice ID for ElevenLabs"""
        default_voice = self.config.get("default_voice")
        if default_voice:
            return default_voice

        # Get first available voice if no default specified
        voices = self.get_available_voices()
        if voices:
            return voices[0]["voice_id"]

        # Fallback to ElevenLabs default voice
        return "21m00Tcm4TlvDq8ikWAM"  # Rachel voice


class EdgeTTSProvider(VoiceSynthesisProvider):
    """
    Implements speech synthesis using Microsoft Edge TTS.
    Provides reliable, free TTS with multiple voices and languages.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(config)
        # Lazy import edge-tts - will be imported when needed
        self.edge_tts = None
        self.available_voices = []

    def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        emotion: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Synthesize speech using Edge TTS.

        Args:
            text: The text to synthesize
            voice_id: Voice ID (e.g., "en-US-AriaNeural")
            emotion: The emotion to convey
            params: Additional parameters

        Returns:
            Dictionary with synthesis results
        """
        # Lazy import edge-tts
        if not self.edge_tts:
            try:
                import edge_tts

                self.edge_tts = edge_tts
            except ImportError:
                self.logger.error("edge-tts package not installed")
                return {
                    "success": False,
                    "error": "edge-tts package not installed",
                }

        # Set default values
        params = params or {}
        voice_id = voice_id or self.get_default_voice_id()

        # Apply emotional adjustments
        if emotion:
            params = self._apply_emotion(params, emotion)

        # Prepare synthesis parameters
        rate = f"{params.get('speed', 1.0):+.1f}%"
        volume = f"{params.get('volume', 0):+.1f}%"
        pitch = f"{(params.get('pitch', 1.0) - 1.0) * 100:+.1f}Hz"

        # Create output file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.close()
        output_file = temp_file.name

        try:
            # Run edge-tts in async mode
            import asyncio

            async def run_edge_tts():
                communicate = self.edge_tts.Communicate(text, voice_id, rate=rate, volume=volume, pitch=pitch)
                await communicate.save(output_file)

            # Run the async function
            asyncio.run(run_edge_tts())

            # Read the audio data
            with open(output_file, "rb") as f:
                audio_data = f.read()

            # Clean up the temporary file
            os.unlink(output_file)

            return {
                "success": True,
                "audio_data": audio_data,
                "format": "mp3",
                "provider": "edge_tts",
                "voice_id": voice_id,
                "text": text,
            }

        except Exception as e:
            self.logger.error(f"Edge TTS synthesis error: {e!s}")
            # Clean up on error
            if os.path.exists(output_file):
                try:
                    os.unlink(output_file)
                except OSError as e:
                    logger.warning(f"Failed to clean up output file {output_file}: {e}")

            return {"success": False, "error": str(e)}

    def is_available(self) -> bool:
        """Check if Edge TTS is available"""
        try:
            import edge_tts

            self.edge_tts = edge_tts
            return True
        except ImportError:
            return False

    def get_available_voices(self) -> list[dict[str, Any]]:
        """
        Get list of available voices from Edge TTS.

        Returns:
            List of voice dictionaries
        """
        if not self.is_available():
            return []

        if self.available_voices:
            return self.available_voices

        try:
            import asyncio

            async def get_voices():
                return await self.edge_tts.VoicesManager.create()

            voices_manager = asyncio.run(get_voices())
            voices = []

            for voice in voices_manager.voices:
                voices.append(
                    {
                        "voice_id": voice["ShortName"],
                        "name": voice["FriendlyName"],
                        "gender": voice["Gender"],
                        "language": voice["Locale"],
                        "provider": "edge_tts",
                    }
                )

            self.available_voices = voices
            return voices

        except Exception as e:
            self.logger.error(f"Error fetching Edge TTS voices: {e}")
            return []

    def get_default_voice_id(self) -> str:
        """Get the default voice ID for Edge TTS"""
        default_voice = self.config.get("default_voice")
        if default_voice:
            return default_voice

        # English female voice as default
        return "en-US-AriaNeural"


class CoquiProvider(VoiceSynthesisProvider):
    """
    Implements speech synthesis using Coqui TTS.
    Provides high-quality open-source TTS with XTTS model support.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(config)
        self.tts = None
        self.model_path = self.config.get("model_path")
        self.voices_dir = self.config.get("voices_dir", "./voices")

    def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        emotion: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Synthesize speech using Coqui TTS.

        Args:
            text: The text to synthesize
            voice_id: Voice reference file
            emotion: The emotion to convey
            params: Additional parameters

        Returns:
            Dictionary with synthesis results
        """
        # Initialize TTS if needed
        if not self.is_available():
            return {"success": False, "error": "Coqui TTS not available"}

        # Set default values
        params = params or {}
        voice_id = voice_id or self.get_default_voice_id()

        # Apply emotional adjustments
        if emotion:
            params = self._apply_emotion(params, emotion)

        # Prepare speaker reference path
        speaker_wav = None
        if voice_id and voice_id != "default":
            speaker_wav = os.path.join(self.voices_dir, f"{voice_id}.wav")
            if not os.path.exists(speaker_wav):
                speaker_wav = None
                self.logger.warning(f"Speaker reference file not found: {speaker_wav}")

        # Create output file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.close()
        output_file = temp_file.name

        try:
            # Generate speech
            speed = params.get("speed", 1.0)
            language = params.get("language", "en")

            self.tts.tts_to_file(
                text=text,
                file_path=output_file,
                speaker_wav=speaker_wav,
                language=language,
                speed=speed,
            )

            # Read the audio data
            with open(output_file, "rb") as f:
                audio_data = f.read()

            # Clean up the temporary file
            os.unlink(output_file)

            return {
                "success": True,
                "audio_data": audio_data,
                "format": "wav",
                "provider": "coqui",
                "voice_id": voice_id if speaker_wav else "default",
                "text": text,
            }

        except Exception as e:
            self.logger.error(f"Coqui TTS synthesis error: {e!s}")
            # Clean up on error
            if os.path.exists(output_file):
                try:
                    os.unlink(output_file)
                except OSError as e:
                    logger.warning(f"Failed to clean up output file {output_file}: {e}")

            return {"success": False, "error": str(e)}

    def is_available(self) -> bool:
        """Check if Coqui TTS is available and initialize if needed"""
        if self.tts is not None:
            return True

        try:
            from TTS.api import TTS

            # Initialize TTS
            model_path = self.model_path

            if model_path:
                # Load custom model
                self.tts = TTS(model_path=model_path)
            else:
                # Use default XTTS model
                self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

            return True

        except ImportError:
            self.logger.error("TTS package not installed")
            return False
        except Exception as e:
            self.logger.error(f"Error initializing Coqui TTS: {e}")
            return False

    def get_available_voices(self) -> list[dict[str, Any]]:
        """
        Get list of available voice references from voices directory.

        Returns:
            List of voice dictionaries
        """
        if not os.path.exists(self.voices_dir):
            return []

        voices = []
        for file in os.listdir(self.voices_dir):
            if file.endswith(".wav"):
                voice_id = os.path.splitext(file)[0]
                voices.append(
                    {
                        "voice_id": voice_id,
                        "name": voice_id,
                        "provider": "coqui",
                    }
                )

        return voices

    def get_default_voice_id(self) -> str:
        """Get the default voice ID for Coqui TTS"""
        default_voice = self.config.get("default_voice")
        if default_voice:
            return default_voice

        # Check if any voices are available
        voices = self.get_available_voices()
        if voices:
            return voices[0]["voice_id"]

        # No voices available, use default voice
        return "default"
