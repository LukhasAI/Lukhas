from __future__ import annotations

from MATRIZ.nodes.phase1.attention_controller import AttentionController
from MATRIZ.nodes.phase1.base import NodeContext


def test_attn_topk_deterministic():
    attn = AttentionController(top_k=2, temperature=1.0)
    ctx = NodeContext(run_id="r", cycle_idx=1, seed=0)
    attn.warmup(ctx)
    out = attn.process(ctx, scores=[0.1, 0.7, 0.2, 0.6])
    assert out["attn"] == [1, 3]
    assert out["entropy"] >= 0.0

def test_attn_empty_scores():
    attn = AttentionController(top_k=2)
    ctx = NodeContext(run_id="r", cycle_idx=2, seed=0)
    out = attn.process(ctx, scores=[])
    assert out["attn"] == []
    assert out["entropy"] == 0.0
