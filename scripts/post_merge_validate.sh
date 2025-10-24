#!/usr/bin/env bash
# post_merge_validate.sh - Agent D final validation script
# Run all T4 gates post-merge and generate JSON report

set -euo pipefail

REPORT_DIR="tmp"
REPORT="$REPORT_DIR/post_merge_report.json"
mkdir -p "$REPORT_DIR"

echo "🔍 Running post-merge validation gates..."
echo ""

# Gate 1: NodeSpec validation
echo "Gate 1/4: NodeSpec schema validation..."
if make nodespec-validate >/dev/null 2>&1; then
  NODESPEC="PASS"
  echo "  ✅ NodeSpec validation passed"
else
  NODESPEC="FAIL"
  echo "  ❌ NodeSpec validation failed"
fi

# Gate 2: Unit tests
echo "Gate 2/4: Unit tests..."
if pytest -q --maxfail=5 >/dev/null 2>&1; then
  TESTS="PASS"
  echo "  ✅ Tests passed"
else
  TESTS="FAIL"
  echo "  ❌ Tests failed"
fi

# Gate 3: Registry smoke test
echo "Gate 3/4: Registry smoke test..."
if make registry-ci >/dev/null 2>&1; then
  REGISTRY_SMOKE="PASS"
  echo "  ✅ Registry smoke passed"
else
  REGISTRY_SMOKE="FAIL"
  echo "  ❌ Registry smoke failed"
fi

# Gate 4: PQC CI check
echo "Gate 4/4: PQC sign/verify check..."
if [ -f ".github/workflows/pqc-sign-verify.yml" ]; then
  PQC_CI="PASS"
  echo "  ✅ PQC CI workflow present"
else
  PQC_CI="FAIL"
  echo "  ❌ PQC CI workflow missing"
fi

# Generate JSON report
echo ""
echo "📊 Generating validation report..."
cat > "$REPORT" <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "gates": {
    "nodespec_validate": "$NODESPEC",
    "unit_tests": "$TESTS",
    "registry_smoke": "$REGISTRY_SMOKE",
    "pqc_ci_present": "$PQC_CI"
  },
  "overall_status": "$(if [ "$NODESPEC" = "PASS" ] && [ "$TESTS" = "PASS" ] && [ "$REGISTRY_SMOKE" = "PASS" ] && [ "$PQC_CI" = "PASS" ]; then echo "PASS"; else echo "FAIL"; fi)",
  "pr_sequence": ["TG-001", "TG-002", "TG-009"],
  "agent_chain": "A→B→C→D"
}
EOF

echo "✅ Report generated: $REPORT"
echo ""
cat "$REPORT"
echo ""

# Exit with appropriate code
if [ "$(jq -r '.overall_status' "$REPORT")" = "PASS" ]; then
  echo "🎉 All gates passed!"
  exit 0
else
  echo "⚠️  Some gates failed. Review report for details."
  exit 1
fi
