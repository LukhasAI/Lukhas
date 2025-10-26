#!/usr/bin/env python3
"""
AI Interface Audit Rollup
Reads JSONL events and appends normalized rows to evidence_ledger.csv.

Default input: reports/audit/merged/ai_interface_events.jsonl
Default output: reports/audit/merged/evidence_ledger.csv

Rows:
- timestamp_utc
- trace_id
- component
- task_type
- success
- latency_ms
- request_size
- prompt_hash
- output_len (if present)
"""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping

DEFAULT_INPUT = Path("reports/audit/merged/ai_interface_events.jsonl")
DEFAULT_OUTPUT = Path("reports/audit/merged/evidence_ledger.csv")


def normalize_event(rec: Mapping) -> dict:
    meta = rec if isinstance(rec, dict) else {}
    return {
        "timestamp_utc": meta.get("timestamp_utc") or datetime.now(timezone.utc).isoformat(),
        "trace_id": meta.get("trace_id", ""),
        "component": meta.get("component", ""),
        "task_type": meta.get("task_type", ""),
        "success": bool(meta.get("success", False)),
        "latency_ms": float(meta.get("latency_ms", 0.0)),
        "request_size": int(meta.get("request_size", 0)),
        "prompt_hash": meta.get("prompt_hash", ""),
        "output_len": int(meta.get("output_len", 0)),
    }


def load_events(path: Path) -> Iterable[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                yield rec
            except Exception:
                continue


def append_to_ledger(rows: Iterable[dict], out_path: Path) -> int:
    os.makedirs(out_path.parent, exist_ok=True)
    write_header = not out_path.exists() or out_path.stat().st_size == 0
    fieldnames = [
        "timestamp_utc",
        "trace_id",
        "component",
        "task_type",
        "success",
        "latency_ms",
        "request_size",
        "prompt_hash",
        "output_len",
    ]
    count = 0
    with out_path.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)
            count += 1
    return count


def rollup(input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT) -> int:
    events = (normalize_event(e) for e in load_events(input_path))
    return append_to_ledger(events, output_path)


def main() -> None:
    input_env = os.getenv("LUKHAS_AI_AUDIT_REPORT_PATH")
    output_env = os.getenv("LUKHAS_EVIDENCE_LEDGER_PATH")
    in_path = Path(input_env) if input_env else DEFAULT_INPUT
    out_path = Path(output_env) if output_env else DEFAULT_OUTPUT
    added = rollup(in_path, out_path)
    print(f"Appended {added} audit rows to {out_path}")


if __name__ == "__main__":
    main()
