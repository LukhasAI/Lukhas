#!/bin/bash
# T4/0.01% Excellence Standalone Reproduction Entry Point
# For external auditors to independently verify LUKHAS AI performance claims

set -e

echo "🔬 LUKHAS AI T4/0.01% Excellence - Independent Reproduction"
echo "=========================================================="
echo ""
echo "This container provides independent verification of LUKHAS AI"
echo "performance claims according to T4/0.01% excellence standards."
echo ""

# Generate unique reproduction ID
REPRODUCTION_ID="repro_$(date +%Y%m%d_%H%M%S)_$$"
export AUDIT_RUN_ID="$REPRODUCTION_ID"

echo "Reproduction ID: $REPRODUCTION_ID"
echo "Container Version: $(cat /etc/debian_version 2>/dev/null || echo 'Unknown')"
echo "Python Version: $(python3 --version)"
echo ""

# Set reproducibility environment
export PYTHONHASHSEED=0
export LUKHAS_MODE=release
export PYTHONDONTWRITEBYTECODE=1

# Create output directory
mkdir -p /output

echo "📊 Starting Independent Reproduction Process"
echo "============================================"
echo ""

# Phase 1: Environment Validation
echo "🔍 Phase 1: Environment Validation"
echo "----------------------------------"

echo "Validating reproducibility environment..."

if [[ "$PYTHONHASHSEED" != "0" ]]; then
    echo "❌ Error: PYTHONHASHSEED not set to 0"
    exit 1
fi

if [[ "$LUKHAS_MODE" != "release" ]]; then
    echo "❌ Error: LUKHAS_MODE not set to release"
    exit 1
fi

echo "✅ Environment validation passed"
echo ""

# Phase 2: Baseline Reproduction
echo "📈 Phase 2: Baseline Performance Reproduction"
echo "--------------------------------------------"

echo "Running baseline performance measurements..."

python3 scripts/audit_baseline.py \
    --environment reproduction \
    --samples 1000 \
    --output "/output/reproduction_baseline_${REPRODUCTION_ID}.json"

if [[ ! -f "/output/reproduction_baseline_${REPRODUCTION_ID}.json" ]]; then
    echo "❌ Error: Baseline reproduction failed"
    exit 1
fi

echo "✅ Baseline reproduction complete"
echo ""

# Phase 3: Multiple Runs for Consistency
echo "🔄 Phase 3: Consistency Validation"
echo "----------------------------------"

echo "Running multiple measurements for consistency validation..."

CONSISTENCY_RUNS=3
CONSISTENCY_FILES=()

for i in $(seq 1 $CONSISTENCY_RUNS); do
    echo "Running consistency test $i/$CONSISTENCY_RUNS..."

    CONSISTENCY_FILE="/output/consistency_${i}_${REPRODUCTION_ID}.json"

    python3 scripts/audit_baseline.py \
        --environment "reproduction_${i}" \
        --samples 500 \
        --output "$CONSISTENCY_FILE"

    if [[ -f "$CONSISTENCY_FILE" ]]; then
        CONSISTENCY_FILES+=("$CONSISTENCY_FILE")
    fi
done

if [[ ${#CONSISTENCY_FILES[@]} -ge 2 ]]; then
    python3 scripts/reproducibility_analysis.py \
        --data "${CONSISTENCY_FILES[@]}" \
        --output "/output/consistency_analysis_${REPRODUCTION_ID}.json" \
        --report "/output/consistency_report_${REPRODUCTION_ID}.md" \
        --target-reproducibility 0.80

    echo "✅ Consistency validation complete"
else
    echo "⚠️  Warning: Insufficient consistency data"
fi

echo ""

# Phase 4: Performance Claims Verification
echo "🎯 Phase 4: Performance Claims Verification"
echo "------------------------------------------"

BASELINE_FILE="/output/reproduction_baseline_${REPRODUCTION_ID}.json"

if [[ -f "$BASELINE_FILE" ]] && command -v jq &> /dev/null; then
    echo "Verifying performance against T4/0.01% claims..."

    # Extract key metrics
    GUARDIAN_P95=$(jq -r '.guardian_stats.p95' "$BASELINE_FILE" 2>/dev/null || echo "N/A")
    MEMORY_P95=$(jq -r '.memory_stats.p95' "$BASELINE_FILE" 2>/dev/null || echo "N/A")
    ORCHESTRATOR_P95=$(jq -r '.orchestrator_stats.p95' "$BASELINE_FILE" 2>/dev/null || echo "N/A")
    CREATIVITY_P95=$(jq -r '.creativity_stats.p95' "$BASELINE_FILE" 2>/dev/null || echo "N/A")

    echo ""
    echo "📊 Reproduction Results vs. T4/0.01% Claims:"
    echo ""

    # Guardian validation (target: ~168μs, tolerance: ±25%)
    echo "Guardian E2E Performance:"
    echo "  Measured p95: ${GUARDIAN_P95}μs"
    echo "  T4/0.01% claim: ~168μs"
    if [[ "$GUARDIAN_P95" != "N/A" ]]; then
        if (( $(echo "$GUARDIAN_P95 < 210" | bc -l) )) && (( $(echo "$GUARDIAN_P95 > 126" | bc -l) )); then
            echo "  ✅ PASS: Within ±25% tolerance of claimed performance"
        else
            echo "  ❌ FAIL: Outside ±25% tolerance (${GUARDIAN_P95}μs)"
        fi
    else
        echo "  ⚠️  WARNING: Could not extract measurement"
    fi

    echo ""

    # Memory validation (target: ~178μs, tolerance: ±25%)
    echo "Memory E2E Performance:"
    echo "  Measured p95: ${MEMORY_P95}μs"
    echo "  T4/0.01% claim: ~178μs"
    if [[ "$MEMORY_P95" != "N/A" ]]; then
        if (( $(echo "$MEMORY_P95 < 222.5" | bc -l) )) && (( $(echo "$MEMORY_P95 > 133.5" | bc -l) )); then
            echo "  ✅ PASS: Within ±25% tolerance of claimed performance"
        else
            echo "  ❌ FAIL: Outside ±25% tolerance (${MEMORY_P95}μs)"
        fi
    else
        echo "  ⚠️  WARNING: Could not extract measurement"
    fi

    echo ""

    # Orchestrator validation (target: ~54ms, tolerance: ±25%)
    echo "Orchestrator E2E Performance:"
    echo "  Measured p95: ${ORCHESTRATOR_P95}μs"
    echo "  T4/0.01% claim: ~54,000μs (54ms)"
    if [[ "$ORCHESTRATOR_P95" != "N/A" ]]; then
        if (( $(echo "$ORCHESTRATOR_P95 < 67500" | bc -l) )) && (( $(echo "$ORCHESTRATOR_P95 > 40500" | bc -l) )); then
            echo "  ✅ PASS: Within ±25% tolerance of claimed performance"
        else
            echo "  ❌ FAIL: Outside ±25% tolerance (${ORCHESTRATOR_P95}μs)"
        fi
    else
        echo "  ⚠️  WARNING: Could not extract measurement"
    fi

    echo ""

    # Creativity validation (new component)
    echo "Creativity E2E Performance:"
    echo "  Measured p95: ${CREATIVITY_P95}μs"
    echo "  Expected range: <50,000μs (50ms)"
    if [[ "$CREATIVITY_P95" != "N/A" ]]; then
        if (( $(echo "$CREATIVITY_P95 < 50000" | bc -l) )); then
            echo "  ✅ PASS: Within expected performance range"
        else
            echo "  ❌ FAIL: Exceeds expected performance (${CREATIVITY_P95}μs)"
        fi
    else
        echo "  ⚠️  WARNING: Could not extract measurement"
    fi

else
    echo "⚠️  Warning: Cannot verify performance claims (missing jq or baseline file)"
fi

echo ""

# Phase 5: Generate Verification Package
echo "📦 Phase 5: Generate Verification Package"
echo "----------------------------------------"

echo "Creating verification checksums..."

cd /output
find . -name "*.json" -o -name "*.md" | sort | xargs sha256sum > "reproduction_checksums_${REPRODUCTION_ID}.sha256"

# Create summary report
cat > "REPRODUCTION_SUMMARY_${REPRODUCTION_ID}.md" << EOF
# T4/0.01% Excellence Independent Reproduction Summary

## Reproduction Information
- **Reproduction ID:** ${REPRODUCTION_ID}
- **Date:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
- **Container:** LUKHAS AI T4/0.01% Reproduction
- **Environment:** Independent verification container

## Files Generated
$(ls -la /output/ | tail -n +2)

## Performance Verification
$(if [[ "$GUARDIAN_P95" != "N/A" ]]; then echo "- Guardian p95: ${GUARDIAN_P95}μs"; fi)
$(if [[ "$MEMORY_P95" != "N/A" ]]; then echo "- Memory p95: ${MEMORY_P95}μs"; fi)
$(if [[ "$ORCHESTRATOR_P95" != "N/A" ]]; then echo "- Orchestrator p95: ${ORCHESTRATOR_P95}μs"; fi)
$(if [[ "$CREATIVITY_P95" != "N/A" ]]; then echo "- Creativity p95: ${CREATIVITY_P95}μs"; fi)

## Verification Status
To verify this reproduction:
1. Check file integrity: \`sha256sum -c reproduction_checksums_${REPRODUCTION_ID}.sha256\`
2. Review baseline measurements in \`reproduction_baseline_${REPRODUCTION_ID}.json\`
3. Compare with original T4/0.01% audit claims

## Independent Auditor Notes
This reproduction was performed in a controlled, isolated container environment
to provide independent verification of LUKHAS AI performance claims.

For questions or verification of this reproduction, examine the raw data files
and compare statistical distributions with the original audit evidence.
EOF

echo "✅ Verification package created"
echo ""

# Phase 6: Final Summary
echo "🎉 Independent Reproduction Complete"
echo "===================================="
echo ""
echo "Reproduction ID: $REPRODUCTION_ID"
echo "Output files: $(ls /output | wc -l)"
echo "Total output size: $(du -sh /output | cut -f1)"
echo ""
echo "📋 Key Files:"
echo "  - reproduction_baseline_${REPRODUCTION_ID}.json (raw measurements)"
echo "  - consistency_analysis_${REPRODUCTION_ID}.json (reproducibility data)"
echo "  - REPRODUCTION_SUMMARY_${REPRODUCTION_ID}.md (human-readable summary)"
echo "  - reproduction_checksums_${REPRODUCTION_ID}.sha256 (integrity verification)"
echo ""
echo "🔍 Verification Commands:"
echo "  sha256sum -c reproduction_checksums_${REPRODUCTION_ID}.sha256"
echo "  cat REPRODUCTION_SUMMARY_${REPRODUCTION_ID}.md"
echo ""

# Determine exit code based on verification
if [[ "$GUARDIAN_P95" != "N/A" && "$MEMORY_P95" != "N/A" && "$ORCHESTRATOR_P95" != "N/A" ]]; then
    # Check if all measurements are within tolerance
    GUARDIAN_OK=$(echo "$GUARDIAN_P95 < 210 && $GUARDIAN_P95 > 126" | bc -l)
    MEMORY_OK=$(echo "$MEMORY_P95 < 222.5 && $MEMORY_P95 > 133.5" | bc -l)
    ORCHESTRATOR_OK=$(echo "$ORCHESTRATOR_P95 < 67500 && $ORCHESTRATOR_P95 > 40500" | bc -l)

    if [[ "$GUARDIAN_OK" == "1" && "$MEMORY_OK" == "1" && "$ORCHESTRATOR_OK" == "1" ]]; then
        echo "✅ REPRODUCTION VERDICT: T4/0.01% CLAIMS VERIFIED"
        exit 0
    else
        echo "❌ REPRODUCTION VERDICT: T4/0.01% CLAIMS NOT VERIFIED"
        exit 1
    fi
else
    echo "⚠️  REPRODUCTION VERDICT: INCOMPLETE DATA (manual review required)"
    exit 2
fi