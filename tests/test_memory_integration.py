import asyncio
import pytest

from candidate.memory.consolidation import (
    ConsolidationOrchestrator, ConsolidationMode, InMemoryStore
)
from candidate.memory.structural_conscience import StructuralConscience

@pytest.mark.asyncio
async def test_end_to_end_consolidation():
    store = InMemoryStore.seed_demo(48)
    orch = ConsolidationOrchestrator(store=store, mode=ConsolidationMode.STANDARD)
    await orch.orchestrate_consolidation(num_cycles=1)

    metrics = orch.metrics_snapshot()
    assert metrics["folds_created"] > 0
    assert metrics["traces_consolidated"] > 0

    # Validate folds structurally
    sc = StructuralConscience()
    # Check last 3 folds
    for fold in store.long_term[-3:]:
        report = sc.validate_memory_structure(fold)
        assert report.ok, f"fold failed structural checks: {report}"