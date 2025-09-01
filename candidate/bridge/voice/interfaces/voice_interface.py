"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: voice_interface.py
Advanced: voice_interface.py
Integration Date: 2025-05-31T07:55:28.355963
"""

import logging
import subprocess
from datetime import datetime
from typing import Any, Callable, Optional

from voice.message_handler import VoiceMessage, VoiceMessageHandler
from voice.voice_integration import VoiceIntegrationLayer
from voice.voice_system_integrator import VoiceSystemIntegrator

"""
Voice Interface for Lukhas System
------------------------------
Provides a unified interface for all voice-related functionality across the system.
Handles text-to-speech synthesis with support for multiple providers (system,
    ElevenLabs, etc.)
"""


logger = logging.getLogger("voice_interface")


class VoiceInterface:
    """
    Unified interface for all voice-related functionality.
    Supports multiple voice providers and handles fallbacks.
    """

    def __init__(self):
        """Initialize voice interface components"""
        self.voice_integration = VoiceIntegrationLayer()
        self.voice_system = VoiceSystemIntegrator()

        # Initialize message handler
        self.message_handler = VoiceMessageHandler()
        self.message_handler.register_output_handler(self._handle_output_message)
        self.message_handler.start()

        # Track active conversations
        self.active_conversations = {}

    async def speak(
        self,
        text: str,
        provider: str = "auto",
        emotion: Optional[str] = None,
        voice_id: Optional[str] = None,
        priority: int = 5,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Speak text using the most appropriate available provider.

        Args:
            text: Text to speak
            provider: Preferred provider ("system", "elevenlabs", "auto")
            emotion: Emotional context for voice modulation
            voice_id: Specific voice ID if using ElevenLabs
            priority: Message priority (1-10, lower is higher priority)
            conversation_id: Optional ID to group related messages

        Returns:
            Dict with status and details of speech synthesis
        """
        # Prepare metadata
        metadata = {
            "provider": provider,
            "emotion": emotion,
            "voice_id": voice_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
        }

        # Add to output queue
        self.message_handler.enqueue_output(text, priority, metadata)
        return {"success": True, "queued": True}

    async def _handle_output_message(self, message: VoiceMessage):
        """Handle a queued output message"""
        try:
            metadata = message.metadata or {}
            provider = metadata.get("provider", "auto")

            # Try the preferred provider first
            if provider == "system" or (provider == "auto" and self._should_use_system_voice(message.content)):
                return await self._speak_system(message.content)

            # Try ElevenLabs
            try:
                result = await self.voice_system.speak(
                    text=message.content,
                    emotion=metadata.get("emotion"),
                    voice_id=metadata.get("voice_id"),
                )
                if result.get("success"):
                    return result
            except Exception as e:
                logger.warning(f"ElevenLabs synthesis failed: {e}")

            # Fallback to system voice if everything else failed
            if provider == "auto":
                return await self._speak_system(message.content)

            return {
                "success": False,
                "error": "All voice synthesis methods failed",
            }

        except Exception as e:
            logger.error(f"Voice synthesis error: {e}")
            return {"success": False, "error": str(e)}

    async def _speak_system(self, text: str) -> dict[str, Any]:
        """Use system text-to-speech as a fallback"""
        try:
            subprocess.run(["say", text])
            return {"success": True, "provider": "system"}
        except Exception as e:
            logger.error(f"System voice failed: {e}")
            return {"success": False, "error": str(e)}

    def _should_use_system_voice(self, text: str) -> bool:
        """Determine if system voice should be used based on text content"""
        # Use system voice for short, simple notifications
        return len(text) < 50 and not any(char in text for char in "!?😊😢😡")

    def register_input_handler(self, handler: Callable[[VoiceMessage], None]):
        """Register a handler for voice input messages"""
        self.message_handler.register_input_handler(handler)

    def add_to_conversation(self, text: str, conversation_id: str, is_input: bool = True):
        """Add a message to a conversation thread"""
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = []

        self.active_conversations[conversation_id].append(
            {
                "text": text,
                "type": "input" if is_input else "output",
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_conversation_history(self, conversation_id: str) -> list[dict[str, Any]]:
        """Get the history of a conversation thread"""
        return self.active_conversations.get(conversation_id, [])
