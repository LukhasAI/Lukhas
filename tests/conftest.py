import os
import sys

import pytest

# Ensure repo root is on sys.path for imports like `import matriz.*`
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Tier-1 freeze configuration
TIER1_ONLY = os.getenv("T4_TIER1_ONLY", "1") == "1"


def pytest_collection_modifyitems(_config, items):
    """Modify test collection to enforce Tier-1 freeze and quarantine policies."""
    for item in list(items):
        p = str(item.fspath)

        # Skip quarantined areas during audit freeze
        if "/quarantine/" in p or "/archive/" in p:
            item.add_marker(pytest.mark.skip(reason="quarantined during audit freeze"))

        # Skip legacy tree unless explicitly requested
        if TIER1_ONLY and "/tests/legacy/" in p:
            item.add_marker(pytest.mark.skip(reason="legacy excluded in Tier-1 mode"))

        # Skip phase2 tests that depend on non-Tier-1 modules
        if TIER1_ONLY and "/tests/phase2/" in p:
            item.add_marker(pytest.mark.skip(reason="phase2 excluded in Tier-1 mode"))


def pytest_configure(config):
    """Configure pytest with Tier-1 awareness."""
    if TIER1_ONLY:
        config.addinivalue_line("markers", "tier1_only: Running in Tier-1 only mode")
        print("🧊 TIER-1 MODE: Legacy and non-Tier-1 tests excluded")
    else:
        print("🔄 FULL MODE: All tests included")


def pytest_runtest_setup(item):
    """Skip tests that import quarantined modules during audit freeze."""
    if "bio" in str(item.fspath):
        pytest.xfail("bio components quarantined during audit freeze")
