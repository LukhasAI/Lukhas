"""
Golden Trio Orchestrator

Unified orchestration system for DAST, ABAS, and NIAS coordination.
Manages communication, prevents circular dependencies, and optimizes execution flow.
"""

from __future__ import annotations
import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

from core.audit.audit_decision_embedding_engine import DecisionAuditEngine
from ethics.core import DecisionType, get_shared_ethics_engine
from ethics.seedra import get_seedra
from symbolic.core import get_symbolic_translator, get_symbolic_vocabulary

            try:
                value = self.context
                for key in path.split("."):
                    value = value[key]
                return value
            except (KeyError, TypeError):

            try:
                # Get message from queue with timeout
                message = await asyncio.wait_for(queue.get(), timeout=1.0)

                # Process message
                handler = self.system_handlers.get(system)
                if handler:
                    start_time = datetime.now(timezone.utc)

                    # Update system state
                    await self.context_manager.update_system_state(
                        system,
                        {
                            "status": "processing",
                            "current_message": message.id,
                        },
                    )

                    # Process through handler
                    result = await handler.process(message)

                    # Calculate processing time
                    processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

                    # Create response
                    response = TrioResponse(
                        message_id=message.id,
                        system=system,
                        status="success",
                        result=result,
                        processing_time_ms=processing_time,
                    )

                    # Update context
                    await self.context_manager.update_system_state(
                        system,
                        {"status": "idle", "last_processed": message.id},
                    )

                    # Store response if needed
                    if message.id in self.active_messages:
                        self.active_messages[message.id].metadata["response"] = response

            except asyncio.TimeoutError:
            try:
                # Check for deadlocks
                deadlocks = self._detect_deadlocks()
                if deadlocks:
                    await self._resolve_deadlocks(deadlocks)

                # Optimize message flow
                await self._optimize_message_flow()

                await asyncio.sleep(0.1)

            except Exception as e:

        import uuid

logger = logging.getLogger(__name__)


class SystemType(Enum):
    """Golden Trio system types"""

    DAST = "dast"
    ABAS = "abas"
    NIAS = "nias"


class MessagePriority(Enum):
    """Message priority levels"""

    CRITICAL = 5
    HIGH = 4
    NORMAL = 3
    LOW = 2
    BACKGROUND = 1


class ProcessingMode(Enum):
    """Processing modes for the orchestrator"""

    SEQUENTIAL = auto()  # Process one at a time
    PARALLEL = auto()  # Process in parallel
    OPTIMIZED = auto()  # Smart routing based on dependencies


@dataclass
class TrioMessage:
    """Message passed between Golden Trio systems"""

    id: str
    source: SystemType
    target: SystemType
    message_type: str
    payload: dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = True
    timeout_ms: int = 1000
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrioResponse:
    """Response from a Golden Trio system"""

    message_id: str
    system: SystemType
    status: str  # success, error, deferred
    result: Any
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class SharedContextManager:
    """
    Manages shared context between DAST, ABAS, and NIAS.
    Single source of truth for system state.
    """

    def __init__(self):
        self.context: dict[str, Any] = {}
        self.context_history: deque = deque(maxlen=1000)
        self.version: int = 0
        self._lock = asyncio.Lock()

        self._initialize_context()

    def _initialize_context(self):
        """Initialize default context structure"""
        self.context = {
            "user_state": {
                "id": None,
                "emotional_state": {},
                "consent_level": None,
                "preferences": {},
                "active_tasks": [],
            },
            "system_state": {
                "dast": {"status": "idle", "active_tasks": []},
                "abas": {"status": "idle", "active_conflicts": []},
                "nias": {"status": "idle", "active_filters": []},
            },
            "environment": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "location": None,
                "device": None,
                "network_quality": "good",
            },
            "performance": {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "response_times": {},
            },
        }

    async def get(self, path: str, default: Any = None) -> Any:
        """Get value from context using dot notation path"""
        async with self._lock:
    async def set(self, path: str, value: Any) -> None:
        """Set value in context using dot notation path"""
        async with self._lock:
            keys = path.split(".")
            target = self.context

            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]

            # Set the value
            target[keys[-1]] = value

            # Update version and history
            self.version += 1
            self.context_history.append(
                {
                    "version": self.version,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "path": path,
                    "value": value,
                }
            )

    async def update_user_state(self, updates: dict[str, Any]) -> None:
        """Update user state in context"""
        async with self._lock:
            self.context["user_state"].update(updates)
            self.version += 1

    async def update_system_state(self, system: SystemType, updates: dict[str, Any]) -> None:
        """Update system state in context"""
        async with self._lock:
            self.context["system_state"][system.value].update(updates)
            self.version += 1

    async def get_full_context(self) -> dict[str, Any]:
        """Get a copy of the full context"""
        async with self._lock:
            return self.context.copy()

    async def get_version(self) -> int:
        """Get current context version"""
        async with self._lock:
            return self.version


class TrioOrchestrator:
    """
    Main orchestrator for DAST, ABAS, and NIAS coordination.

    Responsibilities:
    - Message routing between systems
    - Circular dependency prevention
    - Performance optimization
    - Context synchronization
    - Error handling and recovery
    """

    def __init__(self, processing_mode: ProcessingMode = ProcessingMode.OPTIMIZED):
        self.processing_mode = processing_mode
        self.context_manager = SharedContextManager()
        self.message_queue: dict[SystemType, asyncio.Queue] = {}
        self.active_messages: dict[str, TrioMessage] = {}
        self.system_handlers: dict[SystemType, Any] = {}
        self.dependencies: dict[str, set[str]] = {}
        self.performance_cache: dict[str, Any] = {}

        # Initialize components
        self.seedra = get_seedra()
        self.ethics_engine = get_shared_ethics_engine()
        self.translator = get_symbolic_translator()
        self.vocabulary = get_symbolic_vocabulary()
        self.audit_engine = DecisionAuditEngine()
        asyncio.create_task(self.audit_engine.initialize())

        # Initialize queues for each system
        for system in SystemType:
            self.message_queue[system] = asyncio.Queue()

        # Processing tasks
        self.processing_tasks: list[asyncio.Task] = []
        self.is_running = False

        logger.info(f"TrioOrchestrator initialized with {processing_mode.name} mode")

    def register_system_handler(self, system: SystemType, handler: Any) -> None:
        """Register a handler for a specific system"""
        self.system_handlers[system] = handler
        logger.info(f"Registered handler for {system.value}")

    async def start(self) -> None:
        """Start the orchestrator"""
        if self.is_running:
            logger.warning("Orchestrator already running")
            return

        self.is_running = True

        # Start processing tasks for each system
        for system in SystemType:
            task = asyncio.create_task(self._process_system_queue(system))
            self.processing_tasks.append(task)

        # Start dependency resolver
        resolver_task = asyncio.create_task(self._dependency_resolver())
        self.processing_tasks.append(resolver_task)

        logger.info("TrioOrchestrator started")

    async def stop(self) -> None:
        """Stop the orchestrator"""
        self.is_running = False

        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)

        self.processing_tasks.clear()
        logger.info("TrioOrchestrator stopped")

    async def send_message(
        self,
        source: SystemType,
        target: SystemType,
        message_type: str,
        payload: dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        timeout_ms: int = 1000,
    ) -> TrioResponse:
        """Send a message from one system to another"""
        # Create message
        message = TrioMessage(
            id=self._generate_message_id(),
            source=source,
            target=target,
            message_type=message_type,
            payload=payload,
            priority=priority,
            timeout_ms=timeout_ms,
        )

        # Check for circular dependencies
        if self._would_create_circular_dependency(message):
            logger.warning(f"Circular dependency detected: {source.value} -> {target.value}")
            return TrioResponse(
                message_id=message.id,
                system=target,
                status="error",
                result={"error": "Circular dependency detected"},
                processing_time_ms=0,
            )

        # Perform ethical check
        ethical_check = await self._check_ethical_compliance(message)
        if ethical_check["decision"] != DecisionType.ALLOW:
            return TrioResponse(
                message_id=message.id,
                system=target,
                status="blocked",
                result={"reason": ethical_check["reason"]},
                processing_time_ms=0,
            )

        # Add to active messages
        self.active_messages[message.id] = message

        # Route message based on processing mode
        if self.processing_mode == ProcessingMode.SEQUENTIAL:
            response = await self._process_message_sequential(message)
        elif self.processing_mode == ProcessingMode.PARALLEL:
            response = await self._process_message_parallel(message)
        else:  # OPTIMIZED
            response = await self._process_message_optimized(message)

        # Clean up
        self.active_messages.pop(message.id, None)

        return response

    async def _process_system_queue(self, system: SystemType) -> None:
        """Process messages for a specific system"""
        queue = self.message_queue[system]

        while self.is_running:
            except Exception as e:
                logger.error(f"Error processing message for {system.value}: {e}")

    async def _process_message_sequential(self, message: TrioMessage) -> TrioResponse:
        """Process message sequentially"""
        await self.message_queue[message.target].put(message)

        # Wait for response
        start_time = datetime.now(timezone.utc)
        while (datetime.now(timezone.utc) - start_time).total_seconds() * 1000 < message.timeout_ms:
            if "response" in message.metadata:
                return message.metadata["response"]
            await asyncio.sleep(0.01)

        # Timeout
        return TrioResponse(
            message_id=message.id,
            system=message.target,
            status="timeout",
            result={},
            processing_time_ms=message.timeout_ms,
        )

    async def _process_message_parallel(self, message: TrioMessage) -> TrioResponse:
        """Process message in parallel"""
        # For parallel processing, we can send to multiple systems
        await self.message_queue[message.target].put(message)

        # Return immediately with async tracking
        return TrioResponse(
            message_id=message.id,
            system=message.target,
            status="processing",
            result={"tracking_id": message.id},
            processing_time_ms=0,
        )

    async def _process_message_optimized(self, message: TrioMessage) -> TrioResponse:
        """Process message with optimization"""
        # Check cache first
        cache_key = f"{message.source.value}:{message.target.value}:{message.message_type}"
        if cache_key in self.performance_cache:
            cached_result = self.performance_cache[cache_key]
            if self._is_cache_valid(cached_result):
                return TrioResponse(
                    message_id=message.id,
                    system=message.target,
                    status="cached",
                    result=cached_result["result"],
                    processing_time_ms=0,
                )

        # Route based on priority
        if message.priority == MessagePriority.CRITICAL:
            # Process immediately
            return await self._process_message_sequential(message)
        else:
            # Use parallel processing
            return await self._process_message_parallel(message)

    def _would_create_circular_dependency(self, message: TrioMessage) -> bool:
        """Check if message would create circular dependency"""
        # Simple check - prevent A->B->A patterns
        for active_msg in self.active_messages.values():
            if active_msg.source == message.target and active_msg.target == message.source:
                return True
        return False

    async def _check_ethical_compliance(self, message: TrioMessage) -> dict[str, Any]:
        """Check if message complies with ethical guidelines"""
        action = {
            "type": f"trio_message_{message.message_type}",
            "source": message.source.value,
            "target": message.target.value,
            "payload": message.payload,
        }

        context = await self.context_manager.get_full_context()

        decision = await self.ethics_engine.evaluate_action(
            action, context, f"trio_orchestrator_{message.source.value}"
        )

        return {
            "decision": decision.decision_type,
            "reason": decision.reasoning,
            "confidence": decision.confidence,
        }

    async def _dependency_resolver(self) -> None:
        """Resolve dependencies between messages"""
        while self.is_running:
    def _detect_deadlocks(self) -> list[tuple[str, str]]:
        """Detect potential deadlocks"""
        deadlocks = []

        # Check for circular waits
        for msg_id1, msg1 in self.active_messages.items():
            for msg_id2, msg2 in self.active_messages.items():
                if msg_id1 != msg_id2 and msg1.source == msg2.target and msg1.target == msg2.source:
                    deadlocks.append((msg_id1, msg_id2))

        return deadlocks

    async def _resolve_deadlocks(self, deadlocks: list[tuple[str, str]]) -> None:
        """Resolve detected deadlocks"""
        for msg_id1, msg_id2 in deadlocks:
            logger.warning(f"Resolving deadlock between {msg_id1} and {msg_id2}")

            # Cancel lower priority message
            msg1 = self.active_messages.get(msg_id1)
            msg2 = self.active_messages.get(msg_id2)

            if msg1 and msg2:
                if msg1.priority.value < msg2.priority.value:
                    self.active_messages.pop(msg_id1, None)
                else:
                    self.active_messages.pop(msg_id2, None)

    async def _optimize_message_flow(self) -> None:
        """Optimize message flow based on patterns"""
        # Collect performance metrics
        for system in SystemType:
            queue_size = self.message_queue[system].qsize()
            if queue_size > 10:
                logger.warning(f"High queue size for {system.value}: {queue_size}")

                # Consider switching to parallel processing
                if self.processing_mode == ProcessingMode.SEQUENTIAL:
                    self.processing_mode = ProcessingMode.PARALLEL
                    logger.info("Switched to PARALLEL processing due to high load")

    def _generate_message_id(self) -> str:
        """Generate unique message ID"""

        return str(uuid.uuid4())

    def _is_cache_valid(self, cached_result: dict[str, Any]) -> bool:
        """Check if cached result is still valid"""
        if "timestamp" not in cached_result:
            return False

        age_seconds = (datetime.now(timezone.utc) - cached_result["timestamp"]).total_seconds()
        return age_seconds < 60  # 1 minute cache

    async def get_system_status(self) -> dict[str, Any]:
        """Get status of all systems"""
        context = await self.context_manager.get_full_context()

        return {
            "orchestrator": {
                "processing_mode": self.processing_mode.name,
                "active_messages": len(self.active_messages),
                "is_running": self.is_running,
            },
            "systems": context["system_state"],
            "queues": {system.value: self.message_queue[system].qsize() for system in SystemType},
            "context_version": await self.context_manager.get_version(),
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "systems_registered": len(self.system_handlers),
            "active_messages": len(self.active_messages),
            "processing_tasks": len(self.processing_tasks),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Additional methods for DAST/ABAS/NIAS integration
    async def register_component(self, component_name: str, component_instance: Any) -> None:
        """Register a component (hub) with the orchestrator"""
        # Determine system type from component name
        if "dast" in component_name.lower():
            system_type = SystemType.DAST
        elif "abas" in component_name.lower():
            system_type = SystemType.ABAS
        elif "nias" in component_name.lower():
            system_type = SystemType.NIAS
        else:
            logger.warning(f"Unknown component type: {component_name}")
            return

        # Register as system handler
        self.register_system_handler(system_type, component_instance)
        logger.info(f"Registered component {component_name} as {system_type.value} handler")

    async def notify_task_created(self, system: str, task_id: str, task_data: dict[str, Any]) -> None:
        """Notify orchestrator of task creation"""
        # Update context with new task
        await self.context_manager.set(
            f"system_state.{system}.active_tasks",
            await self.context_manager.get(f"system_state.{system}.active_tasks", []) + [task_id],
        )

        # Log event
        logger.info(f"Task created in {system}: {task_id}")

        # Store task metadata
        self.performance_cache[f"task_{task_id}"] = {
            "system": system,
            "created_at": datetime.now(timezone.utc),
            "data": task_data,
            "status": "created",
        }

    async def notify_task_completed(self, system: str, task_id: str, result: dict[str, Any]) -> None:
        """Notify orchestrator of task completion"""
        # Update context
        active_tasks = await self.context_manager.get(f"system_state.{system}.active_tasks", [])
        if task_id in active_tasks:
            active_tasks.remove(task_id)
            await self.context_manager.set(f"system_state.{system}.active_tasks", active_tasks)

        # Update task metadata
        if f"task_{task_id}" in self.performance_cache:
            self.performance_cache[f"task_{task_id}"].update(
                {
                    "completed_at": datetime.now(timezone.utc),
                    "status": "completed",
                    "result": result,
                }
            )

        logger.info(f"Task completed in {system}: {task_id}")

    async def notify_task_failed(self, system: str, task_id: str, error: str) -> None:
        """Notify orchestrator of task failure"""
        # Update context
        active_tasks = await self.context_manager.get(f"system_state.{system}.active_tasks", [])
        if task_id in active_tasks:
            active_tasks.remove(task_id)
            await self.context_manager.set(f"system_state.{system}.active_tasks", active_tasks)

        # Update task metadata
        if f"task_{task_id}" in self.performance_cache:
            self.performance_cache[f"task_{task_id}"].update(
                {
                    "failed_at": datetime.now(timezone.utc),
                    "status": "failed",
                    "error": error,
                }
            )

        logger.error(f"Task failed in {system}: {task_id} - {error}")

    async def process_audit_event(self, audit_entry: Any) -> None:
        """Process audit event from decision audit system"""
        # Store audit event in context
        audit_events = await self.context_manager.get("audit_events", [])
        audit_events.append(
            {
                "audit_id": getattr(audit_entry, "audit_id", "unknown"),
                "decision_id": getattr(audit_entry, "decision_id", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "decision_audit",
            }
        )

        # Keep only last 100 audit events
        if len(audit_events) > 100:
            audit_events = audit_events[-100:]

        await self.context_manager.set("audit_events", audit_events)
        logger.info(f"Processed audit event: {getattr(audit_entry, 'audit_id', 'unknown')}")


# Global instance
_trio_orchestrator_instance = None


def get_trio_orchestrator() -> TrioOrchestrator:
    """Get or create TrioOrchestrator instance"""
    global _trio_orchestrator_instance
    if _trio_orchestrator_instance is None:
        _trio_orchestrator_instance = TrioOrchestrator()
    return _trio_orchestrator_instance


__all__ = [
    "MessagePriority",
    "ProcessingMode",
    "SharedContextManager",
    "SystemType",
    "TrioMessage",
    "TrioOrchestrator",
    "TrioResponse",
    "get_trio_orchestrator",
]
