"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: whisper_client.py
Advanced: whisper_client.py
Integration Date: 2025-05-31T07:55:29.372300
"""

import os
import tempfile
from datetime import datetime
from typing import Any, BinaryIO, Optional, Union

import aiohttp

from candidate.core.common import get_logger
from candidate.core.common.config import settings

logger = get_logger(__name__)


class WhisperClient:
    """
    Client for interacting with OpenAI's Whisper API for speech recognition.
    Provides async methods for transcribing speech.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning(
                "No OpenAI API key provided. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.model = model
        self.api_base = "https://api.openai.com/v1"
        self.session = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                }
            )

    async def transcribe_audio(
        self,
        audio_data: Union[bytes, str, BinaryIO],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        """
        Transcribe audio data to text using Whisper API

        Args:
            audio_data: Audio data as bytes, file path, or file-like object
            language: ISO-639-1 language code (optional)
            prompt: Optional text to guide the transcription
            response_format: Format of the response (json or text)
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Dictionary containing transcription and metadata
        """
        if not self.api_key:
            return {
                "error": "No API key provided",
                "text": "",
                "confidence": 0.0,
            }

        try:
            await self._ensure_session()

            # Process audio data based on type
            file_to_close = None

            try:
                if isinstance(audio_data, bytes):
                    # Create temporary file from bytes
                    fd, temp_path = tempfile.mkstemp(suffix=".wav")
                    file_to_close = os.fdopen(fd, "wb")
                    file_to_close.write(audio_data)
                    file_to_close.close()
                    file_to_close = None  # Prevent double close
                    audio_path = temp_path
                elif isinstance(audio_data, str):
                    # Assume audio_data is a path
                    audio_path = audio_data
                else:
                    # Assume audio_data is a file-like object
                    fd, temp_path = tempfile.mkstemp(suffix=".wav")
                    file_to_close = os.fdopen(fd, "wb")
                    file_to_close.write(audio_data.read() if hasattr(audio_data, "read") else audio_data)
                    file_to_close.close()
                    file_to_close = None  # Prevent double close
                    audio_path = temp_path

                # Prepare form data
                form_data = aiohttp.FormData()
                form_data.add_field(
                    "file",
                    open(audio_path, "rb"),
                    filename=os.path.basename(audio_path),
                    content_type="audio/wav",
                )
                form_data.add_field("model", self.model)
                form_data.add_field("response_format", response_format)
                form_data.add_field("temperature", str(temperature))

                if language:
                    form_data.add_field("language", language)

                if prompt:
                    form_data.add_field("prompt", prompt)

                logger.info("Sending audio data to Whisper API...")

                async with self.session.post(f"{self.api_base}/audio/transcriptions", data=form_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Whisper API error: {response.status} - {error_text}")
                        return {
                            "error": f"API error: {response.status}",
                            "text": "",
                            "confidence": 0.0,
                        }

                    if response_format == "json":
                        data = await response.json()
                        text = data.get("text", "")
                    else:
                        text = await response.text()
                        data = {"text": text}

                    # Calculate confidence heuristic (not provided by Whisper API)
                    confidence = 0.95 if text else 0.0

                    return {
                        "text": text,
                        "confidence": confidence,
                        "model": self.model,
                        "timestamp": datetime.now().isoformat(),
                    }
            finally:
                # Clean up any temporary files
                if file_to_close:
                    file_to_close.close()

        except Exception as e:
            logger.error(f"Error transcribing audio: {e!s}")
            return {"error": str(e), "text": "", "confidence": 0.0}

    async def transcribe_from_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Transcribe audio from a file path

        Args:
            file_path: Path to the audio file
            language: ISO-639-1 language code (optional)
            prompt: Optional text to guide the transcription

        Returns:
            Dictionary containing transcription and metadata
        """
        if not os.path.exists(file_path):
            return {
                "error": f"File not found: {file_path}",
                "text": "",
                "confidence": 0.0,
            }

        return await self.transcribe_audio(file_path, language=language, prompt=prompt)

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
