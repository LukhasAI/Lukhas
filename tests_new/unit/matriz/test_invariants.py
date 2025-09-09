from __future__ import annotations

from tools.matriz.graph_compiler import compile_graph, validate_invariants


def test_valid_minimal_graph_compiles():
    author = {
        "schema_version": "0.1.0",
        "graph": {
            "nodes": {
                "txt_1": {
                    "type": "TXT",
                    "state": {"confidence": {"min": 0, "max": 1, "value": 0.7}},
                },
                "dec_1": {
                    "type": "DECIDE",
                    "state": {"confidence": {"min": 0, "max": 1, "value": 0.6}},
                },
            },
            "edges": [{"from": "txt_1", "to": "dec_1", "kind": "text", "p95_budget_ms": 10}],
            "triggers": [
                {
                    "name": "decide_on_text",
                    "applies_to": ["DECIDE"],
                    "slo": {"p95_ms": 20, "error_budget_pct": 1.0},
                }
            ],
        },
    }
    plan, report = compile_graph(author)
    assert report["ok"], report["violations"]
    assert plan["execution"]["edges"], "edges should be present in plan"


def test_disallowed_edge_pair_detected():
    author = {
        "graph": {
            "nodes": {
                "a": {"type": "DECIDE"},
                "b": {"type": "IMG"},
            },
            "edges": [{"from": "a", "to": "b"}],
        }
    }
    violations = validate_invariants(author)
    assert any("disallowed type pair" in v for v in violations)