#!/usr/bin/env python3
"""
MATRIZ Orchestrator Stress Testing

Tests orchestrator performance under concurrent load with 100+ concurrent requests.
Validates P95 latency stays within SLO (<250ms) under stress conditions.

# ΛTAG: orchestrator_stress_tests, performance_validation
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime
from typing import Dict, Any, Tuple

try:
    from lukhas.core.matriz.async_orchestrator import AsyncOrchestrator
    from lukhas.core.interfaces import ICognitiveNode
    from lukhas.observability.prometheus_metrics import LUKHASMetrics
    from lukhas.core.registry import get_plugin_registry
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    # Fallback for testing without full orchestrator
    ORCHESTRATOR_AVAILABLE = False
    AsyncOrchestrator = None
    ICognitiveNode = None
    LUKHASMetrics = None
    get_plugin_registry = None


class MockCognitiveNode:
    """Mock cognitive node for stress testing."""

    def __init__(self, name: str, latency_ms: float = 50.0, failure_rate: float = 0.0):
        self.name = name
        self.latency_ms = latency_ms
        self.failure_rate = failure_rate
        self.request_count = 0
        self.error_count = 0

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process request with simulated latency and failure rate."""
        self.request_count += 1

        # Simulate processing latency
        await asyncio.sleep(self.latency_ms / 1000.0)

        # Simulate random failures
        import random
        if random.random() < self.failure_rate:
            self.error_count += 1
            raise Exception(f"Simulated failure in {self.name}")

        return {
            "node": self.name,
            "processed": True,
            "input_size": len(str(context)),
            "timestamp": datetime.now().isoformat(),
            "request_id": context.get("request_id", "unknown")
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get node statistics."""
        return {
            "name": self.name,
            "requests": self.request_count,
            "errors": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "latency_ms": self.latency_ms
        }


@pytest.mark.skipif(not ORCHESTRATOR_AVAILABLE, reason="Orchestrator system not available")
class TestOrchestratorStressTesting:
    """Stress tests for MATRIZ orchestrator under concurrent load."""

    @pytest.fixture
    def orchestrator_config(self):
        """Configuration for stress testing orchestrator."""
        return {
            "max_concurrent_requests": 200,
            "request_timeout_ms": 5000,
            "stage_timeout_ms": 1000,
            "circuit_breaker_threshold": 0.5,
            "metrics_enabled": True,
            "performance_mode": "stress_test"
        }

    @pytest.fixture
    def mock_cognitive_nodes(self):
        """Create mock cognitive nodes with varying performance characteristics."""
        return {
            "fast_node": MockCognitiveNode("fast_node", latency_ms=10.0, failure_rate=0.01),
            "medium_node": MockCognitiveNode("medium_node", latency_ms=50.0, failure_rate=0.02),
            "slow_node": MockCognitiveNode("slow_node", latency_ms=100.0, failure_rate=0.05),
            "unreliable_node": MockCognitiveNode("unreliable_node", latency_ms=30.0, failure_rate=0.15)
        }

    @pytest.fixture
    def orchestrator(self, orchestrator_config, mock_cognitive_nodes):
        """Create orchestrator with mock nodes for stress testing."""
        if AsyncOrchestrator is None:
            pytest.skip("AsyncOrchestrator not available")

        orchestrator = AsyncOrchestrator(config=orchestrator_config)

        # Register mock nodes
        for node_name, node in mock_cognitive_nodes.items():
            orchestrator.register_node(node_name, node)

        return orchestrator

    def test_concurrent_request_handling(self, orchestrator, mock_cognitive_nodes):
        """Test orchestrator handling 100+ concurrent requests."""

        async def single_request(request_id: int) -> Tuple[int, float, bool, str]:
            """Execute single request and measure performance."""
            start_time = time.perf_counter()

            try:
                context = {
                    "request_id": f"stress_req_{request_id}",
                    "data": f"Test data for request {request_id}",
                    "timestamp": datetime.now().isoformat(),
                    "complexity": request_id % 10
                }

                result = await orchestrator.process_request(
                    context=context,
                    pipeline_config={
                        "stages": ["fast_node", "medium_node"],
                        "timeout_ms": 2000
                    }
                )

                latency = (time.perf_counter() - start_time) * 1000  # Convert to ms
                return request_id, latency, True, "success"

            except Exception as e:
                latency = (time.perf_counter() - start_time) * 1000
                return request_id, latency, False, str(e)

        async def stress_test_execution():
            """Execute concurrent stress test."""
            # Generate 150 concurrent requests
            tasks = [single_request(i) for i in range(150)]

            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            return results

        # Run stress test
        if asyncio.get_event_loop().is_running():
            # If already in async context, create new event loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, stress_test_execution())
                results = future.result()
        else:
            results = asyncio.run(stress_test_execution())

        # Analyze results
        successful_requests = []
        failed_requests = []
        latencies = []

        for result in results:
            if isinstance(result, Exception):
                failed_requests.append(str(result))
                continue

            request_id, latency, success, message = result
            latencies.append(latency)

            if success:
                successful_requests.append(request_id)
            else:
                failed_requests.append(f"Request {request_id}: {message}")

        # Performance analysis
        if latencies:
            mean_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
            p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
            max_latency = max(latencies)
        else:
            mean_latency = p95_latency = p99_latency = max_latency = 0

        # Success rate analysis
        total_requests = len(results)
        success_rate = len(successful_requests) / total_requests
        failure_rate = len(failed_requests) / total_requests

        print(f"\nStress Test Results:")
        print(f"  Total requests: {total_requests}")
        print(f"  Successful requests: {len(successful_requests)}")
        print(f"  Failed requests: {len(failed_requests)}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Mean latency: {mean_latency:.2f}ms")
        print(f"  P95 latency: {p95_latency:.2f}ms")
        print(f"  P99 latency: {p99_latency:.2f}ms")
        print(f"  Max latency: {max_latency:.2f}ms")

        # Performance assertions
        assert success_rate >= 0.85, f"Success rate too low: {success_rate:.2%}"
        assert p95_latency <= 250.0, f"P95 latency exceeds SLO: {p95_latency:.2f}ms > 250ms"
        assert mean_latency <= 150.0, f"Mean latency too high: {mean_latency:.2f}ms"

        # Print first few failures for debugging
        if failed_requests:
            print(f"\nFirst 5 failures:")
            for failure in failed_requests[:5]:
                print(f"  {failure}")

    def test_sustained_load_performance(self, orchestrator, mock_cognitive_nodes):
        """Test orchestrator performance under sustained load over time."""

        async def sustained_load_worker(duration_seconds: int, requests_per_second: int):
            """Generate sustained load for specified duration."""
            results = []
            start_time = time.time()
            request_count = 0

            while time.time() - start_time < duration_seconds:
                batch_start = time.time()

                # Generate batch of requests
                batch_tasks = []
                for i in range(requests_per_second):
                    context = {
                        "request_id": f"sustained_{request_count}_{i}",
                        "batch": request_count,
                        "timestamp": datetime.now().isoformat()
                    }

                    task = orchestrator.process_request(
                        context=context,
                        pipeline_config={"stages": ["fast_node", "medium_node"]}
                    )
                    batch_tasks.append(task)

                # Execute batch
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                # Record timing
                batch_duration = time.time() - batch_start
                successful_in_batch = sum(1 for r in batch_results if not isinstance(r, Exception))

                results.append({
                    "batch": request_count,
                    "duration": batch_duration,
                    "requests": len(batch_tasks),
                    "successful": successful_in_batch,
                    "timestamp": time.time()
                })

                request_count += 1

                # Wait remainder of second
                sleep_time = max(0, 1.0 - batch_duration)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            return results

        # Run sustained load test (shorter duration for testing)
        test_duration = 10  # seconds
        rps = 20  # requests per second

        if asyncio.get_event_loop().is_running():
            # Handle nested event loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    sustained_load_worker(test_duration, rps)
                )
                load_results = future.result()
        else:
            load_results = asyncio.run(sustained_load_worker(test_duration, rps))

        # Analyze sustained load results
        total_batches = len(load_results)
        total_requests = sum(r["requests"] for r in load_results)
        total_successful = sum(r["successful"] for r in load_results)
        batch_durations = [r["duration"] for r in load_results]

        avg_batch_duration = statistics.mean(batch_durations)
        max_batch_duration = max(batch_durations)
        success_rate = total_successful / total_requests if total_requests > 0 else 0

        print(f"\nSustained Load Test Results:")
        print(f"  Duration: {test_duration}s")
        print(f"  Target RPS: {rps}")
        print(f"  Total batches: {total_batches}")
        print(f"  Total requests: {total_requests}")
        print(f"  Successful requests: {total_successful}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Average batch duration: {avg_batch_duration:.3f}s")
        print(f"  Max batch duration: {max_batch_duration:.3f}s")

        # Sustained load assertions
        assert success_rate >= 0.90, f"Sustained load success rate too low: {success_rate:.2%}"
        assert avg_batch_duration <= 1.5, f"Batch processing too slow: {avg_batch_duration:.3f}s"
        assert max_batch_duration <= 3.0, f"Maximum batch duration too high: {max_batch_duration:.3f}s"

    def test_orchestrator_circuit_breaker_under_stress(self, orchestrator, mock_cognitive_nodes):
        """Test circuit breaker behavior under high failure rates."""

        # Increase failure rate for unreliable node
        mock_cognitive_nodes["unreliable_node"].failure_rate = 0.8

        async def circuit_breaker_test():
            """Test circuit breaker activation under stress."""
            results = []

            # Generate requests that will trigger circuit breaker
            for i in range(50):
                try:
                    context = {
                        "request_id": f"cb_test_{i}",
                        "timestamp": datetime.now().isoformat()
                    }

                    result = await orchestrator.process_request(
                        context=context,
                        pipeline_config={
                            "stages": ["unreliable_node"],  # Use high-failure node
                            "timeout_ms": 1000
                        }
                    )

                    results.append({"success": True, "result": result})

                except Exception as e:
                    results.append({"success": False, "error": str(e)})

                # Brief delay between requests
                await asyncio.sleep(0.01)

            return results

        # Execute circuit breaker test
        if asyncio.get_event_loop().is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, circuit_breaker_test())
                cb_results = future.result()
        else:
            cb_results = asyncio.run(circuit_breaker_test())

        # Analyze circuit breaker behavior
        successful_requests = [r for r in cb_results if r["success"]]
        failed_requests = [r for r in cb_results if not r["success"]]

        success_rate = len(successful_requests) / len(cb_results)
        circuit_breaker_activations = sum(
            1 for r in failed_requests
            if "circuit" in r.get("error", "").lower()
        )

        print(f"\nCircuit Breaker Test Results:")
        print(f"  Total requests: {len(cb_results)}")
        print(f"  Successful requests: {len(successful_requests)}")
        print(f"  Failed requests: {len(failed_requests)}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Circuit breaker activations: {circuit_breaker_activations}")

        # Circuit breaker should prevent complete system failure
        assert success_rate <= 0.30, "Circuit breaker should limit success rate with high failure node"

        # Get node stats
        unreliable_stats = mock_cognitive_nodes["unreliable_node"].get_stats()
        print(f"  Unreliable node stats: {unreliable_stats}")

    def test_orchestrator_timeout_handling_under_load(self, orchestrator):
        """Test timeout handling under concurrent load."""

        # Create a slow mock node for timeout testing
        slow_timeout_node = MockCognitiveNode("timeout_node", latency_ms=2000.0, failure_rate=0.0)
        orchestrator.register_node("timeout_node", slow_timeout_node)

        async def timeout_test():
            """Test timeout behavior under load."""
            timeout_results = []

            # Generate concurrent requests with short timeouts
            tasks = []
            for i in range(30):
                context = {
                    "request_id": f"timeout_test_{i}",
                    "timestamp": datetime.now().isoformat()
                }

                task = orchestrator.process_request(
                    context=context,
                    pipeline_config={
                        "stages": ["timeout_node"],
                        "timeout_ms": 500  # Short timeout for 2s node
                    }
                )
                tasks.append(task)

            # Execute all timeout tests
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    timeout_results.append({
                        "request_id": i,
                        "timeout": "timeout" in str(result).lower(),
                        "error": str(result)
                    })
                else:
                    timeout_results.append({
                        "request_id": i,
                        "timeout": False,
                        "success": True
                    })

            return timeout_results

        # Execute timeout test
        if asyncio.get_event_loop().is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, timeout_test())
                timeout_results = future.result()
        else:
            timeout_results = asyncio.run(timeout_test())

        # Analyze timeout behavior
        timeout_count = sum(1 for r in timeout_results if r.get("timeout", False))
        success_count = sum(1 for r in timeout_results if r.get("success", False))

        print(f"\nTimeout Test Results:")
        print(f"  Total requests: {len(timeout_results)}")
        print(f"  Timeouts detected: {timeout_count}")
        print(f"  Successful completions: {success_count}")

        # Most requests should timeout (since node takes 2s, timeout is 500ms)
        timeout_rate = timeout_count / len(timeout_results)
        assert timeout_rate >= 0.80, f"Timeout rate too low: {timeout_rate:.2%}"

    def test_orchestrator_memory_usage_under_stress(self, orchestrator):
        """Test memory usage doesn't grow excessively under stress."""

        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        async def memory_stress_test():
            """Generate load to test memory usage."""
            results = []

            # Generate many requests to test memory management
            for batch in range(10):
                batch_tasks = []

                for i in range(50):
                    context = {
                        "request_id": f"memory_test_{batch}_{i}",
                        "large_data": "x" * 10000,  # Add some data
                        "timestamp": datetime.now().isoformat()
                    }

                    task = orchestrator.process_request(
                        context=context,
                        pipeline_config={"stages": ["fast_node"]}
                    )
                    batch_tasks.append(task)

                # Execute batch
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                results.extend(batch_results)

                # Check memory after each batch
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - initial_memory

                if memory_growth > 100:  # Alert if memory grows by more than 100MB
                    print(f"Warning: Memory growth {memory_growth:.1f}MB after batch {batch}")

            return results

        # Execute memory stress test
        if asyncio.get_event_loop().is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, memory_stress_test())
                memory_results = future.result()
        else:
            memory_results = asyncio.run(memory_stress_test())

        final_memory = process.memory_info().rss / 1024 / 1024
        total_memory_growth = final_memory - initial_memory

        print(f"\nMemory Usage Test Results:")
        print(f"  Initial memory: {initial_memory:.1f}MB")
        print(f"  Final memory: {final_memory:.1f}MB")
        print(f"  Memory growth: {total_memory_growth:.1f}MB")
        print(f"  Total requests processed: {len(memory_results)}")

        # Memory growth should be reasonable
        assert total_memory_growth <= 200, f"Excessive memory growth: {total_memory_growth:.1f}MB"

        successful_memory_requests = sum(
            1 for r in memory_results
            if not isinstance(r, Exception)
        )
        success_rate = successful_memory_requests / len(memory_results)

        assert success_rate >= 0.95, f"Memory stress test success rate too low: {success_rate:.2%}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])