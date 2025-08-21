"""
User Interface Manager for Health Advisor Plugin

This module manages all user interactions, ensuring safe, accessible, and HIPAA-compliant
communication through various channels (text, voice, media).

Features:
- Multi-modal input handling (text, voice, images)
- Input validation and sanitization
- Emergency situation detection
- Clear communication of medical disclaimers
- Accessibility support
"""

import logging
from typing import Dict, Any, Tuple, Optional, List
from enum import Enum

from .text_handler import TextHandler
from .voice_handler import VoiceHandler
from .media_capture import MediaCaptureHandler

logger = logging.getLogger(__name__)

class InputType(Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"

class UserInterfaceManager:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the UI manager with configuration"""
        self.config = config or {}
        self.text_handler = TextHandler(config)
        self.voice_handler = VoiceHandler(config)
        self.media_handler = MediaCaptureHandler(config)
        
        # Load safety prompts and disclaimers
        self._load_safety_prompts()
        logger.info("UserInterfaceManager initialized with all handlers")

    def _load_safety_prompts(self):
        """Load medical disclaimers and safety warnings"""
        self.safety_prompts = {
            "initial_disclaimer": (
                "I am an AI health advisor and do not replace professional medical care. "
                "If you are experiencing a medical emergency, please call emergency services immediately."
            ),
            "emergency_warning": (
                "Based on your symptoms, you should seek immediate medical attention. "
                "Please call emergency services or go to the nearest emergency room."
            ),
            "data_privacy": (
                "Your health information is protected under HIPAA. "
                "We maintain strict privacy and security standards."
            )
        }

    async def get_user_input(
        self,
        user_id: str,
        prompt: str,
        expected_input_type: Optional[List[InputType]] = None,
        require_confirmation: bool = False
    ) -> Tuple[Any, InputType]:
        """
        Get input from the user through their preferred or specified channel.
        
        Args:
            user_id: Unique identifier for the user
            prompt: The prompt or question to present to the user
            expected_input_type: List of acceptable input types
            require_confirmation: Whether to require user confirmation of input
            
        Returns:
            Tuple of (input_data, input_type)
        """
        # Default to all input types if none specified
        expected_input_type = expected_input_type or list(InputType)
        
        try:
            # Determine best input method based on context and user preferences
            chosen_input_type = self._determine_input_method(user_id, expected_input_type)
            
            # Get input using appropriate handler
            if chosen_input_type == InputType.VOICE:
                input_data = await self.voice_handler.get_input(prompt)
            elif chosen_input_type in (InputType.IMAGE, InputType.VIDEO):
                input_data = await self.media_handler.capture_media(
                    prompt,
                    media_type=chosen_input_type.value
                )
            else:  # Default to text
                input_data = await self.text_handler.get_input(prompt)
            
            # Validate and sanitize input
            sanitized_input = self._sanitize_input(input_data, chosen_input_type)
            
            # Get confirmation if required
            if require_confirmation:
                confirmed = await self._get_confirmation(sanitized_input, chosen_input_type)
                if not confirmed:
                    return await self.get_user_input(
                        user_id, prompt, expected_input_type, require_confirmation
                    )
            
            return sanitized_input, chosen_input_type
            
        except Exception as e:
            logger.error(f"Error getting user input: {str(e)}")
            # Fallback to text input if other methods fail
            return await self.text_handler.get_input(prompt), InputType.TEXT

    def _determine_input_method(
        self,
        user_id: str,
        allowed_types: List[InputType]
    ) -> InputType:
        """Determine the most appropriate input method based on context and preferences"""
        # TODO: Implement logic to choose input method based on:
        # - User preferences from profile
        # - Current context (e.g., noise level, privacy setting)
        # - Device capabilities
        # For now, default to text if available, otherwise first allowed type
        if InputType.TEXT in allowed_types:
            return InputType.TEXT
        return allowed_types[0]

    def _sanitize_input(self, input_data: Any, input_type: InputType) -> Any:
        """Sanitize and validate user input"""
        # Basic sanitization - extend based on input type
        if input_type == InputType.TEXT:
            return input_data.strip()
        return input_data

    async def _get_confirmation(self, input_data: Any, input_type: InputType) -> bool:
        """Get user confirmation of their input"""
        confirmation_prompt = f"Please confirm your input: {input_data}"
        confirmation, _ = await self.get_user_input(
            "system",  # System-generated confirmation request
            confirmation_prompt,
            [InputType.TEXT],
            require_confirmation=False  # Prevent infinite recursion
        )
        return confirmation.lower() in ('y', 'yes', 'confirm', 'correct')

    def get_initial_diagnostic_prompt(self) -> str:
        """Get the initial prompt for starting a diagnostic session"""
        return (
            f"{self.safety_prompts['initial_disclaimer']}\n\n"
            "Please describe your symptoms or health concerns. "
            "Be as specific as possible about what you're experiencing, "
            "when it started, and any relevant medical history."
        )

    def get_emergency_prompt(self) -> str:
        """Get the emergency warning prompt"""
        return self.safety_prompts['emergency_warning']
