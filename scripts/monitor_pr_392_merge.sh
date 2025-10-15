#!/bin/bash

# Monitor PR #392 for merge and trigger deployment
# Usage: ./scripts/monitor_pr_392_merge.sh [--auto-deploy]

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

AUTO_DEPLOY=false
if [[ "${1:-}" == "--auto-deploy" ]]; then
    AUTO_DEPLOY=true
    echo -e "${YELLOW}Auto-deployment enabled. Will deploy monitoring once PR #392 is merged.${NC}"
fi

echo -e "${BLUE}Monitoring PR #392 for merge status...${NC}"
echo "Press Ctrl+C to stop monitoring."

while true; do
    # Check PR status
    PR_STATE=$(gh pr view 392 --json state -q '.state' 2>/dev/null || echo "ERROR")

    if [[ "$PR_STATE" == "MERGED" ]]; then
        echo -e "\n${GREEN}✅ PR #392 has been MERGED!${NC}"
        echo -e "${BLUE}Guardian fix is now in main branch.${NC}"

        # Pull latest changes
        echo -e "\n${YELLOW}Pulling latest changes from main...${NC}"
        git checkout main
        git pull --ff-only

        # Run verification
        echo -e "\n${BLUE}Running Guardian verification...${NC}"
        python3 -c "
from lukhas.adapters.openai.api import get_app
try:
    app = get_app()
    if app.state.pdp:
        print('✅ Guardian PDP initialized successfully!')
        print(f'   Rules loaded: {len(app.state.pdp.policy.rules)}')
    else:
        print('❌ Guardian PDP not initialized')
except Exception as e:
    print(f'❌ Error: {e}')
"

        if [[ "$AUTO_DEPLOY" == "true" ]]; then
            echo -e "\n${YELLOW}Auto-deploying monitoring infrastructure...${NC}"

            # Deploy Prometheus rules
            if [[ -f "lukhas/observability/rules/guardian-rl.rules.yml" ]]; then
                echo "Deploying Prometheus recording rules..."
                sudo cp lukhas/observability/rules/guardian-rl.rules.yml /etc/prometheus/rules.d/ || {
                    echo -e "${RED}Failed to copy Prometheus rules. May need manual deployment.${NC}"
                }

                # Reload Prometheus
                echo "Reloading Prometheus configuration..."
                curl -X POST http://localhost:9090/-/reload || {
                    echo -e "${RED}Failed to reload Prometheus. May need manual reload.${NC}"
                }
            fi

            # Run health audit
            echo -e "\n${BLUE}Running system health audit...${NC}"
            python3 scripts/system_health_audit.py || true

            # Run smoke tests
            echo -e "\n${BLUE}Running smoke tests...${NC}"
            bash scripts/smoke_test_openai_facade.sh || true

            echo -e "\n${GREEN}✅ Deployment complete!${NC}"
            echo -e "${YELLOW}Note: Import Grafana dashboard manually via UI.${NC}"
            echo "Dashboard location: lukhas/observability/grafana/guardian-rl-dashboard.json"
        else
            echo -e "\n${GREEN}PR #392 merged successfully!${NC}"
            echo -e "${YELLOW}Run with --auto-deploy flag to automatically deploy monitoring.${NC}"
            echo ""
            echo "Manual deployment commands:"
            echo "  sudo cp lukhas/observability/rules/guardian-rl.rules.yml /etc/prometheus/rules.d/"
            echo "  curl -X POST http://localhost:9090/-/reload"
            echo "  # Import dashboard: lukhas/observability/grafana/guardian-rl-dashboard.json"
        fi

        exit 0
    elif [[ "$PR_STATE" == "CLOSED" ]]; then
        echo -e "\n${RED}❌ PR #392 was closed without merging!${NC}"
        exit 1
    elif [[ "$PR_STATE" == "ERROR" ]]; then
        echo -e "${RED}Error checking PR status. Retrying...${NC}"
    else
        echo -n "."
    fi

    # Wait 30 seconds before checking again
    sleep 30
done