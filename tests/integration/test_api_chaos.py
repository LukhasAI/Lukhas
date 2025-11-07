#!/usr/bin/env python3
"""
Test Suite: API Chaos Engineering

Applies chaos engineering principles to the application's API
to test its resilience under various failure conditions.

# ΛTAG: chaos_engineering, resilience_testing, api_testing
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from serve.main import app

# --- Test Fixtures ---

@pytest.fixture
def client():
    """Create a TestClient instance for the FastAPI app."""
    return TestClient(app)

# --- Chaos Integration Tests ---

def test_healthz_endpoint_resilience(client):
    """
    Test the /healthz endpoint's resilience to failures
    in its dependencies by directly injecting an exception.
    """
    # Patch the voice_core_available function to raise an exception
    with patch('serve.main.voice_core_available', side_effect=RuntimeError("Voice core failure")):
        # Make a request to the /healthz endpoint
        response = client.get("/healthz")

        # The endpoint should handle the failure gracefully and return a 200 OK,
        # but with a degraded status.
        assert response.status_code == 200
        assert response.json()["voice_mode"] == "degraded"

def test_healthz_endpoint_network_partition(client):
    """
    Test the /healthz endpoint's resilience to network partitions
    by directly injecting an exception.
    """
    # Patch the voice_core_available function to raise a network-related exception
    with patch('serve.main.voice_core_available', side_effect=ConnectionAbortedError("Network partition simulated")):
        # Make a request to the /healthz endpoint
        response = client.get("/healthz")

        # The endpoint should handle the network partition gracefully
        # and return a 200 OK with a degraded status.
        assert response.status_code == 200
        assert response.json()["voice_mode"] == "degraded"
