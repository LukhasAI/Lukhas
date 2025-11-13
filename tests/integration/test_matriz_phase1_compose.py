from __future__ import annotations
import types
from lukhas.orchestrator.matriz_phase1 import compose_phase1, run_phase1_cycle
from MATRIZ.nodes.phase1.events import wavec_checkpoint

def test_compose_and_run_smoke(monkeypatch):
    reg = compose_phase1()
    # Monkeypatch WaveC to observe checkpoint calls (no real I/O)
    calls = {}
    def _fake_wavec(run_id, cycle_idx, memory_state):
        calls["last"] = (run_id, cycle_idx, memory_state)
    monkeypatch.setattr("lukhas.orchestrator.matriz_phase1.wavec_checkpoint", _fake_wavec, raising=True)

    last = None
    for c in range(1, 12):  # ensure at least one checkpoint (every 10)
        out = run_phase1_cycle(reg, run_id="r1", cycle_idx=c, seed=42)
        last = out
    assert "wm" in last and "attn" in last
    assert isinstance(last["wm"]["wm_items"], list)
    assert "last" in calls and calls["last"][1] == 10  # checkpoint on cycle 10
