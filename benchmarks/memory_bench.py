from __future__ import annotations

import argparse
import json
import random
import time
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from memory.adaptive_memory import AdaptiveMemorySystem, MemoryType
from memory.fold_system import FoldManager

# ΛTAG: performance_benchmark


@dataclass
class BenchmarkResult:
    name: str
    samples: list[float]

    def summary(self) -> dict[str, Any]:
        if not self.samples:
            return {"name": self.name, "avg_ms": 0.0, "p95_ms": 0.0, "max_ms": 0.0}
        sorted_samples = sorted(self.samples)
        p95_index = max(0, int(len(sorted_samples) * 0.95) - 1)
        return {
            "name": self.name,
            "avg_ms": sum(sorted_samples) / len(sorted_samples),
            "p95_ms": sorted_samples[p95_index],
            "max_ms": sorted_samples[-1],
            "samples": len(sorted_samples),
        }


def _time_ops(iterations: int, func: callable) -> list[float]:
    latencies: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        latencies.append((time.perf_counter() - start) * 1000)
    return latencies


def benchmark_fold_manager(create_count: int, recall_iterations: int) -> BenchmarkResult:
    manager = FoldManager()
    for idx in range(create_count):
        manager.create_fold({"content": f"item-{idx}"}, importance=0.5, mode="live")

    ids = list(manager.folds.keys())
    rng = random.Random(7)

    def _recall() -> None:
        target = rng.choice(ids)
        manager.retrieve_fold(target, mode="live")

    latencies = _time_ops(recall_iterations, _recall)
    return BenchmarkResult("fold_manager_recall", latencies)


def benchmark_adaptive_memory(item_count: int, recalls: int) -> BenchmarkResult:
    system = AdaptiveMemorySystem(enable_embeddings=True)
    rng = random.Random(11)
    dimension = 8

    for idx in range(item_count):
        embedding = [rng.random() for _ in range(dimension)]
        system.store(
            f"memory-{idx}",
            memory_type=MemoryType.SEMANTIC,
            embedding=embedding,
            importance=rng.random(),
        )

    query = [rng.random() for _ in range(dimension)]

    def _recall() -> None:
        system.recall_top_k(k=5, query_embedding=query)

    latencies = _time_ops(recalls, _recall)
    return BenchmarkResult("adaptive_memory_recall", latencies)


def run_benchmarks(smoke: bool = False) -> list[BenchmarkResult]:
    create_count = 500 if smoke else 5000
    recall_iterations = 100 if smoke else 1000
    item_count = 500 if smoke else 4000
    recalls = 50 if smoke else 400

    results = [
        benchmark_fold_manager(create_count, recall_iterations),
        benchmark_adaptive_memory(item_count, recalls),
    ]
    return results


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run LUKHAS performance benchmarks")
    parser.add_argument("--smoke", action="store_true", help="Run a lightweight benchmark set")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args(list(argv) if argv is not None else None)

    results = run_benchmarks(smoke=args.smoke)
    summaries = [result.summary() for result in results]

    if args.json:
        print(json.dumps({"benchmarks": summaries}, indent=2))
    else:
        for summary in summaries:
            print(f"🔬 {summary['name']} avg={summary['avg_ms']:.2f}ms p95={summary['p95_ms']:.2f}ms max={summary['max_ms']:.2f}ms")

    # Flag perf regressions via exit code if budgets broken in non-smoke mode
    if not args.smoke:
        budgets = {
            "fold_manager_recall": 100.0,
            "adaptive_memory_recall": 120.0,
        }
        for summary in summaries:
            budget = budgets.get(summary["name"])
            if budget is not None and summary["p95_ms"] > budget:
                print(
                    f"❌ Benchmark {summary['name']} exceeded p95 budget ({summary['p95_ms']:.2f}ms > {budget}ms)",
                    flush=True,
                )
                return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
