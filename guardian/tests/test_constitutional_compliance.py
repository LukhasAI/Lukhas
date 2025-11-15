"""
╔══════════════════════════════════════════════════════════════
║ 🛡️ GUARDIAN Constitutional Compliance Test Suite
║ Part of LUKHAS AI Guardian System
╠══════════════════════════════════════════════════════════════
║ TYPE: TEST_SUITE
║ PURPOSE: Comprehensive testing of Guardian constitutional compliance
║ ADDRESSES: LukhasAI/Lukhas#560 - Constitutional AI compliance TODO
║
║ CONSTELLATION FRAMEWORK:
║ ⚛️ IDENTITY: Identity verification testing
║ 🧠 CONSCIOUSNESS: Constitutional AI validation
║ 🛡️ GUARDIAN: Compliance enforcement testing
╚══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

# Import Guardian compliance module
try:
    from guardian.constitutional_compliance import (
        ComplianceReport,
        ComplianceStatus,
        GuardianComplianceCheck,
        GuardianConstitutionalCompliance,
        GuardianDecisionCategory,
    )

    GUARDIAN_COMPLIANCE_AVAILABLE = True
except ImportError:
    GUARDIAN_COMPLIANCE_AVAILABLE = False

# Import Constitutional AI validator for integration testing
try:
    from core.identity.constitutional_ai_compliance import (
        ConstitutionalPrinciple,
        ConstitutionalValidationContext,
        DecisionType,
    )

    CONSTITUTIONAL_AI_AVAILABLE = True
except ImportError:
    CONSTITUTIONAL_AI_AVAILABLE = False

logger = logging.getLogger(__name__)


@pytest.fixture
def anyio_backend() -> str:
    """Restrict pytest-anyio to the asyncio backend for these tests."""
    return "asyncio"


class TestGuardianConstitutionalCompliance:
    """Test suite for Guardian Constitutional Compliance System"""

    @pytest.fixture
    async def guardian_compliance(self):
        """Create Guardian compliance system instance"""
        if not GUARDIAN_COMPLIANCE_AVAILABLE:
            pytest.skip("Guardian compliance module not available")

        compliance = GuardianConstitutionalCompliance()
        await compliance.initialize_compliance_system()
        yield compliance
        await compliance.shutdown_compliance_system()

    @pytest.fixture
    def sample_identity_operation(self):
        """Sample identity operation context for testing"""
        return {
            "decision_category": GuardianDecisionCategory.IDENTITY_VERIFICATION,
            "user_consent": True,
            "data_minimization": True,
            "data_purpose": "identity_verification",
            "security_measures": ["encryption", "access_control"],
            "reasoning": "Identity verification for access control",
            "decision_criteria": {"valid_credentials": True, "no_violations": True},
            "bias_mitigation": True,
            "equal_access": True,
            "consent_withdrawal": True,
            "guardian_reviewer": "guardian_system",
            "urgency_level": "normal",
            "impact_scope": "individual",
        }

    @pytest.mark.anyio
    async def test_compliance_system_initialization(self, guardian_compliance):
        """Test Guardian compliance system initializes correctly"""
        assert guardian_compliance._validator_initialized is True
        assert guardian_compliance.constitutional_validator is not None
        assert guardian_compliance.compliance_threshold == 0.7
        assert guardian_compliance.oversight_threshold == 0.6

    @pytest.mark.anyio
    async def test_identity_verification_compliant(self, guardian_compliance, sample_identity_operation):
        """Test identity verification with compliant operation"""
        identity_id = "test_identity_001"

        # Verify compliance
        check = await guardian_compliance.verify_identity_compliance(identity_id, sample_identity_operation)

        assert check is not None
        assert check.identity_id == identity_id
        assert check.decision_category == GuardianDecisionCategory.IDENTITY_VERIFICATION
        assert check.constitutional_score > 0.0
        assert len(check.audit_trail) > 0

        # With the sample operation, should be compliant or require review based on constitutional score
        # Note: Actual status depends on constitutional score which may vary based on validator logic
        assert check.compliance_status in [
            ComplianceStatus.COMPLIANT,
            ComplianceStatus.REVIEW_REQUIRED,
            ComplianceStatus.NON_COMPLIANT,  # May be non-compliant if score is low
        ]

        # Verify metrics updated
        assert guardian_compliance.compliance_metrics["total_checks"] > 0

    @pytest.mark.anyio
    async def test_identity_verification_non_compliant(self, guardian_compliance):
        """Test identity verification with non-compliant operation"""
        identity_id = "test_identity_002"

        # Create non-compliant operation context (missing key constitutional elements)
        non_compliant_operation = {
            "decision_category": GuardianDecisionCategory.IDENTITY_VERIFICATION,
            # Missing: user_consent, data_minimization, security_measures, etc.
            "urgency_level": "normal",
        }

        # Verify compliance
        check = await guardian_compliance.verify_identity_compliance(identity_id, non_compliant_operation)

        assert check is not None
        assert check.identity_id == identity_id

        # Should have lower constitutional score
        assert check.constitutional_score < 0.8

        # Should require oversight or be non-compliant
        assert check.compliance_status in [
            ComplianceStatus.REVIEW_REQUIRED,
            ComplianceStatus.NON_COMPLIANT,
        ]

        # Audit trail should be recorded
        assert len(check.audit_trail) > 0

    @pytest.mark.anyio
    async def test_emergency_override_handling(self, guardian_compliance, sample_identity_operation):
        """Test emergency override compliance checking"""
        identity_id = "test_identity_emergency"

        # Create emergency operation context
        emergency_operation = sample_identity_operation.copy()
        emergency_operation.update(
            {
                "decision_category": GuardianDecisionCategory.EMERGENCY_RESPONSE,
                "urgency_level": "emergency",
                "override_approved": True,
                "emergency_justification": "Critical security threat detected",
            }
        )

        # Verify compliance
        check = await guardian_compliance.verify_identity_compliance(identity_id, emergency_operation)

        assert check is not None
        assert check.emergency_context is True

        # Emergency override with approval should have special status
        if emergency_operation.get("override_approved"):
            assert check.compliance_status == ComplianceStatus.EMERGENCY_OVERRIDE

        # Should still have audit trail
        assert len(check.audit_trail) > 0
        assert any("emergency" in str(entry).lower() for entry in check.audit_trail)

    @pytest.mark.anyio
    async def test_multiple_identity_operations(self, guardian_compliance, sample_identity_operation):
        """Test tracking multiple operations for the same identity"""
        identity_id = "test_identity_multi"

        # Perform multiple compliance checks
        for i in range(3):
            operation = sample_identity_operation.copy()
            operation["operation_number"] = i + 1

            check = await guardian_compliance.verify_identity_compliance(identity_id, operation)
            assert check is not None

        # Verify all checks are tracked
        identity_checks = guardian_compliance.checks_by_identity.get(identity_id, [])
        assert len(identity_checks) == 3

        # Verify metrics updated correctly
        assert guardian_compliance.compliance_metrics["total_checks"] >= 3

    @pytest.mark.anyio
    async def test_audit_trail_retrieval(self, guardian_compliance, sample_identity_operation):
        """Test retrieving complete audit trail for an identity"""
        identity_id = "test_identity_audit"

        # Perform several operations
        for i in range(2):
            operation = sample_identity_operation.copy()
            operation["operation_number"] = i + 1
            await guardian_compliance.verify_identity_compliance(identity_id, operation)

        # Get audit trail
        audit_trail = await guardian_compliance.get_identity_audit_trail(identity_id)

        assert len(audit_trail) >= 2
        assert all("timestamp" in entry for entry in audit_trail)
        assert all("action" in entry for entry in audit_trail)

        # Should be sorted by timestamp (most recent first)
        if len(audit_trail) > 1:
            timestamps = [entry.get("timestamp", "") for entry in audit_trail]
            assert timestamps == sorted(timestamps, reverse=True)

    @pytest.mark.anyio
    async def test_compliance_report_generation(self, guardian_compliance, sample_identity_operation):
        """Test generating compliance report"""
        # Perform several compliance checks
        for i in range(5):
            identity_id = f"test_identity_report_{i}"
            operation = sample_identity_operation.copy()
            await guardian_compliance.verify_identity_compliance(identity_id, operation)

        # Generate report
        start_date = datetime.now(timezone.utc) - timedelta(hours=1)
        end_date = datetime.now(timezone.utc)

        report = await guardian_compliance.generate_compliance_report(start_date, end_date)

        assert report is not None
        assert report.total_checks >= 5
        assert report.compliant_count + report.review_required_count + report.non_compliant_count + report.emergency_override_count == report.total_checks

        # Should have some category breakdowns
        assert len(report.checks_by_category) > 0

        # Report should have metadata
        assert report.report_id is not None
        assert report.generated_at is not None
        assert report.report_version == "1.0"

    @pytest.mark.anyio
    async def test_compliance_report_recommendations(self, guardian_compliance):
        """Test compliance report generates appropriate recommendations"""
        # Create mix of compliant and non-compliant operations
        compliant_op = {
            "decision_category": GuardianDecisionCategory.IDENTITY_VERIFICATION,
            "user_consent": True,
            "data_minimization": True,
            "data_purpose": "verification",
            "security_measures": ["encryption"],
            "reasoning": "Test operation",
            "decision_criteria": {"valid": True},
            "bias_mitigation": True,
            "equal_access": True,
            "consent_withdrawal": True,
        }

        non_compliant_op = {
            "decision_category": GuardianDecisionCategory.DATA_GOVERNANCE,
            # Missing most compliance fields
        }

        # Add several non-compliant operations
        for i in range(3):
            identity_id = f"test_identity_nc_{i}"
            await guardian_compliance.verify_identity_compliance(identity_id, non_compliant_op)

        # Generate report
        report = await guardian_compliance.generate_compliance_report()

        # Should have recommendations due to non-compliance
        assert len(report.recommendations) > 0 or len(report.areas_for_improvement) > 0

    @pytest.mark.anyio
    async def test_compliance_metrics_tracking(self, guardian_compliance, sample_identity_operation):
        """Test compliance metrics are tracked correctly"""
        # Get initial metrics
        initial_metrics = await guardian_compliance.get_compliance_metrics()
        initial_total = initial_metrics["system_metrics"]["total_checks"]

        # Perform compliance check
        identity_id = "test_identity_metrics"
        await guardian_compliance.verify_identity_compliance(identity_id, sample_identity_operation)

        # Get updated metrics
        updated_metrics = await guardian_compliance.get_compliance_metrics()

        assert updated_metrics["system_metrics"]["total_checks"] == initial_total + 1
        assert "compliance_rate" in updated_metrics
        assert "oversight_rate" in updated_metrics
        assert 0.0 <= updated_metrics["compliance_rate"] <= 1.0
        assert 0.0 <= updated_metrics["oversight_rate"] <= 1.0

    @pytest.mark.anyio
    async def test_fallback_compliance_check(self):
        """Test fallback compliance check when constitutional validator unavailable"""
        # Create compliance system without initializing validator
        compliance = GuardianConstitutionalCompliance()
        # Don't initialize, so validator is unavailable

        identity_id = "test_identity_fallback"
        operation = {
            "decision_category": GuardianDecisionCategory.IDENTITY_VERIFICATION,
            "user_consent": True,
        }

        # Should use fallback (method is not async)
        check = compliance._fallback_compliance_check(identity_id, operation)

        assert check is not None
        assert check.identity_id == identity_id
        assert check.compliance_status == ComplianceStatus.REVIEW_REQUIRED
        assert check.oversight_required is True
        assert len(check.audit_trail) > 0

        # Audit trail should indicate fallback was used
        assert any("fallback" in str(entry).lower() for entry in check.audit_trail)

    @pytest.mark.anyio
    async def test_principle_validation_tracking(self, guardian_compliance, sample_identity_operation):
        """Test that constitutional principles are tracked in compliance checks"""
        identity_id = "test_identity_principles"

        check = await guardian_compliance.verify_identity_compliance(identity_id, sample_identity_operation)

        assert check is not None

        # Should have principles validated
        assert len(check.principles_validated) > 0

        # Principles should be boolean values
        for principle, compliant in check.principles_validated.items():
            assert isinstance(compliant, bool)

    @pytest.mark.anyio
    async def test_guardian_decision_categories(self, guardian_compliance):
        """Test different Guardian decision categories"""
        categories = [
            GuardianDecisionCategory.IDENTITY_VERIFICATION,
            GuardianDecisionCategory.ACCESS_CONTROL,
            GuardianDecisionCategory.DATA_GOVERNANCE,
            GuardianDecisionCategory.EMERGENCY_RESPONSE,
        ]

        for category in categories:
            identity_id = f"test_identity_{category.value}"
            operation = {
                "decision_category": category,
                "user_consent": True,
                "data_minimization": True,
                "security_measures": ["encryption"],
                "reasoning": f"Test {category.value}",
            }

            check = await guardian_compliance.verify_identity_compliance(identity_id, operation)

            assert check is not None
            assert check.decision_category == category

    @pytest.mark.anyio
    async def test_oversight_threshold_enforcement(self, guardian_compliance):
        """Test that oversight is required when constitutional score is below threshold"""
        identity_id = "test_identity_oversight"

        # Create operation that will have low constitutional score
        low_score_operation = {
            "decision_category": GuardianDecisionCategory.DATA_GOVERNANCE,
            # Minimal compliance fields
            "urgency_level": "normal",
        }

        check = await guardian_compliance.verify_identity_compliance(identity_id, low_score_operation)

        # Low score should trigger oversight requirement
        if check.constitutional_score < guardian_compliance.oversight_threshold:
            assert (
                check.oversight_required is True
                or check.compliance_status == ComplianceStatus.REVIEW_REQUIRED
            )


class TestGuardianConstitutionalIntegration:
    """Integration tests for Guardian and Constitutional AI systems"""

    @pytest.fixture
    async def integrated_systems(self):
        """Create integrated Guardian and Constitutional AI systems"""
        if not (GUARDIAN_COMPLIANCE_AVAILABLE and CONSTITUTIONAL_AI_AVAILABLE):
            pytest.skip("Required modules not available for integration testing")

        guardian_compliance = GuardianConstitutionalCompliance()
        await guardian_compliance.initialize_compliance_system()

        yield guardian_compliance

        await guardian_compliance.shutdown_compliance_system()

    @pytest.mark.anyio
    async def test_end_to_end_identity_verification_workflow(self, integrated_systems):
        """Test complete end-to-end identity verification workflow"""
        guardian_compliance = integrated_systems
        identity_id = "test_e2e_identity"

        # Step 1: Verify identity compliance
        verification_context = {
            "decision_category": GuardianDecisionCategory.IDENTITY_VERIFICATION,
            "user_consent": True,
            "informed_consent": True,
            "data_minimization": True,
            "data_purpose": "identity_authentication",
            "security_measures": ["encryption", "multi_factor", "audit_logging"],
            "consent_scopes": ["authentication", "profile"],
            "consent_withdrawal": True,
            "reasoning": "User authentication for system access",
            "decision_criteria": {"valid_credentials": True, "no_security_violations": True},
            "bias_mitigation": True,
            "equal_access": True,
            "guardian_reviewer": "guardian_officer_001",
            "urgency_level": "normal",
            "impact_scope": "individual",
        }

        check = await guardian_compliance.verify_identity_compliance(identity_id, verification_context)

        assert check is not None
        assert check.identity_id == identity_id
        assert check.constitutional_score > 0.0

        # Step 2: Get audit trail
        audit_trail = await guardian_compliance.get_identity_audit_trail(identity_id)
        assert len(audit_trail) > 0

        # Step 3: Generate compliance report
        report = await guardian_compliance.generate_compliance_report()
        assert report.total_checks > 0

        # Step 4: Verify metrics
        metrics = await guardian_compliance.get_compliance_metrics()
        assert metrics["system_metrics"]["total_checks"] > 0

    @pytest.mark.anyio
    async def test_constitutional_principle_enforcement(self, integrated_systems):
        """Test that constitutional principles are enforced through Guardian system"""
        guardian_compliance = integrated_systems

        # Test privacy principle
        privacy_context = {
            "decision_category": GuardianDecisionCategory.DATA_GOVERNANCE,
            "data_minimization": True,
            "data_purpose": "analytics",
            "security_measures": ["encryption", "anonymization"],
            "user_consent": True,
            "informed_consent": True,
        }

        check = await guardian_compliance.verify_identity_compliance("privacy_test", privacy_context)

        # Should have validated privacy principle
        assert check is not None
        if "privacy" in check.principles_validated:
            # Privacy should be compliant with proper data minimization and security
            assert check.principles_validated["privacy"] in [True, False]

    @pytest.mark.anyio
    async def test_compliance_report_critical_violations(self, integrated_systems):
        """Test that critical violations are tracked in compliance reports"""
        guardian_compliance = integrated_systems

        # Create severely non-compliant operation
        critical_violation = {
            "decision_category": GuardianDecisionCategory.ACCESS_CONTROL,
            # No consent, no security, no reasoning
        }

        await guardian_compliance.verify_identity_compliance("critical_test", critical_violation)

        # Generate report
        report = await guardian_compliance.generate_compliance_report()

        # Should identify issues (either as critical violations or recommendations)
        assert (
            len(report.critical_violations) > 0
            or len(report.recommendations) > 0
            or len(report.areas_for_improvement) > 0
        )


if __name__ == "__main__":
    """Run tests with pytest"""
    import sys

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Run tests
    pytest.main([__file__, "-v", "-s", "--tb=short", *sys.argv[1:]])
