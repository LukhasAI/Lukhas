#!/usr/bin/env python3
"""
Append a single CSV row tracking F401 (unused import) counts.

Reads ruff JSON produced at reports/audit/f401.json (as emitted by the
F401 annotator or any `ruff --select F401 --output-format json` run),
then appends to reports/audit/f401_trends.csv with timestamp + git metadata.

Columns:
  timestamp_utc, commit, branch, core_f401, candidate_f401, other_f401, total_f401

- "core" aggregates lukhas/ and MATRIZ/
- "candidate" is candidate/
- "other" is everything else

Idempotent and tolerant: if the JSON is missing, exits non‑zero with a
clear message; creates the CSV with header if absent.
"""

from __future__ import annotations
import csv
import datetime as _dt
import json
import os
import subprocess
import sys
from typing import Any, Dict, List

SRC = "reports/audit/f401.json"
DST = "reports/audit/f401_trends.csv"


def _git(args: List[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True).strip()
    except Exception:
        return ""


def _prefix(path: str) -> str:
    p = path.replace("\\", "/")

    # Handle both absolute and relative paths
    if "/LOCAL-REPOS/Lukhas/" in p:
        # Convert absolute to relative path
        p = p.split("/LOCAL-REPOS/Lukhas/")[-1]

    if p.startswith("lukhas/") or p.startswith("MATRIZ/"):
        return "core"
    if p.startswith("candidate/"):
        return "candidate"
    return "other"


def main() -> int:
    if not os.path.exists(SRC):
        print(f"[f401_trend] missing {SRC}; run ruff with --select F401 first", file=sys.stderr)
        return 2

    try:
        with open(SRC, "r", encoding="utf-8") as f:
            data: List[Dict[str, Any]] = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[f401_trend] invalid JSON in {SRC}: {e}", file=sys.stderr)
        return 2

    totals = {"core": 0, "candidate": 0, "other": 0}
    for rec in data:
        # Only count actual F401 errors, not syntax errors
        if rec.get("code") != "F401":
            continue

        path = str(rec.get("filename", ""))
        bucket = _prefix(path)
        if bucket in totals:
            totals[bucket] += 1
        else:
            totals["other"] += 1

    total = sum(totals.values())
    now = _dt.datetime.utcnow().isoformat()
    commit = _git(["rev-parse", "--short", "HEAD"])
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])

    # Ensure directory exists
    os.makedirs(os.path.dirname(DST), exist_ok=True)

    # Write header if file doesn't exist
    if not os.path.exists(DST):
        with open(DST, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["timestamp_utc", "commit", "branch", "core_f401", "candidate_f401", "other_f401", "total_f401"]
            )

    # Append the row
    with open(DST, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([now, commit, branch, totals["core"], totals["candidate"], totals["other"], total])

    print(
        f"[f401_trend] appended trend: {total} F401 errors ({totals['core']} core, {totals['candidate']} candidate, {totals['other']} other)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
