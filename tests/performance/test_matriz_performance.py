import asyncio
import gc
import os
import time

import numpy as np
import psutil
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

# Use the lowercase 'matriz' import path as per memory to avoid ModuleNotFoundError
from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator
from matriz.core.example_node import MathReasoningNode

# Performance Targets from the user request
P95_LATENCY_TARGET_MS = 250
MEMORY_TARGET_MB = 100
THROUGHPUT_TARGET_OPS_PER_SEC = 50
CONCURRENCY_TARGET = 10

def get_memory_usage_mb():
    """Returns the current process's memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

@pytest.fixture(scope="module")
def orchestrator():
    """Fixture to create and register a MATRIZ orchestrator for the test module."""
    orc = AsyncCognitiveOrchestrator(total_timeout=2.0)  # Generous timeout for tests
    math_node = MathReasoningNode()
    orc.register_node("math", math_node)
    return orc

# 1. Latency and Throughput Tests

@pytest.mark.asyncio
async def test_latency_and_throughput(benchmark: BenchmarkFixture, orchestrator: AsyncCognitiveOrchestrator):
    """
    Measures p95 latency and throughput for a standard cognitive operation.
    """
    query = "what is (5 + 5) * 2 / 4"

    async def run_query():
        return await orchestrator.process_query_async(query)

    # Use benchmark.pedantic with an inner async function for correct async benchmarking
    benchmark.pedantic(run_query, iterations=100, rounds=10)

    # Assert p95 latency is within the target
    # Correctly calculate p95 from the raw timing data
    timings_ms = np.array(benchmark.stats.stats.data) * 1000  # convert seconds to ms
    p95_latency_ms = np.percentile(timings_ms, 95)

    print(f"P95 Latency: {p95_latency_ms:.2f} ms")
    assert p95_latency_ms < P95_LATENCY_TARGET_MS, f"P95 latency {p95_latency_ms:.2f}ms exceeds {P95_LATENCY_TARGET_MS}ms target"

    # Assert throughput meets the target
    ops_per_sec = benchmark.stats.get('ops')
    if ops_per_sec is not None:
        print(f"Throughput: {ops_per_sec:.2f} ops/sec")
        assert ops_per_sec >= THROUGHPUT_TARGET_OPS_PER_SEC, f"Throughput {ops_per_sec:.2f} ops/sec below {THROUGHPUT_TARGET_OPS_PER_SEC}"


# 2. Memory Test

def test_memory_usage():
    """
    Ensures that a batch operation stays under the memory increase target.
    """
    gc.collect()
    mem_before = get_memory_usage_mb()

    # Create a fresh orchestrator to isolate memory usage
    orc = AsyncCognitiveOrchestrator()
    math_node = MathReasoningNode()
    orc.register_node("math", math_node)

    async def process_batch():
        # Process a batch of 100 simple queries
        tasks = [orc.process_query_async(f"1 + {i}") for i in range(100)]
        await asyncio.gather(*tasks)

    asyncio.run(process_batch())

    gc.collect()
    mem_after = get_memory_usage_mb()
    mem_increase = mem_after - mem_before

    print(f"Memory increase: {mem_increase:.2f} MB")

    # Clean up to release memory
    del orc
    del math_node
    gc.collect()

    assert mem_increase < MEMORY_TARGET_MB, f"Memory usage increase {mem_increase:.2f}MB exceeds {MEMORY_TARGET_MB}MB target"

# 3. Concurrency Test

@pytest.mark.asyncio
async def test_concurrent_operations(orchestrator: AsyncCognitiveOrchestrator):
    """
    Tests the orchestrator's ability to handle multiple (20) concurrent requests.
    """
    num_requests = CONCURRENCY_TARGET * 2

    start_time = time.perf_counter()

    tasks = [orchestrator.process_query_async(f"3 * {i}") for i in range(num_requests)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    duration = time.perf_counter() - start_time
    print(f"Processed {num_requests} concurrent requests in {duration:.2f}s")

    # Verify all requests completed successfully
    assert len(results) == num_requests
    for i, res in enumerate(results):
        assert not isinstance(res, Exception), f"Request {i} failed with exception: {res}"
        assert "error" not in res, f"Request {i} failed with error: {res.get('error')}"
        assert "answer" in res
