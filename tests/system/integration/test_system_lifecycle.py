# owner: Jules-09
# tier: tier2
# module_uid: system.integration.system_lifecycle
# criticality: P2

import os
import shutil
import subprocess
import time

import pytest
import requests

DOCKER_COMPOSE_FILE = "deployment/docker/docker-compose.yml"
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

RUN_SYSTEM_TESTS = os.getenv("RUN_SYSTEM_TESTS") == "1"
# ΛTAG: system_test_opt_in
HAS_DOCKER = shutil.which("docker-compose") or shutil.which("docker")
pytestmark = pytest.mark.skipif(
    not RUN_SYSTEM_TESTS or not HAS_DOCKER,
    reason="System tests require RUN_SYSTEM_TESTS=1 and Docker tooling; skipping to protect CI",
)


@pytest.mark.tier2
@pytest.mark.system
def test_system_startup_shutdown():
    """
    Test system startup and shutdown lifecycle.
    """
    try:
        # Step 1: Start the system
        startup_command = ["docker-compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d"]
        subprocess.run(startup_command, check=True)

        # Step 2: Wait for services to be healthy
        health_url = f"{BASE_URL}/api/v2/health"
        is_healthy = False
        for _ in range(30):  # Wait for up to 30 seconds
            try:
                response = requests.get(health_url)
                if response.status_code == 200 and response.json()["status"] == "healthy":
                    is_healthy = True
                    break
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)

        assert is_healthy, "System did not become healthy in time."

    finally:
        # Step 3: Shutdown the system
        shutdown_command = ["docker-compose", "-f", DOCKER_COMPOSE_FILE, "down"]
        subprocess.run(shutdown_command, check=True)

        # Optional: Check if containers are stopped
        # This can be complex, so for now we just ensure the command runs.
