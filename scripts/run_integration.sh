#!/bin/bash
set -e

# Start services
docker-compose -f devtools/docker-compose.integration.yml up -d

# Wait for services to be healthy
# (In a real-world scenario, you would add health checks here)
sleep 10

# Run integration tests
/Users/agi_dev/Library/Python/3.9/bin/pytest tests/integration

# Stop services
docker-compose -f devtools/docker-compose.integration.yml down
