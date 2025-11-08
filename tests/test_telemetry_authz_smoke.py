#!/usr/bin/env python3
"""
Telemetry Authorization Smoke Tests

Tests that authorization operations emit proper OpenTelemetry spans
with required attributes for auditing and observability.
"""

import hashlib
import json
from typing import Any

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# Test configuration
TEST_SPANS: list[Any] = []
SPAN_EXPORTER = InMemorySpanExporter()


@pytest.fixture(scope="function")
def telemetry_setup():
    """Set up OpenTelemetry for testing."""
    # Create fresh components for each test
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)

    # Get tracer from this provider
    tracer = provider.get_tracer(__name__)

    yield tracer, exporter

    # No cleanup needed - each test gets fresh components


def create_mock_contract(module: str, tiers: list[str], scopes: list[str], webauthn: bool = False) -> dict[str, Any]:
    """Create a mock Matrix contract."""
    return {
        "schema_version": "1.0.0",
        "module": f"lukhas.{module}",
        "identity": {
            "requires_auth": True,
            "accepted_subjects": ["lukhas:user:*"],
            "required_tiers": tiers,
            "required_tiers_numeric": [{"guest": 0, "visitor": 1, "friend": 2, "trusted": 3, "inner_circle": 4, "root_dev": 5}[t] for t in tiers],
            "scopes": scopes,
            "webauthn_required": webauthn,
            "api_policies": []
        }
    }


def simulate_authz_check(tracer, input_data: dict[str, Any], contract: dict[str, Any], allow: bool = True) -> dict[str, Any]:
    """Simulate an authorization check with telemetry."""
    with tracer.start_as_current_span("authz.check") as span:
        # Compute contract hash
        contract_json = json.dumps(contract, sort_keys=True)
        contract_sha = hashlib.sha256(contract_json.encode()).hexdigest()

        # Compute policy hash (mock)
        policy_sha = "sha256:mock_policy_hash"

        # Mask capability token ID
        capability_id = input_data.get("capability_id", "cap_1234567890abcdef")
        masked_capability = f"{capability_id[:8]}***{capability_id[-4:]}"

        # Set span attributes
        span.set_attributes({
            "subject": input_data["subject"],
            "tier": input_data["tier"],
            "tier_num": input_data.get("tier_num", 0),
            "scopes": ",".join(input_data.get("scopes", [])),
            "module": input_data["module"],
            "action": input_data["action"],
            "decision": "allow" if allow else "deny",
            "reason": "Authorized by tier and scope" if allow else "Insufficient tier level",
            "policy_sha": policy_sha,
            "contract_sha": contract_sha,
            "capability_id": masked_capability,
            "mfa_used": input_data.get("mfa_used", False),
            "region": input_data.get("region", "us-west-2"),
            "decision_time_ms": 42,
        })

        # Set span status
        if allow:
            span.set_attribute("status", "success")
        else:
            span.set_attribute("status", "denied")

        return {
            "allow": allow,
            "decision": "allow" if allow else "deny",
            "span_id": span.get_span_context().span_id,
        }


class TestAuthzTelemetrySmoke:
    """Authorization telemetry smoke tests."""

    def test_authz_allow_span_attributes(self, telemetry_setup):
        """Test that allowed authorization emits proper span attributes."""
        tracer, exporter = telemetry_setup

        # Create test data
        contract = create_mock_contract("memoria", ["trusted"], ["memoria.read", "memoria.fold"])
        input_data = {
            "subject": "lukhas:user:test123",
            "tier": "trusted",
            "tier_num": 3,
            "scopes": ["memoria.read", "memoria.fold"],
            "module": "memoria",
            "action": "read",
            "capability_id": "cap_1234567890abcdef",
            "mfa_used": False,
            "region": "us-west-2"
        }

        # Simulate authorization
        simulate_authz_check(tracer, input_data, contract, allow=True)

        # Check that span was created
        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        span = spans[0]

        # Verify span name
        assert span.name == "authz.check"

        # Verify required attributes
        attrs = dict(span.attributes)
        assert attrs["subject"] == "lukhas:user:test123"
        assert attrs["tier"] == "trusted"
        assert attrs["tier_num"] == 3
        assert attrs["scopes"] == "memoria.read,memoria.fold"
        assert attrs["module"] == "memoria"
        assert attrs["action"] == "read"
        assert attrs["decision"] == "allow"
        assert "policy_sha" in attrs
        assert "contract_sha" in attrs
        assert attrs["capability_id"] == "cap_1234***cdef"  # Masked
        assert attrs["mfa_used"] is False
        assert attrs["region"] == "us-west-2"
        assert attrs["decision_time_ms"] == 42

    def test_authz_deny_span_attributes(self, telemetry_setup):
        """Test that denied authorization emits proper span attributes."""
        tracer, exporter = telemetry_setup

        # Create test data - guest trying to access trusted resource
        contract = create_mock_contract("governance", ["inner_circle", "root_dev"], ["governance.enforce"])
        input_data = {
            "subject": "lukhas:user:guest123",
            "tier": "guest",
            "tier_num": 0,
            "scopes": ["governance.enforce"],
            "module": "governance",
            "action": "enforce",
            "capability_id": "cap_abcdef1234567890",
            "mfa_used": False,
            "region": "eu-west-1"
        }

        # Simulate authorization denial
        simulate_authz_check(tracer, input_data, contract, allow=False)

        # Check that span was created
        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        span = spans[0]

        # Verify span name
        assert span.name == "authz.check"

        # Verify required attributes
        attrs = dict(span.attributes)
        assert attrs["subject"] == "lukhas:user:guest123"
        assert attrs["tier"] == "guest"
        assert attrs["tier_num"] == 0
        assert attrs["decision"] == "deny"
        assert attrs["reason"] == "Insufficient tier level"
        assert attrs["module"] == "governance"
        assert attrs["action"] == "enforce"
        assert attrs["capability_id"] == "cap_abcd***7890"  # Masked

    def test_authz_webauthn_required_span(self, telemetry_setup):
        """Test spans for WebAuthn-required modules."""
        tracer, exporter = telemetry_setup

        # Create test data for WebAuthn-required module
        contract = create_mock_contract("identity", ["trusted", "inner_circle"], ["identity.login"], webauthn=True)
        input_data = {
            "subject": "lukhas:user:secure123",
            "tier": "inner_circle",
            "tier_num": 4,
            "scopes": ["identity.login"],
            "module": "identity",
            "action": "login",
            "capability_id": "cap_secure_token_123",
            "mfa_used": True,
            "region": "us-east-1"
        }

        # Simulate authorization
        simulate_authz_check(tracer, input_data, contract, allow=True)

        # Check span attributes
        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        span = spans[0]
        attrs = dict(span.attributes)

        assert attrs["tier"] == "inner_circle"
        assert attrs["mfa_used"] is True
        assert attrs["module"] == "identity"
        assert attrs["decision"] == "allow"

    def test_authz_service_account_span(self, telemetry_setup):
        """Test spans for service account access."""
        tracer, exporter = telemetry_setup

        # Create test data for service account
        contract = create_mock_contract("orchestration", ["friend", "trusted"], ["orchestration.dispatch"])
        contract["identity"]["accepted_subjects"].append("lukhas:svc:orchestration")

        input_data = {
            "subject": "lukhas:svc:orchestration",
            "tier": "trusted",
            "tier_num": 3,
            "scopes": ["orchestration.dispatch"],
            "module": "orchestration",
            "action": "dispatch",
            "capability_id": "svc_token_orchestration",
            "mfa_used": False,
            "region": "us-west-2"
        }

        # Simulate authorization
        simulate_authz_check(tracer, input_data, contract, allow=True)

        # Check span attributes
        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        span = spans[0]
        attrs = dict(span.attributes)

        assert attrs["subject"] == "lukhas:svc:orchestration"
        assert attrs["module"] == "orchestration"
        assert attrs["decision"] == "allow"

    def test_authz_span_performance(self, telemetry_setup):
        """Test that authorization telemetry has minimal overhead."""
        tracer, exporter = telemetry_setup

        contract = create_mock_contract("api", ["visitor", "friend"], ["api.query"])
        input_data = {
            "subject": "lukhas:user:performance_test",
            "tier": "friend",
            "tier_num": 2,
            "scopes": ["api.query"],
            "module": "api",
            "action": "query",
            "capability_id": "cap_perf_test_123",
            "mfa_used": False,
            "region": "us-west-2"
        }

        # Simulate multiple authorization checks
        import time
        start_time = time.time()

        for _i in range(10):
            simulate_authz_check(tracer, input_data, contract, allow=True)

        duration = time.time() - start_time

        # Check that overhead is minimal (should be sub-millisecond per call)
        assert duration < 0.1  # 100ms for 10 calls = 10ms per call max
        spans = exporter.get_finished_spans()
        assert len(spans) == 10

    def test_authz_contract_hash_stability(self, telemetry_setup):
        """Test that contract hashes are stable and deterministic."""
        tracer, exporter = telemetry_setup

        contract = create_mock_contract("test", ["friend"], ["test.action"])
        input_data = {
            "subject": "lukhas:user:hash_test",
            "tier": "friend",
            "tier_num": 2,
            "scopes": ["test.action"],
            "module": "test",
            "action": "action",
        }

        # Simulate authorization twice
        simulate_authz_check(tracer, input_data, contract, allow=True)
        simulate_authz_check(tracer, input_data, contract, allow=True)

        # Check that contract hashes are identical
        spans = exporter.get_finished_spans()
        assert len(spans) == 2
        hash1 = dict(spans[0].attributes)["contract_sha"]
        hash2 = dict(spans[1].attributes)["contract_sha"]
        assert hash1 == hash2

    def test_authz_span_security_masking(self, telemetry_setup):
        """Test that sensitive data is properly masked in spans."""
        tracer, exporter = telemetry_setup

        contract = create_mock_contract("security", ["inner_circle"], ["security.audit"])
        input_data = {
            "subject": "lukhas:user:security_audit",
            "tier": "inner_circle",
            "tier_num": 4,
            "scopes": ["security.audit"],
            "module": "security",
            "action": "audit",
            "capability_id": "cap_very_sensitive_token_123456789",
        }

        # Simulate authorization
        simulate_authz_check(tracer, input_data, contract, allow=True)

        # Check span attributes
        spans = exporter.get_finished_spans()
        assert len(spans) == 1
        span = spans[0]
        attrs = dict(span.attributes)

        # Verify sensitive data is masked
        capability_id = attrs["capability_id"]
        assert "***" in capability_id
        assert not capability_id.startswith("cap_very_sensitive_token")
        assert capability_id.endswith("3456789"[-4:])  # Last 4 chars preserved


if __name__ == "__main__":
    pytest.main([__file__])
