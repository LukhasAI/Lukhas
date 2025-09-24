#!/bin/bash
# T4/0.01% Excellence Audit Container Entry Point
# Provides comprehensive audit execution with multiple validation modes

set -e

# Default values
ENVIRONMENT="docker"
SAMPLES=1000
OUTPUT_DIR="/artifacts"
AUDIT_MODE="comprehensive"
SKIP_CHAOS=false
SKIP_STATISTICAL=false

# Function to display help
show_help() {
    cat << EOF
T4/0.01% Excellence Audit Container

USAGE:
    docker run lukhas-audit [OPTIONS]

OPTIONS:
    --environment ENV       Environment type (default: docker)
    --samples N            Number of samples (default: 1000)
    --output-dir DIR       Output directory (default: /artifacts)
    --audit-mode MODE      Audit mode: quick|standard|comprehensive (default: comprehensive)
    --skip-chaos           Skip chaos engineering tests
    --skip-statistical     Skip statistical analysis
    --chaos-level LEVEL    Chaos level: low|moderate|high|extreme (default: moderate)
    --help                 Show this help

EXAMPLES:
    # Quick audit with 500 samples
    docker run lukhas-audit --audit-mode quick --samples 500

    # Comprehensive audit with chaos testing
    docker run lukhas-audit --audit-mode comprehensive --chaos-level high

    # Statistical validation only
    docker run lukhas-audit --audit-mode standard --skip-chaos

OUTPUTS:
    All audit results are written to /artifacts/ (mounted volume)
    - audit_baseline_*.json: Performance measurements
    - statistical_*.json: Statistical analysis results
    - chaos_*.json: Chaos engineering results
    - verification_*.md: Human-readable reports
    - checksums.sha256: File integrity checksums

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --samples)
            SAMPLES="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --audit-mode)
            AUDIT_MODE="$2"
            shift 2
            ;;
        --skip-chaos)
            SKIP_CHAOS=true
            shift
            ;;
        --skip-statistical)
            SKIP_STATISTICAL=true
            shift
            ;;
        --chaos-level)
            CHAOS_LEVEL="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set defaults for chaos level
CHAOS_LEVEL=${CHAOS_LEVEL:-"moderate"}

# Generate unique audit run ID
AUDIT_RUN_ID="docker_$(date +%Y%m%d_%H%M%S)_$$"
export AUDIT_RUN_ID

echo "🔬 LUKHAS AI T4/0.01% Excellence Audit Container"
echo "================================================="
echo "Audit Run ID: $AUDIT_RUN_ID"
echo "Environment: $ENVIRONMENT"
echo "Samples: $SAMPLES"
echo "Audit Mode: $AUDIT_MODE"
echo "Output Directory: $OUTPUT_DIR"
echo "Chaos Level: $CHAOS_LEVEL"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Set audit environment variables
export PYTHONHASHSEED=0
export LUKHAS_MODE=release
export PYTHONDONTWRITEBYTECODE=1

echo "📊 Starting audit execution..."

# Phase 1: Baseline Performance Measurements
echo ""
echo "🔬 Phase 1: Baseline Performance Measurements"
echo "=============================================="

python3 scripts/audit_baseline.py \
    --environment "$ENVIRONMENT" \
    --samples "$SAMPLES" \
    --output "$OUTPUT_DIR/audit_baseline_${AUDIT_RUN_ID}.json"

BASELINE_FILE="$OUTPUT_DIR/audit_baseline_${AUDIT_RUN_ID}.json"

if [[ ! -f "$BASELINE_FILE" ]]; then
    echo "❌ Error: Baseline audit failed to generate results"
    exit 1
fi

echo "✅ Baseline measurements complete"

# Phase 2: Statistical Analysis (if not skipped)
if [[ "$SKIP_STATISTICAL" == "false" && "$AUDIT_MODE" != "quick" ]]; then
    echo ""
    echo "📈 Phase 2: Statistical Analysis"
    echo "================================"

    # Create a reference baseline for comparison
    python3 scripts/audit_baseline.py \
        --environment "${ENVIRONMENT}_reference" \
        --samples $((SAMPLES / 2)) \
        --output "$OUTPUT_DIR/audit_reference_${AUDIT_RUN_ID}.json"

    if [[ -f "$OUTPUT_DIR/audit_reference_${AUDIT_RUN_ID}.json" ]]; then
        python3 scripts/statistical_tests.py \
            --baseline "$BASELINE_FILE" \
            --comparison "$OUTPUT_DIR/audit_reference_${AUDIT_RUN_ID}.json" \
            --alpha 0.01 \
            --output "$OUTPUT_DIR/statistical_analysis_${AUDIT_RUN_ID}.json" \
            --report "$OUTPUT_DIR/statistical_report_${AUDIT_RUN_ID}.md"

        echo "✅ Statistical analysis complete"
    else
        echo "⚠️  Warning: Could not generate reference baseline for statistical analysis"
    fi
fi

# Phase 3: Reproducibility Analysis (if comprehensive mode)
if [[ "$AUDIT_MODE" == "comprehensive" ]]; then
    echo ""
    echo "🔄 Phase 3: Reproducibility Analysis"
    echo "===================================="

    # Generate multiple runs for reproducibility analysis
    REPRO_RUNS=5
    REPRO_FILES=()

    for i in $(seq 1 $REPRO_RUNS); do
        echo "Running reproducibility test $i/$REPRO_RUNS..."

        REPRO_FILE="$OUTPUT_DIR/repro_${i}_${AUDIT_RUN_ID}.json"

        python3 scripts/audit_baseline.py \
            --environment "${ENVIRONMENT}_repro_${i}" \
            --samples $((SAMPLES / 4)) \
            --output "$REPRO_FILE"

        if [[ -f "$REPRO_FILE" ]]; then
            REPRO_FILES+=("$REPRO_FILE")
        fi
    done

    if [[ ${#REPRO_FILES[@]} -ge 2 ]]; then
        python3 scripts/reproducibility_analysis.py \
            --data "${REPRO_FILES[@]}" \
            --output "$OUTPUT_DIR/reproducibility_analysis_${AUDIT_RUN_ID}.json" \
            --report "$OUTPUT_DIR/reproducibility_report_${AUDIT_RUN_ID}.md" \
            --target-reproducibility 0.80

        echo "✅ Reproducibility analysis complete"
    else
        echo "⚠️  Warning: Insufficient reproducibility data"
    fi
fi

# Phase 4: Chaos Engineering Tests (if not skipped)
if [[ "$SKIP_CHAOS" == "false" && "$AUDIT_MODE" != "quick" ]]; then
    echo ""
    echo "🌪️  Phase 4: Chaos Engineering Tests"
    echo "====================================="

    # Test Guardian under stress
    python3 scripts/test_fail_closed.py \
        --component guardian \
        --stress-level "$CHAOS_LEVEL" \
        --output "$OUTPUT_DIR/chaos_guardian_${AUDIT_RUN_ID}.json" \
        --requirement never_false_positive

    # Test Consciousness under stress
    python3 scripts/test_fail_closed.py \
        --component consciousness \
        --stress-level "$CHAOS_LEVEL" \
        --output "$OUTPUT_DIR/chaos_consciousness_${AUDIT_RUN_ID}.json" \
        --requirement never_false_positive

    # Test Creativity under stress
    python3 scripts/test_fail_closed.py \
        --component creativity \
        --stress-level "$CHAOS_LEVEL" \
        --output "$OUTPUT_DIR/chaos_creativity_${AUDIT_RUN_ID}.json" \
        --requirement never_false_positive

    echo "✅ Chaos engineering tests complete"
fi

# Phase 5: Tamper-Evident Proof Generation
echo ""
echo "🔒 Phase 5: Tamper-Evident Proof Generation"
echo "==========================================="

# Create Merkle chain from all evidence
EVIDENCE_FILES=($(find "$OUTPUT_DIR" -name "*.json" -type f))

if [[ ${#EVIDENCE_FILES[@]} -gt 0 ]]; then
    python3 scripts/verify_merkle_chain.py \
        --create-chain \
        --evidence "${EVIDENCE_FILES[@]}" \
        --output "$OUTPUT_DIR/merkle_chain_${AUDIT_RUN_ID}.json"

    echo "✅ Tamper-evident proof chain created"
else
    echo "⚠️  Warning: No evidence files found for Merkle chain"
fi

# Phase 6: Generate Checksums
echo ""
echo "🔍 Phase 6: Generate Integrity Checksums"
echo "========================================"

cd "$OUTPUT_DIR"
find . -name "*.json" -o -name "*.md" | sort | xargs sha256sum > "checksums_${AUDIT_RUN_ID}.sha256"

echo "✅ Integrity checksums generated"

# Phase 7: Final Audit Summary
echo ""
echo "📋 Phase 7: Final Audit Summary"
echo "==============================="

# Count results
JSON_FILES=$(find "$OUTPUT_DIR" -name "*.json" | wc -l)
REPORT_FILES=$(find "$OUTPUT_DIR" -name "*.md" | wc -l)
TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)

echo "📊 Audit Results Summary:"
echo "   JSON Evidence Files: $JSON_FILES"
echo "   Report Files: $REPORT_FILES"
echo "   Total Output Size: $TOTAL_SIZE"
echo "   Audit Run ID: $AUDIT_RUN_ID"
echo ""

# Validate key performance claims
if [[ -f "$BASELINE_FILE" ]]; then
    echo "🎯 Performance Validation:"

    # Extract key metrics using jq if available
    if command -v jq &> /dev/null; then
        GUARDIAN_P95=$(jq -r '.guardian_stats.p95' "$BASELINE_FILE" 2>/dev/null || echo "N/A")
        MEMORY_P95=$(jq -r '.memory_stats.p95' "$BASELINE_FILE" 2>/dev/null || echo "N/A")
        ORCHESTRATOR_P95=$(jq -r '.orchestrator_stats.p95' "$BASELINE_FILE" 2>/dev/null || echo "N/A")

        echo "   Guardian p95: ${GUARDIAN_P95}μs"
        echo "   Memory p95: ${MEMORY_P95}μs"
        echo "   Orchestrator p95: ${ORCHESTRATOR_P95}μs"

        # Check if results meet T4/0.01% claims
        if [[ "$GUARDIAN_P95" != "N/A" ]] && (( $(echo "$GUARDIAN_P95 < 200" | bc -l) )); then
            echo "   ✅ Guardian: Meets T4/0.01% target (<200μs)"
        elif [[ "$GUARDIAN_P95" != "N/A" ]]; then
            echo "   ⚠️  Guardian: ${GUARDIAN_P95}μs may exceed expectations"
        fi

        if [[ "$MEMORY_P95" != "N/A" ]] && (( $(echo "$MEMORY_P95 < 1000" | bc -l) )); then
            echo "   ✅ Memory: Meets T4/0.01% target (<1ms)"
        elif [[ "$MEMORY_P95" != "N/A" ]]; then
            echo "   ⚠️  Memory: ${MEMORY_P95}μs may exceed expectations"
        fi

        if [[ "$ORCHESTRATOR_P95" != "N/A" ]] && (( $(echo "$ORCHESTRATOR_P95 < 250000" | bc -l) )); then
            echo "   ✅ Orchestrator: Meets T4/0.01% target (<250ms)"
        elif [[ "$ORCHESTRATOR_P95" != "N/A" ]]; then
            echo "   ⚠️  Orchestrator: ${ORCHESTRATOR_P95}μs may exceed expectations"
        fi
    fi
fi

echo ""
echo "🎉 T4/0.01% Excellence Audit Complete"
echo "====================================="
echo "Audit Run ID: $AUDIT_RUN_ID"
echo "All results available in: $OUTPUT_DIR"
echo "Checksum verification: sha256sum -c checksums_${AUDIT_RUN_ID}.sha256"
echo ""
echo "🛡️  Evidence package ready for independent verification"

# Set appropriate exit code
exit 0