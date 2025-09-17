#!/usr/bin/env python3
import json
import sys
import pathlib

paths = [
    pathlib.Path("reports/unit.json"),
    pathlib.Path("reports/capabilities.json"),
    pathlib.Path("reports/e2e.json")
]

total_reruns = 0
for p in paths:
    if not p.exists():
        continue
    data = json.loads(p.read_text())
    # pytest-json-report exposes reruns per test under 'tests' entries where 'outcome' may be 'rerun'
    reruns = sum(1 for t in data.get("tests", []) if t.get("outcome") == "rerun")
    total_reruns += reruns

if total_reruns > 0:
    print(f"❌ Flake radar: {total_reruns} test(s) required rerun(s). Failing the build.")
    sys.exit(1)

print("✅ No reruns detected across suites.")