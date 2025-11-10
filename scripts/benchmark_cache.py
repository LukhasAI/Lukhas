#!/usr/bin/env python3
"""
Benchmark script for cache performance analysis.

Usage:
    python scripts/benchmark_cache.py > reports/cache_performance.md
    python scripts/benchmark_cache.py --iterations 5000
"""
import asyncio
import time
import statistics
import argparse
from caching.cache_system import cache_operation, get_cache_manager


@cache_operation(cache_key="benchmark_op", ttl_seconds=300)
async def benchmark_operation(value: int) -> dict:
    """Simulate a 5KB data fetch with 100ms latency."""
    await asyncio.sleep(0.1)  # Simulate backend delay
    return {"data": "x" * 5000, "value": value}


async def run_benchmark(iterations: int = 1000, reuse_factor: int = 100):
    """
    Run cache performance benchmark.

    Args:
        iterations: Number of benchmark iterations
        reuse_factor: How many unique keys to cycle through (lower = higher hit rate)
    """
    cache_manager = get_cache_manager()
    await cache_manager.clear()

    uncached_times = []
    cached_times = []

    print(f"Running benchmark with {iterations} iterations...")
    print("Phase 1: Measuring uncached performance...")

    # Benchmark uncached operations
    for i in range(iterations):
        await cache_manager.clear()
        start = time.time()
        await benchmark_operation(i)
        uncached_times.append((time.time() - start) * 1000)

    print("Phase 2: Measuring cached performance...")

    # Benchmark cached operations
    await cache_manager.clear()
    for i in range(iterations):
        start = time.time()
        await benchmark_operation(i % reuse_factor)  # Reuse values for cache hits
        cached_times.append((time.time() - start) * 1000)

    # Calculate statistics
    print("\n# Cache Performance Benchmark Results\n")
    print(f"**Iterations:** {iterations}")
    print(f"**Reuse Factor:** {reuse_factor}")
    print(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("| Metric | Uncached | Cached | Improvement |")
    print("|--------|----------|--------|-------------|")

    p50_uncached = statistics.median(uncached_times)
    p50_cached = statistics.median(cached_times)
    p50_improvement = ((1 - p50_cached/p50_uncached) * 100) if p50_uncached > 0 else 0

    p95_uncached = sorted(uncached_times)[int(0.95*iterations)]
    p95_cached = sorted(cached_times)[int(0.95*iterations)]
    p95_improvement = ((1 - p95_cached/p95_uncached) * 100) if p95_uncached > 0 else 0

    p99_uncached = sorted(uncached_times)[int(0.99*iterations)]
    p99_cached = sorted(cached_times)[int(0.99*iterations)]
    p99_improvement = ((1 - p99_cached/p99_uncached) * 100) if p99_uncached > 0 else 0

    print(f"| **p50 Latency** | {p50_uncached:.2f}ms | {p50_cached:.2f}ms | **-{p50_improvement:.1f}%** |")
    print(f"| **p95 Latency** | {p95_uncached:.2f}ms | {p95_cached:.2f}ms | **-{p95_improvement:.1f}%** |")
    print(f"| **p99 Latency** | {p99_uncached:.2f}ms | {p99_cached:.2f}ms | **-{p99_improvement:.1f}%** |")
    print(f"| **Average** | {statistics.mean(uncached_times):.2f}ms | {statistics.mean(cached_times):.2f}ms | **-{((1 - statistics.mean(cached_times)/statistics.mean(uncached_times)) * 100):.1f}%** |")

    # Throughput calculation
    uncached_rps = 1000 / p50_uncached if p50_uncached > 0 else 0
    cached_rps = 1000 / p50_cached if p50_cached > 0 else 0
    throughput_improvement = ((cached_rps / uncached_rps - 1) * 100) if uncached_rps > 0 else 0

    print(f"\n## Throughput Analysis\n")
    print(f"| Metric | Uncached | Cached | Improvement |")
    print(f"|--------|----------|--------|-------------|")
    print(f"| **Requests/sec (p50)** | {uncached_rps:.0f} req/s | {cached_rps:.0f} req/s | **+{throughput_improvement:.0f}%** |")

    stats = await cache_manager.get_statistics()
    print(f"\n## Cache Statistics\n")
    print(f"- **Cache Hit Ratio:** {stats.hit_ratio * 100:.1f}%")
    print(f"- **Total Hits:** {stats.hits}")
    print(f"- **Total Misses:** {stats.misses}")
    print(f"- **Entry Count:** {stats.entry_count}")
    print(f"- **Memory Usage:** {stats.memory_usage_bytes / 1024:.1f} KB")

    print("\n## Interpretation\n")
    if p50_improvement > 80:
        print("✅ **Excellent** - Cache is providing substantial performance improvement")
    elif p50_improvement > 50:
        print("✅ **Good** - Cache is effectively reducing latency")
    elif p50_improvement > 20:
        print("⚠️  **Moderate** - Cache is helping but consider optimization")
    else:
        print("❌ **Poor** - Cache may not be configured optimally")

    if stats.hit_ratio > 0.9:
        print("✅ **High hit ratio** - Cache is effectively reusing data")
    elif stats.hit_ratio > 0.7:
        print("✅ **Good hit ratio** - Cache is performing well")
    else:
        print("⚠️  **Low hit ratio** - Consider increasing TTL or cache size")


def main():
    parser = argparse.ArgumentParser(description="Benchmark cache performance")
    parser.add_argument("--iterations", type=int, default=1000,
                        help="Number of benchmark iterations (default: 1000)")
    parser.add_argument("--reuse-factor", type=int, default=100,
                        help="Number of unique keys to cycle through (default: 100)")

    args = parser.parse_args()

    asyncio.run(run_benchmark(args.iterations, args.reuse_factor))


if __name__ == "__main__":
    main()
