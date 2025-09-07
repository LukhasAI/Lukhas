from __future__ import annotations

import json
import os
from typing import Any

import yaml
import streamlit as st

CHECK_KINDS = {
    "require_provenance",
    "mask_pii",
    "budget_limit",
    "age_gate",
    "content_policy",
}


def load_pack(policy_root: str, jurisdiction: str = "global") -> dict[str, Any]:
    base = os.path.join(policy_root, jurisdiction)
    with open(os.path.join(base, "policy.yaml"), encoding="utf-8") as f:
        policy = yaml.safe_load(f)
    with open(os.path.join(base, "mappings.yaml"), encoding="utf-8") as f:
        mappings = yaml.safe_load(f)
    return {"root": base, "policy": policy, "mappings": mappings}


def coverage_matrix(mappings: dict[str, Any]) -> dict[str, list[str]]:
    tasks = mappings.get("tasks", {})
    out: dict[str, list[str]] = {}
    for task, checks in tasks.items():
        if task == "_default_":
            continue
        kinds = [c.get("kind") for c in checks]
        out[task] = kinds
    return out


def gap_analysis(matrix: dict[str, list[str]]) -> list[dict[str, Any]]:
    gaps = []
    for task, kinds in matrix.items():
        kset = set(kinds)
        if "mask_pii" not in kset:
            gaps.append({"task": task, "gap": "no_mask_pii"})
        if "require_provenance" not in kset:
            gaps.append({"task": task, "gap": "no_provenance"})
        # Example additional checks you may require:
        # if task seems medical and content_policy(medical_high_risk) not present:
        if "medical" in task and "content_policy" not in kset:
            gaps.append({"task": task, "gap": "no_medical_policy"})
    return gaps


def to_markdown(matrix: dict[str, list[str]], gaps: list[dict[str, Any]]) -> str:
    lines = [
        "# Policy Coverage Report",
        "",
        "## Task → Checks",
        "",
        "| Task | Checks |",
        "|---|---|",
    ]
    for task, kinds in sorted(matrix.items()):
        lines.append(f"| `{task}` | {', '.join(sorted(kinds)} |")
    lines += ["", "## Gaps", "", "| Task | Gap |", "|---|---|"]
    if not gaps:
        lines.append("| ✓ | No gaps detected |")
    else:
        for g in gaps:
            lines.append(f"| `{g['task']}` | {g['gap']} |")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Policy Coverage Reporter")
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--out-json")
    ap.add_argument("--out-md")
    args = ap.parse_args()

    pack = load_pack(args.policy_root, args.jurisdiction)
    matrix = coverage_matrix(pack["mappings"])
    gaps = gap_analysis(matrix)
    report = {"jurisdiction": args.jurisdiction, "matrix": matrix, "gaps": gaps}

    print(json.dumps(report, indent=2))
    if args.out_json:
        os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    if args.out_md:
        md = to_markdown(matrix, gaps)
        os.makedirs(os.path.dirname(args.out_md), exist_ok=True)
        with open(args.out_md, "w", encoding="utf-8") as f:
            f.write(md)
