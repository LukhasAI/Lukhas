#!/usr/bin/env python3
"""
verify_perf.py

Reads pytest JUnit XML produced by CI and enforces wall-clock budgets.
Currently verifies the unit contracts suite total time against tests/perf/perf_budgets.json.

Usage (CI):
  pytest -m "not prod_only" --maxfail=1 -q --junitxml=reports/junit-unit.xml
  python tools/verify_perf.py
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BUDGETS = Path("tests/perf/perf_budgets.json")
JUNIT = Path("reports/junit-unit.xml")


def _sum_junit_seconds(junit_path: Path) -> float:
    if not junit_path.exists():
        print(f"❌ Missing JUnit report: {junit_path}")
        sys.exit(2)
    tree = ET.parse(junit_path)
    root = tree.getroot()
    total = 0.0
    for tc in root.iter("testcase"):
        t = tc.get("time")
        if t is not None:
            try:
                total += float(t)
            except ValueError:
                pass
    return total


def main() -> int:
    if not BUDGETS.exists():
        print(f"❌ Missing budgets file: {BUDGETS}")
        return 2
    budgets = json.loads(BUDGETS.read_text())
    unit_budget = float(budgets["budget_seconds"]["unit_contracts_total"])
    total = _sum_junit_seconds(JUNIT)
    threshold_mult = float(budgets.get("threshold_multiplier", 1.0))
    effective_budget = unit_budget * threshold_mult
    if total > effective_budget:
        print(
            f"❌ Performance budget exceeded: unit_contracts_total {total:.2f}s > {effective_budget:.2f}s "
            f"(budget {unit_budget:.2f}s × {threshold_mult:g})"
        )
        return 1
    print(f"✅ Performance budgets within limits: unit_contracts_total {total:.2f}s ≤ {effective_budget:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
