"""
Global Compliance Engine
=======================

Multi-jurisdiction AI regulatory compliance orchestration including:
- Cross-jurisdiction compliance mapping
- Automated compliance reporting
- Regulatory update monitoring
- Global compliance dashboard
- Harmonized compliance workflows
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

# Import other compliance modules
from ..eu_ai_act.compliance_validator import AISystemProfile, EUAIActValidator
from ..gdpr.data_protection_validator import DataProcessingActivity, GDPRValidator
from ..nist.ai_risk_management import AISystemMetrics, NISTAIRiskManager

logger = logging.getLogger(__name__)


class Jurisdiction(Enum):
    """Supported regulatory jurisdictions"""

    EU = "european_union"
    US = "united_states"
    UK = "united_kingdom"
    CANADA = "canada"
    SINGAPORE = "singapore"
    CHINA = "china"
    GLOBAL = "global"


class ComplianceFramework(Enum):
    """Compliance frameworks"""

    EU_AI_ACT = "eu_ai_act"
    GDPR = "gdpr"
    NIST_AI_RMF = "nist_ai_rmf"
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"
    CCPA = "ccpa"


@dataclass
class GlobalComplianceProfile:
    """Global compliance profile for AI system"""

    system_id: str
    name: str
    jurisdictions: list[Jurisdiction]
    frameworks: list[ComplianceFramework]
    deployment_regions: list[str]
    data_residency_requirements: dict[str, str]
    cross_border_transfers: bool
    regulatory_notifications: list[str]


@dataclass
class GlobalComplianceReport:
    """Comprehensive global compliance report"""

    system_id: str
    assessment_date: datetime
    overall_status: str
    jurisdiction_compliance: dict[Jurisdiction, dict[str, Any]]
    framework_compliance: dict[ComplianceFramework, dict[str, Any]]
    cross_jurisdiction_issues: list[str]
    harmonization_recommendations: list[str]
    next_assessment_date: datetime


class GlobalComplianceEngine:
    """
    Multi-jurisdiction AI compliance orchestration engine

    Provides unified compliance management across multiple regulatory
    jurisdictions and frameworks with automated assessment, reporting,
    and harmonization capabilities.
    """

    def __init__(self):
        # Initialize validators
        self.eu_ai_act_validator = EUAIActValidator()
        self.gdpr_validator = GDPRValidator()
        self.nist_risk_manager = NISTAIRiskManager()

        # Jurisdiction requirements mapping
        self.jurisdiction_requirements = {
            Jurisdiction.EU: [ComplianceFramework.EU_AI_ACT, ComplianceFramework.GDPR],
            Jurisdiction.US: [
                ComplianceFramework.NIST_AI_RMF,
                ComplianceFramework.SOC2,
            ],
            Jurisdiction.UK: [ComplianceFramework.GDPR],  # UK GDPR equivalent
            Jurisdiction.CANADA: [ComplianceFramework.NIST_AI_RMF],
            Jurisdiction.SINGAPORE: [ComplianceFramework.NIST_AI_RMF],
            Jurisdiction.CHINA: [],  # Would include China-specific frameworks
            Jurisdiction.GLOBAL: [ComplianceFramework.ISO_27001],
        }

        # Framework compatibility matrix
        self.framework_compatibility = {
            ComplianceFramework.EU_AI_ACT: {
                ComplianceFramework.NIST_AI_RMF: 0.8,  # High compatibility
                ComplianceFramework.GDPR: 0.9,  # Very high compatibility
                ComplianceFramework.ISO_27001: 0.7,  # Moderate compatibility
            },
            ComplianceFramework.GDPR: {
                ComplianceFramework.CCPA: 0.8,
                ComplianceFramework.SOC2: 0.6,
            },
            ComplianceFramework.NIST_AI_RMF: {ComplianceFramework.ISO_27001: 0.8},
        }

    async def assess_global_compliance(
        self,
        profile: GlobalComplianceProfile,
        system_profile: AISystemProfile = None,
        data_activity: DataProcessingActivity = None,
        metrics: AISystemMetrics = None,
    ) -> GlobalComplianceReport:
        """
        Comprehensive global compliance assessment

        Args:
            profile: Global compliance profile
            system_profile: AI system profile for AI Act assessment
            data_activity: Data processing activity for GDPR assessment
            metrics: AI system metrics for NIST assessment

        Returns:
            GlobalComplianceReport with comprehensive analysis
        """
        try:
            jurisdiction_compliance = {}
            framework_compliance = {}

            # Assess each jurisdiction
            for jurisdiction in profile.jurisdictions:
                jurisdiction_compliance[jurisdiction] = await self._assess_jurisdiction_compliance(
                    jurisdiction, profile, system_profile, data_activity, metrics
                )

            # Assess each framework
            for framework in profile.frameworks:
                framework_compliance[framework] = await self._assess_framework_compliance(
                    framework, profile, system_profile, data_activity, metrics
                )

            # Identify cross-jurisdiction issues
            cross_jurisdiction_issues = await self._identify_cross_jurisdiction_issues(jurisdiction_compliance, profile)

            # Generate harmonization recommendations
            harmonization_recommendations = await self._generate_harmonization_recommendations(
                framework_compliance, cross_jurisdiction_issues
            )

            # Calculate overall status
            overall_status = self._calculate_overall_status(jurisdiction_compliance, framework_compliance)

            return GlobalComplianceReport(
                system_id=profile.system_id,
                assessment_date=datetime.now(timezone.utc),
                overall_status=overall_status,
                jurisdiction_compliance=jurisdiction_compliance,
                framework_compliance=framework_compliance,
                cross_jurisdiction_issues=cross_jurisdiction_issues,
                harmonization_recommendations=harmonization_recommendations,
                next_assessment_date=self._calculate_next_assessment_date(overall_status),
            )

        except Exception as e:
            logger.error(f"Global compliance assessment failed for {profile.system_id}: {e}")
            raise

    async def _assess_jurisdiction_compliance(
        self,
        jurisdiction: Jurisdiction,
        profile: GlobalComplianceProfile,
        system_profile: AISystemProfile = None,
        data_activity: DataProcessingActivity = None,
        metrics: AISystemMetrics = None,
    ) -> dict[str, Any]:
        """Assess compliance for specific jurisdiction"""

        required_frameworks = self.jurisdiction_requirements.get(jurisdiction, [])
        compliance_results = {}

        for framework in required_frameworks:
            if framework in profile.frameworks:
                compliance_results[framework.value] = await self._assess_framework_compliance(
                    framework, profile, system_profile, data_activity, metrics
                )
            else:
                compliance_results[framework.value] = {
                    "status": "Not Applicable",
                    "reason": "Framework not specified in profile",
                }

        # Calculate jurisdiction compliance score
        framework_scores = [
            result.get("score", 0.0)
            for result in compliance_results.values()
            if isinstance(result, dict) and "score" in result
        ]

        jurisdiction_score = sum(framework_scores) / len(framework_scores) if framework_scores else 0.0

        return {
            "jurisdiction": jurisdiction.value,
            "compliance_score": jurisdiction_score,
            "frameworks": compliance_results,
            "status": self._determine_jurisdiction_status(jurisdiction_score),
            "specific_requirements": await self._get_jurisdiction_specific_requirements(jurisdiction),
        }

    async def _assess_framework_compliance(
        self,
        framework: ComplianceFramework,
        profile: GlobalComplianceProfile,
        system_profile: AISystemProfile = None,
        data_activity: DataProcessingActivity = None,
        metrics: AISystemMetrics = None,
    ) -> dict[str, Any]:
        """Assess compliance for specific framework"""

        try:
            if framework == ComplianceFramework.EU_AI_ACT and system_profile:
                assessment = await self.eu_ai_act_validator.assess_system_compliance(system_profile)
                return {
                    "framework": framework.value,
                    "status": assessment.compliance_status.value,
                    "score": assessment.confidence_score,
                    "violations": assessment.violations,
                    "requirements": assessment.requirements,
                    "assessment_details": assessment,
                }

            elif framework == ComplianceFramework.GDPR and data_activity:
                assessment = await self.gdpr_validator.assess_gdpr_compliance(data_activity)
                return {
                    "framework": framework.value,
                    "status": assessment.compliance_status,
                    "score": assessment.overall_score,
                    "violations": assessment.violations,
                    "requirements": ["GDPR compliance requirements"],
                    "assessment_details": assessment,
                }

            elif framework == ComplianceFramework.NIST_AI_RMF and metrics:
                from ..nist.ai_risk_management import AILifecycleStage

                assessment = await self.nist_risk_manager.conduct_risk_assessment(
                    profile.system_id, metrics, AILifecycleStage.OPERATE_MONITOR
                )
                return {
                    "framework": framework.value,
                    "status": f"Risk Level: {assessment.risk_level.value}",
                    "score": sum(assessment.trustworthy_scores.values()) / len(assessment.trustworthy_scores),
                    "violations": assessment.identified_risks,
                    "requirements": assessment.mitigation_strategies,
                    "assessment_details": assessment,
                }

            else:
                return await self._assess_other_framework(framework, profile)

        except Exception as e:
            logger.error(f"Framework assessment failed for {framework.value}: {e}")
            return {
                "framework": framework.value,
                "status": "Assessment Failed",
                "score": 0.0,
                "error": str(e),
            }

    async def _assess_other_framework(
        self, framework: ComplianceFramework, profile: GlobalComplianceProfile
    ) -> dict[str, Any]:
        """Assess other compliance frameworks"""

        # Placeholder assessments for frameworks not yet implemented
        framework_assessments = {
            ComplianceFramework.ISO_27001: {
                "status": "Requires Assessment",
                "score": 0.7,  # Placeholder
                "requirements": [
                    "Information security management system",
                    "Risk assessment",
                    "Security controls",
                ],
            },
            ComplianceFramework.SOC2: {
                "status": "Requires Assessment",
                "score": 0.8,  # Placeholder
                "requirements": [
                    "Security controls",
                    "Availability",
                    "Processing integrity",
                    "Confidentiality",
                ],
            },
            ComplianceFramework.CCPA: {
                "status": "Requires Assessment",
                "score": 0.7,  # Placeholder
                "requirements": [
                    "Consumer rights",
                    "Data disclosure",
                    "Opt-out mechanisms",
                ],
            },
        }

        assessment = framework_assessments.get(
            framework,
            {
                "status": "Not Implemented",
                "score": 0.0,
                "requirements": ["Framework assessment not yet implemented"],
            },
        )

        return {
            "framework": framework.value,
            **assessment,
            "violations": [],
            "note": "Placeholder assessment - requires implementation",
        }

    async def _identify_cross_jurisdiction_issues(
        self,
        jurisdiction_compliance: dict[Jurisdiction, dict[str, Any]],
        profile: GlobalComplianceProfile,
    ) -> list[str]:
        """Identify cross-jurisdiction compliance issues"""
        issues = []

        # Data residency conflicts
        if profile.cross_border_transfers:
            if Jurisdiction.EU in profile.jurisdictions:
                issues.append("Cross-border data transfers from eu_require adequacy decision or safeguards")

            if Jurisdiction.CHINA in profile.jurisdictions:
                issues.append("China data localization requirements may conflict with other jurisdictions")

        # Framework conflicts
        framework_scores = {}
        for compliance in jurisdiction_compliance.values():
            for framework_name, framework_result in compliance.get("frameworks", {}).items():
                if isinstance(framework_result, dict) and "score" in framework_result:
                    if framework_name not in framework_scores:
                        framework_scores[framework_name] = []
                    framework_scores[framework_name].append(framework_result["score"])

        # Identify significant score variations
        for framework, scores in framework_scores.items():
            if len(scores) > 1:
                score_variance = max(scores) - min(scores)
                if score_variance > 0.3:
                    issues.append(f"Significant compliance variation in {framework} across jurisdictions")

        # Regulatory notification conflicts
        if len(profile.regulatory_notifications) > 1:
            issues.append("Multiple regulatory notifications may have conflicting requirements")

        return issues

    async def _generate_harmonization_recommendations(
        self,
        framework_compliance: dict[ComplianceFramework, dict[str, Any]],
        cross_jurisdiction_issues: list[str],
    ) -> list[str]:
        """Generate recommendations for compliance harmonization"""
        recommendations = []

        if cross_jurisdiction_issues:
            recommendations.append("Address cross-jurisdiction issues as priority")

        # Framework alignment recommendations
        framework_scores = {
            framework: result.get("score", 0.0)
            for framework, result in framework_compliance.items()
            if isinstance(result, dict)
        }

        lowest_scoring_framework = min(framework_scores.items(), key=lambda x: x[1])
        if lowest_scoring_framework[1] < 0.7:
            recommendations.append(f"Priority improvement needed for {lowest_scoring_framework[0].value}")

        # Compatibility-based recommendations
        recommendations.extend(
            [
                "Leverage framework compatibility for efficient compliance",
                "Implement unified compliance monitoring system",
                "Establish cross-framework governance structure",
                "Regular harmonization reviews and updates",
            ]
        )

        # Data governance recommendations
        recommendations.extend(
            [
                "Implement unified data governance framework",
                "Establish clear data residency policies",
                "Create cross-border transfer safeguards",
            ]
        )

        return recommendations

    def _calculate_overall_status(
        self,
        jurisdiction_compliance: dict[Jurisdiction, dict[str, Any]],
        framework_compliance: dict[ComplianceFramework, dict[str, Any]],
    ) -> str:
        """Calculate overall compliance status"""

        # Collect all compliance scores
        all_scores = []

        for compliance in jurisdiction_compliance.values():
            if "compliance_score" in compliance:
                all_scores.append(compliance["compliance_score"])

        for compliance in framework_compliance.values():
            if isinstance(compliance, dict) and "score" in compliance:
                all_scores.append(compliance["score"])

        if not all_scores:
            return "Assessment Incomplete"

        avg_score = sum(all_scores) / len(all_scores)

        if avg_score >= 0.9:
            return "Fully Compliant"
        elif avg_score >= 0.8:
            return "Mostly Compliant"
        elif avg_score >= 0.6:
            return "Partially Compliant"
        else:
            return "Non-Compliant"

    def _determine_jurisdiction_status(self, score: float) -> str:
        """Determine jurisdiction compliance status"""
        if score >= 0.9:
            return "Compliant"
        elif score >= 0.7:
            return "Mostly Compliant"
        elif score >= 0.5:
            return "Partially Compliant"
        else:
            return "Non-Compliant"

    async def _get_jurisdiction_specific_requirements(self, jurisdiction: Jurisdiction) -> list[str]:
        """Get jurisdiction-specific requirements"""

        requirements_map = {
            Jurisdiction.EU: [
                "GDPR compliance for personal data",
                "EU AI Act compliance for AI systems",
                "Data residency within EU/EEA",
                "Regulatory notifications to competent authorities",
            ],
            Jurisdiction.US: [
                "NIST AI RMF compliance",
                "SOC 2 compliance for service organizations",
                "State-specific privacy laws (CCPA, etc.)",
                "Sector-specific regulations (HIPAA, etc.)",
            ],
            Jurisdiction.UK: [
                "UK GDPR compliance",
                "ICO guidance on AI and data protection",
                "Algorithmic accountability standards",
            ],
            Jurisdiction.CANADA: [
                "PIPEDA compliance",
                "Provincial privacy legislation",
                "AI governance frameworks",
            ],
            Jurisdiction.SINGAPORE: [
                "PDPA compliance",
                "AI governance self-assessment",
                "Cybersecurity framework",
            ],
            Jurisdiction.CHINA: [
                "Data localization requirements",
                "Cybersecurity Law compliance",
                "AI algorithm registration",
            ],
        }

        return requirements_map.get(jurisdiction, ["Jurisdiction-specific requirements to be defined"])

    def _calculate_next_assessment_date(self, overall_status: str) -> datetime:
        """Calculate next global assessment date"""
        if overall_status == "Non-Compliant":
            return datetime.now(timezone.utc) + timedelta(days=30)  # Monthly
        elif overall_status == "Partially Compliant":
            return datetime.now(timezone.utc) + timedelta(days=90)  # Quarterly
        else:
            return datetime.now(timezone.utc) + timedelta(days=180)  # Semi-annually

    async def generate_compliance_dashboard(self, report: GlobalComplianceReport) -> dict[str, Any]:
        """Generate compliance dashboard data"""

        dashboard = {
            "summary": {
                "system_id": report.system_id,
                "overall_status": report.overall_status,
                "assessment_date": report.assessment_date.isoformat(),
                "next_assessment": report.next_assessment_date.isoformat(),
            },
            "jurisdiction_overview": {
                jurisdiction.value: {
                    "status": compliance.get("status", "Unknown"),
                    "score": compliance.get("compliance_score", 0.0),
                }
                for jurisdiction, compliance in report.jurisdiction_compliance.items()
            },
            "framework_overview": {
                framework.value: {
                    "status": compliance.get("status", "Unknown"),
                    "score": compliance.get("score", 0.0),
                }
                for framework, compliance in report.framework_compliance.items()
            },
            "issues_summary": {
                "cross_jurisdiction_issues": len(report.cross_jurisdiction_issues),
                "total_violations": sum(
                    len(compliance.get("violations", []))
                    for compliance in report.framework_compliance.values()
                    if isinstance(compliance, dict)
                ),
                "recommendations": len(report.harmonization_recommendations),
            },
            "action_items": await self._generate_action_items(report),
        }

        return dashboard

    async def _generate_action_items(self, report: GlobalComplianceReport) -> list[dict[str, Any]]:
        """Generate prioritized action items"""
        action_items = []

        # High priority: Cross-jurisdiction issues
        for issue in report.cross_jurisdiction_issues:
            action_items.append(
                {
                    "priority": "High",
                    "category": "Cross-Jurisdiction",
                    "description": issue,
                    "deadline": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                }
            )

        # Medium priority: Framework compliance issues
        for framework, compliance in report.framework_compliance.items():
            if isinstance(compliance, dict) and compliance.get("score", 1.0) < 0.7:
                action_items.append(
                    {
                        "priority": "Medium",
                        "category": "Framework Compliance",
                        "description": f"Improve {framework.value} compliance",
                        "deadline": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat(),
                    }
                )

        # Low priority: Harmonization recommendations
        for recommendation in report.harmonization_recommendations:
            action_items.append(
                {
                    "priority": "Low",
                    "category": "Harmonization",
                    "description": recommendation,
                    "deadline": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
                }
            )

        return action_items


# Export the main global compliance engine
__all__ = [
    "ComplianceFramework",
    "GlobalComplianceEngine",
    "GlobalComplianceProfile",
    "GlobalComplianceReport",
    "Jurisdiction",
]
