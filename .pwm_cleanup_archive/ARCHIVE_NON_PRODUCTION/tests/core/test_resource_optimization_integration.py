"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧪 LUKHAS AI - RESOURCE OPTIMIZATION INTEGRATION TEST SUITE
║ Tests for unified energy and memory optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_resource_optimization_integration.py
║ Path: tests/core/test_resource_optimization_integration.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ TEST COVERAGE
╠══════════════════════════════════════════════════════════════════════════════════
║ - Resource state management and transitions
║ - Optimization strategy application
║ - Cross-subsystem integration
║ - Resource-aware execution
║ - Emergency optimization triggers
║ - Metrics collection and trends
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import time

import pytest

from core.energy_consumption_analysis import EnergyProfile
from core.resource_optimization_integration import (
    OptimizationStrategy,
    ResourceError,
    ResourceMetrics,
    ResourceOptimizationCoordinator,
    ResourceState,
)


class TestResourceMetrics:
    """Test ResourceMetrics dataclass"""

    def test_metrics_creation(self):
        """Test creating resource metrics"""
        metrics = ResourceMetrics(
            timestamp=time.time(),
            energy_used_joules=50.0,
            memory_used_mb=200.0,
            memory_total_mb=500.0,
            network_bandwidth_mbps=10.0,
            cpu_utilization=45.0,
            resource_state=ResourceState.NORMAL,
        )

        assert metrics.energy_used_joules == 50.0
        assert metrics.memory_used_mb == 200.0
        assert metrics.resource_state == ResourceState.NORMAL

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary"""
        metrics = ResourceMetrics(
            timestamp=1234567890,
            energy_used_joules=100.0,
            memory_used_mb=250.0,
            memory_total_mb=500.0,
            network_bandwidth_mbps=5.0,
            cpu_utilization=60.0,
            resource_state=ResourceState.CONSTRAINED,
            active_optimizations=["compression", "throttling"],
        )

        data = metrics.to_dict()
        assert data["timestamp"] == 1234567890
        assert data["memory_utilization"] == 50.0
        assert data["resource_state"] == "CONSTRAINED"
        assert "compression" in data["active_optimizations"]


class TestResourceOptimizationCoordinator:
    """Test main resource optimization coordinator"""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance for tests"""
        return ResourceOptimizationCoordinator(
            target_energy_budget_joules=1000.0,
            target_memory_mb=500,
            optimization_strategy=OptimizationStrategy.BALANCED,
        )

    def test_coordinator_initialization(self, coordinator):
        """Test coordinator initialization"""
        assert coordinator.target_energy_budget == 1000.0
        assert coordinator.target_memory_mb == 500
        assert coordinator.optimization_strategy == OptimizationStrategy.BALANCED
        assert coordinator.resource_state == ResourceState.NORMAL

    @pytest.mark.asyncio
    async def test_communication_initialization(self, coordinator):
        """Test initializing communication fabric"""
        await coordinator.initialize_communication("test-node")
        assert coordinator.comm_fabric is not None
        assert coordinator.comm_fabric.node_id == "test-node"

        # Clean up
        await coordinator.comm_fabric.stop()

    def test_resource_state_updates(self, coordinator):
        """Test resource state transitions"""
        # Normal state
        metrics = ResourceMetrics(
            timestamp=time.time(),
            energy_used_joules=500.0,  # 50% of budget
            memory_used_mb=250.0,  # 50% of target
            memory_total_mb=500.0,
            network_bandwidth_mbps=5.0,
            cpu_utilization=50.0,
            resource_state=ResourceState.NORMAL,
        )

        coordinator._update_resource_state(metrics)
        assert coordinator.resource_state == ResourceState.NORMAL

        # Constrained state
        metrics.energy_used_joules = 750.0  # 75% of budget
        coordinator._update_resource_state(metrics)
        assert coordinator.resource_state == ResourceState.CONSTRAINED

        # Critical state
        metrics.memory_used_mb = 460.0  # 92% of target
        coordinator._update_resource_state(metrics)
        assert coordinator.resource_state == ResourceState.CRITICAL

        # Abundant state
        metrics.energy_used_joules = 100.0  # 10% of budget
        metrics.memory_used_mb = 100.0  # 20% of target
        coordinator._update_resource_state(metrics)
        assert coordinator.resource_state == ResourceState.ABUNDANT

    @pytest.mark.asyncio
    async def test_optimization_strategies(self, coordinator):
        """Test different optimization strategies"""
        metrics = ResourceMetrics(
            timestamp=time.time(),
            energy_used_joules=500.0,
            memory_used_mb=250.0,
            memory_total_mb=500.0,
            network_bandwidth_mbps=5.0,
            cpu_utilization=50.0,
            resource_state=ResourceState.NORMAL,
        )

        # Test performance optimization
        coordinator.optimization_strategy = OptimizationStrategy.PERFORMANCE
        await coordinator._apply_optimizations(metrics)
        assert coordinator.optimization_decisions.get("strategy") == "performance"
        assert (
            coordinator.energy_analyzer.current_profile
            == EnergyProfile.HIGH_PERFORMANCE
        )

        # Test efficiency optimization
        coordinator.optimization_strategy = OptimizationStrategy.EFFICIENCY
        await coordinator._apply_optimizations(metrics)
        assert coordinator.optimization_decisions.get("strategy") == "efficiency"
        assert coordinator.energy_analyzer.current_profile == EnergyProfile.LOW_POWER

        # Test survival optimization
        coordinator.optimization_strategy = OptimizationStrategy.SURVIVAL
        await coordinator._apply_optimizations(metrics)
        assert coordinator.optimization_decisions.get("strategy") == "survival"
        assert coordinator.energy_analyzer.current_profile == EnergyProfile.IDLE

    @pytest.mark.asyncio
    async def test_resource_aware_execution(self, coordinator):
        """Test resource-aware operation execution"""

        # Normal conditions
        async def test_operation():
            return "success"

        result = await coordinator.execute_with_resource_awareness(
            "test_op",
            test_operation,
            estimated_energy=1.0,
            estimated_memory_mb=10.0,
            priority="normal",
        )
        assert result == "success"

        # Critical conditions with low priority
        coordinator.resource_state = ResourceState.CRITICAL

        with pytest.raises(ResourceError):
            await coordinator.execute_with_resource_awareness(
                "low_priority_op", test_operation, priority="low"
            )

        # Critical operations should still proceed
        result = await coordinator.execute_with_resource_awareness(
            "critical_op", test_operation, priority="critical"
        )
        assert result == "success"

    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, coordinator):
        """Test monitoring start/stop"""
        await coordinator.start_monitoring()

        # Wait for some metrics
        await asyncio.sleep(0.1)

        await coordinator.stop_monitoring()

        # Should have collected some metrics
        assert len(coordinator.metrics_history) > 0

    def test_resource_summary(self, coordinator):
        """Test resource summary generation"""
        # Add some mock metrics
        for i in range(5):
            metrics = ResourceMetrics(
                timestamp=time.time() + i,
                energy_used_joules=100.0 * i,
                memory_used_mb=50.0 * i,
                memory_total_mb=500.0,
                network_bandwidth_mbps=5.0,
                cpu_utilization=20.0 * i,
                resource_state=ResourceState.NORMAL,
            )
            coordinator.metrics_history.append(metrics)

        summary = coordinator.get_resource_summary()

        assert summary["current_state"] == "NORMAL"
        assert summary["optimization_strategy"] == "BALANCED"
        assert "latest_metrics" in summary
        assert summary["metrics_history_size"] == 5

    @pytest.mark.asyncio
    async def test_emergency_optimizations(self, coordinator):
        """Test emergency optimization triggers"""
        # Set critical state
        coordinator.resource_state = ResourceState.CRITICAL

        # Add some data to memory
        for i in range(10):
            coordinator.memory_optimizer.store(f"test_{i}", {"data": i}, hint="hot")

        # Apply emergency optimizations
        await coordinator._apply_emergency_optimizations()

        # Check that optimizations were applied
        assert coordinator.optimization_decisions.get("emergency") == "active"
        assert "archived_objects" in coordinator.optimization_decisions

    @pytest.mark.asyncio
    async def test_integrated_optimizations(self, coordinator):
        """Test cross-subsystem optimization integration"""
        # Initialize communication
        await coordinator.initialize_communication("test-node")

        # Start monitoring
        await coordinator.start_monitoring()

        # Simulate resource pressure
        coordinator.resource_state = ResourceState.CONSTRAINED

        # Trigger memory optimization
        coordinator.memory_optimizer._trigger_optimization()

        # Wait for optimization cycle
        await asyncio.sleep(0.1)

        # Should have reduced communication budget
        assert (
            coordinator.comm_fabric.router.energy_budget
            <= coordinator.target_energy_budget
        )

        # Clean up
        await coordinator.stop_monitoring()
        await coordinator.comm_fabric.stop()


class TestIntegration:
    """Integration tests for complete resource optimization"""

    @pytest.mark.asyncio
    async def test_full_resource_optimization_flow(self):
        """Test complete resource optimization workflow"""
        coordinator = ResourceOptimizationCoordinator(
            target_energy_budget_joules=100.0,  # Small budget for testing
            target_memory_mb=100,
            optimization_strategy=OptimizationStrategy.BALANCED,
        )

        # Initialize systems
        await coordinator.initialize_communication("integration-test")
        await coordinator.start_monitoring()

        # Create energy budget
        coordinator.energy_analyzer.create_budget(
            "test_budget", total_joules=100.0, time_window_seconds=60.0
        )

        # Simulate operations that consume resources
        operations_completed = []

        async def simulated_operation(op_id: int):
            await asyncio.sleep(0.01)
            operations_completed.append(op_id)
            return f"result_{op_id}"

        # Execute operations with different priorities
        tasks = []
        for i in range(10):
            priority = "critical" if i < 2 else "normal" if i < 7 else "low"

            task = coordinator.execute_with_resource_awareness(
                f"op_{i}",
                lambda op_id=i: simulated_operation(op_id),
                estimated_energy=5.0,
                estimated_memory_mb=10.0,
                priority=priority,
            )
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check results
        critical_completed = sum(1 for i in operations_completed if i < 2)
        assert critical_completed == 2  # Critical operations should complete

        # Get final summary
        summary = coordinator.get_resource_summary()
        assert summary["current_state"] in ["NORMAL", "CONSTRAINED", "CRITICAL"]
        assert summary["energy_details"]["total_consumed"] > 0

        # Clean up
        await coordinator.stop_monitoring()
        await coordinator.comm_fabric.stop()

    @pytest.mark.asyncio
    async def test_adaptive_behavior(self):
        """Test adaptive behavior under changing conditions"""
        coordinator = ResourceOptimizationCoordinator(
            target_energy_budget_joules=500.0,
            target_memory_mb=200,
            optimization_strategy=OptimizationStrategy.BALANCED,
        )

        await coordinator.start_monitoring()

        # Simulate changing resource conditions
        states_observed = []

        # Monitor state changes
        for i in range(5):
            # Gradually increase resource usage
            energy_used = 100.0 * (i + 1)
            memory_used = 40.0 * (i + 1)

            metrics = ResourceMetrics(
                timestamp=time.time(),
                energy_used_joules=energy_used,
                memory_used_mb=memory_used,
                memory_total_mb=200.0,
                network_bandwidth_mbps=5.0,
                cpu_utilization=20.0 * (i + 1),
                resource_state=coordinator.resource_state,
            )

            coordinator.metrics_history.append(metrics)
            coordinator._update_resource_state(metrics)
            await coordinator._apply_optimizations(metrics)

            states_observed.append(coordinator.resource_state)
            await asyncio.sleep(0.1)

        # Should have transitioned through states
        assert ResourceState.NORMAL in states_observed
        assert (
            ResourceState.CONSTRAINED in states_observed
            or ResourceState.CRITICAL in states_observed
        )

        # Energy profile should have adjusted
        assert (
            coordinator.energy_analyzer.current_profile
            != EnergyProfile.HIGH_PERFORMANCE
        )

        await coordinator.stop_monitoring()


class TestPerformance:
    """Performance tests for resource optimization"""

    @pytest.mark.asyncio
    async def test_metrics_collection_performance(self):
        """Test performance of metrics collection"""
        coordinator = ResourceOptimizationCoordinator()

        start_time = time.time()

        # Collect many metrics
        for _ in range(100):
            metrics = await coordinator._collect_metrics()
            coordinator.metrics_history.append(metrics)

        elapsed = time.time() - start_time

        # Should be fast
        assert elapsed < 1.0
        assert len(coordinator.metrics_history) == 100

    @pytest.mark.asyncio
    async def test_concurrent_operation_handling(self):
        """Test handling many concurrent operations"""
        coordinator = ResourceOptimizationCoordinator()

        async def fast_operation():
            await asyncio.sleep(0.001)
            return "done"

        start_time = time.time()

        # Launch many operations
        tasks = []
        for i in range(100):
            task = coordinator.execute_with_resource_awareness(
                f"op_{i}",
                fast_operation,
                estimated_energy=0.1,
                estimated_memory_mb=1.0,
                priority="normal",
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        # Should complete quickly
        assert elapsed < 2.0
        assert all(r == "done" for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
