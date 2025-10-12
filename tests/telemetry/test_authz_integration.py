"""
Authorization Telemetry Integration Tests

Integration tests that simulate real authorization workflows from end-to-end,
validating that telemetry is properly emitted throughout the complete authorization
pipeline including middleware integration, policy evaluation, and error handling.

These tests validate:
1. Complete authorization workflows with telemetry
2. Multi-step authorization processes (e.g., step-up auth)
3. Authorization in error conditions
4. Integration with existing authorization test matrices
5. Performance characteristics under realistic load
"""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add tools directory to path for importing authorization components
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lukhas.tools"))

from matrix_authz_middleware import AuthzRequest, MatrixAuthzMiddleware
from run_authz_tests import AuthzTestRunner


@pytest.mark.telemetry
@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_authorization_with_telemetry(telemetry_capture, authz_test_scenarios, test_subjects):
    """Test complete end-to-end authorization flows with telemetry collection."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    for scenario in authz_test_scenarios:
        subject_data = test_subjects[scenario["subject_type"]]

        request = AuthzRequest(
            subject=subject_data["subject"],
            tier=subject_data["tier"],
            tier_num=subject_data["tier_num"],
            scopes=subject_data["scopes"],
            module=scenario["module"],
            action=scenario["action"],
            capability_token=f"test-token-{scenario['name']}",
            mfa_verified=scenario.get("requires_mfa", False),
            webauthn_verified=True,
            region="us-west-2"
        )

        # Execute authorization with telemetry capture
        decision = await middleware.authorize_request(request)

        # Verify decision matches expected outcome
        assert decision.allowed == scenario["expected_allowed"], (
            f"Scenario {scenario['name']}: expected {scenario['expected_allowed']}, "
            f"got {decision.allowed}"
        )

    # Verify all scenarios generated spans
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= len(authz_test_scenarios), (
        f"Expected at least {len(authz_test_scenarios)} spans, got {len(authz_spans)}"
    )

    # Verify each scenario has corresponding span with correct attributes
    for scenario in authz_test_scenarios:
        subject_data = test_subjects[scenario["subject_type"]]
        scenario_spans = [
            span for span in authz_spans
            if span.attributes.get("lukhas.subject") == subject_data["subject"]
            and span.attributes.get("lukhas.action") == scenario["action"]
        ]

        assert len(scenario_spans) >= 1, f"No span found for scenario {scenario['name']}"

        span = scenario_spans[0]
        expected_decision = "allow" if scenario["expected_allowed"] else "deny"
        assert span.attributes["lukhas.decision"] == expected_decision, (
            f"Scenario {scenario['name']}: span decision mismatch"
        )


@pytest.mark.telemetry
@pytest.mark.integration
@pytest.mark.asyncio
async def test_middleware_handler_integration_with_telemetry(telemetry_capture, mock_capability_token):
    """Test middleware handler integration with telemetry capture."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Mock the capability token verification to return valid claims
    with patch.object(middleware.verifier, 'verify_capability') as mock_verify:
        mock_verify.return_value = {
            "valid": True,
            "subject": "lukhas:user:test_integration",
            "tier": "trusted",
            "tier_num": 3,
            "scopes": ["memoria.read", "memoria.store"],
            "env": {
                "mfa": False,
                "webauthn_verified": True,
                "device_id": "test-device-123",
                "region": "us-west-2"
            },
            "token": {
                "exp": 1758894061,
                "aud": "lukhas-matrix"
            }
        }

        # Call middleware handler (this simulates HTTP request handling)
        allowed, reason = await middleware.middleware_handler(
            capability_token=mock_capability_token,
            module="memoria",
            action="recall",
            context={"request_id": "test-123"}
        )

        assert allowed is True, f"Expected authorization to succeed, got: {reason}"

    # Verify telemetry was emitted through middleware handler
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No spans emitted through middleware handler"

    span = authz_spans[0]
    attrs = span.attributes

    # Verify middleware handler sets correct attributes
    assert attrs["lukhas.subject"] == "lukhas:user:test_integration"
    assert attrs["lukhas.tier"] == "trusted"
    assert attrs["lukhas.module"] == "memoria"
    assert attrs["lukhas.action"] == "recall"
    assert attrs["lukhas.decision"] == "allow"


@pytest.mark.telemetry
@pytest.mark.integration
@pytest.mark.asyncio
async def test_shadow_mode_telemetry_emission(telemetry_capture, test_subjects):
    """Test that telemetry is emitted even in shadow mode."""
    middleware = MatrixAuthzMiddleware(shadow_mode=True)  # Enable shadow mode

    # Use guest user (would normally be denied)
    guest_subject = test_subjects["guest"]
    request = AuthzRequest(
        subject=guest_subject["subject"],
        tier=guest_subject["tier"],
        tier_num=guest_subject["tier_num"],
        scopes=guest_subject["scopes"],
        module="memoria",
        action="recall",
        capability_token="test-token-shadow",
        mfa_verified=False,
        webauthn_verified=True,
        region="us-west-2"
    )

    # Authorization decision
    decision = await middleware.authorize_request(request)

    # In shadow mode, the actual policy decision is still made and recorded
    assert not decision.allowed, "Guest should still be denied in shadow mode policy evaluation"

    # Verify telemetry is still emitted in shadow mode
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No spans emitted in shadow mode"

    span = authz_spans[0]
    assert span.attributes["lukhas.decision"] == "deny"
    assert span.attributes["lukhas.subject"] == guest_subject["subject"]


@pytest.mark.telemetry
@pytest.mark.integration
@pytest.mark.asyncio
async def test_authorization_with_opa_policy_integration(telemetry_capture, test_subjects):
    """Test authorization with OPA policy integration and telemetry."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Mock OPA evaluation to simulate real policy engine integration
    with patch.object(middleware, '_query_opa') as mock_opa:
        # Simulate OPA response
        mock_opa.return_value = {
            "allow": True,
            "reason": "OPA policy evaluation",
            "policy_sha": "opa_live_12345",
            "decision_metadata": {
                "policy_version": "v1.2.3",
                "evaluation_time_ms": 5.5
            }
        }

        trusted_subject = test_subjects["trusted"]
        request = AuthzRequest(
            subject=trusted_subject["subject"],
            tier=trusted_subject["tier"],
            tier_num=trusted_subject["tier_num"],
            scopes=trusted_subject["scopes"],
            module="memoria",
            action="recall",
            capability_token="test-token-opa",
            mfa_verified=False,
            webauthn_verified=True,
            region="us-west-2"
        )

        decision = await middleware.authorize_request(request)

        # Verify OPA was called
        assert mock_opa.called, "OPA query method should have been called"

        # Verify decision
        assert decision.allowed, "Decision should be allowed from OPA"
        assert decision.policy_sha == "opa_live_12345"

    # Verify telemetry includes OPA-specific attributes
    authz_spans = telemetry_capture.get_authz_spans()
    span = authz_spans[0]
    attrs = span.attributes

    assert attrs["lukhas.policy_sha"] == "opa_live_12345"
    assert attrs["lukhas.reason"] == "OPA policy evaluation"


@pytest.mark.telemetry
@pytest.mark.integration
@pytest.mark.asyncio
async def test_authorization_matrix_test_integration(telemetry_capture):
    """Test integration with existing authorization test matrix."""
    # Load actual authorization test matrix
    matrix_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/authz/memoria_authz.yaml")

    if not matrix_path.exists():
        pytest.skip("Authorization test matrix not found")

    # Create test runner
    runner = AuthzTestRunner(verbose=False)

    # Load test matrix
    test_matrix = runner.load_test_matrix(matrix_path)
    test_cases = test_matrix.get("test_cases", [])

    if not test_cases:
        pytest.skip("No test cases in authorization matrix")

    # Load contract
    contract = runner.load_contract("memoria")

    # Run a subset of test cases with telemetry
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    for test_case in test_cases[:3]:  # Test first 3 cases
        # Build OPA input like the test runner does
        opa_input = runner.build_opa_input(test_case, contract)

        # Convert to AuthzRequest format
        request = AuthzRequest(
            subject=opa_input["subject"],
            tier=opa_input["tier"],
            tier_num=opa_input["tier_num"],
            scopes=opa_input["scopes"],
            module=opa_input["module"],
            action=opa_input["action"],
            capability_token="test-matrix-token",
            mfa_verified=opa_input["env"]["mfa"],
            webauthn_verified=opa_input["env"]["webauthn_verified"],
            region=opa_input["env"]["region"]
        )

        decision = await middleware.authorize_request(request)

        # Verify decision matches test case expectation
        expected = test_case["expected"]
        assert decision.allowed == expected, (
            f"Test case {test_case['name']}: expected {expected}, got {decision.allowed}"
        )

    # Verify telemetry was emitted for all test cases
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 3, "Expected spans for all test cases"


@pytest.mark.telemetry
@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_authorization_telemetry(telemetry_capture, test_subjects):
    """Test telemetry emission under concurrent authorization requests."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Create multiple concurrent authorization requests
    tasks = []
    trusted_subject = test_subjects["trusted"]

    for i in range(5):
        request = AuthzRequest(
            subject=f"{trusted_subject['subject']}_{i}",
            tier=trusted_subject["tier"],
            tier_num=trusted_subject["tier_num"],
            scopes=trusted_subject["scopes"],
            module="memoria",
            action="recall",
            capability_token=f"test-token-concurrent-{i}",
            mfa_verified=False,
            webauthn_verified=True,
            region="us-west-2"
        )

        task = middleware.authorize_request(request)
        tasks.append(task)

    # Execute all requests concurrently
    decisions = await asyncio.gather(*tasks)

    # Verify all decisions succeeded
    for i, decision in enumerate(decisions):
        assert decision.allowed, f"Request {i} should have been allowed"

    # Verify telemetry for all concurrent requests
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 5, f"Expected at least 5 spans, got {len(authz_spans)}"

    # Verify each request has unique subject identifier
    subjects = [span.attributes["lukhas.subject"] for span in authz_spans]
    unique_subjects = set(subjects)
    assert len(unique_subjects) >= 5, "Concurrent requests should have unique subjects"


@pytest.mark.telemetry
@pytest.mark.integration
@pytest.mark.asyncio
async def test_authorization_error_propagation_with_telemetry(telemetry_capture, test_subjects):
    """Test that authorization errors are properly propagated through telemetry."""
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    # Simulate contract loading error
    with patch.object(middleware, 'load_contract') as mock_load:
        mock_load.side_effect = FileNotFoundError("Contract not found")

        trusted_subject = test_subjects["trusted"]
        request = AuthzRequest(
            subject=trusted_subject["subject"],
            tier=trusted_subject["tier"],
            tier_num=trusted_subject["tier_num"],
            scopes=trusted_subject["scopes"],
            module="nonexistent",
            action="test",
            capability_token="test-token-error",
            mfa_verified=False,
            webauthn_verified=True,
            region="us-west-2"
        )

        decision = await middleware.authorize_request(request)

        # Verify error handling
        assert not decision.allowed, "Request should be denied due to error"
        assert "error" in decision.reason.lower(), "Reason should indicate error"

    # Verify error telemetry
    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "Error should still emit span"

    span = authz_spans[0]
    assert span.status == "ERROR", "Span should have ERROR status"
    assert span.attributes["lukhas.decision"] == "deny"
    assert "error" in span.attributes["lukhas.reason"].lower()


@pytest.mark.telemetry
@pytest.mark.integration
def test_telemetry_span_export_format_compatibility(telemetry_capture, test_subjects):
    """Test that telemetry spans can be exported in format compatible with existing infrastructure."""
    # This test ensures our telemetry integration doesn't break existing telemetry processing

    from .conftest import temp_span_dump

    # Generate some test spans
    middleware = MatrixAuthzMiddleware(shadow_mode=False)

    async def generate_test_spans():
        trusted_subject = test_subjects["trusted"]
        request = AuthzRequest(
            subject=trusted_subject["subject"],
            tier=trusted_subject["tier"],
            tier_num=trusted_subject["tier_num"],
            scopes=trusted_subject["scopes"],
            module="memoria",
            action="recall",
            capability_token="test-token-export",
            mfa_verified=False,
            webauthn_verified=True,
            region="us-west-2"
        )

        await middleware.authorize_request(request)

    # Run the async function
    asyncio.run(generate_test_spans())

    authz_spans = telemetry_capture.get_authz_spans()
    assert len(authz_spans) >= 1, "No spans to test export format"

    # Test export compatibility
    with temp_span_dump(authz_spans) as dump_path:
        # Verify the dump can be loaded and has expected structure
        with open(dump_path) as f:
            exported_data = json.load(f)

        assert "spans" in exported_data, "Export should contain spans"
        assert len(exported_data["spans"]) == len(authz_spans), "All spans should be exported"

        # Verify required fields are present in exported format
        for exported_span in exported_data["spans"]:
            assert "name" in exported_span
            assert "attributes" in exported_span
            assert "trace_id" in exported_span
            assert "span_id" in exported_span

            # Verify authz-specific attributes are preserved
            if exported_span["name"] == "authz.check":
                attrs = exported_span["attributes"]
                assert "lukhas.subject" in attrs
                assert "lukhas.decision" in attrs
                assert "lukhas.module" in attrs


if __name__ == "__main__":
    # Run just authorization integration tests when executed directly
    pytest.main(["-v", "-m", "telemetry and integration", __file__])
