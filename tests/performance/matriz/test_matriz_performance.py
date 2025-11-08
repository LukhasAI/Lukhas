"""
MATRIZ Performance Validation Tests using pytest-benchmark.
Tests critical performance requirements for LUKHAS MATRIZ cognitive architecture.
"""

import asyncio
import gc
import os
import statistics
import time

import psutil
import pytest
from matriz.core.example_node import MathReasoningNode

# Use the actual MATRIZ components
from matriz.core.orchestrator import CognitiveOrchestrator

# Performance targets
P95_LATENCY_TARGET_MS = 250
MEMORY_USAGE_TARGET_MB = 100
THROUGHPUT_TARGET_OPS_PER_SEC = 50


# --- Fixtures ---

@pytest.fixture
def cognitive_orchestrator():
    """Returns a CognitiveOrchestrator with a concrete MathReasoningNode."""
    orchestrator = CognitiveOrchestrator()
    orchestrator.register_node("math", MathReasoningNode())
    # Add a default node to handle non-math queries
    from unittest.mock import MagicMock
    mock_facts_node = MagicMock()
    mock_facts_node.process.return_value = {"answer": "mocked fact"}
    orchestrator.register_node("facts", mock_facts_node)
    return orchestrator


# --- Performance Tests ---

def test_matriz_latency(benchmark, cognitive_orchestrator):
    """Benchmark the p95 latency of the MATRIZ engine."""

    def run_engine():
        cognitive_orchestrator.process_query("what is 5+5")

    benchmark.pedantic(run_engine, rounds=100, warmup_rounds=10)

    # pytest-benchmark automatically fails if stats are worse than last time.
    # We add an explicit check for our target.
    p95_latency_ms = statistics.quantiles(benchmark.stats.data, n=100)[94] * 1000
    assert p95_latency_ms < P95_LATENCY_TARGET_MS, f"P95 latency {p95_latency_ms:.2f}ms exceeds target of {P95_LATENCY_TARGET_MS}ms"


def test_matriz_memory_leak():
    """Test for memory leaks in the MATRIZ engine by checking memory reclamation."""
    process = psutil.Process(os.getpid())

    # Establish a baseline
    gc.collect()
    mem_before = process.memory_info().rss

    def run_workload():
        """Creates and uses an orchestrator in a limited scope."""
        orchestrator = CognitiveOrchestrator()
        orchestrator.register_node("math", MathReasoningNode())
        # Simulate a workload that builds up state in the orchestrator
        for i in range(1000):
            orchestrator.process_query(f"what is {i}+{i}")
        # Orchestrator goes out of scope here

    run_workload()

    # Explicitly trigger garbage collection to reclaim memory
    gc.collect()

    mem_after = process.memory_info().rss
    memory_increase_bytes = mem_after - mem_before

    # After the orchestrator is destroyed, memory should return to near baseline.
    # A small increase is acceptable for caching or other system reasons.
    assert memory_increase_bytes < (20 * 1024 * 1024), f"Memory leak detected: memory increased by {memory_increase_bytes / (1024*1024):.2f}MB after workload"


def test_matriz_throughput(benchmark, cognitive_orchestrator):
    """Benchmark the throughput of the MATRIZ engine."""

    def run_engine():
        cognitive_orchestrator.process_query("what is 5+5")

    benchmark(run_engine)

    ops_per_second = benchmark.stats.stats["ops"]
    assert ops_per_second > THROUGHPUT_TARGET_OPS_PER_SEC, f"Throughput of {ops_per_second:.2f} ops/sec is below target of {THROUGHPUT_TARGET_OPS_PER_SEC}"


@pytest.mark.asyncio
async def test_matriz_sustained_load(cognitive_orchestrator):
    """Test the MATRIZ engine under sustained load."""
    start_time = time.monotonic()
    duration_seconds = 5
    request_count = 0
    errors = 0

    while time.monotonic() - start_time < duration_seconds:
        try:
            cognitive_orchestrator.process_query("what is 5+5")
            request_count += 1
            await asyncio.sleep(0.01)  # Simulate some I/O wait
        except Exception:
            errors += 1

    throughput = request_count / duration_seconds
    error_rate = errors / request_count if request_count > 0 else 0

    assert throughput > (THROUGHPUT_TARGET_OPS_PER_SEC * 0.8), f"Sustained load throughput of {throughput:.2f} ops/sec is below 80% of target"
    assert error_rate == 0, f"Encountered {errors} errors during sustained load test"


@pytest.mark.asyncio
async def test_matriz_spike_load(cognitive_orchestrator):
    """Test the MATRIZ engine under a spike load."""
    spike_requests = 200

    start_time = time.monotonic()
    tasks = [
        asyncio.to_thread(cognitive_orchestrator.process_query, f"what is {i}+{i}")
        for i in range(spike_requests)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.monotonic()

    duration = end_time - start_time
    errors = sum(1 for r in results if isinstance(r, Exception))
    success_rate = (spike_requests - errors) / spike_requests

    assert success_rate > 0.99, f"Success rate of {success_rate:.2%} is below 99% during spike test"
    # Ensure the spike is handled in a reasonable time, not purely linearly.
    assert duration < (spike_requests / THROUGHPUT_TARGET_OPS_PER_SEC) * 1.5, f"Spike test duration of {duration:.2f}s was too long"
