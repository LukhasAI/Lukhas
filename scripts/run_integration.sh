#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Integration test runner with Docker services
# Spins up postgres, redis, and minio, then runs integration tests

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/devtools/docker-compose.integration.yml"
RESULTS_DIR="${PROJECT_ROOT}/release_artifacts"
RESULTS_FILE="${RESULTS_DIR}/test_results_integration.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Cleanup function to stop and remove containers
cleanup() {
    log_info "Cleaning up Docker containers..."
    docker-compose -f "${COMPOSE_FILE}" down -v --remove-orphans 2>/dev/null || true
    log_success "Cleanup complete"
}

# Register cleanup on exit
trap cleanup EXIT INT TERM

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running"
    exit 1
fi

log_info "Starting Docker services for integration tests..."
docker-compose -f "${COMPOSE_FILE}" up -d

log_info "Waiting for services to be healthy..."

# Wait for PostgreSQL
log_info "Waiting for PostgreSQL..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose -f "${COMPOSE_FILE}" exec -T postgres pg_isready -U lukhas_test -d lukhas_integration &>/dev/null; then
        log_success "PostgreSQL is ready"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    log_error "PostgreSQL failed to become ready in ${timeout}s"
    exit 1
fi

# Wait for Redis
log_info "Waiting for Redis..."
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose -f "${COMPOSE_FILE}" exec -T redis redis-cli ping &>/dev/null; then
        log_success "Redis is ready"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    log_error "Redis failed to become ready in ${timeout}s"
    exit 1
fi

# Wait for MinIO
log_info "Waiting for MinIO..."
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if curl -sf http://localhost:9000/minio/health/live &>/dev/null; then
        log_success "MinIO is ready"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    log_error "MinIO failed to become ready in ${timeout}s"
    exit 1
fi

log_success "All services are healthy and ready"

# Export connection environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=lukhas_test
export POSTGRES_PASSWORD=lukhas_test_pass
export POSTGRES_DB=lukhas_integration
export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_URL="redis://${REDIS_HOST}:${REDIS_PORT}/0"

export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=lukhas_minio
export MINIO_SECRET_KEY=lukhas_minio_pass
export MINIO_BUCKET=lukhas-integration
export MINIO_USE_SSL=false

log_info "Environment variables exported:"
log_info "  DATABASE_URL=${DATABASE_URL}"
log_info "  REDIS_URL=${REDIS_URL}"
log_info "  MINIO_ENDPOINT=${MINIO_ENDPOINT}"

# Create results directory if it doesn't exist
mkdir -p "${RESULTS_DIR}"

# Run integration tests
log_info "Running integration tests..."
cd "${PROJECT_ROOT}"

set +e  # Don't exit on pytest failure, we want to capture results
PYTHONPATH="${PROJECT_ROOT}" python3 -m pytest tests/integration/ -v --tb=short 2>&1 | tee "${RESULTS_FILE}"
TEST_EXIT_CODE=${PIPESTATUS[0]}
set -e

# Check test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    log_success "Integration tests passed!"
    echo ""
    log_info "Test results saved to: ${RESULTS_FILE}"
    exit 0
else
    log_error "Integration tests failed with exit code ${TEST_EXIT_CODE}"
    echo ""
    log_info "Test results saved to: ${RESULTS_FILE}"
    exit ${TEST_EXIT_CODE}
fi
