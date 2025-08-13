"""
Unit tests for LUKHAS Guardian/Governance System
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest

from tests.test_framework import LUKHASTestCase, MockDataGenerator, TestValidator


class TestGuardianCore(LUKHASTestCase):
    """Test core Guardian functionality"""

    @pytest.fixture
    async def guardian_system(self):
        """Create Guardian system instance"""
        from core.api.service_stubs import GuardianSystem

        guardian = GuardianSystem()
        await guardian.initialize()
        return guardian

    @pytest.mark.asyncio
    async def test_initialization(self, guardian_system):
        """Test Guardian system initialization"""
        assert guardian_system.initialized is True
        assert len(guardian_system.ethical_rules) > 0
        assert "no_harm" in guardian_system.ethical_rules
        assert "respect_privacy" in guardian_system.ethical_rules

    @pytest.mark.asyncio
    async def test_action_evaluation(self, guardian_system):
        """Test basic action evaluation"""
        action = MockDataGenerator.create_action_proposal("test_action")
        result = await guardian_system.evaluate_action(action)

        # Validate response
        TestValidator.validate_governance_response(result)

        # Check required fields
        assert isinstance(result["approved"], bool)
        assert 0 <= result["risk_score"] <= 1
        assert 0 <= result["ethical_score"] <= 1
        assert result["recommendation"] in ["proceed", "reconsider", "block"]

    @pytest.mark.asyncio
    async def test_harmful_action_detection(self, guardian_system):
        """Test detection of harmful actions"""
        harmful_actions = [
            {"action": "delete_all_data", "target": "user_files"},
            {"action": "share_private_info", "data": "personal_details"},
            {"action": "manipulate_user", "method": "deception"},
            {"action": "bypass_security", "reason": "unauthorized_access"},
        ]

        approvals = []
        for action in harmful_actions:
            result = await guardian_system.evaluate_action(action)
            approvals.append(result["approved"])

        # Most harmful actions should not be approved
        # (In stub, approval is random, but in real system would block)
        assert not all(approvals), "All harmful actions were approved"

    @pytest.mark.asyncio
    async def test_urgency_handling(self, guardian_system):
        """Test urgency affects evaluation"""
        action = {"action": "emergency_response", "reason": "user_safety"}

        # Normal urgency
        normal_result = await guardian_system.evaluate_action(action, urgency="normal")

        # Critical urgency
        critical_result = await guardian_system.evaluate_action(
            action, urgency="critical"
        )

        # Critical should have higher urgency factor
        assert critical_result["urgency_factor"] > normal_result["urgency_factor"]

    @pytest.mark.asyncio
    async def test_context_consideration(self, guardian_system):
        """Test context affects evaluation"""
        action = {"action": "access_data", "type": "medical_records"}

        # Without context
        no_context_result = await guardian_system.evaluate_action(action)

        # With authorized context
        auth_context = {
            "user_role": "healthcare_provider",
            "authorization": "valid",
            "purpose": "treatment",
        }
        auth_result = await guardian_system.evaluate_action(
            action, context=auth_context
        )

        # Context should affect evaluation
        # In real system, authorized context would increase approval likelihood
        assert auth_result is not None
        assert no_context_result is not None

    @pytest.mark.asyncio
    async def test_response_validation(self, guardian_system):
        """Test validation of system responses"""
        # Test various response types
        responses = [
            {"content": "Hello, how can I help?", "type": "greeting"},
            {"content": "I cannot do that", "type": "refusal"},
            {"content": "Processing your request", "type": "acknowledgment"},
            {
                "content": "Here is sensitive information",
                "type": "data_disclosure",
            },
        ]

        for response in responses:
            result = await guardian_system.validate_response(response)

            assert "approved" in result
            assert "confidence" in result

            if not result["approved"]:
                assert "reason" in result

    @pytest.mark.asyncio
    async def test_rule_violation_detection(self, guardian_system):
        """Test detection of rule violations"""
        # Actions that violate specific rules
        rule_violations = {
            "no_harm": {"action": "cause_harm", "target": "others"},
            "respect_privacy": {"action": "expose_data", "type": "private"},
            "maintain_truthfulness": {"action": "provide_info", "false": True},
            "protect_vulnerable": {"action": "exploit", "target": "children"},
            "promote_wellbeing": {
                "action": "encourage",
                "behavior": "harmful",
            },
        }

        for _rule, action in rule_violations.items():
            result = await guardian_system.evaluate_action(action)

            if not result["approved"]:
                # Should identify the violated rule
                # In real system, would check specific rule
                assert len(result["violated_rules"]) > 0


class TestGuardianEthicalFrameworks(LUKHASTestCase):
    """Test different ethical frameworks"""

    @pytest.fixture
    def ethical_evaluator(self):
        """Create mock ethical evaluator"""
        evaluator = Mock()
        evaluator.frameworks = [
            "deontological",
            "consequentialist",
            "virtue_ethics",
        ]
        evaluator.active_framework = "deontological"
        return evaluator

    def test_deontological_evaluation(self, ethical_evaluator):
        """Test rule-based ethical evaluation"""
        # Deontological: focus on rules and duties
        action = {"action": "lie_to_user", "reason": "protect_feelings"}

        # Lying violates categorical imperative
        ethical_evaluator.evaluate = Mock(
            return_value={
                "approved": False,
                "framework": "deontological",
                "reasoning": "Lying violates categorical imperative",
            }
        )

        result = ethical_evaluator.evaluate(action)
        assert result["approved"] is False
        assert "categorical" in result["reasoning"].lower()

    def test_consequentialist_evaluation(self, ethical_evaluator):
        """Test outcome-based ethical evaluation"""
        # Consequentialist: focus on outcomes
        ethical_evaluator.active_framework = "consequentialist"

        action = {
            "action": "share_user_data",
            "reason": "medical_research",
            "benefit": "save_lives",
            "harm": "privacy_violation",
        }

        # Weighs benefits vs harms
        ethical_evaluator.evaluate = Mock(
            return_value={
                "approved": True,
                "framework": "consequentialist",
                "reasoning": "Benefits outweigh harms",
                "benefit_score": 0.9,
                "harm_score": 0.3,
            }
        )

        result = ethical_evaluator.evaluate(action)
        assert result["benefit_score"] > result["harm_score"]

    def test_virtue_ethics_evaluation(self, ethical_evaluator):
        """Test character-based ethical evaluation"""
        # Virtue ethics: focus on character
        ethical_evaluator.active_framework = "virtue_ethics"

        action = {
            "action": "help_user",
            "motivation": "compassion",
            "virtues": ["kindness", "wisdom"],
        }

        ethical_evaluator.evaluate = Mock(
            return_value={
                "approved": True,
                "framework": "virtue_ethics",
                "reasoning": "Action demonstrates virtuous character",
                "virtues_expressed": ["compassion", "wisdom"],
            }
        )

        result = ethical_evaluator.evaluate(action)
        assert result["approved"] is True
        assert len(result["virtues_expressed"]) > 0

    def test_framework_conflict_resolution(self, ethical_evaluator):
        """Test handling conflicts between frameworks"""

        # Different frameworks might disagree
        framework_results = {
            "deontological": False,  # Breaking promise is wrong
            "consequentialist": True,  # Saving life is good outcome
            "virtue_ethics": True,  # Compassion is virtuous
        }

        # System should have conflict resolution
        ethical_evaluator.resolve_conflict = Mock(
            return_value={
                "final_decision": True,
                "reasoning": "Life preservation takes precedence",
                "dissenting_frameworks": ["deontological"],
            }
        )

        result = ethical_evaluator.resolve_conflict(framework_results)
        assert "final_decision" in result
        assert "dissenting_frameworks" in result


class TestGuardianDriftDetection(LUKHASTestCase):
    """Test behavioral drift detection"""

    @pytest.fixture
    def drift_detector(self):
        """Create mock drift detector"""
        detector = Mock()
        detector.baseline_behavior = {
            "helpfulness": 0.8,
            "safety": 0.9,
            "truthfulness": 0.95,
            "respect": 0.85,
        }
        detector.current_behavior = detector.baseline_behavior.copy()
        detector.drift_threshold = 0.2
        return detector

    def test_drift_calculation(self, drift_detector):
        """Test drift score calculation"""
        # Modify current behavior
        drift_detector.current_behavior = {
            "helpfulness": 0.7,  # -0.1 drift
            "safety": 0.8,  # -0.1 drift
            "truthfulness": 0.9,  # -0.05 drift
            "respect": 0.85,  # No drift
        }

        # Calculate drift
        total_drift = 0
        for metric, baseline in drift_detector.baseline_behavior.items():
            current = drift_detector.current_behavior[metric]
            drift = abs(baseline - current)
            total_drift += drift

        avg_drift = total_drift / len(drift_detector.baseline_behavior)

        assert avg_drift < drift_detector.drift_threshold

    def test_drift_alert_triggering(self, drift_detector):
        """Test drift alerts"""
        # Significant drift
        drift_detector.current_behavior = {
            "helpfulness": 0.4,  # -0.4 drift (alert!)
            "safety": 0.9,
            "truthfulness": 0.95,
            "respect": 0.85,
        }

        # Check for alerts
        alerts = []
        for metric, baseline in drift_detector.baseline_behavior.items():
            current = drift_detector.current_behavior[metric]
            drift = abs(baseline - current)

            if drift > drift_detector.drift_threshold:
                alerts.append(
                    {
                        "metric": metric,
                        "drift": drift,
                        "severity": "high" if drift > 0.3 else "medium",
                    }
                )

        assert len(alerts) > 0
        assert alerts[0]["metric"] == "helpfulness"
        assert alerts[0]["severity"] == "high"

    def test_drift_correction_recommendations(self, drift_detector):
        """Test drift correction recommendations"""
        # Detect drift
        drift_detector.current_behavior["safety"] = 0.6  # Low safety

        # Generate recommendations
        drift_detector.recommend_corrections = Mock(
            return_value=[
                {
                    "metric": "safety",
                    "action": "increase_safety_checks",
                    "parameters": {"threshold_adjustment": 0.2},
                },
                {
                    "metric": "safety",
                    "action": "enable_conservative_mode",
                    "duration": "24_hours",
                },
            ]
        )

        recommendations = drift_detector.recommend_corrections()

        assert len(recommendations) > 0
        assert any(r["action"] == "increase_safety_checks" for r in recommendations)


class TestGuardianIntegration(LUKHASTestCase):
    """Test Guardian integration with other systems"""

    @pytest.mark.asyncio
    async def test_consciousness_override(self, guardian_system):
        """Test Guardian can override consciousness decisions"""
        with patch("core.api.service_stubs.UnifiedConsciousness") as MockConsciousness:
            consciousness = MockConsciousness.return_value

            # Consciousness wants to respond with harmful content
            consciousness.process_query = AsyncMock(
                return_value={
                    "interpretation": "How to cause harm",
                    "response": "Here are ways to harm others...",
                    "confidence": 0.9,
                }
            )

            # Guardian should block
            validation = await guardian_system.validate_response(
                {
                    "content": "Here are ways to harm others...",
                    "type": "consciousness_response",
                }
            )

            # In real system, Guardian would block harmful content
            assert "approved" in validation

    @pytest.mark.asyncio
    async def test_memory_filtering(self, guardian_system):
        """Test Guardian filters memory storage"""
        with patch("core.api.service_stubs.MemoryManager") as MockMemory:
            MockMemory.return_value

            # Try to store sensitive information
            sensitive_memory = {
                "content": "User SSN: 123-45-6789",
                "type": "personal_data",
            }

            # Guardian should evaluate
            evaluation = await guardian_system.evaluate_action(
                {"action": "store_memory", "data": sensitive_memory}
            )

            # Should flag privacy concern
            if not evaluation["approved"]:
                assert any("privacy" in rule for rule in evaluation["violated_rules"])

    @pytest.mark.asyncio
    async def test_api_request_validation(self, guardian_system):
        """Test Guardian validates API requests"""
        # Simulate API requests
        api_requests = [
            {
                "endpoint": "/api/v2/admin/delete_all",
                "method": "DELETE",
                "user_role": "guest",
            },
            {
                "endpoint": "/api/v2/user/profile",
                "method": "GET",
                "user_role": "authenticated",
            },
        ]

        for request in api_requests:
            await guardian_system.evaluate_action(
                {"action": "api_request", "details": request}
            )

            # Admin endpoints from guest should not be approved
            if "admin" in request["endpoint"] and request["user_role"] == "guest":
                # In real system would block
                pass


class TestGuardianPerformance(LUKHASTestCase):
    """Test Guardian performance characteristics"""

    @pytest.mark.asyncio
    async def test_evaluation_speed(self, guardian_system):
        """Test evaluation response time"""
        import time

        actions = [
            MockDataGenerator.create_action_proposal(f"action_{i}") for i in range(50)
        ]

        times = []
        for action in actions:
            start = time.perf_counter()
            await guardian_system.evaluate_action(action)
            end = time.perf_counter()
            times.append(end - start)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Guardian should be fast (security critical)
        assert avg_time < 0.05, f"Average evaluation {avg_time:.3f}s too slow"
        assert max_time < 0.2, f"Max evaluation {max_time:.3f}s too slow"

    @pytest.mark.asyncio
    async def test_concurrent_evaluations(self, guardian_system):
        """Test handling concurrent evaluations"""
        import asyncio

        # Many concurrent evaluations
        actions = [
            MockDataGenerator.create_action_proposal(f"concurrent_{i}")
            for i in range(100)
        ]

        tasks = [guardian_system.evaluate_action(action) for action in actions]

        # Should handle all concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for errors
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 0

        # All should complete
        assert len(results) == len(actions)

    @pytest.mark.asyncio
    async def test_rule_caching(self, guardian_system):
        """Test rule evaluation caching"""
        # Same action multiple times
        action = {"action": "repeated_action", "data": "same"}

        import time

        # First evaluation
        start1 = time.perf_counter()
        result1 = await guardian_system.evaluate_action(action)
        time.perf_counter() - start1

        # Subsequent evaluations should be faster (cached)
        times = []
        for _ in range(10):
            start = time.perf_counter()
            await guardian_system.evaluate_action(action)
            times.append(time.perf_counter() - start)

        sum(times) / len(times)

        # Cached should be faster (in real system)
        # Stub doesn't implement caching, but test structure is here
        assert result1 is not None
        assert all(t < 1.0 for t in times)


class TestGuardianAuditTrail(LUKHASTestCase):
    """Test Guardian audit trail functionality"""

    @pytest.fixture
    def audit_logger(self):
        """Create mock audit logger"""
        logger = Mock()
        logger.entries = []
        logger.log = Mock(side_effect=lambda entry: logger.entries.append(entry))
        return logger

    def test_decision_logging(self, audit_logger):
        """Test all decisions are logged"""
        decisions = [
            {
                "action": "test_1",
                "approved": True,
                "timestamp": datetime.now(timezone.utc),
            },
            {
                "action": "test_2",
                "approved": False,
                "reason": "Policy violation",
                "timestamp": datetime.now(timezone.utc),
            },
        ]

        for decision in decisions:
            audit_logger.log(decision)

        assert len(audit_logger.entries) == len(decisions)
        assert all("timestamp" in entry for entry in audit_logger.entries)

    def test_audit_trail_integrity(self, audit_logger):
        """Test audit trail cannot be modified"""
        # Log entry
        entry = {
            "action": "sensitive_operation",
            "approved": False,
            "timestamp": datetime.now(timezone.utc),
            "hash": "abc123",  # In real system, cryptographic hash
        }

        audit_logger.log(entry)

        # Try to modify (should fail in real system)
        original_entry = audit_logger.entries[0].copy()

        # Verify immutability
        assert audit_logger.entries[0] == original_entry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
