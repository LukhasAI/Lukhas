#!/bin/bash

# LUKHAS AI - Production Deployment Script
# ========================================

set -e

# Configuration
RESOURCE_GROUP="Lukhas"
CONTAINER_APP_NAME="lukhas-ai"
ACR_NAME="lukhasai"
IMAGE_NAME="lukhas-ai"
LOCATION="uksouth"
DOCKERFILE="deployment/docker/Dockerfile.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_status() {
    echo -e "${BLUE}$1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get image tag
IMAGE_TAG="$ACR_NAME.azurecr.io/$IMAGE_NAME:$(git rev-parse --short HEAD)"

# Step 1: Check Azure CLI and login
echo_status "1️⃣ Checking Azure CLI authentication..."
if ! az account show &>/dev/null; then
    echo_error "Not logged into Azure CLI"
    echo "Please run: az login"
    exit 1
fi
echo_success "Azure CLI authenticated"

# Step 2: Build and push Docker image
echo_status "2️⃣ Building and pushing Docker image..."
echo "   Image: $IMAGE_TAG"
docker build -t "$IMAGE_TAG" -f "$DOCKERFILE" .
az acr login --name "$ACR_NAME"
docker push "$IMAGE_TAG"
echo_success "Image pushed to ACR"

# Step 3: Deploy to Azure Container Apps
echo_status "3️⃣ Deploying to Azure Container Apps..."
az containerapp update \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --image "$IMAGE_TAG" \
    --revision-suffix "$(git rev-parse --short HEAD)"
echo_success "Container app updated"

# Step 4: Run smoke tests
echo_status "4️⃣ Running smoke tests..."
APP_URL=$(az containerapp show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.configuration.ingress.fqdn" -o tsv)
sleep 60
curl -f "https://$APP_URL/health" || (echo_error "Health check failed" && exit 1)
curl -f "https://$APP_URL/api/guardian/status" || (echo_error "Guardian status check failed" && exit 1)
echo_success "Smoke tests passed"

echo ""
echo "🎉 LUKHAS AI Deployment Complete!"
echo "=================================="
echo ""
echo_success "Application URL: https://$APP_URL"
echo ""
