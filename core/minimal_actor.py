"""
Minimal Actor Model Implementation

Provides basic actor pattern for message-based concurrency
in the swarm architecture.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class Actor:
    """
    Base actor class for message-based processing

    Actors communicate exclusively through messages,
    providing isolation and concurrent processing.
    """

    def __init__(self, actor_id: str):
        """
        Initialize actor

        Args:
            actor_id: Unique identifier for this actor
        """
        self.actor_id = actor_id
        self.mailbox: list[Any] = []
        self.is_active = True

    def receive(self, message: Any) -> Any:
        """
        Receive and process a message

        Args:
            message: Message to process

        Returns:
            Result of message processing

        Note:
            Subclasses should override this method to implement
            specific message handling logic.
        """
        logger.debug(f"Actor {self.actor_id} received message: {message}")
        return self._handle_message(message)

    def _handle_message(self, message: Any) -> Any:
        """
        Handle message processing logic

        Args:
            message: Message to handle

        Returns:
            Processing result

        Note:
            Override this method in subclasses for custom behavior
        """
        return {"status": "received", "actor_id": self.actor_id}

    def send(self, target_actor: "Actor", message: Any) -> None:
        """
        Send message to another actor

        Args:
            target_actor: Destination actor
            message: Message to send
        """
        if target_actor.is_active:
            target_actor.receive(message)
        else:
            logger.warning(f"Cannot send message to inactive actor {target_actor.actor_id}")

    def stop(self) -> None:
        """Stop this actor"""
        self.is_active = False
        logger.info(f"Actor {self.actor_id} stopped")


__all__ = ["Actor"]
