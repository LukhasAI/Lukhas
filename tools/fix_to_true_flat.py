#!/usr/bin/env python3
"""
Fix promotion plan to true flat-root (core/ not Lukhas/core/)
"""

import json
import pathlib

PLAN_PATH = pathlib.Path("artifacts/promotion_batch.plan.jsonl")

def main():
    lines = PLAN_PATH.read_text().splitlines()
    out = []
    for line in lines:
        if not line.strip():
            continue
        row = json.loads(line)
        # Fix target from Lukhas/core/... to core/...
        target = row["target"]
        if target.startswith("Lukhas/"):
            target = target[7:]  # Remove "Lukhas/" prefix
        row["target"] = target
        out.append(row)

    PLAN_PATH.write_text("\n".join(json.dumps(r) for r in out) + "\n")
    print(f"Fixed {len(out)} targets to true flat-root")

if __name__ == "__main__":
    main()
