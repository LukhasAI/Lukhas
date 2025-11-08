"""
Performance tests for the MATRIZ cognitive engine.

Targets:
- <250ms p95 latency (critical path)
- <100MB memory usage
- 50+ operations/second throughput
"""

import asyncio
import gc
import os
import time

import numpy as np
import psutil
import pytest
from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator
from matriz.core.example_node import MathReasoningNode

# Mark all tests in this file as performance tests
pytestmark = pytest.mark.performance


@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for the module."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def orchestrator():
    """Provides a configured MATRIZ orchestrator for the test module."""
    orc = AsyncCognitiveOrchestrator(total_timeout=5.0)  # Generous timeout for performance testing
    math_node = MathReasoningNode()
    orc.register_node("math", math_node)
    return orc


class TestMatrizPerformance:
    """Performance and scalability tests for the MATRIZ Cognitive Engine."""

    @pytest.mark.asyncio
    async def test_latency_p95(self, orchestrator, benchmark):
        """Test p95 latency is below 250ms."""
        query = "what is 123 + 456 * 7"

        async def f():
            return await orchestrator.process_query(query)

        # Use pedantic to benchmark the async function correctly
        benchmark.pedantic(f, iterations=10, rounds=5)

        # Manually calculate p95 from raw data for robustness
        raw_data = benchmark.stats.stats.data
        assert raw_data, "Benchmark did not produce any data."
        p95 = np.percentile(raw_data, 95)

        print(f"p95 latency: {p95 * 1000:.2f}ms")
        assert p95 < 0.250

    @pytest.mark.asyncio
    async def test_throughput(self, orchestrator):
        """Test throughput is at least 50 ops/sec."""
        query = "what is 1 + 1"
        ops = 0
        start_time = time.monotonic()

        while time.monotonic() - start_time < 1.0:
            await orchestrator.process_query(query)
            ops += 1

        print(f"Throughput: {ops} ops/sec")
        assert ops >= 50

    @pytest.mark.asyncio
    async def test_memory_leak(self, orchestrator):
        """Test for memory leaks over a large number of operations."""
        query = "1+1"
        process = psutil.Process(os.getpid())

        # Warm-up run
        for _ in range(100):
            await orchestrator.process_query(query)

        gc.collect()
        mem_before = process.memory_info().rss

        # Main run
        iterations = 2000
        for i in range(iterations):
            await orchestrator.process_query(f"{i}+{i+1}")

        gc.collect()
        mem_after = process.memory_info().rss

        mem_increase_mb = (mem_after - mem_before) / (1024 * 1024)
        print(f"Memory increase after {iterations} iterations: {mem_increase_mb:.2f} MB")

        # Allow for some memory growth, but it should be well below the target
        assert mem_increase_mb < 100

    @pytest.mark.asyncio
    async def test_spike_load(self, orchestrator):
        """Test performance under a sudden spike of concurrent requests."""
        spike_count = 100
        queries = [f"what is {i}+{i}" for i in range(spike_count)]

        start_time = time.monotonic()
        tasks = [orchestrator.process_query(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.monotonic() - start_time

        print(f"Spike test with {spike_count} concurrent requests finished in {duration:.2f}s")

        # Check that no exceptions were raised
        assert not any(isinstance(r, Exception) for r in results)
        # Ensure the spike was handled in a reasonable time (e.g., < 2 seconds)
        assert duration < 2.0

    @pytest.mark.asyncio
    async def test_sustained_load(self, orchestrator):
        """Test performance under a sustained load for a period of time."""
        duration_seconds = 5
        latencies = []

        start_time = time.monotonic()
        while time.monotonic() - start_time < duration_seconds:
            query_start_time = time.monotonic()
            await orchestrator.process_query("1+1")
            latencies.append(time.monotonic() - query_start_time)

        # Analyze the second half of the run to see if performance degraded
        second_half_latencies = latencies[len(latencies)//2:]
        avg_latency = sum(second_half_latencies) / len(second_half_latencies)

        print(f"Sustained load test over {duration_seconds}s: Average latency (2nd half) = {avg_latency*1000:.2f}ms")

        # Ensure average latency remains low, indicating no significant degradation
        assert avg_latency < 0.100  # 100ms
