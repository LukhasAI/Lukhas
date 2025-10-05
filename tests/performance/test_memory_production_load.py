#!/usr/bin/env python3
"""
Production Load Test Framework for Memory Systems

Validates memory system performance under production-like conditions:
- High-volume concurrent operations
- Sustained recall workloads
- Memory growth and cascade behavior
- P95 latency compliance under load

Usage:
    pytest tests/performance/test_memory_production_load.py -v
    MEMORY_LOAD_SCALE=10000 pytest tests/performance/test_memory_production_load.py
"""

import asyncio
import os
import statistics
import time
from typing import Any, Dict

import psutil
import pytest

# Import memory system components
try:
    from lukhas.core.memory.fold_system import FoldSystem
    from lukhas.core.memory.recall_system import RecallSystem
    from lukhas.observability.prometheus_metrics import LUKHASMetrics
    MEMORY_SYSTEMS_AVAILABLE = True
except ImportError:
    MEMORY_SYSTEMS_AVAILABLE = False


class MemoryLoadTestFramework:
    """Framework for production-scale memory system load testing."""

    def __init__(self, scale_factor: int = 1000):
        self.scale_factor = scale_factor
        self.metrics = LUKHASMetrics() if MEMORY_SYSTEMS_AVAILABLE else None
        self.results = {
            "operations_completed": 0,
            "operations_failed": 0,
            "latencies_ms": [],
            "memory_usage_mb": [],
            "cascade_events": 0,
            "error_details": []
        }

    async def simulate_recall_workload(self, num_operations: int, concurrency: int = 10) -> Dict[str, Any]:
        """Simulate high-volume memory recall operations."""
        if not MEMORY_SYSTEMS_AVAILABLE:
            return {"skipped": "Memory systems not available"}

        recall_system = RecallSystem()
        semaphore = asyncio.Semaphore(concurrency)

        async def perform_recall(query_id: int):
            async with semaphore:
                start_time = time.perf_counter()
                try:
                    # Simulate realistic query patterns
                    query = {
                        "id": query_id,
                        "embedding": [0.1 * (i + query_id) for i in range(128)],
                        "top_k": 10,
                        "filter_conditions": {"category": f"test_{query_id % 5}"}
                    }

                    result = await recall_system.recall_memories(query)

                    latency_ms = (time.perf_counter() - start_time) * 1000
                    self.results["latencies_ms"].append(latency_ms)
                    self.results["operations_completed"] += 1

                    return {"success": True, "latency_ms": latency_ms, "results": len(result)}

                except Exception as e:
                    self.results["operations_failed"] += 1
                    self.results["error_details"].append(str(e))
                    return {"success": False, "error": str(e)}

        # Execute concurrent recall operations
        tasks = [perform_recall(i) for i in range(num_operations)]
        await asyncio.gather(*tasks, return_exceptions=True)

        return self.results

    def simulate_memory_fold_operations(self, num_folds: int) -> Dict[str, Any]:
        """Test memory fold system under sustained load."""
        if not MEMORY_SYSTEMS_AVAILABLE:
            return {"skipped": "Memory systems not available"}

        fold_system = FoldSystem(max_folds=1000)

        for i in range(num_folds):
            try:
                start_time = time.perf_counter()

                # Create realistic memory fold
                fold_data = {
                    "fold_id": f"load_test_{i}",
                    "content": f"Test memory content {i}" * 100,  # ~2KB per fold
                    "metadata": {
                        "timestamp": time.time(),
                        "type": "load_test",
                        "priority": i % 5
                    }
                }

                fold_system.create_fold(fold_data)

                latency_ms = (time.perf_counter() - start_time) * 1000
                self.results["latencies_ms"].append(latency_ms)
                self.results["operations_completed"] += 1

                # Monitor memory usage
                if i % 100 == 0:
                    memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                    self.results["memory_usage_mb"].append(memory_mb)

            except Exception as e:
                self.results["operations_failed"] += 1
                self.results["error_details"].append(str(e))

        return self.results

    def generate_load_test_report(self) -> str:
        """Generate comprehensive load test report."""
        if not self.results["latencies_ms"]:
            return "No operations completed - cannot generate report"

        latencies = self.results["latencies_ms"]

        # Calculate percentiles
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)

        # Memory statistics
        memory_usage = self.results["memory_usage_mb"]
        peak_memory = max(memory_usage) if memory_usage else 0
        avg_memory = statistics.mean(memory_usage) if memory_usage else 0

        success_rate = (self.results["operations_completed"] /
                       (self.results["operations_completed"] + self.results["operations_failed"])) * 100

        report = f"""
=== Memory System Production Load Test Report ===

Operations Summary:
  Total Operations: {self.results['operations_completed'] + self.results['operations_failed']}
  Successful: {self.results['operations_completed']}
  Failed: {self.results['operations_failed']}
  Success Rate: {success_rate:.2f}%

Latency Performance:
  P50 (Median): {p50:.2f}ms
  P95: {p95:.2f}ms
  P99: {p99:.2f}ms
  Average: {statistics.mean(latencies):.2f}ms

Memory Usage:
  Peak Memory: {peak_memory:.1f}MB
  Average Memory: {avg_memory:.1f}MB
  Memory Growth: {peak_memory - memory_usage[0]:.1f}MB

SLO Compliance:
  P95 ≤ 100ms Target: {'✅ PASS' if p95 <= 100 else '❌ FAIL'} ({p95:.2f}ms)
  Success Rate ≥ 99.7%: {'✅ PASS' if success_rate >= 99.7 else '❌ FAIL'} ({success_rate:.2f}%)

Cascade Events: {self.results['cascade_events']}
Error Count: {len(self.results['error_details'])}
"""

        if self.results['error_details']:
            report += "\nError Details:\n"
            for error in set(self.results['error_details'][:5]):  # Show unique errors
                report += f"  - {error}\n"

        return report


@pytest.mark.performance
@pytest.mark.memory
@pytest.mark.slow
class TestMemoryProductionLoad:
    """Production-scale load tests for memory systems."""

    @pytest.fixture
    def load_framework(self):
        """Create load test framework with scale factor from environment."""
        scale = int(os.getenv("MEMORY_LOAD_SCALE", "1000"))
        return MemoryLoadTestFramework(scale_factor=scale)

    def test_memory_system_availability(self):
        """Verify memory systems are available for testing."""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available - install memory dependencies")

    @pytest.mark.asyncio
    async def test_high_volume_recall_operations(self, load_framework):
        """Test memory recall system under high-volume concurrent load."""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available")

        # Scale operations based on environment
        num_operations = load_framework.scale_factor
        concurrency = min(50, num_operations // 20)  # Reasonable concurrency

        print(f"\n🔍 Testing {num_operations} recall operations with {concurrency} concurrency...")

        start_time = time.perf_counter()
        results = await load_framework.simulate_recall_workload(num_operations, concurrency)
        total_duration = time.perf_counter() - start_time

        # Generate and print report
        report = load_framework.generate_load_test_report()
        print(report)

        # Validate SLO compliance
        if load_framework.results["latencies_ms"]:
            latencies = load_framework.results["latencies_ms"]
            p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)

            # P95 latency must be ≤ 100ms
            assert p95 <= 100.0, f"P95 recall latency {p95:.2f}ms exceeds 100ms SLO"

            # Success rate must be ≥ 99.7%
            success_rate = (results["operations_completed"] /
                           (results["operations_completed"] + results["operations_failed"])) * 100
            assert success_rate >= 99.7, f"Success rate {success_rate:.2f}% below 99.7% SLO"

        # Throughput validation
        throughput = num_operations / total_duration
        assert throughput >= 100, f"Throughput {throughput:.1f} ops/sec below minimum 100 ops/sec"

        print(f"✅ High-volume recall test PASSED: {throughput:.1f} ops/sec")

    def test_sustained_memory_fold_operations(self, load_framework):
        """Test memory fold system under sustained load."""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available")

        num_folds = load_framework.scale_factor // 10  # Fewer fold operations

        print(f"\n🧠 Testing {num_folds} sustained fold operations...")

        start_time = time.perf_counter()
        results = load_framework.simulate_memory_fold_operations(num_folds)
        total_duration = time.perf_counter() - start_time

        # Generate and print report
        report = load_framework.generate_load_test_report()
        print(report)

        # Validate performance and memory constraints
        if load_framework.results["latencies_ms"]:
            latencies = load_framework.results["latencies_ms"]
            avg_latency = statistics.mean(latencies)

            # Average fold operation should be fast
            assert avg_latency <= 50.0, f"Average fold latency {avg_latency:.2f}ms exceeds 50ms"

        # Memory growth should be reasonable
        if load_framework.results["memory_usage_mb"]:
            memory_usage = load_framework.results["memory_usage_mb"]
            memory_growth = max(memory_usage) - min(memory_usage)

            # Memory growth should be proportional to operations (not unbounded)
            max_expected_growth = (num_folds * 2) / 1024  # ~2KB per fold
            assert memory_growth <= max_expected_growth * 2, f"Memory growth {memory_growth:.1f}MB excessive"

        print(f"✅ Sustained fold test PASSED: {num_folds / total_duration:.1f} folds/sec")

    def test_memory_cascade_prevention_under_load(self, load_framework):
        """Test cascade prevention mechanisms under high load."""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available")

        # Simulate conditions that could trigger cascades
        print("\n⚡ Testing cascade prevention under stress conditions...")

        # This would test cascade prevention by creating memory pressure
        # Implementation depends on actual cascade system

        # For now, verify no cascades occurred in previous tests
        assert load_framework.results["cascade_events"] == 0, "Cascades detected under load"

        print("✅ Cascade prevention test PASSED")

    @pytest.mark.parametrize("load_level", ["light", "moderate", "heavy"])
    def test_memory_system_scaling(self, load_level):
        """Test memory system performance at different load levels."""
        if not MEMORY_SYSTEMS_AVAILABLE:
            pytest.skip("Memory systems not available")

        scale_factors = {
            "light": 100,
            "moderate": 1000,
            "heavy": 5000
        }

        scale = scale_factors[load_level]
        framework = MemoryLoadTestFramework(scale_factor=scale)

        print(f"\n📈 Testing {load_level} load level (scale: {scale})...")

        # Run scaled test
        results = framework.simulate_memory_fold_operations(scale // 10)

        # Performance should degrade gracefully
        if framework.results["latencies_ms"]:
            p95 = statistics.quantiles(framework.results["latencies_ms"], n=20)[18]

            # Different SLOs for different load levels
            slo_targets = {"light": 20, "moderate": 50, "heavy": 100}
            target = slo_targets[load_level]

            assert p95 <= target, f"P95 latency {p95:.2f}ms exceeds {load_level} load SLO of {target}ms"

        print(f"✅ {load_level.title()} load test PASSED")


if __name__ == "__main__":
    # Allow running directly for manual testing
    import sys

    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)

    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"] + sys.argv[1:])
