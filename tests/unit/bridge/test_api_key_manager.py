"""Unit tests for API key management guardrails."""

from __future__ import annotations

from candidate.bridge.api.orchestration_endpoints import APIKeyManager


def _build_manager(*, minute_limit: int = 1, daily_cost_limit: float = 1.0) -> APIKeyManager:
    """Create an APIKeyManager with deterministic limits for testing."""

    manager = APIKeyManager()
    manager.api_keys = {
        "test-key": {
            "user_id": "test-user",
            "tier": "test",
            "rate_limit": {"requests_per_minute": minute_limit, "requests_per_day": minute_limit},
            "cost_limit": {"daily": daily_cost_limit},
            "permissions": ["orchestration"],
        }
    }
    return manager


def test_violation_metrics_default_state() -> None:
    """Managers should expose zeroed metrics before any traffic."""

    manager = _build_manager()
    summary = manager.get_violation_metrics()

    assert summary["rate_limit_violations"]["total"] == 0
    assert summary["cost_limit_violations"]["total"] == 0


def test_rate_limit_violation_tracking() -> None:
    """Exceeding minute limits increments the violation counter."""

    manager = _build_manager(minute_limit=1)
    user_info = manager.validate_api_key("test-key")

    assert manager.check_rate_limit("test-key", user_info) is True
    assert manager.check_rate_limit("test-key", user_info) is False

    summary = manager.get_violation_metrics()

    assert summary["rate_limit_violations"]["total"] == 1
    assert summary["rate_limit_violations"]["by_user"]["test-user"] == 1


def test_cost_limit_violation_tracking() -> None:
    """Cost guardrails record violations when exceeded."""

    manager = _build_manager(daily_cost_limit=1.0)
    user_info = manager.validate_api_key("test-key")

    assert manager.check_cost_limit("test-key", user_info, 0.5) is True
    manager.record_cost("test-key", user_info, 0.5)

    assert manager.check_cost_limit("test-key", user_info, 0.6) is False

    summary = manager.get_violation_metrics()

    assert summary["cost_limit_violations"]["total"] == 1
    assert summary["cost_limit_violations"]["by_user"]["test-user"] == 1
