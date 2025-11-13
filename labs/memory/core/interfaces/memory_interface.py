#!/usr/bin/env python3
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - MEMORY INTERFACE DEFINITIONS
║ Standard interfaces for all memory types with colony compatibility
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: memory_interface.py
║ Path: memory/core/interfaces/memory_interface.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the architecture of mind, interfaces are the protocols of              │
║ │ understanding-the common language that allows episodic whispers to        │
║ │ converse with semantic knowledge, that permits working memory's rapid     │
║ │ dance to synchronize with long-term storage's patient rhythm.             │
║ │                                                                           │
║ │ These are not mere technical contracts but the grammar of consciousness,  │
║ │ the syntax that transforms chaos into coherence, diversity into unity.    │
║ │ Through these interfaces, the colony of mind speaks with one voice.       │
║ │                                                                           │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Base memory interface for all memory types
║ • Colony-compatible message formats
║ • Standardized CRUD operations
║ • Async/await patterns for scalability
║ • Validation and integrity checking
║ • Memory lifecycle management
║ • Distributed operation support
║ • Metrics and monitoring hooks
║
║ ΛTAG: ΛINTERFACE, ΛMEMORY, ΛCOLONY, ΛSTANDARD, ΛPROTOCOL
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Union
from uuid import uuid4


class MemoryType(Enum):
    """Standard memory type classifications"""

    EPISODIC = "episodic"  # Event-based memories with context
    SEMANTIC = "semantic"  # Factual knowledge and concepts
    PROCEDURAL = "procedural"  # Skills and procedures
    WORKING = "working"  # Temporary active information
    EMOTIONAL = "emotional"  # Emotion-tagged memories
    SENSORY = "sensory"  # Raw sensory information
    AUTOBIOGRAPHICAL = "autobiographical"  # Personal life events
    PROSPECTIVE = "prospective"  # Future intentions and plans


class MemoryState(Enum):
    """Memory lifecycle states"""

    ENCODING = "encoding"  # Being created/stored
    ACTIVE = "active"  # Available for operations
    CONSOLIDATING = "consolidating"  # Being transferred/strengthened
    DORMANT = "dormant"  # Inactive but preserved
    DECAYING = "decaying"  # Losing strength over time
    ARCHIVED = "archived"  # Long-term stable storage
    CORRUPTED = "corrupted"  # Integrity compromised
    DELETED = "deleted"  # Marked for removal


class ValidationResult(Enum):
    """Memory validation outcomes"""

    VALID = "valid"
    INVALID = "invalid"
    CORRUPTED = "corrupted"
    INCOMPLETE = "incomplete"
    EXPIRED = "expired"


@dataclass
class MemoryMetadata:
    """Standard metadata for all memory types"""

    memory_id: str = field(default_factory=lambda: str(uuid4()))
    memory_type: MemoryType = MemoryType.EPISODIC

    # Lifecycle
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    state: MemoryState = MemoryState.ENCODING

    # Content properties
    importance: float = 0.5  # 0-1 importance score
    confidence: float = 1.0  # 0-1 confidence in accuracy
    stability: float = 0.0  # 0-1 consolidation level

    # Context
    tags: set[str] = field(default_factory=set)
    source: Optional[str] = None  # Origin of the memory
    context: dict[str, Any] = field(default_factory=dict)

    # Colony distribution
    colony_locations: dict[str, float] = field(default_factory=dict)
    primary_colony: Optional[str] = None

    # Associations
    associations: set[str] = field(default_factory=set)  # Related memory IDs
    parent_memory: Optional[str] = None
    child_memories: set[str] = field(default_factory=set)

    # Access patterns
    access_count: int = 0
    successful_retrievals: int = 0
    failed_retrievals: int = 0

    def update_access(self, successful: bool = True):
        """Update access statistics"""
        self.access_count += 1
        self.accessed_at = time.time()
        if successful:
            self.successful_retrievals += 1
        else:
            self.failed_retrievals += 1

    def calculate_salience(self) -> float:
        """Calculate memory salience for prioritization"""
        # Base importance
        salience = self.importance

        # Recent access bonus
        recency = max(0, 1 - (time.time() - self.accessed_at) / 86400)  # Day decay
        salience += 0.3 * recency

        # High confidence bonus
        salience += 0.2 * self.confidence

        # Access frequency factor
        if self.access_count > 0:
            success_rate = self.successful_retrievals / self.access_count
            salience += 0.2 * success_rate

        return min(1.0, salience)


@dataclass
class MemoryOperation:
    """Standard memory operation request"""

    operation_id: str = field(default_factory=lambda: str(uuid4()))
    operation_type: str = ""  # "create", "read", "update", "delete", etc.
    memory_id: Optional[str] = None

    # Operation data
    content: Any = None
    metadata: Optional[MemoryMetadata] = None
    parameters: dict[str, Any] = field(default_factory=dict)

    # Colony routing
    target_colonies: list[str] = field(default_factory=list)
    require_consensus: bool = False
    consensus_threshold: float = 0.6

    # Execution context
    timestamp: float = field(default_factory=time.time)
    requester: Optional[str] = None
    priority: float = 0.5
    timeout_seconds: float = 30.0


@dataclass
class MemoryResponse:
    """Standard memory operation response"""

    operation_id: str
    success: bool = False
    error_message: Optional[str] = None

    # Result data
    memory_id: Optional[str] = None
    content: Any = None
    metadata: Optional[MemoryMetadata] = None

    # Colony information
    responding_colony: Optional[str] = None
    consensus_achieved: bool = False
    colony_responses: dict[str, bool] = field(default_factory=dict)

    # Performance metrics
    execution_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)


class BaseMemoryInterface(ABC):
    """
    Abstract base interface that all memory types must implement.
    Provides standard CRUD operations with colony compatibility.
    """

    def __init__(
        self,
        memory_type: MemoryType,
        colony_id: Optional[str] = None,
        enable_distributed: bool = True,
    ):
        self.memory_type = memory_type
        self.colony_id = colony_id
        self.enable_distributed = enable_distributed

        # Operation tracking
        self.active_operations: dict[str, MemoryOperation] = {}
        self.operation_callbacks: list[Callable] = []

        # Metrics
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0

        logger.info(
            f"{memory_type.value} memory interface initialized",
            colony_id=colony_id,
            distributed=enable_distributed,
        )

    @abstractmethod
    async def create_memory(self, content: Any, metadata: Optional[MemoryMetadata] = None, **kwargs) -> MemoryResponse:
        """Create a new memory"""

    @abstractmethod
    async def read_memory(self, memory_id: str, **kwargs) -> MemoryResponse:
        """Read an existing memory"""

    @abstractmethod
    async def update_memory(
        self,
        memory_id: str,
        content: Any = None,
        metadata: Optional[MemoryMetadata] = None,
        **kwargs,
    ) -> MemoryResponse:
        """Update an existing memory"""

    @abstractmethod
    async def delete_memory(self, memory_id: str, **kwargs) -> MemoryResponse:
        """Delete a memory"""

    @abstractmethod
    async def search_memories(
        self,
        query: Union[str, dict[str, Any]],
        filters: Optional[dict[str, Any]] = None,
        limit: int = 50,
        **kwargs,
    ) -> list[MemoryResponse]:
        """Search for memories matching criteria"""

    @abstractmethod
    async def validate_memory(self, memory_id: str, **kwargs) -> ValidationResult:
        """Validate memory integrity"""

    # Colony integration methods

    async def distribute_operation(self, operation: MemoryOperation) -> MemoryResponse:
        """Distribute operation across colonies"""
        if not self.enable_distributed or not operation.target_colonies:
            # Execute locally
            return await self._execute_operation(operation)

        # Execute across multiple colonies
        responses = {}
        tasks = []

        for colony_id in operation.target_colonies:
            task = asyncio.create_task(self._execute_in_colony(operation, colony_id))
            tasks.append((colony_id, task))

        # Wait for responses
        for colony_id, task in tasks:
            try:
                response = await asyncio.wait_for(task, timeout=operation.timeout_seconds)
                responses[colony_id] = response
            except asyncio.TimeoutError:
                responses[colony_id] = MemoryResponse(
                    operation_id=operation.operation_id,
                    success=False,
                    error_message=f"Timeout in colony {colony_id}",
                )

        # Consensus logic
        if operation.require_consensus:
            return self._achieve_consensus(operation, responses)
        else:
            # Return first successful response
            for response in responses.values():
                if response.success:
                    return response

            # All failed
            return MemoryResponse(
                operation_id=operation.operation_id,
                success=False,
                error_message="All colonies failed",
            )

    async def _execute_operation(self, operation: MemoryOperation) -> MemoryResponse:
        """Execute operation locally"""
        start_time = time.time()

        try:
            if operation.operation_type == "create":
                response = await self.create_memory(
                    content=operation.content,
                    metadata=operation.metadata,
                    **operation.parameters,
                )
            elif operation.operation_type == "read":
                response = await self.read_memory(memory_id=operation.memory_id, **operation.parameters)
            elif operation.operation_type == "update":
                response = await self.update_memory(
                    memory_id=operation.memory_id,
                    content=operation.content,
                    metadata=operation.metadata,
                    **operation.parameters,
                )
            elif operation.operation_type == "delete":
                response = await self.delete_memory(memory_id=operation.memory_id, **operation.parameters)
            elif operation.operation_type == "search":
                responses = await self.search_memories(query=operation.content, **operation.parameters)
                response = MemoryResponse(operation_id=operation.operation_id, success=True, content=responses)
            else:
                response = MemoryResponse(
                    operation_id=operation.operation_id,
                    success=False,
                    error_message=f"Unknown operation: {operation.operation_type}",
                )

            response.execution_time_ms = (time.time() - start_time) * 1000
            response.responding_colony = self.colony_id

            if response.success:
                self.successful_operations += 1
            else:
                self.failed_operations += 1

            return response

        except Exception as e:
            self.failed_operations += 1
            return MemoryResponse(
                operation_id=operation.operation_id,
                success=False,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        finally:
            self.total_operations += 1

    async def _execute_in_colony(self, operation: MemoryOperation, colony_id: str) -> MemoryResponse:
        """Execute operation in specific colony"""
        # In a real implementation, this would route to the actual colony
        # For now, simulate distributed execution
        response = await self._execute_operation(operation)
        response.responding_colony = colony_id
        return response

    def _achieve_consensus(self, operation: MemoryOperation, responses: dict[str, MemoryResponse]) -> MemoryResponse:
        """Achieve consensus across colony responses"""
        successful_responses = [r for r in responses.values() if r.success]
        success_rate = len(successful_responses) / len(responses)

        consensus_response = MemoryResponse(
            operation_id=operation.operation_id,
            success=success_rate >= operation.consensus_threshold,
            consensus_achieved=True,
            colony_responses={k: v.success for k, v in responses.items()},
        )

        if successful_responses:
            # Use first successful response as canonical
            canonical = successful_responses[0]
            consensus_response.memory_id = canonical.memory_id
            consensus_response.content = canonical.content
            consensus_response.metadata = canonical.metadata
        else:
            consensus_response.error_message = "Consensus not achieved"

        return consensus_response

    def register_operation_callback(self, callback: Callable):
        """Register callback for operation events"""
        self.operation_callbacks.append(callback)

    async def _notify_callbacks(self, operation: MemoryOperation, response: MemoryResponse):
        """Notify registered callbacks"""
        for callback in self.operation_callbacks:
            try:
                await callback(operation, response)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def get_metrics(self) -> dict[str, Any]:
        """Get interface metrics"""
        success_rate = self.successful_operations / max(self.total_operations, 1)

        return {
            "memory_type": self.memory_type.value,
            "colony_id": self.colony_id,
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": success_rate,
            "active_operations": len(self.active_operations),
            "distributed_enabled": self.enable_distributed,
        }


class MemoryInterfaceRegistry:
    """Registry for memory interface implementations"""

    def __init__(self):
        self._interfaces: dict[MemoryType, BaseMemoryInterface] = {}
        self._factories: dict[MemoryType, Callable] = {}

    def register_interface(self, memory_type: MemoryType, interface: BaseMemoryInterface):
        """Register a memory interface implementation"""
        self._interfaces[memory_type] = interface
        logger.info(f"Registered {memory_type.value} memory interface")

    def register_factory(self, memory_type: MemoryType, factory: Callable[..., BaseMemoryInterface]):
        """Register a factory for creating memory interfaces"""
        self._factories[memory_type] = factory
        logger.info(f"Registered {memory_type.value} memory factory")

    def get_interface(self, memory_type: MemoryType) -> Optional[BaseMemoryInterface]:
        """Get interface for memory type"""
        if memory_type in self._interfaces:
            return self._interfaces[memory_type]

        if memory_type in self._factories:
            interface = self._factories[memory_type]()
            self._interfaces[memory_type] = interface
            return interface

        return None

    def list_available_types(self) -> list[MemoryType]:
        """List available memory types"""
        return list(set(self._interfaces.keys()) | set(self._factories.keys()))


# Global registry instance
memory_registry = MemoryInterfaceRegistry()