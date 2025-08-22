"""
LUKHAS AI Test Configuration
Safety-first defaults for all test environments
"""

import os
import sys
import pytest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def pytest_configure(config):
    """
    Configure pytest with safety-first defaults.
    These settings ensure tests run in dry-run mode by default.
    """
    # Safety-first environment defaults
    os.environ.setdefault("LUKHAS_DRY_RUN_MODE", "true")
    os.environ.setdefault("LUKHAS_OFFLINE", "true")
    os.environ.setdefault("LUKHAS_FEATURE_MATRIX_EMIT", "true")
    
    # Disable all features by default (safety first)
    os.environ.setdefault("FEATURE_POLICY_DECIDER", "false")
    os.environ.setdefault("FEATURE_ORCHESTRATION_HANDOFF", "false")
    os.environ.setdefault("FEATURE_IDENTITY_PASSKEY", "false")
    os.environ.setdefault("FEATURE_GOVERNANCE_LEDGER", "false")
    
    # Core system flags (all disabled for safety)
    os.environ.setdefault("CORE_ACTIVE", "false")
    os.environ.setdefault("CONSCIOUSNESS_ACTIVE", "false")
    os.environ.setdefault("VIVOX_ACTIVE", "false")
    os.environ.setdefault("QI_ACTIVE", "false")
    os.environ.setdefault("MEMORY_ACTIVE", "false")
    
    # Guardian enforcement
    os.environ.setdefault("GUARDIAN_ENFORCEMENT", "strict")
    os.environ.setdefault("ETHICS_ENFORCEMENT_LEVEL", "strict")
    
    # Performance and safety thresholds
    os.environ.setdefault("SYMBOLIC_DRIFT_THRESHOLD", "0.15")
    os.environ.setdefault("TRINITY_COHERENCE_MIN", "0.3")
    os.environ.setdefault("MEMORY_FOLD_LIMIT", "1000")
    
    # Test environment marker
    os.environ.setdefault("TEST_MODE", "true")
    os.environ.setdefault("DEBUG", "false")
    
    # Logging configuration
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("ENABLE_DRIFT_LOGGING", "true")


# Test fixtures for common operations
@pytest.fixture
def dry_run_mode():
    """Ensure dry-run mode is active"""
    original = os.environ.get("LUKHAS_DRY_RUN_MODE")
    os.environ["LUKHAS_DRY_RUN_MODE"] = "true"
    yield
    if original is not None:
        os.environ["LUKHAS_DRY_RUN_MODE"] = original
    else:
        del os.environ["LUKHAS_DRY_RUN_MODE"]


@pytest.fixture
def mock_api_response():
    """Provide mock API responses for dry-run testing"""
    return {
        "status": "success",
        "mode": "dry_run",
        "data": {"message": "Mock response for testing"},
        "metadata": {
            "dry_run": True,
            "safety_mode": "enabled",
            "trinity_framework": "⚛️🧠🛡️"
        }
    }


@pytest.fixture
def trinity_context():
    """Provide Trinity Framework context for tests"""
    return {
        "identity": "⚛️",
        "consciousness": "🧠",
        "guardian": "🛡️",
        "framework": "⚛️🧠🛡️",
        "balance": {
            "identity": 0.33,
            "consciousness": 0.33,
            "guardian": 0.34
        }
    }


@pytest.fixture
def safety_config():
    """Provide safety-first configuration for tests"""
    return {
        "dry_run_mode": True,
        "offline": True,
        "feature_flags": {
            "policy_decider": False,
            "orchestration_handoff": False,
            "identity_passkey": False,
            "governance_ledger": False
        },
        "safety_thresholds": {
            "drift": 0.15,
            "coherence": 0.3,
            "memory_folds": 1000
        }
    }


# Custom markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may require setup)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (full system)"
    )
    config.addinivalue_line(
        "markers", "dry_run: Tests that verify dry-run mode"
    )
    config.addinivalue_line(
        "markers", "safety: Tests that verify safety features"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take more than 1 second"
    )