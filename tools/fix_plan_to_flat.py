#!/usr/bin/env python3
"""
Rewrite artifacts/promotion_batch.plan.jsonl targets to flat layout:
  Lukhas/<module>/<relpath>

- Computes module and relpath from 'source' if missing
- Preserves all other fields untouched
- Idempotent: running again yields same output
"""

import json
import pathlib
import re
import sys

PLAN_PATH = pathlib.Path("artifacts/promotion_batch.plan.jsonl")


def split_source(source: str):
    parts = re.split(r"[\\/]", source)
    if len(parts) < 2:
        return None, None, ""
    lane = parts[0]
    module = parts[1]
    rel = "/".join(parts[2:]) if len(parts) > 2 else ""
    return lane, module, rel


def to_flat_target(module: str, relpath: str, root="Lukhas"):
    base = f"{root.rstrip('/')}/{module}"
    return f"{base}/{relpath}" if relpath else f"{base}/"


def main():
    if not PLAN_PATH.exists():
        print("ERROR: plan not found:", PLAN_PATH, file=sys.stderr)
        sys.exit(1)

    lines = PLAN_PATH.read_text().splitlines()
    out = []
    for line in lines:
        if not line.strip():
            continue
        row = json.loads(line)
        lane, mod_src, rel_src = split_source(row["source"])
        module = row.get("module") or mod_src or "unknown"
        relpath = row.get("relpath") or rel_src or ""
        row["module"] = module
        row["relpath"] = relpath
        row["target"] = to_flat_target(module, relpath, root="Lukhas")
        out.append(row)

    PLAN_PATH.write_text("\n".join(json.dumps(r) for r in out) + "\n")
    print("Rewrote targets to flat layout in", PLAN_PATH)


if __name__ == "__main__":
    main()
