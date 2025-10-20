#!/usr/bin/env python3
"""
Module: validate_memory_integration.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
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

    # Honest cascade prevention rate calculation
    ok_count = sum(1 for r in reports if r.ok)
    prevention_rate = round(ok_count / max(1, len(reports)), 4)
    print("CASCADE_PREVENTION_RATE:", prevention_rate)

if __name__ == "__main__":
    asyncio.run(main())
