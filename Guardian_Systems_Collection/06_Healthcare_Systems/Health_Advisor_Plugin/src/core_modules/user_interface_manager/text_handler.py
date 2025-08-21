"""
Text Handler for Health Advisor Plugin

Handles all text-based interactions, including input validation,
sanitization, and safety checks.
"""

import logging
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class TextHandler:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the text handler with configuration"""
        self.config = config or {}
        self.emergency_keywords = {
            'chest pain', 'heart attack', 'stroke', 'cannot breathe',
            'difficulty breathing', 'severe bleeding', 'unconscious'
        }
        logger.info("TextHandler initialized")

    async def get_input(self, prompt: str) -> str:
        """
        Get text input from the user with safety checks

        Args:
            prompt: The prompt to display to the user

        Returns:
            Sanitized user input text
        """
        # In a real implementation, this would interface with the UI system
        # For now, we'll simulate the input
        try:
            # Display prompt and get input (implementation depends on UI framework)
            user_input = await self._get_raw_input(prompt)
            
            # Check for emergency keywords
            if self._contains_emergency_keywords(user_input):
                logger.warning("Emergency keywords detected in user input")
                # This would trigger emergency protocol in the main system
                return user_input

            # Sanitize and validate input
            sanitized_input = self._sanitize_input(user_input)
            if not self._validate_input(sanitized_input):
                raise ValueError("Invalid input format")

            return sanitized_input

        except Exception as e:
            logger.error(f"Error in text input: {str(e)}")
            raise

    async def _get_raw_input(self, prompt: str) -> str:
        """
        Get raw input from the user. This method would be implemented
        based on the actual UI framework being used.
        """
        # Placeholder - in real implementation, this would interface with UI
        return "Sample user input"

    def _sanitize_input(self, text: str) -> str:
        """
        Sanitize user input by removing potentially harmful content
        while preserving medically relevant information
        """
        # Remove any obviously dangerous content
        text = text.strip()
        # Remove potential script injection
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
        # Remove other potentially dangerous HTML
        text = re.sub(r'<[^>]*>', '', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text

    def _validate_input(self, text: str) -> bool:
        """
        Validate that the input meets basic requirements
        """
        if not text:
            return False
        if len(text) < 2:  # Require at least 2 characters
            return False
        # Add more validation as needed
        return True

    def _contains_emergency_keywords(self, text: str) -> bool:
        """
        Check if the input contains any emergency keywords that should
        trigger immediate medical attention
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.emergency_keywords)
