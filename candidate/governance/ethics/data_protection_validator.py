"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


GDPR Data Protection Compliance Validator
=========================================

Comprehensive GDPR compliance validation framework including:
- Data processing lawfulness assessment
- Data subject rights validation
- Privacy by design compliance
- Data protection impact assessments
- Consent management validation
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class LawfulBasis(Enum):
    """GDPR lawful bases for processing"""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class DataCategory(Enum):
    """Categories of personal data"""

    PERSONAL_DATA = "personal_data"
    SENSITIVE_DATA = "sensitive_data"
    CRIMINAL_DATA = "criminal_data"
    BIOMETRIC_DATA = "biometric_data"
    HEALTH_DATA = "health_data"
    GENETIC_DATA = "genetic_data"


class ProcessingPurpose(Enum):
    """Data processing purposes"""

    SERVICE_PROVISION = "service_provision"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    RESEARCH = "research"
    COMPLIANCE = "compliance"
    SECURITY = "security"


@dataclass
class DataProcessingActivity:
    """Data processing activity profile"""

    activity_id: str
    name: str
    description: str
    controller: str
    processor: Optional[str]
    data_categories: list[DataCategory]
    lawful_basis: LawfulBasis
    purposes: list[ProcessingPurpose]
    data_subjects: list[str]
    retention_period: Optional[str]
    international_transfers: bool
    automated_decision_making: bool
    profiling: bool


@dataclass
class GDPRAssessment:
    """GDPR compliance assessment result"""

    activity_id: str
    compliance_status: str
    assessment_date: datetime
    lawfulness_score: float
    privacy_rights_score: float
    security_score: float
    transparency_score: float
    overall_score: float
    violations: list[str]
    recommendations: list[str]
    next_review_date: datetime


class GDPRValidator:
    """
    GDPR compliance validation engine

    Provides comprehensive validation against GDPR requirements including:
    - Lawfulness of processing assessment
    - Data subject rights compliance
    - Privacy by design validation
    - Security measures assessment
    """

    def __init__(self):
        self.required_policies = {
            "privacy_policy",
            "data_retention_policy",
            "data_subject_rights_procedure",
            "data_breach_procedure",
            "privacy_by_design_policy",
        }

        self.data_subject_rights = {
            "right_of_access",
            "right_to_rectification",
            "right_to_erasure",
            "right_to_restrict_processing",
            "right_to_data_portability",
            "right_to_object",
            "rights_related_to_automated_decision_making",
        }

        self.security_measures = {
            "encryption_at_rest",
            "encryption_in_transit",
            "access_controls",
            "audit_logging",
            "backup_procedures",
            "incident_response",
        }

    async def assess_gdpr_compliance(self, activity: DataProcessingActivity) -> GDPRAssessment:
        """
        Comprehensive GDPR compliance assessment

        Args:
            activity: Data processing activity to assess

        Returns:
            GDPRAssessment with detailed compliance analysis
        """
        try:
            violations = []
            recommendations = []

            # Assess lawfulness of processing
            lawfulness_score, lawfulness_issues = await self._assess_lawfulness(activity)
            violations.extend(lawfulness_issues)

            # Assess data subject rights
            rights_score, rights_issues = await self._assess_data_subject_rights(activity)
            violations.extend(rights_issues)

            # Assess security measures
            security_score, security_issues = await self._assess_security_measures(activity)
            violations.extend(security_issues)

            # Assess transparency
            transparency_score, transparency_issues = await self._assess_transparency(activity)
            violations.extend(transparency_issues)

            # Generate recommendations
            recommendations = await self._generate_recommendations(violations, activity)

            # Calculate overall score
            overall_score = (lawfulness_score + rights_score + security_score + transparency_score) / 4

            # Determine compliance status
            compliance_status = self._determine_compliance_status(overall_score, violations)

            return GDPRAssessment(
                activity_id=activity.activity_id,
                compliance_status=compliance_status,
                assessment_date=datetime.now(),
                lawfulness_score=lawfulness_score,
                privacy_rights_score=rights_score,
                security_score=security_score,
                transparency_score=transparency_score,
                overall_score=overall_score,
                violations=violations,
                recommendations=recommendations,
                next_review_date=self._calculate_next_review_date(overall_score),
            )

        except Exception as e:
            logger.error(f"GDPR assessment failed for {activity.activity_id}: {e}")
            raise

    async def _assess_lawfulness(self, activity: DataProcessingActivity) -> tuple[float, list[str]]:
        """Assess lawfulness of processing"""
        issues = []
        score = 1.0

        # Check lawful basis validity
        if activity.lawful_basis == LawfulBasis.CONSENT:
            if not hasattr(activity, "consent_mechanism"):
                issues.append("Consent mechanism not documented")
                score -= 0.3
            if not hasattr(activity, "consent_withdrawal"):
                issues.append("Consent withdrawal mechanism not documented")
                score -= 0.2

        elif activity.lawful_basis == LawfulBasis.LEGITIMATE_INTERESTS:
            if not hasattr(activity, "legitimate_interests_assessment"):
                issues.append("Legitimate interests assessment not documented")
                score -= 0.4

        # Check sensitive data processing
        if any(
            cat
            in [
                DataCategory.SENSITIVE_DATA,
                DataCategory.HEALTH_DATA,
                DataCategory.BIOMETRIC_DATA,
            ]
            for cat in activity.data_categories
        ) and activity.lawful_basis not in [
            LawfulBasis.CONSENT,
            LawfulBasis.LEGAL_OBLIGATION,
        ]:
            issues.append("Insufficient lawful basis for sensitive data processing")
            score -= 0.5

        # Check international transfers
        if activity.international_transfers:
            if not hasattr(activity, "adequacy_decision") and not hasattr(activity, "safeguards"):
                issues.append("International transfers lack adequate protection")
                score -= 0.3

        return max(0.0, score), issues

    async def _assess_data_subject_rights(self, activity: DataProcessingActivity) -> tuple[float, list[str]]:
        """Assess data subject rights compliance"""
        issues = []
        score = 1.0

        # Check rights implementation
        for right in self.data_subject_rights:
            if not hasattr(activity, f"{right}_procedure"):
                issues.append(f"Missing procedure for {right.replace('_', ' ')}")
                score -= 0.1

        # Special checks for automated decision-making
        if activity.automated_decision_making or activity.profiling:
            if not hasattr(activity, "automated_decision_safeguards"):
                issues.append("Missing safeguards for automated decision-making")
                score -= 0.2
            if not hasattr(activity, "human_intervention_option"):
                issues.append("Missing human intervention option")
                score -= 0.2

        return max(0.0, score), issues

    async def _assess_security_measures(self, activity: DataProcessingActivity) -> tuple[float, list[str]]:
        """Assess technical and organizational security measures"""
        issues = []
        score = 1.0

        for measure in self.security_measures:
            if not hasattr(activity, measure):
                issues.append(f"Missing security measure: {measure.replace('_', ' ')}")
                score -= 0.15

        # Additional checks for sensitive data
        if any(
            cat in [DataCategory.SENSITIVE_DATA, DataCategory.HEALTH_DATA] for cat in activity.data_categories
        ) and not hasattr(activity, "enhanced_security_measures"):
            issues.append("Enhanced security measures required for sensitive data")
            score -= 0.2

        return max(0.0, score), issues

    async def _assess_transparency(self, activity: DataProcessingActivity) -> tuple[float, list[str]]:
        """Assess transparency and information requirements"""
        issues = []
        score = 1.0

        required_information = [
            "controller_identity",
            "processing_purposes",
            "lawful_basis",
            "data_categories",
            "retention_period",
            "data_subject_rights",
        ]

        for info in required_information:
            if not hasattr(activity, info):
                issues.append(f"Missing transparency information: {info.replace('_', ' ')}")
                score -= 0.15

        # Check privacy policy accessibility
        if not hasattr(activity, "privacy_policy_accessible"):
            issues.append("Privacy policy not easily accessible")
            score -= 0.1

        return max(0.0, score), issues

    async def _generate_recommendations(self, violations: list[str], activity: DataProcessingActivity) -> list[str]:
        """Generate compliance recommendations"""
        recommendations = []

        if violations:
            recommendations.append("Address all identified violations immediately")

        # Lawful basis recommendations
        if activity.lawful_basis == LawfulBasis.CONSENT:
            recommendations.append("Implement granular consent management system")
            recommendations.append("Regular consent refresh mechanism")

        # Security recommendations
        if any("security" in violation.lower() for violation in violations):
            recommendations.extend(
                [
                    "Conduct privacy impact assessment",
                    "Implement data protection by design",
                    "Regular security audits and penetration testing",
                ]
            )

        # Data subject rights recommendations
        if any("right" in violation.lower() for violation in violations):
            recommendations.extend(
                [
                    "Implement automated data subject request handling",
                    "Staff training on data subject rights",
                    "Clear escalation procedures",
                ]
            )

        # General recommendations
        recommendations.extend(
            [
                "Regular GDPR compliance training",
                "Data protection officer consultation",
                "Continuous monitoring and improvement",
            ]
        )

        return recommendations

    def _determine_compliance_status(self, overall_score: float, violations: list[str]) -> str:
        """Determine overall compliance status"""
        if overall_score >= 0.9 and not violations:
            return "Fully Compliant"
        elif overall_score >= 0.7 and len(violations) <= 2:
            return "Mostly Compliant"
        elif overall_score >= 0.5:
            return "Partially Compliant"
        else:
            return "Non-Compliant"

    def _calculate_next_review_date(self, overall_score: float) -> datetime:
        """Calculate next compliance review date"""
        if overall_score >= 0.9:
            return datetime.now() + timedelta(days=180)  # 6 months
        elif overall_score >= 0.7:
            return datetime.now() + timedelta(days=90)  # 3 months
        else:
            return datetime.now() + timedelta(days=30)  # 1 month

    async def generate_dpia_assessment(self, activity: DataProcessingActivity) -> dict[str, Any]:
        """
        Generate Data Protection Impact Assessment (DPIA)

        Required for high-risk processing activities
        """
        dpia_required = (
            activity.automated_decision_making
            or activity.profiling
            or any(
                cat in [DataCategory.SENSITIVE_DATA, DataCategory.BIOMETRIC_DATA] for cat in activity.data_categories
            )
            or activity.international_transfers
        )

        if not dpia_required:
            return {"dpia_required": False, "reason": "Low risk processing"}

        risk_factors = await self._identify_risk_factors(activity)
        mitigation_measures = await self._suggest_mitigation_measures(risk_factors)

        return {
            "dpia_required": True,
            "risk_level": "High" if len(risk_factors) > 3 else "Medium",
            "risk_factors": risk_factors,
            "mitigation_measures": mitigation_measures,
            "residual_risks": await self._calculate_residual_risks(risk_factors, mitigation_measures),
            "dpo_consultation_required": len(risk_factors) > 2,
            "supervisory_authority_consultation": len(risk_factors) > 4,
        }

    async def _identify_risk_factors(self, activity: DataProcessingActivity) -> list[str]:
        """Identify data protection risk factors"""
        risk_factors = []

        if activity.automated_decision_making:
            risk_factors.append("Automated decision-making with legal effects")

        if activity.profiling:
            risk_factors.append("Systematic profiling of individuals")

        if any(cat in [DataCategory.SENSITIVE_DATA, DataCategory.HEALTH_DATA] for cat in activity.data_categories):
            risk_factors.append("Processing of special categories of data")

        if activity.international_transfers:
            risk_factors.append("International data transfers")

        if not hasattr(activity, "data_minimization"):
            risk_factors.append("Potential data minimization issues")

        return risk_factors

    async def _suggest_mitigation_measures(self, risk_factors: list[str]) -> list[str]:
        """Suggest risk mitigation measures"""
        measures = []

        if "Automated decision-making" in str(risk_factors):
            measures.extend(
                [
                    "Implement human oversight mechanisms",
                    "Provide explanation of automated decisions",
                    "Enable contest and review procedures",
                ]
            )

        if "special categories" in str(risk_factors):
            measures.extend(
                [
                    "Enhanced access controls",
                    "Additional encryption measures",
                    "Staff training on sensitive data handling",
                ]
            )

        if "International" in str(risk_factors):
            measures.extend(
                [
                    "Implement standard contractual clauses",
                    "Conduct transfer impact assessment",
                    "Monitor adequacy decisions",
                ]
            )

        measures.extend(
            [
                "Privacy by design implementation",
                "Regular compliance audits",
                "Data breach response procedures",
            ]
        )

        return measures

    async def _calculate_residual_risks(
        self, risk_factors: list[str], mitigation_measures: list[str]
    ) -> dict[str, str]:
        """Calculate residual risks after mitigation"""
        residual_risks = {}

        mitigation_coverage = len(mitigation_measures) / max(len(risk_factors), 1)

        if mitigation_coverage >= 1.5:
            residual_risks["overall"] = "Low"
        elif mitigation_coverage >= 1.0:
            residual_risks["overall"] = "Medium"
        else:
            residual_risks["overall"] = "High"

        residual_risks["monitoring_required"] = residual_risks["overall"] != "Low"
        residual_risks["additional_measures"] = residual_risks["overall"] == "High"

        return residual_risks


# Export the main validator class
__all__ = [
    "DataCategory",
    "DataProcessingActivity",
    "GDPRAssessment",
    "GDPRValidator",
    "LawfulBasis",
    "ProcessingPurpose",
]
