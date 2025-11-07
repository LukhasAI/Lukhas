#!/usr/bin/env python3
"""
Module: lint_star_rules.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ERR = 0

def die(msg: str, code: int = 1):
    print(f"[ERROR] {msg}", file=sys.stderr)
    global ERR
    ERR = 1

def warn(msg: str):
    print(f"[WARN]  {msg}", file=sys.stderr)

def info(msg: str):
    print(f"[INFO]  {msg}")

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"Failed to read JSON {path}: {e}")
        return {}

def compile_rx(pat: str, where: str):
    try:
        return re.compile(pat, re.IGNORECASE)
    except re.error as e:
        die(f"Invalid regex in {where}: {pat} -> {e}")
        return None

def collect_manifests(root: Path):
    for p in root.rglob("module.manifest.json"):
        if '/.archive/' in str(p):
            continue
        try:
            yield p, json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            warn(f"Skipping unreadable manifest {p}: {e}")

def main():
    ap = argparse.ArgumentParser(description="Lint and sanity-check star rules; produce hit counts.")
    ap.add_argument("--rules", default="configs/star_rules.json")
    ap.add_argument("--manifests", default="manifests")
    ap.add_argument("--out", default="docs/audits/star_rules_lint.json")
    ap.add_argument("--fail-on-zero-hits", action="store_true", help="Fail if any rule has 0 matches")
    args = ap.parse_args()

    rules_path = Path(args.rules)
    rules = load_json(rules_path)
    manifests_root = Path(args.manifests)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ---- structural checks
    for k in ["canonical_stars", "rules", "aliases", "weights", "confidence"]:
        if k not in rules:
            die(f"Missing '{k}' in {rules_path}")

    canonical = set(rules["canonical_stars"])
    deny = set(rules.get("deny", []))
    for s in deny:
        if s not in canonical:
            die(f"deny-list contains non-canonical star: {s}")

    # alias validation
    for alias, target in rules.get("aliases", {}).items():
        if target not in canonical:
            die(f"Alias '{alias}' maps to non-canonical star: {target}")

    # weights / confidence
    weights = rules["weights"]
    for k, v in weights.items():
        if not isinstance(v, (int, float)) or v < 0 or v > 1:
            die(f"Weight '{k}' must be 0..1 (got {v})")
    conf = rules["confidence"]
    for k, v in conf.items():
        if not isinstance(v, (int, float)) or v < 0 or v > 1:
            die(f"Confidence '{k}' must be 0..1 (got {v})")

    # compile patterns
    exclusions = [(compile_rx(r["pattern"], "exclusions"), r.get("explain","")) for r in rules.get("exclusions", [])]
    rules_rx = []
    for i, r in enumerate(rules["rules"]):
        star = r.get("star")
        if star not in canonical:
            die(f"Rule #{i} references non-canonical star: {star}")
        rx = compile_rx(r.get("pattern",""), f"rules[{i}]")
        rules_rx.append((rx, star, r.get("source","path_keywords")))
    owner_priors = [(compile_rx(r["owner_regex"], "owner_priors"), r["star"]) for r in rules.get("owner_priors", [])]
    dep_hints = [(compile_rx(r["package_regex"], "dependency_hints"), r["star"]) for r in rules.get("dependency_hints", [])]

    cap_over = {r["capability"]: r["star"] for r in rules.get("capability_overrides", [])}
    node_over = {r["node"]: r["star"] for r in rules.get("node_overrides", [])}
    for s in list(cap_over.values()) + list(node_over.values()):
        if s not in canonical:
            die(f"Override maps to non-canonical star: {s}")

    # ---- hit counting (paths, caps, nodes, owners, deps)
    hit_counts = {
        "rules": Counter(),
        "capability_overrides": Counter(),
        "node_overrides": Counter(),
        "owner_priors": Counter(),
        "dependency_hints": Counter(),
        "exclusions": Counter()
    }
    total_supporting = 0

    for path, m in collect_manifests(manifests_root):
        mod = (m.get("module") or {})
        name = mod.get("name") or mod.get("path") or str(path.parent)
        path_str = str(path.parent)

        align = m.get("constellation_alignment") or {}
        primary = align.get("primary_star", "Supporting")
        is_supporting = (primary == "Supporting")
        if is_supporting:
            total_supporting += 1

        # exclusions (path string)
        for rx, _ex in exclusions:
            if rx and rx.search(path_str):
                hit_counts["exclusions"][rx.pattern] += 1

        # rules over path/name (not gated on supporting; we just count)
        for rx, star, _src in rules_rx:
            if rx and (rx.search(path_str) or (name and rx.search(name))):
                hit_counts["rules"][f"{star}::{rx.pattern}"] += 1

        # caps
        for c in m.get("capabilities") or []:
            cname = (c.get("name") or "").strip()
            if cname in cap_over:
                hit_counts["capability_overrides"][f"{cap_over[cname]}::{cname}"] += 1

        # nodes
        for n in (m.get("matriz_integration") or {}).get("pipeline_nodes", []) or []:
            if n in node_over:
                hit_counts["node_overrides"][f"{node_over[n]}::{n}"] += 1

        # owners
        owner = (m.get("metadata") or {}).get("owner") or ""
        for rx, star in owner_priors:
            if rx and rx.search(owner):
                hit_counts["owner_priors"][f"{star}::{rx.pattern}"] += 1

        # dependencies (external package names)
        for dep in ((m.get("dependencies") or {}).get("external") or []):
            pkg = (dep.get("package") or "")
            for rx, star in dep_hints:
                if rx and rx.search(pkg):
                    hit_counts["dependency_hints"][f"{star}::{rx.pattern}"] += 1

    # zero-hit warnings
    zero_hit_rules = [k for k,v in hit_counts["rules"].items() if v == 0]
    if zero_hit_rules:
        warn(f"{len(zero_hit_rules)} rules have 0 hits")

    # output
    report = {
        "rules_file": str(rules_path),
        "canonical_stars": sorted(canonical),
        "deny": sorted(deny),
        "weights": weights,
        "confidence": conf,
        "totals": {
            "manifests_scanned": sum(1 for _ in manifests_root.rglob("module.manifest.json") if '/.archive/' not in str(_)),
            "supporting_count": total_supporting
        },
        "hit_counts": {k: dict(v) for k,v in hit_counts.items()},
        "zero_hit_rules": zero_hit_rules
    }
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    info(f"Wrote {out_path}")

    if ERR:
        sys.exit(1)
    if args.fail_on_zero_hits and zero_hit_rules:
        die("Zero-hit rules present and --fail-on-zero-hits used.")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
