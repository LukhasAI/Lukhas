#!/usr/bin/env python3
"""
Ablation test: Quarantine system on/off comparison for investor demo.
Demonstrates the cost vs benefit of structural validation.
"""
import asyncio
import logging

from memory.consolidation import ConsolidationMode, ConsolidationOrchestrator, InMemoryStore
from memory.structural_conscience import StructuralConscience

# Silence noisy optional imports for clean demo
for noisy in [
    "candidate.core.colonies",
    "candidate.core.symbolism",
    "candidate.memory.systems",
]:
    logging.getLogger(noisy).setLevel(logging.ERROR)


class QuarantineDisabledOrchestrator(ConsolidationOrchestrator):
    """Orchestrator with structural validation disabled for ablation."""

    def _run_stage(self, stage):
        # Override to skip quarantine validation
        from memory.consolidation.consolidation_orchestrator import SleepStage
        if stage in (SleepStage.NREM_2, SleepStage.NREM_3):
            batch = self._select_batch()
            if not batch:
                return
            folds = self._consolidate_batch(batch)

            # NO QUARANTINE: Write all folds directly (unsafe)
            remaining = max(0, self.max_folds_per_run - self._metrics["folds_created"])
            folds = folds[:remaining]
            if not folds:
                return

            self.store.write_long_term(folds)
            self.store.mark_consolidated([t.trace_id for t in batch])
            self._metrics["batches"] += 1
            self._metrics["folds_created"] += len(folds)
            self._metrics["traces_consolidated"] += len(batch)
            self.consciousness.publish_event("stage_consolidated", {
                "stage": stage.value,
                "batch": len(batch),
                "folds": len(folds)
            })
        elif stage is SleepStage.REM:
            self.consciousness.publish_event("stage_rem_integration", {"stage": stage.value})
        else:
            self.consciousness.publish_event("stage_stabilize", {"stage": stage.value})

async def run_ablation_comparison(seed: int = 1337):
    """Compare quarantine on vs off for same seed."""
    print(f"=== ABLATION TEST (seed={seed}) ===\n")

    print("1. WITH QUARANTINE (production mode):")
    store_safe = InMemoryStore.seed_demo(64, seed=seed)
    orch_safe = ConsolidationOrchestrator(store=store_safe, mode=ConsolidationMode.STANDARD)
    await orch_safe.orchestrate_consolidation(num_cycles=2)

    sc = StructuralConscience()
    reports_safe = [sc.validate_memory_structure(f) for f in store_safe.long_term]
    ok_safe = sum(1 for r in reports_safe if r.ok)

    metrics_safe = orch_safe.metrics_snapshot()
    print(f"   Folds created: {metrics_safe['folds_created']}")
    print(f"   Quarantined: {metrics_safe['quarantined_folds']}")
    print(f"   Structural OK: {ok_safe}/{len(reports_safe)} ({ok_safe/max(1,len(reports_safe)):.1%})")
    print(f"   Runtime: {metrics_safe['last_run_s']:.4f}s")

    print("\n2. WITHOUT QUARANTINE (unsafe mode):")
    store_unsafe = InMemoryStore.seed_demo(64, seed=seed)  # Same seed
    orch_unsafe = QuarantineDisabledOrchestrator(store=store_unsafe, mode=ConsolidationMode.STANDARD)
    await orch_unsafe.orchestrate_consolidation(num_cycles=2)

    reports_unsafe = [sc.validate_memory_structure(f) for f in store_unsafe.long_term]
    ok_unsafe = sum(1 for r in reports_unsafe if r.ok)

    metrics_unsafe = orch_unsafe.metrics_snapshot()
    print(f"   Folds created: {metrics_unsafe['folds_created']}")
    print(f"   Quarantined: {metrics_unsafe.get('quarantined_folds', 0)}")
    print(f"   Structural OK: {ok_unsafe}/{len(reports_unsafe)} ({ok_unsafe/max(1,len(reports_unsafe)):.1%})")
    print(f"   Runtime: {metrics_unsafe['last_run_s']:.4f}s")

    print("\n=== ABLATION SUMMARY ===")
    fold_diff = metrics_unsafe['folds_created'] - metrics_safe['folds_created']
    safety_diff = (ok_safe/max(1,len(reports_safe))) - (ok_unsafe/max(1,len(reports_unsafe)))

    print(f"Quarantine cost: {fold_diff:+d} fewer folds ({fold_diff/max(1,metrics_unsafe['folds_created']):.1%})")
    print(f"Safety benefit: {safety_diff:+.1%} structural integrity improvement")
    print(f"Quarantined unsafe folds: {metrics_safe['quarantined_folds']}")

    # Show failing fold details
    if ok_unsafe < len(reports_unsafe):
        print("\nStructural failures without quarantine:")
        for i, r in enumerate(reports_unsafe):
            if not r.ok:
                print(f"   Fold {i}: {r.issues} (coherence={r.coherence_score}, risk={r.cascade_risk})")

if __name__ == "__main__":
    asyncio.run(run_ablation_comparison())
