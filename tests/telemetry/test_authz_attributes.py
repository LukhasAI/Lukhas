"""
Authorization Span Attribute Validation Tests

Detailed tests for validating that authorization spans contain all required
attributes according to Matrix contract specifications and OpenTelemetry
semantic conventions.

These tests ensure:
1. All required LUKHAS-specific attributes are present
2. OpenTelemetry semantic conventions are followed
3. Attribute values are correctly formatted and typed
4. Contract compliance across different authorization scenarios
"""

import sys
from pathlib import Path

import pytest

# Add tools directory to path for importing authorization middleware
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from matrix_authz_middleware import AuthzRequest, MatrixAuthzMiddleware


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_required_lukhas_attributes(telemetry_capture, test_subjects):
    """Test that all required LUKHAS-specific attributes are present in authz spans."""
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
        region="us-west-2",
    )

    await middleware.authorize_request(request)

    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No authz.check spans found"

    span = authz_spans[0]
    attrs = span.attributes

    # Required LUKHAS authorization attributes
    required_attrs = [
        "subject",
        "tier",
        "tier_num",
        "scopes",
        "module",
        "action",
        "decision",
        "reason",
        "policy_sha",
        "contract_sha",
        "capability_id",
        "mfa_used",
        "region",
        "decision_time_ms",
    ]

    for attr in required_attrs:
        assert attr in attrs, f"Missing required attribute: {attr}"

    # Verify attribute types
    assert isinstance(attrs["tier_num"], int), "tier_num should be integer"
    assert isinstance(attrs["mfa_used"], bool), "mfa_used should be boolean"
    assert isinstance(attrs["decision_time_ms"], (int, float)), "decision_time_ms should be numeric"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_scope_formatting(telemetry_capture, test_subjects):
    """Test that scopes are properly formatted in span attributes."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    trusted_subject = test_subjects["trusted"]
    request = AuthzRequest(
        subject=trusted_subject["subject"],
        tier=trusted_subject["tier"],
        tier_num=trusted_subject["tier_num"],
        scopes=trusted_subject["scopes"],  # ["memoria.read", "memoria.store", "memoria.fold"]
        module="memoria",
        action="recall",
        capability_token="test-token-12345",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2",
    )

    await middleware.authorize_request(request)

    authz_spans = telemetry_capture.get_authz_spans()
    span = authz_spans[0]
    attrs = span.attributes

    # Verify scopes are properly formatted as comma-separated string
    scopes_attr = attrs["scopes"]
    assert isinstance(scopes_attr, str), "Scopes should be formatted as string"

    # Verify all expected scopes are present
    expected_scopes = set(trusted_subject["scopes"])
    actual_scopes = set(scopes_attr.split(","))
    assert expected_scopes == actual_scopes, f"Expected scopes {expected_scopes}, got {actual_scopes}"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_subject_patterns(telemetry_capture, test_subjects):
    """Test that different subject patterns are correctly captured."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Test user subject
    user_subject = test_subjects["trusted"]
    user_request = AuthzRequest(
        subject=user_subject["subject"],  # "lukhas:user:test_trusted"
        tier=user_subject["tier"],
        tier_num=user_subject["tier_num"],
        scopes=user_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token="test-token-12345",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2",
    )

    await middleware.authorize_request(user_request)

    # Test service subject
    service_subject = test_subjects["service"]
    service_request = AuthzRequest(
        subject=service_subject["subject"],  # "lukhas:svc:orchestrator"
        tier=service_subject["tier"],
        tier_num=service_subject["tier_num"],
        scopes=service_subject["scopes"],
        module="memoria",
        action="process",
        capability_token="test-svc-token-12345",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2",
    )

    await middleware.authorize_request(service_request)

    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 2, "Expected spans for both user and service requests"

    # Find user and service spans
    user_span = next((s for s in authz_spans if "user:test_trusted" in s.attributes["subject"]), None)
    service_span = next((s for s in authz_spans if "svc:orchestrator" in s.attributes["subject"]), None)

    assert user_span is not None, "User span not found"
    assert service_span is not None, "Service span not found"

    # Verify subject formats
    assert user_span.attributes["subject"] == "lukhas:user:test_trusted"
    assert service_span.attributes["subject"] == "lukhas:svc:orchestrator"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_tier_consistency(telemetry_capture, test_subjects):
    """Test that tier information is consistent between string and numeric values."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Test different tier levels
    tier_mappings = {"guest": 0, "friend": 2, "trusted": 3, "service": 5}  # root_dev

    for subject_type, expected_tier_num in tier_mappings.items():
        if subject_type == "service":
            subject_data = test_subjects["service"]
        else:
            subject_data = test_subjects[subject_type]

        request = AuthzRequest(
            subject=subject_data["subject"],
            tier=subject_data["tier"],
            tier_num=subject_data["tier_num"],
            scopes=subject_data["scopes"],
            module="memoria",
            action="recall",
            capability_token=f"test-token-{subject_type}",
            mfa_verified=False,
            webauthn_verified=True,
            region="us-west-2",
        )

        await middleware.authorize_request(request)

    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= len(tier_mappings), f"Expected at least {len(tier_mappings)} spans"

    # Verify tier consistency for each span
    for span in authz_spans:
        attrs = span.attributes
        tier_str = attrs["tier"]
        tier_num = attrs["tier_num"]

        # Verify tier_num matches expected mapping
        if tier_str == "guest":
            assert tier_num == 0, f"Guest tier should be 0, got {tier_num}"
        elif tier_str == "friend":
            assert tier_num == 2, f"Friend tier should be 2, got {tier_num}"
        elif tier_str == "trusted":
            assert tier_num == 3, f"Trusted tier should be 3, got {tier_num}"
        elif tier_str == "root_dev":
            assert tier_num == 5, f"Root_dev tier should be 5, got {tier_num}"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_decision_values(telemetry_capture, test_subjects):
    """Test that decision attribute values are standardized."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Test allow decision
    trusted_subject = test_subjects["trusted"]
    allow_request = AuthzRequest(
        subject=trusted_subject["subject"],
        tier=trusted_subject["tier"],
        tier_num=trusted_subject["tier_num"],
        scopes=trusted_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token="test-token-allow",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2",
    )

    await middleware.authorize_request(allow_request)

    # Test deny decision
    guest_subject = test_subjects["guest"]
    deny_request = AuthzRequest(
        subject=guest_subject["subject"],
        tier=guest_subject["tier"],
        tier_num=guest_subject["tier_num"],
        scopes=guest_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token="test-token-deny",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2",
    )

    await middleware.authorize_request(deny_request)

    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 2, "Expected spans for both allow and deny scenarios"

    # Verify decision values are standardized
    decisions = [span.attributes["decision"] for span in authz_spans]
    valid_decisions = {"allow", "deny"}

    for decision in decisions:
        assert decision in valid_decisions, f"Invalid decision value: {decision}. Must be 'allow' or 'deny'"

    # Verify we have both allow and deny decisions
    assert "allow" in decisions, "No allow decision found"
    assert "deny" in decisions, "No deny decision found"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_capability_id_masking(telemetry_capture, test_subjects):
    """Test that capability IDs are properly masked for security."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    full_token = "eyJ2ZXJzaW9uIjoyLCJsb2NhdGlvbiI6Imx1a2hhcy1tYXRyaXgtYXV0aHoiLCJpZGVudGlmaWVyIjoibHVraGFzOnVzZXI6dGVzdDp0cnVzdGVkOjE3NTg4OTIyNjEi"

    trusted_subject = test_subjects["trusted"]
    request = AuthzRequest(
        subject=trusted_subject["subject"],
        tier=trusted_subject["tier"],
        tier_num=trusted_subject["tier_num"],
        scopes=trusted_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token=full_token,
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2",
    )

    await middleware.authorize_request(request)

    authz_spans = telemetry_capture.get_authz_spans()
    span = authz_spans[0]
    attrs = span.attributes

    # Verify capability ID is masked
    capability_id = attrs["capability_id"]
    assert capability_id != full_token, "Capability token should be masked"
    assert capability_id.endswith("..."), "Capability ID should end with ellipsis"
    assert len(capability_id) < len(full_token), "Masked capability ID should be shorter than original"

    # Verify it starts with the expected prefix
    expected_prefix = full_token[:16]
    assert capability_id.startswith(expected_prefix), f"Capability ID should start with {expected_prefix}"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_contract_sha_presence(telemetry_capture, test_subjects, matrix_contract_loader):
    """Test that contract SHA is included for auditability."""
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
        region="us-west-2",
    )

    await middleware.authorize_request(request)

    authz_spans = telemetry_capture.get_authz_spans()
    span = authz_spans[0]
    attrs = span.attributes

    # Verify contract SHA is present
    assert "contract_sha" in attrs, "Missing contract_sha attribute"
    contract_sha = attrs["contract_sha"]

    assert isinstance(contract_sha, str), "Contract SHA should be string"
    assert len(contract_sha) > 0, "Contract SHA should not be empty"

    # Contract SHA should be hex-like (for SHA256 hash)
    assert len(contract_sha) >= 8, "Contract SHA should be at least 8 characters (truncated SHA)"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_region_tracking(telemetry_capture, test_subjects):
    """Test that region information is properly tracked."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    trusted_subject = test_subjects["trusted"]

    # Test different regions
    regions = ["us-west-2", "eu-central-1", "ap-southeast-1", None]

    for region in regions:
        request = AuthzRequest(
            subject=trusted_subject["subject"],
            tier=trusted_subject["tier"],
            tier_num=trusted_subject["tier_num"],
            scopes=trusted_subject["scopes"],
            module="memoria",
            action="recall",
            capability_token=f"test-token-{region or 'none'}",
            mfa_verified=False,
            webauthn_verified=True,
            region=region,
        )

        await middleware.authorize_request(request)

    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= len(regions), f"Expected at least {len(regions)} spans"

    # Verify region attribute handling
    for span in authz_spans:
        attrs = span.attributes
        assert "region" in attrs, "Missing region attribute"

        region_attr = attrs["region"]

        # Region should be string or "unknown" for None values
        assert isinstance(region_attr, str), "Region should be string"
        if region_attr != "unknown":
            # Should be a valid AWS region format
            assert "-" in region_attr, f"Invalid region format: {region_attr}"


@pytest.mark.telemetry
@pytest.mark.asyncio
async def test_authz_span_performance_attribute_ranges(telemetry_capture, test_subjects):
    """Test that performance attributes are within reasonable ranges."""
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
        region="us-west-2",
    )

    await middleware.authorize_request(request)

    authz_spans = telemetry_capture.get_authz_spans()
    span = authz_spans[0]
    attrs = span.attributes

    # Verify decision time is reasonable
    decision_time_ms = attrs["decision_time_ms"]
    assert 0 <= decision_time_ms <= 10000, f"Decision time {decision_time_ms}ms seems unreasonable"

    # Verify span duration is reasonable
    assert 0 <= span.duration_ms <= 10000, f"Span duration {span.duration_ms}ms seems unreasonable"


if __name__ == "__main__":
    # Run just authorization attribute tests when executed directly
    pytest.main(["-v", "-m", "telemetry", __file__])
