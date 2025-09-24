#!/bin/bash

# LUKHAS Health Check Script
# Usage: ./scripts/health-check.sh [environment] [service]

set -euo pipefail

# Check for help first
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    echo "LUKHAS Health Check Script"
    echo ""
    echo "Usage: $0 [environment] [service]"
    echo ""
    echo "Environments: staging, production, local"
    echo "Services: all, core, identity, memory, consciousness, governance, infrastructure"
    echo ""
    echo "Options:"
    echo "  -c, --continuous    Continuous monitoring mode"
    echo "  -h, --help         Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 staging all"
    echo "  $0 production identity"
    echo "  $0 local --continuous"
    exit 0
fi

# Configuration
ENVIRONMENT="${1:-staging}"
SERVICE="${2:-all}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# URLs based on environment
case "$ENVIRONMENT" in
    staging)
        BASE_URL="https://staging.lukhas.ai"
        MONITORING_URL="https://monitoring-staging.lukhas.ai"
        ;;
    production)
        BASE_URL="https://lukhas.ai"
        MONITORING_URL="https://monitoring.lukhas.ai"
        ;;
    local)
        BASE_URL="http://localhost:8080"
        MONITORING_URL="http://localhost:3000"
        ;;
    *)
        echo -e "${RED}[ERROR]${NC} Invalid environment: $ENVIRONMENT"
        exit 1
        ;;
esac

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Health check function
check_endpoint() {
    local name="$1"
    local url="$2"
    local timeout="${3:-10}"

    if curl -f -s --max-time "$timeout" "$url" > /dev/null 2>&1; then
        log_success "✓ $name ($url)"
        return 0
    else
        log_error "✗ $name ($url)"
        return 1
    fi
}

# Detailed health check with JSON response
check_health_detailed() {
    local name="$1"
    local url="$2"

    log_info "Checking $name..."

    local response
    if response=$(curl -f -s --max-time 10 "$url" 2>/dev/null); then
        # Try to parse JSON response
        if echo "$response" | jq . > /dev/null 2>&1; then
            local status=$(echo "$response" | jq -r '.status // "unknown"')
            local version=$(echo "$response" | jq -r '.version // "unknown"')
            local uptime=$(echo "$response" | jq -r '.uptime // "unknown"')

            log_success "✓ $name"
            echo "    Status: $status"
            echo "    Version: $version"
            echo "    Uptime: $uptime"

            # Check for any warnings or errors in health check
            local warnings=$(echo "$response" | jq -r '.warnings[]? // empty' 2>/dev/null)
            if [[ -n "$warnings" ]]; then
                log_warning "    Warnings: $warnings"
            fi

            local errors=$(echo "$response" | jq -r '.errors[]? // empty' 2>/dev/null)
            if [[ -n "$errors" ]]; then
                log_error "    Errors: $errors"
                return 1
            fi
        else
            log_success "✓ $name (non-JSON response)"
        fi
        return 0
    else
        log_error "✗ $name ($url)"
        return 1
    fi
}

# Check core services
check_core_services() {
    log_info "=== Core Services Health Check ==="

    local failed=0

    # Core service endpoints
    local endpoints=(
        "Core Service:$BASE_URL/health"
        "Identity Service:$BASE_URL/api/v1/identity/health"
        "Memory Service:$BASE_URL/api/v1/memory/health"
        "Consciousness Service:$BASE_URL/api/v1/consciousness/health"
        "Governance Service:$BASE_URL/api/v1/governance/health"
    )

    for endpoint_info in "${endpoints[@]}"; do
        IFS=':' read -r name url <<< "$endpoint_info"

        if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "${name,,}" ]] || [[ "$SERVICE" == "${name// /}" ]]; then
            if ! check_health_detailed "$name" "$url"; then
                ((failed++))
            fi
        fi
    done

    echo ""
    return $failed
}

# Check infrastructure services
check_infrastructure() {
    log_info "=== Infrastructure Health Check ==="

    local failed=0

    # Infrastructure endpoints
    local endpoints=(
        "Prometheus:$MONITORING_URL:9090/api/v1/status/config"
        "Grafana:$MONITORING_URL/api/health"
        "AlertManager:$MONITORING_URL:9093/api/v1/status"
    )

    # Only check if monitoring is requested or all services
    if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "infrastructure" ]] || [[ "$SERVICE" == "monitoring" ]]; then
        for endpoint_info in "${endpoints[@]}"; do
            IFS=':' read -r name base_url port path <<< "$endpoint_info"
            local full_url="$base_url:$port$path"

            if ! check_endpoint "$name" "$full_url"; then
                ((failed++))
            fi
        done
    fi

    echo ""
    return $failed
}

# Check API endpoints functionality
check_api_functionality() {
    log_info "=== API Functionality Check ==="

    local failed=0

    # Test OAuth2 discovery endpoint
    if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "identity" ]]; then
        if ! check_endpoint "OAuth2 Discovery" "$BASE_URL/.well-known/openid_configuration"; then
            ((failed++))
        fi
    fi

    # Test public API endpoints
    local api_endpoints=(
        "API Status:$BASE_URL/api/v1/status"
        "Identity Metrics:$BASE_URL/api/v1/identity/metrics"
        "Memory Status:$BASE_URL/api/v1/memory/status"
    )

    for endpoint_info in "${api_endpoints[@]}"; do
        IFS=':' read -r name url <<< "$endpoint_info"
        service_name=$(echo "$name" | cut -d' ' -f1 | tr '[:upper:]' '[:lower:]')

        if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "$service_name" ]]; then
            if ! check_endpoint "$name" "$url"; then
                ((failed++))
            fi
        fi
    done

    echo ""
    return $failed
}

# Check performance metrics
check_performance() {
    log_info "=== Performance Metrics ==="

    if [[ "$ENVIRONMENT" == "local" ]]; then
        log_warning "Performance checks skipped for local environment"
        return 0
    fi

    # Test response times
    local endpoints=(
        "$BASE_URL/health"
        "$BASE_URL/api/v1/identity/health"
        "$BASE_URL/api/v1/memory/health"
    )

    for url in "${endpoints[@]}"; do
        local response_time
        if response_time=$(curl -o /dev/null -s -w "%{time_total}" --max-time 5 "$url" 2>/dev/null); then
            local response_ms=$(echo "$response_time * 1000" | bc)
            if (( $(echo "$response_time < 1.0" | bc -l) )); then
                log_success "✓ $(basename "$url"): ${response_ms%.*}ms"
            else
                log_warning "⚠ $(basename "$url"): ${response_ms%.*}ms (slow)"
            fi
        else
            log_error "✗ $(basename "$url"): timeout"
        fi
    done

    echo ""
}

# Generate health report
generate_report() {
    local total_failed="$1"

    echo "=== Health Check Summary ==="
    echo "Environment: $ENVIRONMENT"
    echo "Service: $SERVICE"
    echo "Timestamp: $(date)"
    echo "Base URL: $BASE_URL"
    echo ""

    if [[ $total_failed -eq 0 ]]; then
        log_success "🎉 All health checks passed!"
        echo ""
        echo "System Status: HEALTHY"
        return 0
    else
        log_error "❌ $total_failed health check(s) failed"
        echo ""
        echo "System Status: DEGRADED"
        echo ""
        echo "Recommended actions:"
        echo "1. Check service logs: docker-compose logs [service-name]"
        echo "2. Verify configuration files"
        echo "3. Check monitoring dashboards: $MONITORING_URL"
        echo "4. Review recent deployments"
        return 1
    fi
}

# Continuous monitoring mode
continuous_mode() {
    log_info "Starting continuous health monitoring (Ctrl+C to stop)..."

    while true; do
        clear
        echo "LUKHAS Health Monitor - $(date)"
        echo "Environment: $ENVIRONMENT | Service: $SERVICE"
        echo "================================================"

        local failed=0
        failed=$((failed + $(check_core_services)))

        if [[ $failed -eq 0 ]]; then
            echo -e "${GREEN}Status: HEALTHY${NC}"
        else
            echo -e "${RED}Status: DEGRADED ($failed failures)${NC}"
        fi

        echo ""
        echo "Next check in 30 seconds..."
        sleep 30
    done
}

# Main function
main() {
    # Check if help is requested in first argument
    if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
        echo "LUKHAS Health Check Script"
        echo ""
        echo "Usage: $0 [environment] [service]"
        echo ""
        echo "Environments: staging, production, local"
        echo "Services: all, core, identity, memory, consciousness, governance, infrastructure"
        echo ""
        echo "Options:"
        echo "  -c, --continuous    Continuous monitoring mode"
        echo "  -h, --help         Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 staging all"
        echo "  $0 production identity"
        echo "  $0 local --continuous"
        exit 0
    fi

    case "${SERVICE}" in
        -c|--continuous)
            continuous_mode
            ;;
        -h|--help)
            echo "LUKHAS Health Check Script"
            echo ""
            echo "Usage: $0 [environment] [service]"
            echo ""
            echo "Environments: staging, production, local"
            echo "Services: all, core, identity, memory, consciousness, governance, infrastructure"
            echo ""
            echo "Options:"
            echo "  -c, --continuous    Continuous monitoring mode"
            echo "  -h, --help         Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 staging all"
            echo "  $0 production identity"
            echo "  $0 local --continuous"
            exit 0
            ;;
    esac

    log_info "LUKHAS Health Check - $ENVIRONMENT environment"
    echo ""

    local total_failed=0

    # Run health checks based on service selection
    case "$SERVICE" in
        all)
            total_failed=$((total_failed + $(check_core_services)))
            total_failed=$((total_failed + $(check_infrastructure)))
            check_api_functionality
            check_performance
            ;;
        core|identity|memory|consciousness|governance)
            total_failed=$((total_failed + $(check_core_services)))
            ;;
        infrastructure|monitoring)
            total_failed=$((total_failed + $(check_infrastructure)))
            ;;
        *)
            log_error "Unknown service: $SERVICE"
            exit 1
            ;;
    esac

    generate_report $total_failed
}

# Check dependencies
if ! command -v curl &> /dev/null; then
    log_error "curl is required but not installed"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    log_warning "jq is not installed - JSON parsing will be limited"
fi

if ! command -v bc &> /dev/null; then
    log_warning "bc is not installed - performance timing will be limited"
fi

# Parse arguments before calling main
case "${1:-}" in
    -h|--help)
        main "$@"
        ;;
    *)
        main "$@"
        ;;
esac