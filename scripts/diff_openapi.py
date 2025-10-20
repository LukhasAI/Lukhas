#!/usr/bin/env python3
"""
Module: diff_openapi.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Semantic OpenAPI diff (baseline vs candidate) with breaking-change detection.

Breaking changes (exit 2):
- removed path
- removed method on existing path
- removed 2xx response for an operation
- NEW required requestBody added where previously none existed
- removed required parameter

Usage:
  python3 scripts/diff_openapi.py --base docs/openapi/base.json --cand docs/openapi/lukhas-openai.json
"""
import json
import sys
import argparse


def load(p):
    with open(p) as f:
        return json.load(f)


def opkey(path, method):
    return f"{method.upper()} {path}"


def required_params(op):
    out = set()
    for param in op.get("parameters", []) or []:
        if param.get("required"):
            out.add((param.get("in"), param.get("name")))
    return out


def has_required_body(op):
    rb = (op.get("requestBody") or {})
    return bool(rb.get("required") is True)


def two_xx_present(op):
    for code in (op.get("responses") or {}).keys():
        if str(code).startswith("2"):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Baseline OpenAPI spec")
    ap.add_argument("--cand", required=True, help="Candidate OpenAPI spec")
    args = ap.parse_args()

    base = load(args.base)
    cand = load(args.cand)
    bpaths = base.get("paths", {}) or {}
    cpaths = cand.get("paths", {}) or {}

    problems = []
    notes = []

    # Removed paths
    removed_paths = sorted(set(bpaths.keys()) - set(cpaths.keys()))
    for p in removed_paths:
        problems.append(f"REMOVED path: {p}")

    # Compare common paths
    for p in sorted(set(bpaths.keys()) & set(cpaths.keys())):
        bops = bpaths[p] or {}
        cops = cpaths[p] or {}
        bmethods = set(k.lower() for k in bops.keys() if k.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head'])
        cmethods = set(k.lower() for k in cops.keys() if k.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head'])

        # removed methods
        for m in sorted(bmethods - cmethods):
            problems.append(f"REMOVED method: {m.upper()} {p}")

        # per-operation checks
        for m in sorted(bmethods & cmethods):
            bop = bops.get(m) or {}
            cop = cops.get(m) or {}

            # 2xx presence
            if two_xx_present(bop) and not two_xx_present(cop):
                problems.append(f"REMOVED 2xx response: {m.upper()} {p}")

            # requestBody requirement added
            if not has_required_body(bop) and has_required_body(cop):
                problems.append(f"ADDED required requestBody: {m.upper()} {p}")

            # required params removed
            br = required_params(bop)
            cr = required_params(cop)
            removed = br - cr
            for (loc, name) in sorted(removed):
                problems.append(f"REMOVED required param: {m.upper()} {p} [{loc}:{name}]")

            # Additive notes (non-breaking)
            added = cr - br
            for (loc, name) in sorted(added):
                notes.append(f"ADDED required param: {m.upper()} {p} [{loc}:{name}]")

    # New paths (non-breaking, informational)
    new_paths = sorted(set(cpaths.keys()) - set(bpaths.keys()))
    for p in new_paths:
        notes.append(f"NEW path: {p}")

    if problems:
        print("❌ Breaking changes detected:")
        for x in problems:
            print(" -", x)
        if notes:
            print("\nℹ️  Non-breaking changes:")
            for n in notes:
                print(" -", n)
        sys.exit(2)
    else:
        print("✅ No breaking changes detected.")
        if notes:
            print("\nℹ️  Non-breaking changes:")
            for n in notes:
                print(" -", n)
        sys.exit(0)


if __name__ == "__main__":
    main()
