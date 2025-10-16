#!/usr/bin/env python3
"""
Telemetry Authorization Smoke Tests

Tests that authorization operations emit proper OpenTelemetry spans
with required attributes for auditing and observability.
"""

import hashlib
import json
from typing import Any, Dict, List

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# Test configuration
TEST_SPANS: List[Any] = []
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


def create_mock_contract(module: str, tiers: List[str], scopes: List[str], webauthn: bool = False) -> Dict[str, Any]:
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


def simulate_authz_check(tracer, input_data: Dict[str, Any], contract: Dict[str, Any], allow: bool = True) -> Dict[str, Any]:
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
            "lukhas.subject": input_data["subject"],
            "lukhas.tier": input_data["tier"],
            "lukhas.tier_num": input_data.get("tier_num", 0),
            "lukhas.scopes": ",".join(input_data.get("scopes", [])),
            "lukhas.module": input_data["module"],
            "lukhas.action": input_data["action"],
            "lukhas.decision": "allow" if allow else "deny",
            "lukhas.reason": "Authorized by tier and scope" if allow else "Insufficient tier level",
            "lukhas.policy_sha": policy_sha,
            "lukhas.contract_sha": contract_sha,
            "lukhas.capability_id": masked_capability,
            "lukhas.mfa_used": input_data.get("mfa_used", False),
            "lukhas.region": input_data.get("region", "us-west-2"),
            "lukhas.decision_time_ms": 42,
        })

        # Set span status
        if allow:
            span.set_attribute("lukhas.status", "success")
        else:
            span.set_attribute("lukhas.status", "denied")

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
        assert attrs["lukhas.subject"] == "lukhas:user:test123"
        assert attrs["lukhas.tier"] == "trusted"
        assert attrs["lukhas.tier_num"] == 3
        assert attrs["lukhas.scopes"] == "memoria.read,memoria.fold"
        assert attrs["lukhas.module"] == "memoria"
        assert attrs["lukhas.action"] == "read"
        assert attrs["lukhas.decision"] == "allow"
        assert "lukhas.policy_sha" in attrs
        assert "lukhas.contract_sha" in attrs
        assert attrs["lukhas.capability_id"] == "cap_1234***cdef"  # Masked
        assert attrs["lukhas.mfa_used"] == False
        assert attrs["lukhas.region"] == "us-west-2"
        assert attrs["lukhas.decision_time_ms"] == 42

    def test_authz_deny_span_attributes(self, telemetry_setup):
        """Test that denied authorization emits proper span attributes."""
        tracer, exporter = telemetry_setup

        # Create test data - guest trying to access trusted resource
        contract = create_mock_contract("lukhas.governance", ["inner_circle", "root_dev"], ["lukhas.governance.enforce"])
        input_data = {
            "subject": "lukhas:user:guest123",
            "tier": "guest",
            "tier_num": 0,
            "scopes": ["lukhas.governance.enforce"],
            "module": "lukhas.governance",
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
        assert attrs["lukhas.subject"] == "lukhas:user:guest123"
        assert attrs["lukhas.tier"] == "guest"
        assert attrs["lukhas.tier_num"] == 0
        assert attrs["lukhas.decision"] == "deny"
        assert attrs["lukhas.reason"] == "Insufficient tier level"
        assert attrs["lukhas.module"] == "lukhas.governance"
        assert attrs["lukhas.action"] == "enforce"
        assert attrs["lukhas.capability_id"] == "cap_abcd***7890"  # Masked

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

        assert attrs["lukhas.tier"] == "inner_circle"
        assert attrs["lukhas.mfa_used"] == True
        assert attrs["lukhas.module"] == "identity"
        assert attrs["lukhas.decision"] == "allow"

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

        assert attrs["lukhas.subject"] == "lukhas:svc:orchestration"
        assert attrs["lukhas.module"] == "orchestration"
        assert attrs["lukhas.decision"] == "allow"

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

        for i in range(10):
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
        hash1 = dict(spans[0].attributes)["lukhas.contract_sha"]
        hash2 = dict(spans[1].attributes)["lukhas.contract_sha"]
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
        capability_id = attrs["lukhas.capability_id"]
        assert "***" in capability_id
        assert not capability_id.startswith("cap_very_sensitive_token")
        assert capability_id.endswith("3456789"[-4:])  # Last 4 chars preserved


if __name__ == "__main__":
    pytest.main([__file__])
