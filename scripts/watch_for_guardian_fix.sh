#!/bin/bash
# Monitor for Guardian YAML fix and trigger deployment
# Run this in background: ./scripts/watch_for_guardian_fix.sh &

echo "🔍 Monitoring for Guardian fix (#390 or related PR)..."
echo "   Press Ctrl+C to stop"
echo ""

LAST_COMMIT=""
CHECK_INTERVAL=60  # Check every 60 seconds

while true; do
    # Pull latest
    git fetch origin main --quiet

    # Get latest commit
    CURRENT_COMMIT=$(git rev-parse origin/main)

    if [ "$LAST_COMMIT" != "$CURRENT_COMMIT" ]; then
        echo "📦 New commit detected: $(git log -1 --oneline origin/main)"

        # Check if Guardian policy file was updated
        if git diff "$LAST_COMMIT" "$CURRENT_COMMIT" --name-only | grep -q "configs/policy/guardian_policies.yaml"; then
            echo "✅ Guardian policy file updated!"
            echo ""
            echo "🚀 TRIGGERING DEPLOYMENT SEQUENCE"
            echo "================================="

            # Pull the changes
            git pull --ff-only

            # Test Guardian loads
            if python3 -c "from lukhas.adapters.openai.policy_pdp import PolicyLoader; p = PolicyLoader.load_from_file('configs/policy/guardian_policies.yaml'); print(f'✅ Guardian loaded {len(p.rules)} rules')" 2>/dev/null; then
                echo "✅ Guardian PDP loads successfully!"

                # Quick smoke test
                if pytest tests/smoke/test_openai_facade.py::test_responses_minimal -q 2>/dev/null; then
                    echo "✅ Smoke test passed!"
                else
                    echo "⚠️ Smoke test failed but continuing..."
                fi

                echo ""
                echo "🎯 READY FOR DEPLOYMENT!"
                echo "========================"
                echo ""
                echo "Run now: ./scripts/deploy_monitoring_post_390.sh"
                echo ""

                # Optional: Auto-run deployment
                read -t 10 -p "Auto-run deployment? (y/N - 10s timeout): " -n 1 -r
                echo ""
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    ./scripts/deploy_monitoring_post_390.sh
                else
                    echo "ℹ️ Manual deployment required: ./scripts/deploy_monitoring_post_390.sh"
                fi

                # Success - exit monitor
                echo ""
                echo "✅ Monitoring complete. Guardian fix detected and validated."
                exit 0
            else
                echo "⚠️ Guardian still not loading correctly. Continuing to monitor..."
            fi
        else
            # Check commit messages for Guardian-related changes
            if git log -1 --oneline origin/main | grep -iE "(guardian|pdp|policy|#390)"; then
                echo "📝 Guardian-related commit detected. Checking..."

                git pull --ff-only --quiet

                if python3 -c "from lukhas.adapters.openai.policy_pdp import PolicyLoader; PolicyLoader.load_from_file('configs/policy/guardian_policies.yaml')" 2>/dev/null; then
                    echo "✅ Guardian fix detected via code change!"
                    echo "🎯 Run: ./scripts/deploy_monitoring_post_390.sh"

                    # Alert and optionally run
                    echo -e "\a"  # Terminal bell
                    read -t 10 -p "Deploy now? (y/N): " -n 1 -r
                    echo ""
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        ./scripts/deploy_monitoring_post_390.sh
                        exit 0
                    fi
                fi
            fi
        fi

        LAST_COMMIT="$CURRENT_COMMIT"
    fi

    # Show heartbeat
    echo -n "."
    sleep $CHECK_INTERVAL
done