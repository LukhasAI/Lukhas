"""
Authorization Telemetry Smoke Tests

Validates that authorization operations properly emit OpenTelemetry spans
with the required attributes as specified in Matrix contracts.

These are smoke tests focused on:
1. Span existence - authz.check spans are emitted during authorization
2. Span attributes - spans contain proper authorization context
3. Span structure - spans follow OpenTelemetry data model
4. Error propagation - failed authorization emits proper error spans
"""

import sys
import asyncio
from pathlib import Path

import pytest

# Add tools directory to path for importing authorization middleware
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from matrix_authz_middleware import MatrixAuthzMiddleware, AuthzRequest


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_check_span_emission(telemetry_capture, test_subjects):
    """Test that authorization operations emit authz.check spans."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Build authorization request for trusted user
    trusted_subject = test_subjects["trusted"]
    request = AuthzRequest(
        subject=trusted_subject["subject"],
        tier=trusted_subject["tier"],
        tier_num=trusted_subject["tier_num"],
        scopes=trusted_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token="test-token-12345",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2"
    )

    # Make authorization decision (this should emit spans)
    decision = await middleware.authorize_request(request)

    # Verify authz.check span was emitted
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No authz.check spans found"

    span = authz_spans[0]
    assert span.name == "authz.check", f"Expected span name 'authz.check', got '{span.name}'"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_attributes_allow(telemetry_capture, test_subjects, span_validator):
    """Test that authorization spans contain required attributes for ALLOW decisions."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Build authorization request for trusted user (should be allowed)
    trusted_subject = test_subjects["trusted"]
    request = AuthzRequest(
        subject=trusted_subject["subject"],
        tier=trusted_subject["tier"],
        tier_num=trusted_subject["tier_num"],
        scopes=trusted_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token="test-token-12345",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2"
    )

    # Make authorization decision
    decision = await middleware.authorize_request(request)

    # Verify span attributes
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No authz.check spans found"

    span = authz_spans[0]
    attrs = span.attributes

    # Check required authorization context attributes
    assert "lukhas.subject" in attrs, "Missing lukhas.subject attribute"
    assert "lukhas.tier" in attrs, "Missing lukhas.tier attribute"
    assert "lukhas.tier_num" in attrs, "Missing lukhas.tier_num attribute"
    assert "lukhas.scopes" in attrs, "Missing lukhas.scopes attribute"
    assert "lukhas.module" in attrs, "Missing lukhas.module attribute"
    assert "lukhas.action" in attrs, "Missing lukhas.action attribute"
    assert "lukhas.decision" in attrs, "Missing lukhas.decision attribute"
    assert "lukhas.reason" in attrs, "Missing lukhas.reason attribute"
    assert "lukhas.decision_time_ms" in attrs, "Missing lukhas.decision_time_ms attribute"

    # Verify attribute values
    assert attrs["lukhas.subject"] == trusted_subject["subject"]
    assert attrs["lukhas.tier"] == trusted_subject["tier"]
    assert attrs["lukhas.tier_num"] == trusted_subject["tier_num"]
    assert attrs["lukhas.module"] == "memoria"
    assert attrs["lukhas.action"] == "recall"
    assert attrs["lukhas.decision"] == "allow", f"Expected decision=allow, got {attrs['lukhas.decision']}"

    # Verify span structure
    assert span_validator.validate_span_structure(span), "Span structure validation failed"
    assert span_validator.validate_authz_span(span), "Authorization span validation failed"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_attributes_deny(telemetry_capture, test_subjects, span_validator):
    """Test that authorization spans contain required attributes for DENY decisions."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Build authorization request for guest user (should be denied)
    guest_subject = test_subjects["guest"]
    request = AuthzRequest(
        subject=guest_subject["subject"],
        tier=guest_subject["tier"],
        tier_num=guest_subject["tier_num"],
        scopes=guest_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token="test-token-12345",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2"
    )

    # Make authorization decision
    decision = await middleware.authorize_request(request)

    # Verify span attributes
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No authz.check spans found"

    span = authz_spans[0]
    attrs = span.attributes

    # Verify core attributes
    assert attrs["lukhas.subject"] == guest_subject["subject"]
    assert attrs["lukhas.tier"] == guest_subject["tier"]
    assert attrs["lukhas.tier_num"] == guest_subject["tier_num"]
    assert attrs["lukhas.module"] == "memoria"
    assert attrs["lukhas.action"] == "recall"
    assert attrs["lukhas.decision"] == "deny", f"Expected decision=deny, got {attrs['lukhas.decision']}"

    # Verify deny reason is provided
    assert "lukhas.reason" in attrs
    reason = attrs["lukhas.reason"]
    assert "not authorized" in reason.lower() or "denied" in reason.lower(), f"Expected denial reason, got: {reason}"

    # Verify span status indicates error for denied authorization
    assert span.status == "ERROR", f"Expected ERROR status for denied authorization, got {span.status}"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_mfa_stepup(telemetry_capture, test_subjects):
    """Test that MFA step-up scenarios are properly reflected in spans."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Test fold action which requires step-up authentication
    trusted_subject = test_subjects["trusted"]

    # First test without MFA (should be denied)
    request_no_mfa = AuthzRequest(
        subject=trusted_subject["subject"],
        tier=trusted_subject["tier"],
        tier_num=trusted_subject["tier_num"],
        scopes=trusted_subject["scopes"],
        module="memoria",
        action="fold",
        capability_token="test-token-12345",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2"
    )

    decision_no_mfa = await middleware.authorize_request(request_no_mfa)

    # Then test with MFA (should be allowed)
    request_with_mfa = AuthzRequest(
        subject=trusted_subject["subject"],
        tier=trusted_subject["tier"],
        tier_num=trusted_subject["tier_num"],
        scopes=trusted_subject["scopes"],
        module="memoria",
        action="fold",
        capability_token="test-token-12345",
        mfa_verified=True,
        webauthn_verified=True,
        region="us-west-2"
    )

    decision_with_mfa = await middleware.authorize_request(request_with_mfa)

    # Verify both spans were emitted
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 2, f"Expected at least 2 spans, got {len(authz_spans)}"

    # Verify MFA attribute is captured
    for span in authz_spans:
        assert "lukhas.mfa_used" in span.attributes, "Missing lukhas.mfa_used attribute"

    # Find the specific spans
    no_mfa_spans = [s for s in authz_spans if s.attributes.get("lukhas.mfa_used") is False]
    mfa_spans = [s for s in authz_spans if s.attributes.get("lukhas.mfa_used") is True]

    assert len(no_mfa_spans) >= 1, "No span found for no-MFA scenario"
    assert len(mfa_spans) >= 1, "No span found for MFA scenario"

    # Verify decisions match expectations
    no_mfa_span = no_mfa_spans[0]
    mfa_span = mfa_spans[0]

    assert no_mfa_span.attributes["lukhas.decision"] == "deny", "Expected deny without MFA"
    assert mfa_span.attributes["lukhas.decision"] == "allow", "Expected allow with MFA"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_service_account(telemetry_capture, test_subjects):
    """Test that service account authorization is properly tracked in spans."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Build authorization request for service account
    service_subject = test_subjects["service"]
    request = AuthzRequest(
        subject=service_subject["subject"],
        tier=service_subject["tier"],
        tier_num=service_subject["tier_num"],
        scopes=service_subject["scopes"],
        module="memoria",
        action="process",
        capability_token="test-svc-token-12345",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2"
    )

    # Make authorization decision
    decision = await middleware.authorize_request(request)

    # Verify span attributes
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No authz.check spans found"

    span = authz_spans[0]
    attrs = span.attributes

    # Verify service account is properly identified
    assert attrs["lukhas.subject"] == "lukhas:svc:orchestrator"
    assert attrs["lukhas.tier"] == "root_dev"
    assert attrs["lukhas.decision"] == "allow", "Service account should be allowed"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_performance_tracking(telemetry_capture, test_subjects):
    """Test that authorization performance metrics are captured in spans."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    trusted_subject = test_subjects["trusted"]
    request = AuthzRequest(
        subject=trusted_subject["subject"],
        tier=trusted_subject["tier"],
        tier_num=trusted_subject["tier_num"],
        scopes=trusted_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token="test-token-12345",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2"
    )

    # Make authorization decision
    decision = await middleware.authorize_request(request)

    # Verify performance tracking
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No authz.check spans found"

    span = authz_spans[0]
    attrs = span.attributes

    # Verify decision time is tracked
    assert "lukhas.decision_time_ms" in attrs, "Missing decision_time_ms attribute"
    decision_time = attrs["lukhas.decision_time_ms"]
    assert isinstance(decision_time, (int, float)), "Decision time should be numeric"
    assert decision_time >= 0, "Decision time should be non-negative"

    # Verify span duration is reasonable (< 1 second for this test)
    assert span.duration_ms < 1000, f"Authorization took too long: {span.duration_ms}ms"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_error_handling(telemetry_capture, test_subjects):
    """Test that authorization errors are properly captured in spans."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Build request with invalid token scenario
    trusted_subject = test_subjects["trusted"]
    request = AuthzRequest(
        subject=trusted_subject["subject"],
        tier=trusted_subject["tier"],
        tier_num=trusted_subject["tier_num"],
        scopes=trusted_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token="invalid-token",  # This should cause token validation to fail
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2"
    )

    # Make authorization decision (should handle error gracefully)
    decision = await middleware.authorize_request(request)

    # Verify span was still emitted even with error
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No authz.check spans found even with error"

    span = authz_spans[0]

    # Verify error is reflected in span
    assert span.status == "ERROR", f"Expected ERROR status for invalid token, got {span.status}"
    assert span.attributes["lukhas.decision"] == "deny", "Expected deny for invalid token"

    # Verify error reason is captured
    reason = span.attributes.get("lukhas.reason", "")
    assert "token" in reason.lower() or "invalid" in reason.lower(), f"Expected token error reason, got: {reason}"


@pytest.mark.telemetry
def test_authz_span_compatibility_with_existing_tests(telemetry_capture):
    """Test that new telemetry captures are compatible with existing telemetry test format."""
    from .conftest import temp_span_dump, CapturedSpan

    # Create a sample span like those expected by existing tests
    sample_span = CapturedSpan(
        name="authz.check",
        attributes={
            "lukhas.subject": "lukhas:user:test",
            "lukhas.module": "memoria",
            "lukhas.decision": "allow",
            "lukhas.reason": "Policy checks passed"
        },
        status="OK",
        status_message=None,
        duration_ms=15.5,
        trace_id="12345678901234567890123456789012",
        span_id="1234567890123456"
    )

    # Test compatibility with temp dump format
    with temp_span_dump([sample_span]) as dump_path:
        assert dump_path.exists(), "Span dump file should be created"

        # Verify it can be loaded by existing test infrastructure
        import json
        with open(dump_path) as f:
            data = json.load(f)

        assert "spans" in data, "Dump should contain spans key"
        assert len(data["spans"]) == 1, "Should contain one span"

        span_data = data["spans"][0]
        assert span_data["name"] == "authz.check", "Span name should be preserved"
        assert "lukhas.subject" in span_data["attributes"], "Attributes should be preserved"


if __name__ == "__main__":
    # Run just authorization telemetry tests when executed directly
    pytest.main(["-v", "-m", "telemetry", __file__])