"""
Actor System Module - Production Version
Provides ActorRef, ActorSystem, and Actor base classes for LUKHAS AI
Trinity Framework: ⚛️🧠🛡️

This is the production-ready actor system that supports the colony architecture.
"""

import logging
from typing import Any
from typing import Optional

logger = logging.getLogger(__name__)


class ActorRef:
    """Reference to an actor (enables location transparency)"""

    def __init__(self, actor_id: str, actor_system: Optional["ActorSystem"] = None):
        self.actor_id = actor_id
        self.actor_system = actor_system

    def send(self, message: Any) -> None:
        """Send a message to this actor"""
        if self.actor_system:
            self.actor_system.send(self.actor_id, message)

    def __repr__(self) -> str:
        return f"ActorRef({self.actor_id})"


class ActorSystem:
    """Basic actor system for managing actors"""

    def __init__(self):
        self.actors: dict[str, Actor] = {}
        logger.info("ActorSystem initialized")

    def send(self, actor_id: str, message: Any) -> None:
        """Send a message to an actor"""
        if actor_id in self.actors:
            self.actors[actor_id].receive(message)
        else:
            logger.warning(f"Actor {actor_id} not found in system")

    def register(self, actor_id: str, actor: "Actor") -> ActorRef:
        """Register an actor and return its reference"""
        self.actors[actor_id] = actor
        logger.debug(f"Registered actor: {actor_id}")
        return ActorRef(actor_id, self)

    def unregister(self, actor_id: str) -> None:
        """Unregister an actor from the system"""
        if actor_id in self.actors:
            del self.actors[actor_id]
            logger.debug(f"Unregistered actor: {actor_id}")


# Create a default actor system instance
default_actor_system = ActorSystem()


def get_global_actor_system() -> ActorSystem:
    """Get the global actor system instance"""
    return default_actor_system


class Actor:
    """Base actor class for all actors in the system"""

    def __init__(self, actor_id: str):
        self.actor_id = actor_id
        self.handlers: dict[str, Any] = {}

    def register_handler(self, message_type: str, handler: Any) -> None:
        """Register a message handler for a specific message type"""
        self.handlers[message_type] = handler

    def receive(self, message: Any) -> None:
        """
        Receive and process a message.
        Override this method in subclasses for custom message handling.
        """
        message_type = type(message).__name__
        if message_type in self.handlers:
            self.handlers[message_type](message)
        else:
            self.handle_unknown_message(message)

    def handle_unknown_message(self, message: Any) -> None:
        """Handle unknown message types. Override for custom behavior."""
        logger.debug(
            f"Actor {self.actor_id} received unknown message type: {type(message).__name__}"
        )


class AIAgentActor(Actor):
    """
    AI Agent implemented as an actor.
    Lightweight, stateful AI agent that can handle tasks.
    """

    def __init__(self, actor_id: str, capabilities: Optional[list[str]] = None):
        super().__init__(actor_id)
        self.capabilities = capabilities or []
        self.current_tasks: dict[str, dict] = {}
        self.memory: dict[str, Any] = {}
        self.energy_level = 100.0  # Energy efficiency tracking
        self.state = "idle"  # idle, working, error

    def add_capability(self, capability: str) -> None:
        """Add a new capability to the agent"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)

    def assign_task(self, task_id: str, task_data: dict) -> None:
        """Assign a new task to the agent"""
        self.current_tasks[task_id] = task_data
        self.state = "working"

    def complete_task(self, task_id: str, result: Any) -> Any:
        """Mark a task as complete and return the result"""
        if task_id in self.current_tasks:
            del self.current_tasks[task_id]
            if not self.current_tasks:
                self.state = "idle"
            return result
        return None

    def receive(self, message: Any) -> None:
        """Process incoming messages"""
        # Handle task-related messages
        if hasattr(message, "__dict__"):
            if hasattr(message, "task_id"):
                self.assign_task(message.task_id, vars(message))
        else:
            super().receive(message)


# Export all public classes and functions
__all__ = [
    "ActorRef",
    "ActorSystem",
    "Actor",
    "AIAgentActor",
    "get_global_actor_system",
    "default_actor_system",
]
