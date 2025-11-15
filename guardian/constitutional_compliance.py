"""
╔══════════════════════════════════════════════════════════════
║ 🛡️ GUARDIAN Constitutional Compliance Integration
║ Part of LUKHAS AI Guardian System
╠══════════════════════════════════════════════════════════════
║ TYPE: COMPLIANCE_SYSTEM
║ ROLE: Guardian-level constitutional AI compliance enforcement
║ PURPOSE: Identity verification and compliance validation for Guardian operations
║
║ CONSTELLATION FRAMEWORK:
║ ⚛️ IDENTITY: Identity verification and validation
║ 🧠 CONSCIOUSNESS: Ethical AI decision oversight
║ 🛡️ GUARDIAN: Constitutional compliance enforcement
╚══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ComplianceStatus(Enum):
    """Guardian compliance status levels"""

    COMPLIANT = "compliant"
    REVIEW_REQUIRED = "review_required"
    NON_COMPLIANT = "non_compliant"
    EMERGENCY_OVERRIDE = "emergency_override"


class GuardianDecisionCategory(Enum):
    """Categories of Guardian decisions requiring compliance validation"""

    IDENTITY_VERIFICATION = "identity_verification"
    ACCESS_CONTROL = "access_control"
    DATA_GOVERNANCE = "data_governance"
    EMERGENCY_RESPONSE = "emergency_response"
    POLICY_ENFORCEMENT = "policy_enforcement"
    AUDIT_REVIEW = "audit_review"


@dataclass
class GuardianComplianceCheck:
    """Guardian compliance check record"""

    check_id: str = field(default_factory=lambda: f"gcc-{uuid.uuid4().hex[:12]}")
    decision_category: GuardianDecisionCategory = GuardianDecisionCategory.IDENTITY_VERIFICATION
    identity_id: str = ""
    compliance_status: ComplianceStatus = ComplianceStatus.REVIEW_REQUIRED

    # Constitutional validation details
    constitutional_score: float = 0.0
    principles_validated: dict[str, bool] = field(default_factory=dict)
    validation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Guardian-specific context
    guardian_reviewer: str = ""
    oversight_required: bool = False
    emergency_context: bool = False

    # Audit trail
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    compliance_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceReport:
    """Guardian compliance report"""

    report_id: str = field(default_factory=lambda: f"gcr-{uuid.uuid4().hex[:12]}")
    report_period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    report_period_end: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Summary statistics
    total_checks: int = 0
    compliant_count: int = 0
    review_required_count: int = 0
    non_compliant_count: int = 0
    emergency_override_count: int = 0

    # Detailed breakdowns
    checks_by_category: dict[str, int] = field(default_factory=dict)
    compliance_by_principle: dict[str, float] = field(default_factory=dict)

    # Notable incidents
    critical_violations: list[GuardianComplianceCheck] = field(default_factory=list)
    emergency_overrides: list[GuardianComplianceCheck] = field(default_factory=list)

    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    areas_for_improvement: list[str] = field(default_factory=list)

    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    report_version: str = "1.0"


class GuardianConstitutionalCompliance:
    """
    Guardian Constitutional Compliance System

    Integrates with core Constitutional AI validator to provide Guardian-level
    compliance checking, identity verification, and audit trail management.
    """

    def __init__(self):
        # Constitutional AI validator integration
        self.constitutional_validator = None
        self._validator_initialized = False

        # Compliance check history
        self.compliance_checks: list[GuardianComplianceCheck] = []
        self.checks_by_identity: dict[str, list[GuardianComplianceCheck]] = defaultdict(list)

        # Audit trail
        self.audit_events: list[dict[str, Any]] = []

        # Metrics
        self.compliance_metrics = {
            "total_checks": 0,
            "compliant_checks": 0,
            "review_required_checks": 0,
            "non_compliant_checks": 0,
            "average_constitutional_score": 0.0,
        }

        # Configuration
        self.oversight_threshold = 0.6  # Constitutional score below this requires oversight
        self.compliance_threshold = 0.7  # Minimum score for automatic compliance

        logger.info("🛡️ Guardian Constitutional Compliance system initialized")

    async def initialize_compliance_system(self) -> bool:
        """Initialize Guardian compliance system with Constitutional AI validator"""
        try:
            # Import and initialize constitutional validator
            from core.identity.constitutional_ai_compliance import ConstitutionalAIValidator

            self.constitutional_validator = ConstitutionalAIValidator()
            await self.constitutional_validator.initialize_constitutional_validation()

            self._validator_initialized = True
            logger.info("✅ Guardian compliance system initialized with Constitutional AI validator")
            return True

        except ImportError as e:
            logger.error(f"❌ Failed to import Constitutional AI validator: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Guardian compliance system: {e}")
            return False

    async def verify_identity_compliance(
        self, identity_id: str, operation_context: dict[str, Any]
    ) -> GuardianComplianceCheck:
        """
        Verify identity operation compliance with Constitutional AI principles

        Args:
            identity_id: Identity being verified
            operation_context: Context of the operation requiring verification

        Returns:
            GuardianComplianceCheck with compliance status and details
        """
        if not self._validator_initialized:
            logger.warning("⚠️ Constitutional validator not initialized, using fallback validation")
            return self._fallback_compliance_check(identity_id, operation_context)

        try:
            # Import required types
            from core.identity.constitutional_ai_compliance import (
                ConstitutionalValidationContext,
                DecisionType,
            )

            # Map Guardian decision category to Constitutional decision type
            decision_type_mapping = {
                GuardianDecisionCategory.IDENTITY_VERIFICATION: DecisionType.IDENTITY_CREATION,
                GuardianDecisionCategory.ACCESS_CONTROL: DecisionType.ACCESS_GRANT,
                GuardianDecisionCategory.DATA_GOVERNANCE: DecisionType.DATA_PROCESSING,
                GuardianDecisionCategory.EMERGENCY_RESPONSE: DecisionType.EMERGENCY_OVERRIDE,
                GuardianDecisionCategory.POLICY_ENFORCEMENT: DecisionType.ACCESS_GRANT,
                GuardianDecisionCategory.AUDIT_REVIEW: DecisionType.ACCESS_GRANT,
            }

            decision_category = operation_context.get(
                "decision_category", GuardianDecisionCategory.IDENTITY_VERIFICATION
            )
            decision_type = decision_type_mapping.get(decision_category, DecisionType.AUTHENTICATION)

            # Create constitutional validation context
            validation_context = ConstitutionalValidationContext(
                decision_type=decision_type,
                identity_id=identity_id,
                decision_data=operation_context,
                decision_maker=operation_context.get("guardian_reviewer", "guardian_system"),
                urgency_level=operation_context.get("urgency_level", "normal"),
                impact_scope=operation_context.get("impact_scope", "individual"),
            )

            # Perform constitutional validation
            validation_result = await self.constitutional_validator.validate_identity_decision(
                validation_context
            )

            # Create Guardian compliance check
            compliance_check = GuardianComplianceCheck(
                decision_category=decision_category,
                identity_id=identity_id,
                constitutional_score=validation_result.overall_compliance_score,
                guardian_reviewer=operation_context.get("guardian_reviewer", ""),
                oversight_required=validation_result.human_oversight_required,
                emergency_context=(operation_context.get("urgency_level") == "emergency"),
            )

            # Extract validated principles
            compliance_check.principles_validated = {
                principle.value: evaluation.compliant
                for principle, evaluation in validation_result.principle_evaluations.items()
            }

            # Determine compliance status
            if validation_result.constitutional_compliant:
                compliance_check.compliance_status = ComplianceStatus.COMPLIANT
            elif validation_result.human_oversight_required or validation_result.overall_compliance_score < self.oversight_threshold:
                compliance_check.compliance_status = ComplianceStatus.REVIEW_REQUIRED
            else:
                compliance_check.compliance_status = ComplianceStatus.NON_COMPLIANT

            # Handle emergency overrides
            if compliance_check.emergency_context and operation_context.get("override_approved"):
                compliance_check.compliance_status = ComplianceStatus.EMERGENCY_OVERRIDE

            # Add to audit trail
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "compliance_verification",
                "identity_id": identity_id,
                "compliance_status": compliance_check.compliance_status.value,
                "constitutional_score": compliance_check.constitutional_score,
                "validation_id": validation_result.validation_id,
            }
            compliance_check.audit_trail.append(audit_entry)
            self.audit_events.append(audit_entry)

            # Store compliance check
            self.compliance_checks.append(compliance_check)
            self.checks_by_identity[identity_id].append(compliance_check)

            # Update metrics
            self._update_compliance_metrics(compliance_check)

            logger.info(
                f"🛡️ Identity compliance verified: {identity_id} - Status: {compliance_check.compliance_status.value} (Score: {compliance_check.constitutional_score:.3f})"
            )

            return compliance_check

        except Exception as e:
            logger.error(f"❌ Error during compliance verification: {e}")
            return self._fallback_compliance_check(identity_id, operation_context)

    def _fallback_compliance_check(
        self, identity_id: str, operation_context: dict[str, Any]
    ) -> GuardianComplianceCheck:
        """Fallback compliance check when constitutional validator is unavailable"""
        logger.warning("⚠️ Using fallback compliance check")

        compliance_check = GuardianComplianceCheck(
            decision_category=operation_context.get(
                "decision_category", GuardianDecisionCategory.IDENTITY_VERIFICATION
            ),
            identity_id=identity_id,
            compliance_status=ComplianceStatus.REVIEW_REQUIRED,
            constitutional_score=0.5,  # Default moderate score
            oversight_required=True,  # Always require oversight in fallback
        )

        # Add fallback audit entry
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "fallback_compliance_check",
            "identity_id": identity_id,
            "reason": "constitutional_validator_unavailable",
        }
        compliance_check.audit_trail.append(audit_entry)
        self.audit_events.append(audit_entry)

        return compliance_check

    async def generate_compliance_report(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> ComplianceReport:
        """
        Generate Guardian compliance report for specified period

        Args:
            start_date: Report period start (defaults to 24 hours ago)
            end_date: Report period end (defaults to now)

        Returns:
            ComplianceReport with summary and detailed compliance information
        """
        if start_date is None:
            start_date = datetime.now(timezone.utc) - timedelta(days=1)
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        # Filter checks within period
        period_checks = [
            check
            for check in self.compliance_checks
            if start_date <= check.validation_timestamp <= end_date
        ]

        # Create report
        report = ComplianceReport(
            report_period_start=start_date,
            report_period_end=end_date,
            total_checks=len(period_checks),
        )

        # Calculate summary statistics
        for check in period_checks:
            if check.compliance_status == ComplianceStatus.COMPLIANT:
                report.compliant_count += 1
            elif check.compliance_status == ComplianceStatus.REVIEW_REQUIRED:
                report.review_required_count += 1
            elif check.compliance_status == ComplianceStatus.NON_COMPLIANT:
                report.non_compliant_count += 1
                # Track critical violations
                if check.constitutional_score < 0.5:
                    report.critical_violations.append(check)
            elif check.compliance_status == ComplianceStatus.EMERGENCY_OVERRIDE:
                report.emergency_override_count += 1
                report.emergency_overrides.append(check)

            # Track by category
            category = check.decision_category.value
            report.checks_by_category[category] = report.checks_by_category.get(category, 0) + 1

            # Track principle compliance
            for principle, compliant in check.principles_validated.items():
                if principle not in report.compliance_by_principle:
                    report.compliance_by_principle[principle] = 0.0
                report.compliance_by_principle[principle] += (1.0 if compliant else 0.0)

        # Calculate average compliance by principle
        if period_checks:
            for principle in report.compliance_by_principle:
                report.compliance_by_principle[principle] /= len(period_checks)

        # Generate recommendations
        if report.non_compliant_count > report.total_checks * 0.1:
            report.recommendations.append(
                "High non-compliance rate detected. Review and strengthen compliance processes."
            )

        if report.emergency_override_count > 0:
            report.recommendations.append(
                f"Review {report.emergency_override_count} emergency override(s) for policy compliance."
            )

        # Identify areas for improvement
        for principle, compliance_rate in report.compliance_by_principle.items():
            if compliance_rate < 0.7:
                report.areas_for_improvement.append(
                    f"Low compliance for {principle}: {compliance_rate:.1%}"
                )

        logger.info(
            f"📊 Generated compliance report: {report.total_checks} checks, {report.compliant_count} compliant ({report.compliant_count / max(report.total_checks, 1):.1%})"
        )

        return report

    async def get_identity_audit_trail(self, identity_id: str) -> list[dict[str, Any]]:
        """
        Get complete audit trail for an identity

        Args:
            identity_id: Identity to retrieve audit trail for

        Returns:
            List of audit events for the identity
        """
        identity_checks = self.checks_by_identity.get(identity_id, [])
        audit_trail = []

        for check in identity_checks:
            audit_trail.extend(check.audit_trail)

        # Sort by timestamp
        audit_trail.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        logger.info(f"📋 Retrieved audit trail for {identity_id}: {len(audit_trail)} events")
        return audit_trail

    async def get_compliance_metrics(self) -> dict[str, Any]:
        """Get current compliance metrics"""
        return {
            "system_metrics": self.compliance_metrics.copy(),
            "recent_checks": len([c for c in self.compliance_checks[-100:]]),
            "compliance_rate": (
                self.compliance_metrics["compliant_checks"] / max(self.compliance_metrics["total_checks"], 1)
            ),
            "oversight_rate": (
                self.compliance_metrics["review_required_checks"] / max(self.compliance_metrics["total_checks"], 1)
            ),
        }

    def _update_compliance_metrics(self, check: GuardianComplianceCheck) -> None:
        """Update internal compliance metrics"""
        self.compliance_metrics["total_checks"] += 1

        if check.compliance_status == ComplianceStatus.COMPLIANT:
            self.compliance_metrics["compliant_checks"] += 1
        elif check.compliance_status == ComplianceStatus.REVIEW_REQUIRED:
            self.compliance_metrics["review_required_checks"] += 1
        elif check.compliance_status == ComplianceStatus.NON_COMPLIANT:
            self.compliance_metrics["non_compliant_checks"] += 1

        # Update average constitutional score
        total = self.compliance_metrics["total_checks"]
        current_avg = self.compliance_metrics["average_constitutional_score"]
        new_avg = ((current_avg * (total - 1)) + check.constitutional_score) / total
        self.compliance_metrics["average_constitutional_score"] = new_avg

    async def shutdown_compliance_system(self) -> None:
        """Shutdown Guardian compliance system"""
        logger.info("🛑 Shutting down Guardian compliance system...")

        if self._validator_initialized and self.constitutional_validator:
            await self.constitutional_validator.shutdown_constitutional_validation()

        logger.info(f"📊 Final compliance metrics: {self.compliance_metrics}")
        logger.info("✅ Guardian compliance system shutdown complete")


# Global Guardian compliance instance
guardian_constitutional_compliance = GuardianConstitutionalCompliance()


__all__ = [
    "ComplianceStatus",
    "GuardianDecisionCategory",
    "GuardianComplianceCheck",
    "ComplianceReport",
    "GuardianConstitutionalCompliance",
    "guardian_constitutional_compliance",
]
