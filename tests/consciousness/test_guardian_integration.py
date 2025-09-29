#!/usr/bin/env python3
"""
Tests for Guardian Integration with Consciousness Engines
Phase 3 Implementation - T4/0.01% Excellence Standards

Comprehensive test suite for Guardian-consciousness integration covering:
- Drift detection with 0.15 threshold
- Safety validation and fail-closed behavior
- Performance targets (<250ms p95 latency)
- GDPR compliance and audit trails
- Constitutional AI principle alignment

Constellation Framework: 🛡️ Guardian-🧠 Consciousness Testing
"""

import pytest
import time
from unittest.mock import Mock, patch

# Import consciousness components
from lukhas.consciousness.types import (
    ConsciousnessState
)

# Import Guardian integration components
from lukhas.consciousness.guardian_integration import (
    ConsciousnessGuardianIntegration,
    GuardianValidationConfig,
    ConsciousnessValidationContext,
    GuardianValidationResult,
    GuardianValidationType,
    ValidationResult,
    create_validation_context
)


class TestGuardianValidationConfig:
    """Test Guardian validation configuration"""

    def test_default_config_creation(self):
        """Test creation of default Guardian configuration"""
        config = GuardianValidationConfig()

        assert config.p95_target_ms == 200.0
        assert config.p99_target_ms == 250.0
        assert config.drift_threshold == 0.15  # AUDITOR_CHECKLIST.md requirement
        assert config.drift_alpha == 0.3
        assert config.fail_closed_on_error is True
        assert config.gdpr_audit_enabled is True
        assert config.guardian_active is True

    def test_config_validation_success(self):
        """Test successful configuration validation"""
        config = GuardianValidationConfig(
            p95_target_ms=150.0,
            drift_threshold=0.2,
            drift_alpha=0.4
        )

        errors = config.validate()
        assert len(errors) == 0

    def test_config_validation_failures(self):
        """Test configuration validation failures"""
        config = GuardianValidationConfig(
            p95_target_ms=-10.0,
            drift_threshold=1.5,
            drift_alpha=-0.1,
            timeout_ms=100.0  # Less than p99_target_ms
        )

        errors = config.validate()
        assert len(errors) == 4
        assert "p95_target_ms must be positive" in errors
        assert "drift_threshold must be between 0 and 1" in errors
        assert "drift_alpha must be between 0 and 1" in errors
        assert "timeout_ms should be >= p99_target_ms" in errors

    def test_t4_excellence_targets(self):
        """Test T4/0.01% excellence performance targets"""
        config = GuardianValidationConfig()

        # Phase 3 requirements from PHASE_MATRIX.md
        assert config.p99_target_ms <= 250.0
        assert config.drift_threshold == 0.15
        assert config.fail_closed_on_error is True


class TestConsciousnessValidationContext:
    """Test consciousness validation context"""

    def test_context_creation_with_defaults(self):
        """Test validation context creation with defaults"""
        context = ConsciousnessValidationContext()

        assert context.validation_type == GuardianValidationType.CONSCIOUSNESS_STATE_TRANSITION
        assert context.tenant == "default"
        assert context.lane == "consciousness"
        assert context.sensitive_operation is False
        assert len(context.risk_indicators) == 0
        assert context.operation_id is not None
        assert context.correlation_id is not None

    def test_context_creation_with_consciousness_state(self):
        """Test context creation with consciousness state"""
        state = ConsciousnessState(
            phase="REFLECT",
            level=0.8,
            emotional_tone="focused",
            awareness_level=0.9
        )

        context = ConsciousnessValidationContext(
            validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
            consciousness_state=state,
            user_id="user123",
            session_id="session456",
            sensitive_operation=True
        )

        assert context.consciousness_state == state
        assert context.user_id == "user123"
        assert context.session_id == "session456"
        assert context.sensitive_operation is True

    def test_create_validation_context_helper(self):
        """Test create_validation_context helper function"""
        state = ConsciousnessState(phase="CREATE", level=0.9)

        context = create_validation_context(
            validation_type=GuardianValidationType.CREATIVE_GENERATION,
            consciousness_state=state,
            user_id="user789",
            sensitive_operation=True,
            tenant="test_tenant"
        )

        assert context.validation_type == GuardianValidationType.CREATIVE_GENERATION
        assert context.consciousness_state == state
        assert context.user_id == "user789"
        assert context.tenant == "test_tenant"
        assert context.sensitive_operation is True


class TestGuardianValidationResult:
    """Test Guardian validation results"""

    def test_result_creation(self):
        """Test validation result creation"""
        result = GuardianValidationResult(
            operation_id="op123",
            validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
            result=ValidationResult.APPROVED
        )

        assert result.operation_id == "op123"
        assert result.result == ValidationResult.APPROVED
        assert result.is_approved() is True
        assert result.validation_duration_ms == 0.0
        assert len(result.audit_trail) == 0

    def test_result_denial(self):
        """Test validation result denial"""
        result = GuardianValidationResult(
            operation_id="op456",
            validation_type=GuardianValidationType.CONSCIOUSNESS_STATE_TRANSITION,
            result=ValidationResult.DENIED,
            reason="Drift threshold exceeded",
            confidence=0.95
        )

        assert result.is_approved() is False
        assert result.reason == "Drift threshold exceeded"
        assert result.confidence == 0.95

    def test_audit_trail_management(self):
        """Test audit trail management"""
        result = GuardianValidationResult(
            operation_id="op789",
            validation_type=GuardianValidationType.SAFETY_CHECK,
            result=ValidationResult.APPROVED
        )

        result.add_audit_entry("drift_detection", {
            "drift_score": 0.05,
            "threshold": 0.15,
            "passed": True
        })

        assert len(result.audit_trail) == 1
        entry = result.audit_trail[0]
        assert entry["event_type"] == "drift_detection"
        assert entry["details"]["drift_score"] == 0.05
        assert entry["operation_id"] == "op789"
        assert "timestamp" in entry


@pytest.mark.asyncio
class TestConsciousnessGuardianIntegration:
    """Test consciousness Guardian integration"""

    @pytest.fixture
    def guardian_config(self):
        """Guardian configuration fixture"""
        return GuardianValidationConfig(
            p95_target_ms=100.0,  # Fast for testing
            drift_threshold=0.15,
            fail_closed_on_error=True,
            gdpr_audit_enabled=True
        )

    @pytest.fixture
    def mock_guardian_system(self):
        """Mock Guardian system fixture"""
        guardian = Mock()
        guardian.serialize_decision = Mock(return_value={
            "decision": {"status": "allow"},
            "integrity": {"content_sha256": "abc123"}
        })
        return guardian

    @pytest.fixture
    def mock_ethics_engine(self):
        """Mock ethics engine fixture"""
        ethics = Mock()
        ethics.validate_action = Mock(return_value=Mock(
            decision="approved",
            rationale="Test approval",
            severity=Mock(value="low"),
            confidence=0.9,
            triad_compliance={"identity": True, "consciousness": True, "guardian": True}
        ))
        return ethics

    @pytest.fixture
    def guardian_integration(self, guardian_config, mock_guardian_system, mock_ethics_engine):
        """Guardian integration fixture"""
        # Mock the guardian imports to avoid import errors
        with patch('lukhas.consciousness.guardian_integration.GUARDIAN_AVAILABLE', True):
            with patch('lukhas.consciousness.guardian_integration.GuardianSystem', return_value=mock_guardian_system):
                with patch('lukhas.consciousness.guardian_integration.EthicsEngine', return_value=mock_ethics_engine):
                    integration = ConsciousnessGuardianIntegration(
                        config=guardian_config,
                        guardian_system=mock_guardian_system,
                        ethics_engine=mock_ethics_engine
                    )
                    return integration

    def test_guardian_integration_initialization(self, guardian_integration, guardian_config):
        """Test Guardian integration initialization"""
        assert guardian_integration.config == guardian_config
        assert guardian_integration._component_id == "ConsciousnessGuardianIntegration"
        assert guardian_integration._consecutive_errors == 0
        assert guardian_integration._emergency_mode is False

    def test_configuration_validation_error(self):
        """Test configuration validation error handling"""
        invalid_config = GuardianValidationConfig(
            p95_target_ms=-100.0,
            drift_threshold=2.0
        )

        with pytest.raises(ValueError, match="Invalid GuardianValidationConfig"):
            ConsciousnessGuardianIntegration(config=invalid_config)

    async def test_consciousness_validation_success(self, guardian_integration):
        """Test successful consciousness validation"""
        # Create test consciousness state
        state = ConsciousnessState(
            phase="REFLECT",
            level=0.7,
            awareness_level=0.8,
            emotional_tone="focused"
        )

        # Create validation context
        context = create_validation_context(
            validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
            consciousness_state=state,
            user_id="test_user",
            session_id="test_session"
        )

        # Mock the Guardian implementation methods to return safe results
        with patch.object(guardian_integration, 'guardian_impl') as mock_impl:
            mock_impl.detect_drift.return_value = Mock(
                drift_score=0.05,
                threshold_exceeded=False,
                severity=Mock(value="low"),
                remediation_needed=False,
                details={"reason": "Within threshold"}
            )
            mock_impl.check_safety.return_value = Mock(
                safe=True,
                risk_level=Mock(value="low"),
                violations=[],
                recommendations=[],
                constitutional_check=True
            )

            # Perform validation
            result = await guardian_integration.validate_consciousness_operation(context)

            # Verify result
            assert result.is_approved() is True
            assert result.validation_duration_ms > 0
            assert result.drift_result.drift_score == 0.05
            assert result.safety_result.safe is True
            assert len(result.audit_trail) > 0

    async def test_consciousness_validation_drift_failure(self, guardian_integration):
        """Test consciousness validation failure due to drift"""
        state = ConsciousnessState(phase="REFLECT", level=0.7)
        context = create_validation_context(
            validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
            consciousness_state=state
        )

        # Mock drift detection to exceed threshold
        with patch.object(guardian_integration, 'guardian_impl') as mock_impl:
            mock_impl.detect_drift.return_value = Mock(
                drift_score=0.25,  # Exceeds 0.15 threshold
                threshold_exceeded=True,
                severity=Mock(value="high"),
                remediation_needed=True,
                details={"reason": "Threshold exceeded"}
            )
            mock_impl.check_safety.return_value = Mock(
                safe=True,
                risk_level=Mock(value="low"),
                violations=[],
                recommendations=[],
                constitutional_check=True
            )

            result = await guardian_integration.validate_consciousness_operation(context)

            # Verify denial due to drift
            assert result.is_approved() is False
            assert "Drift threshold exceeded" in result.reason
            assert result.drift_result.drift_score == 0.25

    async def test_consciousness_validation_safety_failure(self, guardian_integration):
        """Test consciousness validation failure due to safety"""
        state = ConsciousnessState(phase="DECIDE", level=0.9)
        context = create_validation_context(
            validation_type=GuardianValidationType.DECISION_MAKING,
            consciousness_state=state,
            sensitive_operation=True
        )

        # Mock safety failure
        with patch.object(guardian_integration, 'guardian_impl') as mock_impl:
            mock_impl.detect_drift.return_value = Mock(
                drift_score=0.05,
                threshold_exceeded=False,
                severity=Mock(value="low"),
                remediation_needed=False,
                details={"reason": "Within threshold"}
            )
            mock_impl.check_safety.return_value = Mock(
                safe=False,
                risk_level=Mock(value="high"),
                violations=["harmful_content", "privacy_violation"],
                recommendations=["Review content", "Add safeguards"],
                constitutional_check=True
            )

            result = await guardian_integration.validate_consciousness_operation(context)

            # Verify denial due to safety
            assert result.is_approved() is False
            assert "Safety validation failed" in result.reason
            assert result.safety_result.safe is False
            assert len(result.safety_result.violations) == 2

    async def test_performance_target_compliance(self, guardian_integration):
        """Test that validation meets p95 performance targets"""
        state = ConsciousnessState(phase="AWARE", level=0.6)
        context = create_validation_context(
            validation_type=GuardianValidationType.AWARENESS_PROCESSING,
            consciousness_state=state
        )

        # Mock Guardian components for fast response
        with patch.object(guardian_integration, 'guardian_impl') as mock_impl:
            mock_impl.detect_drift.return_value = Mock(
                drift_score=0.05,
                threshold_exceeded=False,
                severity=Mock(value="low"),
                remediation_needed=False,
                details={"reason": "Within threshold"}
            )
            mock_impl.check_safety.return_value = Mock(
                safe=True,
                risk_level=Mock(value="low"),
                violations=[],
                recommendations=[],
                constitutional_check=True
            )

            # Run multiple validations to test performance
            latencies = []
            for _ in range(20):
                start_time = time.time()
                result = await guardian_integration.validate_consciousness_operation(context)
                end_time = time.time()

                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                assert result.validation_duration_ms > 0

            # Calculate p95 latency
            latencies.sort()
            p95_index = int(len(latencies) * 0.95)
            p95_latency = latencies[p95_index]

            # Verify p95 meets target (200ms for test config)
            assert p95_latency < 200.0, f"p95 latency {p95_latency:.2f}ms exceeds target 200ms"

    async def test_fail_closed_behavior_on_error(self, guardian_integration):
        """Test fail-closed behavior when Guardian components fail"""
        state = ConsciousnessState(phase="CREATE", level=0.8)
        context = create_validation_context(
            validation_type=GuardianValidationType.CREATIVE_GENERATION,
            consciousness_state=state
        )

        # Mock Guardian implementation to raise exception
        with patch.object(guardian_integration, 'guardian_impl') as mock_impl:
            mock_impl.detect_drift.side_effect = Exception("Guardian system error")

            result = await guardian_integration.validate_consciousness_operation(context)

            # Verify fail-closed behavior
            assert result.result == ValidationResult.ERROR
            assert result.is_approved() is False
            assert "Guardian validation error" in result.reason

    async def test_emergency_mode_activation(self, guardian_integration):
        """Test emergency mode activation after consecutive errors"""
        state = ConsciousnessState(phase="DECIDE", level=0.7)
        context = create_validation_context(
            validation_type=GuardianValidationType.DECISION_MAKING,
            consciousness_state=state
        )

        # Simulate consecutive errors to trigger emergency mode
        with patch.object(guardian_integration, 'guardian_impl') as mock_impl:
            mock_impl.detect_drift.side_effect = Exception("Persistent error")

            # Trigger multiple failures
            for _ in range(6):  # More than max_consecutive_errors (5)
                result = await guardian_integration.validate_consciousness_operation(context)
                assert result.is_approved() is False

            # Verify emergency mode is active
            assert guardian_integration._emergency_mode is True
            assert guardian_integration._consecutive_errors >= 5

            # Next validation should be handled in emergency mode
            result = await guardian_integration.validate_consciousness_operation(context)
            assert result.result == ValidationResult.DENIED
            assert "Guardian emergency mode active" in result.reason

    def test_baseline_state_management(self, guardian_integration):
        """Test baseline state management for drift detection"""
        state1 = ConsciousnessState(phase="IDLE", level=0.3)
        state2 = ConsciousnessState(phase="AWARE", level=0.7)

        # Update baseline states
        guardian_integration.update_baseline_state(state1, "tenant1", "session1")
        guardian_integration.update_baseline_state(state2, "tenant2", "session2")

        # Verify baseline states are stored
        assert len(guardian_integration._baseline_states) == 2
        assert "tenant1:session1" in guardian_integration._baseline_states
        assert "tenant2:session2" in guardian_integration._baseline_states
        assert guardian_integration._baseline_states["tenant1:session1"] == state1
        assert guardian_integration._baseline_states["tenant2:session2"] == state2

    def test_audit_trail_gdpr_compliance(self, guardian_integration):
        """Test GDPR-compliant audit trail management"""
        # Add audit events
        for i in range(10):
            guardian_integration._add_audit_event(
                event_type=f"test_event_{i}",
                details={"index": i, "data": "test"}
            )

        initial_count = len(guardian_integration._audit_events)
        assert initial_count == 10

        # Simulate time passage beyond retention period
        old_time = time.time() - (guardian_integration._audit_retention_ms / 1000) - 3600
        for event in guardian_integration._audit_events[:5]:
            event["timestamp"] = old_time

        # Add new event to trigger cleanup
        guardian_integration._add_audit_event("new_event", {"cleanup": True})

        # Verify old events were cleaned up
        remaining_events = len(guardian_integration._audit_events)
        assert remaining_events < initial_count
        assert remaining_events == 6  # 5 recent + 1 new

    async def test_gdpr_validation_with_user_consent(self, guardian_integration):
        """Test GDPR validation with user consent"""
        state = ConsciousnessState(phase="REFLECT", level=0.7)
        context = create_validation_context(
            validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
            consciousness_state=state,
            user_id="gdpr_user_123",
            sensitive_operation=True
        )

        # Mock Guardian components
        with patch.object(guardian_integration, 'guardian_impl') as mock_impl:
            mock_impl.detect_drift.return_value = Mock(
                drift_score=0.05,
                threshold_exceeded=False,
                severity=Mock(value="low"),
                remediation_needed=False,
                details={"reason": "Within threshold"}
            )
            mock_impl.check_safety.return_value = Mock(
                safe=True,
                risk_level=Mock(value="low"),
                violations=[],
                recommendations=[],
                constitutional_check=True
            )

            result = await guardian_integration.validate_consciousness_operation(context)

            # Verify GDPR compliance tracking
            assert result.gdpr_compliant is True
            assert result.consent_verified is True
            gdpr_audit = [entry for entry in result.audit_trail if entry["event_type"] == "gdpr_validation"]
            assert len(gdpr_audit) == 1

    def test_performance_statistics(self, guardian_integration):
        """Test performance statistics collection"""
        # Add some test data
        guardian_integration._validation_latencies = [10.0, 15.0, 20.0, 25.0, 30.0]
        guardian_integration._drift_scores = [0.05, 0.08, 0.12, 0.18, 0.22]

        # Create some validation history
        for i in range(10):
            result = GuardianValidationResult(
                operation_id=f"op_{i}",
                validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
                result=ValidationResult.APPROVED if i < 8 else ValidationResult.DENIED
            )
            guardian_integration._validation_history.append(result)

        stats = guardian_integration.get_performance_stats()

        # Verify statistics
        assert "guardian_integration" in stats
        assert "drift_detection" in stats
        assert "validation_success" in stats

        gi_stats = stats["guardian_integration"]
        assert gi_stats["total_validations"] == 5
        assert gi_stats["average_latency_ms"] == 20.0
        assert gi_stats["median_latency_ms"] == 20.0

        drift_stats = stats["drift_detection"]
        assert drift_stats["average_drift_score"] == 0.13
        assert drift_stats["threshold_exceedances"] == 2  # 0.18, 0.22 > 0.15

        success_stats = stats["validation_success"]
        assert success_stats["total_validations"] == 10
        assert success_stats["approved_count"] == 8
        assert success_stats["success_rate"] == 0.8

    async def test_guardian_envelope_generation(self, guardian_integration):
        """Test Guardian decision envelope generation"""
        state = ConsciousnessState(phase="CREATE", level=0.9)
        context = create_validation_context(
            validation_type=GuardianValidationType.CREATIVE_GENERATION,
            consciousness_state=state,
            user_id="envelope_user",
            session_id="envelope_session"
        )

        # Mock Guardian components for approval
        with patch.object(guardian_integration, 'guardian_impl') as mock_impl:
            mock_impl.detect_drift.return_value = Mock(
                drift_score=0.05,
                threshold_exceeded=False,
                severity=Mock(value="low"),
                remediation_needed=False,
                details={"reason": "Within threshold"}
            )
            mock_impl.check_safety.return_value = Mock(
                safe=True,
                risk_level=Mock(value="low"),
                violations=[],
                recommendations=[],
                constitutional_check=True
            )

            result = await guardian_integration.validate_consciousness_operation(context)

            # Verify Guardian envelope was generated for approved operation
            assert result.is_approved() is True
            assert result.guardian_envelope is not None
            assert "decision" in result.guardian_envelope
            assert result.guardian_envelope["decision"]["status"] == "allow"

    async def test_reset_state_functionality(self, guardian_integration):
        """Test state reset functionality"""
        # Add some test data
        guardian_integration._validation_latencies = [10.0, 20.0, 30.0]
        guardian_integration._drift_scores = [0.1, 0.2, 0.3]
        guardian_integration._consecutive_errors = 3
        guardian_integration._emergency_mode = True
        guardian_integration._baseline_states["test"] = ConsciousnessState()

        # Reset state
        await guardian_integration.reset_state()

        # Verify all state is cleared
        assert len(guardian_integration._validation_latencies) == 0
        assert len(guardian_integration._drift_scores) == 0
        assert len(guardian_integration._validation_history) == 0
        assert len(guardian_integration._baseline_states) == 0
        assert len(guardian_integration._state_history) == 0
        assert len(guardian_integration._audit_events) == 0
        assert guardian_integration._consecutive_errors == 0
        assert guardian_integration._emergency_mode is False


if __name__ == "__main__":
    pytest.main([__file__])