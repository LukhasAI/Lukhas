#!/usr/bin/env python3
"""
MATRIZ Pipeline Performance Benchmarks

Validates SLO compliance:
- Pipeline latency <250ms p95
- Orchestrator timeout handling
- Node routing efficiency

Usage:
    python benchmarks/matriz_pipeline.py
    python -m pytest benchmarks/matriz_pipeline.py --benchmark
"""

import asyncio
import statistics
import time

import pytest

try:
    from matriz.core.async_orchestrator import AsyncOrchestrator
    from matriz.core.pipeline_context import (
        PipelineContext,  # noqa: F401  # TODO: matriz.core.pipeline_context.P...
    )

    MATRIZ_AVAILABLE = True
except ImportError:
    MATRIZ_AVAILABLE = False


class MATRIZBenchmarks:
    """MATRIZ pipeline performance benchmarks"""

    def __init__(self):
        if not MATRIZ_AVAILABLE:
            pytest.skip("MATRIZ modules not available")

        self.orchestrator = AsyncOrchestrator()

    async def benchmark_pipeline_latency(self, num_requests: int = 100) -> dict:
        """Benchmark pipeline latency - SLO: <250ms p95"""
        print(f"⚡ Benchmarking MATRIZ pipeline with {num_requests} requests...")

        latencies = []

        for i in range(num_requests):
            # Create test query
            query = f"Test query {i}: process data and return result"

            start_time = time.perf_counter()
            try:
                # Process through pipeline
                await self.orchestrator.process_query(query)
                end_time = time.perf_counter()

                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)

            except Exception as e:
                # Record timeout/error as max latency
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(max(latency_ms, 500))  # Cap at 500ms for errors
                print(f"   Warning: Request {i} failed: {e}")

        # Calculate statistics
        if latencies:
            p50 = statistics.median(latencies)
            p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
            p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
            mean_latency = statistics.mean(latencies)
        else:
            p50 = p95 = p99 = mean_latency = 0

        results = {
            "test": "matriz_pipeline_latency",
            "num_requests": num_requests,
            "successful_requests": len([l for l in latencies if l < 500]),
            "latency_ms": {
                "mean": round(mean_latency, 2),
                "p50": round(p50, 2),
                "p95": round(p95, 2),
                "p99": round(p99, 2),
            },
            "slo_compliance": {"target_p95_ms": 250, "actual_p95_ms": round(p95, 2), "compliant": p95 < 250},
        }

        print("📊 MATRIZ Pipeline Results:")
        print(f"   P50: {p50:.1f}ms, P95: {p95:.1f}ms, P99: {p99:.1f}ms")
        print(f"   Success Rate: {len([l for l in latencies if l < 500])}/{num_requests}")
        print(f"   SLO Compliance: {'✅ PASS' if p95 < 250 else '❌ FAIL'} (P95 < 250ms)")

        return results

    async def benchmark_concurrent_load(self, concurrent_requests: int = 50) -> dict:
        """Benchmark concurrent request handling"""
        print(f"🔄 Benchmarking concurrent load with {concurrent_requests} requests...")

        async def process_request(request_id: int):
            query = f"Concurrent test query {request_id}"
            start_time = time.perf_counter()

            try:
                await self.orchestrator.process_query(query)
                end_time = time.perf_counter()
                return {"id": request_id, "success": True, "latency_ms": (end_time - start_time) * 1000}
            except Exception as e:
                end_time = time.perf_counter()
                return {
                    "id": request_id,
                    "success": False,
                    "latency_ms": (end_time - start_time) * 1000,
                    "error": str(e),
                }

        # Execute concurrent requests
        start_time = time.perf_counter()
        tasks = [process_request(i) for i in range(concurrent_requests)]
        request_results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.perf_counter() - start_time

        # Analyze results
        successful = [r for r in request_results if isinstance(r, dict) and r.get("success", False)]
        failed = [r for r in request_results if not isinstance(r, dict) or not r.get("success", False)]

        latencies = [r["latency_ms"] for r in successful]
        if latencies:
            avg_latency = statistics.mean(latencies)
            max_latency = max(latencies)
        else:
            avg_latency = max_latency = 0

        throughput = len(successful) / total_time if total_time > 0 else 0

        results = {
            "test": "concurrent_load",
            "concurrent_requests": concurrent_requests,
            "successful": len(successful),
            "failed": len(failed),
            "success_rate_percent": round((len(successful) / concurrent_requests) * 100, 1),
            "total_time_seconds": round(total_time, 2),
            "throughput_rps": round(throughput, 1),
            "latency_ms": {"average": round(avg_latency, 2), "maximum": round(max_latency, 2)},
            "performance": {
                "high_throughput": throughput > 10,  # >10 requests/second
                "low_failure_rate": (len(failed) / concurrent_requests) < 0.05,  # <5% failure
            },
        }

        print("📊 Concurrent Load Results:")
        print(f"   Success: {len(successful)}/{concurrent_requests} ({results['success_rate_percent']}%)")
        print(f"   Throughput: {throughput:.1f} req/sec")
        print(f"   Avg Latency: {avg_latency:.1f}ms, Max: {max_latency:.1f}ms")

        return results

    async def benchmark_timeout_handling(self) -> dict:
        """Benchmark timeout and error handling"""
        print("⏰ Benchmarking timeout handling...")

        # Test with various timeout scenarios
        test_cases = [
            {"query": "quick operation", "expected_fast": True},
            {"query": "medium complexity task", "expected_fast": False},
            {"query": "simulate very long running operation", "expected_timeout": True},
        ]

        results_data = []
        timeouts_handled = 0
        errors_handled = 0

        for i, test_case in enumerate(test_cases):
            start_time = time.perf_counter()

            try:
                # Set a reasonable timeout for testing
                await asyncio.wait_for(
                    self.orchestrator.process_query(test_case["query"]), timeout=1.0  # 1 second timeout
                )

                end_time = time.perf_counter()
                latency = (end_time - start_time) * 1000

                results_data.append({"test_case": i, "success": True, "latency_ms": latency, "timeout": False})

            except asyncio.TimeoutError:
                timeouts_handled += 1
                end_time = time.perf_counter()
                latency = (end_time - start_time) * 1000

                results_data.append({"test_case": i, "success": False, "latency_ms": latency, "timeout": True})

            except Exception as e:
                errors_handled += 1
                end_time = time.perf_counter()
                latency = (end_time - start_time) * 1000

                results_data.append({"test_case": i, "success": False, "latency_ms": latency, "error": str(e)})

        results = {
            "test": "timeout_handling",
            "test_cases": len(test_cases),
            "timeouts_handled": timeouts_handled,
            "errors_handled": errors_handled,
            "total_handled": timeouts_handled + errors_handled,
            "handling_effectiveness": {
                "graceful_degradation": timeouts_handled > 0,
                "error_recovery": errors_handled >= 0,  # Should not crash
            },
            "test_results": results_data,
        }

        print("📊 Timeout Handling Results:")
        print(f"   Timeouts Handled: {timeouts_handled}")
        print(f"   Errors Handled: {errors_handled}")
        print(f"   Graceful Degradation: {'✅ YES' if timeouts_handled > 0 else '⚠️ UNTESTED'}")

        return results


async def run_all_benchmarks():
    """Run complete MATRIZ benchmark suite"""
    print("🚀 Starting MATRIZ Pipeline Benchmarks...")
    print("=" * 60)

    if not MATRIZ_AVAILABLE:
        print("❌ MATRIZ modules not available - skipping benchmarks")
        return []

    benchmarks = MATRIZBenchmarks()
    results = []

    try:
        # Run all benchmark tests
        results.append(await benchmarks.benchmark_pipeline_latency(50))
        results.append(await benchmarks.benchmark_concurrent_load(25))
        results.append(await benchmarks.benchmark_timeout_handling())

        # Summary
        print("\n" + "=" * 60)
        print("📊 MATRIZ BENCHMARK SUMMARY")
        print("=" * 60)

        all_compliant = True
        for result in results:
            test_name = result["test"].replace("_", " ").title()
            if "slo_compliance" in result:
                compliant = result["slo_compliance"]["compliant"]
                status = "✅ PASS" if compliant else "❌ FAIL"
                print(f"{test_name}: {status}")
                all_compliant = all_compliant and compliant
            else:
                print(f"{test_name}: 📊 COMPLETE")

        print(f"\nOverall SLO Compliance: {'✅ ALL PASS' if all_compliant else '❌ SOME FAILED'}")

        return results

    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return []


# pytest integration
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_matriz_pipeline_benchmark():
    """pytest-compatible MATRIZ pipeline benchmark"""
    if not MATRIZ_AVAILABLE:
        pytest.skip("MATRIZ not available")

    benchmarks = MATRIZBenchmarks()
    results = await benchmarks.benchmark_pipeline_latency(25)
    assert results["slo_compliance"]["compliant"], "MATRIZ pipeline latency SLO violated"


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_concurrent_load_benchmark():
    """pytest-compatible concurrent load benchmark"""
    if not MATRIZ_AVAILABLE:
        pytest.skip("MATRIZ not available")

    benchmarks = MATRIZBenchmarks()
    results = await benchmarks.benchmark_concurrent_load(20)
    assert results["success_rate_percent"] > 90, "Concurrent load success rate too low"


if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
