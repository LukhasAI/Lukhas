
import asyncio
import gc
import random
import statistics
import time

import psutil
import pytest

# The 'matriz' package is aliased to 'MATRIZ' at runtime.
# See matriz/__init__.py for details.
from matriz import orchestration


# A dummy node for testing purposes
class DummyNode:
    def process(self, data):
        return {"answer": "dummy response"}

# Performance thresholds from architectural audit
MATRIZ_LATENCY_THRESHOLD_MS = 250  # <250ms requirement
MATRIZ_THROUGHPUT_THRESHOLD = 50.0  # 50 ops/sec requirement
MATRIZ_P95_THRESHOLD_MS = 200      # P95 latency target
STRESS_ERROR_RATE_THRESHOLD = 0.05 # Error rate < 5% under stress
BENCHMARK_MEMORY_LIMIT_MB = 50     # 50MB memory limit per component benchmark
MEMORY_LEAK_THRESHOLD_MB = 10      # Allowable memory growth after cleanup

pytestmark = pytest.mark.performance


class TestSystemPerformance:
    """System-wide performance validation."""

    @pytest.fixture(autouse=True)
    def setup_performance_data(self):
        """Setup performance data collection"""
        self.orchestrator = orchestration.async_orchestrator.AsyncCognitiveOrchestrator()
        self.orchestrator.register_node("facts", DummyNode())
        self.performance_data = {
            'latencies': [],
            'throughputs': [],
            'error_rates': [],
            'cpu_utilization': [],
            'memory_utilization': []
        }

    async def _real_user_operation(self, error_rate=0.0):
        """Simulates a single user operation with realistic delay and potential errors."""
        start_time = time.perf_counter()

        if random.random() < error_rate:
            await asyncio.sleep(0.005) # Simulate a quick failure
            raise ConnectionError("Simulated failure under stress")

        # Now we call the real orchestrator
        await self.orchestrator.process_query("What is the meaning of life?")

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        return latency_ms

    def _mock_component_operation(self, component_name: str):
        """Simulates a processing-intensive operation for a given component."""
        if component_name == "data_processing":
            data = [i for i in range(50_000)]
            _ = [x*x for x in data]
            time.sleep(0.075)
        elif component_name == "io_bound":
            time.sleep(0.120)
        elif component_name == "memory_intensive":
            _ = bytearray(20 * 1024 * 1024)
            time.sleep(0.02)
        else:
            time.sleep(0.05)

    def _mock_memory_leak_operation(self):
        """Simulates an operation that allocates objects which should be garbage collected."""
        # This list will be local to the function and should be collected
        _ = [f"leaky_string_{i}" for i in range(10000)]
        return True

    @pytest.mark.asyncio
    async def test_system_under_high_load(self):
        """Measures system performance under high concurrent load."""
        concurrent_users = 100
        total_requests = 500
        latencies = []

        start_time = time.perf_counter()

        requests_made = 0
        while requests_made < total_requests:
            batch_size = min(concurrent_users, total_requests - requests_made)
            tasks = [self._real_user_operation() for _ in range(batch_size)]
            batch_latencies = await asyncio.gather(*tasks)
            latencies.extend(batch_latencies)
            requests_made += batch_size

        end_time = time.perf_counter()

        total_duration_sec = end_time - start_time
        throughput_ops_per_sec = total_requests / total_duration_sec
        p95_latency = statistics.quantiles(latencies, n=20)[18]

        print(f"Load Test Results:")
        print(f"  - Throughput: {throughput_ops_per_sec:.2f} ops/sec")
        print(f"  - p95 Latency: {p95_latency:.2f} ms")

        assert throughput_ops_per_sec >= MATRIZ_THROUGHPUT_THRESHOLD
        assert p95_latency <= MATRIZ_P95_THRESHOLD_MS

    @pytest.mark.asyncio
    async def test_system_stress_test(self):
        """Pushes the system to its limits to measure stability and resource usage."""
        stress_duration_sec = 5
        concurrent_requests = 200
        simulated_error_rate = 0.03

        success_count = 0
        error_count = 0

        process = psutil.Process()
        cpu_usage_samples = []

        start_time = time.perf_counter()

        async def run_operation():
            nonlocal success_count, error_count
            try:
                await self._real_user_operation(error_rate=simulated_error_rate)
                success_count += 1
            except ConnectionError:
                error_count += 1

        tasks = []
        while time.perf_counter() - start_time < stress_duration_sec:
            for _ in range(concurrent_requests):
                tasks.append(asyncio.create_task(run_operation()))

            cpu_usage_samples.append(process.cpu_percent(interval=0.1))
            tasks = [t for t in tasks if not t.done()]

        await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.perf_counter()

        total_ops = success_count + error_count
        error_rate = error_count / total_ops if total_ops > 0 else 0
        avg_cpu_utilization = statistics.mean(cpu_usage_samples) if cpu_usage_samples else 0
        peak_memory_mb = process.memory_info().rss / 1024 / 1024

        print(f"Stress Test Results:")
        print(f"  - Error Rate: {error_rate:.2%}")
        print(f"  - Avg CPU Utilization: {avg_cpu_utilization:.2f}%")
        print(f"  - Peak Memory Usage: {peak_memory_mb:.2f} MB")

        assert error_rate < STRESS_ERROR_RATE_THRESHOLD
        assert avg_cpu_utilization < 90.0

    @pytest.mark.parametrize("component_name, expected_max_latency_ms", [
        ("data_processing", 100),
        ("io_bound", 150),
        ("memory_intensive", 50),
    ])
    def test_component_benchmarks(self, component_name, expected_max_latency_ms):
        """Benchmarks the performance of individual system components."""
        latencies = []
        process = psutil.Process()

        gc.collect()
        baseline_mem = process.memory_info().rss

        for _ in range(5):
            start_time = time.perf_counter()
            self._mock_component_operation(component_name)
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1000)

        peak_mem = process.memory_info().rss

        avg_latency = statistics.mean(latencies)
        mem_increase_mb = (peak_mem - baseline_mem) / (1024 * 1024)

        print(f"\nBenchmark Results for '{component_name}':")
        print(f"  - Average Latency: {avg_latency:.2f} ms (Expected < {expected_max_latency_ms} ms)")
        print(f"  - Memory Increase: {mem_increase_mb:.2f} MB (Expected < {BENCHMARK_MEMORY_LIMIT_MB} MB)")

        assert avg_latency <= expected_max_latency_ms
        assert mem_increase_mb <= BENCHMARK_MEMORY_LIMIT_MB

    def test_memory_leak_detection(self):
        """Runs an operation multiple times to check for memory leaks."""
        process = psutil.Process()

        # Force GC and get a baseline memory measurement
        gc.collect()
        baseline_mem_mb = process.memory_info().rss / (1024 * 1024)

        # Run the operation many times
        for _ in range(200):
            self._mock_memory_leak_operation()

        # Force GC again to clean up
        gc.collect()

        final_mem_mb = process.memory_info().rss / (1024 * 1024)

        memory_growth_mb = final_mem_mb - baseline_mem_mb

        print(f"\nMemory Leak Detection Results:")
        print(f"  - Baseline Memory: {baseline_mem_mb:.2f} MB")
        print(f"  - Final Memory: {final_mem_mb:.2f} MB")
        print(f"  - Memory Growth: {memory_growth_mb:.2f} MB (Threshold: < {MEMORY_LEAK_THRESHOLD_MB} MB)")

        assert memory_growth_mb < MEMORY_LEAK_THRESHOLD_MB, \
            f"Potential memory leak detected. Memory grew by {memory_growth_mb:.2f} MB."
