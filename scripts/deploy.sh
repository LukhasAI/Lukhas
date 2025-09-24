#!/bin/bash

# LUKHAS Deployment Automation Script
# Usage: ./scripts/deploy.sh [environment] [component]
# Example: ./scripts/deploy.sh production all

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment"

# Default values
ENVIRONMENT="${1:-staging}"
COMPONENT="${2:-all}"
REGISTRY="ghcr.io"
IMAGE_NAME="lukhas"
DOCKER_COMPOSE_FILE="$DEPLOYMENT_DIR/docker-compose.$ENVIRONMENT.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Validation functions
validate_environment() {
    case "$ENVIRONMENT" in
        staging|production)
            log_info "Deploying to $ENVIRONMENT environment"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
            exit 1
            ;;
    esac
}

validate_prerequisites() {
    log_info "Validating prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check if logged into registry
    if ! docker info | grep -q "Registry"; then
        log_warning "Not logged into container registry. Attempting login..."
        if ! docker login "$REGISTRY"; then
            log_error "Failed to login to container registry"
            exit 1
        fi
    fi

    # Check Docker Compose file exists
    if [[ ! -f "$DOCKER_COMPOSE_FILE" ]]; then
        log_error "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        exit 1
    fi

    log_success "Prerequisites validated"
}

# Backup functions
backup_database() {
    log_info "Creating database backup..."

    local backup_dir="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # Get database credentials from environment file
    local env_file="$DEPLOYMENT_DIR/.env.$ENVIRONMENT"
    if [[ -f "$env_file" ]]; then
        source "$env_file"
    fi

    # Create PostgreSQL backup
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_dump \
        -U "${POSTGRES_USER:-lukhas}" \
        -d "${POSTGRES_DB:-lukhas}" \
        > "$backup_dir/postgres_backup.sql"

    # Create Redis backup
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T redis redis-cli BGSAVE

    log_success "Database backup created: $backup_dir"
    echo "$backup_dir" > /tmp/lukhas_backup_path
}

# Health check functions
health_check() {
    local service="$1"
    local max_attempts="${2:-30}"
    local attempt=1

    log_info "Health checking $service..."

    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T "$service" curl -f http://localhost:8080/health &>/dev/null; then
            log_success "$service is healthy"
            return 0
        fi

        log_info "Attempt $attempt/$max_attempts failed, waiting 10s..."
        sleep 10
        ((attempt++))
    done

    log_error "$service failed health check after $max_attempts attempts"
    return 1
}

# Deployment functions
deploy_infrastructure() {
    log_info "Deploying infrastructure services..."

    # Start infrastructure services first
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d \
        postgres redis nginx prometheus grafana alertmanager jaeger loki

    # Wait for infrastructure to be ready
    sleep 30

    # Verify infrastructure health
    local infra_services=("postgres" "redis")
    for service in "${infra_services[@]}"; do
        if ! docker-compose -f "$DOCKER_COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            log_error "Infrastructure service $service failed to start"
            return 1
        fi
    done

    log_success "Infrastructure services deployed successfully"
}

deploy_lukhas_services() {
    log_info "Deploying LUKHAS application services..."

    # Pull latest images
    docker-compose -f "$DOCKER_COMPOSE_FILE" pull lukhas-core lukhas-identity lukhas-memory lukhas-consciousness lukhas-governance

    # Deploy services with rolling update
    local services=("lukhas-core" "lukhas-identity" "lukhas-memory" "lukhas-consciousness" "lukhas-governance")

    for service in "${services[@]}"; do
        if [[ "$COMPONENT" != "all" && "$COMPONENT" != "$service" ]]; then
            continue
        fi

        log_info "Deploying $service..."

        # Scale up new instance
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --scale "$service"=2 "$service"

        # Wait for new instance to be healthy
        if health_check "$service" 30; then
            # Scale down old instance
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --scale "$service"=1 "$service"
            log_success "$service deployed successfully"
        else
            log_error "$service deployment failed"
            # Rollback
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --scale "$service"=1 "$service"
            return 1
        fi
    done

    log_success "LUKHAS services deployed successfully"
}

# Smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."

    local base_url
    case "$ENVIRONMENT" in
        staging)
            base_url="https://staging.lukhas.ai"
            ;;
        production)
            base_url="https://lukhas.ai"
            ;;
    esac

    # Test core endpoints
    local endpoints=(
        "$base_url/health"
        "$base_url/api/v1/identity/health"
        "$base_url/api/v1/memory/health"
        "$base_url/api/v1/consciousness/health"
        "$base_url/api/v1/governance/health"
    )

    for endpoint in "${endpoints[@]}"; do
        if curl -f -s "$endpoint" > /dev/null; then
            log_success "✓ $endpoint"
        else
            log_error "✗ $endpoint"
            return 1
        fi
    done

    # Run comprehensive smoke test suite
    if [[ -f "$PROJECT_ROOT/tests/smoke/${ENVIRONMENT}_smoke_tests.py" ]]; then
        cd "$PROJECT_ROOT"
        python "tests/smoke/${ENVIRONMENT}_smoke_tests.py"
    fi

    log_success "Smoke tests passed"
}

# Monitoring setup
configure_monitoring() {
    log_info "Configuring monitoring and alerting..."

    # Ensure monitoring services are running
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d prometheus grafana alertmanager

    # Wait for Prometheus to be ready
    local attempt=1
    while [[ $attempt -le 30 ]]; do
        if curl -f -s http://localhost:9090/api/v1/status/config > /dev/null; then
            break
        fi
        sleep 5
        ((attempt++))
    done

    # Import Grafana dashboards
    local dashboards_dir="$DEPLOYMENT_DIR/grafana/dashboards"
    if [[ -d "$dashboards_dir" ]]; then
        for dashboard in "$dashboards_dir"/*.json; do
            log_info "Importing dashboard: $(basename "$dashboard")"
            curl -X POST \
                -H "Content-Type: application/json" \
                -d @"$dashboard" \
                "http://admin:admin@localhost:3000/api/dashboards/db" || true
        done
    fi

    log_success "Monitoring configured"
}

# Cleanup functions
cleanup_old_images() {
    log_info "Cleaning up old Docker images..."

    # Remove unused images older than 24 hours
    docker image prune -f --filter "until=24h"

    # Remove old LUKHAS images (keep last 3 versions)
    docker images "$REGISTRY/$IMAGE_NAME" --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | \
        tail -n +4 | \
        awk '{print $1}' | \
        xargs -r docker rmi || true

    log_success "Cleanup completed"
}

# Rollback function
rollback() {
    local backup_path
    if [[ -f /tmp/lukhas_backup_path ]]; then
        backup_path=$(cat /tmp/lukhas_backup_path)
    fi

    log_warning "Rolling back deployment..."

    # Stop current services
    docker-compose -f "$DOCKER_COMPOSE_FILE" down

    # Restore from backup if available
    if [[ -n "$backup_path" && -d "$backup_path" ]]; then
        log_info "Restoring from backup: $backup_path"

        # Restore database
        if [[ -f "$backup_path/postgres_backup.sql" ]]; then
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d postgres
            sleep 10
            docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres psql \
                -U "${POSTGRES_USER:-lukhas}" \
                -d "${POSTGRES_DB:-lukhas}" \
                < "$backup_path/postgres_backup.sql"
        fi
    fi

    # Start services with previous configuration
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

    log_success "Rollback completed"
}

# Main deployment function
main() {
    log_info "Starting LUKHAS deployment to $ENVIRONMENT"

    # Trap for cleanup on error
    trap 'log_error "Deployment failed. Rolling back..."; rollback; exit 1' ERR

    validate_environment
    validate_prerequisites

    # Create backup before deployment
    if [[ "$ENVIRONMENT" == "production" ]]; then
        backup_database
    fi

    # Deploy infrastructure first
    deploy_infrastructure

    # Deploy LUKHAS services
    deploy_lukhas_services

    # Configure monitoring
    configure_monitoring

    # Run smoke tests
    run_smoke_tests

    # Cleanup
    cleanup_old_images

    log_success "🚀 LUKHAS deployment to $ENVIRONMENT completed successfully!"

    # Show deployment summary
    echo ""
    echo "=== Deployment Summary ==="
    echo "Environment: $ENVIRONMENT"
    echo "Component: $COMPONENT"
    echo "Timestamp: $(date)"
    echo "Services:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    echo ""
    echo "Monitoring URLs:"
    case "$ENVIRONMENT" in
        staging)
            echo "  Application: https://staging.lukhas.ai"
            echo "  Grafana: https://monitoring-staging.lukhas.ai"
            ;;
        production)
            echo "  Application: https://lukhas.ai"
            echo "  Grafana: https://monitoring.lukhas.ai"
            ;;
    esac
}

# Help function
show_help() {
    echo "LUKHAS Deployment Script"
    echo ""
    echo "Usage: $0 [environment] [component]"
    echo ""
    echo "Environments:"
    echo "  staging     Deploy to staging environment"
    echo "  production  Deploy to production environment"
    echo ""
    echo "Components:"
    echo "  all                  Deploy all services (default)"
    echo "  lukhas-core         Deploy core service only"
    echo "  lukhas-identity     Deploy identity service only"
    echo "  lukhas-memory       Deploy memory service only"
    echo "  lukhas-consciousness Deploy consciousness service only"
    echo "  lukhas-governance   Deploy governance service only"
    echo ""
    echo "Examples:"
    echo "  $0 staging all"
    echo "  $0 production lukhas-identity"
    echo "  $0 staging"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac