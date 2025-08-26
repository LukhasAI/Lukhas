#!/bin/bash

# LUKHAS AI - NewRelic Setup Script
# GitHub Student Pack Integration
# ===============================

echo "🎓 LUKHAS AI - NewRelic Monitoring Setup"
echo "GitHub Student Pack ($300/month value)"
echo "======================================"
echo ""

# Check if NewRelic license key is provided
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <NEWRELIC_LICENSE_KEY>"
    echo ""
    echo "📋 Steps to get your license key:"
    echo "1. Go to: https://newrelic.com/students"
    echo "2. Sign up with your student email"
    echo "3. Connect GitHub Student Pack"
    echo "4. Get license key from: https://one.newrelic.com"
    echo ""
    exit 1
fi

NEWRELIC_LICENSE_KEY="$1"

echo "🔧 Setting up NewRelic monitoring..."
echo ""

# Step 1: Install NewRelic package
echo "1️⃣ Installing NewRelic Python agent..."
pip install newrelic>=9.2.0

# Step 2: Set environment variables for Azure Container Apps
echo "2️⃣ Setting up Azure Container Apps environment variables..."

# Update Azure Container Apps with NewRelic configuration
az containerapp secret set \
    --name lukhas-ai \
    --resource-group Lukhas \
    --secrets newrelic-license-key="6b3bf1f99ed5cdd301408489c073724fFFFFNRAL"

# Add NewRelic environment variables
az containerapp update \
    --name lukhas-ai \
    --resource-group Lukhas \
    --set-env-vars \
        NEWRELIC_LICENSE_KEY=secretref:newrelic-license-key \
        NEW_RELIC_APP_NAME="LUKHAS AI Production" \
        NEW_RELIC_LOG_LEVEL=INFO \
        NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true \
        NEW_RELIC_APPLICATION_LOGGING_ENABLED=true \
        NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED=true

echo "3️⃣ Verifying NewRelic setup..."

# Test the configuration
python3 -c "
import os
os.environ['NEWRELIC_LICENSE_KEY'] = '$NEWRELIC_LICENSE_KEY'
from monitoring.newrelic_config import initialize_monitoring
monitor = initialize_monitoring('$NEWRELIC_LICENSE_KEY')
print('✅ NewRelic configuration test passed')
"

echo ""
echo "✅ NewRelic monitoring setup complete!"
echo ""
echo "🎯 What's configured:"
echo "   • Application: LUKHAS AI Production"
echo "   • Environment: Production"
echo "   • Platform: Azure Container Apps"
echo "   • Features: Full monitoring suite ($300/month value)"
echo ""
echo "🔗 Access your monitoring dashboard:"
echo "   • NewRelic One: https://one.newrelic.com"
echo "   • Look for 'LUKHAS AI Production' application"
echo ""
echo "📊 Monitored metrics:"
echo "   • API performance and errors"
echo "   • Consciousness interaction tracking"
echo "   • Dream generation metrics"
echo "   • Trinity Framework health (⚛️🧠🛡️)"
echo "   • Custom LUKHAS AI business metrics"
echo ""
echo "🚀 Your container app will restart with monitoring enabled!"
