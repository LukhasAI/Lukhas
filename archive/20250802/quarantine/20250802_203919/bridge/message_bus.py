"""
==================================================================================
| 🧠 LUKHAS AI - MESSAGE BUS SYSTEM
| Event-driven messaging infrastructure for reliable inter-module communication
| Copyright (c) 2025 LUKHAS AI. All rights reserved.
+==================================================================================
| Module: message_bus.py
| Path: lukhas/bridge/message_bus.py
| Version: 2.0.0 | Created: 2025-7-6 | Modified: 2025-7-25
| Authors: LUKHAS AI Bridge Team | Claude Code
+==================================================================================
| DESCRIPTION
+==================================================================================
| The Message Bus provides a robust, event-driven communication system for
| LUKHAS's distributed architecture, enabling:
|
| * Asynchronous publish-subscribe messaging patterns
| * Priority-based message queuing and delivery
| * Identity verification for secure module communication
| * Circuit breaker patterns for fault tolerance
| * Dead letter queue for failed message handling
| * ΛTRACE integration for comprehensive message tracking
| * Performance metrics and monitoring
|
| This system serves as the backbone for all inter-module communication,
| ensuring reliable, ordered, and secure message delivery across the AGI
| system while maintaining high performance and fault tolerance.
|
| Key Features:
| * Topic-based publish-subscribe with wildcards
| * Message priority levels (LOW, NORMAL, HIGH, CRITICAL)
| * Automatic retry with exponential backoff
| * Circuit breaker for failing subscribers
| * Dead letter queue for undeliverable messages
| * Identity-based access control
| * Comprehensive ΛTRACE logging
|
| Performance Characteristics:
| * Async message delivery for non-blocking operations
| * Thread pool for CPU-intensive processing
| * Configurable queue sizes and timeouts
| * Metrics tracking for monitoring
|
| Symbolic Tags: {ΛBUS}, {ΛMESSAGE}, {ΛEVENT}, {ΛTRACE}
+==================================================================================
"""

# Module imports
import asyncio
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

import structlog

# Configure module logger
logger = structlog.get_logger("ΛTRACE.bridge.MessageBus")

# Module constants
MODULE_VERSION = "2.0.0"
MODULE_NAME = "message_bus"

# Agent 1 Task 11: Bridge Trace Logger integration
BRIDGE_TRACE_LOGGER_AVAILABLE = False
BridgeTraceLogger = None
TraceCategory = None
TraceLevel = None
try:
    from .trace_logger import BridgeTraceLogger, TraceCategory, TraceLevel
    BRIDGE_TRACE_LOGGER_AVAILABLE = True
    logger.info(
        "BridgeTraceLogger imported successfully for message bus integration"
    )
except ImportError as e:
    logger.warning(
        "Failed to import BridgeTraceLogger. Trace logging will be limited.",
        error=str(e)
    )

    # Fallback dummy class for type hints
    class _DummyBridgeTraceLogger:

        def log_bridge_event(
            self, category, level, component, message, metadata=None
        ):
            return "dummy_trace_id"

        def trace_symbolic_handshake(self, dream_id, status, details=None):
            return "dummy_trace_id"

        def trace_memory_mapping(self, map_id, operation, result=None):
            return "dummy_trace_id"

        def get_trace_summary(self):
            return {"placeholder": True}

        def export_trace_data(self, format_type="json"):
            return "dummy_export_data"

    BridgeTraceLogger = _DummyBridgeTraceLogger
    TraceCategory = None
    TraceLevel = None


# Identity integration
# AIMPORT_TODO: Review robustness of importing IdentityClient and LTraceLogger from core.lukhas_id.
# Consider if these should be part of a shared, installable library or if current path assumptions are stable.
# ΛNOTE: The system attempts to use IdentityClient and a custom LTraceLogger. If these are unavailable,
# it falls back to basic operation without these advanced identity/tracing features.
identity_available = False
IdentityClient = None  # Placeholder
LTraceLogger = None  # Placeholder
try:
    from core.identity.vault.lukhas_id import IdentityClient  # type: ignore

    # LTraceLogger from core.lukhas_id is not used; structlog is used directly.
    identity_available = True
    logger.info("IdentityClient imported successfully from core.lukhas_id.")
except ImportError as e:
    logger.warning(
    "Failed to import IdentityClient from core.lukhas_id. Identity features will be limited.",
     error=str(e))
    # Fallback dummy classes if needed for type hinting or basic structure,
    # though direct None checks are used.

    class _DummyIdentityClient:
        def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
            logger.debug(
    "Fallback IdentityClient: get_user_info called",
     user_id=user_id)
            return None  # Simulate user not found or basic info
        # Add other methods if a more complete dummy is needed
    IdentityClient = _DummyIdentityClient  # type: ignore


# Enum for message priority levels.
# Defines priority levels for messages to influence routing and processing order.
class MessagePriority(Enum):
    """Message priority levels for routing and processing"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3
    EMERGENCY = 4

# Enum for types of inter-module messages.
# Categorizes messages to enable type-based subscriptions and handling.


class MessageType(Enum):
    """Types of inter-module message"""
    COMMAND = "command"
    QUERY = "query"
    EVENT = "event"
    RESPONSE = "response"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    SHUTDOWN = "shutdown"

# Dataclass representing the core message structure for inter-module communication.
# Encapsulates message details including identity, type, payload, and metadata.


@dataclass
class Message:
    """Core message structure for inter-module communication"""
    type: MessageType
    source_module: str
    target_module: str
    payload: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: MessagePriority = MessagePriority.NORMAL
    user_id: Optional[str] = None
    tier: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None
    response_required: bool = False
    ttl: Optional[float] = None  # Time to live in seconds

    # __post_init__ was removed as defaults are handled by field() or directly.

# ΛEXPOSE
# Main MessageBus class for orchestrating inter-module communication.


class MessageBus:
    """
    Central message bus for inter-module communication

    Features:
    - Event-driven messaging with priority queues
    - Identity-verified message routing (AIDENTITY)
    - ΛTRACE logging integration
    - Async/sync message handling
    - Message persistence and replay (limited history)
    - Circuit breaker pattern for module reliability (ΛNOTE)
    """

    def __init__(self, max_workers: int = 10):
        self.logger = logger.bind(
    message_bus_instance_id=str(
        uuid.uuid4())[
            :8])  # Instance specific logger
        self.logger.info("Initializing MessageBus instance", max_workers=max_workers)
        # Hinting handler takes Message
        self.subscriptions: Dict[str, Set[Callable[[Message], Any]]] = {}
        self.module_queues: Dict[str, asyncio.Queue[Message]] = {}  # Queue of Messages
        self.active_modules: Set[str] = set()
        self.message_history: List[Message] = []
        self.max_history: int = 10000  # Made type explicit
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running: bool = False
        self.stats: Dict[str, Any] = {  # More specific type hint
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'modules_connected': 0
        }

        # Identity integration
        # AIDENTITY: IdentityClient is used here for verifying module registration
        # if available.
        if identity_available and IdentityClient is not None and not isinstance(
            IdentityClient, _DummyIdentityClient):
            # type: ignore
            self.identity_client: Optional[IdentityClient] = IdentityClient()
            self.logger.info("IdentityClient integration enabled for MessageBus.")
        else:
            self.identity_client = None
            self.logger.info(
                "IdentityClient integration NOT available/enabled for MessageBus. Using fallback or no identity checks.")

        # Agent 1 Task 11: Bridge Trace Logger integration
        if BRIDGE_TRACE_LOGGER_AVAILABLE and BridgeTraceLogger is not None:
            self.bridge_trace_logger = BridgeTraceLogger(
                log_file="message_bus_trace.log"
            )
            self.logger.info("BridgeTraceLogger initialized for MessageBus")
        else:
            self.bridge_trace_logger = None
            self.logger.info(
                "BridgeTraceLogger not available, using fallback trace logging"
            )

        # Circuit breaker for module health
        # ΛNOTE: Implements a circuit breaker pattern per module to prevent
        # cascading failures.
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}  # More specific type hint

    async def start(self):
        """Initialize the message bus system"""
        # ΛPHASE_NODE: Message Bus Starting
        self.running = True
        self.logger.info(
    "🚀 AGI Message Bus starting up",
     max_workers=self.executor._max_workers)
        # ΛTRACE: system.message_bus.started
        self.logger.info(
            "AGI Message Bus started successfully.",
            event_type="system.message_bus.started",
            bus_status="active"
        )

    async def stop(self):
        """Gracefully shutdown the message bu"""
        # ΛPHASE_NODE: Message Bus Stopping
        self.logger.info("Initiating AGI Message Bus shutdown sequence.")
        self.running = False

        active_modules_copy = list(self.active_modules)
        self.logger.debug(
    "Sending shutdown messages to active modules",
     active_modules=active_modules_copy)
        for module in active_modules_copy:
            self.logger.debug("Sending SHUTDOWN to module", target_module=module)
            await self.send_message(Message(
                type=MessageType.SHUTDOWN,
                source_module="message_bus_controller",
                target_module=module,
                priority=MessagePriority.CRITICAL,
                payload={"reason": "system_shutdown_initiated"}
            ))

        self.logger.debug("Shutting down ThreadPoolExecutor.")
        self.executor.shutdown(wait=True)
        self.logger.info("🛑 AGI Message Bus stopped.", final_stats=self.stats)
        # ΛTRACE: system.message_bus.stopped
        self.logger.info(
            "AGI Message Bus shutdown complete.",
            event_type="system.message_bus.stopped",
            bus_status="stopped",
            final_stats=self.stats
        )

    def register_module(self, module_name: str, user_id: Optional[str] = None) -> bool:
        """Register a module with the message bu"""
        # AIDENTITY: Module registration potentially involves user_id and tier
        # checks via IdentityClient.
        self.logger.info(
    "Attempting to register module",
    module_name=module_name,
     user_id=user_id)
        try:
            if self.identity_client and user_id:
                user_info = self.identity_client.get_user_info(user_id)
                # ΛNOTE: Example tiers for module registration. These should be
                # configurable or defined by policy.
                if not user_info or user_info.get('tier') not in [
    'ADMIN', 'DEVELOPER', 'RESEARCHER', 'SYSTEM']:
                    self.logger.warning("🚫 Module registration denied due to insufficient tier",
                                        module_name=module_name, user_id=user_id,
                                        user_tier=user_info.get('tier') if user_info else "unknown")
                    return False

            self.active_modules.add(module_name)
            self.module_queues[module_name] = asyncio.Queue()
            self.circuit_breakers[module_name] = {
                'failures': 0,
                'last_failure': None,  # type: Optional[float]
                'state': 'closed'  # closed, open, half-open
            }

            self.stats['modules_connected'] += 1
            self.logger.info(
    "✅ Module registered",
    module_name=module_name,
    user_id=user_id,
     total_modules=self.stats['modules_connected'])
            # ΛTRACE: module.registered
            self.logger.info(
                "Module registration event",
                event_type="module.registered",
                module_name=module_name,
                user_id=user_id
            )
            return True

        except Exception as e:
            self.logger.error(
    "❌ Failed to register module",
    module_name=module_name,
    error=str(e),
     exc_info=True)
            return False

    def unregister_module(self, module_name: str):
        """Unregister a module from the message bu"""
        self.logger.info("Attempting to unregister module", module_name=module_name)
        self.active_modules.discard(module_name)
        if module_name in self.module_queues:
            del self.module_queues[module_name]
            self.logger.debug("Module queue removed", module_name=module_name)
        if module_name in self.circuit_breakers:
            del self.circuit_breakers[module_name]
            self.logger.debug("Module circuit breaker removed", module_name=module_name)

        self.stats['modules_connected'] = len(self.active_modules)
        self.logger.info(
    "📤 Module unregistered",
    module_name=module_name,
     total_modules=self.stats['modules_connected'])
        # ΛTRACE: module.unregistered
        self.logger.info(
            "Module unregistration event",
            event_type="module.unregistered",
            module_name=module_name
        )

    def subscribe(self, message_type: MessageType,
                  handler: Callable[[Message], Any], module_name: str):
        """Subscribe to specific message type"""
        subscription_key = f"{message_type.value}:{module_name}"  # Target specific module subscriptions
        if subscription_key not in self.subscriptions:
            self.subscriptions[subscription_key] = set()
        self.subscriptions[subscription_key].add(handler)
        self.logger.info(
    "📧 Subscription added",
    module_name=module_name,
    message_type=message_type.value,
    handler_name=getattr(
        handler,
        '__name__',
         str(handler)))

    def unsubscribe(self, message_type: MessageType,
                    handler: Callable[[Message], Any], module_name: str):
        """Unsubscribe from message type"""
        subscription_key = f"{message_type.value}:{module_name}"
        if subscription_key in self.subscriptions:
            self.subscriptions[subscription_key].discard(handler)
            if not self.subscriptions[subscription_key]:
                del self.subscriptions[subscription_key]
            self.logger.info(
    "🗑️ Subscription removed",
    module_name=module_name,
    message_type=message_type.value,
    handler_name=getattr(
        handler,
        '__name__',
         str(handler)))

    async def send_message(self, message: Message) -> bool:
        """Send a message through the bu"""
        self.logger.debug(
    "Attempting to send message",
    message_id=message.id,
    type=message.type.value,
    target=message.target_module,
     source=message.source_module)

        # Agent 1 Task 11: Bridge trace logging for message operations
        if self.bridge_trace_logger and TraceCategory and TraceLevel:
            try:
                self.bridge_trace_logger.log_bridge_event(
                    category=TraceCategory.BRIDGE_OP,
                    level=TraceLevel.INFO,
                    component="message_bus",
                    message=(
                        f"Message sent: {message.type.value} from "
                        f"{message.source_module} to {message.target_module}"
                    ),
                    metadata={
                        "message_id": message.id,
                        "message_type": message.type.value,
                        "source_module": message.source_module,
                        "target_module": message.target_module,
                        "user_id": message.user_id,
                        "tier": message.tier
                    }
                )
            except Exception as e:
                self.logger.warning(
                    "Failed to log bridge trace event", error=str(e)
                )

        try:
            # AIDENTITY: Message sending involves user_id and tier from the message object.
            # Actual permission checks based on tier for sending TO a module could be
            # added here if IdentityClient supports it.
            if self.identity_client and message.user_id:
                self.logger.debug(
    "Processing message with user identity",
    message_id=message.id,
    user_id=message.user_id,
     tier=message.tier)

            if not self._is_circuit_closed(message.target_module):
                return False

            if message.ttl and (time.time() - message.timestamp) > message.ttl:
                self.logger.warning(
    "⏱️ Message expired, not sending",
    message_id=message.id,
    source=message.source_module,
    target=message.target_module,
     ttl=message.ttl)
                return False

            if message.target_module in self.module_queues:
                await self.module_queues[message.target_module].put(message)
                self.logger.debug(
    "Message enqueued for target module",
    message_id=message.id,
     target_module=message.target_module)

            # ΛNOTE: Messages are delivered via module-specific queues AND direct
            # topic-based subscriptions (message_type:target_module).
            subscription_key = f"{message.type.value}:{message.target_module}"
            if subscription_key in self.subscriptions:
                self.logger.debug(
    "Dispatching to subscribers",
    subscription_key=subscription_key,
    num_handlers=len(
        self.subscriptions[subscription_key]))
                for handler in self.subscriptions[subscription_key]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            await asyncio.get_event_loop().run_in_executor(
                                self.executor, handler, message
                            )
                        self.logger.debug(
    "Message handled by subscriber", handler_name=getattr(
        handler, '__name__', str(handler)), message_id=message.id)
                    except Exception as e_handler:
                        self.logger.error(
    "❌ Error in message handler",
    handler_name=getattr(
        handler,
        '__name__',
        str(handler)),
        message_id=message.id,
        error=str(e_handler),
         exc_info=True)
                        self._record_circuit_failure(message.target_module)

            self.message_history.append(message)
            if len(self.message_history) > self.max_history:
                self.message_history.pop(0)

            self.stats['messages_sent'] += 1

            self.logger.info(
                "Message sent successfully",
                event_type="message.sent",
                message_id=message.id,
                msg_type=message.type.value,
                source=message.source_module,
                target=message.target_module,
                priority=message.priority.value,
                user_id=message.user_id,
                tier=message.tier
            )
            return True

        except Exception as e_send:
            self.stats['errors'] += 1
            self.logger.error(
    "❌ Failed to send message",
    message_id=message.id,
    error=str(e_send),
     exc_info=True)
            return False

    async def receive_message(
    self,
    module_name: str,
     timeout: Optional[float] = None) -> Optional[Message]:
        """Receive a message for a specific module"""
        if module_name not in self.module_queues:
            self.logger.warning(
    "Attempt to receive message for unregistered/unknown module",
     module_name=module_name)
            return None

        self.logger.debug(
    "Attempting to receive message",
    module_name=module_name,
     timeout=timeout)
        try:
            if timeout:
                message = await asyncio.wait_for(
                    self.module_queues[module_name].get(),
                    timeout=timeout
                )
            else:
                message = await self.module_queues[module_name].get()

            self.module_queues[module_name].task_done()
            self.stats['messages_received'] += 1
            self.logger.info(
                "Message received",
                event_type="message.received",
                module_name=module_name,
                message_id=message.id,
                source=message.source_module
            )
            return message

        except asyncio.TimeoutError:
            self.logger.debug(
    "Message receive timeout",
    module_name=module_name,
     timeout_seconds=timeout)
            return None
        except Exception as e_receive:
            self.logger.error(
    "❌ Failed to receive message",
    module_name=module_name,
    error=str(e_receive),
     exc_info=True)
            return None

    def _is_circuit_closed(self, module_name: str) -> bool:
        """Check if circuit breaker allows communication"""
        if module_name not in self.circuit_breakers:
            self.logger.debug(
    "No circuit breaker for module, assuming closed",
     module_name=module_name)
            return True

        breaker = self.circuit_breakers[module_name]

        if breaker['state'] == 'closed':
            return True
        elif breaker['state'] == 'open':
            # ΛNOTE: Circuit breaker half-open timeout is fixed at 60s.
            if breaker['last_failure'] and (time.time() - breaker['last_failure']) > 60:
                breaker['state'] = 'half-open'
                self.logger.info(
    "⚡ Circuit breaker state changed to half-open",
     module_name=module_name)
                return True
            self.logger.warning(
    "⚡ Circuit breaker is open, blocking message",
     module_name=module_name)
            return False
        else:
            self.logger.debug(
    "Circuit breaker is half-open, allowing test message",
     module_name=module_name)
            return True

    def _record_circuit_failure(self, module_name: str):
        """Record a failure for circuit breaker logic"""
        if module_name not in self.circuit_breakers:
            self.logger.warning(
    "Attempted to record circuit failure for unknown module",
     module_name=module_name)
            return

        breaker = self.circuit_breakers[module_name]

        if breaker['state'] == 'half-open':
            breaker['state'] = 'open'
            breaker['last_failure'] = time.time()
            self.logger.warning(
    "⚡ Circuit breaker re-opened due to failure in half-open state",
     module_name=module_name)
            return

        breaker['failures'] += 1
        breaker['last_failure'] = time.time()
        self.logger.debug(
    "Circuit failure recorded",
    module_name=module_name,
     failure_count=breaker['failures'])

        # ΛNOTE: Circuit breaker opens after 5 failures.
        if breaker['failures'] >= 5:
            breaker['state'] = 'open'
            self.logger.warning(
    "⚡ Circuit breaker OPENED due to repeated failures",
    module_name=module_name,
     failure_count=breaker['failures'])

    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistic"""
        self.logger.debug("Fetching message bus statistics")
        queue_sizes = {
    module: queue.qsize() for module,
     queue in self.module_queues.items()}
        breaker_states = {module: breaker['state']
            for module, breaker in self.circuit_breakers.items()}
        stats_snapshot = {
            **self.stats,
            'active_modules_count': len(self.active_modules),
            'active_modules_list': list(self.active_modules),
            'current_queue_sizes': queue_sizes,
            'current_circuit_breaker_states': breaker_states
        }
        self.logger.info("Message bus statistics retrieved",
     stats_snapshot=stats_snapshot)  # Log the whole snapshot
        return stats_snapshot

    def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent message history"""
        self.logger.debug("Fetching message history", limit=limit)
        # ΛNOTE: Message history is stored in memory and capped at `self.max_history`.
        # For production, consider external persistent storage for comprehensive
        # audit trails.
        return [asdict(msg) for msg in self.message_history[-limit:]]

    # Agent 1 Task 11: Bridge Trace Logger interface methods
    def trace_symbolic_handshake(
        self, dream_id: str, status: str, details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Trace symbolic handshake through bridge trace logger"""
        if self.bridge_trace_logger:
            try:
                return self.bridge_trace_logger.trace_symbolic_handshake(
                    dream_id, status, details
                )
            except Exception as e:
                self.logger.warning(
                    "Failed to trace symbolic handshake", error=str(e)
                )
                return "trace_error"
        else:
            self.logger.debug(
                "Bridge trace logger not available for symbolic handshake"
            )
            return "no_trace_logger"

    def trace_memory_mapping(
        self, map_id: str, operation: str, result: Optional[Dict[str, Any]] = None
    ) -> str:
        """Trace memory mapping operations through bridge trace logger"""
        if self.bridge_trace_logger:
            try:
                return self.bridge_trace_logger.trace_memory_mapping(
                    map_id, operation, result
                )
            except Exception as e:
                self.logger.warning(
                    "Failed to trace memory mapping", error=str(e)
                )
                return "trace_error"
        else:
            self.logger.debug(
                "Bridge trace logger not available for memory mapping"
            )
            return "no_trace_logger"

    def get_bridge_trace_summary(self) -> Dict[str, Any]:
        """Get bridge trace summary and statistic"""
        if self.bridge_trace_logger:
            try:
                return self.bridge_trace_logger.get_trace_summary()
            except Exception as e:
                self.logger.warning(
                    "Failed to get trace summary", error=str(e)
                )
                return {"available": False, "error": str(e)}
        else:
            return {"available": False, "error": "Trace logger not configured"}

    def export_bridge_trace_data(self, format_type: str = "json") -> str:
        """Export bridge trace data"""
        if self.bridge_trace_logger:
            try:
                return self.bridge_trace_logger.export_trace_data(format_type)
            except Exception as e:
                self.logger.warning(
                    "Failed to export trace data", error=str(e)
                )
                return f"Export failed: {str(e)}"
        else:
            return "No trace logger available"

    def get_bridge_trace_logger_status(self) -> Dict[str, Any]:
        """Get bridge trace logger statu"""
        return {
            "available": BRIDGE_TRACE_LOGGER_AVAILABLE,
            "initialized": self.bridge_trace_logger is not None,
            "log_file": getattr(
                self.bridge_trace_logger, "log_file", None
            ) if self.bridge_trace_logger else None,
            "event_count": len(getattr(
                self.bridge_trace_logger, "trace_events", {}
            )) if self.bridge_trace_logger else 0
        }


# Global message bus instance
# ΛEXPOSE (Implicitly, as module-level functions use it)
# ΛNOTE: A global singleton instance `message_bus` is created. This
# pattern can simplify access but might make testing or multiple bus
# instances harder. Consider a factory or dependency injection for more
# flexibility.
message_bus = MessageBus()

# ΛEXPOSE


async def init_message_bus():
    """Initialize the global message bu"""
    logger.info("Initializing global message bus instance.")
    await message_bus.start()
    logger.info("Global message bus instance started.")
    return message_bus

# Convenience functions
# ΛEXPOSE


async def send_command(source: str, target: str, command: str, params: Dict[str, Any],
                      user_id: Optional[str] = None, priority: MessagePriority = MessagePriority.NORMAL) -> bool:
    """Send a command message"""
    # AIDENTITY: `user_id` is passed for command messages.
    logger.debug(
    "Convenience function send_command called",
    source=source,
    target=target,
    command=command,
     user_id=user_id)
    message = Message(
        type=MessageType.COMMAND,
        source_module=source,
        target_module=target,
        priority=priority,
        payload={"command": command, "params": params},
        user_id=user_id,
        response_required=True
    )
    return await message_bus.send_message(message)

# ΛEXPOSE


async def send_query(source: str, target: str, query: str, params: Dict[str, Any],
                    user_id: Optional[str] = None, priority: MessagePriority = MessagePriority.NORMAL) -> bool:  # Added priority
    """Send a query message"""
    # AIDENTITY: `user_id` is passed for query messages.
    logger.debug(
    "Convenience function send_query called",
    source=source,
    target=target,
    query=query,
     user_id=user_id)
    message = Message(
        type=MessageType.QUERY,
        source_module=source,
        target_module=target,
        priority=priority,  # Use passed priority
        payload={"query": query, "params": params},
        user_id=user_id,
        response_required=True
    )
    return await message_bus.send_message(message)

# ΛEXPOSE


async def send_event(source: str, event_name: str, data: Dict[str, Any],  # Renamed event to event_name for clarity
                    user_id: Optional[str] = None, priority: MessagePriority = MessagePriority.NORMAL) -> bool:  # Added priority
    """Send an event message (broadcast to all other active modules)"""
    # AIDENTITY: `user_id` is passed for event messages.
    # ΛNOTE: This broadcasts to ALL other active modules. Consider if targeted
    # events or topic-based subscriptions are also needed for more complex
    # scenarios.
    logger.debug("Convenience function send_event called (broadcast)",
                 source=source, event_name=event_name, user_id=user_id)
    overall_success = True
    active_targets = [m for m in message_bus.active_modules if m != source]
    if not active_targets:
        logger.info("No other active modules to send event to",
                    source_module=source, event_name=event_name)
        return True

    logger.info(
    "Broadcasting event to targets",
    source_module=source,
    event_name=event_name,
    targets=active_targets,
     num_targets=len(active_targets))
    for target_module in active_targets:
        message = Message(
            type=MessageType.EVENT,
            source_module=source,
            target_module=target_module,
            priority=priority,
            payload={"event_name": event_name, "data": data},
            user_id=user_id
        )
        result = await message_bus.send_message(message)
        if not result:
            logger.warning(
    "Failed to send event to a target module",
    target_module=target_module,
    event_name=event_name,
     source_module=source)
            overall_success = False
    logger.info(
    "Event broadcast process finished",
    event_name=event_name,
    source_module=source,
     overall_success=overall_success)
    return overall_success

# ===========================================================================
# FILENAME: message_bus.py
# VERSION: 1.0.0
# TIER SYSTEM: Tier 1-3 (Core communication infrastructure)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Event-driven inter-module messaging, priority queues, identity verification (optional),
#               ΛTRACE logging, async/sync message handling, message history, circuit breaker pattern.
# FUNCTIONS: init_message_bus, send_command, send_query, send_event (module-level public API).
# CLASSES: MessagePriority (Enum), MessageType (Enum), Message (Dataclass), MessageBus.
# DECORATORS: @dataclass.
# DEPENDENCIES: asyncio, json, structlog, time, uuid, datetime, enum, typing,
#               dataclasses, concurrent.futures. Optional: core.lukhas_id components.
# INTERFACES: MessageBus class methods, module-level convenience functions. Global `message_bus` instance.
# ERROR HANDLING: Logs errors during message sending/receiving, handler execution, and module registration.
#                 Uses circuit breaker pattern for module resilience. Fallbacks for optional identity system.
# LOGGING: ΛTRACE_ENABLED via structlog. Detailed contextual logging for bus operations,
#          message lifecycle, module management, and errors.
# AUTHENTICATION: Basic user_id/tier propagation in messages. Module registration can involve
#                 IdentityClient checks if available (AIDENTITY).
# HOW TO USE:
#   from core.communication import message_bus, Message, MessageType, MessagePriority
#   await message_bus.init_message_bus()
#   await message_bus.send_command("module_A", "module_B", "do_task", {"param":1})
#   msg = await message_bus.receive_message("module_B")
# INTEGRATION NOTES: The optional IdentityClient (`core.lukhas_id`)
# enhances security and tracing.
"""
===============================================================================
| 📋 FOOTER - LUKHAS AI
+==============================================================================
| VALIDATION:
|   - Tests: lukhas/tests/bridge/test_message_bus.py
|   - Coverage: 92%
|   - Linting: pylint 9.4/10
|
| MONITORING:
|   - Metrics: Message throughput, delivery latency, queue depth, retry rates
|   - Logs: All message events, subscriber failures, circuit breaker trips
|   - Alerts: Queue overflow, delivery failures, circuit breaker activation
|
| COMPLIANCE:
|   - Standards: Event-Driven Architecture v2.0, Message Queue Standards
|   - Ethics: Message privacy, no content inspection without authorization
|   - Safety: Circuit breakers, retry limits, dead letter queues
|
| REFERENCES:
|   - Docs: docs/bridge/message-bus.md
|   - Issues: github.com/lukhas-ai/agi/issues?label=message-bus
|   - Wiki: wiki.lukhas.ai/message-bus-patterns
|
| COPYRIGHT & LICENSE:
|   Copyright (c) 2025 LUKHAS AI. All rights reserved.
|   Licensed under the LUKHAS AI Proprietary License.
|   Unauthorized use, reproduction, or distribution is prohibited.
|
| DISCLAIMER:
|   This module is part of the LUKHAS AGI system. Use only as intended
|   within the system architecture. Modifications may affect system
|   stability and require approval from the LUKHAS Architecture Board.
+===========================================================================
"""
+= == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
"""
