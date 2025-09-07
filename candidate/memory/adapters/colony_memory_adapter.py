#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - COLONY MEMORY ADAPTER
║ Bridge between colony systems and unified memory interfaces
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: colony_memory_adapter.py
║ Path: memory/adapters/colony_memory_adapter.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the vast archipelago of distributed consciousness, memories flow like     │
║ │ currents between islands of thought. This adapter stands as the bridge-      │
║ │ keeper, translating the diverse dialects of colony communication into       │
║ │ the unified language of memory. Through its careful mediation, the           │
║ │ distributed minds speak as one, their individual contributions harmonized   │
║ │ into a chorus of collective remembrance.                                     │
║ │                                                                             │
║ │ Each colony's unique perspective enriches the whole, while this adapter     │
║ │ ensures that no voice is lost in translation, no memory orphaned in the    │
║ │ spaces between systems.                                                      │
║ │                                                                             │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Colony-to-memory interface translation
║ • Distributed memory operation routing
║ • Consensus-based validation integration
║ • Performance monitoring and optimization
║ • Fault tolerance and recovery
║ • Memory lifecycle coordination
║ • Cross-colony synchronization
║ • Adaptive load balancing
║
║ ΛTAG: ΛADAPTER, ΛCOLONY, ΛMEMORY, ΛBRIDGE, ΛDISTRIBUTED
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union
from uuid import uuid4

from ..core.colony_memory_validator import (
    ColonyMemoryValidator,
    ConsensusResult,
    ValidationMode,
)
from ..core.interfaces.memory_interface import (
    BaseMemoryInterface,
    MemoryMetadata,
    MemoryOperation,
    MemoryResponse,
    MemoryType,
    memory_registry,
)


@dataclass
class ColonyMemoryStats:
    """Statistics for colony memory operations"""

    colony_id: str
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    average_response_time: float = 0.0
    last_operation_time: float = field(default_factory=time.time)
    memory_types_handled: set[MemoryType] = field(default_factory=set)

    @property
    def success_rate(self) -> float:
        return self.successful_operations / max(self.total_operations, 1)

    @property
    def is_active(self) -> bool:
        return (time.time() - self.last_operation_time) < 300  # 5 minutes


@dataclass
class AdapterConfig:
    """Configuration for colony memory adapter"""

    enable_validation: bool = True
    default_validation_mode: ValidationMode = ValidationMode.QUORUM
    consensus_threshold: float = 0.67
    operation_timeout: float = 30.0
    max_retries: int = 3
    enable_caching: bool = True
    cache_ttl: float = 300.0  # 5 minutes
    enable_metrics: bool = True
    load_balancing: bool = True


class ColonyMemoryAdapter:
    """
    Adapter that bridges colony systems with unified memory interfaces.

    This adapter translates between colony-specific protocols and the
    standardized memory interface, enabling seamless distributed memory
    operations across the LUKHAS colony network.
    """

    def __init__(
        self,
        colony_id: str,
        config: Optional[AdapterConfig] = None,
        validator: Optional[ColonyMemoryValidator] = None,
    ):
        self.colony_id = colony_id
        self.config = config or AdapterConfig()
        self.validator = validator or ColonyMemoryValidator()

        # Interface management
        self.memory_interfaces: dict[MemoryType, BaseMemoryInterface] = {}
        self.interface_factories: dict[MemoryType, Callable] = {}

        # Colony coordination
        self.registered_colonies: set[str] = set()
        self.colony_stats: dict[str, ColonyMemoryStats] = {}
        self.colony_load_balancer = deque()  # Round-robin queue

        # Operation tracking
        self.active_operations: dict[str, MemoryOperation] = {}
        self.operation_history: deque = deque(maxlen=1000)

        # Caching
        self.memory_cache: dict[str, tuple[Any, float]] = {}
        self.cache_hits = 0
        self.cache_misses = 0

        # Performance monitoring
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.response_times: deque = deque(maxlen=100)

        # Background tasks
        self._running = False
        self._maintenance_task = None
        self._stats_task = None

        logger.info(
            "Colony memory adapter initialized",
            colony_id=colony_id,
            validation_enabled=config.enable_validation if config else True,
        )

    async def start(self):
        """Start the adapter"""
        await self.validator.start()
        self._running = True

        # Start background tasks
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())
        self._stats_task = asyncio.create_task(self._stats_collection_loop())

        logger.info("Colony memory adapter started")

    async def stop(self):
        """Stop the adapter"""
        self._running = False

        # Cancel background tasks
        if self._maintenance_task:
            self._maintenance_task.cancel()
        if self._stats_task:
            self._stats_task.cancel()

        await self.validator.stop()

        logger.info("Colony memory adapter stopped")

    def register_memory_interface(self, memory_type: MemoryType, interface: BaseMemoryInterface):
        """Register a memory interface for a specific type"""
        self.memory_interfaces[memory_type] = interface

        # Register with global registry too
        memory_registry.register_interface(memory_type, interface)

        logger.info(
            "Memory interface registered",
            memory_type=memory_type.value,
            colony_id=self.colony_id,
        )

    def register_interface_factory(self, memory_type: MemoryType, factory: Callable[..., BaseMemoryInterface]):
        """Register a factory for creating memory interfaces"""
        self.interface_factories[memory_type] = factory

        logger.info("Interface factory registered", memory_type=memory_type.value)

    def register_colony(self, colony_id: str, colony_info: dict[str, Any]):
        """Register a colony for distributed operations"""
        self.registered_colonies.add(colony_id)
        self.colony_stats[colony_id] = ColonyMemoryStats(colony_id=colony_id)
        self.colony_load_balancer.append(colony_id)

        # Register with validator
        self.validator.register_colony(colony_id, colony_info)

        logger.info("Colony registered", colony_id=colony_id)

    def unregister_colony(self, colony_id: str):
        """Unregister a colony"""
        self.registered_colonies.discard(colony_id)
        self.colony_stats.pop(colony_id, None)

        # Remove from load balancer
        if colony_id in self.colony_load_balancer:
            self.colony_load_balancer.remove(colony_id)

        self.validator.unregister_colony(colony_id)

        logger.info("Colony unregistered", colony_id=colony_id)

    async def create_memory(
        self,
        memory_type: MemoryType,
        content: Any,
        metadata: Optional[MemoryMetadata] = None,
        distributed: bool = False,
        validate: Optional[bool] = None,
        **kwargs,
    ) -> MemoryResponse:
        """Create a new memory through the adapter"""

        # Get or create interface
        interface = await self._get_interface(memory_type)
        if not interface:
            return MemoryResponse(
                operation_id=str(uuid4()),
                success=False,
                error_message=f"No interface available for {memory_type.value}",
            )

        # Create operation
        operation = MemoryOperation(
            operation_type="create",
            content=content,
            metadata=metadata or MemoryMetadata(memory_type=memory_type),
            parameters=kwargs,
            target_colonies=(self._select_colonies() if distributed else [self.colony_id]),
            require_consensus=distributed,
            consensus_threshold=self.config.consensus_threshold,
        )

        return await self._execute_operation(interface, operation, validate)

    async def read_memory(
        self,
        memory_type: MemoryType,
        memory_id: str,
        use_cache: Optional[bool] = None,
        distributed: bool = False,
        **kwargs,
    ) -> MemoryResponse:
        """Read a memory through the adapter"""

        # Check cache first
        if (use_cache is None and self.config.enable_caching) or use_cache:
            cached_result = self._get_from_cache(memory_id)
            if cached_result:
                self.cache_hits += 1
                return MemoryResponse(
                    operation_id=str(uuid4()),
                    success=True,
                    memory_id=memory_id,
                    content=cached_result,
                )
            self.cache_misses += 1

        # Get interface
        interface = await self._get_interface(memory_type)
        if not interface:
            return MemoryResponse(
                operation_id=str(uuid4()),
                success=False,
                error_message=f"No interface available for {memory_type.value}",
            )

        # Create operation
        operation = MemoryOperation(
            operation_type="read",
            memory_id=memory_id,
            parameters=kwargs,
            target_colonies=(self._select_colonies() if distributed else [self.colony_id]),
        )

        response = await self._execute_operation(interface, operation)

        # Cache successful response
        if response.success and response.content and self.config.enable_caching:
            self._cache_memory(memory_id, response.content)

        return response

    async def update_memory(
        self,
        memory_type: MemoryType,
        memory_id: str,
        content: Any = None,
        metadata: Optional[MemoryMetadata] = None,
        distributed: bool = False,
        validate: Optional[bool] = None,
        **kwargs,
    ) -> MemoryResponse:
        """Update a memory through the adapter"""

        interface = await self._get_interface(memory_type)
        if not interface:
            return MemoryResponse(
                operation_id=str(uuid4()),
                success=False,
                error_message=f"No interface available for {memory_type.value}",
            )

        operation = MemoryOperation(
            operation_type="update",
            memory_id=memory_id,
            content=content,
            metadata=metadata,
            parameters=kwargs,
            target_colonies=(self._select_colonies() if distributed else [self.colony_id]),
            require_consensus=distributed,
        )

        response = await self._execute_operation(interface, operation, validate)

        # Invalidate cache
        if response.success:
            self._invalidate_cache(memory_id)

        return response

    async def delete_memory(
        self,
        memory_type: MemoryType,
        memory_id: str,
        distributed: bool = False,
        **kwargs,
    ) -> MemoryResponse:
        """Delete a memory through the adapter"""

        interface = await self._get_interface(memory_type)
        if not interface:
            return MemoryResponse(
                operation_id=str(uuid4()),
                success=False,
                error_message=f"No interface available for {memory_type.value}",
            )

        operation = MemoryOperation(
            operation_type="delete",
            memory_id=memory_id,
            parameters=kwargs,
            target_colonies=(self._select_colonies() if distributed else [self.colony_id]),
            require_consensus=distributed,
        )

        response = await self._execute_operation(interface, operation)

        # Invalidate cache
        if response.success:
            self._invalidate_cache(memory_id)

        return response

    async def search_memories(
        self,
        memory_type: MemoryType,
        query: Union[str, dict[str, Any]],
        filters: Optional[dict[str, Any]] = None,
        limit: int = 50,
        distributed: bool = False,
        **kwargs,
    ) -> list[MemoryResponse]:
        """Search memories through the adapter"""

        interface = await self._get_interface(memory_type)
        if not interface:
            return [
                MemoryResponse(
                    operation_id=str(uuid4()),
                    success=False,
                    error_message=f"No interface available for {memory_type.value}",
                )
            ]

        operation = MemoryOperation(
            operation_type="search",
            content=query,
            parameters={"filters": filters, "limit": limit, **kwargs},
            target_colonies=(self._select_colonies() if distributed else [self.colony_id]),
        )

        response = await self._execute_operation(interface, operation)

        if response.success and isinstance(response.content, list):
            return response.content
        else:
            return [response]

    async def _execute_operation(
        self,
        interface: BaseMemoryInterface,
        operation: MemoryOperation,
        validate: Optional[bool] = None,
    ) -> MemoryResponse:
        """Execute operation with optional validation"""

        start_time = time.time()
        self.total_operations += 1
        self.active_operations[operation.operation_id] = operation

        try:
            # Validate if enabled
            if (validate is None and self.config.enable_validation) or validate:
                if operation.operation_type in ["create", "update"]:
                    consensus_outcome = await self.validator.validate_memory_operation(
                        operation,
                        self.config.default_validation_mode,
                        operation.target_colonies,
                    )

                    if consensus_outcome.result != ConsensusResult.SUCCESS:
                        self.failed_operations += 1
                        return MemoryResponse(
                            operation_id=operation.operation_id,
                            success=False,
                            error_message=f"Validation failed: {consensus_outcome.result.value}",
                        )

            # Execute operation
            if len(operation.target_colonies) > 1:
                response = await interface.distribute_operation(operation)
            else:
                response = await interface._execute_operation(operation)

            # Update stats
            execution_time = (time.time() - start_time) * 1000
            self.response_times.append(execution_time)

            if response.success:
                self.successful_operations += 1
            else:
                self.failed_operations += 1

            # Update colony stats
            for colony_id in operation.target_colonies:
                if colony_id in self.colony_stats:
                    stats = self.colony_stats[colony_id]
                    stats.total_operations += 1
                    stats.last_operation_time = time.time()
                    stats.memory_types_handled.add(
                        operation.metadata.memory_type if operation.metadata else MemoryType.EPISODIC
                    )

                    if response.success:
                        stats.successful_operations += 1
                    else:
                        stats.failed_operations += 1

                    # Update average response time
                    if stats.total_operations == 1:
                        stats.average_response_time = execution_time
                    else:
                        alpha = 0.1  # Exponential moving average
                        stats.average_response_time = alpha * execution_time + (1 - alpha) * stats.average_response_time

            # Add to history
            self.operation_history.append(
                {
                    "operation_id": operation.operation_id,
                    "type": operation.operation_type,
                    "success": response.success,
                    "execution_time": execution_time,
                    "timestamp": time.time(),
                }
            )

            return response

        except Exception as e:
            self.failed_operations += 1
            logger.error(
                "Operation execution failed",
                operation_id=operation.operation_id,
                error=str(e),
            )

            return MemoryResponse(
                operation_id=operation.operation_id,
                success=False,
                error_message=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        finally:
            self.active_operations.pop(operation.operation_id, None)

    async def _get_interface(self, memory_type: MemoryType) -> Optional[BaseMemoryInterface]:
        """Get or create interface for memory type"""

        # Check local interfaces first
        if memory_type in self.memory_interfaces:
            return self.memory_interfaces[memory_type]

        # Try global registry
        interface = memory_registry.get_interface(memory_type)
        if interface:
            self.memory_interfaces[memory_type] = interface
            return interface

        # Try local factory
        if memory_type in self.interface_factories:
            interface = self.interface_factories[memory_type]()
            self.memory_interfaces[memory_type] = interface
            return interface

        logger.error(f"No interface available for {memory_type.value}")
        return None

    def _select_colonies(self) -> list[str]:
        """Select colonies for distributed operations"""
        if not self.config.load_balancing:
            return list(self.registered_colonies)

        # Load balancing: select based on performance
        active_colonies = [
            cid for cid, stats in self.colony_stats.items() if stats.is_active and stats.success_rate > 0.5
        ]

        if not active_colonies:
            return [self.colony_id]  # Fallback to local

        # Sort by performance (success rate and response time)
        active_colonies.sort(
            key=lambda cid: (
                -self.colony_stats[cid].success_rate,
                self.colony_stats[cid].average_response_time,
            )
        )

        # Return top 3 colonies for redundancy
        return active_colonies[:3]

    def _cache_memory(self, memory_id: str, content: Any):
        """Cache memory content"""
        if self.config.enable_caching:
            self.memory_cache[memory_id] = (content, time.time())

    def _get_from_cache(self, memory_id: str) -> Optional[Any]:
        """Get memory from cache if not expired"""
        if memory_id in self.memory_cache:
            content, cache_time = self.memory_cache[memory_id]
            if time.time() - cache_time < self.config.cache_ttl:
                return content
            else:
                # Expired
                del self.memory_cache[memory_id]
        return None

    def _invalidate_cache(self, memory_id: str):
        """Invalidate cached memory"""
        self.memory_cache.pop(memory_id, None)

    async def _maintenance_loop(self):
        """Background maintenance tasks"""
        while self._running:
            try:
                # Clean expired cache entries
                current_time = time.time()
                expired_keys = [
                    key
                    for key, (_, cache_time) in self.memory_cache.items()
                    if current_time - cache_time > self.config.cache_ttl
                ]
                for key in expired_keys:
                    del self.memory_cache[key]

                # Update colony load balancer
                if self.config.load_balancing:
                    # Rotate colonies in load balancer based on performance
                    self.colony_load_balancer.rotate(1)

                await asyncio.sleep(60)  # Run every minute

            except Exception as e:
                logger.error(f"Maintenance error: {e}")
                await asyncio.sleep(10)

    async def _stats_collection_loop(self):
        """Collect and log statistics"""
        while self._running:
            try:
                if self.config.enable_metrics:
                    stats = self.get_adapter_stats()
                    logger.debug("Adapter statistics", **stats)

                await asyncio.sleep(300)  # Every 5 minutes

            except Exception as e:
                logger.error(f"Stats collection error: {e}")
                await asyncio.sleep(60)

    def get_adapter_stats(self) -> dict[str, Any]:
        """Get comprehensive adapter statistics"""
        success_rate = self.successful_operations / max(self.total_operations, 1)
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0

        cache_hit_rate = self.cache_hits / max(self.cache_hits + self.cache_misses, 1)

        return {
            "colony_id": self.colony_id,
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": success_rate,
            "average_response_time_ms": avg_response_time,
            "active_operations": len(self.active_operations),
            "registered_colonies": len(self.registered_colonies),
            "active_colonies": sum(1 for stats in self.colony_stats.values() if stats.is_active),
            "memory_interfaces": len(self.memory_interfaces),
            "cache_entries": len(self.memory_cache),
            "cache_hit_rate": cache_hit_rate,
            "validator_stats": self.validator.get_metrics(),
        }

    def get_colony_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all registered colonies"""
        return {
            colony_id: {
                "total_operations": stats.total_operations,
                "success_rate": stats.success_rate,
                "average_response_time": stats.average_response_time,
                "is_active": stats.is_active,
                "memory_types": [mt.value for mt in stats.memory_types_handled],
            }
            for colony_id, stats in self.colony_stats.items()
        }


# Example usage and integration
async def demonstrate_colony_adapter():
    """Demonstrate colony memory adapter functionality"""

    # Create adapter
    adapter = ColonyMemoryAdapter(
        colony_id="main_colony",
        config=AdapterConfig(enable_validation=True, enable_caching=True, load_balancing=True),
    )

    await adapter.start()

    try:
        print("🌐 COLONY MEMORY ADAPTER DEMONSTRATION")
        print("=" * 60)

        # Register some colonies
        adapter.register_colony("colony_1", {"type": "episodic", "capacity": 1000})
        adapter.register_colony("colony_2", {"type": "semantic", "capacity": 2000})

        print(f"Registered colonies: {len(adapter.registered_colonies)}")

        # Test memory operations (would need actual interfaces in practice)
        print("\nAdapter ready for memory operations")
        print(f"Available memory types: {[mt.value for mt in MemoryType]}")

        # Show stats
        stats = adapter.get_adapter_stats()
        print(f"Success rate: {stats['success_rate']:.2%}")
        print(f"Cache hit rate: {stats['cache_hit_rate']:.2%}")

    finally:
        await adapter.stop()


if __name__ == "__main__":
    asyncio.run(demonstrate_colony_adapter())
