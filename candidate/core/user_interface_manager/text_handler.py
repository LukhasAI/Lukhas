import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TextHandler:
    """
    Handles text-based interactions with users.
    Jobs-inspired focus on clear, intuitive communication.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        logger.info("TextHandler initialized")

    def send_message(self, user_id: str, message: str) -> bool:
        """Sends a text message to the user"""
        try:
            # Keep as print since this is text message simulation for user
            print(f"[TEXT to {user_id}] {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}: {e}")
            return False

    def get_message(self, timeout_seconds: int = 30) -> Optional[str]:
        """Gets a text message from the user"""
        try:
            # Keep as input since this is text message interface for user
            user_input = input("[TEXT] Enter your message: ")
            return user_input if user_input.strip() else None
        except Exception as e:
            logger.error(f"Failed to get message: {e}")
            return None