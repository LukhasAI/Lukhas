#!/usr/bin/env python3
"""
CI gate to ratchet down legacy lukhas.* import usage.
Fails build if:
  - Current alias hits exceed sprint budget
  - Current alias hits exceed baseline + allowed delta (prevents regressions)

Environment variables:
  - LUKHAS_IMPORT_BUDGET: Max allowed alias hits (default: 999999)
  - LUKHAS_IMPORT_MAX_DELTA: Max increase from baseline (default: 0)
  - UPDATE_BASELINE: Set to "1" to update baseline after passing checks
"""
import os
import json
from pathlib import Path

LEDGER = Path("artifacts/lukhas_import_ledger.ndjson")
BUDGET = int(os.getenv("LUKHAS_IMPORT_BUDGET", "999999"))
BASELINE_FILE = Path("artifacts/legacy_import_baseline.json")

def count_aliases():
    if not LEDGER.exists():
        return 0
    n = 0
    for line in LEDGER.read_text().splitlines():
        if not line.strip():
            continue
        try:
            if json.loads(line).get("event") == "alias":
                n += 1
        except Exception:
            pass
    return n

def main():
    current = count_aliases()
    baseline = 0
    if BASELINE_FILE.exists():
        try:
            baseline = json.loads(BASELINE_FILE.read_text()).get("alias_hits", 0)
        except Exception:
            pass

    # Do not allow regression beyond budget or baseline+delta
    delta = int(os.getenv("LUKHAS_IMPORT_MAX_DELTA", "0"))

    print(f"alias_hits: current={current}, baseline={baseline}, budget={BUDGET}, delta={delta}")

    if current > BUDGET:
        print("FAIL: over sprint budget")
        return 2
    if current > baseline + delta:
        print("FAIL: alias usage increased")
        return 3

    # Update baseline on main or when flag is set
    if os.getenv("UPDATE_BASELINE") == "1":
        BASELINE_FILE.write_text(json.dumps({"alias_hits": current}, indent=2))
        print("Updated baseline.")

    print("PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
