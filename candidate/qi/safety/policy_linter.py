from __future__ import annotations

import argparse
import json
import os

import yaml
import streamlit as st

REQUIRED = {"require_provenance", "mask_pii", "budget_limit"}


def lint(policy_root: str, jurisdiction: str = "global"):
    base = os.path.join(policy_root, jurisdiction)
    mappings = yaml.safe_load(open(os.path.join(base, "mappings.yaml")))
    tasks = mappings.get("tasks", {})
    issues = []
    for task, checks in tasks.items():
        if task == "_default_":
            continue
        kinds = {c.get("kind") for c in checks}
        miss = sorted(REQUIRED - kinds)
        if miss:
            issues.append({"task": task, "missing": miss})
    return {"issues": issues}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--jurisdiction", default="global")
    args = ap.parse_args()
    print(json.dumps(lint(args.policy_root, args.jurisdiction), indent=2))
