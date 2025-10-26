#!/usr/bin/env python3
"""
Report stats over generated manifests.

Outputs:
- docs/audits/manifest_stats.json
- docs/audits/manifest_stats.md
- Prints a short summary to stdout

Robust against mixed content: skips non-dict JSON, missing fields, etc.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def load_json(p: Path) -> Any:
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to parse {p}: {e}", file=sys.stderr)
        return None

def coalesce(*vals):
    for v in vals:
        if v not in (None, "", []):
            return v
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifests", default="manifests", help="Root folder containing module.manifest.json files")
    ap.add_argument("--out", default="docs/audits", help="Output folder for stats")
    args = ap.parse_args()

    root = Path(args.manifests)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_paths = sorted([p for p in root.rglob("module.manifest.json") if '/.archive/' not in str(p)])
    if not manifest_paths:
        print(f"[ERROR] No manifests found under {root}", file=sys.stderr)
        sys.exit(2)

    star_counts = Counter()
    tier_counts = Counter()
    node_counts = Counter()
    colony_counts = Counter()
    t1_no_tests = []
    t1_missing_test_paths = []
    capability_gaps = []
    invalid_stars = []
    sample_modules = []

    for mp in manifest_paths:
        data = load_json(mp)
        if not isinstance(data, dict):
            print(f"[WARN] Skipping non-dict JSON: {mp}", file=sys.stderr)
            continue

        module = data.get("module", {}) if isinstance(data.get("module"), dict) else {}
        align  = data.get("constellation_alignment", {}) if isinstance(data.get("constellation_alignment"), dict) else {}
        testing = data.get("testing", {}) if isinstance(data.get("testing"), dict) else {}
        mi = data.get("matriz_integration", {}) if isinstance(data.get("matriz_integration"), dict) else {}

        name = coalesce(module.get("name"), module.get("path"), str(mp.parent))
        star = align.get("primary_star", "Supporting")
        tier = testing.get("quality_tier", None)
        has_tests = bool(testing.get("has_tests", False))
        test_paths_present = "test_paths" in testing
        pipeline_nodes = mi.get("pipeline_nodes", []) if isinstance(mi.get("pipeline_nodes"), list) else []
        colony = module.get("colony", None)

        star_counts[star] += 1
        if tier:
            tier_counts[tier] += 1
        for n in pipeline_nodes:
            node_counts[n] += 1
        if colony is not None:
            colony_counts[str(colony)] += 1

        if tier == "T1_critical" and not has_tests:
            t1_no_tests.append(name)
        if tier == "T1_critical" and not test_paths_present:
            t1_missing_test_paths.append(name)

        caps = data.get("capabilities", [])
        if not caps:
            capability_gaps.append(name)

        if star == "⚛️ Ambiguity (Quantum)":
            invalid_stars.append(f"{name} (deprecated, use '🔮 Oracle (Quantum)')")

        if len(sample_modules) < 25:
            sample_modules.append({
                "module": name,
                "star": star,
                "tier": tier or "",
                "has_tests": has_tests,
                "nodes": pipeline_nodes,
                "colony": colony if colony is not None else "",
                "file": str(mp),
            })

    stats = {
        "total_manifests": sum(star_counts.values()),
        "stars": dict(star_counts),
        "tiers": dict(tier_counts),
        "matriz_nodes": dict(node_counts),
        "colonies": dict(colony_counts),
        "gaps": {
            "t1_no_tests": t1_no_tests,
            "t1_missing_test_paths_property": t1_missing_test_paths,
            "capability_gaps": capability_gaps,
            "invalid_stars": invalid_stars,
        },
        "sample": sample_modules,
    }

    json_path = out_dir / "manifest_stats.json"
    md_path   = out_dir / "manifest_stats.md"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    def md_counts(title: str, c: Counter) -> str:
        lines = [f"### {title}", "", "| Key | Count |", "|---|---|"]
        for k, v in c.most_common():
            lines.append(f"| {k} | {v} |")
        return "\n".join(lines) + "\n"

    md = []
    md.append("# Manifest Statistics\n")
    md.append(f"- Total manifests: **{stats['total_manifests']}**\n")
    md.append(md_counts("Stars", star_counts))
    md.append(md_counts("Quality Tiers", tier_counts))
    md.append(md_counts("MATRIZ Nodes", node_counts))
    if colony_counts:
        md.append(md_counts("Colonies", colony_counts))

    gaps = stats["gaps"]
    md.append("## Gaps\n")
    if not any(gaps.values()):
        md.append("- None ✅\n")
    else:
        if gaps["t1_no_tests"]:
            md.append(f"- T1 without tests: {len(gaps['t1_no_tests'])}\n")
        if gaps["t1_missing_test_paths_property"]:
            md.append(f"- T1 missing `testing.test_paths` property: {len(gaps['t1_missing_test_paths_property'])}\n")
        if gaps["capability_gaps"]:
            md.append(f"- Manifests with empty capabilities: {len(gaps['capability_gaps'])}\n")
        if gaps["invalid_stars"]:
            md.append(f"- Invalid star entries (e.g., Ambiguity): {len(gaps['invalid_stars'])}\n")

    md.append("\n## Sample (up to 25)\n\n")
    md.append("| Module | Star | Tier | Has Tests | Nodes | Colony | File |\n")
    md.append("|---|---|---|---:|---|---|---|\n")
    for s in stats["sample"]:
        md.append(f"| {s['module']} | {s['star']} | {s['tier']} | {str(s['has_tests']).lower()} | {', '.join(s['nodes'])} | {s['colony']} | `{s['file']}` |\n")

    with md_path.open("w", encoding="utf-8") as f:
        f.write("".join(md))

    print(f"[OK] Wrote {json_path} and {md_path}")
    print(f"[SUMMARY] Stars: {dict(star_counts)}")
    print(f"[SUMMARY] Tiers: {dict(tier_counts)}")
    if gaps["invalid_stars"]:
        print(f"[WARN] Invalid stars detected: {len(gaps['invalid_stars'])}")

if __name__ == "__main__":
    main()
