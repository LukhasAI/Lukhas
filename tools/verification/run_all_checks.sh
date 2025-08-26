#!/usr/bin/env bash
set -euo pipefail

SHA="${GITHUB_SHA:-$(git rev-parse HEAD)}"
ART="verification_artifacts/${SHA}"
mkdir -p "${ART}/system_status" "${ART}/test_results" "${ART}/implementation_evidence"

echo "Commit SHA: ${SHA}" | tee "${ART}/build_info.txt"

echo "== Acceptance gate =="
python3 tools/acceptance_gate.py | tee "${ART}/test_results/acceptance_gate.txt"

echo "== Import-linter =="
if ! command -v lint-imports >/dev/null 2>&1; then
  python3 -m pip install -q import-linter
fi
python3 -m import_linter || true | tee "${ART}/test_results/import_linter.txt"

echo "== E2E dry-run tests =="
python3 -m pytest tests/test_e2e_dryrun.py -q --maxfail=1 \
  | tee "${ART}/test_results/pytest_e2e_dryrun.txt"

echo "== Module inventory (accepted only) =="
python3 - <<'PY' | tee "${ART}/system_status/module_inventory.txt"
import os
root="lukhas"
py=0; dirs=0
for d,sub,files in os.walk(root):
    dirs += 1
    py += sum(1 for f in files if f.endswith(".py"))
print(f"accepted package: {root}")
print(f"python_files: {py}")
print(f"dirs: {dirs}")
PY

# Summarize
python3 - <<'PY' | tee "${ART}/system_status/summary.md"
import os, re, json
sha=os.environ.get("GITHUB_SHA", os.popen("git rev-parse HEAD").read().strip())
try:
    gate=open(f"verification_artifacts/{sha}/test_results/acceptance_gate.txt").read()
    gate_ok=("✅" in gate) and ("❌" not in gate)
except:
    gate_ok=False
print("# Phase 1 Verification Summary")
print(f"- Commit: `{sha}`")
print(f"- Acceptance gate: {'✅ PASS' if gate_ok else '❌ FAIL'}")
print("- Dry-run tests: see test_results/pytest_e2e_dryrun.txt")
print("- Import-linter: see test_results/import_linter.txt")
PY

echo "Artifacts written to: ${ART}"
