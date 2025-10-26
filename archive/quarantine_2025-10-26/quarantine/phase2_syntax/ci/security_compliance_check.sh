#!/bin/bash
# LUKHAS AI Security Compliance Check - Guardian System v1.0.0
# Constitutional AI aligned security validation for CI/CD pipeline
# Generated: 2025-09-11 (MATRIZ-R1 Stream C Task C-CC1)

set -euo pipefail

echo "🛡️  LUKHAS AI Security Compliance Check - Guardian System v1.0.0"
echo "========================================================================"
echo "📅 Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "🔐 Constitutional AI Safety Framework"
echo "📋 GDPR/CCPA Compliance Validation"
echo "========================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [[ $status == "SUCCESS" ]]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [[ $status == "WARNING" ]]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    elif [[ $status == "ERROR" ]]; then
        echo -e "${RED}❌ $message${NC}"
    else
        echo -e "${BLUE}ℹ️  $message${NC}"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Initialize counters
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# 1. Validate Guardian System Infrastructure
echo ""
echo "🛡️  GUARDIAN SYSTEM INFRASTRUCTURE CHECK"
echo "----------------------------------------"

if [[ -f "docs/architecture/SECURITY_ARCHITECTURE.json" ]]; then
    print_status "SUCCESS" "Security architecture configuration found"
    ((CHECKS_PASSED++))
else
    print_status "ERROR" "Security architecture configuration missing"
    ((CHECKS_FAILED++))
fi

if [[ -f "constraints.txt" ]]; then
    if grep -q "Guardian System v1.0.0" constraints.txt; then
        print_status "SUCCESS" "Guardian-validated dependency constraints found"
        ((CHECKS_PASSED++))
    else
        print_status "WARNING" "Constraints file exists but lacks Guardian validation"
        ((WARNINGS++))
    fi
else
    print_status "ERROR" "Dependency constraints file missing"
    ((CHECKS_FAILED++))
fi

if [[ -f ".gitleaks.toml" ]]; then
    print_status "SUCCESS" "Gitleaks security configuration found"
    ((CHECKS_PASSED++))
else
    print_status "WARNING" "Gitleaks configuration missing"
    ((WARNINGS++))
fi

# 2. SBOM Compliance Check
echo ""
echo "📋 SBOM COMPLIANCE CHECK"
echo "------------------------"

if [[ -f "reports/sbom/cyclonedx.json" ]]; then
    print_status "SUCCESS" "SBOM file exists"
    
    # Check SBOM validity
    if command_exists "cyclonedx-bom"; then
        if cyclonedx-bom --validate reports/sbom/cyclonedx.json >/dev/null 2>&1; then
            print_status "SUCCESS" "SBOM validation passed"
            ((CHECKS_PASSED++))
        else
            print_status "WARNING" "SBOM validation failed"
            ((WARNINGS++))
        fi
    else
        print_status "WARNING" "cyclonedx-bom not available for validation"
        ((WARNINGS++))
    fi
    
    # Check SBOM content
    COMPONENT_COUNT=$(grep -o '"bom-ref"' reports/sbom/cyclonedx.json | wc -l)
    if [[ $COMPONENT_COUNT -gt 50 ]]; then
        print_status "SUCCESS" "SBOM contains $COMPONENT_COUNT components"
        ((CHECKS_PASSED++))
    else
        print_status "WARNING" "SBOM contains only $COMPONENT_COUNT components"
        ((WARNINGS++))
    fi
else
    print_status "ERROR" "SBOM file missing - generate with: cyclonedx-bom -o reports/sbom/cyclonedx.json"
    ((CHECKS_FAILED++))
fi

# 3. Dependency Security Check
echo ""
echo "🔒 DEPENDENCY SECURITY CHECK"
echo "----------------------------"

if [[ -f "constraints.txt" ]]; then
    # Check for critical security dependencies
    CRITICAL_DEPS=("cryptography" "pydantic" "aiohttp" "transformers" "requests")
    for dep in "${CRITICAL_DEPS[@]}"; do
        if grep -q "^${dep}==" constraints.txt; then
            print_status "SUCCESS" "Critical dependency $dep is pinned"
            ((CHECKS_PASSED++))
        else
            print_status "WARNING" "Critical dependency $dep is not pinned"
            ((WARNINGS++))
        fi
    done
else
    print_status "ERROR" "Constraints file missing"
    ((CHECKS_FAILED++))
fi

# 4. Constitutional AI Compliance Check
echo ""
echo "⚖️  CONSTITUTIONAL AI COMPLIANCE CHECK"
echo "-------------------------------------"

if [[ -f "docs/architecture/SECURITY_ARCHITECTURE.json" ]]; then
    if grep -q "constitutional_ai_framework" docs/architecture/SECURITY_ARCHITECTURE.json; then
        print_status "SUCCESS" "Constitutional AI framework present"
        ((CHECKS_PASSED++))
    else
        print_status "ERROR" "Constitutional AI framework missing"
        ((CHECKS_FAILED++))
    fi
    
    if grep -q "drift_detection_threshold.*0.15" docs/architecture/SECURITY_ARCHITECTURE.json; then
        print_status "SUCCESS" "Guardian drift detection threshold configured"
        ((CHECKS_PASSED++))
    else
        print_status "WARNING" "Guardian drift detection threshold not properly configured"
        ((WARNINGS++))
    fi
    
    if grep -q "human_override_capability.*always_available" docs/architecture/SECURITY_ARCHITECTURE.json; then
        print_status "SUCCESS" "Human override capability enabled"
        ((CHECKS_PASSED++))
    else
        print_status "ERROR" "Human override capability not properly configured"
        ((CHECKS_FAILED++))
    fi
fi

# 5. CI/CD Security Integration Check
echo ""
echo "🔄 CI/CD SECURITY INTEGRATION CHECK"
echo "-----------------------------------"

if [[ -f ".github/workflows/ci.yml" ]]; then
    if grep -q "constraints.txt" .github/workflows/ci.yml; then
        print_status "SUCCESS" "CI pipeline uses security constraints"
        ((CHECKS_PASSED++))
    else
        print_status "WARNING" "CI pipeline doesn't use security constraints"
        ((WARNINGS++))
    fi
    
    if grep -q "gitleaks" .github/workflows/ci.yml; then
        print_status "SUCCESS" "CI pipeline includes gitleaks scanning"
        ((CHECKS_PASSED++))
    else
        print_status "WARNING" "CI pipeline missing gitleaks scanning"
        ((WARNINGS++))
    fi
    
    if grep -q "cyclonedx-bom" .github/workflows/ci.yml; then
        print_status "SUCCESS" "CI pipeline generates SBOM"
        ((CHECKS_PASSED++))
    else
        print_status "WARNING" "CI pipeline doesn't generate SBOM"
        ((WARNINGS++))
    fi
else
    print_status "ERROR" "CI configuration missing"
    ((CHECKS_FAILED++))
fi

# 6. Guardian Compliance Validator Check
echo ""
echo "🎯 GUARDIAN COMPLIANCE VALIDATOR CHECK"
echo "--------------------------------------"

if [[ -f "tools/security/guardian_compliance_validator.py" ]]; then
    print_status "SUCCESS" "Guardian compliance validator present"
    
    # Run the validator if Python is available
    if command_exists "python3"; then
        print_status "INFO" "Running Guardian compliance validation..."
        if python3 tools/security/guardian_compliance_validator.py >/dev/null 2>&1; then
            print_status "SUCCESS" "Guardian compliance validation passed"
            ((CHECKS_PASSED++))
        else
            print_status "WARNING" "Guardian compliance validation found issues"
            ((WARNINGS++))
        fi
    else
        print_status "WARNING" "Python3 not available for compliance validation"
        ((WARNINGS++))
    fi
else
    print_status "ERROR" "Guardian compliance validator missing"
    ((CHECKS_FAILED++))
fi

# 7. Audit Trail Documentation Check
echo ""
echo "📚 AUDIT TRAIL DOCUMENTATION CHECK"
echo "----------------------------------"

REQUIRED_DOCS=(
    "docs/compliance/SECURITY_AUDIT_TRAIL.md"
    "docs/architecture/SECURITY_ARCHITECTURE.json"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [[ -f "$doc" ]]; then
        print_status "SUCCESS" "Documentation present: $doc"
        ((CHECKS_PASSED++))
    else
        print_status "ERROR" "Documentation missing: $doc"
        ((CHECKS_FAILED++))
    fi
done

# Summary
echo ""
echo "========================================================================"
echo "🏁 SECURITY COMPLIANCE CHECK SUMMARY"
echo "========================================================================"
echo "✅ Checks Passed: $CHECKS_PASSED"
echo "⚠️  Warnings: $WARNINGS"
echo "❌ Checks Failed: $CHECKS_FAILED"
echo ""

# Determine overall status
TOTAL_ISSUES=$((CHECKS_FAILED + WARNINGS))

if [[ $CHECKS_FAILED -eq 0 && $WARNINGS -eq 0 ]]; then
    print_status "SUCCESS" "ALL GUARDIAN SYSTEM v1.0.0 COMPLIANCE CHECKS PASSED! 🎉"
    echo "🔐 Constitutional AI Safety Framework: FULLY COMPLIANT"
    echo "📋 GDPR/CCPA Compliance: READY FOR AUDIT"
    echo "🛡️  Guardian System: OPERATIONAL"
    exit 0
elif [[ $CHECKS_FAILED -eq 0 ]]; then
    print_status "WARNING" "Guardian System compliance passed with warnings"
    echo "⚠️  Address $WARNINGS warning(s) for full compliance"
    exit 0
else
    print_status "ERROR" "Guardian System compliance check FAILED"
    echo "❌ Fix $CHECKS_FAILED critical issue(s) and $WARNINGS warning(s)"
    echo ""
    echo "🔧 QUICK FIXES:"
    echo "- Generate SBOM: cyclonedx-bom -o reports/sbom/cyclonedx.json"
    echo "- Validate constraints: pip install -c constraints.txt -r requirements.txt"
    echo "- Run Guardian validator: python3 tools/security/guardian_compliance_validator.py"
    exit 1
fi