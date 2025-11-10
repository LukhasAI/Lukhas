"""
Normalize PyTest JUnit XML into NDJSON events for Memory Healix.
Usage:
  python tools/normalize_junit.py --in reports/junit.xml --out reports/events.ndjson
"""
from __future__ import annotations
import argparse, json, xml.etree.ElementTree as ET
from datetime import datetime

def _coerce_short(s: str | None, n: int = 512) -> str:
    return (s or "")[:n]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", default="reports/junit.xml")
    p.add_argument("--out", dest="out", default="reports/events.ndjson")
    p.add_argument("--suite", default="unit")
    p.add_argument("--commit", default="")
    p.add_argument("--branch", default="")
    args = p.parse_args()

    root = ET.parse(args.inp).getroot()
    with open(args.out, "w", encoding="utf-8") as w:
        for tc in root.iter("testcase"):
            fail = next(iter(tc.iter("failure")), None)
            err = next(iter(tc.iter("error")), None)
            node = fail or err
            if not node:
                continue
            evt = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "suite": args.suite,
                "test_id": f"{tc.get('classname')}::{tc.get('name')}",
                "file": _coerce_short(tc.get("file")),
                "time": tc.get("time"),
                "error_class": _coerce_short(node.get("type") or "Failure"),
                "message": _coerce_short(node.get("message")),
                "stack": _coerce_short(node.text, 4000),
                "repro_cmd": f"pytest -q {tc.get('file') or ''}::{tc.get('name')}",
                "commit": args.commit,
                "branch": args.branch,
            }
            w.write(json.dumps(evt, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
