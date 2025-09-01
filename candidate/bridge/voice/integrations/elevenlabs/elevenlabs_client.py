"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: elevenlabs_client.py
Advanced: elevenlabs_client.py
Integration Date: 2025-05-31T07:55:29.366776
"""

import os
import sys
from datetime import datetime
from typing import Any, Optional

import aiohttp

from candidate.core.common import get_logger

logger = get_logger(__name__)


class ElevenLabsClient:
    """
    Client for interacting with ElevenLabs API for high-quality voice synthesis.
    Provides async methods for generating and managing voice outputs.
    """

    def __init__(self, api_key: Optional[str] = None, voice_id: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.warning(
                "No ElevenLabs API key provided. Set ELEVENLABS_API_KEY environment variable or pass api_key parameter."
            )

        self.voice_id = voice_id or os.environ.get("VOICE_ID", "s0XGIcqmceN2l7kjsqoZ")
        self.api_base = "https://api.elevenlabs.io/v1"
        self.session = None
        BASE_DIR = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        )
        self.audio_storage_path = os.path.join(BASE_DIR, "temp", "audio", "elevenlabs")

        # Create audio storage directory if it doesn't exist
        if not os.path.exists(self.audio_storage_path):
            os.makedirs(self.audio_storage_path)

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json",
                }
            )

    async def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model: str = "eleven_monolingual_v1",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
    ) -> dict[str, Any]:
        """
        Convert text to speech using ElevenLabs API

        Args:
            voice_id: ID of the voice to use (defaults to instance voice_id)
            model: ID of the model to use
            stability: Stability factor (0.0-1.0)
            similarity_boost: Voice clarity/similarity factor (0.0-1.0)
            style: Style factor for more expressive delivery (0.0-1.0)
            use_speaker_boost: Enhance speech generation with speaker boost

        Returns:
            Dictionary containing audio file path and metadata
        """
        if not self.api_key:
            return {"error": "No API key provided"}

        try:
            await self._ensure_session()

            # Use instance voice_id if none provided
            voice_id = voice_id or self.voice_id

            payload = {
                "text": text,
                "model_id": model,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost,
                },
            }

            logger.info(f"Generating speech with ElevenLabs: {text[:50]}...")
            url = f"{self.api_base}/text-to-speech/{voice_id}"

            async with self.session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"ElevenLabs API error: {response.status} - {error_text}")
                    return {
                        "error": f"API error: {response.status}",
                        "audio_path": None,
                    }

                # Get audio content as binary
                audio_data = await response.read()

                # Save to file
                file_path = await self._save_audio(audio_data, text)

                return {
                    "audio_path": file_path,
                    "text": text,
                    "voice_id": voice_id,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error generating speech: {e!s}")
            return {"error": str(e), "audio_path": None}

    async def get_voices(self) -> dict[str, Any]:
        """
        Get available voices from ElevenLabs API

        Returns:
            Dictionary containing voice information
        """
        if not self.api_key:
            return {"error": "No API key provided"}

        try:
            await self._ensure_session()

            url = f"{self.api_base}/voices"
            async with self.session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"ElevenLabs API error: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}"}

                data = await response.json()
                return data

        except Exception as e:
            logger.error(f"Error fetching voices: {e!s}")
            return {"error": str(e)}

    async def get_user_info(self) -> dict[str, Any]:
        """
        Get user information and subscription details

        Returns:
            Dictionary containing user information
        """
        if not self.api_key:
            return {"error": "No API key provided"}

        try:
            await self._ensure_session()

            url = f"{self.api_base}/user"
            async with self.session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"ElevenLabs API error: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}"}

                data = await response.json()
                return data

        except Exception as e:
            logger.error(f"Error fetching user info: {e!s}")
            return {"error": str(e)}

    async def _save_audio(self, audio_data: bytes, text: str) -> str:
        """
        Save audio data to file

        Args:
            audio_data: Binary audio data
            text: Text that was converted to speech

        Returns:
            Path to the saved audio file
        """
        try:
            # Create a filename based on text and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_text = "".join(c if c.isalnum() else "_" for c in text[:30])
            filename = f"{safe_text}_{timestamp}.mp3"
            filepath = os.path.join(self.audio_storage_path, filename)

            # Write audio data to file
            with open(filepath, "wb") as f:
                f.write(audio_data)

            logger.info(f"Saved audio to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving audio: {e!s}")
            return ""

    async def generate_and_play(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> dict[str, Any]:
        """
        Generate speech and play it (for desktop environments)

        Args:
            text: Text to convert to speech
            voice_id: ID of the voice to use (defaults to instance voice_id)
            stability: Stability factor (0.0-1.0)
            similarity_boost: Voice clarity/similarity factor (0.0-1.0)

        Returns:
            Dictionary containing result and metadata
        """
        result = await self.text_to_speech(
            text,
            voice_id=voice_id,
            stability=stability,
            similarity_boost=similarity_boost,
        )

        if "error" in result:
            return result

        # Play audio if a valid path was returned
        audio_path = result.get("audio_path")
        if audio_path and os.path.exists(audio_path):
            try:
                # Try to use platform-specific audio playback
                played = False
                if sys.platform == "darwin":  # macOS
                    played = os.system(f"afplay {audio_path}") == 0
                elif sys.platform == "win32":  # Windows
                    played = os.system(f"start {audio_path}") == 0
                else:  # Linux and other platforms
                    # Try multiple players
                    if (
                        os.system(f"aplay {audio_path}") == 0
                        or os.system(f"mpg123 {audio_path}") == 0
                        or (os.system(f"ffplay -nodisp -autoexit {audio_path} > /dev/null 2>&1") == 0)
                    ):
                        played = True
                    else:
                        logger.warning("Could not find a suitable audio player for Linux")

                result["played"] = played
            except Exception as e:
                logger.error(f"Error playing audio: {e!s}")
                result["played"] = False

        return result

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
