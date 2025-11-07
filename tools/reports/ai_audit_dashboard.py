#!/usr/bin/env python3
"""
AI Audit Dashboard Generator
Reads evidence_ledger.csv and writes a Markdown summary with key metrics.

Defaults:
- Input CSV: reports/audit/merged/evidence_ledger.csv
- Output MD: reports/dashboard/ai_audit_summary.md

Environment overrides:
- LUKHAS_EVIDENCE_LEDGER_PATH
- LUKHAS_AUDIT_DASHBOARD_PATH
"""
from __future__ import annotations

import csv
import os
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import List, Tuple

DEFAULT_INPUT = Path("reports/audit/merged/evidence_ledger.csv")
DEFAULT_OUTPUT = Path("reports/dashboard/ai_audit_summary.md")


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    idx = int(0.95 * len(s)) - 1
    idx = max(0, min(idx, len(s) - 1))
    return float(s[idx])


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            out.append(row)
    return out


def top_counts(rows: list[dict], key: str, n: int = 5) -> list[tuple[str, int]]:
    c = Counter(row.get(key, "") for row in rows)
    return c.most_common(n)


def generate_dashboard(input_csv: Path = DEFAULT_INPUT, out_md: Path = DEFAULT_OUTPUT) -> int:
    rows = load_rows(input_csv)
    os.makedirs(out_md.parent, exist_ok=True)

    total = len(rows)
    succ = sum(1 for r in rows if str(r.get("success", "")).lower() in ("true", "1", "yes"))
    fail = total - succ
    latencies = [float(r.get("latency_ms", 0.0) or 0.0) for r in rows]
    avg_latency = mean(latencies) if latencies else 0.0
    p95_latency = p95(latencies)

    by_component = top_counts(rows, "component")
    by_task = top_counts(rows, "task_type")

    lines = [
        "# AI Interface Audit Summary",
        "",
        f"Total Events: {total}",
        f"Success: {succ}",
        f"Failure: {fail}",
        f"Success Rate: { (succ / total * 100.0) if total else 0.0:.2f}%",
        "",
        "## Latency",
        f"- Average: {avg_latency:.2f} ms",
        f"- P95: {p95_latency:.2f} ms",
        "",
        "## Top Components",
    ]
    for comp, cnt in by_component:
        lines.append(f"- {comp or '(none)'}: {cnt}")
    lines.append("")
    lines.append("## Top Task Types")
    for task, cnt in by_task:
        lines.append(f"- {task or '(none)'}: {cnt}")

    out_md.write_text("\n".join(lines))
    return total


def main() -> None:
    in_path = Path(os.getenv("LUKHAS_EVIDENCE_LEDGER_PATH") or DEFAULT_INPUT)
    out_path = Path(os.getenv("LUKHAS_AUDIT_DASHBOARD_PATH") or DEFAULT_OUTPUT)
    total = generate_dashboard(in_path, out_path)
    print(f"Wrote dashboard for {total} events to {out_path}")


if __name__ == "__main__":
    main()
