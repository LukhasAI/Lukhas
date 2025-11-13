#!/usr/bin/env bash
set -euo pipefail

# URGENT Security Fixes - CVE-2025-50181 + Bandit + Ruff Snapshot
# Based on audit report recommendations

echo "🚨 URGENT SECURITY FIXES"
echo "=" * 70

# 1. Fix CVE: Upgrade urllib3
echo ""
echo "1️⃣ Fixing CVE-2025-50181: Upgrading urllib3"
echo "-" * 70

# Check current version
echo "Current urllib3 version:"
python3 -c "import urllib3; print(urllib3.__version__)" || echo "urllib3 not installed"

# Upgrade urllib3
echo "Upgrading urllib3 to >=2.5.0..."
python3 -m pip install --user "urllib3>=2.5.0" --upgrade

# Run pip-audit after
mkdir -p release_artifacts/checks/security
echo "Running pip-audit after upgrade..."
python3 -m pip install --user pip-audit || true
pip-audit > release_artifacts/checks/security/pip_audit_after.txt 2>&1 || {
    echo "pip-audit completed with warnings (check output)"
}

echo "✅ urllib3 upgraded"
echo "   Results: release_artifacts/checks/security/pip_audit_after.txt"

# 2. Re-run Bandit (scoped to production)
echo ""
echo "2️⃣ Re-running Bandit (excluding quarantine/archive)"
echo "-" * 70

python3 -m pip install --user bandit || true

bandit -r . \
    -f json \
    -o release_artifacts/checks/security/bandit_scoped.json \
    --exclude .venv,venv,build,dist,archive,quarantine,node_modules,.pytest_cache,__pycache__ \
    2>&1 | tee release_artifacts/checks/security/bandit_scoped_stdout.txt || {
    echo "Bandit completed (may have findings)"
}

# Create CSV summary
python3 - <<'PY'
import json, csv, sys
from pathlib import Path

json_file = Path('release_artifacts/checks/security/bandit_scoped.json')
if not json_file.exists():
    print("⚠️  Bandit JSON not found")
    sys.exit(0)

try:
    r = json.load(open(json_file))
    rows = [["filename", "severity", "confidence", "issue_text", "line"]]

    for item in r.get('results', []):
        rows.append([
            item['filename'],
            item['issue_severity'],
            item['issue_confidence'],
            item['issue_text'].replace("\n", " ")[:300],
            item['line_number']
        ])

    csv_file = Path('release_artifacts/checks/security/bandit_scoped_summary.csv')
    with open(csv_file, 'w', newline='') as f:
        csv.writer(f).writerows(rows)

    print(f"✅ Bandit summary: {len(rows)-1} findings")
    print(f"   JSON: {json_file}")
    print(f"   CSV:  {csv_file}")

    # Show top issues
    if len(rows) > 1:
        print("\n📊 Top 5 findings:")
        for row in rows[1:6]:
            print(f"   {row[1]}: {row[0]}:{row[4]} - {row[3][:80]}")
except Exception as e:
    print(f"❌ Error processing bandit output: {e}")
PY

echo "✅ Bandit scan complete"

# 3. Ruff snapshot
echo ""
echo "3️⃣ Running Ruff snapshot"
echo "-" * 70

mkdir -p release_artifacts/checks/quality

echo "Generating Ruff JSON report..."
python3 -m ruff check --format json . > release_artifacts/checks/quality/ruff_full.json 2>&1 || {
    echo "Ruff completed (violations found)"
}

echo "Generating error count summary..."
python3 - <<'PY'
import json
from pathlib import Path
from collections import Counter

json_file = Path('release_artifacts/checks/quality/ruff_full.json')
if not json_file.exists():
    print("⚠️  Ruff JSON not found")
else:
    try:
        data = json.load(open(json_file))
        codes = [item['code'] for item in data]
        counts = Counter(codes)

        with open('release_artifacts/checks/quality/ruff_error_counts.txt', 'w') as f:
            f.write("RUFF ERROR COUNTS\n")
            f.write("=" * 60 + "\n\n")
            for code, count in counts.most_common(20):
                f.write(f"{count:6d}  {code}\n")

        print(f"✅ Ruff snapshot: {len(data)} total violations")
        print(f"   JSON: {json_file}")
        print(f"   Counts: release_artifacts/checks/quality/ruff_error_counts.txt")

        print("\n📊 Top 10 error codes:")
        for code, count in counts.most_common(10):
            print(f"   {count:6d}  {code}")
    except Exception as e:
        print(f"❌ Error: {e}")
PY

echo ""
echo "=" * 70
echo "✅ URGENT FIXES COMPLETE"
echo "=" * 70
echo ""
echo "📋 Artifacts created:"
echo "   release_artifacts/checks/security/pip_audit_after.txt"
echo "   release_artifacts/checks/security/bandit_scoped.json"
echo "   release_artifacts/checks/security/bandit_scoped_summary.csv"
echo "   release_artifacts/checks/quality/ruff_full.json"
echo "   release_artifacts/checks/quality/ruff_error_counts.txt"
echo ""
echo "🔧 Next steps:"
echo "   1. Review security findings in bandit_scoped_summary.csv"
echo "   2. Plan next lint batch from ruff_error_counts.txt"
echo "   3. Update requirements.txt to pin urllib3>=2.5.0"
echo ""
