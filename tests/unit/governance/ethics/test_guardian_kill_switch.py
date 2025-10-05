"""Guardian kill-switch integration tests."""

import pytest

from lukhas.governance.ethics.ethics_engine import (
    GUARDIAN_EMERGENCY_DISABLE_FILE,
    ConstitutionalFramework,
    EthicsEngine,
    SafetyMonitor,
)


@pytest.fixture(autouse=True)
def _cleanup_kill_switch():
    """Ensure the kill-switch file is cleaned up before and after tests."""
    try:
        GUARDIAN_EMERGENCY_DISABLE_FILE.unlink()
    except FileNotFoundError:
        pass
    yield
    try:
        GUARDIAN_EMERGENCY_DISABLE_FILE.unlink()
    except FileNotFoundError:
        pass


def test_validate_action_respects_kill_switch():
    """EthicsEngine should bypass evaluation when kill switch file exists."""
    engine = EthicsEngine()

    GUARDIAN_EMERGENCY_DISABLE_FILE.touch()
    decision = engine.validate_action("test_action", {})

    assert decision.decision == "allow"
    assert decision.triad_compliance["guardian"] is False


def test_safety_monitor_respects_kill_switch():
    """SafetyMonitor should allow actions immediately when kill switch active."""
    framework = ConstitutionalFramework()
    monitor = SafetyMonitor(framework)

    GUARDIAN_EMERGENCY_DISABLE_FILE.touch()
    assert monitor.monitor_action("any", {}) is True
