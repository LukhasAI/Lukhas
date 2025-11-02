"""
Unit tests for Guardian metrics observability.

Tests Prometheus metric recording for policy decisions, denial reasons,
latency tracking, and cardinality controls.
"""

import pytest

from observability.guardian_metrics import (
    _cap_reason,
    _normalize_route,
    get_decision_stats,
    record_decision,
    record_rule_evaluation,
    set_policy_version,
)


class TestGuardianMetrics:
    """Test suite for Guardian metrics."""

    def test_cap_reason_deny_rule(self):
        """Test capping of deny rule matched reasons."""
        reason = "deny_rule_matched:R-001-VeryLongRuleIdentifier"
        capped = _cap_reason(reason)

        # Should normalize to just "deny_rule_matched"
        assert capped == "deny_rule_matched"

    def test_cap_reason_default_deny(self):
        """Test default_deny reason handling."""
        assert _cap_reason("default_deny") == "default_deny"

    def test_cap_reason_scope_insufficient(self):
        """Test scope-related reasons."""
        assert _cap_reason("insufficient scope for operation") == "insufficient_scope"
        assert _cap_reason("missing required scope") == "insufficient_scope"

    def test_cap_reason_rate_limit(self):
        """Test rate limit reasons."""
        assert _cap_reason("rate_limit exceeded") == "rate_limit_exceeded"

    def test_cap_reason_truncation(self):
        """Test long reason truncation."""
        long_reason = "x" * 100
        capped = _cap_reason(long_reason, max_length=64)

        # Should be truncated
        assert len(capped) <= 64

    def test_cap_reason_empty(self):
        """Test empty reason handling."""
        assert _cap_reason("") == "unknown"
        assert _cap_reason(None) == "unknown"

    def test_normalize_route_embeddings(self):
        """Test route normalization for embeddings endpoint."""
        assert _normalize_route("/v1/embeddings") == "/v1/embeddings"
        assert _normalize_route("/v1/embeddings/batch") == "/v1/embeddings"

    def test_normalize_route_responses(self):
        """Test route normalization for responses endpoint."""
        assert _normalize_route("/v1/responses") == "/v1/responses"
        assert _normalize_route("/v1/responses/stream") == "/v1/responses"

    def test_normalize_route_health(self):
        """Test route normalization for health endpoints."""
        assert _normalize_route("/healthz") == "/health"
        assert _normalize_route("/readyz") == "/health"

    def test_normalize_route_query_params(self):
        """Test query parameter stripping."""
        route = "/v1/models?limit=10&offset=20"
        normalized = _normalize_route(route)

        assert "?" not in normalized
        assert "limit" not in normalized

    def test_normalize_route_unknown(self):
        """Test unknown route handling."""
        assert _normalize_route("/custom/endpoint") == "/custom/endpoint"
        assert _normalize_route("") == "unknown"

    def test_record_decision_allow(self):
        """Test recording allow decision."""
        # Should not raise exception
        record_decision(
            allow=True,
            scope="dreams:write",
            route="/v1/dreams",
            duration_seconds=0.001,
        )

    def test_record_decision_deny(self):
        """Test recording deny decision with reason."""
        # Should not raise exception
        record_decision(
            allow=False,
            scope="dreams:restricted",
            route="/v1/dreams",
            reason="deny_rule_matched:R-002",
            duration_seconds=0.002,
        )

    def test_record_rule_evaluation(self):
        """Test recording rule evaluation."""
        # Should not raise exception
        record_rule_evaluation(rule_id="R-001-AllowDreamCreate", effect="Allow")
        record_rule_evaluation(rule_id="R-002-DenyRestricted", effect="Deny")

    def test_set_policy_version(self):
        """Test setting policy version gauge."""
        # Should not raise exception
        set_policy_version(etag="abc123def456", tenant_id="acme-corp")
        set_policy_version(etag="xyz789", tenant_id=None)

    def test_get_decision_stats(self):
        """Test getting decision statistics summary."""
        stats = get_decision_stats()

        assert isinstance(stats, dict)
        assert "metrics_enabled" in stats

    def test_record_decision_no_optional_params(self):
        """Test recording decision with minimal params."""
        # Should handle missing optional params gracefully
        record_decision(allow=True)
        record_decision(allow=False, reason="default_deny")

    def test_record_decision_long_route(self):
        """Test recording decision with very long route."""
        long_route = "/v1/custom/" + "x" * 100
        # Should not raise exception (route will be normalized/truncated)
        record_decision(allow=True, route=long_route)
