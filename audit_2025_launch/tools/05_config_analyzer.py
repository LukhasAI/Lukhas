#!/usr/bin/env python3
import json
import re
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
AUDIT_REPORTS_DIR = ROOT_DIR / "audit_2025_launch" / "reports"
EXCLUDE = ["__pycache__", ".venv", ".git", "node_modules"]

def should_exclude(p): return any(x in str(p) for x in EXCLUDE)

print("=" * 80)
print("LUKHAS PRE-LAUNCH AUDIT - PHASE 5: CONFIGURATION ANALYSIS")
print("=" * 80)

configs = []
for ext in [".json", ".yaml", ".yml", ".toml", ".ini", ".env"]:
    for cf in ROOT_DIR.rglob(f"*{ext}"):
        if cf.is_file() and not should_exclude(cf):
            configs.append({"path": str(cf.relative_to(ROOT_DIR)), "type": ext[1:], "size": cf.stat().st_size})

env_vars = set()
for py_file in list(ROOT_DIR.rglob("*.py"))[:500]:
    if should_exclude(py_file): continue
    try:
        with open(py_file, encoding='utf-8', errors='ignore') as f:
            for match in re.finditer(r'os\.getenv\(["\']([^"\']+)["\']', f.read()):
                env_vars.add(match.group(1))
    except: pass

report = {"timestamp": datetime.now().isoformat(), "summary": {"total_configs": len(configs), "env_vars_python": len(env_vars)}, "config_files": configs[:100], "environment_variables": {"used_in_python": sorted(list(env_vars))[:50]}}

with open(AUDIT_REPORTS_DIR / "config_inventory.json", "w") as f: json.dump(report, f, indent=2)
print(f"✓ Found {len(configs)} config files, {len(env_vars)} env vars")
print("=" * 80)
