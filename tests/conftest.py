import os
import pathlib
import random
import sqlite3
import sys
from pathlib import Path

import pytest

# Seed determinism for reproducible tests
PYTHONHASHSEED = os.environ.get("PYTHONHASHSEED")
if PYTHONHASHSEED is None:
    os.environ["PYTHONHASHSEED"] = "0"

# Set random seed for deterministic test behavior
random.seed(1337)

# T4 Lane Configuration
def pytest_addoption(parser):
    parser.addoption("--lane", action="store", default=os.getenv("LUKHAS_LANE", "experimental"))

def pytest_configure(config):
    os.environ.setdefault("LUKHAS_LANE", config.getoption("--lane"))

def pytest_runtest_setup(item):
    if "prod_only" in item.keywords and os.getenv("LUKHAS_LANE", "experimental") not in {"candidate","prod"}:
        pytest.skip("prod_only test skipped outside candidate/prod lanes")

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


import types


@pytest.fixture(autouse=True, scope="session")
def _stub_streamlit_for_tests():
    if "streamlit" not in sys.modules:
        stub = types.SimpleNamespace(
            write=lambda *a, **k: None,
            markdown=lambda *a, **k: None,
            cache_data=lambda *a, **k: (lambda f: f),
        )
        sys.modules["streamlit"] = stub
    yield


# ---------------------------------------------------------------------------
# CI Quality Gates: deterministic, fast collection & selection
# ---------------------------------------------------------------------------

CI_QG = os.getenv("CI_QUALITY_GATES") == "1"


def pytest_ignore_collect(path: Path, config):
    """Basic directory-level ignore during quality gates to avoid costly import-time failures."""
    if CI_QG:
        p = Path(path)
        parts = set(p.parts)
        if "integration" in parts or "e2e" in parts or "benchmarks" in parts:
            return True
    return False


def pytest_collection_modifyitems(config, items):
    """In quality gates mode, only keep smoke and unmarked/unit tests.

    Converts ad-hoc per-test skipping into stable, marker-based selection.
    """
    if not CI_QG:
        return

    skip_marks = {"integration", "e2e", "bench", "cloud", "enterprise", "mcp", "bio"}
    selected = []
    for item in items:
        marks = {m.name for m in item.iter_markers()}
        # Include telemetry tests in quality gates as they are smoke tests
        if "smoke" in marks or "telemetry" in marks or not marks.intersection(skip_marks):
            selected.append(item)
    items[:] = selected

# ---------------------------------------------------------------------------
# Silence only noisy SSL warnings in tests (runtime remains strict)
# ---------------------------------------------------------------------------
import warnings

try:
    import urllib3  # type: ignore
    from urllib3.exceptions import InsecureRequestWarning  # type: ignore
except Exception:
    urllib3 = None
    InsecureRequestWarning = None

warnings.simplefilter("default", Warning)
if urllib3 and InsecureRequestWarning:
    urllib3.disable_warnings(InsecureRequestWarning)
