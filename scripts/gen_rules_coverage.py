#!/usr/bin/env python3
"""
Render a readable coverage report for star rules.

Inputs:
- docs/audits/star_rules_lint.json (produced by scripts/lint_star_rules.py)

Outputs:
- docs/audits/star_rules_coverage.md (tables + zero-hit highlights)
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def as_table(title: str, rows: list[tuple[str,int]]) -> str:
    lines = [f"## {title}", "", "| Key | Count |", "|---|---:|"]
    for k, v in rows:
        lines.append(f"| `{k}` | {v} |")
    lines.append("")
    return "\n".join(lines)

def main():
    lint_path = Path("docs/audits/star_rules_lint.json")
    out_path  = Path("docs/audits/star_rules_coverage.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not lint_path.exists():
        print(f"[ERROR] Missing {lint_path}. Run scripts/lint_star_rules.py first.", file=sys.stderr)
        sys.exit(2)

    data = load(lint_path)
    hc = data.get("hit_counts", {})

    sections = [
        ("Rule matches (path/keyword)", hc.get("rules", {})),
        ("Capability overrides (hits)", hc.get("capability_overrides", {})),
        ("Node overrides (hits)", hc.get("node_overrides", {})),
        ("Owner priors (hits)", hc.get("owner_priors", {})),
        ("Dependency hints (hits)", hc.get("dependency_hints", {})),
        ("Exclusions (triggered)", hc.get("exclusions", {})),
    ]

    md = []
    md.append("# Star Rules Coverage\n")
    md.append(f"- Rules file: `{data.get('rules_file','configs/star_rules.json')}`")
    md.append(f"- Manifests scanned: **{data.get('totals',{}).get('manifests_scanned',0)}**")
    md.append(f"- Supporting count: **{data.get('totals',{}).get('supporting_count',0)}**")
    md.append("")

    # Zero-hit rules
    zero = data.get("zero_hit_rules", [])
    if zero:
        md.append("## Zero-hit rules (needs review)\n\nThese regex rules matched nothing across the current manifests. Consider deleting, fixing, or moving them into `rules/experiments/`.\n")
        md.append("| Rule |")
        md.append("|---|")
        for z in zero:
            md.append(f"| `{z}` |")
        md.append("")
    else:
        md.append("## Zero-hit rules\n- None ✅\n")

    # Tables
    for title, mapping in sections:
        rows = sorted(mapping.items(), key=lambda x: x[1], reverse=True)
        md.append(as_table(title, rows[:100]))

    # Top opportunities (which stars got the most rule hits)
    star_totals = defaultdict(int)
    for key, cnt in (hc.get("rules", {}) or {}).items():
        # key format: "{STAR}::{regex}"
        star = key.split("::", 1)[0]
        star_totals[star] += cnt
    star_rows = sorted(star_totals.items(), key=lambda x: x[1], reverse=True)
    md.append(as_table("Rule activity by star (top)", star_rows))

    out_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"[OK] Wrote {out_path}")

if __name__ == "__main__":
    main()
