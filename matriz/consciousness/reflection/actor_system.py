from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - ACTOR SYSTEM FRAMEWORK
║ Lightweight distributed actor framework for AI agents
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: actor_system.py
║ Path: lukhas/core/actor_system.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: LUKHAS AI Core Team | GitHub Copilot
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Actor system framework implementing high-performance distributed AI agents with
║ 126-130 with AsyncIO-based concurrent processing and location transparency.
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from abc import ABC
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Callable, Optional, Union

from core.common import get_logger

try:  # Optional dependency for distributed comms; keep import-safe during tests
    from .p2p_communication import P2PNode  # type: ignore
except Exception:  # pragma: no cover
    class P2PNode:  # minimal stub for import-time safety
        pass

# Import mailbox components if available
try:
    from .mailbox import BackPressureStrategy, Mailbox, MailboxFactory, MailboxType

    ENHANCED_MAILBOX_AVAILABLE = True
except ImportError:
    ENHANCED_MAILBOX_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)


class ActorState(Enum):
    """Actor lifecycle states"""

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class SupervisionStrategy(Enum):
    """Supervision strategies for handling child actor failures"""

    RESTART = "restart"
    STOP = "stop"
    ESCALATE = "escalate"


@dataclass
class ActorMessage:
    """Message sent between actors"""

    message_id: str
    sender: str
    recipient: str
    message_type: str
    payload: dict[str, Any]
    timestamp: float
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ActorRef:
    """Reference to an actor (enables location transparency)"""

    def __init__(self, actor_id: str, actor_system: "ActorSystem"):
        self.actor_id = actor_id
        self.actor_system = actor_system

    async def tell(
        self,
        message_type: str,
        payload: dict[str, Any],
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        sender: Optional[str] = "unknown",
    ) -> bool:
        """Send a fire-and-forget message to the actor"""
        message = ActorMessage(
            message_id=str(uuid.uuid4()),
            sender=sender,  # Will be set by actor system
            recipient=self.actor_id,
            message_type=message_type,
            payload=payload,
            timestamp=time.time(),
            correlation_id=correlation_id,
            reply_to=reply_to,
        )

        return await self.actor_system.deliver_message(message)

    async def ask(
        self,
        message_type: str,
        payload: dict[str, Any],
        timeout: float = 5.0,
        correlation_id: Optional[str] = None,
    ) -> Any:
        """Send a message and wait for a response"""
        response_id = str(uuid.uuid4())
        response_future = asyncio.Future()

        # Register response handler
        self.actor_system.register_response_handler(response_id, response_future)

        try:
            # Send message with reply_to
            await self.tell(message_type, payload, correlation_id, response_id, sender=self.actor_id)

            # Wait for response
            result = await asyncio.wait_for(response_future, timeout)
            if isinstance(result, dict) and "error" in result:
                raise RuntimeError(result["error"])
            if isinstance(result, Exception):
                raise result
            return result
        except asyncio.TimeoutError:
            self.actor_system.unregister_response_handler(response_id)
            raise
        finally:
            self.actor_system.unregister_response_handler(response_id)

    def __str__(self):
        return f"ActorRef({self.actor_id})"


class Actor(ABC):
    """
    Base class for all actors in the system.
    Implements lightweight, isolated computation units.

    In response to a message, an actor can perform three fundamental actions:
    1. Send a finite number of messages to other actors (using `self.actor_system.tell` or `self.actor_ref.ask`).
    2. Create a finite number of new actors (using `self.create_child`).
    3. Designate the behavior for the next message it receives (using `self.become`).
    """

    def __init__(self, actor_id: str, mailbox: Optional[Union[asyncio.Queue, "Mailbox"]] = None):
        self.actor_id = actor_id
        self.state = ActorState.CREATED

        # Use provided mailbox or create default
        if mailbox is not None:
            self.mailbox = mailbox
        elif ENHANCED_MAILBOX_AVAILABLE:
            # Use enhanced bounded mailbox by default if available
            self.mailbox = MailboxFactory.create_mailbox(
                MailboxType.BOUNDED,
                max_size=1000,
                back_pressure_strategy=BackPressureStrategy.BLOCK,
            )
        else:
            # Fallback to standard asyncio queue
            self.mailbox = asyncio.Queue(maxsize=1000)

        self.message_handlers: dict[str, Callable] = {}
        self.supervisor: Optional[ActorRef] = None
        self.children: dict[str, ActorRef] = {}
        self.actor_system: Optional[ActorSystem] = None
        self.supervision_strategy: SupervisionStrategy = SupervisionStrategy.RESTART
        self._running = False
        self._stats = {
            "messages_processed": 0,
            "messages_failed": 0,
            "last_activity": time.time(),
            "created_at": time.time(),
        }

    async def start(self, actor_system: "ActorSystem"):
        """Start the actor"""
        self.actor_system = actor_system
        self.state = ActorState.STARTING

        try:
            await self.pre_start()
            self.state = ActorState.RUNNING
            self._running = True

            # Start message processing loop
            asyncio.create_task(self._message_loop())

            logger.info(f"Actor {self.actor_id} started successfully")
        except Exception as e:
            self.state = ActorState.FAILED
            logger.error(f"Failed to start actor {self.actor_id}: {e}")
            raise

    async def stop(self):
        """Stop the actor gracefully"""
        self.state = ActorState.STOPPING
        self._running = False

        try:
            # Stop all children first
            for child_ref in list(self.children.values()):
                await child_ref.actor_system.stop_actor(child_ref.actor_id)

            await self.pre_stop()
            self.state = ActorState.STOPPED

            logger.info(f"Actor {self.actor_id} stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping actor {self.actor_id}: {e}")
            self.state = ActorState.FAILED

    async def _message_loop(self):
        """Main message processing loop - guarantees sequential processing"""
        while self._running:
            try:
                # Get message from mailbox
                if ENHANCED_MAILBOX_AVAILABLE and hasattr(self.mailbox, "get"):
                    # Enhanced mailbox with built-in timeout handling
                    message = await asyncio.wait_for(self.mailbox.get(), timeout=1.0)
                else:
                    # Standard asyncio queue
                    message = await asyncio.wait_for(self.mailbox.get(), timeout=1.0)

                # Process message sequentially - this is the key guarantee
                # Only one message is processed at a time, ensuring no race conditions
                await self._process_message(message)
                self._stats["messages_processed"] += 1
                self._stats["last_activity"] = time.time()

            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except Exception as e:
                self._stats["messages_failed"] += 1
                logger.error(f"Actor {self.actor_id} message processing error: {e}")
                self.state = ActorState.FAILED

                # Notify supervisor of failure
                if self.supervisor:
                    await self.supervisor.tell(
                        "child_failed",
                        {"child_id": self.actor_id, "error": e},
                    )

    async def _process_message(self, message: ActorMessage):
        """Process a single message"""
        try:
            # Check if we have a handler for this message type
            if message.message_type in self.message_handlers:
                handler = self.message_handlers[message.message_type]
                response = await handler(message)

                # Send response if requested
                if message.reply_to and response is not None:
                    await self._send_response(message.reply_to, response)
            else:
                await self.unhandled_message(message)

        except Exception as e:
            logger.error(f"Handler error in {self.actor_id}: {e}")
            # Send error response if expected
            if message.reply_to:
                await self._send_response(message.reply_to, e)
            raise

    async def _send_response(self, reply_to: str, response: Any):
        """Send a response back to the sender"""
        if self.actor_system:
            self.actor_system.handle_response(reply_to, response)

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler

    def become(self, new_handlers: dict[str, Callable]):
        """
        Change the actor's behavior by replacing its message handlers.
        This is one of the three fundamental actor actions.
        """
        self.message_handlers = new_handlers
        logger.info(f"Actor {self.actor_id} has changed its behavior.")

    async def send_message(self, message: ActorMessage) -> bool:
        """Add message to mailbox"""
        try:
            # Handle enhanced mailbox
            if ENHANCED_MAILBOX_AVAILABLE and hasattr(self.mailbox, "put"):
                return await self.mailbox.put(message)
            # Handle standard asyncio queue
            else:
                await self.mailbox.put(message)
                return True
        except asyncio.QueueFull:
            logger.warning(f"Mailbox full for actor {self.actor_id}")
            return False

    async def create_child(self, child_class: type, child_id: str, *args, **kwargs) -> ActorRef:
        """Create a child actor"""
        if not self.actor_system:
            raise RuntimeError("Actor not started")

        child_ref = await self.actor_system.create_actor(child_class, child_id, *args, **kwargs)

        # Set supervision
        child_actor = self.actor_system.get_actor(child_id)
        if child_actor:
            child_actor.supervisor = ActorRef(self.actor_id, self.actor_system)

        self.children[child_id] = child_ref
        return child_ref

    # Abstract methods to be implemented by subclasses
    async def pre_start(self):
        """Called before actor starts"""

    async def pre_stop(self):
        """Called before actor stops"""

    async def post_stop(self):
        """Called after actor stops"""

    async def pre_restart(self, reason: Exception):
        """Called before actor is restarted"""

    async def unhandled_message(self, message: ActorMessage):
        """Handle unknown message types"""
        logger.warning(f"Unhandled message {message.message_type} in {self.actor_id}")

    def supervision_strategy(self) -> SupervisionStrategy:
        """Define the supervision strategy for this actor's children."""
        return SupervisionStrategy.RESTART

    async def handle_child_failure(self, child_id: str, error: Exception):
        """Handle a child actor failure."""
        strategy = self.supervision_strategy()
        logger.info(f"Supervisor {self.actor_id} handling failure of child {child_id} with strategy {strategy.value}")
        if strategy == SupervisionStrategy.RESTART:
            await self.actor_system.restart_actor(child_id)
        elif strategy == SupervisionStrategy.STOP:
            await self.actor_system.stop_actor(child_id)
        elif strategy == SupervisionStrategy.ESCALATE and self.supervisor:
            await self.supervisor.tell("child_failed", {"child_id": self.actor_id, "error": str(error)})

    def get_stats(self) -> dict[str, Any]:
        """Get actor statistics"""
        stats = {
            **self._stats,
            "state": self.state.value,
            "children_count": len(self.children),
        }

        # Get mailbox size
        if ENHANCED_MAILBOX_AVAILABLE and hasattr(self.mailbox, "qsize"):
            stats["mailbox_size"] = self.mailbox.qsize()
            # Get detailed mailbox stats if available
            if hasattr(self.mailbox, "get_stats"):
                stats["mailbox_details"] = self.mailbox.get_stats()
        else:
            stats["mailbox_size"] = self.mailbox.qsize()

        return stats


class ActorSystem:
    """
    Actor system managing the lifecycle of all actors.
    Provides location transparency, fault tolerance, and supervision.
    This is the main entry point for creating and interacting with actors.
    """

    def __init__(self, system_name: str = "lukhas-actors"):
        self.system_name = system_name
        self.actors: dict[str, Actor] = {}
        self.actor_refs: dict[str, ActorRef] = {}
        self.response_handlers: dict[str, asyncio.Future] = {}
        self._lock = threading.Lock()
        self._running = False

        # P2P Management
        self.p2p_nodes: dict[str, P2PNode] = {}

        # Sharding support (simple hash-based)
        self.shard_count = 16
        self.local_shards = set(range(self.shard_count))  # All shards local for now

    async def start(self):
        """Start the actor system"""
        self._running = True
        logger.info(f"Actor system '{self.system_name}' started")

    async def stop(self):
        """Stop the actor system and all actors"""
        self._running = False

        # Stop all actors
        stop_tasks = []
        for actor in list(self.actors.values()):
            stop_tasks.append(actor.stop())

        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)

        self.actors.clear()
        self.actor_refs.clear()

        logger.info(f"Actor system '{self.system_name}' stopped")

    async def create_actor(self, actor_class: type, actor_id: str, *args, **kwargs) -> ActorRef:
        """Create and start a new actor"""
        if not self._running:
            raise RuntimeError("Actor system not running")

        if actor_id in self.actors:
            # This can happen during a restart, so we just log it and continue
            logger.warning(f"Actor {actor_id} already exists, it will be replaced.")
            await self.stop_actor(actor_id)

        # Check if actor should be on this node (sharding)
        shard = self._get_shard(actor_id)
        if shard not in self.local_shards:
            raise RuntimeError(f"Actor {actor_id} should be on different node")

        # Create actor instance
        actor = actor_class(actor_id, *args, **kwargs)

        # Register actor
        with self._lock:
            self.actors[actor_id] = actor
            self.actor_refs[actor_id] = ActorRef(actor_id, self)

        # Start actor
        await actor.start(self)

        logger.info(f"Created actor {actor_id} of type {actor_class.__name__}")
        return self.actor_refs[actor_id]

    async def stop_actor(self, actor_id: str):
        """Stop and remove an actor"""
        actor = self.actors.get(actor_id)
        if actor:
            await actor.stop()
            await actor.post_stop()

            with self._lock:
                if actor_id in self.actors:
                    del self.actors[actor_id]
                if actor_id in self.actor_refs:
                    del self.actor_refs[actor_id]

    async def restart_actor(self, actor_id: str):
        """Restart an actor."""
        actor = self.get_actor(actor_id)
        if actor:
            actor_class = type(actor)
            supervisor = actor.supervisor
            await self.stop_actor(actor_id)
            new_ref = await self.create_actor(actor_class, actor_id)
            new_actor = self.get_actor(actor_id)
            if new_actor:
                new_actor.supervisor = supervisor
            logger.info(f"Restarted actor {actor_id}")
            return new_ref

    def get_actor_ref(self, actor_id: str) -> Optional[ActorRef]:
        """Get reference to an actor"""
        return self.actor_refs.get(actor_id)

    def get_actor(self, actor_id: str) -> Optional[Actor]:
        """Get actor instance (for internal use)"""
        return self.actors.get(actor_id)

    async def deliver_message(self, message: ActorMessage) -> bool:
        """Deliver a message to the target actor"""
        actor = self.actors.get(message.recipient)
        if actor:
            return await actor.send_message(message)
        else:
            logger.warning(f"Actor {message.recipient} not found")
            return False

    def register_response_handler(self, response_id: str, future: asyncio.Future):
        """Register a handler for ask pattern responses"""
        self.response_handlers[response_id] = future

    def unregister_response_handler(self, response_id: str):
        """Unregister a response handler"""
        self.response_handlers.pop(response_id, None)

    def handle_response(self, response_id: str, response: Any):
        """Handle a response for ask pattern"""
        future = self.response_handlers.pop(response_id, None)
        if future and not future.cancelled():
            future.set_result(response)

    def _get_shard(self, actor_id: str) -> int:
        """Get shard number for an actor ID"""
        return hash(actor_id) % self.shard_count

    async def handle_failure(self, failed_actor: Actor, reason: Exception):
        """Handle actor failure based on supervision strategy"""
        if not failed_actor.supervisor:
            logger.error(f"Actor {failed_actor.actor_id} failed with no supervisor. Stopping.")
            await self.stop_actor(failed_actor.actor_id)
            return

        supervisor = self.get_actor(failed_actor.supervisor.actor_id)
        if not supervisor:
            logger.error(f"Supervisor for {failed_actor.actor_id} not found. Stopping.")
            await self.stop_actor(failed_actor.actor_id)
            return

        strategy = supervisor.supervision_strategy
        logger.info(
            f"Supervisor {supervisor.actor_id} handling failure of {failed_actor.actor_id} with strategy {strategy.value}"
        )

        if strategy == SupervisionStrategy.RESTART:
            await self.restart_actor(failed_actor.actor_id, reason)
        elif strategy == SupervisionStrategy.STOP:
            await self.stop_actor(failed_actor.actor_id)
        elif strategy == SupervisionStrategy.RESUME:
            failed_actor.state = ActorState.RUNNING  # Simplistic resume
        elif strategy == SupervisionStrategy.ESCALATE:
            if supervisor.supervisor:
                await self.handle_failure(supervisor, reason)
            else:
                logger.error(f"Cannot escalate failure from {supervisor.actor_id}, no supervisor. Stopping.")
                await self.stop_actor(supervisor.actor_id)

    def get_system_stats(self) -> dict[str, Any]:
        """Get system-wide statistics"""
        stats = {
            "system_name": self.system_name,
            "actor_count": len(self.actors),
            "shard_count": self.shard_count,
            "local_shards": list(self.local_shards),
            "p2p_nodes": len(self.p2p_nodes),
            "actors": {},
        }

        for actor_id, actor in self.actors.items():
            stats["actors"][actor_id] = actor.get_stats()

        return stats

    async def get_p2p_node(self, actor_id: str) -> Optional[P2PNode]:
        """Get or create a P2P node for an actor."""
        if actor_id not in self.p2p_nodes:
            actor = self.get_actor(actor_id)
            if actor:
                node = P2PNode(node_id=actor_id, capabilities=actor.capabilities)
                await node.start()
                self.p2p_nodes[actor_id] = node
        return self.p2p_nodes.get(actor_id)


class AIAgentActor(Actor):
    """
    Example AI Agent implemented as an actor.
    Demonstrates a lightweight, stateful AI agent that can handle tasks,
    manage its own memory, and collaborate with other agents.
    It also shows how an actor can change its behavior using `become`.
    """

    def __init__(self, actor_id: str, capabilities: Optional[list[str]] = None):
        super().__init__(actor_id)
        self.capabilities = capabilities or []
        self.current_tasks: dict[str, dict] = {}
        self.memory: dict[str, Any] = {}
        self.energy_level = 100.0  # Energy efficiency tracking

        # Register message handlers
        self.register_handler("assign_task", self._handle_assign_task)
        self.register_handler("complete_task", self._handle_complete_task)
        self.register_handler("query_status", self._handle_query_status)
        self.register_handler("update_memory", self._handle_update_memory)
        self.register_handler("collaborate", self._handle_collaborate)
        self.register_handler("child_failed", self._handle_child_failure)
        self.register_handler("p2p_connect", self._handle_p2p_connect)
        self.register_handler("p2p_send", self._handle_p2p_send)

    async def _handle_p2p_connect(self, message: ActorMessage) -> dict[str, Any]:
        """Handle a P2P connect request."""
        p2p_node = await self.actor_system.get_p2p_node(self.actor_id)
        if p2p_node:
            address = message.payload["address"]
            port = message.payload["port"]
            peer_id = await p2p_node.connect_to_peer(address, port)
            if peer_id:
                return {"status": "connected", "peer_id": peer_id}
        return {"status": "failed"}

    async def _handle_p2p_send(self, message: ActorMessage) -> dict[str, Any]:
        """Handle a P2P send request."""
        p2p_node = await self.actor_system.get_p2p_node(self.actor_id)
        if p2p_node:
            peer_id = message.payload["peer_id"]
            payload = message.payload["payload"]
            success = await p2p_node.send_to_peer(peer_id, payload)
            return {"status": "sent" if success else "failed"}
        return {"status": "failed"}

    async def _handle_child_failure(self, message: ActorMessage):
        """Handle a child failure."""
        child_id = message.payload["child_id"]
        error = message.payload["error"]
        logger.error(f"Child {child_id} of {self.actor_id} failed with error: {error}")
        await self.handle_child_failure(child_id, Exception(error))

    async def pre_start(self):
        """Initialize agent"""
        logger.info(f"AI Agent {self.actor_id} initializing with capabilities: {self.capabilities}")
        self.memory["start_time"] = time.time()

    async def _handle_assign_task(self, message: ActorMessage) -> dict[str, Any]:
        """Handle task assignment"""
        task_data = message.payload
        task_id = task_data.get("task_id")

        if len(self.current_tasks) >= 3:  # Limit concurrent tasks
            return {"status": "rejected", "reason": "too_many_tasks"}

        self.current_tasks[task_id] = {
            "task_data": task_data,
            "assigned_at": time.time(),
            "status": "in_progress",
        }

        # Simulate energy consumption
        self.energy_level -= 5.0

        logger.info(f"Agent {self.actor_id} accepted task {task_id}")
        return {"status": "accepted", "estimated_duration": 10.0}

    async def _handle_complete_task(self, message: ActorMessage) -> dict[str, Any]:
        """Handle task completion"""
        task_id = message.payload.get("task_id")
        result = message.payload.get("result")

        if task_id in self.current_tasks:
            task = self.current_tasks[task_id]
            task["status"] = "completed"
            task["completed_at"] = time.time()
            task["result"] = result

            # Update memory with learning
            self.memory[f"task_{task_id}"] = {
                "duration": task["completed_at"] - task["assigned_at"],
                "result_summary": result.get("summary", ""),
            }

            # Energy recovery
            self.energy_level = min(100.0, self.energy_level + 2.0)

            del self.current_tasks[task_id]

            logger.info(f"Agent {self.actor_id} completed task {task_id}")
            return {"status": "acknowledged"}

        return {"status": "error", "reason": "task_not_found"}

    async def _handle_query_status(self, message: ActorMessage) -> dict[str, Any]:
        """Handle status query"""
        return {
            "agent_id": self.actor_id,
            "capabilities": self.capabilities,
            "active_tasks": len(self.current_tasks),
            "energy_level": self.energy_level,
            "memory_size": len(self.memory),
            "uptime": time.time() - self.memory.get("start_time", time.time()),
        }

    async def _handle_update_memory(self, message: ActorMessage) -> dict[str, Any]:
        """Handle memory update"""
        memory_update = message.payload.get("memory_update", {})
        self.memory.update(memory_update)

        return {"status": "updated", "memory_size": len(self.memory)}

    async def _handle_collaborate(self, message: ActorMessage) -> dict[str, Any]:
        """Handle collaboration request from another agent"""
        request = message.payload
        collaboration_type = request.get("type")

        if collaboration_type == "share_knowledge":
            # Share relevant memory
            knowledge = {k: v for k, v in self.memory.items() if not k.startswith("_private")}
            return {"status": "shared", "knowledge": knowledge}

        elif collaboration_type == "request_assistance":
            required_capability = request.get("capability")
            if required_capability in self.capabilities:
                return {"status": "available", "can_assist": True}
            else:
                return {"status": "unavailable", "can_assist": False}

        return {"status": "unknown_collaboration_type"}


# Global actor system instance
_global_actor_system = None


async def get_global_actor_system() -> ActorSystem:
    """Get the global actor system instance"""
    global _global_actor_system
    if _global_actor_system is None:
        _global_actor_system = ActorSystem()
        await _global_actor_system.start()
    return _global_actor_system


async def demo_actor_system():
    """Demonstrate the actor system, including supervision and behavior changes."""
    system = await get_global_actor_system()

    # Create AI agents
    agent1_ref = await system.create_actor(AIAgentActor, "reasoning-agent-001", capabilities=["reasoning", "analysis"])

    agent2_ref = await system.create_actor(AIAgentActor, "memory-agent-001", capabilities=["memory", "storage"])

    # Test interaction
    correlation_id = str(uuid.uuid4())

    # Agent 1 gets a task
    response = await agent1_ref.ask(
        "assign_task",
        {
            "task_id": "analyze-data-001",
            "task_type": "analysis",
            "data": {"complexity": "high"},
        },
        correlation_id=correlation_id,
    )

    print("Task assignment response:", response)

    # Check status
    status = await agent1_ref.ask("query_status", {})
    print("Agent 1 status:", status)

    # Agent collaboration
    collab_response = await agent2_ref.ask("collaborate", {"type": "request_assistance", "capability": "memory"})
    print("Collaboration response:", collab_response)

    # System stats
    stats = system.get_system_stats()
    print("System stats:", json.dumps(stats, indent=2))


if __name__ == "__main__":
    asyncio.run(demo_actor_system())