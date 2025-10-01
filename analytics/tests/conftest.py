"""
Test configuration for analytics module.
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "module_name": "analytics",
        "test_mode": True,
        "log_level": "DEBUG"
    }


@pytest.fixture(scope="session")
def temp_dir():
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture(scope="function")
def clean_environment():
    """Ensure clean test environment."""
    # Store original environment
    original_env = dict(os.environ)

    # Set test environment
    os.environ["LUKHAS_ENV"] = "testing"
    os.environ["LUKHAS_MODULE"] = "analytics"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_analytics_config():
    """Mock configuration for analytics module."""
    return {
        "module": {
            "name": "analytics",
            "version": "1.0.0-test"
        },
        "runtime": {
            "log_level": "DEBUG",
            "debug_mode": True
        }
    }
