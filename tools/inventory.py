#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
LANES = {
    "accepted": ROOT / "lukhas",
    "labs": ROOT / "labs",
    "quarantine": ROOT / "quarantine",
    "archive": ROOT / "archive",
}


def list_py(d):
    return list(d.rglob("*.py")) if d.exists() else []


def has_init(p):
    return (p / "__init__.py").exists()


def count_lines(files):
    tot = 0
    for f in files:
        try:
            with f.open("r", encoding="utf-8", errors="ignore") as fh:
                tot += sum(1 for _ in fh)
        except Exception:
            pass
    return tot


def accepted_illegal_imports(files):
    bad, pat = [], re.compile(r"^\s*(?:from|import)\s+(candidate|quarantine|archive)\b")
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            if pat.search(line):
                bad.append({"file": str(f.relative_to(ROOT)), "line": i, "text": line.strip()})
    return bad


report = {}
for lane, path in LANES.items():
    files = list_py(path)
    report[lane] = {
        "exists": path.exists(),
        "is_package": has_init(path) if path.exists() else False,
        "files": len(files),
        "loc": count_lines(files),
        "examples": [str(p.relative_to(ROOT)) for p in files[:12]],
    }
accepted_files = list_py(LANES["accepted"]) if LANES["accepted"].exists() else []
illegal = accepted_illegal_imports(accepted_files)
out = {
    "root": str(ROOT),
    "lanes": report,
    "accepted_illegal_imports": illegal,
    "summary": {k: report.get(k, {}).get("files", 0) for k in LANES},
}
print(json.dumps(out, indent=2))