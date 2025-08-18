#!/bin/bash

# LUKHAS AI - Fresh Production Deployment
# Post-deletion deployment script
# ===================================

set -e

echo "🚀 LUKHAS AI - Fresh Production Deployment"
echo "========================================="
echo "🎓 Using GitHub Student Pack resources"
echo "⚛️🧠🛡️ Trinity Framework enabled"
echo ""

# Configuration
RESOURCE_GROUP="Lukhas"
ENVIRONMENT_NAME="lukhas-ai-production-v2"
CONTAINER_APP_NAME="lukhas-ai"
LOCATION="uksouth"

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

# Step 1: Check Azure CLI and login
echo_status "1️⃣ Checking Azure CLI authentication..."
if ! az account show &>/dev/null; then
    echo_error "Not logged into Azure CLI"
    echo "Please run: az login"
    exit 1
fi
echo_success "Azure CLI authenticated"

# Step 2: Install Container Apps extension
echo_status "2️⃣ Installing/updating Azure Container Apps extension..."
az extension add --name containerapp --upgrade &>/dev/null || true
echo_success "Container Apps extension ready"

# Step 3: Create new Container Apps environment
echo_status "3️⃣ Creating fresh Container Apps environment..."
echo "   Environment: $ENVIRONMENT_NAME"
echo "   Location: $LOCATION"
echo "   Resource Group: $RESOURCE_GROUP"

az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --logs-workspace-id $(az monitor log-analytics workspace show \
        --resource-group $RESOURCE_GROUP \
        --workspace-name lukhas-dev-logs \
        --query customerId \
        --output tsv) \
    --logs-workspace-key $(az monitor log-analytics workspace get-shared-keys \
        --resource-group $RESOURCE_GROUP \
        --workspace-name lukhas-dev-logs \
        --query primarySharedKey \
        --output tsv)

echo_success "Container Apps environment created"

# Step 4: Deploy LUKHAS AI container app
echo_status "4️⃣ Deploying LUKHAS AI container app..."

az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
    --target-port 8080 \
    --ingress external \
    --cpu 1.0 \
    --memory 2Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars \
        LUKHAS_PRODUCTION=true \
        LUKHAS_API_HOST=0.0.0.0 \
        LUKHAS_API_PORT=8080 \
        LUKHAS_LOG_LEVEL=INFO \
        AZURE_OPENAI_ENDPOINT=https://lukhas.openai.azure.com/ \
        AZURE_OPENAI_API_VERSION=2024-02-15-preview \
        LUKHAS_ENABLE_CONSCIOUSNESS=true \
        LUKHAS_ENABLE_MEMORY=true \
        LUKHAS_ENABLE_DREAMS=true \
        LUKHAS_ENABLE_GOVERNANCE=true \
        LUKHAS_TRINITY_FRAMEWORK="⚛️🧠🛡️" \
        LUKHAS_SYSTEM_NAME="LUKHAS AI"

echo_success "Container app deployed"

# Step 5: Set secrets
echo_status "5️⃣ Configuring secrets..."
az containerapp secret set \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --secrets \
        azure-openai-key=2p6GG9edEDWo0G07UOAcuQX5H311Jqh3P6FUEldpdJt5ZqCOwIjLJQQJ99BFACmepeSXJ3w3AAABACOGp0v2 \
        lukhas-api-key=lukhas-production-key-2024-secure

echo_success "Secrets configured"

# Step 6: Get deployment information
echo_status "6️⃣ Getting deployment information..."
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" \
    --output tsv)

echo ""
echo "🎉 LUKHAS AI Deployment Complete!"
echo "=================================="
echo ""
echo_success "Application URL: https://$APP_URL"
echo_success "API Documentation: https://$APP_URL/docs (once updated)"
echo_success "Health Check: https://$APP_URL/"
echo ""
echo "🔗 Azure Portal Links:"
echo "   Container App: https://portal.azure.com/#@gonzodominguezicloud.onmicrosoft.com/resource/subscriptions/655855d4-df7b-44af-aedc-8169e7e34144/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME"
echo "   Environment: https://portal.azure.com/#@gonzodominguezicloud.onmicrosoft.com/resource/subscriptions/655855d4-df7b-44af-aedc-8169e7e34144/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/managedEnvironments/$ENVIRONMENT_NAME"
echo ""
echo "📋 Next Steps:"
echo "   1. ✅ Environment created"
echo "   2. ✅ Container app deployed"
echo "   3. 🔄 Update to LUKHAS AI image (via VS Code or Azure CLI)"
echo "   4. 🔑 Set OpenAI API key (if using regular OpenAI)"
echo "   5. 📊 Set up NewRelic monitoring ($300/month from Student Pack)"
echo ""
echo_warning "Current image is placeholder - update with LUKHAS AI image next"