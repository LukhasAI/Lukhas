# owner: Jules-04
# tier: tier2
# module_uid: candidate.governance.guardian_system_integration
# criticality: P0
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from labs.governance.guardian_system_integration import (
    GuardianStatus,
    GuardianSystemIntegration,
    GuardianValidationRequest,
    ValidationResult,
)


async def create_initialized_guardian():
    """Helper to create and initialize a mocked GuardianSystemIntegration."""
    with (
        patch("labs.governance.guardian_system_integration.ConsentLedgerV1"),
        patch("labs.governance.guardian_system_integration.AdvancedDriftDetector"),
        patch("labs.governance.guardian_system_integration.ComprehensiveEthicsPolicyEngine"),
        patch("labs.governance.guardian_system_integration.ComprehensiveAuditSystem"),
        patch("labs.governance.guardian_system_integration.GlyphEngine"),
    ):
        guardian = GuardianSystemIntegration()
        # Since the components are mocked at import time, we need to create new mocks
        # and assign them to the instance.
        guardian.consent_ledger = MagicMock()
        guardian.drift_detector = MagicMock()
        guardian.ethics_engine = MagicMock()
        guardian.audit_system = MagicMock()
        guardian.glyph_engine = MagicMock()

        guardian.status = GuardianStatus.ACTIVE
        return guardian


@pytest.mark.asyncio
class TestGuardianSystemIntegration:
    async def test_validate_action_approved(self):
        """Test that a safe action is approved by the guardian system."""
        guardian_system = await create_initialized_guardian()
        guardian_system.consent_ledger.check_consent.return_value = {"allowed": True}
        guardian_system.drift_detector.measure_drift = AsyncMock(
            return_value=MagicMock(drift_score=0.1, threshold_exceeded=False)
        )
        guardian_system.ethics_engine.evaluate_action = AsyncMock(
            return_value=MagicMock(
                overall_ethical_score=0.9,
                constitutional_compliance=True,
                recommended_action=MagicMock(value="approve"),
                policy_violations=[],
            )
        )
        guardian_system.audit_system.log_event = AsyncMock(return_value="event-id-123")

        request = GuardianValidationRequest(
            request_id="test-req-1",
            timestamp=datetime.now(timezone.utc),
            user_id="test-user",
            session_id="test-session-1",
            action="view_public_document",
            resource="/documents/public/1",
            context={},
        )

        response = await guardian_system.validate_action(request)

        assert response.result == ValidationResult.APPROVED
        assert response.reasoning

    async def test_validate_action_consent_denied(self):
        """Test that an action is denied if consent is not given."""
        guardian_system = await create_initialized_guardian()
        guardian_system.consent_ledger.check_consent.return_value = {"allowed": False, "reason": "consent_not_granted"}
        guardian_system.drift_detector.measure_drift = AsyncMock(
            return_value=MagicMock(drift_score=0.1, threshold_exceeded=False)
        )
        guardian_system.ethics_engine.evaluate_action = AsyncMock(
            return_value=MagicMock(
                overall_ethical_score=0.9,
                constitutional_compliance=True,
                recommended_action=MagicMock(value="approve"),
                policy_violations=[],
            )
        )
        guardian_system.audit_system.log_event = AsyncMock(return_value="event-id-123")

        request = GuardianValidationRequest(
            request_id="test-req-2",
            timestamp=datetime.now(timezone.utc),
            user_id="test-user",
            session_id="test-session-2",
            action="view_private_document",
            resource="/documents/private/1",
            context={},
        )

        response = await guardian_system.validate_action(request)

        assert response.result == ValidationResult.DENIED
        assert "consent_denied" in response.reasoning

    async def test_validate_action_drift_detected(self):
        """Test that an action is flagged when drift is detected."""
        guardian_system = await create_initialized_guardian()
        guardian_system.consent_ledger.check_consent.return_value = {"allowed": True}
        guardian_system.drift_detector.measure_drift = AsyncMock(
            return_value=MagicMock(drift_score=0.2, threshold_exceeded=True)
        )
        guardian_system.ethics_engine.evaluate_action = AsyncMock(
            return_value=MagicMock(
                overall_ethical_score=0.9,
                constitutional_compliance=True,
                recommended_action=MagicMock(value="approve"),
                policy_violations=[],
            )
        )
        guardian_system.audit_system.log_event = AsyncMock(return_value="event-id-123")

        request = GuardianValidationRequest(
            request_id="test-req-3",
            timestamp=datetime.now(timezone.utc),
            user_id="test-user",
            session_id="test-session-3",
            action="execute_sensitive_command",
            resource="system:config",
            context={},
        )

        response = await guardian_system.validate_action(request)

        assert response.result == ValidationResult.DRIFT_DETECTED
        assert "drift_threshold_exceeded" in response.reasoning

    async def test_validate_action_ethics_denial(self):
        """Test that an action is denied based on ethics evaluation."""
        guardian_system = await create_initialized_guardian()
        guardian_system.consent_ledger.check_consent.return_value = {"allowed": True}
        guardian_system.drift_detector.measure_drift = AsyncMock(
            return_value=MagicMock(drift_score=0.1, threshold_exceeded=False)
        )
        guardian_system.ethics_engine.evaluate_action = AsyncMock(
            return_value=MagicMock(
                overall_ethical_score=0.3,
                constitutional_compliance=False,
                recommended_action=MagicMock(value="deny"),
                policy_violations=["test_violation"],
            )
        )
        guardian_system.audit_system.log_event = AsyncMock(return_value="event-id-123")

        request = GuardianValidationRequest(
            request_id="test-req-4",
            timestamp=datetime.now(timezone.utc),
            user_id="test-user",
            session_id="test-session-4",
            action="generate_harmful_content",
            resource="text_generator",
            context={},
        )

        response = await guardian_system.validate_action(request)

        assert response.result == ValidationResult.EMERGENCY_STOP
        assert "constitutional_violation" in response.reasoning

    async def test_validation_timeout(self):
        """Test that the validation times out if a component is too slow."""
        guardian_system = await create_initialized_guardian()
        guardian_system.consent_ledger.check_consent.return_value = {"allowed": True}
        guardian_system.drift_detector.measure_drift = AsyncMock(
            return_value=MagicMock(drift_score=0.1, threshold_exceeded=False)
        )

        async def slow_ethics(*args, **kwargs):
            await asyncio.sleep(0.5)
            return MagicMock(
                overall_ethical_score=0.9,
                constitutional_compliance=True,
                recommended_action=MagicMock(value="approve"),
                policy_violations=[],
            )

        guardian_system.ethics_engine.evaluate_action = slow_ethics
        guardian_system.audit_system.log_event = AsyncMock(return_value="event-id-123")

        request = GuardianValidationRequest(
            request_id="test-req-5",
            timestamp=datetime.now(timezone.utc),
            user_id="test-user",
            session_id="test-session-5",
            action="some_action",
            resource="some_resource",
            context={},
            max_validation_time_ms=100,
        )

        response = await guardian_system.validate_action(request)

        assert response.result == ValidationResult.EMERGENCY_STOP
        assert "timeout" in response.reasoning
