#!/usr/bin/env python3
"""
Module: suggest_star_promotions.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, List, Tuple


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not read {path}: {e}", file=sys.stderr)
        return None

def normalize_star(s: str) -> str:
    return s.strip()

def build_regex(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)

def choose_best(candidates: List[Tuple[str, float, str]], min_conf: float) -> Tuple[str, float, str] | None:
    if not candidates:
        return None
    # Prefer highest confidence; stable tiebreaker by star label
    candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
    best = candidates[0]
    return best if best[1] >= min_conf else None

def main():
    ap = argparse.ArgumentParser(description="Suggest star promotions for Supporting modules.")
    ap.add_argument("--manifests", default="manifests", help="Root of manifests/")
    ap.add_argument("--rules", default="configs/star_rules.json", help="Ruleset JSON")
    ap.add_argument("--out", default="docs/audits", help="Output folder")
    ap.add_argument("--min-confidence", type=float, default=None, help="Override ruleset min_confidence")
    args = ap.parse_args()

    ruleset = load_json(Path(args.rules)) or {}
    min_conf = args.min_confidence if args.min_confidence is not None else float(ruleset.get("confidence", {}).get("min_suggest", 0.50))
    deny = set(ruleset.get("deny", []))

    # Compile patterns
    rule_patterns = [(build_regex(r["pattern"]), normalize_star(r["star"]), r.get("source", "path_keywords"))
                     for r in ruleset.get("rules", [])]
    cap_over = {r["capability"]: normalize_star(r["star"]) for r in ruleset.get("capability_overrides", [])}
    node_over = {r["node"]: normalize_star(r["star"]) for r in ruleset.get("node_overrides", [])}

    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_scripts_suggest_star_promotions_py_L61"}

    promotions = []
    counts = Counter()

    for mp in sorted(Path(args.manifests).rglob("module.manifest.json")):
        if '/.archive/' in str(mp):
            continue
        data = load_json(mp)
        if not isinstance(data, dict):
            continue

        align = data.get("constellation_alignment", {}) or {}
        primary = normalize_star(align.get("primary_star", "Supporting"))
        if primary != "Supporting":
            continue

        module = data.get("module", {}) or {}
        name = module.get("name") or module.get("path") or str(mp.parent)
        path_str = str(mp.parent)

        caps = data.get("capabilities", []) or []
        nodes = (data.get("matriz_integration", {}) or {}).get("pipeline_nodes", []) or []

        candidates: List[Tuple[str, float, str]] = []

        # 1) capability overrides (weight 0.6)
        for c in caps:
            cap_name = (c.get("name") or "").strip()
            star = cap_over.get(cap_name)
            if star:
                candidates.append((star, 0.6, f"capability:{cap_name}"))

        # 2) node overrides (weight 0.5)
        for n in nodes:
            star = node_over.get(n)
            if star:
                candidates.append((star, 0.5, f"node:{n}"))

        # 3) path/keyword rules (weight 0.4 if matched)
        for rx, star, src in rule_patterns:
            if rx.search(path_str) or (name and rx.search(name)):
                candidates.append((star, 0.4, f"{src}:{rx.pattern}"))

        # pick best
        best = choose_best(candidates, min_conf)
        if not best:
            continue
        new_star, conf, reason = best
        if new_star in deny:
            continue

        promotions.append({
            "module": name,
            "file": str(mp),
            "current_star": primary,
            "suggested_star": new_star,
            "confidence": round(conf, 2),
            "reason": reason
        })
        counts[new_star] += 1

    # Write CSV
    csv_path = out_dir / "star_promotions.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["module","file","current_star","suggested_star","confidence","reason"])
        w.writeheader()
        for row in promotions:
            w.writerow(row)

    # Write Markdown summary
    md_path = out_dir / "star_promotions.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Suggested Star Promotions (Supporting → Specific)\n\n")
        f.write(f"- Min confidence: **{min_conf}**\n")
        f.write(f"- Total suggestions: **{len(promotions)}**\n\n")
        f.write("## By Star\n\n| Star | Count |\n|---|---:|\n")
        for k, v in counts.most_common():
            f.write(f"| {k} | {v} |\n")
        f.write("\n## Details\n\n")
        f.write("| Module | Suggested | Confidence | Reason | File |\n|---|---|---:|---|---|\n")
        for row in promotions[:500]:
            f.write(f"| {row['module']} | {row['suggested_star']} | {row['confidence']} | {row['reason']} | `{row['file']}` |\n")

    print(f"[OK] Wrote {csv_path} and {md_path}")

if __name__ == "__main__":
    main()
