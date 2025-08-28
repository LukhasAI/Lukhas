"""
LUKHAS Actor System
===================
Actor model implementation for concurrent message passing and state management.
Integrates with the Event Bus for system-wide coordination.
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from .event_bus import EventTypes, emit_event

logger = logging.getLogger(__name__)


class ActorState(Enum):
    """Actor lifecycle states"""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class Message:
    """Actor message structure"""
    message_id: str
    sender: str
    recipient: str
    message_type: str
    payload: dict[str, Any]
    timestamp: float
    reply_to: Optional[str] = None
    correlation_id: Optional[str] = None

    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()


class Actor(ABC):
    """Base Actor class for message-driven processing"""

    def __init__(self, actor_id: str, actor_type: str = "generic"):
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.state = ActorState.CREATED
        self.logger = logging.getLogger(f"actor.{actor_type}.{actor_id}")

        # Message handling
        self._message_queue = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None

        # Actor management
        self._parent: Optional[Actor] = None
        self._children: set[Actor] = set()
        self._supervisor: Optional[ActorSupervisor] = None

        # Performance metrics
        self._metrics = {
            "messages_received": 0,
            "messages_sent": 0,
            "messages_processed": 0,
            "errors": 0,
            "uptime": 0.0
        }
        self._start_time = None

        self.logger.debug(f"Actor created: {self.actor_id}")

    @abstractmethod
    async def handle_message(self, message: Message) -> None:
        """Handle incoming messages. Override in subclasses."""
        pass

    async def on_start(self) -> None:
        """Called when actor starts. Override for initialization."""
        pass

    async def on_stop(self) -> None:
        """Called when actor stops. Override for cleanup."""
        pass

    async def on_error(self, error: Exception) -> None:
        """Called when actor encounters error. Override for error handling."""
        self.logger.error(f"Actor error: {error}")
        self._metrics["errors"] += 1

        # Notify supervisor if available
        if self._supervisor:
            await self._supervisor.handle_actor_error(self, error)

    async def start(self) -> None:
        """Start the actor"""
        if self._running:
            self.logger.warning("Actor already running")
            return

        try:
            self.state = ActorState.STARTING
            self._running = True
            self._start_time = time.time()

            # Start message processing loop
            self._task = asyncio.create_task(self._message_loop())

            # Call initialization hook
            await self.on_start()

            self.state = ActorState.RUNNING
            self.logger.info(f"Actor started: {self.actor_id}")

            # Emit system event
            emit_event(
                EventTypes.MODULE_INITIALIZED,
                f"actor.{self.actor_type}",
                {"actor_id": self.actor_id, "actor_type": self.actor_type}
            )

        except Exception as e:
            self.state = ActorState.ERROR
            await self.on_error(e)
            raise

    async def stop(self) -> None:
        """Stop the actor"""
        if not self._running:
            return

        try:
            self.state = ActorState.STOPPING
            self._running = False

            # Call cleanup hook
            await self.on_stop()

            # Cancel message processing
            if self._task and not self._task.done():
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass

            # Stop all children
            if self._children:
                await asyncio.gather(
                    *[child.stop() for child in self._children],
                    return_exceptions=True
                )

            # Update metrics
            if self._start_time:
                self._metrics["uptime"] = time.time() - self._start_time

            self.state = ActorState.STOPPED
            self.logger.info(f"Actor stopped: {self.actor_id}")

            # Emit system event
            emit_event(
                EventTypes.MODULE_SHUTDOWN,
                f"actor.{self.actor_type}",
                {"actor_id": self.actor_id, "uptime": self._metrics["uptime"]}
            )

        except Exception as e:
            self.state = ActorState.ERROR
            await self.on_error(e)

    async def send_message(
        self,
        recipient: str,
        message_type: str,
        payload: dict[str, Any],
        reply_to: Optional[str] = None
    ) -> str:
        """Send a message to another actor"""
        message = Message(
            message_id=str(uuid.uuid4()),
            sender=self.actor_id,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            reply_to=reply_to,
            timestamp=time.time()
        )

        # Route through actor system
        if hasattr(self, "_system"):
            await self._system.route_message(message)
        else:
            self.logger.warning(f"No actor system available to route message to {recipient}")

        self._metrics["messages_sent"] += 1
        return message.message_id

    async def _deliver_message(self, message: Message) -> None:
        """Internal method to deliver message to this actor"""
        await self._message_queue.put(message)
        self._metrics["messages_received"] += 1

    async def _message_loop(self) -> None:
        """Main message processing loop"""
        self.logger.debug(f"Message loop started for {self.actor_id}")

        while self._running:
            try:
                # Wait for messages with timeout to check running flag
                message = await asyncio.wait_for(
                    self._message_queue.get(),
                    timeout=1.0
                )

                # Process message
                await self.handle_message(message)
                self._metrics["messages_processed"] += 1

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.on_error(e)

        self.logger.debug(f"Message loop ended for {self.actor_id}")

    def add_child(self, child: "Actor") -> None:
        """Add a child actor"""
        child._parent = self
        self._children.add(child)

    def remove_child(self, child: "Actor") -> None:
        """Remove a child actor"""
        child._parent = None
        self._children.discard(child)

    def get_metrics(self) -> dict[str, Any]:
        """Get actor performance metrics"""
        metrics = self._metrics.copy()
        if self._start_time and self.state == ActorState.RUNNING:
            metrics["current_uptime"] = time.time() - self._start_time
        return metrics


class ActorSupervisor:
    """Supervisor for managing actor lifecycle and failures"""

    def __init__(self, supervisor_id: str):
        self.supervisor_id = supervisor_id
        self.actors: dict[str, Actor] = {}
        self.logger = logging.getLogger(f"supervisor.{supervisor_id}")

        # Supervision policies
        self.restart_policies = {
            "always": self._restart_always,
            "on_failure": self._restart_on_failure,
            "never": self._restart_never
        }

    async def supervise(self, actor: Actor, policy: str = "on_failure") -> None:
        """Add actor under supervision"""
        actor._supervisor = self
        self.actors[actor.actor_id] = actor

        # Store policy for this actor
        if not hasattr(self, "_policies"):
            self._policies = {}
        self._policies[actor.actor_id] = policy

        self.logger.info(f"Now supervising actor {actor.actor_id} with policy {policy}")

    async def handle_actor_error(self, actor: Actor, error: Exception) -> None:
        """Handle actor errors based on supervision policy"""
        policy = getattr(self, "_policies", {}).get(actor.actor_id, "on_failure")

        self.logger.error(f"Actor {actor.actor_id} error: {error}, applying policy: {policy}")

        handler = self.restart_policies.get(policy, self._restart_on_failure)
        await handler(actor, error)

    async def _restart_always(self, actor: Actor, error: Exception) -> None:
        """Always restart actor on error"""
        await self._restart_actor(actor)

    async def _restart_on_failure(self, actor: Actor, error: Exception) -> None:
        """Restart actor only on failure (not user stops)"""
        if actor.state == ActorState.ERROR:
            await self._restart_actor(actor)

    async def _restart_never(self, actor: Actor, error: Exception) -> None:
        """Never restart actor"""
        self.logger.info(f"Actor {actor.actor_id} failed, not restarting due to policy")

    async def _restart_actor(self, actor: Actor) -> None:
        """Restart a failed actor"""
        try:
            self.logger.info(f"Restarting actor {actor.actor_id}")

            # Stop if running
            if actor._running:
                await actor.stop()

            # Small delay before restart
            await asyncio.sleep(0.1)

            # Start again
            await actor.start()

            self.logger.info(f"Actor {actor.actor_id} successfully restarted")

        except Exception as e:
            self.logger.error(f"Failed to restart actor {actor.actor_id}: {e}")

    async def stop_all(self) -> None:
        """Stop all supervised actors"""
        if self.actors:
            await asyncio.gather(
                *[actor.stop() for actor in self.actors.values()],
                return_exceptions=True
            )
        self.actors.clear()


class ActorSystem:
    """Actor system for managing actors and message routing"""

    def __init__(self, system_id: str = "lukhas_actor_system"):
        self.system_id = system_id
        self.actors: dict[str, Actor] = {}
        self.supervisors: dict[str, ActorSupervisor] = {}
        self.message_history: deque = deque(maxlen=1000)
        self.logger = logging.getLogger(f"actor_system.{system_id}")

        # System metrics
        self.metrics = {
            "actors_created": 0,
            "messages_routed": 0,
            "routing_errors": 0
        }

    def register_actor(self, actor: Actor) -> None:
        """Register an actor with the system"""
        actor._system = self
        self.actors[actor.actor_id] = actor
        self.metrics["actors_created"] += 1

        self.logger.info(f"Registered actor: {actor.actor_id} ({actor.actor_type})")

    def unregister_actor(self, actor_id: str) -> None:
        """Unregister an actor from the system"""
        if actor_id in self.actors:
            del self.actors[actor_id]
            self.logger.info(f"Unregistered actor: {actor_id}")

    async def route_message(self, message: Message) -> bool:
        """Route a message to its recipient"""
        try:
            recipient = self.actors.get(message.recipient)
            if not recipient:
                self.logger.error(f"No actor found for recipient: {message.recipient}")
                self.metrics["routing_errors"] += 1
                return False

            # Deliver message
            await recipient._deliver_message(message)

            # Track message
            self.message_history.append({
                "message_id": message.message_id,
                "sender": message.sender,
                "recipient": message.recipient,
                "type": message.message_type,
                "timestamp": message.timestamp
            })

            self.metrics["messages_routed"] += 1
            return True

        except Exception as e:
            self.logger.error(f"Message routing error: {e}")
            self.metrics["routing_errors"] += 1
            return False

    async def broadcast_message(
        self,
        sender: str,
        message_type: str,
        payload: dict[str, Any],
        actor_filter: Optional[callable] = None
    ) -> int:
        """Broadcast a message to all or filtered actors"""
        recipients = self.actors.values()

        if actor_filter:
            recipients = [a for a in recipients if actor_filter(a)]

        sent_count = 0
        for actor in recipients:
            if actor.actor_id != sender:  # Don't send to self
                message = Message(
                    message_id=str(uuid.uuid4()),
                    sender=sender,
                    recipient=actor.actor_id,
                    message_type=message_type,
                    payload=payload,
                    timestamp=time.time()
                )

                if await self.route_message(message):
                    sent_count += 1

        return sent_count

    def get_actor(self, actor_id: str) -> Optional[Actor]:
        """Get actor by ID"""
        return self.actors.get(actor_id)

    def get_actors_by_type(self, actor_type: str) -> list[Actor]:
        """Get all actors of a specific type"""
        return [a for a in self.actors.values() if a.actor_type == actor_type]

    def get_system_metrics(self) -> dict[str, Any]:
        """Get system-wide metrics"""
        running_actors = sum(1 for a in self.actors.values() if a.state == ActorState.RUNNING)

        return {
            **self.metrics,
            "total_actors": len(self.actors),
            "running_actors": running_actors,
            "message_history_size": len(self.message_history)
        }

    async def shutdown(self) -> None:
        """Shutdown the actor system"""
        self.logger.info("Shutting down actor system")

        # Stop all supervisors (which will stop their actors)
        if self.supervisors:
            await asyncio.gather(
                *[supervisor.stop_all() for supervisor in self.supervisors.values()],
                return_exceptions=True
            )

        # Stop any remaining actors
        if self.actors:
            await asyncio.gather(
                *[actor.stop() for actor in self.actors.values()],
                return_exceptions=True
            )

        self.actors.clear()
        self.supervisors.clear()
        self.logger.info("Actor system shutdown complete")


# Global actor system instance
actor_system = ActorSystem()


# Helper functions
def register_actor(actor: Actor) -> None:
    """Register actor with global system"""
    actor_system.register_actor(actor)


def get_actor(actor_id: str) -> Optional[Actor]:
    """Get actor from global system"""
    return actor_system.get_actor(actor_id)


async def send_message(
    sender: str,
    recipient: str,
    message_type: str,
    payload: dict[str, Any]
) -> bool:
    """Send message through global system"""
    message = Message(
        message_id=str(uuid.uuid4()),
        sender=sender,
        recipient=recipient,
        message_type=message_type,
        payload=payload,
        timestamp=time.time()
    )
    return await actor_system.route_message(message)


# Export key components
__all__ = [
    "Actor",
    "ActorSystem",
    "ActorSupervisor",
    "ActorState",
    "Message",
    "actor_system",
    "register_actor",
    "get_actor",
    "send_message"
]
