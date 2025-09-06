"""
EU AI Act Compliance Validator
=============================

Comprehensive validation framework for EU AI Act compliance including:
- Risk assessment and categorization
- Transparency requirements validation
- Conformity assessment automation
- Documentation compliance checking
- High-risk AI system validation
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__, timezone)


class AISystemRiskCategory(Enum):
    """EU AI Act risk categories"""

    MINIMAL_RISK = "minimal"
    LIMITED_RISK = "limited"
    HIGH_RISK = "high"
    UNACCEPTABLE_RISK = "unacceptable"


class ComplianceStatus(Enum):
    """Compliance status levels"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"
    PENDING_ASSESSMENT = "pending"


@dataclass
class AISystemProfile:
    """AI System profile for compliance assessment"""

    system_id: str
    name: str
    description: str
    intended_use: str
    deployment_context: list[str]
    data_types: list[str]
    algorithms_used: list[str]
    human_oversight_level: str
    automated_decision_making: bool
    affects_fundamental_rights: bool


@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""

    system_id: str
    risk_category: AISystemRiskCategory
    compliance_status: ComplianceStatus
    assessment_date: datetime
    requirements: list[str]
    violations: list[str]
    recommendations: list[str]
    next_review_date: datetime
    confidence_score: float


class EUAIActValidator:
    """
    EU AI Act compliance validation engine

    Provides comprehensive validation against EU AI Act requirements including:
    - Automated risk categorization
    - Compliance requirement mapping
    - Documentation validation
    - Conformity assessment
    """

    def __init__(self):
        self.high_risk_use_cases = {
            "biometric_identification",
            "critical_infrastructure",
            "education_vocational_training",
            "employment_workers_management",
            "essential_private_services",
            "law_enforcement",
            "migration_asylum_border_control",
            "administration_of_justice",
            "democratic_processes",
        }

        self.prohibited_practices = {
            "subliminal_techniques",
            "vulnerability_exploitation",
            "social_scoring_public_authorities",
            "real_time_biometric_identification",
        }

        self.transparency_requirements = {
            "ai_system_notification",
            "human_oversight_information",
            "accuracy_limitations",
            "risk_information",
            "instruction_documentation",
        }

    async def assess_system_compliance(self, system_profile: AISystemProfile) -> ComplianceAssessment:
        """
        Comprehensive compliance assessment for an AI system

        Args:
            system_profile: AI system profile to assess

        Returns:
            ComplianceAssessment with detailed results
        """
        try:
            # Risk categorization
            risk_category = await self._categorize_risk(system_profile)

            # Compliance validation
            violations = await self._validate_compliance(system_profile, risk_category)

            # Generate requirements
            requirements = await self._generate_requirements(risk_category)

            # Generate recommendations
            recommendations = await self._generate_recommendations(violations, risk_category)

            # Calculate compliance status
            compliance_status = self._calculate_compliance_status(violations)

            # Calculate confidence score
            confidence_score = await self._calculate_confidence(system_profile, violations)

            return ComplianceAssessment(
                system_id=system_profile.system_id,
                risk_category=risk_category,
                compliance_status=compliance_status,
                assessment_date=datetime.now(timezone.utc),
                requirements=requirements,
                violations=violations,
                recommendations=recommendations,
                next_review_date=self._calculate_next_review_date(risk_category),
                confidence_score=confidence_score,
            )

        except Exception as e:
            logger.error(f"Compliance assessment failed for {system_profile.system_id}: {e}")
            raise

    async def _categorize_risk(self, system_profile: AISystemProfile) -> AISystemRiskCategory:
        """Categorize AI system risk level according to EU AI Act"""

        # Check for prohibited practices
        for context in system_profile.deployment_context:
            if any(prohibited in context.lower() for prohibited in self.prohibited_practices):
                return AISystemRiskCategory.UNACCEPTABLE_RISK

        # Check for high-risk use cases
        for context in system_profile.deployment_context:
            if any(high_risk in context.lower() for high_risk in self.high_risk_use_cases):
                return AISystemRiskCategory.HIGH_RISK

        # Check for limited risk indicators
        if (
            system_profile.automated_decision_making
            or "emotion_recognition" in system_profile.algorithms_used
            or "biometric_categorization" in system_profile.algorithms_used
        ):
            return AISystemRiskCategory.LIMITED_RISK

        return AISystemRiskCategory.MINIMAL_RISK

    async def _validate_compliance(
        self, system_profile: AISystemProfile, risk_category: AISystemRiskCategory
    ) -> list[str]:
        """Validate compliance requirements"""
        violations = []

        if risk_category == AISystemRiskCategory.UNACCEPTABLE_RISK:
            violations.append("System involves prohibited AI practices")
            return violations

        if risk_category == AISystemRiskCategory.HIGH_RISK:
            violations.extend(await self._validate_high_risk_requirements(system_profile))

        if risk_category in [
            AISystemRiskCategory.HIGH_RISK,
            AISystemRiskCategory.LIMITED_RISK,
        ]:
            violations.extend(await self._validate_transparency_requirements(system_profile))

        return violations

    async def _validate_high_risk_requirements(self, system_profile: AISystemProfile) -> list[str]:
        """Validate high-risk AI system requirements"""
        violations = []

        # Risk management system
        if not hasattr(system_profile, "risk_management_system"):
            violations.append("Missing risk management system documentation")

        # Data governance
        if not system_profile.data_types:
            violations.append("Missing data governance documentation")

        # Human oversight
        if system_profile.human_oversight_level.lower() not in [
            "meaningful",
            "effective",
        ]:
            violations.append("Insufficient human oversight provisions")

        # Accuracy requirements
        if not hasattr(system_profile, "accuracy_metrics"):
            violations.append("Missing accuracy and performance metrics")

        # Robustness requirements
        if not hasattr(system_profile, "robustness_testing"):
            violations.append("Missing robustness and security testing")

        return violations

    async def _validate_transparency_requirements(self, system_profile: AISystemProfile) -> list[str]:
        """Validate transparency requirements"""
        violations = []

        for requirement in self.transparency_requirements:
            if not hasattr(system_profile, requirement):
                violations.append(f"Missing transparency requirement: {requirement}")

        return violations

    async def _generate_requirements(self, risk_category: AISystemRiskCategory) -> list[str]:
        """Generate applicable compliance requirements"""
        requirements = []

        if risk_category == AISystemRiskCategory.UNACCEPTABLE_RISK:
            requirements.append("System must be discontinued immediately")
            return requirements

        if risk_category == AISystemRiskCategory.HIGH_RISK:
            requirements.extend(
                [
                    "Implement comprehensive risk management system",
                    "Establish data governance and quality measures",
                    "Maintain detailed documentation and records",
                    "Ensure meaningful human oversight",
                    "Implement accuracy and robustness measures",
                    "Conduct conformity assessment",
                    "CE marking and registration required",
                ]
            )

        if risk_category in [
            AISystemRiskCategory.HIGH_RISK,
            AISystemRiskCategory.LIMITED_RISK,
        ]:
            requirements.extend(
                [
                    "Provide clear information to users",
                    "Implement transparency measures",
                    "Enable human oversight capabilities",
                ]
            )

        requirements.append("Monitor ongoing compliance")
        return requirements

    async def _generate_recommendations(self, violations: list[str], risk_category: AISystemRiskCategory) -> list[str]:
        """Generate compliance recommendations"""
        recommendations = []

        if violations:
            recommendations.append("Address all identified violations immediately")
            recommendations.append("Conduct comprehensive compliance review")

        if risk_category == AISystemRiskCategory.HIGH_RISK:
            recommendations.extend(
                [
                    "Engage qualified conformity assessment body",
                    "Implement continuous monitoring systems",
                    "Establish incident response procedures",
                    "Regular compliance audits recommended",
                ]
            )

        recommendations.append("Stay updated on regulatory developments")
        return recommendations

    def _calculate_compliance_status(self, violations: list[str]) -> ComplianceStatus:
        """Calculate overall compliance status"""
        if not violations:
            return ComplianceStatus.COMPLIANT
        elif len(violations) <= 2:
            return ComplianceStatus.REQUIRES_REVIEW
        else:
            return ComplianceStatus.NON_COMPLIANT

    async def _calculate_confidence(self, system_profile: AISystemProfile, violations: list[str]) -> float:
        """Calculate confidence score for assessment"""
        base_confidence = 0.8

        # Reduce confidence based on missing information
        missing_info_penalty = len(violations) * 0.1

        # Increase confidence for detailed profiles
        if hasattr(system_profile, "detailed_documentation"):
            base_confidence += 0.1

        return max(0.0, min(1.0, base_confidence - missing_info_penalty))

    def _calculate_next_review_date(self, risk_category: AISystemRiskCategory) -> datetime:
        """Calculate next compliance review date"""
        from datetime import timedelta

        if risk_category == AISystemRiskCategory.HIGH_RISK:
            return datetime.now(timezone.utc) + timedelta(days=90)  # Quarterly
        elif risk_category == AISystemRiskCategory.LIMITED_RISK:
            return datetime.now(timezone.utc) + timedelta(days=180)  # Semi-annually
        else:
            return datetime.now(timezone.utc) + timedelta(days=365)  # Annually

    async def generate_compliance_report(self, assessment: ComplianceAssessment) -> dict[str, Any]:
        """Generate comprehensive compliance report"""

        report = {
            "assessment_summary": {
                "system_id": assessment.system_id,
                "risk_category": assessment.risk_category.value,
                "compliance_status": assessment.compliance_status.value,
                "assessment_date": assessment.assessment_date.isoformat(),
                "confidence_score": assessment.confidence_score,
            },
            "requirements": assessment.requirements,
            "violations": assessment.violations,
            "recommendations": assessment.recommendations,
            "next_steps": await self._generate_next_steps(assessment),
            "regulatory_references": await self._get_regulatory_references(assessment.risk_category),
        }

        return report

    async def _generate_next_steps(self, assessment: ComplianceAssessment) -> list[str]:
        """Generate actionable next steps"""
        next_steps = []

        if assessment.compliance_status == ComplianceStatus.NON_COMPLIANT:
            next_steps.extend(
                [
                    "Immediately address critical violations",
                    "Conduct comprehensive system review",
                    "Implement required compliance measures",
                    "Schedule re-assessment within 30 days",
                ]
            )
        elif assessment.compliance_status == ComplianceStatus.REQUIRES_REVIEW:
            next_steps.extend(
                [
                    "Address identified issues",
                    "Update documentation",
                    "Schedule follow-up assessment",
                ]
            )
        else:
            next_steps.extend(
                [
                    "Maintain current compliance measures",
                    "Monitor for regulatory updates",
                    f"Schedule next review: {assessment.next_review_date.strftime('%Y-%m-%d')}",
                ]
            )

        return next_steps

    async def _get_regulatory_references(self, risk_category: AISystemRiskCategory) -> list[str]:
        """Get relevant regulatory references"""
        references = [
            "EU AI Act (Regulation (EU) 2024/1689)",
            "GDPR (Regulation (EU) 2016/679)",
        ]

        if risk_category == AISystemRiskCategory.HIGH_RISK:
            references.extend(
                [
                    "Annex III - High-risk AI systems",
                    "Article 9 - Risk management system",
                    "Article 10 - Data and data governance",
                    "Article 14 - Human oversight",
                    "Article 15 - Accuracy, robustness and cybersecurity",
                ]
            )

        return references


# Export the main validator class
__all__ = [
    "AISystemProfile",
    "AISystemRiskCategory",
    "ComplianceAssessment",
    "ComplianceStatus",
    "EUAIActValidator",
]
