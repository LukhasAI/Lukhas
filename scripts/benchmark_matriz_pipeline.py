#!/usr/bin/env python3
"""
MATRIZ Pipeline Performance Benchmark
T4/0.01% Tail Latency Validation

Validates that the optimized MATRIZ pipeline meets:
- p95 < 250ms
- p99 < 300ms (safety margin)
- Error rate < 0.01%
- Circuit breaker functionality
"""

import argparse
import asyncio
import json
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

# Add LUKHAS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.matriz.optimized_orchestrator import OptimizedAsyncOrchestrator
from MATRIZ.core.async_orchestrator import AsyncCognitiveOrchestrator
from MATRIZ.nodes.fact_node import FactNode
from MATRIZ.nodes.math_node import MathNode


@dataclass
class BenchmarkResult:
    """Results from a benchmark run"""
    total_queries: int
    successful_queries: int
    failed_queries: int
    latencies_ms: List[float]
    p50_ms: float
    p95_ms: float
    p99_ms: float
    avg_ms: float
    max_ms: float
    min_ms: float
    error_rate: float
    within_budget_rate: float
    cache_hit_rate: float = 0.0
    circuit_breaker_trips: int = 0
    total_duration_s: float = 0.0


class MATRIZBenchmark:
    """Performance benchmark for MATRIZ pipeline optimization"""

    def __init__(self):
        # Test queries with varying complexity
        self.test_queries = [
            # Mathematical queries (should be fast)
            "2 + 2",
            "10 * 5",
            "100 / 4",
            "What is 15 + 7?",
            "Calculate 8 * 9",

            # Factual queries (medium complexity)
            "What is the capital of France?",
            "Who wrote Romeo and Juliet?",
            "What is the boiling point of water?",
            "How many sides does a triangle have?",
            "What year was the internet invented?",

            # General queries (variable complexity)
            "Hello world",
            "How are you today?",
            "Tell me a joke",
            "What is the weather like?",
            "Can you help me?",

            # Longer queries (potential outliers)
            "Can you explain the difference between machine learning and artificial intelligence in detail?",
            "What are the main factors that contribute to climate change and what can we do about it?",
            "How does photosynthesis work and why is it important for life on Earth?",
            "What is the history of space exploration and what are the future plans?",
            "Explain quantum computing and how it differs from classical computing",
        ]

        # Stress test queries (for outlier detection)
        self.stress_queries = [
            # Repeated complex queries
            "What is the meaning of life, the universe, and everything according to Douglas Adams?" * 3,
            # Empty or malformed queries
            "",
            "   ",
            None,
            # Very long query
            "a" * 1000,
        ]

    def setup_orchestrator(self, orchestrator_type: str = "optimized") -> AsyncCognitiveOrchestrator:
        """Setup orchestrator with test nodes"""

        if orchestrator_type == "optimized":
            orchestrator = OptimizedAsyncOrchestrator(
                total_timeout=0.240,  # 240ms budget
                cache_enabled=True,
                metrics_enabled=True
            )
        else:
            orchestrator = AsyncCognitiveOrchestrator(
                total_timeout=0.250,  # 250ms budget
            )

        # Register test nodes
        math_node = MathNode()
        fact_node = FactNode()

        orchestrator.register_node("math", math_node)
        orchestrator.register_node("facts", fact_node)

        return orchestrator

    async def benchmark_queries(
        self,
        orchestrator: AsyncCognitiveOrchestrator,
        queries: List[str],
        iterations: int = 1
    ) -> BenchmarkResult:
        """Benchmark a set of queries"""

        latencies = []
        successful_queries = 0
        failed_queries = 0
        within_budget = 0
        circuit_breaker_trips = 0
        cache_hits = 0
        total_queries = len(queries) * iterations

        start_time = time.perf_counter()

        for iteration in range(iterations):
            for query in queries:
                query_start = time.perf_counter()

                try:
                    # Handle None queries
                    if query is None:
                        query = "test query"

                    result = await orchestrator.process_query(str(query))
                    query_duration = (time.perf_counter() - query_start) * 1000  # Convert to ms

                    latencies.append(query_duration)

                    # Check if query succeeded
                    if result.get("error"):
                        failed_queries += 1
                    else:
                        successful_queries += 1

                    # Check if within budget
                    if result.get("metrics", {}).get("within_budget", False):
                        within_budget += 1

                    # Check for cache hits (optimized orchestrator only)
                    if result.get("from_cache", False):
                        cache_hits += 1

                    # Check for circuit breaker trips
                    if result.get("metrics", {}).get("circuit_breaker_active", False):
                        circuit_breaker_trips += 1

                except Exception as e:
                    query_duration = (time.perf_counter() - query_start) * 1000
                    latencies.append(query_duration)
                    failed_queries += 1
                    print(f"Query failed with exception: {e}")

        total_duration = time.perf_counter() - start_time

        # Calculate statistics
        if latencies:
            p50 = statistics.median(latencies)
            p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
            p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
            avg_latency = statistics.mean(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)
        else:
            p50 = p95 = p99 = avg_latency = max_latency = min_latency = 0.0

        error_rate = failed_queries / total_queries if total_queries > 0 else 0.0
        within_budget_rate = within_budget / total_queries if total_queries > 0 else 0.0
        cache_hit_rate = cache_hits / total_queries if total_queries > 0 else 0.0

        return BenchmarkResult(
            total_queries=total_queries,
            successful_queries=successful_queries,
            failed_queries=failed_queries,
            latencies_ms=latencies,
            p50_ms=p50,
            p95_ms=p95,
            p99_ms=p99,
            avg_ms=avg_latency,
            max_ms=max_latency,
            min_ms=min_latency,
            error_rate=error_rate,
            within_budget_rate=within_budget_rate,
            cache_hit_rate=cache_hit_rate,
            circuit_breaker_trips=circuit_breaker_trips,
            total_duration_s=total_duration
        )

    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark comparing optimized vs standard orchestrator"""

        print("🚀 Starting MATRIZ Pipeline T4/0.01% Benchmark")
        print("=" * 60)

        results = {}

        # Test standard orchestrator
        print("\n📊 Testing Standard AsyncCognitiveOrchestrator...")
        standard_orchestrator = self.setup_orchestrator("standard")
        standard_result = await self.benchmark_queries(
            standard_orchestrator,
            self.test_queries,
            iterations=5
        )
        results["standard"] = standard_result

        # Test optimized orchestrator
        print("⚡ Testing OptimizedAsyncOrchestrator...")
        optimized_orchestrator = self.setup_orchestrator("optimized")

        # Warm up caches first
        print("🔥 Warming up caches...")
        await optimized_orchestrator.warmup_caches(self.test_queries[:5])

        optimized_result = await self.benchmark_queries(
            optimized_orchestrator,
            self.test_queries,
            iterations=5
        )
        results["optimized"] = optimized_result

        # Stress test with optimized orchestrator
        print("🔥 Running stress test...")
        stress_result = await self.benchmark_queries(
            optimized_orchestrator,
            self.stress_queries,
            iterations=3
        )
        results["stress_test"] = stress_result

        # Load test - higher concurrency
        print("⚡ Running load test...")
        load_result = await self.run_load_test(optimized_orchestrator)
        results["load_test"] = load_result

        return results

    async def run_load_test(self, orchestrator: OptimizedAsyncOrchestrator, concurrent_requests: int = 50) -> BenchmarkResult:
        """Run load test with concurrent requests"""

        # Create concurrent tasks
        tasks = []
        test_queries = self.test_queries[:10]  # Use subset for load test

        start_time = time.perf_counter()

        for i in range(concurrent_requests):
            query = test_queries[i % len(test_queries)]
            task = asyncio.create_task(self.time_single_query(orchestrator, query))
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_duration = time.perf_counter() - start_time

        # Process results
        latencies = []
        successful_queries = 0
        failed_queries = 0

        for result in results:
            if isinstance(result, Exception):
                failed_queries += 1
                latencies.append(1000.0)  # 1 second timeout
            else:
                latencies.append(result["latency_ms"])
                if result["success"]:
                    successful_queries += 1
                else:
                    failed_queries += 1

        # Calculate statistics
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies)
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)

        return BenchmarkResult(
            total_queries=concurrent_requests,
            successful_queries=successful_queries,
            failed_queries=failed_queries,
            latencies_ms=latencies,
            p50_ms=p50,
            p95_ms=p95,
            p99_ms=p99,
            avg_ms=statistics.mean(latencies),
            max_ms=max(latencies),
            min_ms=min(latencies),
            error_rate=failed_queries / concurrent_requests,
            within_budget_rate=sum(1 for l in latencies if l < 240) / len(latencies),
            total_duration_s=total_duration
        )

    async def time_single_query(self, orchestrator: AsyncCognitiveOrchestrator, query: str) -> Dict[str, Any]:
        """Time a single query execution"""
        start_time = time.perf_counter()

        try:
            result = await orchestrator.process_query(query)
            latency_ms = (time.perf_counter() - start_time) * 1000

            return {
                "latency_ms": latency_ms,
                "success": not bool(result.get("error")),
                "result": result
            }
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return {
                "latency_ms": latency_ms,
                "success": False,
                "error": str(e)
            }

    def print_results(self, results: Dict[str, BenchmarkResult]) -> None:
        """Print formatted benchmark results"""

        print("\n" + "=" * 60)
        print("📈 MATRIZ Pipeline Benchmark Results")
        print("=" * 60)

        for test_name, result in results.items():
            print(f"\n🔍 {test_name.replace('_', ' ').title()}")
            print("-" * 40)

            print(f"Total Queries:     {result.total_queries}")
            print(f"Success Rate:      {((result.successful_queries / result.total_queries) * 100):.1f}%")
            print(f"Error Rate:        {(result.error_rate * 100):.3f}%")
            print(f"Within Budget:     {(result.within_budget_rate * 100):.1f}%")

            print("\n⏱️  Latency Statistics:")
            print(f"  P50 (median):    {result.p50_ms:.1f} ms")
            print(f"  P95:             {result.p95_ms:.1f} ms")
            print(f"  P99:             {result.p99_ms:.1f} ms")
            print(f"  Average:         {result.avg_ms:.1f} ms")
            print(f"  Max:             {result.max_ms:.1f} ms")
            print(f"  Min:             {result.min_ms:.1f} ms")

            if hasattr(result, 'cache_hit_rate') and result.cache_hit_rate > 0:
                print(f"\n💾 Cache Hit Rate:   {(result.cache_hit_rate * 100):.1f}%")

            if result.circuit_breaker_trips > 0:
                print(f"⚡ Circuit Breaker:  {result.circuit_breaker_trips} trips")

            print(f"🕒 Total Duration:   {result.total_duration_s:.2f}s")

            # T4/0.01% compliance check
            self.check_t4_compliance(test_name, result)

    def check_t4_compliance(self, test_name: str, result: BenchmarkResult) -> None:
        """Check if results meet T4/0.01% compliance targets"""

        print(f"\n✅ T4/0.01% Compliance Check ({test_name}):")

        # P95 < 250ms target
        p95_compliant = result.p95_ms < 250.0
        p95_status = "✅ PASS" if p95_compliant else "❌ FAIL"
        print(f"  P95 < 250ms:      {result.p95_ms:.1f}ms {p95_status}")

        # P99 < 300ms target (safety margin)
        p99_compliant = result.p99_ms < 300.0
        p99_status = "✅ PASS" if p99_compliant else "❌ FAIL"
        print(f"  P99 < 300ms:      {result.p99_ms:.1f}ms {p99_status}")

        # Error rate < 0.01%
        error_compliant = result.error_rate < 0.0001
        error_status = "✅ PASS" if error_compliant else "❌ FAIL"
        print(f"  Error < 0.01%:     {(result.error_rate * 100):.4f}% {error_status}")

        # Overall compliance
        overall_compliant = p95_compliant and p99_compliant and error_compliant
        overall_status = "✅ T4/0.01% COMPLIANT" if overall_compliant else "❌ NON-COMPLIANT"
        print(f"  Overall:           {overall_status}")

    def save_results(self, results: Dict[str, BenchmarkResult], output_file: Path) -> None:
        """Save results to JSON file"""

        serializable_results = {}

        for test_name, result in results.items():
            serializable_results[test_name] = {
                "total_queries": result.total_queries,
                "successful_queries": result.successful_queries,
                "failed_queries": result.failed_queries,
                "p50_ms": result.p50_ms,
                "p95_ms": result.p95_ms,
                "p99_ms": result.p99_ms,
                "avg_ms": result.avg_ms,
                "max_ms": result.max_ms,
                "min_ms": result.min_ms,
                "error_rate": result.error_rate,
                "within_budget_rate": result.within_budget_rate,
                "cache_hit_rate": getattr(result, 'cache_hit_rate', 0.0),
                "circuit_breaker_trips": result.circuit_breaker_trips,
                "total_duration_s": result.total_duration_s,
                "latency_histogram": self.create_histogram(result.latencies_ms),
                "t4_compliance": {
                    "p95_compliant": result.p95_ms < 250.0,
                    "p99_compliant": result.p99_ms < 300.0,
                    "error_compliant": result.error_rate < 0.0001,
                    "overall_compliant": result.p95_ms < 250.0 and result.p99_ms < 300.0 and result.error_rate < 0.0001
                }
            }

        # Add metadata
        benchmark_data = {
            "metadata": {
                "timestamp": time.time(),
                "version": "1.0.0",
                "target_p95_ms": 250.0,
                "target_p99_ms": 300.0,
                "target_error_rate": 0.0001
            },
            "results": serializable_results
        }

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(benchmark_data, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

    def create_histogram(self, latencies: List[float], bins: int = 10) -> Dict[str, int]:
        """Create latency histogram for analysis"""
        if not latencies:
            return {}

        min_lat = min(latencies)
        max_lat = max(latencies)
        bin_width = (max_lat - min_lat) / bins

        histogram = {}
        for i in range(bins):
            bin_start = min_lat + i * bin_width
            bin_end = bin_start + bin_width
            bin_label = f"{bin_start:.0f}-{bin_end:.0f}ms"

            count = sum(1 for lat in latencies if bin_start <= lat < bin_end)
            histogram[bin_label] = count

        return histogram


async def main():
    """Main benchmark execution"""
    parser = argparse.ArgumentParser(description='MATRIZ Pipeline Performance Benchmark')
    parser.add_argument('--output', type=Path, default=Path('artifacts/matriz_benchmark_results.json'),
                       help='Output file for results')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick benchmark (fewer iterations)')

    args = parser.parse_args()

    benchmark = MATRIZBenchmark()

    # Override for quick test
    if args.quick:
        benchmark.test_queries = benchmark.test_queries[:5]  # Use fewer queries
        print("🚀 Running quick benchmark...")

    try:
        results = await benchmark.run_comprehensive_benchmark()
        benchmark.print_results(results)
        benchmark.save_results(results, args.output)

        # Check overall compliance
        optimized_result = results.get("optimized")
        if optimized_result:
            overall_compliant = (
                optimized_result.p95_ms < 250.0 and
                optimized_result.p99_ms < 300.0 and
                optimized_result.error_rate < 0.0001
            )

            if overall_compliant:
                print("\n🎉 MATRIZ Pipeline is T4/0.01% COMPLIANT!")
                return 0
            else:
                print("\n⚠️  MATRIZ Pipeline does not meet T4/0.01% targets")
                return 1
        else:
            print("\n❌ Benchmark failed - no results available")
            return 1

    except Exception as e:
        print(f"\n❌ Benchmark failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
