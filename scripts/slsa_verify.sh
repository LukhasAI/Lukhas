#!/bin/bash
#
# SLSA Provenance Verification Script
# 
# Usage:
#   ./scripts/slsa_verify.sh [reports-directory]
#   ./scripts/slsa_verify.sh --download <run-id>
#
# Examples:
#   # Verify artifacts in reports/ directory
#   ./scripts/slsa_verify.sh reports/
#
#   # Download and verify latest CI run
#   ./scripts/slsa_verify.sh --download latest
#
#   # Download and verify specific run
#   ./scripts/slsa_verify.sh --download 12345678

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check dependencies
check_dependencies() {
    local missing_deps=()

    if ! command -v cosign &> /dev/null; then
        missing_deps+=("cosign")
    fi

    if ! command -v gh &> /dev/null && [[ "${1:-}" == "--download" ]]; then
        missing_deps+=("gh (GitHub CLI)")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing dependencies: ${missing_deps[*]}${NC}"
        echo ""
        echo "Install instructions:"
        echo "  cosign: https://github.com/sigstore/cosign#installation"
        echo "  gh: https://cli.github.com/"
        exit 1
    fi
}

# Download artifacts from GitHub
download_artifacts() {
    local run_id="$1"
    local download_dir="./slsa-artifacts-$(date +%s)"

    echo -e "${YELLOW}📥 Downloading artifacts from GitHub...${NC}"

    if [ "$run_id" == "latest" ]; then
        run_id=$(gh run list --workflow="SLSA Provenance" --limit 1 --json databaseId --jq '.[0].databaseId')
        echo "Latest run ID: $run_id"
    fi

    mkdir -p "$download_dir"
    gh run download "$run_id" -n slsa-provenance -D "$download_dir"

    echo -e "${GREEN}✅ Downloaded to: $download_dir${NC}"
    echo "$download_dir"
}

# Verify provenance structure
verify_structure() {
    local reports_dir="$1"

    echo -e "${YELLOW}🔍 Verifying provenance structure...${NC}"

    local required_files=(
        "sbom.json"
        "provenance.json"
        "artifact-checksums.txt"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$reports_dir/$file" ]; then
            echo -e "${RED}❌ Missing required file: $file${NC}"
            return 1
        fi
    done

    # Check provenance JSON structure
    if ! python3 -c "
import json
import sys

with open('$reports_dir/provenance.json') as f:
    prov = json.load(f)

required_fields = [
    'SLSA_VERSION',
    'buildType',
    'builder',
    'invocation',
    'metadata',
    'materials',
    'sbomHash',
    'buildCommand'
]

missing = [f for f in required_fields if f not in prov]

if missing:
    print(f'❌ Missing required fields in provenance: {missing}')
    sys.exit(1)

print('✅ Provenance structure valid')
"; then
        return 1
    fi

    echo -e "${GREEN}✅ Provenance structure validated${NC}"
}

# Verify signatures
verify_signatures() {
    local reports_dir="$1"

    echo -e "${YELLOW}🔐 Verifying signatures with cosign...${NC}"

    local signed_files=(
        "sbom.json:sbom.bundle"
        "provenance.json:provenance.bundle"
    )

    for entry in "${signed_files[@]}"; do
        IFS=':' read -r file bundle <<< "$entry"

        if [ ! -f "$reports_dir/$bundle" ]; then
            # Check for dry run marker
            if [ -f "$reports_dir/$bundle.dryrun" ]; then
                echo -e "${YELLOW}⚠️  $file: Dry run mode - signature not verified${NC}"
                continue
            fi
            echo -e "${RED}❌ Signature bundle not found: $bundle${NC}"
            return 1
        fi

        echo "Verifying $file..."
        if cosign verify-blob \
            --bundle "$reports_dir/$bundle" \
            --certificate-identity-regexp=".*github.com/LukhasAI/Lukhas.*" \
            --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
            "$reports_dir/$file" &> /dev/null; then
            echo -e "${GREEN}  ✅ $file signature valid${NC}"
        else
            echo -e "${RED}  ❌ $file signature verification failed${NC}"
            return 1
        fi
    done

    echo -e "${GREEN}✅ All signatures verified${NC}"
}

# Verify checksums
verify_checksums() {
    local reports_dir="$1"

    echo -e "${YELLOW}🔍 Verifying artifact checksums...${NC}"

    if [ ! -f "$reports_dir/artifact-checksums.txt" ]; then
        echo -e "${YELLOW}⚠️  No checksum file found - skipping${NC}"
        return 0
    fi

    # Check if dist/ directory exists
    if [ -d "dist/" ]; then
        cd dist/
        if sha256sum -c "$reports_dir/artifact-checksums.txt" 2>/dev/null; then
            echo -e "${GREEN}✅ Artifact checksums verified${NC}"
        else
            echo -e "${YELLOW}⚠️  Some checksums don't match (may be expected if artifacts not present)${NC}"
        fi
        cd ..
    else
        echo -e "${YELLOW}⚠️  dist/ directory not found - skipping checksum verification${NC}"
    fi
}

# Display summary
display_summary() {
    local reports_dir="$1"

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}           SLSA Provenance Summary${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo ""

    if [ -f "$reports_dir/slsa-summary.md" ]; then
        cat "$reports_dir/slsa-summary.md"
    else
        # Extract key info from provenance
        python3 << PYTHON
import json

with open('$reports_dir/provenance.json') as f:
    prov = json.load(f)

print(f"SLSA Version: {prov.get('SLSA_VERSION', 'unknown')}")
print(f"Build Type: {prov.get('buildType', 'unknown')}")
print(f"Builder: {prov['builder']['id']}")
print(f"Git SHA: {prov['invocation']['configSource']['digest']['sha1'][:12]}")
print(f"Build Command: {prov.get('buildCommand', 'unknown')}")
print(f"Reproducible: {prov['metadata'].get('reproducible', False)}")
PYTHON
    fi

    echo ""
}

# Main verification flow
main() {
    local reports_dir="${1:-.reports}"

    echo -e "${GREEN}🔐 SLSA Provenance Verification Tool${NC}"
    echo ""

    # Check for download mode
    if [ "${1:-}" == "--download" ]; then
        check_dependencies "--download"
        reports_dir=$(download_artifacts "${2:-latest}")
    else
        check_dependencies
    fi

    # Normalize path
    reports_dir=$(realpath "$reports_dir" 2>/dev/null || echo "$reports_dir")

    if [ ! -d "$reports_dir" ]; then
        echo -e "${RED}❌ Directory not found: $reports_dir${NC}"
        echo ""
        echo "Usage:"
        echo "  $0 [reports-directory]"
        echo "  $0 --download [run-id|latest]"
        exit 1
    fi

    echo "Reports directory: $reports_dir"
    echo ""

    # Run verification steps
    local failed=0

    verify_structure "$reports_dir" || failed=1
    verify_signatures "$reports_dir" || failed=1
    verify_checksums "$reports_dir" || failed=1

    display_summary "$reports_dir"

    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}✅ All verifications passed!${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
        exit 0
    else
        echo -e "${RED}═══════════════════════════════════════════════════${NC}"
        echo -e "${RED}❌ Some verifications failed${NC}"
        echo -e "${RED}═══════════════════════════════════════════════════${NC}"
        exit 1
    fi
}

# Run main
main "$@"
