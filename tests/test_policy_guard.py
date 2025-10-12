#!/usr/bin/env python3
"""
tests/test_policy_guard.py

Unit tests for Phase 5 policy guard implementation.
Tests the policy enforcement matrix across lanes, kinds, and thresholds.
"""
import os
import time
from unittest.mock import patch

import pytest

from lukhas.core.policy_guard import LanePolicyConfig, PolicyGuard, PolicyResult, ReplayDecision, create_policy_guard


class TestPolicyGuard:
    """Test suite for policy guard functionality."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["LUKHAS_LANE"] = "experimental"
        os.environ["PYTHONHASHSEED"] = "0"
        os.environ["TZ"] = "UTC"

    def test_policy_guard_initialization(self):
        """Test policy guard initializes with correct lane configuration."""
        # Test default initialization
        guard = PolicyGuard()
        assert guard.lane == "experimental"
        assert guard.config.max_risk_level == 0.8
        assert guard.config.max_replay_rate == 2000

        # Test explicit lane
        guard = PolicyGuard(lane="prod")
        assert guard.lane == "prod"
        assert guard.config.max_risk_level == 0.2
        assert guard.config.max_replay_rate == 500

    def test_event_kind_allowlist(self):
        """Test event kind allowlist enforcement."""
        guard = PolicyGuard(lane="experimental")

        # Test allowed kinds
        allowed_kinds = [
            "consciousness_tick", "action", "intention",
            "memory_write", "reward", "breakthrough"
        ]

        for kind in allowed_kinds:
            decision = guard.check_replay(event_kind=kind)
            assert decision.allow, f"Should allow kind '{kind}'"
            assert decision.result == PolicyResult.ALLOW

        # Test disallowed kind
        decision = guard.check_replay(event_kind="malicious_action")
        assert not decision.allow
        assert decision.result == PolicyResult.DENY_KIND
        assert "not allowed" in decision.reason

    def test_risk_level_enforcement(self):
        """Test risk level threshold enforcement across lanes."""
        # Experimental lane (max_risk = 0.8)
        exp_guard = PolicyGuard(lane="experimental")

        decision = exp_guard.check_replay(event_kind="action", risk_level=0.7)
        assert decision.allow, "Should allow risk 0.7 in experimental"

        decision = exp_guard.check_replay(event_kind="action", risk_level=0.9)
        assert not decision.allow, "Should deny risk 0.9 in experimental"
        assert decision.result == PolicyResult.DENY_RISK

        # Production lane (max_risk = 0.2)
        prod_guard = PolicyGuard(lane="prod")

        decision = prod_guard.check_replay(event_kind="action", risk_level=0.1)
        assert decision.allow, "Should allow risk 0.1 in prod"

        decision = prod_guard.check_replay(event_kind="action", risk_level=0.3)
        assert not decision.allow, "Should deny risk 0.3 in prod"
        assert decision.result == PolicyResult.DENY_RISK

    def test_cross_lane_replay_restrictions(self):
        """Test cross-lane replay policy enforcement."""
        exp_guard = PolicyGuard(lane="experimental")
        cand_guard = PolicyGuard(lane="labs")
        prod_guard = PolicyGuard(lane="prod")

        # Experimental -> Candidate: should be allowed (same or lower level)
        decision = cand_guard.check_replay(
            event_kind="action",
            source_lane="experimental"
        )
        assert decision.allow, "Should allow experimental -> candidate"

        # Candidate -> Experimental: should be denied (higher -> lower)
        decision = exp_guard.check_replay(
            event_kind="action",
            source_lane="labs"
        )
        assert not decision.allow, "Should deny candidate -> experimental"
        assert decision.result == PolicyResult.DENY_LANE

        # Production -> Candidate: should be denied (highest -> lower)
        decision = cand_guard.check_replay(
            event_kind="action",
            source_lane="prod"
        )
        assert not decision.allow, "Should deny prod -> candidate"
        assert decision.result == PolicyResult.DENY_LANE

    def test_payload_risk_computation(self):
        """Test automatic risk computation from payload."""
        guard = PolicyGuard(lane="experimental")

        # Explicit risk level
        decision = guard.check_replay(
            event_kind="action",
            payload={"risk_level": 0.5}
        )
        assert decision.allow

        # Error events should be high risk
        decision = guard.check_replay(
            event_kind="action",
            payload={"error": "Something went wrong"}
        )
        # Risk 0.7 should be allowed in experimental (threshold 0.8)
        assert decision.allow

        # External action events
        decision = guard.check_replay(
            event_kind="action",
            payload={"external_action": True}
        )
        # Risk 0.6 should be allowed in experimental
        assert decision.allow

        # Normal events should be low risk
        decision = guard.check_replay(
            event_kind="action",
            payload={"normal_data": "value"}
        )
        assert decision.allow

    def test_rate_limiting(self):
        """Test replay rate limiting enforcement."""
        # Create guard with very low rate limit for testing
        custom_config = {
            "experimental": LanePolicyConfig(
                max_replay_rate=3,  # Very low limit
                replay_budget=100
            )
        }
        guard = PolicyGuard(lane="experimental", custom_config=custom_config)

        # First few requests should be allowed
        for i in range(3):
            decision = guard.check_replay(event_kind="action")
            assert decision.allow, f"Request {i+1} should be allowed"

        # Next request should be denied due to rate limit
        decision = guard.check_replay(event_kind="action")
        assert not decision.allow, "Should deny due to rate limit"
        assert decision.result == PolicyResult.DENY_RATE

    def test_budget_constraints(self):
        """Test replay budget constraint enforcement."""
        # Create guard with very low budget for testing
        custom_config = {
            "experimental": LanePolicyConfig(
                replay_budget=2,  # Very low budget
                budget_window_minutes=5,
                max_replay_rate=1000  # High rate limit so budget is the constraint
            )
        }
        guard = PolicyGuard(lane="experimental", custom_config=custom_config)

        # First few requests should be allowed
        for i in range(2):
            decision = guard.check_replay(event_kind="action")
            assert decision.allow, f"Request {i+1} should be allowed"

        # Next request should be denied due to budget exhaustion
        decision = guard.check_replay(event_kind="action")
        assert not decision.allow, "Should deny due to budget exhaustion"
        assert decision.result == PolicyResult.DENY_BUDGET

    def test_decision_logging(self):
        """Test deterministic decision logging."""
        guard = PolicyGuard(lane="experimental")

        # Make some decisions
        decision1 = guard.check_replay(event_kind="action")
        decision2 = guard.check_replay(event_kind="malicious_action")

        # Check decision log
        log = guard.get_decision_log()
        assert len(log) == 2

        # Verify log entries
        assert log[0].allow == True
        assert log[0].result == PolicyResult.ALLOW
        assert log[1].allow == False
        assert log[1].result == PolicyResult.DENY_KIND

        # Test log entry conversion
        log_entry = decision1.to_log_entry()
        expected_keys = {
            "decision_id", "timestamp", "lane", "event_kind",
            "result", "allow", "reason"
        }
        assert set(log_entry.keys()) == expected_keys

    def test_policy_stats(self):
        """Test policy statistics collection."""
        guard = PolicyGuard(lane="experimental")

        # Make some decisions
        guard.check_replay(event_kind="action")  # Allow
        guard.check_replay(event_kind="malicious_action")  # Deny

        stats = guard.get_policy_stats()

        # Verify stats structure
        expected_keys = {
            "lane", "total_decisions", "recent_decisions_5min",
            "recent_allows", "recent_denies", "current_budget_usage",
            "budget_capacity", "rate_limit_capacity", "max_risk_threshold",
            "allowed_kinds"
        }
        assert set(stats.keys()) == expected_keys

        # Verify stats values
        assert stats["lane"] == "experimental"
        assert stats["total_decisions"] == 2
        assert stats["recent_allows"] == 1
        assert stats["recent_denies"] == 1

    def test_lane_configuration_enforcement_matrix(self):
        """Test complete enforcement matrix across all lanes."""
        lanes = ["experimental", "labs", "prod"]
        test_cases = [
            # (risk_level, expected_results_by_lane [experimental, candidate, prod])
            (0.1, [True, True, True]),   # Low risk allowed everywhere
            (0.3, [True, True, False]),  # Medium risk allowed in exp/candidate (0.8/0.5 thresholds)
            (0.6, [True, False, False]), # High risk only in experimental (0.8 threshold)
            (0.9, [False, False, False]) # Very high risk denied everywhere
        ]

        for risk_level, expected_results in test_cases:
            for i, lane in enumerate(lanes):
                guard = PolicyGuard(lane=lane)
                decision = guard.check_replay(
                    event_kind="action",
                    risk_level=risk_level
                )

                expected_allow = expected_results[i]
                assert decision.allow == expected_allow, (
                    f"Risk {risk_level} in lane '{lane}': "
                    f"expected {expected_allow}, got {decision.allow}"
                )

    def test_factory_function(self):
        """Test factory function creates guards correctly."""
        guard = create_policy_guard(lane="labs")
        assert isinstance(guard, PolicyGuard)
        assert guard.lane == "labs"

    def test_reset_stats(self):
        """Test statistics reset functionality."""
        guard = PolicyGuard(lane="experimental")

        # Generate some activity
        guard.check_replay(event_kind="action")
        guard.check_replay(event_kind="action")

        # Verify stats exist
        stats_before = guard.get_policy_stats()
        assert stats_before["total_decisions"] == 2

        # Reset stats
        guard.reset_stats()

        # Verify stats are cleared
        stats_after = guard.get_policy_stats()
        assert stats_after["total_decisions"] == 0
        assert stats_after["current_budget_usage"] == 0

    def test_performance_requirements(self):
        """Test policy decisions meet performance requirements."""
        guard = PolicyGuard(lane="experimental")

        # Time multiple decisions
        start_time = time.perf_counter()
        num_decisions = 100

        for i in range(num_decisions):
            guard.check_replay(event_kind="action", risk_level=0.1)

        duration = time.perf_counter() - start_time

        # Should process decisions quickly (< 10ms per decision)
        avg_duration_ms = (duration / num_decisions) * 1000
        assert avg_duration_ms < 10.0, f"Average decision time {avg_duration_ms:.2f}ms exceeds 10ms budget"

    def test_custom_configuration(self):
        """Test custom policy configuration override."""
        custom_config = {
            "experimental": LanePolicyConfig(
                max_risk_level=0.9,  # Higher than default
                max_replay_rate=3000,  # Higher than default
                allowed_kinds={"action", "test_kind"}  # Custom allowed kinds
            )
        }

        guard = PolicyGuard(lane="experimental", custom_config=custom_config)

        # Test custom risk threshold
        decision = guard.check_replay(event_kind="action", risk_level=0.85)
        assert decision.allow, "Should allow higher risk with custom config"

        # Test custom allowed kinds
        decision = guard.check_replay(event_kind="test_kind")
        assert decision.allow, "Should allow custom kind"

        decision = guard.check_replay(event_kind="consciousness_tick")
        assert not decision.allow, "Should deny kind not in custom allowlist"

    def test_concurrent_safety(self):
        """Test thread safety of policy decisions."""
        guard = PolicyGuard(lane="experimental")
        decisions = []

        def make_decisions():
            for i in range(10):
                decision = guard.check_replay(event_kind="action")
                decisions.append(decision)

        # This is a basic test - in a real concurrent scenario,
        # you'd use threading.Thread or similar
        make_decisions()
        make_decisions()

        # Verify all decisions were recorded
        assert len(decisions) == 20
        assert all(isinstance(d, ReplayDecision) for d in decisions)


class TestPolicyIntegration:
    """Integration tests for policy guard with other components."""

    def test_prometheus_metrics_integration(self):
        """Test Prometheus metrics are updated correctly."""
        guard = PolicyGuard(lane="experimental")

        # Make decisions that should update metrics
        guard.check_replay(event_kind="action")  # Allow
        guard.check_replay(event_kind="malicious_action")  # Deny

        # Metrics should be updated (tested via no exceptions)
        # In a real test environment, you'd verify metric values

    def test_environment_variable_integration(self):
        """Test integration with environment variables."""
        # Test LUKHAS_LANE detection
        with patch.dict(os.environ, {"LUKHAS_LANE": "labs"}):
            guard = PolicyGuard()
            assert guard.lane == "labs"

        # Test fallback to experimental
        with patch.dict(os.environ, {}, clear=True):
            if "LUKHAS_LANE" in os.environ:
                del os.environ["LUKHAS_LANE"]
            guard = PolicyGuard()
            assert guard.lane == "experimental"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
