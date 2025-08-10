"""
Integration tests for Symbiotic Swarm state management and resource efficiency
Tests TODO 134, 135, and 136 implementations
"""

import json
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.core_utilities_analyzer import ResourceEfficiencyAnalyzer
from core.event_sourcing import (
    AIAgentAggregate,
    EventReplayService,
    EventStore,
)
from core.practical_optimizations import (
    AdaptiveCache,
    ComputationReuse,
    ObjectPool,
    ResourceManager,
    deserialize_swarm_message,
    optimize_swarm_communication,
)
from memory.distributed_state_manager import (
    DistributedStateManager,
    MultiNodeStateManager,
    StateType,
)


class TestEventSourcingIntegration:
    """Test event sourcing system integration"""

    def test_event_store_persistence(self):
        """Test that events are persisted correctly"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            # Create event store
            store = EventStore(db_path)

            # Create and modify agent
            agent = AIAgentAggregate("test-agent-001", store)
            agent.create_agent(["reasoning", "memory"])
            agent.assign_task("task-001", {"type": "test"})
            agent.complete_task("task-001", {"status": "success"})
            agent.commit_events()

            # Create new store instance
            store2 = EventStore(db_path)

            # Verify events persisted
            events = store2.get_events_for_aggregate("test-agent-001")
            assert len(events) == 3
            assert events[0].event_type == "AgentCreated"
            assert events[1].event_type == "TaskAssigned"
            assert events[2].event_type == "TaskCompleted"

        finally:
            os.unlink(db_path)

    def test_event_replay_recovery(self):
        """Test state recovery through event replay"""
        store = EventStore()

        # Create agent with state
        agent1 = AIAgentAggregate("recovery-agent", store)
        agent1.create_agent(["skill1", "skill2"])
        agent1.assign_task("task-001", {"data": "test"})
        agent1.update_memory({"key": "value"})
        agent1.commit_events()

        # Create new agent instance - should recover state
        agent2 = AIAgentAggregate("recovery-agent", store)

        assert agent2.capabilities == ["skill1", "skill2"]
        assert "task-001" in agent2.active_tasks
        assert agent2.memory["key"] == "value"
        assert agent2.version == 3

    def test_temporal_queries(self):
        """Test temporal query capabilities"""
        store = EventStore()
        replay_service = EventReplayService(store)

        # Create timeline of events
        agent = AIAgentAggregate("temporal-agent", store)

        start_time = time.time()
        agent.create_agent(["capability1"])
        agent.commit_events()

        time.sleep(0.1)
        checkpoint1 = time.time()

        agent.add_capability("capability2")
        agent.commit_events()

        time.sleep(0.1)
        checkpoint2 = time.time()

        agent.add_capability("capability3")
        agent.commit_events()

        # Query at different points in time
        agent_at_checkpoint1 = replay_service.replay_aggregate_to_point_in_time(
            "temporal-agent", checkpoint1
        )
        assert len(agent_at_checkpoint1.capabilities) == 1

        agent_at_checkpoint2 = replay_service.replay_aggregate_to_point_in_time(
            "temporal-agent", checkpoint2
        )
        assert len(agent_at_checkpoint2.capabilities) == 2


class TestDistributedStateManager:
    """Test distributed state management integration"""

    def test_basic_state_operations(self):
        """Test basic get/set/delete operations"""
        manager = DistributedStateManager("test-node", num_shards=4)

        # Set values
        assert manager.set("key1", "value1")
        assert manager.set("key2", {"nested": "data"})
        assert manager.set("key3", [1, 2, 3])

        # Get values
        assert manager.get("key1") == "value1"
        assert manager.get("key2")["nested"] == "data"
        assert manager.get("key3") == [1, 2, 3]
        assert manager.get("nonexistent") is None

        # Delete value
        assert manager.delete("key1")
        assert manager.get("key1") is None

        manager.shutdown()

    def test_state_type_optimization(self):
        """Test state type optimization"""
        manager = DistributedStateManager("test-node", num_shards=4)

        # Set different state types
        manager.set("hot_data", "frequently_accessed", StateType.HOT)
        manager.set("warm_data", "occasional_access", StateType.WARM, ttl=60)
        manager.set("cold_data", "rarely_accessed", StateType.COLD, ttl=10)

        # Access hot data multiple times
        for _ in range(10):
            assert manager.get("hot_data") == "frequently_accessed"

        # Check metrics
        stats = manager.get_global_stats()
        assert stats["metrics"]["cache_hits"] >= 9  # First access is a miss

        manager.shutdown()

    def test_snapshot_and_recovery(self):
        """Test snapshot creation and recovery"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create manager with data
            manager1 = DistributedStateManager(
                "snapshot-node",
                num_shards=4,
                event_store=EventStore(f"{tmpdir}/events.db"),
                snapshot_interval=5,
            )

            # Add enough events to trigger snapshot
            for i in range(10):
                manager1.set(f"key_{i}", f"value_{i}")

            # Force snapshot
            manager1._create_snapshot()
            initial_stats = manager1.get_global_stats()
            manager1.shutdown()

            # Create new manager - should recover from snapshot
            manager2 = DistributedStateManager(
                "snapshot-node",
                num_shards=4,
                event_store=EventStore(f"{tmpdir}/events.db"),
            )

            # Verify data recovered
            for i in range(10):
                assert manager2.get(f"key_{i}") == f"value_{i}"

            # Verify snapshot was used
            assert manager2.metrics["snapshots"] >= 1

            manager2.shutdown()

    def test_multi_node_coordination(self):
        """Test multi-node state management"""
        manager = MultiNodeStateManager(
            [
                {"node_id": "node-001", "num_shards": 4},
                {"node_id": "node-002", "num_shards": 4},
                {"node_id": "node-003", "num_shards": 4},
            ]
        )

        # Set values across nodes
        for i in range(30):
            assert manager.set(f"distributed_key_{i}", f"value_{i}")

        # Verify distribution
        cluster_stats = manager.get_cluster_stats()
        assert cluster_stats["total_keys"] == 30
        assert len(cluster_stats["nodes"]) == 3

        # Each node should have some keys
        for node_stats in cluster_stats["nodes"].values():
            assert node_stats["total_keys"] > 0

        manager.shutdown_all()

    def test_concurrent_access(self):
        """Test concurrent access to distributed state"""
        manager = DistributedStateManager("concurrent-node", num_shards=8)

        def worker(worker_id: int):
            for i in range(100):
                key = f"worker_{worker_id}_key_{i}"
                manager.set(key, i)
                assert manager.get(key) == i

        # Run concurrent workers
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            for future in futures:
                future.result()

        # Verify all data
        stats = manager.get_global_stats()
        assert stats["total_keys"] == 1000  # 10 workers * 100 keys

        manager.shutdown()


class TestResourceEfficiencyAnalyzer:
    """Test resource efficiency analysis"""

    def test_resource_monitoring(self):
        """Test basic resource monitoring"""
        analyzer = ResourceEfficiencyAnalyzer(sample_interval=0.1, history_size=100)

        analyzer.start_monitoring()

        # Generate some load
        data = []
        for _ in range(10):
            data.append([i for i in range(10000)])
            time.sleep(0.1)

        # Get quick stats
        stats = analyzer.get_quick_stats()
        assert stats["cpu_percent"] >= 0
        assert stats["memory_mb"] > 0
        assert stats["threads"] > 0

        analyzer.stop_monitoring()

    def test_efficiency_analysis(self):
        """Test efficiency analysis and recommendations"""
        analyzer = ResourceEfficiencyAnalyzer(sample_interval=0.1, history_size=100)

        analyzer.start_monitoring()

        # Simulate workload
        for _ in range(5):
            # CPU intensive
            sum(i**2 for i in range(100000))
            time.sleep(0.1)

        # Analyze efficiency
        report = analyzer.analyze_efficiency(duration_hours=0.001)  # Last few seconds

        assert report.efficiency_score >= 0
        assert report.efficiency_score <= 100
        assert len(report.recommendations) > 0
        assert report.snapshots_analyzed > 0

        # Check for expected analysis sections
        assert "average_utilization" in report.cpu_analysis
        assert "average_utilization" in report.memory_analysis
        assert "total_consumption_kwh" in report.energy_analysis

        analyzer.stop_monitoring()

    def test_bottleneck_detection(self):
        """Test bottleneck detection"""
        analyzer = ResourceEfficiencyAnalyzer()
        analyzer.start_monitoring()

        # Create memory pressure
        large_data = []
        for _ in range(10):
            large_data.append([0] * 1000000)  # Allocate memory
            time.sleep(0.1)

        report = analyzer.analyze_efficiency(duration_hours=0.001)

        # Should detect memory growth
        memory_trend = report.trends.get("memory")
        if memory_trend and memory_trend.trend_direction == "increasing":
            # Should have memory-related bottleneck or recommendation
            memory_bottlenecks = [
                b for b in report.bottlenecks if "memory" in b["type"].lower()
            ]
            memory_recommendations = [
                r for r in report.recommendations if "memory" in r["category"].lower()
            ]
            assert len(memory_bottlenecks) > 0 or len(memory_recommendations) > 0

        analyzer.stop_monitoring()


class TestPracticalOptimizations:
    """Test practical optimization strategies"""

    def test_adaptive_cache(self):
        """Test adaptive caching strategy"""
        cache = AdaptiveCache(max_size_mb=1)

        # Test basic caching
        def compute(x):
            time.sleep(0.01)
            return x * 2

        # First call - miss
        start = time.time()
        result1 = cache.get("test_key", lambda: compute(42))
        time1 = time.time() - start

        # Second call - hit
        start = time.time()
        result2 = cache.get("test_key", lambda: compute(42))
        time2 = time.time() - start

        assert result1 == result2 == 84
        assert time2 < time1 * 0.5  # Should be much faster

        metrics = cache.get_metrics()
        assert metrics["hits"] == 1
        assert metrics["misses"] == 1
        assert metrics["hit_rate"] == 0.5

    def test_object_pooling(self):
        """Test object pooling efficiency"""

        class TestObject:
            def __init__(self):
                self.data = [0] * 1000
                time.sleep(0.001)  # Simulate expensive init

        pool = ObjectPool(
            factory=TestObject,
            max_size=10,
            reset_fn=lambda obj: setattr(obj, "data", [0] * 1000),
        )

        # Measure allocation time
        start = time.time()
        objects1 = [pool.acquire() for _ in range(5)]
        time1 = time.time() - start

        # Release objects
        for obj in objects1:
            pool.release(obj)

        # Reacquire - should be faster
        start = time.time()
        objects2 = [pool.acquire() for _ in range(5)]
        time2 = time.time() - start

        assert time2 < time1 * 0.5  # Reuse should be faster

        metrics = pool.get_metrics()
        assert metrics["reuses"] >= 5
        assert metrics["reuse_rate"] > 0

    def test_computation_reuse(self):
        """Test computation reuse and memoization"""
        reuse = ComputationReuse(max_cache_size=100)

        call_count = 0

        @reuse.memoize("test")
        def expensive_function(n):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)
            return n * n

        # First calls
        result1 = expensive_function(10)
        result2 = expensive_function(10)  # Should use cache
        result3 = expensive_function(20)

        assert result1 == 100
        assert result2 == 100
        assert result3 == 400
        assert call_count == 2  # Only computed twice

        metrics = reuse.get_metrics()
        assert metrics["computations_saved"] == 1
        assert metrics["hit_rate"] > 0

    def test_swarm_communication_optimization(self):
        """Test swarm communication compression"""
        # Test various payload sizes
        test_cases = [
            {"small": "data"},  # Small payload
            {"medium": "x" * 1000},  # Medium payload
            {"large": list(range(1000))},  # Large payload
        ]

        for payload in test_cases:
            # Optimize
            optimized = optimize_swarm_communication(payload)

            # Deserialize
            restored = deserialize_swarm_message(optimized)

            # Verify correctness
            assert restored == payload

            # Check compression for large payloads
            json_size = len(json.dumps(payload).encode())
            if json_size > 1024:
                # Should be compressed
                assert optimized[0] == ord("Z")
                assert len(optimized) < json_size

    def test_resource_manager_integration(self):
        """Test integrated resource manager"""
        manager = ResourceManager()

        # Test computation optimization
        def compute_square(x):
            time.sleep(0.01)
            return x * x

        # First computation
        result1 = manager.optimize_computation(
            "square_100",
            lambda: compute_square(100),
            {"deterministic": True, "cache_ttl": 60},
        )

        # Second computation - should use cache
        start = time.time()
        result2 = manager.optimize_computation(
            "square_100", lambda: compute_square(100), {"deterministic": True}
        )
        elapsed = time.time() - start

        assert result1 == result2 == 10000
        assert elapsed < 0.005  # Should be from cache

        # Get comprehensive metrics
        all_metrics = manager.get_all_metrics()
        assert "cache" in all_metrics
        assert "reuse" in all_metrics

        # Generate report
        report = manager.create_resource_report()
        assert "CACHE EFFICIENCY" in report
        assert "COMPUTATION REUSE" in report


@pytest.mark.integration
class TestFullSystemIntegration:
    """Test full system integration across all components"""

    def test_end_to_end_state_management(self):
        """Test complete state management workflow"""
        # Initialize all components
        event_store = EventStore()
        state_manager = DistributedStateManager(
            "integration-node", num_shards=4, event_store=event_store
        )
        resource_manager = ResourceManager()
        analyzer = ResourceEfficiencyAnalyzer()

        analyzer.start_monitoring()

        # Simulate agent workflow
        agent = AIAgentAggregate("agent-001", event_store)
        agent.create_agent(["reasoning", "memory", "learning"])

        # Process tasks with state management
        for i in range(10):
            # Assign task
            task_id = f"task-{i:03d}"
            agent.assign_task(task_id, {"type": "compute", "input": i})

            # Store intermediate state
            state_manager.set(
                f"task_state_{task_id}",
                {"status": "processing", "progress": 0},
                StateType.HOT,
            )

            # Simulate processing with optimization
            result = resource_manager.optimize_computation(
                f"task_computation_{task_id}", lambda: i * i, {"deterministic": True}
            )

            # Update state
            state_manager.set(
                f"task_state_{task_id}",
                {"status": "completed", "result": result},
                StateType.WARM,
            )

            # Complete task
            agent.complete_task(task_id, {"result": result})

        # Commit all events
        agent.commit_events()

        # Analyze efficiency
        efficiency_report = analyzer.analyze_efficiency(duration_hours=0.001)

        # Verify system state
        assert agent.state == "idle"  # All tasks completed
        assert len(agent.active_tasks) == 0

        # Verify state persistence
        state_stats = state_manager.get_global_stats()
        assert state_stats["total_keys"] == 20  # 2 states per task

        # Verify optimization effectiveness
        resource_metrics = resource_manager.get_all_metrics()
        cache_metrics = resource_metrics["cache"]
        assert cache_metrics["hit_rate"] > 0  # Some cache hits

        # Cleanup
        analyzer.stop_monitoring()
        state_manager.shutdown()

    def test_failure_recovery(self):
        """Test system recovery from failures"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/events.db"

            # Phase 1: Create initial state
            store1 = EventStore(db_path)
            manager1 = DistributedStateManager("recovery-node", event_store=store1)

            # Create agent and state
            agent1 = AIAgentAggregate("agent-recovery", store1)
            agent1.create_agent(["skill1", "skill2"])
            agent1.assign_task("critical-task", {"important": True})
            agent1.commit_events()

            # Store critical state
            manager1.set("critical_data", {"value": 42}, StateType.HOT)
            manager1.set("checkpoint", {"stage": "processing"}, StateType.HOT)

            # Simulate crash
            manager1.shutdown()

            # Phase 2: Recovery
            store2 = EventStore(db_path)
            manager2 = DistributedStateManager("recovery-node", event_store=store2)

            # Recover agent state
            agent2 = AIAgentAggregate("agent-recovery", store2)
            assert "critical-task" in agent2.active_tasks
            assert agent2.capabilities == ["skill1", "skill2"]

            # Recover distributed state
            assert manager2.get("critical_data") == {"value": 42}
            assert manager2.get("checkpoint") == {"stage": "processing"}

            # System recovered successfully
            manager2.shutdown()


if __name__ == "__main__":
    # Run basic tests
    print("Running Symbiotic Swarm Integration Tests...\n")

    # Test Event Sourcing
    print("Testing Event Sourcing...")
    event_tests = TestEventSourcingIntegration()
    event_tests.test_event_store_persistence()
    event_tests.test_event_replay_recovery()
    event_tests.test_temporal_queries()
    print("✓ Event Sourcing tests passed\n")

    # Test Distributed State Manager
    print("Testing Distributed State Manager...")
    state_tests = TestDistributedStateManager()
    state_tests.test_basic_state_operations()
    state_tests.test_state_type_optimization()
    state_tests.test_concurrent_access()
    print("✓ Distributed State Manager tests passed\n")

    # Test Resource Efficiency
    print("Testing Resource Efficiency Analyzer...")
    efficiency_tests = TestResourceEfficiencyAnalyzer()
    efficiency_tests.test_resource_monitoring()
    efficiency_tests.test_efficiency_analysis()
    print("✓ Resource Efficiency tests passed\n")

    # Test Practical Optimizations
    print("Testing Practical Optimizations...")
    optimization_tests = TestPracticalOptimizations()
    optimization_tests.test_adaptive_cache()
    optimization_tests.test_object_pooling()
    optimization_tests.test_computation_reuse()
    optimization_tests.test_swarm_communication_optimization()
    print("✓ Practical Optimization tests passed\n")

    # Test Full Integration
    print("Testing Full System Integration...")
    integration_tests = TestFullSystemIntegration()
    integration_tests.test_end_to_end_state_management()
    integration_tests.test_failure_recovery()
    print("✓ Full Integration tests passed\n")

    print("All tests completed successfully! ✨")
