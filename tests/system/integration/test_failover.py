# owner: Jules-09
# tier: tier2
# module_uid: system.integration.failover
# criticality: P2

import pytest
import shutil
import subprocess
import time
import requests
import os

DOCKER_COMPOSE_FILE = "deployment/docker/docker-compose.yml"
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

RUN_SYSTEM_TESTS = os.getenv("RUN_SYSTEM_TESTS") == "1"
# ΛTAG: system_test_opt_in
HAS_DOCKER = shutil.which("docker-compose") or shutil.which("docker")
pytestmark = pytest.mark.skipif(
    not RUN_SYSTEM_TESTS or not HAS_DOCKER,
    reason=(
        "System tests require RUN_SYSTEM_TESTS=1 and Docker tooling; skipping to protect CI"
    ),
)


@pytest.fixture(scope="module")
def system_up():
    """Fixture to start and stop the system for the test module."""
    try:
        subprocess.run(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d"], check=True)
        # Wait for the system to be healthy
        health_url = f"{BASE_URL}/api/v2/health"
        for _ in range(30):
            try:
                response = requests.get(health_url)
                if response.status_code == 200 and response.json()["status"] == "healthy":
                    break
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        else:
            pytest.fail("System did not become healthy in time.")

        yield

    finally:
        subprocess.run(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "down"], check=True)

@pytest.mark.tier2
@pytest.mark.system
def test_redis_failover(system_up):
    """
    Test the system's resilience to Redis failure.
    """
    try:
        # 1. Stop the redis service
        subprocess.run(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "stop", "redis"], check=True)

        # 2. Check if the API is still responsive
        health_url = f"{BASE_URL}/api/v2/health"
        response = requests.get(health_url)
        assert response.status_code == 200
        # The system might be degraded but should still be running
        assert response.json()["status"] == "healthy"

        # 3. Restart the redis service
        subprocess.run(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "start", "redis"], check=True)
        time.sleep(5) # Give it some time to recover

        # 4. Check if the system is fully healthy again
        response = requests.get(health_url)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    except Exception as e:
        pytest.fail(f"An unexpected error occurred during the failover test: {e}")
