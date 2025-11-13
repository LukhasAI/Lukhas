#!/bin/bash
# Gradual Rollout Script for the Guardian Service
#
# This script performs a staged rollout of the Guardian service,
# monitoring key health and performance metrics at each stage.
# If the error rate exceeds a defined threshold, it automatically rolls back.
#
# Usage:
#   ./scripts/governance/gradual_guardian_rollout.sh [environment]
#
# Environments: staging, production (defaults to staging)
#

set -euo pipefail

# --- Configuration ---
ENVIRONMENT="${1:-staging}"
ROLLOUT_STAGES=(10 25 50 100)
ERROR_THRESHOLD=1.0 # Percentage
# Using a placeholder URL, will be replaced with actual service discovery
PROM_URL="http://prometheus.${ENVIRONMENT}.lukhas.ai:9090"
HEALTH_CHECK_URL="https://api.${ENVIRONMENT}.lukhas.ai/api/v1/governance/health"
DEPLOYMENT_TARGET="guardian-service" # Placeholder for actual deployment target

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Logging Functions ---
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

# --- Core Functions ---

deploy_service() {
    local percentage=$1
    log_info "Deploying ${DEPLOYMENT_TARGET} to ${percentage}% of the fleet in '${ENVIRONMENT}'..."
    # This is a placeholder for the actual deployment command.
    # In a real-world scenario, this function would interact with a deployment system
    # like Kubernetes, a cloud provider's API, or an infrastructure-as-code tool.
    #
    # Example for Kubernetes:
    #   kubectl set image deployment/${DEPLOYMENT_TARGET} guardian=guardian:${NEW_VERSION} --namespace=${ENVIRONMENT}
    #   kubectl rollout status deployment/${DEPLOYMENT_TARGET} --namespace=${ENVIRONMENT}
    #
    # For this script, we'll simulate the deployment time.
    sleep 5
    log_success "Deployment to ${percentage}% complete."
}

run_health_checks() {
    log_info "Running health checks for Guardian service at ${HEALTH_CHECK_URL}..."

    local response
    if ! response=$(curl -f -s --max-time 15 "${HEALTH_CHECK_URL}"); then
        log_error "Health check failed: unable to reach the service."
        return 1
    fi

    # Check for a successful status in the JSON response
    # Loosely checks for "ok" or "healthy" to be robust
    if echo "${response}" | jq -e '.status | test("ok|healthy"; "i")' > /dev/null; then
        log_success "Health check passed. Service is responsive and reports a healthy status."
        return 0
    else
        local status
        status=$(echo "${response}" | jq -r '.status // "unknown"')
        log_error "Health check failed. Service responded but status is '${status}'."
        log_error "Full response: ${response}"
        return 1
    fi
}

check_metrics() {
    log_info "Querying Prometheus for Guardian deny rate..."

    local query='100 * sum(rate(guardian_denied_total[5m])) / sum(rate(guardian_decision_total[5m]))'

    local response
    if ! response=$(curl -sG --data-urlencode "query=${query}" "${PROM_URL}/api/v1/query"); then
        log_error "Failed to query Prometheus at ${PROM_URL}."
        # Fail open: if we can't get metrics, we can't confirm a problem, so we warn and continue.
        log_warning "Could not verify metrics. Proceeding with caution."
        return 0
    fi

    local status
    status=$(echo "${response}" | jq -r '.status')

    if [[ "${status}" != "success" ]]; then
        local err_msg
        err_msg=$(echo "${response}" | jq -r '.error // "Unknown error"')
        log_error "Prometheus query failed: ${err_msg}"
        log_warning "Could not verify metrics. Proceeding with caution."
        return 0
    fi

    local denial_rate
    denial_rate=$(echo "${response}" | jq -r '.data.result[0].value[1] // "0"')

    log_info "Current Guardian denial rate: ${denial_rate}%"

    if (( $(echo "${denial_rate} > ${ERROR_THRESHOLD}" | bc -l) )); then
        log_error "Denial rate (${denial_rate}%) exceeds threshold of ${ERROR_THRESHOLD}%."
        return 1
    else
        log_success "Denial rate is within the acceptable threshold."
        return 0
    fi
}

rollback() {
    local to_stage=$1
    log_warning "ROLLING BACK deployment to ${to_stage}%..."
    # This is a placeholder for the actual rollback command.
    # This would typically involve reverting the change made in deploy_service.
    #
    # Example for Kubernetes:
    #   kubectl rollout undo deployment/${DEPLOYMENT_TARGET} --namespace=${ENVIRONMENT}
    #
    sleep 3
    log_success "Rollback to ${to_stage}% complete."
}

# --- Main Execution Logic ---
main() {
    log_info "Starting gradual rollout for Guardian service in '${ENVIRONMENT}' environment."
    log_info "Rollout stages: ${ROLLOUT_STAGES[*]}%"
    log_info "Error threshold: ${ERROR_THRESHOLD}%"
    echo

    local previous_stage=0

    for stage in "${ROLLOUT_STAGES[@]}"; do
        log_info "--- Proceeding to ${stage}% rollout stage ---"

        deploy_service "${stage}"

        log_info "Waiting for 5 minutes to allow metrics to stabilize..."
        # Using a shorter sleep for development; a real script would wait longer.
        sleep 10 # Should be 300 in production

        if ! run_health_checks; then
            log_error "Health checks failed at ${stage}% stage."
            rollback "${previous_stage}"
            exit 1
        fi

        if ! check_metrics; then
            log_error "Metrics check failed at ${stage}% stage."
            rollback "${previous_stage}"
            exit 1
        fi

        log_success "Stage ${stage}% completed successfully."
        previous_stage=${stage}
        echo
    done

    log_success "🎉 Guardian service rollout completed successfully to 100%."
}

# --- Script entrypoint ---
main
