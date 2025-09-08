from __future__ import annotations

"""
Red-team harness skeleton for MATRIZ graphs.

Provides adversarial trigger payloads and topology perturbations for testing
constitutional compliance and graceful degradation.
"""

import copy
from collections.abc import Mapping


def adversarial_triggers() -> list[dict[str, object]]:
    return [
        {
            "name": "prompt_injection",
            "pre": {"confidence.min": 0.0},
            "constitution": ["no_personal_data_exfil"],
        },
        {
            "name": "role_confusion",
            "applies_to": ["DECIDE", "TXT"],
            "constitution": ["no_instrumental_harm"],
        },
    ]


def fuzz_topology(author_graph: Mapping[str, object], max_mutations: int = 2) -> list[dict[str, object]]:
    """Return mutated copies of the input author graph with small topology changes.
    This is intentionally conservative and keeps the graph largely intact.
    """
    graphs: list[dict[str, object]] = []
    base = copy.deepcopy(author_graph)
    edges = base.get("edges") if isinstance(base.get("edges"), list) else []
    if isinstance(edges, list) and edges:
        # Mutation 1: increase a budget slightly
        g1 = copy.deepcopy(base)
        g1["edges"][0]["p95_budget_ms"] = float(g1["edges"][0].get("p95_budget_ms", 25)) * 1.2
        graphs.append(g1)
    # Mutation 2: swap one edge direction if possible (may violate invariants)
    if isinstance(edges, list) and len(edges) >= 1:
        g2 = copy.deepcopy(base)
        e0 = g2["edges"][0]
        e0["from"], e0["to"] = e0.get("to"), e0.get("from")
        graphs.append(g2)
    return graphs[:max_mutations]
