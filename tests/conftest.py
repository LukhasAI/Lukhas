import os
import sys
import pathlib
import sqlite3
from pathlib import Path

import pytest

# T4 Deterministic Path Setup
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Legacy compatibility
project_root = REPO_ROOT


@pytest.fixture(scope="session")
def settings():
    """Test configuration settings."""
    return {"env": "test", "debug": os.getenv("PYTEST_DEBUG", "false").lower() == "true"}


@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def lukhas_test_config():
    """LUKHAS-specific test configuration."""
    return {
        "consciousness_active": False,
        "dream_simulation_enabled": False,
        "quantum_processing_enabled": False,
        "ethics_enforcement_level": "strict",
    }


# T4 Core Fixtures
@pytest.fixture(scope="function")
def module_path():
    """T4 fixture: Provides repo root path for module loading."""
    return REPO_ROOT


@pytest.fixture(scope="function")
def sqlite_db(tmp_path):
    """T4 fixture: Provides isolated SQLite database for tests."""
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
    finally:
        conn.close()


# T4 Quarantine Bookkeeping
def pytest_runtest_makereport(item, call):
    """T4 quarantine system: Track quarantine test failures."""
    if "quarantine" in item.keywords and call.when == "call" and call.excinfo:
        item._quarantine_fail = getattr(item, "_quarantine_fail", 0) + 1
