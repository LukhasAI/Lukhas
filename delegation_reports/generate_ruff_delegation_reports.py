#!/usr/bin/env python3
from datetime import datetime, timezone
"""Generate delegation-ready reports from Ruff JSON output.

Produces three files in the repo root:
- ruff-master-report.json  -> per-file list of issues with small suggestions
- ruff-by-code.json       -> per-rule grouping with counts, examples, top files
- ruff-summary.json       -> total counts and top-level summary

This script is safe to run repeatedly.
"""

import json
import os
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
INPUT = os.path.join(ROOT, "ruff-all-errors.json")
OUT_MASTER = os.path.join(ROOT, "ruff-master-report.json")
OUT_BY_CODE = os.path.join(ROOT, "ruff-by-code.json")
OUT_SUMMARY = os.path.join(ROOT, "ruff-summary.json")


def short_suggestion(code: str) -> str:
    # Lightweight mapping of ruff codes to low-risk suggested actions
    if code.startswith("DTZ"):
        return "Make datetime timezone-aware (use timezone.utc or pass tzinfo)."
    if code in ("ARG001", "ARG002"):
        return "Mark unused args with a leading underscore or reference them (_ = arg)."
    if code == "E501":
        return "Reflow long line (run Black/auto-format or wrap string)."
    if code.startswith("PERF"):
        return "Consider a micro-optimisation (list comprehension, extend, move try outside loop)."
    if code.startswith("F8") or code == "F821":
        return "Fix undefined name or import; inspect the referenced symbol."
    if code.startswith("B9") or code == "B904":
        return "Prefer `raise ... from err` inside except clauses to preserve context."
    return "Review and apply standard remediation for this rule."


def main():
    if not os.path.exists(INPUT):
        print(f"Input not found: {INPUT}")
        return 1

    print(f"Reading {INPUT} ...")
    with open(INPUT, encoding="utf-8") as fh:
        data = json.load(fh)

    total = len(data)
    per_file = defaultdict(list)
    per_code = defaultdict(list)

    for item in data:
        filename = item.get("filename") or "<unknown>"
        code = item.get("code") or "<NO_CODE>"
        row = item.get("location", {}).get("row")
        col = item.get("location", {}).get("column")
        end_row = item.get("end_location", {}).get("row")
        end_col = item.get("end_location", {}).get("column")
        message = item.get("message")
        url = item.get("url")

        record = {
            "code": code,
            "message": message,
            "row": row,
            "col": col,
            "end_row": end_row,
            "end_col": end_col,
            "url": url,
            "suggestion": short_suggestion(code),
        }

        per_file[filename].append(record)
        per_code[code].append({"filename": filename, "row": row, "col": col, "message": message})

    # Build master report
    master = {}
    file_counts = []
    for fn, issues in per_file.items():
        master[fn] = {
            "count": len(issues),
            "issues": issues,
        }
        file_counts.append((fn, len(issues)))

    file_counts.sort(key=lambda x: x[1], reverse=True)

    # Build by-code report
    by_code = {}
    code_counts = []
    for code, occ in per_code.items():
        counter = Counter([o["filename"] for o in occ])
        top_files = counter.most_common(5)
        examples = occ[:3]
        by_code[code] = {
            "count": len(occ),
            "top_files": top_files,
            "examples": examples,
            "suggestion": short_suggestion(code),
        }
        code_counts.append((code, len(occ)))

    code_counts.sort(key=lambda x: x[1], reverse=True)

    summary = {
        "total_violations": total,
        "total_files": len(per_file),
        "top_files": file_counts[:20],
        "top_codes": code_counts[:50],
    }

    print(f"Writing master report -> {OUT_MASTER}")
    with open(OUT_MASTER, "w", encoding="utf-8") as fh:
        json.dump(master, fh, indent=2, sort_keys=True)

    print(f"Writing by-code report -> {OUT_BY_CODE}")
    with open(OUT_BY_CODE, "w", encoding="utf-8") as fh:
        json.dump(by_code, fh, indent=2, sort_keys=True)

    print(f"Writing summary -> {OUT_SUMMARY}")
    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)

    print("Done.\nSummary:\n", json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())