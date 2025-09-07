from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import streamlit as st

from .graph_compiler import compile_graph


def _file_sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    h.update(path.read_bytes())
    return "sha256:" + h.hexdigest()


def compile_dir(in_dir: Path, out_dir: Path) -> tuple[int, list[str]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    violations_accum: list[str] = []
    processed = 0
    for p in sorted(in_dir.glob("*.json")):
        author = json.loads(p.read_text())
        inputs = [(str(p), _file_sha256(p))]
        plan, report = compile_graph(author, inputs=inputs)
        target = out_dir / p.stem
        target.mkdir(parents=True, exist_ok=True)
        (target / "runtime_plan.json").write_text(json.dumps(plan, indent=2))
        (target / "validation_report.json").write_text(json.dumps(report, indent=2))
        if not report.get("ok"):
            violations_accum.extend([f"{p.name}: {v}" for v in report.get("violations", [])])
        processed += 1
    return processed, violations_accum


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compile all MATRIZ graphs in a directory")
    ap.add_argument("in_dir", help="Input directory with *.json graphs")
    ap.add_argument("out_dir", help="Output directory for compiled plans")
    args = ap.parse_args(argv)

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    if not in_dir.exists():
        ap.error(f"input dir not found: {in_dir}")
    count, violations = compile_dir(in_dir, out_dir)
    print(f"Compiled {count} graph(s) to {out_dir}")
    if violations:
        print("Violations:\n" + "\n".join(violations))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
