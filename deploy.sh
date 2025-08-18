#!/bin/bash

# LUKHAS AI - Quick Azure Container Apps Deployment
# GitHub Student Pack Ready

echo "🚀 Deploying LUKHAS AI to Azure Container Apps..."
echo "Using your existing Azure for Students resources"
echo ""

# Build and deploy in one step
az containerapp up \
  --name lukhas-ai \
  --resource-group Lukhas \
  --location uksouth \
  --environment lukhas-dev-apps-env \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --target-port 8080 \
  --ingress external \
  --query properties.configuration.ingress.fqdn

echo ""
echo "✅ Initial deployment complete!"
echo "🔄 Now updating with LUKHAS AI image..."

# Get the app URL
APP_URL=$(az containerapp show --name lukhas-ai --resource-group Lukhas --query "properties.configuration.ingress.fqdn" --output tsv)

echo "🌐 Your LUKHAS AI will be available at: https://$APP_URL"
echo ""
echo "📋 Next steps:"
echo "1. Set your OpenAI API key in Azure Portal"
echo "2. Update to custom LUKHAS image when ready"
echo "3. Monitor logs via Azure Portal or VS Code"