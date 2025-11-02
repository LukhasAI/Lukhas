"""
══════════════════════════════════════════════════════════════════════════════════
║ 🔋 LUKHAS AI - RESOURCE OPTIMIZATION INTEGRATION MODULE
║ Unified energy and memory optimization for the Symbiotic Swarm
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: resource_optimization_integration.py
║ Path: lukhas/core/resource_optimization_integration.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module integrates energy consumption analysis, memory optimization, and
║ efficient communication to provide a unified resource management system for
║ the Symbiotic Swarm architecture. It implements intelligent resource allocation,
║ predictive optimization, and adaptive behavior based on system load.
║
║ Key Features:
║ - Unified resource monitoring and management
║ - Energy-aware memory optimization
║ - Communication efficiency based on resource availability
║ - Predictive resource allocation
║ - Adaptive system behavior under constraints
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import contextlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional

from core.interfaces.core_interface import MessagePriority
from core.interfaces.dependency_injection import get_service
from memory.memory_optimization import MemoryOptimizer, MemoryTier

# Import our resource management modules
from .energy_consumption_analysis import (
    EnergyAwareComponent,
    EnergyComponent,
    EnergyConsumptionAnalyzer,
    EnergyProfile,
)

logger = logging.getLogger(__name__)


class ResourceState(Enum):
    """Overall system resource state"""

    ABUNDANT = auto()  # Plenty of resources available
    NORMAL = auto()  # Normal operating conditions
    CONSTRAINED = auto()  # Some resource constraints
    CRITICAL = auto()  # Critical resource shortage


class OptimizationStrategy(Enum):
    """Resource optimization strategies"""

    PERFORMANCE = auto()  # Maximize performance
    BALANCED = auto()  # Balance performance and efficiency
    EFFICIENCY = auto()  # Maximize efficiency
    SURVIVAL = auto()  # Minimum resource usage


@dataclass
class ResourceMetrics:
    """Unified resource metrics"""

    timestamp: float
    energy_used_joules: float
    memory_used_mb: float
    memory_total_mb: float
    network_bandwidth_mbps: float
    cpu_utilization: float
    resource_state: ResourceState
    active_optimizations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "energy_used_joules": self.energy_used_joules,
            "memory_used_mb": self.memory_used_mb,
            "memory_total_mb": self.memory_total_mb,
            "memory_utilization": (
                (self.memory_used_mb / self.memory_total_mb * 100) if self.memory_total_mb > 0 else 0
            ),
            "network_bandwidth_mbps": self.network_bandwidth_mbps,
            "cpu_utilization": self.cpu_utilization,
            "resource_state": self.resource_state.name,
            "active_optimizations": self.active_optimizations,
        }


class ResourceOptimizationCoordinator:
    """
    Main coordinator that integrates energy, memory, and communication optimization
    """

    def __init__(
        self,
        target_energy_budget_joules: float = 1000.0,
        target_memory_mb: int = 1000,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    ):
        # Initialize subsystems
        self.energy_analyzer = EnergyConsumptionAnalyzer()
        self.memory_optimizer = MemoryOptimizer(target_memory_mb=target_memory_mb)
        self.comm_fabric = None  # Will be initialized per node

        # Configuration
        self.target_energy_budget = target_energy_budget_joules
        self.target_memory_mb = target_memory_mb
        self.optimization_strategy = optimization_strategy

        # State tracking
        self.resource_state = ResourceState.NORMAL
        self.metrics_history: list[ResourceMetrics] = []
        self.optimization_decisions: dict[str, Any] = {}

        # Thresholds for state transitions
        self.thresholds = {
            "energy_critical": 0.9,  # 90% of budget
            "energy_constrained": 0.7,  # 70% of budget
            "memory_critical": 0.9,  # 90% of target
            "memory_constrained": 0.7,  # 70% of target
        }

        # Monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._optimization_interval = 5.0  # seconds

        # Register cross-system optimizations
        self._register_integrated_optimizations()

        logger.info(f"Resource Optimization Coordinator initialized with strategy: {optimization_strategy.name}")

    async def initialize_communication(self, node_id: str):
        """Initialize communication fabric for a node"""
        # Get communication fabric through dependency injection
        try:
            self.comm_fabric = get_service("communication_fabric")
            await self.comm_fabric.start()
        except ValueError:
            logger.warning("Communication fabric not available through dependency injection")
            self.comm_fabric = None

        # Set up energy tracking for communication
        self._setup_communication_energy_tracking()

    def _setup_communication_energy_tracking(self):
        """Set up energy tracking for communication operations"""
        if not self.comm_fabric:
            return

        # Wrap send_message to track energy
        original_send = self.comm_fabric.send_message

        async def energy_aware_send(*args, **kwargs):
            start_time = time.time()
            result = await original_send(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            # Record energy consumption
            message_size = kwargs.get("payload", {})
            self.energy_analyzer.record_energy_consumption(
                EnergyComponent.COMMUNICATION,
                "message_send",
                energy_joules=0.001 * len(str(message_size)),  # Estimate
                duration_ms=duration_ms,
                metadata={"priority": kwargs.get("priority", MessagePriority.NORMAL).name},
            )

            return result

        self.comm_fabric.send_message = energy_aware_send

    def _register_integrated_optimizations(self):
        """Register optimization callbacks that work across subsystems"""

        # Memory optimization based on energy state

        def energy_aware_memory_compression():
            if self.resource_state in [
                ResourceState.CONSTRAINED,
                ResourceState.CRITICAL,
            ]:
                # Aggressive compression when energy is low
                freed = 0
                cache = self.memory_optimizer.tiered_cache

                # Move more data to cold storage
                for tier in [MemoryTier.HOT, MemoryTier.WARM]:
                    tier_cache = cache.tiers[tier]
                    to_demote = []

                    for key, mem_obj in list(tier_cache.items())[:10]:  # Demote up to 10 items
                        if mem_obj.access_frequency() < 1.0:
                            to_demote.append((key, mem_obj))

                    for key, mem_obj in to_demote:
                        old_size = mem_obj.size_bytes
                        del tier_cache[key]
                        cache._store_in_tier(mem_obj, MemoryTier.COLD)
                        freed += old_size - mem_obj.size_bytes

                return freed
            return 0

        self.memory_optimizer.register_optimization(energy_aware_memory_compression)

        # Communication optimization based on resources

        def resource_aware_communication():
            if self.comm_fabric and self.resource_state == ResourceState.CRITICAL:
                # Switch to low-power communication profile
                self.comm_fabric.router.energy_budget *= 0.5  # Reduce budget
                logger.info("Reduced communication energy budget due to critical resources")
            return 0

        self.memory_optimizer.register_optimization(resource_aware_communication)

    async def start_monitoring(self):
        """Start unified resource monitoring"""
        # Start subsystem monitoring
        await self.energy_analyzer.start_monitoring()
        await self.memory_optimizer.start_monitoring()

        # Start coordinator monitoring
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Resource optimization monitoring started")

    async def stop_monitoring(self):
        """Stop resource monitoring"""
        await self.energy_analyzer.stop_monitoring()
        await self.memory_optimizer.stop_monitoring()

        if self._monitoring_task:
            self._monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitoring_task

        logger.info("Resource optimization monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring and optimization loop"""
        while True:
            try:
                # Collect metrics
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)

                # Keep history limited
                if len(self.metrics_history) > 1000:
                    self.metrics_history.pop(0)

                # Update resource state
                self._update_resource_state(metrics)

                # Apply optimization strategy
                await self._apply_optimizations(metrics)

                # Log status
                if len(self.metrics_history) % 10 == 0:
                    logger.info(
                        f"Resource state: {self.resource_state.name}, "
                        f"Energy: {metrics.energy_used_joules:.1f}J, "
                        f"Memory: {metrics.memory_used_mb:.1f}MB"
                    )

                await asyncio.sleep(self._optimization_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self._optimization_interval)

    async def _collect_metrics(self) -> ResourceMetrics:
        """Collect unified resource metrics"""
        # Get energy stats
        energy_stats = self.energy_analyzer.get_energy_statistics(time_window_seconds=self._optimization_interval)

        # Get memory stats
        memory_stats = self.memory_optimizer.get_memory_stats()

        # Get communication stats if available
        comm_stats = self.comm_fabric.get_communication_stats() if self.comm_fabric else {}

        # Calculate network bandwidth (simplified)
        network_bandwidth = 0.0
        if comm_stats:
            bytes_sent = comm_stats.get("p2p_stats", {}).get("transfer_stats", {}).get("bytes_sent", 0)
            network_bandwidth = (bytes_sent * 8 / 1_000_000) / self._optimization_interval  # Mbps

        # Get CPU utilization (simplified estimate)
        cpu_utilization = min(100.0, energy_stats.get("average_power_watts", 0) * 10)

        return ResourceMetrics(
            timestamp=time.time(),
            energy_used_joules=energy_stats.get("total_energy_joules", 0),
            memory_used_mb=memory_stats.get("current_memory_mb", 0),
            memory_total_mb=self.target_memory_mb,
            network_bandwidth_mbps=network_bandwidth,
            cpu_utilization=cpu_utilization,
            resource_state=self.resource_state,
            active_optimizations=list(self.optimization_decisions.keys()),
        )

    def _update_resource_state(self, metrics: ResourceMetrics):
        """Update overall resource state based on metrics"""
        # Calculate resource utilization ratios
        energy_ratio = metrics.energy_used_joules / self.target_energy_budget if self.target_energy_budget > 0 else 0
        memory_ratio = metrics.memory_used_mb / metrics.memory_total_mb if metrics.memory_total_mb > 0 else 0

        # Determine state based on worst constraint
        if energy_ratio >= self.thresholds["energy_critical"] or memory_ratio >= self.thresholds["memory_critical"]:
            self.resource_state = ResourceState.CRITICAL
        elif (
            energy_ratio >= self.thresholds["energy_constrained"]
            or memory_ratio >= self.thresholds["memory_constrained"]
        ):
            self.resource_state = ResourceState.CONSTRAINED
        elif energy_ratio < 0.5 and memory_ratio < 0.5:
            self.resource_state = ResourceState.ABUNDANT
        else:
            self.resource_state = ResourceState.NORMAL

    async def _apply_optimizations(self, metrics: ResourceMetrics):
        """Apply optimizations based on current state and strategy"""
        self.optimization_decisions.clear()

        # Apply strategy-specific optimizations
        if self.optimization_strategy == OptimizationStrategy.PERFORMANCE:
            await self._optimize_for_performance(metrics)
        elif self.optimization_strategy == OptimizationStrategy.EFFICIENCY:
            await self._optimize_for_efficiency(metrics)
        elif self.optimization_strategy == OptimizationStrategy.SURVIVAL:
            await self._optimize_for_survival(metrics)
        else:  # BALANCED
            await self._optimize_balanced(metrics)

        # Apply state-specific emergency optimizations
        if self.resource_state == ResourceState.CRITICAL:
            await self._apply_emergency_optimizations()

    async def _optimize_for_performance(self, metrics: ResourceMetrics):
        """Optimize for maximum performance"""
        # Set high-performance profiles
        self.energy_analyzer.set_energy_profile(EnergyProfile.HIGH_PERFORMANCE)

        # Keep data in hot tiers
        self.optimization_decisions["memory_tier_preference"] = "hot"

        # Use fastest communication modes
        if self.comm_fabric:
            self.comm_fabric.router.energy_budget = self.target_energy_budget * 0.5  # Allow more energy for comm

        self.optimization_decisions["strategy"] = "performance"

    async def _optimize_for_efficiency(self, metrics: ResourceMetrics):
        """Optimize for maximum efficiency"""
        # Set efficient profiles
        self.energy_analyzer.set_energy_profile(EnergyProfile.LOW_POWER)

        # Aggressive memory compression
        self.memory_optimizer._trigger_optimization()
        self.optimization_decisions["memory_compression"] = "aggressive"

        # Efficient communication
        if self.comm_fabric:
            self.comm_fabric.router.energy_budget = self.target_energy_budget * 0.2

        self.optimization_decisions["strategy"] = "efficiency"

    async def _optimize_balanced(self, metrics: ResourceMetrics):
        """Balanced optimization based on resource state"""
        if self.resource_state == ResourceState.ABUNDANT:
            # Favor performance when resources are plentiful
            self.energy_analyzer.set_energy_profile(EnergyProfile.NORMAL)
            self.optimization_decisions["bias"] = "performance"
        elif self.resource_state == ResourceState.CONSTRAINED:
            # Start conserving resources
            self.energy_analyzer.set_energy_profile(EnergyProfile.LOW_POWER)
            self.memory_optimizer._trigger_optimization()
            self.optimization_decisions["bias"] = "conservation"
        else:
            # Normal operation
            self.energy_analyzer.set_energy_profile(EnergyProfile.NORMAL)
            self.optimization_decisions["bias"] = "balanced"

    async def _optimize_for_survival(self, metrics: ResourceMetrics):
        """Minimize resource usage for survival mode"""
        # Minimum energy profile
        self.energy_analyzer.set_energy_profile(EnergyProfile.IDLE)

        # Maximum compression
        self.memory_optimizer._trigger_optimization()

        # Minimal communication
        if self.comm_fabric:
            self.comm_fabric.router.energy_budget = self.target_energy_budget * 0.1

        self.optimization_decisions["strategy"] = "survival"
        self.optimization_decisions["mode"] = "minimal"

    async def _apply_emergency_optimizations(self):
        """Apply emergency optimizations in critical state"""
        logger.warning("Applying emergency resource optimizations")

        # Force garbage collection
        import gc

        gc.collect()

        # Clear non-essential caches
        cache = self.memory_optimizer.tiered_cache

        # Move everything possible to archive
        for tier in [MemoryTier.HOT, MemoryTier.WARM, MemoryTier.COLD]:
            tier_cache = cache.tiers[tier]
            items_to_archive = []

            for key, mem_obj in tier_cache.items():
                if mem_obj.access_frequency() < 0.1:  # Very low access
                    items_to_archive.append((key, mem_obj))

            for key, mem_obj in items_to_archive:
                del tier_cache[key]
                cache._store_in_tier(mem_obj, MemoryTier.ARCHIVED)

        self.optimization_decisions["emergency"] = "active"
        self.optimization_decisions["archived_objects"] = len(items_to_archive)

    def get_resource_summary(self) -> dict[str, Any]:
        """Get comprehensive resource usage summary"""
        if not self.metrics_history:
            return {"status": "no_data"}

        latest = self.metrics_history[-1]

        # Calculate trends if enough history
        trends = {}
        if len(self.metrics_history) >= 10:
            recent = self.metrics_history[-10:]
            old = self.metrics_history[-20:-10] if len(self.metrics_history) >= 20 else self.metrics_history[:10]

            trends["energy_trend"] = sum(m.energy_used_joules for m in recent) / len(recent) - sum(
                m.energy_used_joules for m in old
            ) / len(old)
            trends["memory_trend"] = sum(m.memory_used_mb for m in recent) / len(recent) - sum(
                m.memory_used_mb for m in old
            ) / len(old)

        # Get subsystem details
        energy_stats = self.energy_analyzer.get_energy_statistics()
        memory_stats = self.memory_optimizer.get_memory_stats()

        return {
            "current_state": self.resource_state.name,
            "optimization_strategy": self.optimization_strategy.name,
            "latest_metrics": latest.to_dict(),
            "trends": trends,
            "energy_details": {
                "total_consumed": energy_stats.get("total_energy_joules", 0),
                "budget_remaining": self.target_energy_budget - energy_stats.get("total_energy_joules", 0),
                "carbon_footprint_kg": energy_stats.get("carbon_footprint_kg", 0),
                "recommendations": energy_stats.get("recommendations", []),
            },
            "memory_details": {
                "utilization_percent": (
                    (latest.memory_used_mb / latest.memory_total_mb * 100) if latest.memory_total_mb > 0 else 0
                ),
                "tier_distribution": memory_stats.get("cache_stats", {}).get("tier_stats", {}),
                "optimization_count": memory_stats.get("optimization_stats", {}).get("optimizations_triggered", 0),
            },
            "active_optimizations": self.optimization_decisions,
            "metrics_history_size": len(self.metrics_history),
        }

    async def execute_with_resource_awareness(
        self,
        operation_name: str,
        operation_func: Callable,
        estimated_energy: float = 1.0,
        estimated_memory_mb: float = 10.0,
        priority: str = "normal",
    ) -> Any:
        """
        Execute an operation with resource awareness and optimization
        """
        # Check if we can afford the operation
        can_proceed = True
        wait_time = 0

        if self.resource_state == ResourceState.CRITICAL:
            if priority != "critical":
                # Defer non-critical operations
                can_proceed = False
                wait_time = 5.0
                logger.warning(f"Deferring {operation_name} due to critical resources")
        elif self.resource_state == ResourceState.CONSTRAINED and priority == "low":
            can_proceed = False
            wait_time = 2.0

        if not can_proceed:
            await asyncio.sleep(wait_time)
            # Re-check after wait
            if self.resource_state == ResourceState.CRITICAL and priority != "critical":
                raise ResourceError(f"Cannot execute {operation_name}: resources critically low")

        # Track operation
        start_time = time.time()

        try:
            # Execute with energy tracking
            component = EnergyAwareComponent(operation_name, self.energy_analyzer)
            result = await component.execute_with_energy_tracking(
                operation_name,
                operation_func,
                input_size=int(estimated_memory_mb * 1024),  # Convert to KB
            )

            return result

        finally:
            # Update metrics
            duration = time.time() - start_time
            logger.debug(f"Operation {operation_name} completed in {duration:.3f}s")


class ResourceError(Exception):
    """Exception raised when resources are insufficient"""


# Integration example


async def demonstrate_integrated_optimization():
    """Demonstrate integrated resource optimization"""

    # Initialize coordinator
    coordinator = ResourceOptimizationCoordinator(
        target_energy_budget_joules=1000.0,
        target_memory_mb=500,
        optimization_strategy=OptimizationStrategy.BALANCED,
    )

    # Initialize communication
    await coordinator.initialize_communication("demo-node-001")

    # Start monitoring
    await coordinator.start_monitoring()

    # Create energy budget
    coordinator.energy_analyzer.create_budget("demo_budget", total_joules=1000.0, time_window_seconds=3600.0)

    # Simulate various operations
    print("Simulating resource-intensive operations...")

    # Memory-intensive operations
    for i in range(50):
        key = f"data_{i}"
        data = list(range(1000))

        # Store with resource tracking
        await coordinator.execute_with_resource_awareness(
            f"store_{key}",
            lambda: coordinator.memory_optimizer.store(key, data, hint="warm"),
            estimated_energy=0.5,
            estimated_memory_mb=0.1,
        )

        await asyncio.sleep(0.01)

    # Communication operations
    for i in range(20):
        await coordinator.comm_fabric.send_message(
            "demo-node-002",
            "data_sync",
            {"batch": i, "data": list(range(100))},
            MessagePriority.NORMAL,
        )
        await asyncio.sleep(0.05)

    # Simulate high load
    print("\nSimulating high load...")
    tasks = []

    async def heavy_operation(op_id: int):
        data = list(range(10000))
        await coordinator.execute_with_resource_awareness(
            f"heavy_op_{op_id}",
            lambda: sum(data) * 2,
            estimated_energy=5.0,
            estimated_memory_mb=10.0,
            priority="normal" if op_id % 5 != 0 else "critical",
        )

    # Launch concurrent operations
    for i in range(10):
        tasks.append(asyncio.create_task(heavy_operation(i)))

    await asyncio.gather(*tasks, return_exceptions=True)

    # Wait for metrics to accumulate
    await asyncio.sleep(2.0)

    # Get resource summary
    summary = coordinator.get_resource_summary()
    print("\nResource Optimization Summary:")
    print(json.dumps(summary, indent=2))

    # Simulate resource pressure
    print("\nSimulating resource pressure...")
    coordinator.resource_state = ResourceState.CRITICAL

    # Try operations under pressure
    try:
        await coordinator.execute_with_resource_awareness("low_priority_op", lambda: "result", priority="low")
    except ResourceError as e:
        print(f"Operation blocked: {e}")

    # Critical operation should succeed
    result = await coordinator.execute_with_resource_awareness(
        "critical_op", lambda: "critical_result", priority="critical"
    )
    print(f"Critical operation succeeded: {result}")

    # Stop monitoring
    await coordinator.stop_monitoring()

    # Final statistics
    print("\nFinal Statistics:")
    print(f"Energy consumed: {summary['energy_details']['total_consumed']:.1f}J")
    print(f"Memory utilization: {summary['memory_details']['utilization_percent']:.1f}%")
    print(f"Optimizations triggered: {summary['memory_details']['optimization_count']}")


if __name__ == "__main__":
    asyncio.run(demonstrate_integrated_optimization())
