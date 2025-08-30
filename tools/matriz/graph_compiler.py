"""
MATRIZ Graph Compiler v0.1

Parses an authored MATRIZ graph (JSON/dict), applies invariants and budgets,
computes provenance, and emits a runtime plan and validation report.

Usage:
  python -m tools.matriz.graph_compiler input.json --out-dir reports/matriz

Public API (importable for tests):
  - compile_graph(author: dict, inputs: list[tuple[path,str]]) -> tuple[dict, dict]
  - validate_invariants(author: dict) -> list[str]
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, MutableMapping, Sequence
from pathlib import Path

# Allowed node roles for v0.1
ALLOWED_TYPES: set[str] = {
    "TXT",
    "IMG",
    "SND",
    "EMO",
    "DECIDE",
    "CONTEXT",
    "MEMORY",
    "ROUTER",
}

# Allowed edge pairs (from_type -> to_type)
ALLOWED_EDGES: set[tuple[str, str]] = {
    ("TXT", "DECIDE"),
    ("TXT", "CONTEXT"),
    ("CONTEXT", "DECIDE"),
    ("MEMORY", "CONTEXT"),
    ("IMG", "CONTEXT"),
    ("SND", "CONTEXT"),
    ("EMO", "CONTEXT"),
    ("ROUTER", "DECIDE"),
}


def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return "sha256:" + h.hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _get_git_sha() -> str:
    try:
        import subprocess

        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return "TBD"


def _utc_timestamp() -> str:
    try:
        import datetime as _dt

        return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    except Exception:
        return "TBD"


def _node_type(author_graph: Mapping[str, object], node_id: str) -> str | None:
    nodes = author_graph.get("nodes", {})  # type: ignore[assignment]
    node = nodes.get(node_id) if isinstance(nodes, Mapping) else None  # type: ignore[index]
    if isinstance(node, Mapping):
        t = node.get("type")
        if isinstance(t, str):
            return t
    return None


def _collect_nodes(author_graph: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    nodes = author_graph.get("nodes", {})  # type: ignore[assignment]
    return (
        {k: v for k, v in nodes.items() if isinstance(v, Mapping)}
        if isinstance(nodes, Mapping)
        else {}
    )


def _collect_edges(author_graph: Mapping[str, object]) -> list[Mapping[str, object]]:
    edges = author_graph.get("edges", [])  # type: ignore[assignment]
    return [e for e in edges if isinstance(e, Mapping)] if isinstance(edges, list) else []


def _collect_triggers(author_graph: Mapping[str, object]) -> list[Mapping[str, object]]:
    triggers = author_graph.get("triggers", [])  # type: ignore[assignment]
    return [t for t in triggers if isinstance(t, Mapping)] if isinstance(triggers, list) else []


def validate_invariants(author: Mapping[str, object]) -> list[str]:
    """Return list of invariant violations; empty if valid."""
    errs: list[str] = []

    if not isinstance(author.get("graph"), Mapping):
        return ["graph: missing or invalid object"]
    graph = author["graph"]  # type: ignore[assignment]

    nodes = _collect_nodes(graph)
    if not nodes:
        errs.append("graph.nodes: must contain at least one node")

    # Node type whitelist and basic state sanity
    for nid, n in nodes.items():
        t = n.get("type")
        if not isinstance(t, str) or t not in ALLOWED_TYPES:
            errs.append(f"node '{nid}': invalid or disallowed type '{t}'")
        state = n.get("state")
        if isinstance(state, Mapping):
            for k, v in state.items():
                if isinstance(v, Mapping):
                    mn, mx, val = v.get("min"), v.get("max"), v.get("value")
                    if not (isinstance(mn, (int, float)) and isinstance(mx, (int, float))):
                        errs.append(f"node '{nid}': state.{k} must have numeric min/max")
                        continue
                    if mn > mx:
                        errs.append(f"node '{nid}': state.{k} min > max")
                    if val is not None:
                        if not isinstance(val, (int, float)):
                            errs.append(f"node '{nid}': state.{k}.value must be numeric")
                        elif not (mn <= val <= mx):
                            errs.append(f"node '{nid}': state.{k}.value {val} outside [{mn},{mx}]")

    # Edges must connect existing nodes and be allowed by type-pair rules
    edges = _collect_edges(graph)
    for i, e in enumerate(edges):
        src = e.get("from")
        dst = e.get("to")
        if not isinstance(src, str) or not isinstance(dst, str):
            errs.append(f"edge[{i}]: missing 'from' or 'to'")
            continue
        if src not in nodes or dst not in nodes:
            errs.append(f"edge[{i}]: references unknown node(s) '{src}' -> '{dst}'")
            continue
        st = nodes[src].get("type")
        dt = nodes[dst].get("type")
        if isinstance(st, str) and isinstance(dt, str):
            if (st, dt) not in ALLOWED_EDGES:
                errs.append(f"edge[{i}]: disallowed type pair {st}->{dt}")

        p95 = e.get("p95_budget_ms")
        if p95 is not None and not isinstance(p95, (int, float)):
            errs.append(f"edge[{i}]: p95_budget_ms must be numeric")

    # Trigger budget presence and structure
    for i, t in enumerate(_collect_triggers(graph)):
        slo = t.get("slo") if isinstance(t, Mapping) else None
        if slo is not None and isinstance(slo, Mapping):
            p95 = slo.get("p95_ms")
            if p95 is None or not isinstance(p95, (int, float)) or p95 < 0:
                errs.append(f"trigger[{i}]: slo.p95_ms must be non-negative number")
        # Optional: ensure applies_to roles are valid
        roles = t.get("applies_to") if isinstance(t, Mapping) else None
        if roles is not None:
            if not isinstance(roles, list) or not all(isinstance(r, str) for r in roles):
                errs.append(f"trigger[{i}]: applies_to must be list[str]")
            else:
                for r in roles:
                    if r not in ALLOWED_TYPES:
                        errs.append(f"trigger[{i}]: applies_to contains unknown role '{r}'")

    return errs


def compile_graph(
    author: MutableMapping[str, object], inputs: Sequence[tuple[str, str]] | None = None
) -> tuple[dict[str, object], dict[str, object]]:
    """Compile author graph -> (runtime_plan, validation_report).

    - Adds defaults where safe (schema_version, p95 budgets if missing via fallback).
    - Computes provenance with git sha, scope hash, and input hashes.
    - Runs invariant checks and includes results in validation report.
    - Emits a minimal runtime plan with execution groups and budgeted edges.
    """
    # Defaults
    author.setdefault("schema_version", "0.1.0")
    graph = author.setdefault("graph", {})
    if not isinstance(graph, MutableMapping):
        raise ValueError("graph must be an object")

    nodes = graph.setdefault("nodes", {})
    if not isinstance(nodes, MutableMapping):
        raise ValueError("graph.nodes must be an object")

    # Fill default edge p95 if provided but missing
    edges = graph.get("edges")
    if isinstance(edges, list):
        for e in edges:
            if isinstance(e, MutableMapping):
                e.setdefault("p95_budget_ms", 25)

    # Provenance
    inputs = list(inputs or [])
    prov_inputs = [
        {"path": p, "sha256": h} for (p, h) in inputs if isinstance(p, str) and isinstance(h, str)
    ]
    # Scope hash over the canonical JSON of the author graph
    scope_hash = _sha256_bytes(json.dumps(author, sort_keys=True, separators=(",", ":")).encode())
    provenance = {
        "git_sha": _get_git_sha(),
        "timestamp_utc": _utc_timestamp(),
        "scope_hash": scope_hash,
        "inputs": prov_inputs,
    }

    # Invariants
    violations = validate_invariants(author)
    ok = len(violations) == 0

    # Execution groups: naive topological layering via types (TXT/INPUT first, DECIDE later)
    # For v0.1 we sort nodes by a simple key to get deterministic grouping
    node_ids = list(nodes.keys())
    node_ids.sort()
    groups = [[nid] for nid in node_ids]

    # Emit budgeted edges with basic drop policy on breach
    plan_edges: list[dict[str, object]] = []
    for e in _collect_edges(graph):
        src = e.get("from")
        dst = e.get("to")
        if isinstance(src, str) and isinstance(dst, str):
            plan_edges.append(
                {
                    "from": src,
                    "to": dst,
                    "p95_budget_ms": e.get("p95_budget_ms", 25),
                    "drop_on_breach": True,
                }
            )

    runtime_plan: dict[str, object] = {
        "schema_version": "0.1.0",
        "provenance": provenance,
        "execution": {"groups": groups, "edges": plan_edges},
        "triggers": _collect_triggers(graph),
        "observability": {"trace_ids": "stable", "metrics_tags": {}},
    }

    validation_report: dict[str, object] = {
        "schema_version": "0.1.0",
        "provenance": provenance,
        "ok": ok,
        "violations": violations,
        "stats": {"node_count": len(node_ids), "edge_count": len(plan_edges)},
    }

    return runtime_plan, validation_report


def _cli(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MATRIZ Graph Compiler v0.1")
    ap.add_argument("input", help="Author graph JSON path")
    ap.add_argument(
        "--out-dir", default="reports/matriz", help="Output directory for plan and report"
    )
    args = ap.parse_args(argv)

    in_path = Path(args.input)
    if not in_path.exists():
        ap.error(f"input not found: {in_path}")

    author = json.loads(in_path.read_text())
    inputs = [(str(in_path), _sha256_file(in_path))]
    plan, report = compile_graph(author, inputs=inputs)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "runtime_plan.json").write_text(json.dumps(plan, indent=2))
    (out_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {out_dir}/runtime_plan.json and validation_report.json")
    return 0 if report.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(_cli())
