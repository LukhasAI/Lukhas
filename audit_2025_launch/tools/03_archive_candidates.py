#!/usr/bin/env python3
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
AUDIT_REPORTS_DIR = ROOT_DIR / "audit_2025_launch" / "reports"
EXCLUDE = ["__pycache__", ".venv", ".git", "node_modules", "archive"]

def should_exclude(p):
    return any(x in str(p) for x in EXCLUDE)

print("=" * 80)
print("LUKHAS PRE-LAUNCH AUDIT - PHASE 3: ARCHIVE CANDIDATES")
print("=" * 80)

candidates = []
cutoff = datetime.now() - timedelta(days=180)

for py_file in ROOT_DIR.rglob("*.py"):
    if should_exclude(py_file):
        continue
    mtime = datetime.fromtimestamp(py_file.stat().st_mtime)
    if mtime < cutoff:
        try:
            with open(py_file, encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if any(m in content for m in ["# DEPRECATED", "# Legacy", "TODO: remove"]):
                    candidates.append({"path": str(py_file.relative_to(ROOT_DIR)), "reason": "deprecated_marker", "confidence": 80})
                elif (datetime.now() - mtime).days > 365:
                    candidates.append({"path": str(py_file.relative_to(ROOT_DIR)), "reason": "stale_file", "confidence": 60})
        except OSError:
            pass

report = {"timestamp": datetime.now().isoformat(), "summary": {"total_candidates": len(candidates), "high_confidence": len([c for c in candidates if c["confidence"] >= 70])}, "candidates": candidates[:100]}

with open(AUDIT_REPORTS_DIR / "archive_candidates.json", "w") as f: json.dump(report, f, indent=2)
print(f"✓ Found {len(candidates)} archive candidates ({report['summary']['high_confidence']} high-confidence)")
print("=" * 80)
