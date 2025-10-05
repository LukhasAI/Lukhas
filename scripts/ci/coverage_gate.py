#!/usr/bin/env python3
"""T4/0.01% Coverage Gate
Enforces per-module coverage targets with lane-based defaults.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Lane-based default coverage targets
LANE_DEFAULTS = {"L0": 70, "L1": 75, "L2": 80, "L3": 85, "L4": 90, "L5": 90}


def lane_of(tags: list[str]) -> str:
    """Extract lane from tags."""
    for t in tags or []:
        if t.startswith("lane:"):
            return t.split(":")[1]
    return "L2"


def main():
    root = Path(".")
    bad = []

    for mf in root.rglob("module.manifest.json"):
        try:
            d = json.loads(mf.read_text())
        except Exception as e:
            print(f"⚠️  Failed to parse {mf}: {e}")
            continue

        name = d.get("module", mf.parent.name)
        tags = d.get("tags", [])
        lane = lane_of(tags)
        testing = d.get("testing") or {}
        target = testing.get("coverage_target", LANE_DEFAULTS.get(lane, 80))
        observed = testing.get("coverage_observed")

        if observed is None:
            # Allow missing if no tests dir
            if (mf.parent / "tests").exists():
                bad.append((name, f"missing coverage_observed (target {target}%)"))
            continue

        if observed < target:
            bad.append((name, f"{observed}% < target {target}% (lane {lane})"))

    if bad:
        print(f"❌ Coverage gate failed ({len(bad)} violations):")
        for name, msg in sorted(bad):
            print(f"  {name}: {msg}")
        sys.exit(1)

    print("✅ Coverage gate OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
