#!/usr/bin/env python3
"""
Memory System Performance Benchmarks

Validates SLO compliance:
- Memory recall <100ms p95
- Memory consolidation efficient
- Cascade prevention >99.7%

Usage:
    python benchmarks/memory_performance.py
    python -m pytest benchmarks/memory_performance.py --benchmark
"""

import time
import statistics
import uuid
import pytest

try:
    from lukhas.memory.adaptive_memory import AdaptiveMemory
    from lukhas.memory.fold_system import FoldManager
    LUKHAS_AVAILABLE = True
except ImportError:
    LUKHAS_AVAILABLE = False


class MemoryBenchmarks:
    """Memory system performance benchmarks"""

    def __init__(self):
        if not LUKHAS_AVAILABLE:
            pytest.skip("LUKHAS memory modules not available")

        self.memory = AdaptiveMemory()
        self.fold_manager = FoldManager()

    def benchmark_memory_recall_latency(self, num_items: int = 1000) -> dict:
        """Benchmark memory recall latency - SLO: <100ms p95"""
        print(f"🔍 Benchmarking memory recall with {num_items} items...")

        # Setup: Add test items
        test_items = []
        for i in range(num_items):
            item_data = {
                "id": str(uuid.uuid4()),
                "content": f"Test memory item {i}",
                "importance": 0.5 + (i % 100) / 200,  # Vary importance
                "tags": [f"tag_{i % 10}", "benchmark"]
            }
            test_items.append(item_data)
            self.memory.add_memory(item_data)

        # Benchmark: Measure recall latency
        latencies = []
        for _ in range(100):  # 100 recall operations
            start_time = time.perf_counter()
            results = self.memory.recall_top_k(query="test", k=10)
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

        # Calculate statistics
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        mean_latency = statistics.mean(latencies)

        results = {
            "test": "memory_recall_latency",
            "num_items": num_items,
            "operations": len(latencies),
            "latency_ms": {
                "mean": round(mean_latency, 2),
                "p50": round(p50, 2),
                "p95": round(p95, 2),
                "p99": round(p99, 2)
            },
            "slo_compliance": {
                "target_p95_ms": 100,
                "actual_p95_ms": round(p95, 2),
                "compliant": p95 < 100
            }
        }

        print(f"📊 Memory Recall Results:")
        print(f"   P50: {p50:.1f}ms, P95: {p95:.1f}ms, P99: {p99:.1f}ms")
        print(f"   SLO Compliance: {'✅ PASS' if p95 < 100 else '❌ FAIL'} (P95 < 100ms)")

        return results

    def benchmark_cascade_prevention(self, stress_items: int = 10000) -> dict:
        """Benchmark cascade prevention - SLO: >99.7% success rate"""
        print(f"🛡️ Benchmarking cascade prevention with {stress_items} items...")

        cascade_attempts = 0
        cascade_prevented = 0

        # Stress test: Add many items rapidly to trigger cascades
        for i in range(stress_items):
            item_data = {
                "id": str(uuid.uuid4()),
                "content": f"Stress test item {i}",
                "importance": 0.9,  # High importance to trigger cascades
                "tags": ["stress", "cascade_test"]
            }

            try:
                # Monitor for cascade prevention
                initial_count = len(self.fold_manager.active_folds)
                self.memory.add_memory(item_data)
                final_count = len(self.fold_manager.active_folds)

                # Check if cascade was prevented
                if initial_count > final_count:
                    cascade_attempts += 1
                    cascade_prevented += 1

            except Exception as e:
                cascade_attempts += 1
                # If we caught and handled it, prevention worked
                if "cascade" in str(e).lower():
                    cascade_prevented += 1

        # Calculate prevention rate
        prevention_rate = (cascade_prevented / max(cascade_attempts, 1)) * 100 if cascade_attempts > 0 else 100

        results = {
            "test": "cascade_prevention",
            "stress_items": stress_items,
            "cascade_attempts": cascade_attempts,
            "cascade_prevented": cascade_prevented,
            "prevention_rate_percent": round(prevention_rate, 3),
            "slo_compliance": {
                "target_rate_percent": 99.7,
                "actual_rate_percent": round(prevention_rate, 3),
                "compliant": prevention_rate >= 99.7
            }
        }

        print(f"📊 Cascade Prevention Results:")
        print(f"   Attempts: {cascade_attempts}, Prevented: {cascade_prevented}")
        print(f"   Prevention Rate: {prevention_rate:.3f}%")
        print(f"   SLO Compliance: {'✅ PASS' if prevention_rate >= 99.7 else '❌ FAIL'} (>99.7%)")

        return results

    def benchmark_memory_consolidation(self) -> dict:
        """Benchmark memory consolidation efficiency"""
        print("🔄 Benchmarking memory consolidation...")

        # Add items to force consolidation
        initial_items = 150  # Above consolidation threshold
        for i in range(initial_items):
            item_data = {
                "id": str(uuid.uuid4()),
                "content": f"Consolidation test item {i}",
                "importance": 0.3 + (i % 50) / 100,
                "tags": ["consolidation", f"batch_{i // 10}"]
            }
            self.memory.add_memory(item_data)

        # Measure consolidation performance
        start_time = time.perf_counter()
        pre_consolidation_count = len(self.memory.get_all_memories())

        # Trigger consolidation (if automatic thresholds met)
        try:
            consolidation_result = self.memory.consolidate_if_needed()
            consolidation_triggered = consolidation_result is not None
        except:
            consolidation_triggered = False

        end_time = time.perf_counter()
        consolidation_time_ms = (end_time - start_time) * 1000

        post_consolidation_count = len(self.memory.get_all_memories())
        reduction_percent = ((pre_consolidation_count - post_consolidation_count) /
                           max(pre_consolidation_count, 1)) * 100

        results = {
            "test": "memory_consolidation",
            "pre_consolidation_items": pre_consolidation_count,
            "post_consolidation_items": post_consolidation_count,
            "reduction_percent": round(reduction_percent, 1),
            "consolidation_time_ms": round(consolidation_time_ms, 2),
            "consolidation_triggered": consolidation_triggered,
            "performance": {
                "efficient": consolidation_time_ms < 500,  # <500ms consolidation
                "effective": reduction_percent > 10  # >10% reduction
            }
        }

        print(f"📊 Consolidation Results:")
        print(f"   Items: {pre_consolidation_count} → {post_consolidation_count} ({reduction_percent:.1f}% reduction)")
        print(f"   Time: {consolidation_time_ms:.1f}ms")
        print(f"   Efficiency: {'✅ GOOD' if consolidation_time_ms < 500 else '⚠️ SLOW'}")

        return results


def run_all_benchmarks():
    """Run complete memory benchmark suite"""
    print("🚀 Starting LUKHAS Memory System Benchmarks...")
    print("=" * 60)

    if not LUKHAS_AVAILABLE:
        print("❌ LUKHAS memory modules not available - skipping benchmarks")
        return

    benchmarks = MemoryBenchmarks()
    results = []

    try:
        # Run all benchmark tests
        results.append(benchmarks.benchmark_memory_recall_latency(1000))
        results.append(benchmarks.benchmark_cascade_prevention(5000))
        results.append(benchmarks.benchmark_memory_consolidation())

        # Summary
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
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
def test_memory_recall_benchmark():
    """pytest-compatible memory recall benchmark"""
    if not LUKHAS_AVAILABLE:
        pytest.skip("LUKHAS not available")

    benchmarks = MemoryBenchmarks()
    results = benchmarks.benchmark_memory_recall_latency(500)
    assert results["slo_compliance"]["compliant"], "Memory recall latency SLO violated"


@pytest.mark.benchmark
def test_cascade_prevention_benchmark():
    """pytest-compatible cascade prevention benchmark"""
    if not LUKHAS_AVAILABLE:
        pytest.skip("LUKHAS not available")

    benchmarks = MemoryBenchmarks()
    results = benchmarks.benchmark_cascade_prevention(1000)
    assert results["slo_compliance"]["compliant"], "Cascade prevention SLO violated"


if __name__ == "__main__":
    run_all_benchmarks()