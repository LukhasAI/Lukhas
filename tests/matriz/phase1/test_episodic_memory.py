from __future__ import annotations
from MATRIZ.nodes.phase1.episodic_memory import EpisodicMemory
from MATRIZ.nodes.phase1.base import NodeContext
from MATRIZ.nodes.phase1 import events as events_mod

def test_epi_append_and_query(monkeypatch):
    epi = EpisodicMemory()
    ctx = NodeContext(run_id="r", cycle_idx=0, seed=42)
    # Intercept event emission for safety "smell test"
    emissions = {}
    def fake_emit(evt):
        emissions["last"] = evt
    monkeypatch.setattr(events_mod, "emit_event", fake_emit, raising=True)

    for i in range(5):
        ctx2 = NodeContext(run_id="r", cycle_idx=i, seed=42)
        epi.process(ctx2, append=True, time=f"t{i}", context={"i": i}, affect={"valence": 0.0}, payload={"x": i})

    out = epi.process(ctx, query_last=2)
    eps = out["episodes"]
    assert len(eps) == 2 and eps[-1]["time"] == "t4"
    assert "last" in emissions and emissions["last"].payload["op"] == "append"
