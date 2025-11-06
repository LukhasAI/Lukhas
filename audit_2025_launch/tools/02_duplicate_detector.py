#!/usr/bin/env python3
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
AUDIT_REPORTS_DIR = ROOT_DIR / "audit_2025_launch" / "reports"
EXCLUDE = ["__pycache__", ".venv", ".git", "node_modules"]

def should_exclude(p): return any(x in str(p) for x in EXCLUDE)
def hash_file(fp):
    try:
        h = hashlib.sha256()
        with open(fp, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError): return None

print("=" * 80)
print("LUKHAS PRE-LAUNCH AUDIT - PHASE 2: DUPLICATE DETECTION")
print("=" * 80)

hash_map = defaultdict(list)
for fp in ROOT_DIR.rglob("*"):
    if fp.is_file() and not should_exclude(fp) and fp.suffix in [".py", ".md", ".json"]:
        fh = hash_file(fp)
        if fh: hash_map[fh].append({"path": str(fp.relative_to(ROOT_DIR)), "size": fp.stat().st_size})

duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
total_wasted = sum(sum(f["size"] for f in files[1:]) for files in duplicates.values())

report = {"timestamp": datetime.now().isoformat(), "summary": {"total_duplicate_groups": len(duplicates), "total_wasted_space_mb": round(total_wasted/(1024*1024), 2)}, "duplicates": list(duplicates.values())[:50]}

with open(AUDIT_REPORTS_DIR / "duplicate_files.json", "w") as f: json.dump(report, f, indent=2)
print(f"✓ Found {len(duplicates)} duplicate groups, {report['summary']['total_wasted_space_mb']} MB wasted")
print("=" * 80)
