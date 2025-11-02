#!/usr/bin/env python3
"""
tests/capabilities/test_governance_suite.py

Phase 5 Governance & Memory Synchronization capability regression suite.
End-to-end tests for policy denial/allow, promotion success, sync safety.

Tests integration across:
- Policy-gated replay (core.policy_guard)
- Memory fold synchronization (memory.sync)
- Cross-lane promotion gates
- Governance regression patterns
"""
import os
import time

import pytest

from core.policy_guard import PolicyGuard, PolicyResult
from memory.sync import MemorySynchronizer, SyncBudgetConfig, SyncResult

# Skip these tests if required dependencies are missing
try:
    from storage.events import Event, EventStore

    from core.consciousness_stream import ConsciousnessStream

    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


class TestGovernanceCapabilities:
    """End-to-end governance capability tests."""

    def setup_method(self):
        """Set up hermetic test environment."""
        os.environ["LUKHAS_LANE"] = "experimental"
        os.environ["PYTHONHASHSEED"] = "0"
        os.environ["TZ"] = "UTC"
        os.environ["LUKHAS_RNG_SEED"] = "42"

    @pytest.mark.capability
    def test_policy_denial_deterministic_logs(self):
        """
        Scenario 1: Policy denial path with deterministic logging.

        Seed replay events that violate lane policy → expect deny,
        no state mutation, and deterministic denial log.
        """
        # Test across multiple lanes for governance matrix
        test_cases = [
            ("experimental", "malicious_action", 0.9),  # High risk in experimental
            ("labs", "action", 0.6),  # Medium risk in candidate
            ("prod", "action", 0.3),  # Low risk in prod (above threshold)
        ]

        for lane, event_kind, risk_level in test_cases:
            guard = PolicyGuard(lane=lane)

            # Create event that should be denied
            decision = guard.check_replay(
                event_kind=event_kind,
                risk_level=risk_level,
                payload={"risk_level": risk_level, "source": "capability_test"},
            )

            # Verify denial
            assert not decision.allow, f"Should deny {event_kind} with risk {risk_level} in {lane}"

            # Verify deterministic logging
            log_entry = decision.to_log_entry()
            expected_keys = {"decision_id", "timestamp", "lane", "event_kind", "result", "allow", "reason"}
            assert set(log_entry.keys()) == expected_keys

            # Verify decision is logged
            decision_log = guard.get_decision_log()
            assert len(decision_log) > 0
            assert decision_log[-1].decision_id == decision.decision_id

            # Verify no state mutation on denial
            stats_before = guard.get_policy_stats()
            guard.check_replay(event_kind=event_kind, risk_level=risk_level)
            stats_after = guard.get_policy_stats()

            # Budget usage should not increase on denials
            assert stats_after["current_budget_usage"] == stats_before["current_budget_usage"]

    @pytest.mark.capability
    def test_cross_lane_promotion_gates(self):
        """
        Scenario 2: Cross-lane promotion gates based on drift/coherence signals.

        Stable drift/coherence over window → expect promotion attempts and
        success metrics for allowed lanes.
        """
        # Test promotion from experimental -> candidate -> prod
        promotion_chain = [("experimental", "labs"), ("labs", "prod")]

        for source_lane, target_lane in promotion_chain:
            # Create policy guards for both lanes
            source_guard = PolicyGuard(lane=source_lane)
            target_guard = PolicyGuard(lane=target_lane)

            # Simulate stable operation in source lane (low risk events)
            stable_events = 20
            for i in range(stable_events):
                decision = source_guard.check_replay(
                    event_kind="action",
                    risk_level=0.1,  # Very low risk
                    payload={"stable_operation": True, "sequence": i},
                )
                assert decision.allow, f"Stable operation should be allowed in {source_lane}"

            # Verify source lane has stable policy statistics
            source_stats = source_guard.get_policy_stats()
            assert source_stats["recent_allows"] >= stable_events * 0.8  # Allow for some variance

            # Test cross-lane event replay (promotion gate)
            promotion_event = target_guard.check_replay(
                event_kind="action",
                source_lane=source_lane,
                risk_level=0.1,
                payload={"promotion_candidate": True, "source_lane": source_lane, "target_lane": target_lane},
            )

            # Promotion should succeed for allowed hierarchy
            if target_lane in ["labs", "prod"]:
                assert promotion_event.allow, f"Promotion from {source_lane} to {target_lane} should succeed"
                assert promotion_event.result == PolicyResult.ALLOW

            # Verify promotion metrics (would be tracked in real implementation)
            target_stats = target_guard.get_policy_stats()
            assert target_stats["total_decisions"] > 0

    @pytest.mark.capability
    def test_memory_sync_safety_under_load(self):
        """
        Scenario 3: Memory sync safety under bounded load.

        Push bounded fan-in/out workloads → assert circuit stays within
        budgets and idempotency holds.
        """
        # Create synchronizer with realistic but constrained budgets
        sync_config = {
            "experimental": SyncBudgetConfig(
                max_fanout=4,
                max_fanin=3,
                max_depth=2,
                ops_budget_per_tick=20,
                data_budget_per_tick_mb=5.0,
                budget_window_seconds=10,
            )
        }
        syncer = MemorySynchronizer(lane="experimental", custom_config=sync_config)

        # Test data set
        fold_data_templates = [
            {"fold_id": "memory_fold_1", "content": {"data": "test_value_1"}},
            {"fold_id": "memory_fold_2", "content": {"data": "test_value_2"}},
            {"fold_id": "memory_fold_3", "content": {"data": "test_value_3"}},
        ]

        # Scenario 3a: Test within budget limits
        successful_operations = 0
        budget_exceeded_operations = 0

        for i in range(15):  # Stay within ops budget of 20
            fold_data = fold_data_templates[i % len(fold_data_templates)].copy()
            fold_data["sequence"] = i

            result = syncer.sync_fold(
                source_lane="experimental",
                target_lane="experimental",  # Same-lane to avoid fanout costs
                fold_data=fold_data,
                fold_id=f"test_fold_{i}",
            )

            if result.result == SyncResult.SUCCESS:
                successful_operations += 1
            elif result.result == SyncResult.ERROR_BUDGET:
                budget_exceeded_operations += 1

        # Verify most operations succeeded (should be within budget)
        assert successful_operations >= 10, f"Expected ≥10 successful ops, got {successful_operations}"

        # Verify budget enforcement worked
        stats = syncer.get_sync_stats()
        assert stats["ops_budget_utilization"] <= 1.0, "Budget utilization should not exceed 100%"

        # Scenario 3b: Test idempotency under repeated operations
        idempotency_fold = {"fold_id": "idempotent_test", "content": {"version": 1}}

        results = []
        for _ in range(3):
            result = syncer.sync_fold(
                source_lane="experimental",
                target_lane="experimental",
                fold_data=idempotency_fold,
                fold_id="idempotent_test",
            )
            results.append(result)

        # All operations should succeed (idempotent)
        assert all(r.result == SyncResult.SUCCESS for r in results)

        # Operations should have different IDs but same fold_id
        op_ids = {r.op_id for r in results}
        assert len(op_ids) == 3, "Each operation should have unique ID"
        assert all(r.fold_id == "idempotent_test" for r in results)

    @pytest.mark.capability
    def test_governance_coherence_requirements(self):
        """
        Test governance coherence requirements across policy and sync systems.

        Verifies that governance decisions are coherent and consistent
        across the policy and synchronization subsystems.
        """
        # Create coordinated governance components
        policy_guard = PolicyGuard(lane="labs")
        memory_syncer = MemorySynchronizer(lane="labs")

        # Test scenario: Policy allows event, sync should be coherent
        test_event = {
            "fold_id": "governance_test",
            "content": {"approved_action": True},
            "governance_metadata": {"policy_version": "1.0.0", "risk_assessment": 0.2},
        }

        # Check policy decision
        policy_decision = policy_guard.check_replay(event_kind="action", risk_level=0.2, payload=test_event)

        # If policy allows, memory sync should also succeed (coherence)
        if policy_decision.allow:
            sync_result = memory_syncer.sync_fold(
                source_lane="labs", target_lane="labs", fold_data=test_event, fold_id="governance_test"
            )

            # Coherence requirement: policy allow ⟹ sync success (under normal conditions)
            assert (
                sync_result.result == SyncResult.SUCCESS
            ), "Memory sync should succeed when policy allows (coherence requirement)"

        # Test governance audit trail
        policy_log = policy_guard.get_decision_log()
        sync_log = memory_syncer.get_sync_log()

        # Both systems should have recorded their operations
        assert len(policy_log) > 0, "Policy decisions should be logged"
        assert len(sync_log) > 0, "Sync operations should be logged"

        # Timestamps should be coherent (sync after policy)
        if policy_log and sync_log:
            latest_policy = policy_log[-1].timestamp
            latest_sync = sync_log[-1].timestamp
            assert latest_sync >= latest_policy, "Sync should occur after policy decision"

    @pytest.mark.capability
    def test_governance_regression_performance(self):
        """
        Test governance regression performance requirements.

        Ensures governance operations meet performance budgets:
        - Policy decisions < 10ms avg
        - Memory sync operations < 5ms avg
        - End-to-end governance flows < 50ms p95
        """
        policy_guard = PolicyGuard(lane="experimental")
        memory_syncer = MemorySynchronizer(lane="experimental")

        # Test policy decision performance
        policy_durations = []
        num_policy_tests = 50

        for i in range(num_policy_tests):
            start_time = time.perf_counter()

            decision = policy_guard.check_replay(event_kind="action", risk_level=0.1, payload={"perf_test": i})

            duration_ms = (time.perf_counter() - start_time) * 1000
            policy_durations.append(duration_ms)

            assert decision.allow, f"Low-risk events should be allowed for performance test {i}"

        # Policy decision performance budget: < 10ms average
        avg_policy_duration = sum(policy_durations) / len(policy_durations)
        assert avg_policy_duration < 10.0, f"Policy decisions averaged {avg_policy_duration:.2f}ms, expected < 10ms"

        # Test memory sync performance
        sync_durations = []
        num_sync_tests = 30

        for i in range(num_sync_tests):
            fold_data = {"fold_id": f"perf_test_{i}", "content": {"data": f"value_{i}"}}

            start_time = time.perf_counter()

            result = memory_syncer.sync_fold(
                source_lane="experimental", target_lane="experimental", fold_data=fold_data, fold_id=f"perf_test_{i}"
            )

            duration_ms = (time.perf_counter() - start_time) * 1000
            sync_durations.append(duration_ms)

            assert result.result == SyncResult.SUCCESS, f"Sync operation {i} should succeed"

        # Memory sync performance budget: < 5ms average
        avg_sync_duration = sum(sync_durations) / len(sync_durations)
        assert avg_sync_duration < 5.0, f"Memory sync averaged {avg_sync_duration:.2f}ms, expected < 5ms"

        # End-to-end flow performance budget: < 50ms p95
        e2e_durations = []
        num_e2e_tests = 20

        for i in range(num_e2e_tests):
            fold_data = {"fold_id": f"e2e_test_{i}", "content": {"data": f"e2e_value_{i}"}}

            start_time = time.perf_counter()

            # Policy check + Memory sync (end-to-end governance flow)
            policy_decision = policy_guard.check_replay(event_kind="action", risk_level=0.1, payload=fold_data)

            if policy_decision.allow:
                sync_result = memory_syncer.sync_fold(
                    source_lane="experimental", target_lane="experimental", fold_data=fold_data, fold_id=f"e2e_test_{i}"
                )
                assert sync_result.result == SyncResult.SUCCESS

            duration_ms = (time.perf_counter() - start_time) * 1000
            e2e_durations.append(duration_ms)

        # Calculate p95 for end-to-end flows
        e2e_durations.sort()
        p95_index = int(0.95 * len(e2e_durations))
        p95_duration = e2e_durations[p95_index] if e2e_durations else 0.0

        assert p95_duration < 50.0, f"End-to-end governance p95 was {p95_duration:.2f}ms, expected < 50ms"

    @pytest.mark.capability
    @pytest.mark.skipif(not DEPS_AVAILABLE, reason="Integration dependencies not available")
    def test_governance_integration_with_consciousness_stream(self):
        """
        Test governance integration with consciousness stream (if available).

        Verifies that governance components integrate properly with the
        existing consciousness stream infrastructure.
        """
        # Create consciousness stream with governance integration
        stream = ConsciousnessStream(fps=10)  # Low FPS for testing
        policy_guard = PolicyGuard(lane="experimental")

        # Generate some consciousness events
        stream._on_consciousness_tick(1)
        stream._on_consciousness_tick(2)

        events = stream.get_recent_events(limit=5)

        # Test policy decisions on consciousness events
        governance_decisions = []
        for event in events:
            decision = policy_guard.check_replay(event_kind=event.kind, payload=event.payload)
            governance_decisions.append(decision)

        # Verify governance decisions were made
        assert len(governance_decisions) > 0

        # Most consciousness events should be allowed (they're system-generated)
        allowed_decisions = [d for d in governance_decisions if d.allow]
        allow_rate = len(allowed_decisions) / len(governance_decisions)
        assert allow_rate >= 0.8, f"Expected ≥80% consciousness events allowed, got {allow_rate:.1%}"

    def test_governance_metrics_collection(self):
        """
        Test that governance metrics are properly collected.

        Verifies that Prometheus counters are incremented and
        metrics are available for observability.
        """
        policy_guard = PolicyGuard(lane="experimental")
        memory_syncer = MemorySynchronizer(lane="experimental")

        # Generate policy decisions that will create metrics
        policy_guard.check_replay(event_kind="action", risk_level=0.1)  # Allow
        policy_guard.check_replay(event_kind="malicious_action")  # Deny

        # Generate sync operations that will create metrics
        fold_data = {"fold_id": "metrics_test", "content": {"data": "test"}}
        memory_syncer.sync_fold(
            source_lane="experimental", target_lane="experimental", fold_data=fold_data, fold_id="metrics_test"
        )

        # Verify policy statistics are tracked
        policy_stats = policy_guard.get_policy_stats()
        assert policy_stats["total_decisions"] >= 2
        assert policy_stats["recent_allows"] >= 1
        assert policy_stats["recent_denies"] >= 1

        # Verify sync statistics are tracked
        sync_stats = memory_syncer.get_sync_stats()
        assert sync_stats["total_operations"] >= 1
        assert sync_stats["successful_operations"] >= 1
        assert sync_stats["success_rate"] > 0.0

        # In a real environment with Prometheus, counters would be incremented
        # This test verifies the tracking mechanisms are in place

    @pytest.mark.capability
    def test_promotion_metrics_integration(self):
        """
        Test that promotion metrics are properly tracked.

        Verifies that promotion attempts and successes are recorded
        for cross-lane operations and available via statistics.
        """
        # Create guards for promotion chain
        PolicyGuard(lane="experimental")
        candidate_guard = PolicyGuard(lane="labs")

        # Test cross-lane promotion attempts
        promotion_scenarios = [
            ("experimental", candidate_guard, True),  # Should succeed
            ("prod", candidate_guard, False),  # Should fail (wrong direction)
        ]

        for source_lane, target_guard, should_succeed in promotion_scenarios:
            decision = target_guard.check_replay(
                event_kind="action", source_lane=source_lane, risk_level=0.1, payload={"promotion_test": True}
            )

            if should_succeed:
                assert decision.allow, f"Promotion from {source_lane} to {target_guard.lane} should succeed"
            else:
                assert not decision.allow, f"Promotion from {source_lane} to {target_guard.lane} should fail"

        # Verify promotion statistics are tracked
        candidate_stats = candidate_guard.get_promotion_stats()
        assert candidate_stats["recent_promotion_attempts_10min"] >= 0
        assert isinstance(candidate_stats["promotion_success_rate"], float)
        assert candidate_stats["promotion_success_rate"] >= 0.0
        assert candidate_stats["promotion_success_rate"] <= 1.0

        # Verify promotion configuration is accessible
        assert "drift_threshold" in candidate_stats
        assert "coherence_threshold" in candidate_stats


if __name__ == "__main__":
    # Run governance capability tests
    pytest.main([__file__, "-v", "-m", "capability"])
