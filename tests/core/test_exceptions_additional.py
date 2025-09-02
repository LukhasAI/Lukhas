"""Additional tests for common exceptions to improve coverage."""

# ΛTAG: coverage

from __future__ import annotations

import pytest

from lukhas.core.common.exceptions import (
    AuthenticationError,
    AuthorizationError,
    CircuitBreakerError,
    ConfigurationError,
    GLYPHError,
    GuardianRejectionError,
    MemoryDriftError,
    ModuleTimeoutError,
    ValidationError,
    raise_guardian_rejection,
    raise_if_drift_excessive,
)


def test_guardian_rejection_error_to_dict() -> None:
    """Guardian rejection populates ethics and suggestion details."""
    # ΛTAG: guardian
    err = GuardianRejectionError(
        message="Rejected",
        ethics_violation="test_violation",
        suggestion="fix_it",
    )
    assert err.to_dict()["details"] == {
        "ethics_violation": "test_violation",
        "suggestion": "fix_it",
    }


def test_raise_guardian_rejection_function() -> None:
    """raise_guardian_rejection raises GuardianRejectionError."""
    # ΛTAG: guardian
    with pytest.raises(GuardianRejectionError):
        raise_guardian_rejection("nope", ethics_violation="bad", suggestion="good")


def test_memory_drift_error_and_check_metric() -> None:
    """Memory drift error reports exceeded drift correctly."""
    # ΛTAG: drift
    drift_level = 0.6
    threshold = 0.3
    err = MemoryDriftError(
        message="Drift exceeded",
        memory_id="m1",
        drift_level=drift_level,
        threshold=threshold,
    )
    drift_score = drift_level - threshold
    assert err.details["exceeded_by"] == pytest.approx(drift_score)


def test_raise_if_drift_excessive_branches() -> None:
    """raise_if_drift_excessive triggers only when drift is high."""
    # ΛTAG: drift
    raise_if_drift_excessive("m2", drift_level=0.2, threshold=0.3)
    with pytest.raises(MemoryDriftError):
        raise_if_drift_excessive("m3", drift_level=0.5, threshold=0.3)


def test_module_timeout_error_details() -> None:
    """Module timeout error includes optional context."""
    # ΛTAG: coverage
    err = ModuleTimeoutError(
        message="Too slow",
        module_name="mod",
        operation="op",
        timeout_seconds=1.5,
    )
    assert err.details == {"module": "mod", "operation": "op", "timeout_seconds": 1.5}


def test_configuration_error_with_file() -> None:
    """Configuration error captures config file and key."""
    # ΛTAG: coverage
    err = ConfigurationError(
        message="Config missing",
        config_key="alpha",
        config_file="settings.yml",
    )
    assert err.details == {"config_key": "alpha", "config_file": "settings.yml"}


def test_authentication_error_without_method() -> None:
    """Authentication error omits auth_method when not provided."""
    # ΛTAG: coverage
    err = AuthenticationError()
    assert "auth_method" not in err.details


def test_authorization_error_details() -> None:
    """Authorization error reports required and current tiers."""
    # ΛTAG: coverage
    err = AuthorizationError(
        required_tier=2,
        current_tier=1,
        required_permission="write",
    )
    assert err.details == {
        "required_tier": 2,
        "current_tier": 1,
        "required_permission": "write",
    }


def test_validation_error_with_constraint() -> None:
    """Validation error includes constraint when provided."""
    # ΛTAG: coverage
    err = ValidationError(
        message="Bad input",
        field="name",
        value="",
        constraint="non_empty",
    )
    assert err.details["constraint"] == "non_empty"


def test_glyph_error_details() -> None:
    """GLYPH error carries glyph identifiers."""
    # ΛTAG: coverage
    err = GLYPHError(message="Glyph fail", glyph_id="g1", glyph_symbol="⊗")
    assert err.details == {"glyph_id": "g1", "glyph_symbol": "⊗"}


def test_circuit_breaker_error_details() -> None:
    """Circuit breaker error exposes service metrics."""
    # ΛTAG: coverage
    err = CircuitBreakerError(
        message="Circuit open",
        service_name="svc",
        failure_count=5,
        threshold=3,
        reset_timeout=10.0,
    )
    assert err.details["service_name"] == "svc"

