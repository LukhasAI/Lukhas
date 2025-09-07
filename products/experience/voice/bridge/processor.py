import logging
from typing import Dict, List

import streamlit as st

logger = logging.getLogger(__name__)
"""
CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
lukhas AI System - Core Voice Component
File: voice_processor.py
Path: core/voice/voice_processor.py
Created: 2025-06-20
Author: lukhas AI Team

TAGS: [CRITICAL, KeyFile, Voice, Audio]
"""

import json
import os
from enum import Enum
from typing import Any, Optional, Union

import pyttsx3
import speech_recognition as sr

from candidate.core.common import get_logger

logger = get_logger(__name__)


class VoiceMode(Enum):
    """Voice processing modes"""

    TEXT_TO_SPEECH = "tts"
    SPEECH_TO_TEXT = "stt"
    BOTH = "both"


class VoiceProcessor:
    """Main voice processing system for lukhas AGI"""

    def __init__(self, config_path: str = "config/voice_config.json"):
        self.config = self._load_config(config_path)
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.setup_voice_properties()

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load voice configuration"""
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load voice config: {e}")
            return {}

    def setup_voice_properties(self):
        """Configure voice properties from config"""
        config = self.config.get("text_to_speech", {})
        self.engine.setProperty("rate", config.get("rate", 175))
        self.engine.setProperty("volume", config.get("volume", 1.0))

        voices = self.engine.getProperty("voices")
        voice_name = config.get("voice", "en-US-neural-1")
        for voice in voices:
            if voice_name in voice.name:
                self.engine.setProperty("voice", voice.id)
                break

    async def text_to_speech(self, text: str, output_path: Optional[str] = None) -> bool:
        """Convert text to speech

        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file

        Returns:
            bool: Success status
        """
        try:
            if output_path:
                self.engine.save_to_file(text, output_path)
            else:
                self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            return False

    async def speech_to_text(self, audio_path: Optional[str] = None) -> Optional[str]:
        """Convert speech to text

        Args:
            audio_path: Optional path to audio file

        Returns:
            str: Transcribed text or None if failed
        """
        try:
            if audio_path:
                with sr.AudioFile(audio_path) as source:
                    audio = self.recognizer.record(source)
            else:
                with sr.Microphone() as source:
                    logger.info("Listening...")
                    audio = self.recognizer.listen(source)

            text = self.recognizer.recognize_google(audio)
            return text
        except Exception as e:
            logger.error(f"Speech-to-text failed: {e}")
            return None

    async def process_voice(self, input_data: Union[str, bytes], mode: VoiceMode = VoiceMode.BOTH) -> dict[str, Any]:
        """Process voice data

        Args:
            input_data: Text or audio data
            mode: Processing mode

        Returns:
            Dict containing results
        """
        results = {}

        try:
            if mode in (VoiceMode.TEXT_TO_SPEECH, VoiceMode.BOTH) and isinstance(input_data, str):
                success = await self.text_to_speech(input_data)
                results["tts_success"] = success

            if mode in (VoiceMode.SPEECH_TO_TEXT, VoiceMode.BOTH) and isinstance(input_data, bytes):
                with open("temp_audio.wav", "wb") as f:
                    f.write(input_data)
                text = await self.speech_to_text("temp_audio.wav")
                results["transcribed_text"] = text
                os.remove("temp_audio.wav")

            return results
        except Exception as e:
            logger.error(f"Voice processing failed: {e}")
            return {"error": str(e)}

    def cleanup(self):
        """Clean up resources"""
        self.engine.stop()
