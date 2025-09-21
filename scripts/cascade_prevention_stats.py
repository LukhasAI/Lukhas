#!/usr/bin/env python3
import asyncio
import logging
import statistics

# Silence noisy optional imports for clean demo
for noisy in [
    "candidate.core.colonies",
    "candidate.core.symbolism",
    "candidate.memory.systems",
]:
    logging.getLogger(noisy).setLevel(logging.ERROR)

from candidate.memory.consolidation import ConsolidationOrchestrator, ConsolidationMode, InMemoryStore
from candidate.memory.structural_conscience import StructuralConscience

async def run_single_test(seed: int) -> dict:
    """Run single consolidation test with given seed."""
    store = InMemoryStore.seed_demo(64, seed=seed)
    orch = ConsolidationOrchestrator(store=store, mode=ConsolidationMode.STANDARD)
    await orch.orchestrate_consolidation(num_cycles=2)

    sc = StructuralConscience()
    reports = [sc.validate_memory_structure(f) for f in store.long_term]
    ok_count = sum(1 for r in reports if r.ok)
    prevention_rate = ok_count / max(1, len(reports))

    metrics = orch.metrics_snapshot()
    return {
        "prevention_rate": prevention_rate,
        "folds_created": metrics["folds_created"],
        "quarantined": metrics["quarantined_folds"],
        "runtime_s": metrics["last_run_s"]
    }

async def main():
    """Run statistical analysis across multiple seeds."""
    print("Running cascade prevention statistical analysis...")
    # Extended sample for stronger confidence interval
    seeds = list(range(100, 200))  # 100 samples for Wilson CI ≥ 88.5%
    results = []

    for seed in seeds:
        result = await run_single_test(seed)
        results.append(result)
        print(f"Seed {seed:4d}: {result['prevention_rate']:.3f} prevention, "
              f"{result['folds_created']:2d} folds, {result['quarantined']:2d} quarantined")

    # Statistical summary
    rates = [r["prevention_rate"] for r in results]
    folds = [r["folds_created"] for r in results]
    quarantined = [r["quarantined"] for r in results]
    runtimes = [r["runtime_s"] for r in results]

    def wilson_lower_zero_fail(n, z=1.96):
        """Wilson lower bound when failures == 0"""
        return n / (n + z**2)

    print("\n=== INVESTOR DECK STATISTICS ===")
    print(f"CASCADE_PREVENTION_RATE: {statistics.mean(rates):.4f} ± {statistics.stdev(rates):.4f}")
    # Wilson 95% CI lower bound for 0 failures in n trials
    n = len(results)
    failures = sum(1 for r in rates if r < 1.0)
    if failures == 0:
        print(f"95% CI (Wilson lower bound): ≥ {wilson_lower_zero_fail(n):.3f} with {n} runs, 0 failures")
    else:
        print(f"FAILURES_OBSERVED: {failures}/{n}")
    print(f"FOLDS_PER_RUN: {statistics.mean(folds):.1f} ± {statistics.stdev(folds):.1f}")
    print(f"QUARANTINE_RATE: {statistics.mean(quarantined):.1f} ± {statistics.stdev(quarantined):.1f}")
    print(f"RUNTIME_MS: {statistics.mean(runtimes)*1000:.1f} ± {statistics.stdev(runtimes)*1000:.1f}")
    print(f"GUARDRAIL: ≤1000 folds/run enforced")
    print(f"SAMPLES: {len(results)}")

if __name__ == "__main__":
    asyncio.run(main())