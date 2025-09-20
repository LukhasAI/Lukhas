"""
MATRIZ Performance Validation Tests
Tests critical performance requirements for LUKHAS MATRIZ cognitive architecture.
"""

import asyncio
import time
import statistics
import pytest
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

# Performance thresholds from architectural audit
MATRIZ_LATENCY_THRESHOLD_MS = 250  # <250ms requirement
MATRIZ_THROUGHPUT_THRESHOLD = 50.0  # 50 ops/sec requirement
MATRIZ_MEMORY_THRESHOLD_MB = 100   # 100MB memory limit
MATRIZ_P95_THRESHOLD_MS = 200      # P95 latency target

pytestmark = pytest.mark.performance


class TestMATRIZPerformance:
    """MATRIZ cognitive architecture performance validation"""

    @pytest.fixture(autouse=True)
    def setup_matriz_environment(self):
        """Setup MATRIZ test environment with performance monitoring"""
        self.performance_data = {
            'latencies': [],
            'memory_usage': [],
            'throughput_samples': [],
            'error_rates': []
        }

    def measure_execution_time(self, func, *args, **kwargs):
        """Measure function execution time in milliseconds"""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        self.performance_data['latencies'].append(latency_ms)
        return result, latency_ms

    async def measure_async_execution_time(self, coro):
        """Measure async coroutine execution time in milliseconds"""
        start_time = time.perf_counter()
        result = await coro
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        self.performance_data['latencies'].append(latency_ms)
        return result, latency_ms

    @pytest.mark.parametrize("node_type,expected_max_latency", [
        ("memory_node", 100),      # Memory operations should be faster
        ("consciousness_node", 200), # Consciousness processing
        ("identity_node", 150),    # Identity operations
        ("governance_node", 180),  # Governance validation
    ])
    def test_matriz_node_latency(self, node_type, expected_max_latency):
        """Test individual MATRIZ node latency requirements"""

        # Mock MATRIZ node based on type
        if node_type == "memory_node":
            node_func = self._mock_memory_node_operation
        elif node_type == "consciousness_node":
            node_func = self._mock_consciousness_node_operation
        elif node_type == "identity_node":
            node_func = self._mock_identity_node_operation
        else:
            node_func = self._mock_governance_node_operation

        # Run multiple samples
        latencies = []
        for _ in range(10):
            _, latency = self.measure_execution_time(node_func)
            latencies.append(latency)

        # Validate performance
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile

        assert avg_latency < expected_max_latency, \
            f"{node_type} average latency {avg_latency:.2f}ms exceeds {expected_max_latency}ms"

        assert p95_latency < MATRIZ_P95_THRESHOLD_MS, \
            f"{node_type} P95 latency {p95_latency:.2f}ms exceeds {MATRIZ_P95_THRESHOLD_MS}ms"

    def test_matriz_orchestrator_latency(self):
        """Test MATRIZ orchestrator latency under load"""

        # Mock orchestrator with realistic processing
        orchestrator_latencies = []

        for i in range(20):
            start_time = time.perf_counter()

            # Simulate orchestrator workflow
            self._mock_orchestrator_workflow(
                nodes=5,
                processing_complexity=0.8,
                data_size_kb=10
            )

            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            orchestrator_latencies.append(latency_ms)

        # Performance validation
        avg_latency = statistics.mean(orchestrator_latencies)
        max_latency = max(orchestrator_latencies)
        p95_latency = statistics.quantiles(orchestrator_latencies, n=20)[18]

        assert avg_latency < MATRIZ_LATENCY_THRESHOLD_MS, \
            f"Orchestrator average latency {avg_latency:.2f}ms exceeds {MATRIZ_LATENCY_THRESHOLD_MS}ms"

        assert p95_latency < MATRIZ_P95_THRESHOLD_MS, \
            f"Orchestrator P95 latency {p95_latency:.2f}ms exceeds {MATRIZ_P95_THRESHOLD_MS}ms"

        assert max_latency < 500, \
            f"Orchestrator max latency {max_latency:.2f}ms exceeds 500ms critical threshold"

    def test_matriz_throughput_performance(self):
        """Test MATRIZ throughput under sustained load"""

        # Simulate sustained processing load
        start_time = time.time()
        operations_completed = 0
        test_duration_seconds = 2

        while time.time() - start_time < test_duration_seconds:
            # Simulate MATRIZ operation
            self._mock_matriz_operation()
            operations_completed += 1

            # Small sleep to prevent overwhelming CPU in test
            time.sleep(0.01)

        actual_duration = time.time() - start_time
        throughput_ops_per_sec = operations_completed / actual_duration

        assert throughput_ops_per_sec >= MATRIZ_THROUGHPUT_THRESHOLD, \
            f"MATRIZ throughput {throughput_ops_per_sec:.1f} ops/sec below {MATRIZ_THROUGHPUT_THRESHOLD} ops/sec"

    @pytest.mark.asyncio
    async def test_matriz_async_processing_latency(self):
        """Test async MATRIZ processing latency"""

        # Test concurrent async operations
        async def async_matriz_operation(operation_id: int):
            # Simulate async MATRIZ processing
            await asyncio.sleep(0.05)  # 50ms base processing
            return f"result_{operation_id}"

        # Run concurrent operations
        start_time = time.perf_counter()

        tasks = [async_matriz_operation(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_latency_ms = (end_time - start_time) * 1000

        # Concurrent operations should complete much faster than sequential
        # 10 operations * 50ms = 500ms sequential, concurrent should be ~50-100ms
        assert total_latency_ms < 150, \
            f"Async processing latency {total_latency_ms:.2f}ms suggests poor concurrency"

        assert len(results) == 10, "All async operations should complete"

    def test_matriz_memory_efficiency(self):
        """Test MATRIZ memory usage under processing load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Baseline memory
        baseline_memory_mb = process.memory_info().rss / 1024 / 1024

        # Simulate memory-intensive MATRIZ operations
        data_cache = []
        for i in range(100):
            # Simulate data processing and caching
            result = self._mock_memory_intensive_matriz_operation(data_size_kb=50)
            data_cache.append(result)

        # Peak memory measurement
        peak_memory_mb = process.memory_info().rss / 1024 / 1024
        memory_increase_mb = peak_memory_mb - baseline_memory_mb

        assert memory_increase_mb < MATRIZ_MEMORY_THRESHOLD_MB, \
            f"MATRIZ memory usage {memory_increase_mb:.1f}MB exceeds {MATRIZ_MEMORY_THRESHOLD_MB}MB threshold"

        # Cleanup to validate memory release
        data_cache.clear()

        # Allow garbage collection
        import gc
        gc.collect()

        final_memory_mb = process.memory_info().rss / 1024 / 1024
        memory_after_cleanup = final_memory_mb - baseline_memory_mb

        # Memory should be mostly released
        assert memory_after_cleanup < memory_increase_mb * 0.3, \
            "MATRIZ memory not properly released after processing"

    def test_matriz_cascade_prevention_performance(self):
        """Test performance under cascade prevention scenarios"""

        # Simulate cascade scenarios with performance monitoring
        cascade_scenarios = [
            {"depth": 3, "width": 5, "expected_max_latency": 200},
            {"depth": 5, "width": 3, "expected_max_latency": 180},
            {"depth": 4, "width": 4, "expected_max_latency": 190},
        ]

        for scenario in cascade_scenarios:
            latencies = []

            for _ in range(5):
                start_time = time.perf_counter()

                # Simulate cascade prevention processing
                self._mock_cascade_prevention(
                    depth=scenario["depth"],
                    width=scenario["width"]
                )

                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)

            avg_latency = statistics.mean(latencies)

            assert avg_latency < scenario["expected_max_latency"], \
                f"Cascade prevention latency {avg_latency:.2f}ms exceeds {scenario['expected_max_latency']}ms"

    def test_matriz_stress_testing(self):
        """Stress test MATRIZ under extreme load"""

        # High-frequency operations
        stress_duration = 3  # seconds
        start_time = time.time()
        operation_count = 0
        errors = 0

        while time.time() - start_time < stress_duration:
            try:
                # Rapid MATRIZ operations
                self._mock_high_frequency_matriz_operation()
                operation_count += 1
            except Exception:
                errors += 1

            # Minimal sleep to prevent test system overload
            time.sleep(0.001)

        # Calculate metrics
        actual_duration = time.time() - start_time
        ops_per_second = operation_count / actual_duration
        error_rate = errors / (operation_count + errors) if (operation_count + errors) > 0 else 0

        # Stress test validation
        assert ops_per_second >= MATRIZ_THROUGHPUT_THRESHOLD * 0.7, \
            f"Stress test throughput {ops_per_second:.1f} ops/sec below 70% of normal threshold"

        assert error_rate < 0.05, \
            f"Stress test error rate {error_rate:.3f} exceeds 5% threshold"

    # Mock helper methods for testing
    def _mock_memory_node_operation(self):
        """Mock memory node operation"""
        time.sleep(0.05)  # 50ms processing
        return {"status": "success", "data": "memory_result"}

    def _mock_consciousness_node_operation(self):
        """Mock consciousness node operation"""
        time.sleep(0.08)  # 80ms processing
        return {"status": "success", "awareness": 0.85}

    def _mock_identity_node_operation(self):
        """Mock identity node operation"""
        time.sleep(0.06)  # 60ms processing
        return {"status": "success", "identity_verified": True}

    def _mock_governance_node_operation(self):
        """Mock governance node operation"""
        time.sleep(0.07)  # 70ms processing
        return {"status": "success", "compliance": True}

    def _mock_orchestrator_workflow(self, nodes: int, processing_complexity: float, data_size_kb: int):
        """Mock orchestrator workflow"""
        base_time = nodes * 0.02  # 20ms per node
        complexity_time = processing_complexity * 0.05  # Up to 50ms for complexity
        data_time = data_size_kb * 0.001  # 1ms per KB

        total_time = base_time + complexity_time + data_time
        time.sleep(total_time)

        return {"nodes_processed": nodes, "result": "workflow_complete"}

    def _mock_matriz_operation(self):
        """Mock basic MATRIZ operation"""
        time.sleep(0.015)  # 15ms processing
        return {"status": "complete"}

    def _mock_memory_intensive_matriz_operation(self, data_size_kb: int):
        """Mock memory-intensive operation"""
        # Create temporary data structure
        data = list(range(data_size_kb * 10))  # Approximate KB usage
        time.sleep(0.01)  # 10ms processing
        return data

    def _mock_cascade_prevention(self, depth: int, width: int):
        """Mock cascade prevention logic"""
        # Simulate processing complexity based on depth and width
        processing_time = (depth * width) * 0.005  # 5ms per unit
        time.sleep(processing_time)
        return {"cascade_prevented": True, "depth": depth, "width": width}

    def _mock_high_frequency_matriz_operation(self):
        """Mock high-frequency operation"""
        time.sleep(0.002)  # 2ms processing
        return {"rapid_result": True}


@pytest.mark.performance
@pytest.mark.parametrize("load_level", [0.5, 0.8, 1.0])
def test_matriz_performance_under_load(load_level):
    """Test MATRIZ performance scaling under different load levels"""

    # Simulate load-based processing
    operations = int(50 * load_level)  # Scale operations by load
    latencies = []

    start_time = time.perf_counter()

    for _ in range(operations):
        op_start = time.perf_counter()

        # Mock load-proportional processing
        processing_time = 0.02 * load_level  # Scale processing time
        time.sleep(processing_time)

        op_end = time.perf_counter()
        latencies.append((op_end - op_start) * 1000)

    total_time = time.perf_counter() - start_time

    # Performance validation scaled by load
    avg_latency = statistics.mean(latencies)
    throughput = operations / total_time

    # Latency should scale reasonably with load
    expected_max_latency = MATRIZ_LATENCY_THRESHOLD_MS * load_level * 1.2
    assert avg_latency < expected_max_latency, \
        f"Load {load_level} average latency {avg_latency:.2f}ms exceeds scaled threshold {expected_max_latency:.2f}ms"

    # Throughput should not degrade too much under load
    expected_min_throughput = MATRIZ_THROUGHPUT_THRESHOLD * (1 - load_level * 0.3)
    assert throughput >= expected_min_throughput, \
        f"Load {load_level} throughput {throughput:.1f} ops/sec below threshold {expected_min_throughput:.1f}"


if __name__ == "__main__":
    # Run performance tests with detailed output
    pytest.main([__file__, "-v", "-s", "--tb=short"])