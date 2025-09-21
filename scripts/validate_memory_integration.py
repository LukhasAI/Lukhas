#!/usr/bin/env python3
import asyncio
from candidate.memory.consolidation import ConsolidationOrchestrator, ConsolidationMode, InMemoryStore
from candidate.memory.structural_conscience import StructuralConscience

async def main():
    store = InMemoryStore.seed_demo(64)
    orch = ConsolidationOrchestrator(store=store, mode=ConsolidationMode.STANDARD)
    await orch.orchestrate_consolidation(num_cycles=2)

    sc = StructuralConscience()
    reports = [sc.validate_memory_structure(f) for f in store.long_term]
    ok = all(r.ok for r in reports)

    print("METRICS:", orch.metrics_snapshot())
    print("FOLDS:", len(store.long_term))
    print("STRUCTURAL_OK:", ok)
    if not ok:
        for i, r in enumerate(reports):
            if not r.ok:
                print(i, r)

if __name__ == "__main__":
    asyncio.run(main())