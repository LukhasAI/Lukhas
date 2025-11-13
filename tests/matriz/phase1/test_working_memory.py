from __future__ import annotations

import time

from MATRIZ.nodes.phase1.base import NodeContext
from MATRIZ.nodes.phase1.working_memory import WorkingMemory


def test_wm_capacity_and_eviction():
    wm = WorkingMemory(capacity=3)
    ctx = NodeContext(run_id="r", cycle_idx=0, seed=123)
    wm.warmup(ctx)
    for i in range(5):
        wm.process(ctx, item={"i": i})
    out = wm.process(ctx)  # no-op call to read state
    assert len(out["wm_items"]) == 3
    # Oldest entries should have been evicted
    assert out["wm_items"][0]["i"] == 2
    assert out["wm_items"][-1]["i"] == 4

def test_wm_latency_budget_sanity():
    wm = WorkingMemory(capacity=64)
    ctx = NodeContext(run_id="r", cycle_idx=0, seed=999, latency_budget_ms=5)
    wm.warmup(ctx)
    start = time.perf_counter()
    for i in range(100):
        wm.process(ctx, item={"i": i})
    ms = (time.perf_counter() - start) * 1000
    assert ms < 100.0  # loose bound; tune later with microbench
