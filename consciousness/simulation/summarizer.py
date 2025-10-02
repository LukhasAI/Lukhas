from __future__ import annotations
from typing import Dict, Any, List, TypedDict

class DreamResult(TypedDict):
    shards: list[dict]
    scores: dict
    trace_id: str

def build_dream_result(seed: Dict[str, Any], rollouts: List[Dict[str, Any]], trace_id: str) -> DreamResult:
    shards = []
    for r in rollouts:
        shards.append({
            "type": "dream_shard",
            "variant": r["variant"],
            "proposal": {
                "problem": seed.get("goal"),
                "approach": r["assumptions"],
                "plan": [
                    "Formulate hypothesis",
                    "Design minimal verification",
                    "Define success metrics",
                ],
                "ul_tags": ["ΛSIM", f"ΛVAR:{r['variant'].upper()}"],
            },
            "risks": [
                {"label": "oversimplification", "mitigation": "expand test coverage"},
                {"label": "distribution shift", "mitigation": "include adversarial examples"},
            ],
            "scores": r["scores"],
        })
    aggregate = {
        "utility_mean": round(sum(s["scores"]["utility"] for s in rollouts) / len(rollouts), 3),
        "risk_max": round(max(s["scores"]["risk"] for s in rollouts), 3),
        "novelty_max": round(max(s["scores"]["novelty"] for s in rollouts), 3),
    }
    return {"shards": shards, "scores": aggregate, "trace_id": trace_id}

def build_matada_nodes(seed: Dict[str, Any], rollouts: List[Dict[str, Any]], trace_id: str, *, schema_ref: str) -> List[dict]:
    nodes = []
    for i, r in enumerate(rollouts, start=1):
        nodes.append({
            "id": f"{trace_id}#N{i}",
            "type": "advisory.plan",
            "lane": "simulation",
            "version": "1.0.0",
            "trace": {"trace_id": trace_id, "order": i},
            "metadata": {
                "variant": r["variant"],
                "schema_ref": schema_ref,
                "ul_tags": ["ΛSIM", f"ΛVAR:{r['variant'].upper()}"],
            },
            "payload": {
                "goal": seed.get("goal"),
                "assumptions": r["assumptions"],
                "scores": r["scores"],
                "plan": ["Formulate hypothesis","Design minimal verification","Define success metrics"],
            },
            "provenance": {
                "generator": "lukhas.consciousness.simulation",
                "inputs": {"ctx_keys": r.get("ctx", [])},
            },
        })
    return nodes
