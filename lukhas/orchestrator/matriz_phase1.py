from __future__ import annotations

import json
from typing import Any, Dict

from MATRIZ.nodes.phase1 import (
    AttentionController,
    EpisodicMemory,
    NodeContext,
    NodeRegistry,
    WorkingMemory,
)
from MATRIZ.nodes.phase1.events import wavec_checkpoint

DEFAULT_CONFIG = {
    "working_memory": {"capacity": 7},
    "attention_controller": {"top_k": 3, "temperature": 1.0},
    "episodic_memory": {},
    "wavec_every_n": 10,
}

def _load_config(path: str | None) -> Dict[str, Any]:
    if not path:
        return dict(DEFAULT_CONFIG)
    # Accept YAML or JSON; for now parse JSON if .json else fallback to defaults
    try:
        if path.endswith(".json"):
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return dict(DEFAULT_CONFIG)

def compose_phase1(config_path: str | None = None) -> NodeRegistry:
    cfg = _load_config(config_path)
    reg = NodeRegistry()
    # Register nodes (in dependency‑light order)
    wm = WorkingMemory(**cfg.get("working_memory", {}))
    attn = AttentionController(**cfg.get("attention_controller", {}))
    epi = EpisodicMemory(**cfg.get("episodic_memory", {}))
    reg.register(wm)
    reg.register(attn)
    reg.register(epi)
    return reg

def run_phase1_cycle(registry: NodeRegistry, run_id: str, cycle_idx: int, seed: int) -> Dict[str, Any]:
    ctx = NodeContext(run_id=run_id, cycle_idx=cycle_idx, seed=seed)
    wm = registry.get("working_memory")
    attn = registry.get("attention_controller")
    epi = registry.get("episodic_memory")

    # Warmup (idempotent)
    wm.warmup(ctx); attn.warmup(ctx); epi.warmup(ctx)

    # Minimal dataflow:
    wm_out = wm.process(ctx, item={"cycle": cycle_idx, "goal": "phase1-demo"})
    attn_out = attn.process(ctx, scores=[0.1, 0.7, 0.2, 0.3])
    epi.process(ctx, append=True, time=f"t{cycle_idx}", context={"demo": True},
                affect={"valence": 0.1}, payload={"wm_size": len(wm_out["wm_items"])})

    # WaveC checkpoint cadence
    every_n = 10
    if cycle_idx % every_n == 0:
        snapshot = {"wm_len": len(wm_out["wm_items"]), "attn": attn_out.get("attn", [])}
        wavec_checkpoint(run_id, cycle_idx, snapshot)

    return {"wm": wm_out, "attn": attn_out, "epi_count": registry.get("episodic_memory").process(ctx)["count"]}
