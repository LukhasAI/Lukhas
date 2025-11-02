#!/usr/bin/env python3
"""
Mode comparison: STANDARD vs INTENSIVE vs MAINTENANCE consolidation.
Shows control dial story for different throughput/safety trade-offs.
"""
import asyncio
import logging

# Silence noisy optional imports for clean demo
for noisy in [
    "candidate.core.colonies",
    "candidate.core.symbolism",
    "candidate.memory.systems",
]:
    logging.getLogger(noisy).setLevel(logging.ERROR)

from memory.consolidation import ConsolidationMode, ConsolidationOrchestrator, InMemoryStore
from memory.structural_conscience import StructuralConscience


async def run_mode_comparison(seed: int = 2025):
    """Compare all three consolidation modes."""
    print(f"=== MODE COMPARISON (seed={seed}) ===\n")

    modes = [
        (ConsolidationMode.MAINTENANCE, "Low throughput, minimal resource usage"),
        (ConsolidationMode.STANDARD, "Balanced throughput and safety"),
        (ConsolidationMode.INTENSIVE, "High throughput, resource intensive"),
    ]

    results = {}

    for mode, description in modes:
        print(f"{mode.value.upper()} MODE: {description}")

        store = InMemoryStore.seed_demo(64, seed=seed)
        orch = ConsolidationOrchestrator(store=store, mode=mode)
        await orch.orchestrate_consolidation(num_cycles=2)

        sc = StructuralConscience()
        reports = [sc.validate_memory_structure(f) for f in store.long_term]
        ok_count = sum(1 for r in reports if r.ok)

        metrics = orch.metrics_snapshot()
        results[mode] = {
            "folds": metrics["folds_created"],
            "quarantined": metrics["quarantined_folds"],
            "structural_ok": ok_count / max(1, len(reports)),
            "runtime_ms": metrics["last_run_s"] * 1000,
            "traces": metrics["traces_consolidated"],
        }

        print(f"   Folds created: {metrics['folds_created']}")
        print(f"   Quarantined: {metrics['quarantined_folds']}")
        print(f"   Structural OK: {ok_count}/{len(reports)} ({ok_count/max(1,len(reports)):.1%})")
        print(f"   Traces processed: {metrics['traces_consolidated']}")
        print(f"   Runtime: {metrics['last_run_s']*1000:.1f}ms")
        print()

    print("=== MODE COMPARISON SUMMARY ===")
    print("Mode        │ Folds │ Quarantined │ Structural │ Runtime │ Efficiency")
    print("────────────┼───────┼─────────────┼────────────┼─────────┼──────────")

    for mode, description in modes:
        r = results[mode]
        efficiency = r["folds"] / max(1, r["runtime_ms"]) if r["runtime_ms"] > 0 else 0
        print(
            f"{mode.value:<11} │ {r['folds']:5d} │ {r['quarantined']:11d} │ {r['structural_ok']:9.1%} │ {r['runtime_ms']:6.1f}ms │ {efficiency:8.0f} f/s"
        )

    print("\n=== INVESTOR INSIGHTS ===")
    std = results[ConsolidationMode.STANDARD]
    intensive = results[ConsolidationMode.INTENSIVE]
    maintenance = results[ConsolidationMode.MAINTENANCE]

    print(
        f"• INTENSIVE mode: {intensive['folds']/std['folds']:.1f}x more folds, {intensive['quarantined']/max(1,std['quarantined']):.1f}x quarantine rate"
    )
    print(
        f"• MAINTENANCE mode: {maintenance['folds']/std['folds']:.1f}x folds, {maintenance['quarantined']/max(1,std['quarantined']):.1f}x quarantine rate"
    )
    print(f"• All modes maintain ≥{min(r['structural_ok'] for r in results.values()):.0%} structural integrity")
    print("• Control dial: adjust mode based on workload vs safety requirements")


if __name__ == "__main__":
    asyncio.run(run_mode_comparison())
