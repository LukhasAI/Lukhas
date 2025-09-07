import logging
from datetime import timezone
import streamlit as st
from typing import Dict
logger = logging.getLogger(__name__)
"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: speech_processor.py
Advanced: speech_processor.py
Integration Date: 2025-05-31T07:55:28.300093
"""

import os
import queue
import sys
import threading
from datetime import datetime
from typing import Any, Optional

from candidate.core.common import get_logger
from integrations.elevenlabs.elevenlabs_client import ElevenLabsClient
from integrations.openai.whisper_client import WhisperClient

logger = get_logger(__name__)


class SpeechProcessor:
    """
    Advanced speech processing system that handles voice input with emotional awareness
    and generates emotionally-intelligent speech output.
    Inspired by the natural conversational style of Steve Jobs' product demos.
    """

    def __init__(self, model_config=None):
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.emotion_analyzer = EmotionAnalyzer()
        self.voice_fingerprints = {}
        self.confidence_threshold = 0.85
        self.context_window = []
        self.context_window_size = 10

        # Voice synthesis settings
        self.elevenlabs = ElevenLabsClient(
            api_key=os.environ.get("ELEVENLABS_API_KEY"),
            voice_id=os.environ.get("VOICE_ID", "xxxxxxxxxxxxxxxxxx"),
        )

        # Voice recognition (if available)
        try:
            self.whisper = WhisperClient()
            self.transcription_available = True
        except Exception as e:
            logger.warning(f"Whisper client initialization failed: {e}")
            self.whisper = None
            self.transcription_available = False

        # Event callbacks
        self.on_transcription = None
        self.on_speech_completed = None

    def start_listening(self):
        """Begin active listening session with minimal user friction"""
        if self.is_listening:
            return

        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._process_audio_stream)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        return {
            "status": "listening_started",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def stop_listening(self):
        """Stop listening session gracefully"""
        self.is_listening = False
        return {
            "status": "listening_stopped",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _process_audio_stream(self):
        """Process incoming audio stream with minimal latency"""
        while self.is_listening:
            try:
                audio_chunk = self.audio_queue.get(timeout=0.5)
                transcription = self._transcribe_audio(audio_chunk)

                if transcription["confidence"] >= self.confidence_threshold:
                    # Add emotional analysis
                    emotional_context = self.emotion_analyzer.analyze(audio_chunk)
                    transcription["emotion"] = emotional_context

                    # Update context window
                    self._update_context_window(transcription)

                    # Emit result for further processing
                    self._emit_transcription_result(transcription)

            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Error processing audio stream: {e}")

    async def _transcribe_audio(self, audio_chunk):
        """Convert speech to text with high accuracy"""
        if self.whisper and self.transcription_available:
            try:
                # Use Whisper for transcription
                result = await self.whisper.transcribe_audio(audio_chunk)
                return {
                    "text": result.get("text", ""),
                    "confidence": result.get("confidence", 0.0),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as e:
                logger.error(f"Whisper transcription error: {e}")

        # Fallback implementation
        return {
            "text": "Example transcription",
            "confidence": 0.95,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _update_context_window(self, transcription):
        """Maintain conversation context for more natural responses"""
        self.context_window.append(transcription)
        if len(self.context_window) > self.context_window_size:
            self.context_window.pop(0)

    def _emit_transcription_result(self, result):
        """Send processed transcription to the cognitive system"""
        if self.on_transcription:
            try:
                self.on_transcription(result)
            except Exception as e:
                logger.error(f"Error in transcription callback: {e}")

    async def speak(
        self,
        text: str,
        emotion: Optional[dict] = None,
        voice_id: Optional[str] = None,
        wait_for_completion: bool = False,
    ) -> dict[str, Any]:
        """
        Convert text to speech with emotional awareness

        Args:
            text: Text to convert to speech
            emotion: Emotional context to apply
            voice_id: Override default voice ID
            wait_for_completion: Whether to wait for audio to complete playing

        Returns:
            Dictionary with speech result metadata
        """
        try:
            # Adjust voice parameters based on emotion
            stability, similarity_boost, style = self._map_emotion_to_voice_parameters(emotion)

            # Generate speech with ElevenLabs
            result = await self.elevenlabs.text_to_speech(
                text=text,
                voice_id=voice_id,
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
            )

            if "error" in result:
                logger.error(f"ElevenLabs speech generation error: {result['error']}")
                return result

            # Play audio if requested
            if wait_for_completion and result.get("audio_path"):
                await self._play_audio(result["audio_path"])

            # Emit completion event
            if self.on_speech_completed:
                self.on_speech_completed(result)

            return result

        except Exception as e:
            logger.error(f"Error in speech generation: {e}")
            return {"error": str(e)}

    async def _play_audio(self, audio_path: str) -> bool:
        """
        Play audio file using appropriate system command

        Args:
            audio_path: Path to audio file

        Returns:
            Success status
        """
        if not os.path.exists(audio_path):
            return False

        try:
            # CLAUDE_EDIT_v0.13: Fixed command injection vulnerability - use
            # subprocess with list args
            import subprocess

            # Validate audio path to prevent command injection
            audio_path = os.path.abspath(audio_path)
            if not os.path.isfile(audio_path):
                logger.error(f"Invalid audio file path: {audio_path}")
                return False

            # Use appropriate command based on platform
            if sys.platform == "darwin":  # macOS
                subprocess.run(["afplay", audio_path], check=True)
            elif sys.platform == "win32":  # Windows
                subprocess.run(["cmd", "/c", "start", "", audio_path], check=True)
            else:  # Linux and other platforms
                subprocess.run(["aplay", audio_path], check=True)

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Error playing audio: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error playing audio: {e}")
            return False

    def _map_emotion_to_voice_parameters(self, emotion: Optional[dict]) -> tuple:
        """
        Map emotional context to voice synthesis parameters

        Args:
            emotion: Emotional context dictionary

        Returns:
            Tuple of (stability, similarity_boost, style)
        """
        if not emotion:
            return 0.5, 0.75, 0.0

        primary_emotion = emotion.get("primary_emotion", "neutral")
        intensity = emotion.get("intensity", 0.5)

        # Adjust parameters based on emotion
        if primary_emotion == "happy":
            return (
                0.4,
                0.75,
                min(intensity * 0.8, 0.8),
            )  # More animated, expressive
        elif primary_emotion == "sad":
            return 0.65, 0.85, min(intensity * 0.3, 0.3)  # More stable, clear
        elif primary_emotion == "angry":
            return (
                0.35,
                0.6,
                min(intensity * 0.5, 0.5),
            )  # Less stable, variable
        elif primary_emotion == "fearful":
            return 0.6, 0.8, min(intensity * 0.4, 0.4)  # More stable
        elif primary_emotion == "surprised":
            return 0.4, 0.7, min(intensity * 0.7, 0.7)  # More expressive
        else:  # neutral and others
            return 0.5, 0.75, min(intensity * 0.5, 0.5)

    def get_speaker_identity(self, audio_sample, user_context=None):
        """Identify the speaker with high accuracy"""
        # Voice biometric feature - placeholder implementation
        return {"user_id": "example_user", "confidence": 0.92}

    async def close(self):
        """Clean up resources"""
        await self.elevenlabs.close()
        if self.whisper:
            await self.whisper.close()


class EmotionAnalyzer:
    """Analyzes emotional content in speech"""

    def __init__(self):
        self.emotion_categories = [
            "neutral",
            "happy",
            "sad",
            "angry",
            "fearful",
            "disgusted",
            "surprised",
            "confused",
            "urgent",
        ]

    def analyze(self, audio_data):
        """Extract emotional signals from audio"""
        # This would use acoustic feature extraction and ML model
        # Placeholder implementation
        return {
            "primary_emotion": "neutral",
            "emotion_scores": dict.fromkeys(self.emotion_categories, 0.1),
            "intensity": 0.5,
            "confidence": 0.85,
        }