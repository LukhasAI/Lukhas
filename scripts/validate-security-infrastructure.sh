#!/bin/bash

# ΛiD Authentication System - Security Infrastructure Validation
#
# This script validates the security infrastructure components and
# ensures all security measures are properly implemented.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# Logging
LOG_FILE="security-validation-$(date +%Y%m%d-%H%M%S).log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

test_result() {
    local test_name="$1"
    local result="$2"
    local message="$3"

    if [[ "$result" == "PASS" ]]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        [[ -n "$message" ]] && echo "   $message"
        ((TESTS_PASSED++))
        log "PASS: $test_name - $message"
    elif [[ "$result" == "FAIL" ]]; then
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        [[ -n "$message" ]] && echo "   $message"
        ((TESTS_FAILED++))
        log "FAIL: $test_name - $message"
    elif [[ "$result" == "WARN" ]]; then
        echo -e "${YELLOW}⚠️  WARN${NC}: $test_name"
        [[ -n "$message" ]] && echo "   $message"
        ((WARNINGS++))
        log "WARN: $test_name - $message"
    fi
}

# Test environment configuration
test_environment_config() {
    echo -e "${BLUE}🔧 Testing Environment Configuration...${NC}"

    # Check .env.example exists
    if [[ -f ".env.example" ]]; then
        test_result "Environment template exists" "PASS" ".env.example found"
    else
        test_result "Environment template exists" "FAIL" ".env.example not found"
        return
    fi

    # Check required ΛiD auth variables
    local required_vars=(
        "AUTH_PASSWORD_ENABLED"
        "AUTH_MAGIC_LINK_TTL_SECONDS"
        "AUTH_ACCESS_TTL_MINUTES"
        "AUTH_REFRESH_TTL_DAYS"
        "AUTH_REQUIRE_UV"
        "AUTH_RPID"
        "AUTH_ALLOWED_ORIGINS"
        "JWT_PRIVATE_KEY"
        "JWT_PUBLIC_KEY"
        "JWT_KEY_ID"
        "BREAK_GLASS_OWNER_EMAIL"
        "AUTH_AUDIT_LOGGING"
    )

    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" .env.example; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -eq 0 ]]; then
        test_result "Required auth variables present" "PASS" "All ${#required_vars[@]} variables found"
    else
        test_result "Required auth variables present" "FAIL" "Missing: ${missing_vars[*]}"
    fi

    # Check security defaults
    if grep -q "AUTH_PASSWORD_ENABLED=false" .env.example; then
        test_result "Password auth disabled by default" "PASS" "AUTH_PASSWORD_ENABLED=false"
    else
        test_result "Password auth disabled by default" "WARN" "Password auth should be disabled"
    fi

    if grep -q "AUTH_PREVENT_ENUMERATION=true" .env.example; then
        test_result "Enumeration protection enabled" "PASS" "AUTH_PREVENT_ENUMERATION=true"
    else
        test_result "Enumeration protection enabled" "WARN" "Enumeration protection should be enabled"
    fi
}

# Test HTTPS development setup
test_https_development() {
    echo -e "${BLUE}🔒 Testing HTTPS Development Setup...${NC}"

    # Check Next.js config exists
    if [[ -f "lukhas_website/next.config.js" ]]; then
        test_result "Next.js config exists" "PASS" "next.config.js found"
    else
        test_result "Next.js config exists" "FAIL" "next.config.js not found"
        return
    fi

    # Check HTTPS configuration
    if grep -q "server:" lukhas_website/next.config.js && grep -q "https:" lukhas_website/next.config.js; then
        test_result "HTTPS dev config present" "PASS" "Server HTTPS configuration found"
    else
        test_result "HTTPS dev config present" "FAIL" "HTTPS configuration missing"
    fi

    # Check security headers
    local security_headers=(
        "X-Content-Type-Options"
        "X-Frame-Options"
        "Referrer-Policy"
        "Permissions-Policy"
    )

    local missing_headers=()
    for header in "${security_headers[@]}"; do
        if ! grep -q "$header" lukhas_website/next.config.js; then
            missing_headers+=("$header")
        fi
    done

    if [[ ${#missing_headers[@]} -eq 0 ]]; then
        test_result "Security headers configured" "PASS" "All ${#security_headers[@]} headers found"
    else
        test_result "Security headers configured" "WARN" "Missing headers: ${missing_headers[*]}"
    fi

    # Check certificate generation script
    if [[ -f "scripts/generate-dev-certs.sh" && -x "scripts/generate-dev-certs.sh" ]]; then
        test_result "Certificate generation script" "PASS" "Script exists and is executable"
    else
        test_result "Certificate generation script" "FAIL" "Script missing or not executable"
    fi
}

# Test JWKS infrastructure
test_jwks_infrastructure() {
    echo -e "${BLUE}🔑 Testing JWKS Infrastructure...${NC}"

    # Check JWKS TypeScript module
    if [[ -f "lukhas_website/packages/auth/jwks.ts" ]]; then
        test_result "JWKS module exists" "PASS" "jwks.ts found"
    else
        test_result "JWKS module exists" "FAIL" "jwks.ts not found"
        return
    fi

    # Check JWKS API endpoint
    if [[ -f "lukhas_website/app/api/.well-known/jwks/route.ts" ]]; then
        test_result "JWKS API endpoint exists" "PASS" "route.ts found"
    else
        test_result "JWKS API endpoint exists" "FAIL" "JWKS endpoint not found"
    fi

    # Check JWKS module structure
    local jwks_components=(
        "JWKSManager"
        "KeyRotationManager"
        "generateKeyPair"
        "getJWKS"
        "rotateKeys"
    )

    local missing_components=()
    for component in "${jwks_components[@]}"; do
        if ! grep -q "$component" lukhas_website/packages/auth/jwks.ts; then
            missing_components+=("$component")
        fi
    done

    if [[ ${#missing_components[@]} -eq 0 ]]; then
        test_result "JWKS components complete" "PASS" "All ${#jwks_components[@]} components found"
    else
        test_result "JWKS components complete" "WARN" "Missing: ${missing_components[*]}"
    fi
}

# Test security infrastructure
test_security_infrastructure() {
    echo -e "${BLUE}🛡️ Testing Security Infrastructure...${NC}"

    # Check security module
    if [[ -f "lukhas_website/packages/auth/security.ts" ]]; then
        test_result "Security module exists" "PASS" "security.ts found"
    else
        test_result "Security module exists" "FAIL" "security.ts not found"
        return
    fi

    # Check security components
    local security_components=(
        "SecurityManager"
        "checkEmailRateLimit"
        "checkAuthRateLimit"
        "getSafeResponse"
        "logAuditEvent"
        "DEFAULT_SECURITY_CONFIG"
    )

    local missing_components=()
    for component in "${security_components[@]}"; do
        if ! grep -q "$component" lukhas_website/packages/auth/security.ts; then
            missing_components+=("$component")
        fi
    done

    if [[ ${#missing_components[@]} -eq 0 ]]; then
        test_result "Security components complete" "PASS" "All ${#security_components[@]} components found"
    else
        test_result "Security components complete" "WARN" "Missing: ${missing_components[*]}"
    fi

    # Check rate limiting configuration
    if grep -q "emailRateLimit" lukhas_website/packages/auth/security.ts &&
       grep -q "ipRateLimit" lukhas_website/packages/auth/security.ts &&
       grep -q "failedAuthLimit" lukhas_website/packages/auth/security.ts; then
        test_result "Rate limiting configured" "PASS" "Email, IP, and auth rate limits found"
    else
        test_result "Rate limiting configured" "FAIL" "Rate limiting configuration incomplete"
    fi
}

# Test documentation
test_documentation() {
    echo -e "${BLUE}📚 Testing Documentation...${NC}"

    # Check security documentation directory
    if [[ -d "docs/security" ]]; then
        test_result "Security docs directory exists" "PASS" "docs/security/ found"
    else
        test_result "Security docs directory exists" "FAIL" "docs/security/ not found"
        return
    fi

    # Check key documentation files
    local doc_files=(
        "docs/security/README.md"
        "docs/security/break-glass-procedure.md"
        "docs/security/email-security-requirements.md"
    )

    local missing_docs=()
    for doc in "${doc_files[@]}"; do
        if [[ ! -f "$doc" ]]; then
            missing_docs+=("$(basename "$doc")")
        fi
    done

    if [[ ${#missing_docs[@]} -eq 0 ]]; then
        test_result "Security documentation complete" "PASS" "All ${#doc_files[@]} documents found"
    else
        test_result "Security documentation complete" "WARN" "Missing docs: ${missing_docs[*]}"
    fi

    # Check break-glass procedure completeness
    if [[ -f "docs/security/break-glass-procedure.md" ]]; then
        local bg_sections=(
            "Multi-Factor Authentication"
            "Emergency Access Procedure"
            "Audit Requirements"
            "Key Rotation Schedule"
            "Emergency Contact"
        )

        local missing_sections=()
        for section in "${bg_sections[@]}"; do
            if ! grep -q "$section" docs/security/break-glass-procedure.md; then
                missing_sections+=("$section")
            fi
        done

        if [[ ${#missing_sections[@]} -eq 0 ]]; then
            test_result "Break-glass documentation complete" "PASS" "All sections present"
        else
            test_result "Break-glass documentation complete" "WARN" "Missing sections: ${missing_sections[*]}"
        fi
    fi
}

# Test utility scripts
test_utility_scripts() {
    echo -e "${BLUE}🔧 Testing Utility Scripts...${NC}"

    # Check key management script
    if [[ -f "scripts/key-management.sh" && -x "scripts/key-management.sh" ]]; then
        test_result "Key management script exists" "PASS" "Script exists and is executable"
    else
        test_result "Key management script exists" "FAIL" "Script missing or not executable"
    fi

    # Check key management commands
    if [[ -f "scripts/key-management.sh" ]]; then
        local key_commands=(
            "generate-jwt-keys"
            "rotate-keys"
            "generate-totp"
            "validate-keys"
            "backup-keys"
        )

        local missing_commands=()
        for cmd in "${key_commands[@]}"; do
            if ! grep -q "$cmd" scripts/key-management.sh; then
                missing_commands+=("$cmd")
            fi
        done

        if [[ ${#missing_commands[@]} -eq 0 ]]; then
            test_result "Key management commands complete" "PASS" "All ${#key_commands[@]} commands found"
        else
            test_result "Key management commands complete" "WARN" "Missing commands: ${missing_commands[*]}"
        fi
    fi

    # Check validation script (this script)
    if [[ -f "scripts/validate-security-infrastructure.sh" && -x "scripts/validate-security-infrastructure.sh" ]]; then
        test_result "Security validation script exists" "PASS" "Script exists and is executable"
    else
        test_result "Security validation script exists" "WARN" "Script missing or not executable"
    fi
}

# Test dependencies
test_dependencies() {
    echo -e "${BLUE}📦 Testing Dependencies...${NC}"

    # Check required system tools
    local system_deps=("openssl" "curl" "jq" "base64")
    local missing_deps=()

    for dep in "${system_deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done

    if [[ ${#missing_deps[@]} -eq 0 ]]; then
        test_result "System dependencies available" "PASS" "All ${#system_deps[@]} tools found"
    else
        test_result "System dependencies available" "FAIL" "Missing tools: ${missing_deps[*]}"
    fi

    # Check Node.js and npm
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        local node_version=$(node --version)
        local npm_version=$(npm --version)
        test_result "Node.js and npm available" "PASS" "Node $node_version, npm $npm_version"
    else
        test_result "Node.js and npm available" "FAIL" "Node.js or npm not found"
    fi

    # Check TypeScript support
    if [[ -f "lukhas_website/package.json" ]]; then
        if grep -q "typescript" lukhas_website/package.json; then
            test_result "TypeScript configured" "PASS" "TypeScript dependency found"
        else
            test_result "TypeScript configured" "WARN" "TypeScript dependency missing"
        fi
    fi
}

# Main validation function
main() {
    echo -e "${BLUE}🔐 ΛiD Authentication System - Security Infrastructure Validation${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo ""

    log "Starting security infrastructure validation"

    # Run all tests
    test_environment_config
    echo ""

    test_https_development
    echo ""

    test_jwks_infrastructure
    echo ""

    test_security_infrastructure
    echo ""

    test_documentation
    echo ""

    test_utility_scripts
    echo ""

    test_dependencies
    echo ""

    # Summary
    echo -e "${BLUE}📊 Validation Summary${NC}"
    echo -e "${BLUE}===================${NC}"
    echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
    echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
    echo ""

    local total_tests=$((TESTS_PASSED + TESTS_FAILED))
    if [[ $total_tests -gt 0 ]]; then
        local success_rate=$((TESTS_PASSED * 100 / total_tests))
        echo -e "${BLUE}Success Rate: ${success_rate}%${NC}"
    fi

    echo ""
    echo -e "${BLUE}📝 Detailed log written to: $LOG_FILE${NC}"

    log "Validation completed - Passed: $TESTS_PASSED, Failed: $TESTS_FAILED, Warnings: $WARNINGS"

    # Exit with appropriate code
    if [[ $TESTS_FAILED -gt 0 ]]; then
        exit 1
    elif [[ $WARNINGS -gt 0 ]]; then
        exit 2
    else
        exit 0
    fi
}

# Run main function
main "$@"
