#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - BASE MEMORY COLONY
║ Foundation class for specialized memory processing colonies
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: base_memory_colony.py
║ Path: memory/colonies/base_memory_colony.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Colony Architecture Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the distributed symphony of mind, each colony is both musician and     │
║ │ conductor, specialized yet harmonious. Like cells in a living organism,   │
║ │ each colony carries the DNA of memory processing while expressing its     │
║ │ unique function. Together, they form not just a system, but an ecosystem. │
║ │                                                                            │
║ │ The base colony provides the common language, the shared protocols that   │
║ │ allow episodic urgency to converse with semantic patience, emotional      │
║ │ resonance to collaborate with working memory's rapid fire. This is the    │
║ │ foundation upon which memory's democracy is built.                        │
║ │                                                                            │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Standardized colony interface
║ • Memory type specialization
║ • Inter-colony communication
║ • Consensus participation
║ • Health monitoring
║ • Load balancing
║ • Fault tolerance
║ • Performance metrics
║
║ ΛTAG: ΛCOLONY, ΛBASE, ΛMEMORY, ΛDISTRIBUTED, ΛSPECIALIZATION
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

# Import memory components
try:
    from ..core.colony_memory_validator import ValidationMode
    from ..core.interfaces import (
        MemoryOperation,
        MemoryResponse,
        MemoryType,
        ValidationResult,
    )

    INTERFACES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Memory interfaces not available: {e}")
    INTERFACES_AVAILABLE = False

    # Stubs for development
    class MemoryType(Enum):
        EPISODIC = "episodic"
        SEMANTIC = "semantic"

    ValidationResult = object
    ValidationMode = object


class ColonyRole(Enum):
    """Roles that colonies can play in the memory system"""

    SPECIALIST = "specialist"  # Specialized in specific memory type
    VALIDATOR = "validator"  # Focuses on validation operations
    ARBITER = "arbiter"  # Resolves conflicts between colonies
    BACKUP = "backup"  # Provides redundancy
    MONITOR = "monitor"  # Observes and reports system health


class ColonyState(Enum):
    """Operational states of a colony"""

    INITIALIZING = "initializing"  # Starting up
    ACTIVE = "active"  # Fully operational
    BUSY = "busy"  # At capacity, accepting limited requests
    DEGRADED = "degraded"  # Operating with reduced capacity
    MAINTENANCE = "maintenance"  # Undergoing maintenance
    OFFLINE = "offline"  # Not accepting requests


@dataclass
class ColonyCapabilities:
    """Capabilities and limits of a colony"""

    max_concurrent_operations: int = 100
    supported_memory_types: set[MemoryType] = field(default_factory=set)
    supported_operations: set[str] = field(default_factory=set)

    # Performance characteristics
    average_response_time_ms: float = 100.0
    throughput_ops_per_second: float = 10.0
    memory_capacity_mb: float = 1024.0

    # Reliability metrics
    uptime_percentage: float = 99.0
    error_rate_percentage: float = 1.0

    # Specialization strength (0-1)
    specialization_confidence: float = 0.8


@dataclass
class ColonyMetrics:
    """Real-time metrics for colony performance"""

    colony_id: str

    # Operational metrics
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    active_operations: int = 0

    # Performance metrics
    average_response_time_ms: float = 0.0
    current_load_percentage: float = 0.0
    memory_usage_mb: float = 0.0

    # Health metrics
    last_heartbeat: float = field(default_factory=time.time)
    consecutive_failures: int = 0

    # Consensus participation
    consensus_votes: int = 0
    consensus_accuracy: float = 1.0

    def calculate_health_score(self) -> float:
        """Calculate overall health score (0-1)"""
        # Success rate component
        success_rate = self.successful_operations / max(self.total_operations, 1)

        # Load component (optimal around 70%)
        load_factor = 1.0 - abs(0.7 - self.current_load_percentage / 100.0)

        # Reliability component
        reliability = max(0.0, 1.0 - self.consecutive_failures / 10.0)

        # Recency component
        recency = max(0.0, 1.0 - (time.time() - self.last_heartbeat) / 300.0)  # 5 min decay

        return success_rate * 0.3 + load_factor * 0.2 + reliability * 0.3 + recency * 0.2


class BaseMemoryColony(ABC):
    """
    Abstract base class for all specialized memory colonies.
    Provides common functionality for distributed memory processing.
    """

    def __init__(
        self,
        colony_id: str,
        colony_role: ColonyRole,
        specialized_memory_types: list[MemoryType],
        capabilities: Optional[ColonyCapabilities] = None,
    ):
        self.colony_id = colony_id
        self.colony_role = colony_role
        self.specialized_memory_types = set(specialized_memory_types)
        self.capabilities = capabilities or ColonyCapabilities(supported_memory_types=set(specialized_memory_types))

        # State management
        self.state = ColonyState.INITIALIZING
        self.metrics = ColonyMetrics(colony_id=colony_id)

        # Operation management
        self.active_operations: dict[str, MemoryOperation] = {}
        self.operation_queue: deque = deque()
        self.operation_history: list[dict[str, Any]] = []

        # Communication
        self.peer_colonies: dict[str, BaseMemoryColony] = {}
        self.message_callbacks: list[Callable] = []

        # Memory storage (each subclass implements differently)
        self.local_storage: dict[str, Any] = {}

        # Background tasks
        self._running = False
        self._heartbeat_task = None
        self._processing_task = None
        self._maintenance_task = None

        logger.info(
            f"{self.colony_role.value.title()} memory colony initialized",
            colony_id=colony_id,
            specialized_types=[t.value for t in specialized_memory_types],
        )

    async def start(self):
        """Start the colony and its background processes"""
        self._running = True
        self.state = ColonyState.ACTIVE

        # Start specialized subsystems
        await self._initialize_specialized_systems()

        # Start background tasks
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._processing_task = asyncio.create_task(self._operation_processing_loop())
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())

        logger.info(f"Colony {self.colony_id} started")

    async def stop(self):
        """Stop the colony gracefully"""
        self._running = False
        self.state = ColonyState.OFFLINE

        # Cancel background tasks
        for task in [
            self._heartbeat_task,
            self._processing_task,
            self._maintenance_task,
        ]:
            if task:
                task.cancel()

        # Complete active operations
        await self._complete_active_operations()

        # Cleanup specialized systems
        await self._cleanup_specialized_systems()

        logger.info(
            f"Colony {self.colony_id} stopped",
            total_operations=self.metrics.total_operations,
            success_rate=self.metrics.successful_operations / max(self.metrics.total_operations, 1),
        )

    async def process_memory_operation(self, operation: MemoryOperation) -> MemoryResponse:
        """Process a memory operation according to colony specialization"""

        # Check if colony can handle this operation
        if not self._can_handle_operation(operation):
            return MemoryResponse(
                operation_id=operation.operation_id,
                success=False,
                error_message=f"Colony {self.colony_id} cannot handle this operation type",
            )

        # Check capacity
        if len(self.active_operations) >= self.capabilities.max_concurrent_operations:
            return MemoryResponse(
                operation_id=operation.operation_id,
                success=False,
                error_message="Colony at capacity, try again later",
            )

        # Track operation
        self.active_operations[operation.operation_id] = operation
        self.metrics.active_operations = len(self.active_operations)

        start_time = time.time()

        try:
            # Delegate to specialized processing
            response = await self._process_specialized_operation(operation)

            # Update metrics
            response_time = (time.time() - start_time) * 1000
            self.metrics.total_operations += 1

            if response.success:
                self.metrics.successful_operations += 1
                self.metrics.consecutive_failures = 0
            else:
                self.metrics.failed_operations += 1
                self.metrics.consecutive_failures += 1

            # Update average response time
            self._update_response_time(response_time)

            # Record operation in history
            self.operation_history.append(
                {
                    "operation_id": operation.operation_id,
                    "operation_type": operation.operation_type,
                    "success": response.success,
                    "response_time_ms": response_time,
                    "timestamp": time.time(),
                }
            )

            # Keep history limited
            if len(self.operation_history) > 1000:
                self.operation_history.pop(0)

            response.responding_colony = self.colony_id
            response.execution_time_ms = response_time

            return response

        except Exception as e:
            self.metrics.failed_operations += 1
            self.metrics.consecutive_failures += 1

            logger.error(
                f"Colony {self.colony_id} operation failed",
                operation_id=operation.operation_id,
                error=str(e),
            )

            return MemoryResponse(
                operation_id=operation.operation_id,
                success=False,
                error_message=str(e),
                responding_colony=self.colony_id,
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        finally:
            # Remove from active operations
            self.active_operations.pop(operation.operation_id, None)
            self.metrics.active_operations = len(self.active_operations)

    async def participate_in_consensus(self, consensus_request: dict[str, Any]) -> dict[str, Any]:
        """Participate in inter-colony consensus"""

        self.metrics.consensus_votes += 1

        # Delegate to specialized consensus logic
        try:
            vote = await self._cast_consensus_vote(consensus_request)

            # Track accuracy if outcome is known
            if "expected_outcome" in consensus_request:
                expected = consensus_request["expected_outcome"]
                if vote.get("decision") == expected:
                    # Update running accuracy
                    current_accuracy = self.metrics.consensus_accuracy
                    self.metrics.consensus_accuracy = current_accuracy * 0.9 + 1.0 * 0.1
                else:
                    self.metrics.consensus_accuracy = current_accuracy * 0.9 + 0.0 * 0.1

            return vote

        except Exception as e:
            logger.error(f"Consensus participation failed: {e}")
            return {
                "colony_id": self.colony_id,
                "decision": "abstain",
                "confidence": 0.0,
                "error": str(e),
            }

    def register_peer_colony(self, colony: "BaseMemoryColony"):
        """Register a peer colony for communication"""
        self.peer_colonies[colony.colony_id] = colony
        logger.debug(f"Colony {self.colony_id} registered peer: {colony.colony_id}")

    def register_message_callback(self, callback: Callable):
        """Register callback for inter-colony messages"""
        self.message_callbacks.append(callback)

    async def send_message_to_colony(self, target_colony_id: str, message: dict[str, Any]) -> bool:
        """Send message to another colony"""
        if target_colony_id not in self.peer_colonies:
            return False

        target_colony = self.peer_colonies[target_colony_id]
        message["sender_colony_id"] = self.colony_id
        message["timestamp"] = time.time()

        try:
            await target_colony._receive_message(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {target_colony_id}: {e}")
            return False

    async def _receive_message(self, message: dict[str, Any]):
        """Receive message from another colony"""
        for callback in self.message_callbacks:
            try:
                await callback(message)
            except Exception as e:
                logger.error(f"Message callback failed: {e}")

    def get_health_status(self) -> dict[str, Any]:
        """Get current health and status information"""
        return {
            "colony_id": self.colony_id,
            "role": self.colony_role.value,
            "state": self.state.value,
            "health_score": self.metrics.calculate_health_score(),
            "specialized_types": [t.value for t in self.specialized_memory_types],
            "metrics": {
                "total_operations": self.metrics.total_operations,
                "success_rate": (self.metrics.successful_operations / max(self.metrics.total_operations, 1)),
                "active_operations": self.metrics.active_operations,
                "current_load": self.metrics.current_load_percentage,
                "average_response_time_ms": self.metrics.average_response_time_ms,
                "consecutive_failures": self.metrics.consecutive_failures,
            },
            "capabilities": {
                "max_concurrent": self.capabilities.max_concurrent_operations,
                "supported_types": [t.value for t in self.capabilities.supported_memory_types],
                "specialization_confidence": self.capabilities.specialization_confidence,
            },
        }

    # Abstract methods that subclasses must implement

    @abstractmethod
    async def _initialize_specialized_systems(self):
        """Initialize systems specific to colony type"""

    @abstractmethod
    async def _cleanup_specialized_systems(self):
        """Cleanup systems specific to colony type"""

    @abstractmethod
    async def _process_specialized_operation(self, operation: MemoryOperation) -> MemoryResponse:
        """Process operation according to colony specialization"""

    @abstractmethod
    async def _cast_consensus_vote(self, consensus_request: dict[str, Any]) -> dict[str, Any]:
        """Cast vote in inter-colony consensus"""

    # Helper methods

    def _can_handle_operation(self, operation: MemoryOperation) -> bool:
        """Check if colony can handle the given operation"""

        # Check if operation type is supported
        if (
            operation.operation_type not in self.capabilities.supported_operations
            and len(self.capabilities.supported_operations) > 0
        ):
            return False

        # Check memory type compatibility
        if operation.metadata and hasattr(operation.metadata, "memory_type"):
            memory_type = operation.metadata.memory_type
            if (
                memory_type not in self.capabilities.supported_memory_types
                and len(self.capabilities.supported_memory_types) > 0
            ):
                return False

        # Check current state
        return self.state in [ColonyState.ACTIVE, ColonyState.BUSY]

    def _update_response_time(self, response_time_ms: float):
        """Update running average of response time"""
        current_avg = self.metrics.average_response_time_ms
        if current_avg == 0.0:
            self.metrics.average_response_time_ms = response_time_ms
        else:
            # Exponential moving average
            self.metrics.average_response_time_ms = current_avg * 0.9 + response_time_ms * 0.1

    async def _complete_active_operations(self):
        """Complete or cancel active operations during shutdown"""
        timeout = 10.0  # 10 second timeout for graceful completion

        if not self.active_operations:
            return

        logger.info(f"Colony {self.colony_id} completing {len(self.active_operations)} active operations")

        try:
            await asyncio.wait_for(
                asyncio.gather(
                    *[self._cancel_operation(op_id) for op_id in list(self.active_operations.keys())],
                    return_exceptions=True,
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(f"Colony {self.colony_id} timed out completing operations")

    async def _cancel_operation(self, operation_id: str):
        """Cancel a specific operation"""
        # Implementation depends on specific colony type
        self.active_operations.pop(operation_id, None)

    # Background tasks

    async def _heartbeat_loop(self):
        """Send periodic heartbeat and update metrics"""
        while self._running:
            self.metrics.last_heartbeat = time.time()

            # Update load percentage
            current_load = len(self.active_operations) / self.capabilities.max_concurrent_operations * 100
            self.metrics.current_load_percentage = current_load

            # Adjust state based on load
            if current_load > 90:
                self.state = ColonyState.BUSY
            elif current_load > 50:
                self.state = ColonyState.ACTIVE
            else:
                self.state = ColonyState.ACTIVE

            await asyncio.sleep(5.0)  # Heartbeat every 5 seconds

    async def _operation_processing_loop(self):
        """Process queued operations"""
        while self._running:
            if self.operation_queue and len(self.active_operations) < self.capabilities.max_concurrent_operations:
                operation = self.operation_queue.popleft()
                asyncio.create_task(self.process_memory_operation(operation))

            await asyncio.sleep(0.1)  # Check queue frequently

    async def _maintenance_loop(self):
        """Perform periodic maintenance tasks"""
        while self._running:
            # Cleanup old history
            if len(self.operation_history) > 1000:
                self.operation_history = self.operation_history[-500:]

            # Reset consecutive failures if recent success
            if (
                self.metrics.consecutive_failures > 0
                and self.operation_history
                and self.operation_history[-1].get("success", False)
            ):
                self.metrics.consecutive_failures = max(0, self.metrics.consecutive_failures - 1)

            await asyncio.sleep(60.0)  # Maintenance every minute