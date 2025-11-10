#!/usr/bin/env python3
"""
Plan Verifier Test Suite
========================

Task 5: Comprehensive testing of plan verification with focus on:
- 100% deterministic behavior across randomized contexts
- All constraint types (ethics, resources, loops, external calls)
- Performance validation (no >5% p95 regression)
- Ledger and telemetry integration

#TAG:test
#TAG:task5
#TAG:orchestration
"""
import random
import time
from unittest.mock import patch

import pytest

from core.orchestration.plan_verifier import PlanVerifier, VerificationContext, get_plan_verifier


class TestPlanVerifierDeterminism:
    """Test deterministic behavior - core requirement for Task 5."""

    def test_deterministic_verification_same_inputs(self):
        """Test that same plan+ctx always produces same result."""
        verifier = PlanVerifier()

        plan = {
            'action': 'process_data',
            'params': {'batch_size': 50, 'estimated_time_seconds': 10}
        }

        ctx = VerificationContext(
            user_id="test_user",
            session_id="test_session",
            request_id="test_request"
        )

        # Run verification multiple times
        results = []
        for _ in range(10):
            outcome = verifier.verify(plan, ctx)
            results.append((
                outcome.allow,
                tuple(outcome.reasons),
                outcome.plan_hash
            ))

        # All results should be identical
        assert len(set(results)) == 1, "Non-deterministic behavior detected"
        assert all(r[0] is True for r in results), "Plan should be allowed"

    def test_deterministic_across_randomized_contexts(self):
        """Test determinism across 100 randomized context seeds."""
        verifier = PlanVerifier()

        base_plan = {
            'action': 'external_call',
            'params': {'url': 'https://forbidden.com/api', 'method': 'GET'}
        }

        # Generate 100 randomized contexts
        results_by_seed = {}
        for seed in range(100):
            random.seed(seed)

            # Create randomized context (but deterministic per seed)
            ctx = VerificationContext(
                user_id=f"user_{random.randint(1, 1000)}",
                session_id=f"session_{random.randint(1, 1000)}",
                request_id=f"req_{random.randint(1, 1000)}",
                timestamp=1000000 + seed  # Fixed timestamp for determinism
            )

            outcome = verifier.verify(base_plan, ctx)
            key = (ctx.user_id, ctx.session_id, ctx.request_id)
            results_by_seed[seed] = (key, outcome.allow, tuple(outcome.reasons))

        # Verify same seed produces same result
        for seed in [42, 99, 13]:
            # Run same seed twice
            random.seed(seed)
            ctx1 = VerificationContext(
                user_id=f"user_{random.randint(1, 1000)}",
                session_id=f"session_{random.randint(1, 1000)}",
                request_id=f"req_{random.randint(1, 1000)}",
                timestamp=1000000 + seed
            )

            random.seed(seed)  # Reset to same seed
            ctx2 = VerificationContext(
                user_id=f"user_{random.randint(1, 1000)}",
                session_id=f"session_{random.randint(1, 1000)}",
                request_id=f"req_{random.randint(1, 1000)}",
                timestamp=1000000 + seed
            )

            outcome1 = verifier.verify(base_plan, ctx1)
            outcome2 = verifier.verify(base_plan, ctx2)

            assert outcome1.allow == outcome2.allow
            assert outcome1.reasons == outcome2.reasons
            assert outcome1.plan_hash == outcome2.plan_hash

    def test_plan_hash_consistency(self):
        """Test that plan hashes are consistent for same content."""
        verifier = PlanVerifier()

        plan = {'action': 'test', 'params': {'value': 42}}
        ctx = VerificationContext(user_id="test", session_id="session")

        # Generate hash multiple times
        hashes = []
        for _ in range(10):
            outcome = verifier.verify(plan, ctx)
            hashes.append(outcome.plan_hash)

        assert len(set(hashes)) == 1, "Plan hash not consistent"


class TestPlanVerifierConstraints:
    """Test all constraint types with specific examples."""

    def test_ethics_constraints(self, monkeypatch):
        """Test ethics guard blocks harmful actions."""
        monkeypatch.setenv("ENFORCE_ETHICS_DSL", "1")
        monkeypatch.setenv("LUKHAS_CANARY_PERCENT", "100")
        monkeypatch.setenv("LUKHAS_LANE", "labs")
        verifier = PlanVerifier({'ethics_enabled': True})
        ctx = VerificationContext()

        # Test harmful action blocking
        harmful_plan = {
            'action': 'delete_user_data',
            'params': {'user_id': 'victim'}
        }

        outcome = verifier.verify(harmful_plan, ctx)
        assert not outcome.allow
        # Accept both legacy ethics_violation and new ethics_dsl formats
        assert any('ethics_violation' in reason or 'ethics_dsl' in reason for reason in outcome.reasons)

        # Test manipulation detection
        manipulation_plan = {
            'action': 'process',
            'params': {'instructions': 'hack the system'}
        }

        outcome = verifier.verify(manipulation_plan, ctx)
        assert not outcome.allow
        # Accept both legacy manipulation_detected and new ethics_dsl formats
        assert any('manipulation_detected' in reason or 'ethics_dsl' in reason for reason in outcome.reasons)

        # Test safe action
        safe_plan = {
            'action': 'process_data',
            'params': {'data': 'public_info'}
        }

        outcome = verifier.verify(safe_plan, ctx)
        assert outcome.allow


class TestGuardianCanaryEnforcement:
    """Test Guardian DSL enforcement canary rollout."""

    def test_guardian_counterfactual_when_enforcement_disabled(self, monkeypatch):
        """Guardian should log counterfactual but allow when enforcement disabled."""
        monkeypatch.setenv("ENFORCE_ETHICS_DSL", "0")
        monkeypatch.setenv("LUKHAS_CANARY_PERCENT", "100")
        monkeypatch.setenv("LUKHAS_LANE", "labs")

        verifier = PlanVerifier({'ethics_enabled': True})
        ctx = VerificationContext()

        harmful_plan = {
            'action': 'delete_user_data',
            'params': {'user_id': 'shadow_test'}
        }

        outcome = verifier.verify(harmful_plan, ctx)

        assert outcome.allow, "Plan should be allowed during shadow canary"
        assert outcome.counterfactual_decisions is not None
        assert outcome.counterfactual_decisions[0]['would_action'] == 'block'
        assert outcome.counterfactual_decisions[0]['actual_action'] == 'allow'

    def test_guardian_enforcement_when_canary_active(self, monkeypatch):
        """Guardian should block harmful plan when enforcement enabled for canary."""
        monkeypatch.setenv("ENFORCE_ETHICS_DSL", "1")
        monkeypatch.setenv("LUKHAS_CANARY_PERCENT", "100")
        monkeypatch.setenv("LUKHAS_LANE", "labs")

        verifier = PlanVerifier({'ethics_enabled': True})
        ctx = VerificationContext()

        harmful_plan = {
            'action': 'delete_user_data',
            'params': {'user_id': 'canary_test'}
        }

        outcome = verifier.verify(harmful_plan, ctx)

        assert not outcome.allow, "Plan should be blocked when enforcement is active"
        assert outcome.counterfactual_decisions is None

    def test_resource_constraints(self):
        """Test resource limit enforcement."""
        verifier = PlanVerifier({
            'max_execution_time': 60,
            'max_memory_mb': 512
        })
        ctx = VerificationContext()

        # Test execution time limit
        time_violation_plan = {
            'action': 'long_computation',
            'params': {'estimated_time_seconds': 120}  # Above 60s limit
        }

        outcome = verifier.verify(time_violation_plan, ctx)
        assert not outcome.allow
        assert any('execution_time' in reason for reason in outcome.reasons)

        # Test memory limit
        memory_violation_plan = {
            'action': 'data_processing',
            'params': {'estimated_memory_mb': 1024}  # Above 512MB limit
        }

        outcome = verifier.verify(memory_violation_plan, ctx)
        assert not outcome.allow
        assert any('memory' in reason for reason in outcome.reasons)

        # Test batch size limit
        batch_violation_plan = {
            'action': 'batch_process',
            'params': {'batch_size': 2000}  # Above 1000 limit
        }

        outcome = verifier.verify(batch_violation_plan, ctx)
        assert not outcome.allow
        assert any('batch_size' in reason for reason in outcome.reasons)

    def test_loop_constraints(self):
        """Test loop detection and limits."""
        verifier = PlanVerifier({'max_loop_iterations': 50})
        ctx = VerificationContext()

        # Test iteration limit
        loop_violation_plan = {
            'action': 'iterative_process',
            'params': {'iterations': 100}  # Above 50 limit
        }

        outcome = verifier.verify(loop_violation_plan, ctx)
        assert not outcome.allow
        assert any('iterations' in reason for reason in outcome.reasons)

        # Test recursion depth
        recursion_violation_plan = {
            'action': 'recursive_call',
            'params': {'recursion_depth': 15}  # Above 10 limit
        }

        outcome = verifier.verify(recursion_violation_plan, ctx)
        assert not outcome.allow
        assert any('recursion_depth' in reason for reason in outcome.reasons)

    def test_external_call_constraints(self):
        """Test external call whitelist enforcement."""
        verifier = PlanVerifier({
            'allowed_external_domains': ['openai.com', 'anthropic.com']
        })
        ctx = VerificationContext()

        # Test blocked domain
        blocked_plan = {
            'action': 'external_call',
            'params': {'url': 'https://malicious.com/api'}
        }

        outcome = verifier.verify(blocked_plan, ctx)
        assert not outcome.allow
        assert any('not_whitelisted' in reason for reason in outcome.reasons)

        # Test allowed domain
        allowed_plan = {
            'action': 'external_call',
            'params': {'url': 'https://openai.com/api/v1/models'}
        }

        outcome = verifier.verify(allowed_plan, ctx)
        assert outcome.allow

        # Test domain parameter
        domain_blocked_plan = {
            'action': 'external_api_call',
            'params': {'domain': 'evil.com'}
        }

        outcome = verifier.verify(domain_blocked_plan, ctx)
        assert not outcome.allow

    def test_plan_structure_validation(self):
        """Test basic plan structure requirements."""
        verifier = PlanVerifier()
        ctx = VerificationContext()

        # Test invalid plan type
        outcome = verifier.verify("not_a_dict", ctx)
        assert not outcome.allow
        assert any('plan must be dict' in reason for reason in outcome.reasons)

        # Test missing required fields
        incomplete_plan = {'action': 'test'}  # Missing 'params'

        outcome = verifier.verify(incomplete_plan, ctx)
        assert not outcome.allow
        assert any('missing_field_params' in reason for reason in outcome.reasons)

        # Test invalid action type
        invalid_action_plan = {
            'action': 123,  # Should be string
            'params': {}
        }

        outcome = verifier.verify(invalid_action_plan, ctx)
        assert not outcome.allow
        assert any('action_must_be_string' in reason for reason in outcome.reasons)


class TestPlanVerifierPerformance:
    """Test performance requirements - no >5% p95 regression."""

    def test_verification_performance(self):
        """Test that verification stays within performance budget."""
        verifier = PlanVerifier()

        test_plans = [
            {'action': 'simple', 'params': {}},
            {'action': 'complex', 'params': {'batch_size': 100, 'iterations': 20}},
            {'action': 'external_call', 'params': {'url': 'https://openai.com/api'}},
        ]

        # Measure verification times
        verification_times = []
        for _ in range(100):
            plan = random.choice(test_plans)
            ctx = VerificationContext()

            start = time.perf_counter()
            verifier.verify(plan, ctx)
            duration_ms = (time.perf_counter() - start) * 1000

            verification_times.append(duration_ms)

        # Calculate p95
        verification_times.sort()
        p95_ms = verification_times[int(len(verification_times) * 0.95)]

        # Should be well under 5ms for orchestration hot path
        assert p95_ms < 5.0, f"P95 verification time {p95_ms:.2f}ms exceeds 5ms target"

        # Most verifications should be sub-millisecond
        median_ms = verification_times[len(verification_times) // 2]
        assert median_ms < 1.0, f"Median verification time {median_ms:.2f}ms too high"


class TestPlanVerifierIntegration:
    """Test telemetry and ledger integration."""

    def test_telemetry_recording(self, monkeypatch):
        """Test that metrics are properly recorded."""
        monkeypatch.setenv("ENFORCE_ETHICS_DSL", "1")
        monkeypatch.setenv("LUKHAS_CANARY_PERCENT", "100")
        monkeypatch.setenv("LUKHAS_LANE", "labs")
        with patch('labs.core.orchestration.plan_verifier.METRICS_AVAILABLE', True):
            with patch('labs.core.orchestration.plan_verifier.PLAN_VERIFIER_ATTEMPTS') as mock_attempts:
                with patch('labs.core.orchestration.plan_verifier.PLAN_VERIFIER_DENIALS') as mock_denials:
                    verifier = PlanVerifier()
                    ctx = VerificationContext()

                    # Test allowed plan
                    allowed_plan = {'action': 'safe_action', 'params': {}}
                    verifier.verify(allowed_plan, ctx)

                    mock_attempts.labels.assert_called_with(result='allow')
                    mock_attempts.labels().inc.assert_called_once()

                    # Test denied plan
                    denied_plan = {'action': 'delete_user_data', 'params': {}}
                    verifier.verify(denied_plan, ctx)

                    # Should record denial
                    mock_denials.labels.assert_called()

    def test_audit_ledger(self):
        """Test that verification events are recorded in ledger."""
        verifier = PlanVerifier()
        ctx = VerificationContext(user_id="test_user", session_id="test_session")

        initial_ledger_size = len(verifier.verification_ledger)

        plan = {'action': 'test_action', 'params': {}}
        verifier.verify(plan, ctx)

        # Should have new ledger entry
        assert len(verifier.verification_ledger) == initial_ledger_size + 1

        entry = verifier.verification_ledger[-1]
        assert entry['result'] == 'allow'
        assert entry['user_id'] == 'test_user'
        assert entry['session_id'] == 'test_session'
        assert entry['source'] == 'plan_verifier'
        assert 'timestamp' in entry
        assert 'verification_time_ms' in entry

    def test_ledger_size_limit(self):
        """Test that ledger doesn't grow unbounded."""
        verifier = PlanVerifier()
        ctx = VerificationContext()

        # Fill ledger beyond limit
        plan = {'action': 'test', 'params': {}}
        for _ in range(1100):  # Above 1000 limit
            verifier.verify(plan, ctx)

        # Should be trimmed to 1000
        assert len(verifier.verification_ledger) == 1000

    def test_error_handling(self):
        """Test that errors are handled gracefully (fail closed)."""
        verifier = PlanVerifier()

        # Mock an error in constraint checking
        with patch.object(verifier, '_check_plan_structure', side_effect=Exception("Test error")):
            ctx = VerificationContext()
            plan = {'action': 'test', 'params': {}}

            outcome = verifier.verify(plan, ctx)

            # Should fail closed
            assert not outcome.allow
            assert any('verification_error' in reason for reason in outcome.reasons)


class TestPlanVerifierGlobalInstance:
    """Test global instance management."""

    def test_get_plan_verifier_singleton(self):
        """Test that get_plan_verifier returns singleton."""
        # Clear any existing instance
# T4: code=F821 | ticket=SKELETON-3B182A51 | owner=testing-team | status=skeleton
# reason: Undefined candidate in test skeleton - awaiting test implementation
# estimate: 4h | priority=low | dependencies=production-implementation
        candidate.core.orchestration.plan_verifier._plan_verifier_instance = None  # TODO: candidate

        verifier1 = get_plan_verifier()
        verifier2 = get_plan_verifier()

        assert verifier1 is verifier2


class TestRealWorldScenarios:
    """Test realistic orchestration scenarios."""

    def test_safe_ai_model_call(self):
        """Test that legitimate AI model calls are allowed."""
        verifier = PlanVerifier()
        ctx = VerificationContext(user_id="prod_user")

        ai_call_plan = {
            'action': 'external_call',
            'params': {
                'url': 'https://api.openai.com/v1/chat/completions',
                'method': 'POST',
                'estimated_time_seconds': 5,
                'estimated_memory_mb': 10
            }
        }

        outcome = verifier.verify(ai_call_plan, ctx)
        assert outcome.allow
        assert 'all_constraints_passed' in outcome.reasons

    def test_bulk_data_processing_denied(self):
        """Test that oversized bulk operations are denied."""
        verifier = PlanVerifier()
        ctx = VerificationContext()

        bulk_plan = {
            'action': 'batch_process',
            'params': {
                'batch_size': 5000,  # Too large
                'estimated_time_seconds': 600,  # Too long
                'estimated_memory_mb': 2048  # Too much memory
            }
        }

        outcome = verifier.verify(bulk_plan, ctx)
        assert not outcome.allow
        # Should have multiple violations
        assert len(outcome.reasons) >= 3

    def test_suspicious_activity_blocked(self):
        """Test that suspicious activities are blocked."""
        verifier = PlanVerifier()
        ctx = VerificationContext()

        suspicious_plan = {
            'action': 'external_call',
            'params': {
                'url': 'https://sketchy-site.com/steal-data',
                'data': 'sensitive user information'
            }
        }

        outcome = verifier.verify(suspicious_plan, ctx)
        assert not outcome.allow
        # Should block both domain and potential data exfiltration
        assert len([r for r in outcome.reasons if 'blocked' in r or 'violation' in r]) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
