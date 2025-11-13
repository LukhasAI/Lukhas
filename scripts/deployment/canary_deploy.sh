#!/bin/bash

# Canary Deployment Script for LUKHAS AI
# This script manages a gradual rollout to a canary revision in Azure Container Apps.

set -eo pipefail

# Configuration
# These variables are expected to be set in the GitHub Actions environment
# RESOURCE_GROUP="Lukhas"
# CONTAINER_APP_NAME="lukhas-ai"
# ACR_NAME="lukhasai"
# IMAGE_TAG - The new image tag to deploy

# Traffic percentages for gradual rollout
TRAFFIC_STAGES=(10 25 50 100)

# Health check configuration
HEALTH_CHECK_ENDPOINT="/health"
HEALTH_CHECK_INTERVAL=30 # seconds
HEALTH_CHECK_RETRIES=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to get the URL of the container app
get_app_url() {
    az containerapp show \
        --name "$CONTAINER_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "properties.configuration.ingress.fqdn" \
        -o tsv
}

# Function to perform a health check on a revision
health_check() {
    local revision_url="$1"
    local revision_name="$2"
    log_info "Performing health check on revision '$revision_name' at https://$revision_url$HEALTH_CHECK_ENDPOINT..."

    for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
        local response_code=$(curl -s -o /dev/null -w "%{http_code}" "https://$revision_url$HEALTH_CHECK_ENDPOINT")
        if [ "$response_code" == "200" ]; then
            log_success "Health check passed for revision '$revision_name'."
            return 0
        fi
        log_warning "Health check attempt $i/$HEALTH_CHECK_RETRIES failed for revision '$revision_name' (HTTP code: $response_code). Retrying in $HEALTH_CHECK_INTERVAL seconds..."
        sleep "$HEALTH_CHECK_INTERVAL"
    done

    log_error "Health check failed for revision '$revision_name' after $HEALTH_CHECK_RETRIES attempts."
    return 1
}

# Function to roll back to the stable revision
rollback() {
    log_warning "Rolling back deployment..."
    # Find the revision that is not the canary and has traffic > 0. This is the stable revision.
    local stable_revision=$(az containerapp revision list -n "$CONTAINER_APP_NAME" -g "$RESOURCE_GROUP" --query "[?name!='$canary_revision_name' && trafficWeight > \`0\`].name" -o tsv)

    if [ -z "$stable_revision" ]; then
        log_error "Could not find a stable revision to roll back to. Deactivating canary."
        az containerapp revision deactivate --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" --revision "$canary_revision_name"
        exit 1
    fi

    log_info "Rolling back to stable revision: $stable_revision"
    az containerapp ingress traffic set \
        --name "$CONTAINER_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --revision-weights "$stable_revision=100"

    log_success "Rollback complete. All traffic is now directed to revision '$stable_revision'."

    log_info "Deactivating failed canary revision: $canary_revision_name"
    az containerapp revision deactivate --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" --revision "$canary_revision_name"

    exit 1
}

# Main deployment logic
main() {
    log_info "Starting canary deployment for image: $ACR_NAME.azurecr.io/lukhas-ai:$IMAGE_TAG"

    # Get the canary revision name by matching the image tag
    log_info "Looking for revision with image: $ACR_NAME.azurecr.io/lukhas-ai:$IMAGE_TAG"
    local canary_revision_name=$(az containerapp revision list -n "$CONTAINER_APP_NAME" -g "$RESOURCE_GROUP" --query "[?template.containers[0].image=='$ACR_NAME.azurecr.io/lukhas-ai:$IMAGE_TAG'].name" -o tsv)
    if [ -z "$canary_revision_name" ]; then
        log_error "Failed to find a revision with the image tag: $IMAGE_TAG"
        exit 1
    fi
    log_info "Canary revision identified as: $canary_revision_name"

    # Get the stable revision name
    local stable_revision_name=$(az containerapp revision list -n "$CONTAINER_APP_NAME" -g "$RESOURCE_GROUP" --query "[?trafficWeight==`100`].name" -o tsv)

    # Get the canary revision URL
    local app_url=$(get_app_url)
    local canary_revision_url="$canary_revision_name.$app_url"

    # Handle initial deployment (no stable revision)
    if [ -z "$stable_revision_name" ]; then
        log_warning "No stable revision found. This appears to be an initial deployment."
        log_info "Performing health check on new revision '$canary_revision_name'..."
        if ! health_check "$canary_revision_url" "$canary_revision_name"; then
            log_error "Initial deployment health check failed. Deactivating revision."
            az containerapp revision deactivate --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" --revision "$canary_revision_name"
            exit 1
        fi

        log_info "Health check passed. Setting traffic to 100% for '$canary_revision_name'."
        az containerapp ingress traffic set \
            --name "$CONTAINER_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --revision-weights "$canary_revision_name=100"

        log_success "Initial deployment successful. 100% of traffic is now on revision '$canary_revision_name'."
        exit 0
    fi

    log_info "Stable revision identified as: $stable_revision_name"

    # If canary is already stable, no action needed
    if [ "$stable_revision_name" == "$canary_revision_name" ]; then
        log_warning "The new image is already deployed and stable. No traffic shift needed."
        exit 0
    fi

    # Perform an initial health check on the canary revision before shifting traffic
    if ! health_check "$canary_revision_url" "$canary_revision_name"; then
        rollback
    fi

    # Gradual traffic rollout
    for stage in "${TRAFFIC_STAGES[@]}"; do
        log_info "Shifting ${stage}% of traffic to canary revision '$canary_revision_name'..."
        az containerapp ingress traffic set \
            --name "$CONTAINER_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --revision-weights "$stable_revision_name=$((100 - stage))" "$canary_revision_name=$stage"

        log_info "Waiting for traffic to stabilize..."
        sleep 60

        log_info "Performing health checks after shifting traffic..."
        if ! health_check "$canary_revision_url" "$canary_revision_name"; then
            rollback
        fi
        log_success "Canary revision is healthy with ${stage}% of traffic."
    done

    log_success "Canary deployment successful. 100% of traffic is now on revision '$canary_revision_name'."
}

# Execute the main function
main
