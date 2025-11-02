#!/usr/bin/env python3
"""Canonical p95 overhead benchmark - apples to apples measurement."""
import os
import random
import statistics
import sys
import time

sys.path.append(".")

os.environ["LUKHAS_EXPERIMENTAL"] = "1"
os.environ["LUKHAS_LANE"] = "labs"

from monitoring.drift_manager import DriftManager


def p95(samples):
    return statistics.quantiles(samples, n=100)[94]


def bench(fn, iters=200, warmup=30):
    random.seed(7)  # Fixed seed for repeatability
    times = []
    for i in range(iters):
        start = time.perf_counter_ns()
        fn()
        dt = (time.perf_counter_ns() - start) / 1e6  # Convert to ms
        times.append(dt)
    return p95(times[warmup:]), times[warmup:]


def baseline_compute():
    """Pure compute path - no repair triggered."""
    manager = DriftManager()
    return manager.compute("ethical", {"compliance": 0.95}, {"compliance": 0.93})  # Below threshold


def repair_compute():
    """Compute path that triggers repair logic."""
    manager = DriftManager()
    manager._initialize_repair_engine()  # Initialize once
    return manager.compute("ethical", {"compliance": 0.95}, {"compliance": 0.70})  # Above threshold


def main():
    print("=== CANONICAL P95 OVERHEAD BENCHMARK ===")
    print("Seed: 7, Warmup: 30, Samples: 170")

    # Measure baseline (compute only, no repair trigger)
    print("\n1. Measuring baseline (compute-only path)...")
    baseline_p95, baseline_times = bench(baseline_compute)
    baseline_avg = sum(baseline_times) / len(baseline_times)

    # Measure with repair logic active (but still compute path)
    print("2. Measuring with repair engine active...")
    repair_p95, repair_times = bench(repair_compute)
    repair_avg = sum(repair_times) / len(repair_times)

    # Calculate overhead
    abs_overhead_ms = repair_p95 - baseline_p95
    pct_overhead = (abs_overhead_ms / baseline_p95) * 100 if baseline_p95 > 0 else 0

    print("\n=== RESULTS ===")
    print(f"Baseline p95:     {baseline_p95:.4f}ms (avg: {baseline_avg:.4f}ms)")
    print(f"With repair p95:  {repair_p95:.4f}ms (avg: {repair_avg:.4f}ms)")
    print(f"Absolute Δ:       {abs_overhead_ms:+.4f}ms")
    print(f"Relative Δ:       {pct_overhead:+.1f}%")

    # Assessment
    passes_pct = abs(pct_overhead) <= 5.0
    passes_abs = abs(abs_overhead_ms) <= 10.0

    print("\n=== GATE ASSESSMENT ===")
    print(f"≤5% target:       {'✅ PASS' if passes_pct else '❌ FAIL'} ({pct_overhead:+.1f}%)")
    print(f"≤10ms absolute:   {'✅ PASS' if passes_abs else '❌ FAIL'} ({abs_overhead_ms:+.4f}ms)")
    print(f"Overall:          {'✅ PASS' if (passes_pct or passes_abs) else '❌ FAIL'}")

    # PR-ready output
    print("\n=== PR METRICS ===")
    print(f"BASELINE_P95_MS={baseline_p95:.4f}")
    print(f"REPAIR_P95_MS={repair_p95:.4f}")
    print(f"OVERHEAD_ABS_MS={abs_overhead_ms:+.4f}")
    print(f"OVERHEAD_PCT={pct_overhead:+.1f}")

    return {
        "baseline_p95": baseline_p95,
        "repair_p95": repair_p95,
        "overhead_ms": abs_overhead_ms,
        "overhead_pct": pct_overhead,
        "passes_gate": passes_pct or passes_abs,
    }


if __name__ == "__main__":
    result = main()
    exit(0 if result["passes_gate"] else 1)
