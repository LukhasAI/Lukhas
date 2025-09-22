#!/bin/bash

"""
MATRIZ Orchestrator Canary Deployment Script

Manages canary deployments with automated traffic splitting and health validation.

Usage:
    ./deployment/canary/deploy-canary.sh [command] [options]

Commands:
    start           Start canary deployment
    promote         Promote canary to stable
    rollback        Rollback to stable version
    status          Show deployment status
    cleanup         Clean up canary resources

Options:
    --image=TAG             Docker image tag for canary (default: latest)
    --traffic=PERCENTAGE    Initial traffic percentage (default: 10)
    --platform=TYPE         Deployment platform: k8s|docker (default: k8s)
    --monitoring            Enable comprehensive monitoring
    --dry-run              Show what would be deployed without executing

Examples:
    ./deploy-canary.sh start --image=v2.1.0 --traffic=5
    ./deploy-canary.sh promote
    ./deploy-canary.sh rollback --platform=docker
"""

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Default values
CANARY_IMAGE_TAG="latest"
TRAFFIC_PERCENTAGE=10
DEPLOYMENT_PLATFORM="k8s"
ENABLE_MONITORING=false
DRY_RUN=false
NAMESPACE="lukhas-ai"

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

# Parse command line arguments
parse_args() {
    COMMAND="${1:-status}"
    shift || true

    while [[ $# -gt 0 ]]; do
        case $1 in
            --image=*)
                CANARY_IMAGE_TAG="${1#*=}"
                shift
                ;;
            --traffic=*)
                TRAFFIC_PERCENTAGE="${1#*=}"
                shift
                ;;
            --platform=*)
                DEPLOYMENT_PLATFORM="${1#*=}"
                shift
                ;;
            --monitoring)
                ENABLE_MONITORING=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

# Validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."

    if [[ "$DEPLOYMENT_PLATFORM" == "k8s" ]]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl not found. Please install Kubernetes CLI."
            exit 1
        fi

        if ! command -v argocd &> /dev/null; then
            log_warning "ArgoCD CLI not found. Some features may be limited."
        fi

        # Check cluster connection
        if ! kubectl cluster-info &> /dev/null; then
            log_error "Cannot connect to Kubernetes cluster."
            exit 1
        fi
    elif [[ "$DEPLOYMENT_PLATFORM" == "docker" ]]; then
        if ! command -v docker &> /dev/null; then
            log_error "Docker not found. Please install Docker."
            exit 1
        fi

        if ! command -v docker-compose &> /dev/null; then
            log_error "docker-compose not found. Please install Docker Compose."
            exit 1
        fi
    fi

    log_success "Prerequisites validated"
}

# Start canary deployment
start_canary() {
    log_info "Starting MATRIZ Orchestrator canary deployment..."
    log_info "Image: ghcr.io/lukhasai/matriz-orchestrator:${CANARY_IMAGE_TAG}"
    log_info "Initial traffic: ${TRAFFIC_PERCENTAGE}%"
    log_info "Platform: ${DEPLOYMENT_PLATFORM}"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "DRY RUN MODE - No changes will be applied"
    fi

    if [[ "$DEPLOYMENT_PLATFORM" == "k8s" ]]; then
        start_k8s_canary
    elif [[ "$DEPLOYMENT_PLATFORM" == "docker" ]]; then
        start_docker_canary
    fi
}

# Kubernetes canary deployment
start_k8s_canary() {
    log_info "Deploying to Kubernetes cluster..."

    # Update image tag in deployment manifest
    local temp_manifest="/tmp/matriz-canary-deployment.yaml"
    sed "s|ghcr.io/lukhasai/matriz-orchestrator:latest|ghcr.io/lukhasai/matriz-orchestrator:${CANARY_IMAGE_TAG}|g" \
        "${SCRIPT_DIR}/matriz-canary-deployment.yaml" > "$temp_manifest"

    if [[ "$DRY_RUN" == "false" ]]; then
        # Apply the rollout configuration
        kubectl apply -f "$temp_manifest"

        # Wait for rollout to be available
        log_info "Waiting for canary rollout to be ready..."
        kubectl rollout status rollout/lukhas-matriz-orchestrator -n "$NAMESPACE" --timeout=300s

        # Set initial traffic weight
        kubectl argo rollouts set image lukhas-matriz-orchestrator \
            matriz-orchestrator="ghcr.io/lukhasai/matriz-orchestrator:${CANARY_IMAGE_TAG}" \
            -n "$NAMESPACE"

        log_success "Canary deployment started successfully"
        show_k8s_status
    else
        log_info "Would apply: $temp_manifest"
        log_info "Would set traffic to ${TRAFFIC_PERCENTAGE}%"
    fi

    rm -f "$temp_manifest"
}

# Docker canary deployment
start_docker_canary() {
    log_info "Deploying with Docker Compose..."

    # Set environment variables for docker-compose
    export CANARY_IMAGE_TAG
    export CANARY_TRAFFIC_PERCENTAGE=$TRAFFIC_PERCENTAGE

    if [[ "$DRY_RUN" == "false" ]]; then
        # Start canary services
        docker-compose -f "${SCRIPT_DIR}/docker-compose.canary.yml" up -d matriz-orchestrator-canary

        # Wait for health check
        log_info "Waiting for canary service to be healthy..."
        local max_attempts=30
        local attempt=0

        while [[ $attempt -lt $max_attempts ]]; do
            if docker-compose -f "${SCRIPT_DIR}/docker-compose.canary.yml" ps matriz-orchestrator-canary | grep -q "healthy"; then
                log_success "Canary service is healthy"
                break
            fi

            attempt=$((attempt + 1))
            log_info "Health check attempt $attempt/$max_attempts..."
            sleep 10
        done

        if [[ $attempt -eq $max_attempts ]]; then
            log_error "Canary service failed to become healthy"
            exit 1
        fi

        log_success "Canary deployment started successfully"
        show_docker_status
    else
        log_info "Would start: matriz-orchestrator-canary"
        log_info "Would configure traffic: ${TRAFFIC_PERCENTAGE}%"
    fi
}

# Promote canary to stable
promote_canary() {
    log_info "Promoting canary to stable..."

    if [[ "$DEPLOYMENT_PLATFORM" == "k8s" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            kubectl argo rollouts promote lukhas-matriz-orchestrator -n "$NAMESPACE"
            kubectl rollout status rollout/lukhas-matriz-orchestrator -n "$NAMESPACE" --timeout=300s
            log_success "Canary promoted to stable successfully"
        else
            log_info "Would promote canary to stable"
        fi
    elif [[ "$DEPLOYMENT_PLATFORM" == "docker" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            # Update stable service with canary image
            docker tag "ghcr.io/lukhasai/matriz-orchestrator:${CANARY_IMAGE_TAG}" \
                      "ghcr.io/lukhasai/matriz-orchestrator:stable"

            # Restart stable service with new image
            docker-compose -f "${SCRIPT_DIR}/docker-compose.canary.yml" up -d matriz-orchestrator-stable

            log_success "Canary promoted to stable successfully"
        else
            log_info "Would promote canary to stable"
        fi
    fi
}

# Rollback to stable version
rollback_canary() {
    log_info "Rolling back canary deployment..."

    if [[ "$DEPLOYMENT_PLATFORM" == "k8s" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            kubectl argo rollouts abort lukhas-matriz-orchestrator -n "$NAMESPACE"
            kubectl rollout status rollout/lukhas-matriz-orchestrator -n "$NAMESPACE" --timeout=300s
            log_success "Canary deployment rolled back successfully"
        else
            log_info "Would rollback canary deployment"
        fi
    elif [[ "$DEPLOYMENT_PLATFORM" == "docker" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            # Stop canary service
            docker-compose -f "${SCRIPT_DIR}/docker-compose.canary.yml" stop matriz-orchestrator-canary
            docker-compose -f "${SCRIPT_DIR}/docker-compose.canary.yml" rm -f matriz-orchestrator-canary

            log_success "Canary deployment rolled back successfully"
        else
            log_info "Would stop and remove canary service"
        fi
    fi
}

# Show deployment status
show_status() {
    log_info "MATRIZ Orchestrator Canary Deployment Status"
    echo "========================================="

    if [[ "$DEPLOYMENT_PLATFORM" == "k8s" ]]; then
        show_k8s_status
    elif [[ "$DEPLOYMENT_PLATFORM" == "docker" ]]; then
        show_docker_status
    fi
}

# Show Kubernetes status
show_k8s_status() {
    echo ""
    log_info "Kubernetes Rollout Status:"
    kubectl get rollout lukhas-matriz-orchestrator -n "$NAMESPACE" 2>/dev/null || log_warning "No rollout found"

    echo ""
    log_info "Pod Status:"
    kubectl get pods -l app=lukhas-matriz -n "$NAMESPACE" 2>/dev/null || log_warning "No pods found"

    echo ""
    log_info "Service Status:"
    kubectl get svc -l app=lukhas-matriz -n "$NAMESPACE" 2>/dev/null || log_warning "No services found"

    if command -v kubectl argo &> /dev/null; then
        echo ""
        log_info "Traffic Distribution:"
        kubectl argo rollouts get rollout lukhas-matriz-orchestrator -n "$NAMESPACE" 2>/dev/null || log_warning "ArgoCD rollout not found"
    fi
}

# Show Docker status
show_docker_status() {
    echo ""
    log_info "Container Status:"
    docker-compose -f "${SCRIPT_DIR}/docker-compose.canary.yml" ps

    echo ""
    log_info "Health Status:"
    docker-compose -f "${SCRIPT_DIR}/docker-compose.canary.yml" ps --services | while read service; do
        health=$(docker inspect --format='{{.State.Health.Status}}' "${service}" 2>/dev/null || echo "unknown")
        echo "  $service: $health"
    done

    echo ""
    log_info "Traffic Configuration:"
    echo "  Stable: 90%"
    echo "  Canary: ${TRAFFIC_PERCENTAGE:-10}%"
}

# Cleanup canary resources
cleanup_canary() {
    log_info "Cleaning up canary deployment resources..."

    if [[ "$DEPLOYMENT_PLATFORM" == "k8s" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            kubectl delete rollout lukhas-matriz-orchestrator -n "$NAMESPACE" --ignore-not-found=true
            kubectl delete svc lukhas-matriz-canary lukhas-matriz-stable -n "$NAMESPACE" --ignore-not-found=true
            kubectl delete analysistemplate matriz-success-rate matriz-latency-p95 matriz-error-rate matriz-comprehensive-health -n "$NAMESPACE" --ignore-not-found=true
            log_success "Kubernetes resources cleaned up"
        else
            log_info "Would delete canary Kubernetes resources"
        fi
    elif [[ "$DEPLOYMENT_PLATFORM" == "docker" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            docker-compose -f "${SCRIPT_DIR}/docker-compose.canary.yml" down --volumes
            log_success "Docker resources cleaned up"
        else
            log_info "Would stop and remove Docker resources"
        fi
    fi
}

# Enable monitoring integrations
setup_monitoring() {
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        log_info "Setting up comprehensive monitoring..."

        # Apply monitoring configurations
        if [[ "$DEPLOYMENT_PLATFORM" == "k8s" && "$DRY_RUN" == "false" ]]; then
            kubectl apply -f "${PROJECT_ROOT}/monitoring/prometheus-config.yml" -n "$NAMESPACE"
            kubectl apply -f "${PROJECT_ROOT}/monitoring/alert-rules.yml" -n "$NAMESPACE"
        fi

        log_success "Monitoring configured"
    fi
}

# Main execution
main() {
    echo "🚀 MATRIZ Orchestrator Canary Deployment Manager"
    echo "================================================"

    parse_args "$@"
    validate_prerequisites
    setup_monitoring

    case "$COMMAND" in
        "start")
            start_canary
            ;;
        "promote")
            promote_canary
            ;;
        "rollback")
            rollback_canary
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            cleanup_canary
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            log_info "Available commands: start, promote, rollback, status, cleanup"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"