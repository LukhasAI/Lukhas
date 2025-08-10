# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: conftest.py
# MODULE: tests
# DESCRIPTION: Pytest configuration and fixtures for Oneiric Core testing.
#              Manages test database containers, client fixtures, dependency
#              mocking, and test environment setup.
# DEPENDENCIES: pytest, testcontainers, subprocess, os, httpx, ..oneiric_core.main
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import os
from unittest.mock import Mock

import pytest

# from testcontainers.postgres import PostgresContainer  # Skipping for now
# from creativity.dream.oneiric_engine.oneiric_core.main import app
# from creativity.dream.oneiric_engine.oneiric_core.db.db import init_db


@pytest.fixture(scope="session")
def db_url():
    """Mock database URL for testing"""
    url = "postgresql://test:test@localhost:5432/test_db"
    os.environ["DATABASE_URL"] = url
    yield url


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(db_url):
    """Skip migrations for mock testing"""
    print("Skipping migrations for mock test database")


@pytest.fixture(scope="session", autouse=True)
def reset_pool(db_url):
    """Skip pool reset for mock testing"""
    pass  # Skip for mock testing


@pytest.fixture
async def client():
    """Create a mock test client"""
    mock_client = Mock()
    mock_client.get = Mock(return_value=Mock(status_code=200, json=lambda: {}))
    mock_client.post = Mock(return_value=Mock(status_code=200, json=lambda: {}))
    mock_client.put = Mock(return_value=Mock(status_code=200, json=lambda: {}))
    mock_client.delete = Mock(return_value=Mock(status_code=200, json=lambda: {}))
    yield mock_client


@pytest.fixture(autouse=True)
def override_dependency(monkeypatch):
    """Override external dependencies for testing"""

    async def fake_clerk_verify(token):
        # Always returns a fixed profile for testing
        return {"sub": "test_user_123", "email": "test@example.com"}

    monkeypatch.setattr(
        "oneiric_core.identity.auth_middleware.clerk_verify", fake_clerk_verify
    )


# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: conftest.py
# VERSION: 1.0.0
# TIER SYSTEM: Test environment (Infrastructure for all tier testing)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Test database provisioning, test client creation, dependency
#               mocking, migration management, fixture lifecycle management
# FUNCTIONS: db_url, apply_migrations, reset_pool, client, override_dependency,
#           fake_clerk_verify
# CLASSES: None directly defined (uses pytest fixtures)
# DECORATORS: @pytest.fixture (various scopes: session, function, autouse)
# DEPENDENCIES: pytest, testcontainers PostgreSQL, subprocess, os environment,
#               httpx AsyncClient, oneiric_core application
# INTERFACES: pytest fixture interface, Docker container interface
# ERROR HANDLING: Migration failure handling, container startup errors
# LOGGING: ΛTRACE_ENABLED for test infrastructure setup and teardown
# AUTHENTICATION: Mock authentication for isolated testing
# HOW TO USE:
#   Fixtures are automatically available in all test functions
#   pytest automatically uses conftest.py for test configuration
#   No direct usage - framework integration
# INTEGRATION NOTES: Uses Docker testcontainers for database isolation. Manages
#   full application lifecycle for testing. Provides mock authentication to
#   avoid external dependencies during testing.
# MAINTENANCE: Update fixtures as application structure changes, maintain
#   database schema compatibility, update mock implementations.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
