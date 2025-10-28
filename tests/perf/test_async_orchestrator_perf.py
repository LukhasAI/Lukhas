# tests/perf/test_async_orchestrator_perf.py
"""
Performance benchmarks for async orchestrator (env-gated).
"""

import asyncio
import os
import statistics as stats
import time

import pytest
from core.registry import register
from labs.core.orchestration.async_orchestrator import AsyncOrchestrator
from nodes.example_nodes import DecisionNode, IntentNode, ThoughtNode


@pytest.fixture
def fast_orchestrator():
    """Create orchestrator optimized for performance."""
    config = {"MATRIZ_ASYNC": "1"}
    orch = AsyncOrchestrator(config)

    # Configure with aggressive timeouts for speed
    orch.configure_stages([
        {"name": "INTENT", "timeout_ms": 50, "max_retries": 1},
        {"name": "THOUGHT", "timeout_ms": 75, "max_retries": 1},
        {"name": "DECISION", "timeout_ms": 100, "max_retries": 1}
    ])

    return orch


@pytest.fixture
def register_fast_nodes():
    """Register optimized test nodes."""
    register("node:intent", IntentNode())
    register("node:thought", ThoughtNode())
    register("node:decision", DecisionNode())
    yield


@pytest.mark.skipif(
    os.getenv("LUKHAS_PERF") != "1",
    reason="Performance tests only run with LUKHAS_PERF=1"
)
@pytest.mark.asyncio
async def test_pipeline_p95_under_budget(fast_orchestrator, register_fast_nodes):
    """Test that pipeline p95 latency is under 250ms budget."""
    latencies = []
    context = {"query": "What is the capital of France?"}

    # Warmup runs
    for _ in range(5):
        await fast_orchestrator.process_query(context)

    # Benchmark runs
    for _ in range(100):
        start_time = time.perf_counter()
        result = await fast_orchestrator.process_query(context)
        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)

        # Ensure we got a valid result
        assert result is not None

    # Calculate statistics
    latencies.sort()
    p50 = latencies[int(0.5 * len(latencies))]
    p95 = latencies[int(0.95 * len(latencies))]
    p99 = latencies[int(0.99 * len(latencies))]
    mean = stats.mean(latencies)

    print("\nPerformance Results:")
    print(f"  Mean: {mean:.2f}ms")
    print(f"  P50:  {p50:.2f}ms")
    print(f"  P95:  {p95:.2f}ms")
    print(f"  P99:  {p99:.2f}ms")

    # Assert p95 budget
    assert p95 < 250.0, f"P95 latency {p95:.2f}ms exceeds 250ms budget"

    # Additional performance checks
    assert mean < 100.0, f"Mean latency {mean:.2f}ms is too high"
    assert p50 < 75.0, f"P50 latency {p50:.2f}ms is too high"


@pytest.mark.skipif(
    os.getenv("LUKHAS_PERF") != "1",
    reason="Performance tests only run with LUKHAS_PERF=1"
)
@pytest.mark.asyncio
async def test_throughput_benchmark(fast_orchestrator, register_fast_nodes):
    """Test concurrent throughput."""
    context = {"query": "Test query"}
    concurrent_requests = 20

    start_time = time.perf_counter()

    # Run concurrent requests
    tasks = [
        fast_orchestrator.process_query(context)
        for _ in range(concurrent_requests)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.perf_counter()
    total_time = end_time - start_time

    # Check that most requests succeeded
    successful = sum(1 for r in results if not isinstance(r, Exception))
    success_rate = successful / len(results)

    throughput_rps = concurrent_requests / total_time

    print("\nThroughput Results:")
    print(f"  Concurrent requests: {concurrent_requests}")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Success rate: {success_rate:.2%}")
    print(f"  Throughput: {throughput_rps:.1f} req/s")

    assert success_rate >= 0.9, f"Success rate {success_rate:.2%} too low"
    assert throughput_rps >= 50.0, f"Throughput {throughput_rps:.1f} req/s too low"


@pytest.mark.skipif(
    os.getenv("LUKHAS_PERF") != "1",
    reason="Performance tests only run with LUKHAS_PERF=1"
)
@pytest.mark.asyncio
async def test_memory_efficiency(fast_orchestrator, register_fast_nodes):
    """Test memory usage doesn't grow excessively."""
    import gc
    import tracemalloc

    tracemalloc.start()
    gc.collect()

    context = {"query": "Memory test"}

    # Baseline memory
    baseline_snapshot = tracemalloc.take_snapshot()

    # Run many operations
    for _ in range(1000):
        await fast_orchestrator.process_query(context)

        # Occasional cleanup
        if _ % 100 == 0:
            gc.collect()

    # Final memory check
    final_snapshot = tracemalloc.take_snapshot()
    top_stats = final_snapshot.compare_to(baseline_snapshot, 'lineno')

    total_diff = sum(stat.size_diff for stat in top_stats)
    total_diff_mb = total_diff / 1024 / 1024

    print("\nMemory Results:")
    print(f"  Memory difference: {total_diff_mb:.2f} MB")

    # Memory should not grow excessively
    assert total_diff_mb < 10.0, f"Memory growth {total_diff_mb:.2f}MB too high"

    tracemalloc.stop()


@pytest.mark.skipif(
    os.getenv("LUKHAS_PERF") != "1",
    reason="Performance tests only run with LUKHAS_PERF=1"
)
def test_cold_start_performance():
    """Test orchestrator initialization performance."""
    start_time = time.perf_counter()

    # Cold start
    config = {"MATRIZ_ASYNC": "1"}
    orchestrator = AsyncOrchestrator(config)
    orchestrator.configure_stages([
        {"name": "INTENT", "timeout_ms": 100},
        {"name": "THOUGHT", "timeout_ms": 100},
        {"name": "DECISION", "timeout_ms": 100}
    ])

    end_time = time.perf_counter()
    init_time_ms = (end_time - start_time) * 1000

    print("\nCold Start Results:")
    print(f"  Initialization time: {init_time_ms:.2f}ms")

    # Initialization should be fast
    assert init_time_ms < 50.0, f"Initialization time {init_time_ms:.2f}ms too slow"
