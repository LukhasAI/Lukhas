#!/bin/bash

# LUKHAS AI - Azure OpenAI Deployment Script
# For GitHub Student Pack / Azure for Students

echo "🚀 LUKHAS AI - Azure OpenAI Deployment"
echo "======================================"

# Configuration
RESOURCE_GROUP="Lukhas"
OPENAI_SERVICE="Lukhas"
LOCATION="uksouth"

echo "📍 Using Resource Group: $RESOURCE_GROUP"
echo "🧠 Using OpenAI Service: $OPENAI_SERVICE"
echo "🌍 Using Location: $LOCATION"
echo ""

# Step 1: Check current service status
echo "1️⃣ Checking Azure OpenAI service status..."
az cognitiveservices account show --name $OPENAI_SERVICE --resource-group $RESOURCE_GROUP --query "{name:name, kind:kind, location:location, endpoint:properties.endpoint}" --output table

echo ""

# Step 2: List available models
echo "2️⃣ Available OpenAI models in $LOCATION:"
az cognitiveservices model list --location $LOCATION --query "[?kind=='OpenAI' && (contains(model.name, 'gpt-4') || contains(model.name, 'gpt-35-turbo'))].{Name:model.name, Version:model.version}" --output table

echo ""

# Step 3: Try to deploy GPT-3.5-turbo with minimal capacity
echo "3️⃣ Attempting to deploy GPT-3.5-turbo..."
echo "   (If this fails with quota error, you'll need to request quota increase)"

# Try with capacity 1 (minimum)
az cognitiveservices account deployment create \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --deployment-name "gpt-35-turbo" \
  --model-name "gpt-35-turbo" \
  --model-version "0125" \
  --model-format "OpenAI" \
  --sku-capacity 1 \
  --sku-name "Standard" 2>&1

echo ""

# Step 4: Try to deploy GPT-4 (if GPT-3.5 worked)
echo "4️⃣ Attempting to deploy GPT-4..."
az cognitiveservices account deployment create \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --deployment-name "gpt-4" \
  --model-name "gpt-4" \
  --model-version "0125-Preview" \
  --model-format "OpenAI" \
  --sku-capacity 1 \
  --sku-name "Standard" 2>&1

echo ""

# Step 5: List deployed models
echo "5️⃣ Currently deployed models:"
az cognitiveservices account deployment list \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --query "[].{Name:name, Model:properties.model.name, Version:properties.model.version, Capacity:properties.scaleSettings.capacity}" \
  --output table

echo ""

# Step 6: Get API key
echo "6️⃣ Getting API key for integration..."
API_KEY=$(az cognitiveservices account keys list --name $OPENAI_SERVICE --resource-group $RESOURCE_GROUP --query "key1" --output tsv)
echo "Azure OpenAI API Key: $API_KEY"

echo ""
echo "✅ Deployment script complete!"
echo ""
echo "📋 Next Steps if quota errors occurred:"
echo "   1. Go to https://portal.azure.com"
echo "   2. Navigate to your OpenAI service: $OPENAI_SERVICE"
echo "   3. Go to 'Model deployments' -> 'Manage Deployments'"
echo "   4. Click 'Create new deployment'"
echo "   5. Select model and request quota increase if needed"
echo ""
echo "🔗 Useful links:"
echo "   • Azure Portal: https://portal.azure.com"
echo "   • OpenAI Service: https://portal.azure.com/#@gonzodominguezicloud.onmicrosoft.com/resource/subscriptions/655855d4-df7b-44af-aedc-8169e7e34144/resourceGroups/Lukhas/providers/Microsoft.CognitiveServices/accounts/Lukhas"
echo "   • Quota Management: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade/newsupportrequest"