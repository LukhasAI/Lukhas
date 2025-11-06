#!/usr/bin/env python3
"""LUKHAS Pre-Launch Audit - Phase 1: Baseline Metrics"""
import json
import os
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
AUDIT_DATA_DIR = ROOT_DIR / "audit_2025_launch" / "data"
AUDIT_DATA_DIR.mkdir(parents=True, exist_ok=True)

EXCLUDE_PATTERNS = ["__pycache__", ".pytest_cache", ".venv", "venv", "dist", "build", "node_modules", ".git"]

def should_exclude(path):
    return any(pattern in str(path) for pattern in EXCLUDE_PATTERNS)

def count_files_by_extension():
    counts, sizes = defaultdict(int), defaultdict(int)
    for file_path in ROOT_DIR.rglob("*"):
        if file_path.is_file() and not should_exclude(file_path):
            ext = file_path.suffix or "no_extension"
            counts[ext] += 1
            try: sizes[ext] += file_path.stat().st_size
            except: pass
    return dict(counts), dict(sizes)

def count_by_directory():
    directories = ["docs", "tests", "config", "utils", "branding", "scripts", "tools", "mcp-servers", "lukhas", "candidate", "matriz", "core"]
    dir_stats = {}
    for dir_name in directories:
        dir_path = ROOT_DIR / dir_name
        if dir_path.exists():
            file_count = sum(1 for _ in dir_path.rglob("*") if _.is_file() and not should_exclude(_))
            try: size_bytes = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file() and not should_exclude(f))
            except: size_bytes = 0
            dir_stats[dir_name] = {"file_count": file_count, "size_mb": round(size_bytes / (1024 * 1024), 2)}
    return dir_stats

print("=" * 80)
print("LUKHAS PRE-LAUNCH AUDIT - PHASE 1: BASELINE METRICS")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}\n")

ext_counts, ext_sizes = count_files_by_extension()
dir_stats = count_by_directory()

baseline_report = {
    "timestamp": datetime.now().isoformat(),
    "directory_stats": dir_stats,
    "extension_stats": {"counts": dict(sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:20])}
}

output_file = AUDIT_DATA_DIR / "baseline_metrics.json"
with open(output_file, 'w') as f:
    json.dump(baseline_report, indent=2, fp=f)

print(f"✓ Baseline metrics saved to: {output_file}")
print("=" * 80)
