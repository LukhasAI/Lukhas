"""
LUKHAS AI Global Compliance Manager
==================================

Multi-jurisdictional AI compliance orchestration system that harmonizes regulatory
requirements across EU, US, UK, Canada, and other major jurisdictions. Provides
unified compliance assessment, cross-border data governance, and real-time
regulatory change adaptation.

Features:
- Automatic jurisdiction detection based on data subjects and operations
- Cross-border data transfer compliance (GDPR, CBPR, etc.)
- Regulatory requirement harmonization and conflict resolution
- Real-time compliance scoring across multiple frameworks
- Automated compliance gap analysis and remediation
- International regulatory change monitoring and adaptation
- Multi-stakeholder governance and democratic oversight interfaces
- Unified audit trails for global compliance reporting

Integration:
- Trinity Framework (⚛️🧠🛡️) global compliance alignment
- Constitutional AI international human rights enforcement
- Guardian System 2.0 multi-jurisdictional violation detection
- Secure logging for international regulatory audit trails
"""
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import streamlit as st

# Import compliance engines
from .eu_ai_act_classifier import EUAIActClassifier
from .nist_ai_rmf import NISTAIRiskFramework
from .privacy_compliance_engine import PrivacyComplianceEngine


# Global compliance types
class Jurisdiction(Enum):
    """Supported regulatory jurisdictions"""

    EUROPEAN_UNION = "eu"
    UNITED_STATES = "us"
    UNITED_KINGDOM = "uk"
    CANADA = "ca"
    AUSTRALIA = "au"
    SINGAPORE = "sg"
    JAPAN = "jp"
    SOUTH_KOREA = "kr"
    SWITZERLAND = "ch"
    NEW_ZEALAND = "nz"
    CALIFORNIA = "us_ca"  # Special California jurisdiction
    GLOBAL = "global"


class ComplianceFramework(Enum):
    """Global compliance frameworks"""

    EU_AI_ACT_2024 = "eu_ai_act_2024"
    GDPR_2018 = "gdpr_2018"
    CCPA_2020 = "ccpa_2020"
    CCPA_ADMT_2025 = "ccpa_admt_2025"
    NIST_AI_RMF_2023 = "nist_ai_rmf_2023"
    UK_AI_REGULATION = "uk_ai_regulation"
    CANADA_AIDA = "canada_aida"  # Artificial Intelligence and Data Act
    AUSTRALIA_AI_ETHICS = "australia_ai_ethics"
    SINGAPORE_VERVAI = "singapore_vervai"  # Verifiable AI
    ISO_23053_2022 = "iso_23053_2022"  # AI governance
    ISO_23894_2023 = "iso_23894_2023"  # AI risk management


class ComplianceStatus(Enum):
    """Compliance status levels"""

    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    EXEMPT = "exempt"


class DataTransferMechanism(Enum):
    """Cross-border data transfer mechanisms"""

    ADEQUACY_DECISION = "adequacy_decision"
    STANDARD_CONTRACTUAL_CLAUSES = "standard_contractual_clauses"
    BINDING_CORPORATE_RULES = "binding_corporate_rules"
    CERTIFICATION = "certification"
    CODE_OF_CONDUCT = "code_of_conduct"
    DEROGATION = "derogation"


@dataclass
class JurisdictionProfile:
    """Jurisdiction-specific compliance profile"""

    jurisdiction: Jurisdiction
    applicable_frameworks: list[ComplianceFramework]
    data_localization_required: bool
    cross_border_restrictions: list[str]
    enforcement_authority: str
    penalty_structure: dict[str, str]
    adequacy_status: Optional[str] = None
    special_requirements: list[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class GlobalComplianceAssessment:
    """Comprehensive global compliance assessment"""

    assessment_id: str
    system_name: str
    assessment_timestamp: datetime

    # Jurisdiction analysis
    applicable_jurisdictions: list[Jurisdiction]
    primary_jurisdiction: Jurisdiction
    data_subject_locations: dict[Jurisdiction, int]  # Count by jurisdiction

    # Framework compliance status
    framework_compliance: dict[ComplianceFramework, ComplianceStatus]
    compliance_scores: dict[ComplianceFramework, float]  # 0.0-1.0

    # Cross-border compliance
    cross_border_transfers: list[dict[str, Any]]
    transfer_mechanisms: dict[str, DataTransferMechanism]
    data_sovereignty_compliance: bool

    # Overall assessment
    overall_compliance_score: float
    global_compliance_status: ComplianceStatus

    # Gaps and recommendations
    compliance_gaps: list[dict[str, Any]]
    harmonization_conflicts: list[dict[str, Any]]
    priority_actions: list[str]
    estimated_remediation_time: int  # days

    # Reporting
    next_review_date: datetime
    regulatory_notifications_required: list[str]


@dataclass
class RegulatoryChange:
    """Regulatory change tracking"""

    change_id: str
    jurisdiction: Jurisdiction
    framework: ComplianceFramework
    change_type: str  # new_law, amendment, interpretation, guidance
    effective_date: datetime
    impact_assessment: str  # low, medium, high, critical
    affected_systems: list[str]
    required_actions: list[str]
    compliance_deadline: Optional[datetime] = None


class GlobalComplianceManager:
    """
    Global Multi-Jurisdictional AI Compliance Manager

    Orchestrates compliance across multiple jurisdictions with unified
    assessment, harmonized requirements, and automated adaptation to
    regulatory changes.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize global compliance manager"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize compliance engines
        self.eu_classifier = EUAIActClassifier()
        self.privacy_engine = PrivacyComplianceEngine()
        self.nist_framework = NISTAIRiskFramework()

        # Global compliance storage
        self.global_assessments: dict[str, GlobalComplianceAssessment] = {}
        self.jurisdiction_profiles: dict[Jurisdiction, JurisdictionProfile] = {}
        self.regulatory_changes: dict[str, RegulatoryChange] = {}

        # Initialize jurisdiction profiles
        self._initialize_jurisdiction_profiles()

        # Compliance thresholds and weights
        self.compliance_thresholds = {
            ComplianceStatus.COMPLIANT: 0.85,
            ComplianceStatus.PARTIALLY_COMPLIANT: 0.65,
            ComplianceStatus.NON_COMPLIANT: 0.0,
        }

        # Framework weights for global scoring
        self.framework_weights = {
            ComplianceFramework.EU_AI_ACT_2024: 0.25,
            ComplianceFramework.GDPR_2018: 0.20,
            ComplianceFramework.NIST_AI_RMF_2023: 0.20,
            ComplianceFramework.CCPA_ADMT_2025: 0.15,
            ComplianceFramework.UK_AI_REGULATION: 0.10,
            ComplianceFramework.CANADA_AIDA: 0.10,
        }

        self.logger.info("Global Compliance Manager initialized")

    def _initialize_jurisdiction_profiles(self):
        """Initialize jurisdiction-specific compliance profiles"""

        # European Union
        self.jurisdiction_profiles[Jurisdiction.EUROPEAN_UNION] = JurisdictionProfile(
            jurisdiction=Jurisdiction.EUROPEAN_UNION,
            applicable_frameworks=[
                ComplianceFramework.EU_AI_ACT_2024,
                ComplianceFramework.GDPR_2018,
                ComplianceFramework.ISO_23053_2022,
            ],
            data_localization_required=False,
            cross_border_restrictions=["adequate_protection_required"],
            enforcement_authority="European Commission + Member State Authorities",
            penalty_structure={
                "ai_act_violations": "Up to €35M or 7% global revenue",
                "gdpr_violations": "Up to €20M or 4% global revenue",
            },
            adequacy_status="internal_market",
            special_requirements=[
                "high_risk_ai_conformity_assessment",
                "gpai_model_registration",
                "fundamental_rights_impact_assessment",
            ],
        )

        # United States (Federal)
        self.jurisdiction_profiles[Jurisdiction.UNITED_STATES] = JurisdictionProfile(
            jurisdiction=Jurisdiction.UNITED_STATES,
            applicable_frameworks=[ComplianceFramework.NIST_AI_RMF_2023, ComplianceFramework.ISO_23053_2022],
            data_localization_required=False,
            cross_border_restrictions=["national_security_review"],
            enforcement_authority="Federal Trade Commission + Sector Regulators",
            penalty_structure={
                "ftc_violations": "Up to $46,517 per violation",
                "sector_specific": "Varies by regulator",
            },
            special_requirements=[
                "federal_ai_impact_assessment",
                "algorithmic_accountability_reporting",
                "bias_evaluation_documentation",
            ],
        )

        # California (Special US Jurisdiction)
        self.jurisdiction_profiles[Jurisdiction.CALIFORNIA] = JurisdictionProfile(
            jurisdiction=Jurisdiction.CALIFORNIA,
            applicable_frameworks=[
                ComplianceFramework.CCPA_2020,
                ComplianceFramework.CCPA_ADMT_2025,
                ComplianceFramework.NIST_AI_RMF_2023,
            ],
            data_localization_required=False,
            cross_border_restrictions=["consumer_privacy_protection"],
            enforcement_authority="California Privacy Protection Agency",
            penalty_structure={
                "ccpa_violations": "Up to $7,500 per intentional violation",
                "admt_violations": "Up to $2,500 per consumer affected",
            },
            special_requirements=[
                "automated_decision_transparency",
                "consumer_opt_out_mechanisms",
                "privacy_impact_assessments",
            ],
        )

        # United Kingdom
        self.jurisdiction_profiles[Jurisdiction.UNITED_KINGDOM] = JurisdictionProfile(
            jurisdiction=Jurisdiction.UNITED_KINGDOM,
            applicable_frameworks=[
                ComplianceFramework.UK_AI_REGULATION,
                ComplianceFramework.GDPR_2018,  # UK GDPR
                ComplianceFramework.ISO_23053_2022,
            ],
            data_localization_required=False,
            cross_border_restrictions=["data_protection_adequacy"],
            enforcement_authority="Information Commissioner's Office + Sector Regulators",
            penalty_structure={
                "gdpr_violations": "Up to £17.5M or 4% global revenue",
                "sector_violations": "Varies by sector",
            },
            adequacy_status="eu_adequate",
            special_requirements=[
                "algorithmic_impact_assessment",
                "public_sector_transparency",
                "sector_specific_guidance_compliance",
            ],
        )

        # Canada
        self.jurisdiction_profiles[Jurisdiction.CANADA] = JurisdictionProfile(
            jurisdiction=Jurisdiction.CANADA,
            applicable_frameworks=[ComplianceFramework.CANADA_AIDA, ComplianceFramework.ISO_23053_2022],
            data_localization_required=False,
            cross_border_restrictions=["privacy_impact_assessment"],
            enforcement_authority="Office of the Privacy Commissioner + Innovation, Science and Economic Development Canada",
            penalty_structure={
                "aida_violations": "Up to $25M or 3% global revenue (proposed)",
                "privacy_violations": "Up to $10M per violation",
            },
            adequacy_status="eu_adequate",
            special_requirements=[
                "high_impact_system_registration",
                "algorithmic_impact_assessment",
                "responsible_ai_governance",
            ],
        )

    async def comprehensive_compliance_check(
        self, ai_system_data: dict[str, Any], jurisdiction_hint: str = "auto"
    ) -> GlobalComplianceAssessment:
        """
        Comprehensive multi-jurisdictional compliance assessment

        Args:
            ai_system_data: AI system configuration and metadata
            jurisdiction_hint: Jurisdiction hint ("auto", "eu", "us", etc.)

        Returns:
            Complete global compliance assessment
        """

        try:
            assessment_id = self._generate_assessment_id(ai_system_data)
            system_name = ai_system_data.get("name", "unknown_system")

            # Determine applicable jurisdictions
            applicable_jurisdictions = await self._determine_applicable_jurisdictions(ai_system_data, jurisdiction_hint)
            primary_jurisdiction = self._determine_primary_jurisdiction(applicable_jurisdictions, ai_system_data)

            # Analyze data subject locations
            data_subject_locations = self._analyze_data_subject_locations(ai_system_data)

            # Assess compliance for each framework
            framework_compliance = {}
            compliance_scores = {}

            for jurisdiction in applicable_jurisdictions:
                profile = self.jurisdiction_profiles[jurisdiction]

                for framework in profile.applicable_frameworks:
                    if framework not in framework_compliance:
                        status, score = await self._assess_framework_compliance(framework, ai_system_data, jurisdiction)
                        framework_compliance[framework] = status
                        compliance_scores[framework] = score

            # Assess cross-border data transfers
            cross_border_transfers = await self._assess_cross_border_transfers(ai_system_data, applicable_jurisdictions)
            transfer_mechanisms = self._determine_transfer_mechanisms(cross_border_transfers)
            data_sovereignty_compliance = await self._check_data_sovereignty(ai_system_data, applicable_jurisdictions)

            # Calculate overall compliance
            overall_score = self._calculate_overall_compliance_score(compliance_scores, applicable_jurisdictions)
            global_status = self._determine_global_compliance_status(overall_score)

            # Identify gaps and conflicts
            compliance_gaps = await self._identify_compliance_gaps(framework_compliance, compliance_scores)
            harmonization_conflicts = await self._identify_harmonization_conflicts(
                applicable_jurisdictions, ai_system_data
            )

            # Generate priority actions
            priority_actions = self._generate_priority_actions(compliance_gaps, harmonization_conflicts, global_status)

            # Estimate remediation time
            remediation_time = self._estimate_remediation_time(compliance_gaps, global_status)

            # Determine regulatory notifications
            notifications_required = self._determine_regulatory_notifications(
                applicable_jurisdictions, ai_system_data, framework_compliance
            )

            # Create global assessment
            assessment = GlobalComplianceAssessment(
                assessment_id=assessment_id,
                system_name=system_name,
                assessment_timestamp=datetime.now(timezone.utc),
                applicable_jurisdictions=applicable_jurisdictions,
                primary_jurisdiction=primary_jurisdiction,
                data_subject_locations=data_subject_locations,
                framework_compliance=framework_compliance,
                compliance_scores=compliance_scores,
                cross_border_transfers=cross_border_transfers,
                transfer_mechanisms=transfer_mechanisms,
                data_sovereignty_compliance=data_sovereignty_compliance,
                overall_compliance_score=overall_score,
                global_compliance_status=global_status,
                compliance_gaps=compliance_gaps,
                harmonization_conflicts=harmonization_conflicts,
                priority_actions=priority_actions,
                estimated_remediation_time=remediation_time,
                next_review_date=self._calculate_next_review(global_status),
                regulatory_notifications_required=notifications_required,
            )

            # Store assessment
            self.global_assessments[assessment_id] = assessment

            self.logger.info(
                f"Global compliance assessment completed: {assessment_id}, "
                f"Overall status: {global_status.value}, "
                f"Jurisdictions: {len(applicable_jurisdictions)}"
            )

            return assessment

        except Exception as e:
            self.logger.error(f"Global compliance assessment failed: {e!s}")
            raise

    async def _determine_applicable_jurisdictions(
        self, ai_system_data: dict[str, Any], jurisdiction_hint: str
    ) -> list[Jurisdiction]:
        """Determine applicable jurisdictions for compliance assessment"""

        jurisdictions = set()

        # Explicit jurisdiction hint
        if jurisdiction_hint != "auto":
            try:
                jurisdictions.add(Jurisdiction(jurisdiction_hint))
            except ValueError:
                self.logger.warning(f"Invalid jurisdiction hint: {jurisdiction_hint}")

        # Data subject location analysis
        data_subjects = ai_system_data.get("data_subjects", [])
        for subject in data_subjects:
            location = subject.get("location", "")
            if location:
                jurisdiction = self._location_to_jurisdiction(location)
                if jurisdiction:
                    jurisdictions.add(jurisdiction)

        # System deployment locations
        deployment_locations = ai_system_data.get("deployment_locations", [])
        for location in deployment_locations:
            jurisdiction = self._location_to_jurisdiction(location)
            if jurisdiction:
                jurisdictions.add(jurisdiction)

        # Business operation locations
        business_locations = ai_system_data.get("business_locations", [])
        for location in business_locations:
            jurisdiction = self._location_to_jurisdiction(location)
            if jurisdiction:
                jurisdictions.add(jurisdiction)

        # Default to major jurisdictions if none identified
        if not jurisdictions:
            jurisdictions = {Jurisdiction.EUROPEAN_UNION, Jurisdiction.UNITED_STATES, Jurisdiction.UNITED_KINGDOM}

        return list(jurisdictions)

    def _location_to_jurisdiction(self, location: str) -> Optional[Jurisdiction]:
        """Map location string to jurisdiction"""

        location_mapping = {
            # EU Countries
            "austria": Jurisdiction.EUROPEAN_UNION,
            "belgium": Jurisdiction.EUROPEAN_UNION,
            "bulgaria": Jurisdiction.EUROPEAN_UNION,
            "croatia": Jurisdiction.EUROPEAN_UNION,
            "cyprus": Jurisdiction.EUROPEAN_UNION,
            "czech republic": Jurisdiction.EUROPEAN_UNION,
            "denmark": Jurisdiction.EUROPEAN_UNION,
            "estonia": Jurisdiction.EUROPEAN_UNION,
            "finland": Jurisdiction.EUROPEAN_UNION,
            "france": Jurisdiction.EUROPEAN_UNION,
            "germany": Jurisdiction.EUROPEAN_UNION,
            "greece": Jurisdiction.EUROPEAN_UNION,
            "hungary": Jurisdiction.EUROPEAN_UNION,
            "ireland": Jurisdiction.EUROPEAN_UNION,
            "italy": Jurisdiction.EUROPEAN_UNION,
            "latvia": Jurisdiction.EUROPEAN_UNION,
            "lithuania": Jurisdiction.EUROPEAN_UNION,
            "luxembourg": Jurisdiction.EUROPEAN_UNION,
            "malta": Jurisdiction.EUROPEAN_UNION,
            "netherlands": Jurisdiction.EUROPEAN_UNION,
            "poland": Jurisdiction.EUROPEAN_UNION,
            "portugal": Jurisdiction.EUROPEAN_UNION,
            "romania": Jurisdiction.EUROPEAN_UNION,
            "slovakia": Jurisdiction.EUROPEAN_UNION,
            "slovenia": Jurisdiction.EUROPEAN_UNION,
            "spain": Jurisdiction.EUROPEAN_UNION,
            "sweden": Jurisdiction.EUROPEAN_UNION,
            # Other jurisdictions
            "united states": Jurisdiction.UNITED_STATES,
            "usa": Jurisdiction.UNITED_STATES,
            "california": Jurisdiction.CALIFORNIA,
            "united kingdom": Jurisdiction.UNITED_KINGDOM,
            "uk": Jurisdiction.UNITED_KINGDOM,
            "canada": Jurisdiction.CANADA,
            "australia": Jurisdiction.AUSTRALIA,
            "singapore": Jurisdiction.SINGAPORE,
            "japan": Jurisdiction.JAPAN,
            "south korea": Jurisdiction.SOUTH_KOREA,
            "switzerland": Jurisdiction.SWITZERLAND,
            "new zealand": Jurisdiction.NEW_ZEALAND,
        }

        return location_mapping.get(location.lower())

    def _determine_primary_jurisdiction(
        self, applicable_jurisdictions: list[Jurisdiction], ai_system_data: dict[str, Any]
    ) -> Jurisdiction:
        """Determine primary jurisdiction for compliance focus"""

        # Priority order for primary jurisdiction
        priority_order = [
            Jurisdiction.EUROPEAN_UNION,  # Highest penalties and strictest requirements
            Jurisdiction.CALIFORNIA,  # Strict privacy requirements
            Jurisdiction.UNITED_STATES,  # Large market
            Jurisdiction.UNITED_KINGDOM,  # Similar to EU
            Jurisdiction.CANADA,  # Emerging comprehensive regulation
            Jurisdiction.AUSTRALIA,
            Jurisdiction.SINGAPORE,
            Jurisdiction.JAPAN,
            Jurisdiction.SOUTH_KOREA,
            Jurisdiction.SWITZERLAND,
            Jurisdiction.NEW_ZEALAND,
        ]

        # Find highest priority jurisdiction
        for jurisdiction in priority_order:
            if jurisdiction in applicable_jurisdictions:
                return jurisdiction

        # Fallback to first jurisdiction
        return applicable_jurisdictions[0] if applicable_jurisdictions else Jurisdiction.GLOBAL

    def _analyze_data_subject_locations(self, ai_system_data: dict[str, Any]) -> dict[Jurisdiction, int]:
        """Analyze data subject geographic distribution"""

        location_counts = {}
        data_subjects = ai_system_data.get("data_subjects", [])

        for subject in data_subjects:
            location = subject.get("location", "")
            if location:
                jurisdiction = self._location_to_jurisdiction(location)
                if jurisdiction:
                    location_counts[jurisdiction] = location_counts.get(jurisdiction, 0) + 1

        # If no specific data, estimate based on system scope
        if not location_counts:
            system_scope = ai_system_data.get("geographic_scope", "global")
            if system_scope == "global":
                location_counts = {
                    Jurisdiction.EUROPEAN_UNION: 100,
                    Jurisdiction.UNITED_STATES: 150,
                    Jurisdiction.UNITED_KINGDOM: 30,
                    Jurisdiction.CANADA: 20,
                    Jurisdiction.AUSTRALIA: 15,
                }

        return location_counts

    async def _assess_framework_compliance(
        self, framework: ComplianceFramework, ai_system_data: dict[str, Any], jurisdiction: Jurisdiction
    ) -> tuple[ComplianceStatus, float]:
        """Assess compliance for specific framework"""

        try:
            if framework == ComplianceFramework.EU_AI_ACT_2024:
                # Use EU AI Act classifier
                classification = await self.eu_classifier.classify_ai_system(ai_system_data)
                compliance_score = self._calculate_eu_ai_act_score(classification)

            elif framework in [
                ComplianceFramework.GDPR_2018,
                ComplianceFramework.CCPA_2020,
                ComplianceFramework.CCPA_ADMT_2025,
            ]:
                # Use privacy compliance engine
                assessment = await self.privacy_engine.assess_privacy_impact(ai_system_data, jurisdiction.value)
                compliance_score = 1.0 - assessment.risk_score  # Invert risk to compliance

            elif framework == ComplianceFramework.NIST_AI_RMF_2023:
                # Use NIST framework
                assessment = await self.nist_framework.assess_ai_system_risk(ai_system_data)
                compliance_score = 1.0 - assessment.overall_risk_score  # Invert risk to compliance

            else:
                # Default assessment for other frameworks
                compliance_score = await self._assess_general_framework(framework, ai_system_data)

            # Determine status from score
            if compliance_score >= self.compliance_thresholds[ComplianceStatus.COMPLIANT]:
                status = ComplianceStatus.COMPLIANT
            elif compliance_score >= self.compliance_thresholds[ComplianceStatus.PARTIALLY_COMPLIANT]:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT

            return status, compliance_score

        except Exception as e:
            self.logger.error(f"Framework compliance assessment failed for {framework.value}: {e!s}")
            return ComplianceStatus.UNDER_REVIEW, 0.5

    def _calculate_eu_ai_act_score(self, classification_result: dict[str, Any]) -> float:
        """Calculate EU AI Act compliance score"""

        risk_tier = classification_result.get("risk_tier", "minimal")

        # Score based on risk tier compliance
        tier_scores = {
            "prohibited": 0.0,  # Non-compliant if prohibited
            "high": 0.6,  # Requires significant compliance measures
            "limited": 0.8,  # Some transparency requirements
            "minimal": 1.0,  # Minimal requirements
        }

        base_score = tier_scores.get(risk_tier, 0.5)

        # Adjust based on compliance measures
        if classification_result.get("conformity_assessment_complete", False):
            base_score += 0.2
        if classification_result.get("registration_complete", False):
            base_score += 0.1
        if classification_result.get("fundamental_rights_assessment", False):
            base_score += 0.1

        return min(base_score, 1.0)

    async def _assess_general_framework(self, framework: ComplianceFramework, ai_system_data: dict[str, Any]) -> float:
        """Assess compliance for general frameworks"""

        # Simplified assessment based on common requirements
        compliance_factors = {
            "documentation": ai_system_data.get("documentation_complete", False) * 0.3,
            "risk_assessment": ai_system_data.get("risk_assessment_complete", False) * 0.3,
            "monitoring": ai_system_data.get("monitoring_systems", False) * 0.2,
            "governance": ai_system_data.get("governance_framework", False) * 0.2,
        }

        return sum(compliance_factors.values())

    async def _assess_cross_border_transfers(
        self, ai_system_data: dict[str, Any], jurisdictions: list[Jurisdiction]
    ) -> list[dict[str, Any]]:
        """Assess cross-border data transfer requirements"""

        transfers = []

        # Check if system involves cross-border data transfer
        if ai_system_data.get("cross_border_data_transfer", False):

            for source_jurisdiction in jurisdictions:
                for target_jurisdiction in jurisdictions:
                    if source_jurisdiction != target_jurisdiction:

                        transfer = {
                            "source_jurisdiction": source_jurisdiction.value,
                            "target_jurisdiction": target_jurisdiction.value,
                            "data_categories": ai_system_data.get("transferred_data_categories", []),
                            "transfer_volume": ai_system_data.get("transfer_volume", "unknown"),
                            "transfer_frequency": ai_system_data.get("transfer_frequency", "unknown"),
                            "adequacy_status": self._check_adequacy_status(source_jurisdiction, target_jurisdiction),
                            "compliance_required": True,
                        }

                        transfers.append(transfer)

        return transfers

    def _check_adequacy_status(self, source: Jurisdiction, target: Jurisdiction) -> str:
        """Check adequacy status between jurisdictions"""

        # EU adequacy decisions
        eu_adequate_countries = [
            Jurisdiction.UNITED_KINGDOM,
            Jurisdiction.CANADA,
            Jurisdiction.SWITZERLAND,
            Jurisdiction.NEW_ZEALAND,
            Jurisdiction.JAPAN,
            Jurisdiction.SOUTH_KOREA,
        ]

        if source == Jurisdiction.EUROPEAN_UNION:
            if target in eu_adequate_countries:
                return "adequate"
            else:
                return "inadequate_protection_required"

        return "assessment_required"

    def _determine_transfer_mechanisms(self, transfers: list[dict[str, Any]]) -> dict[str, DataTransferMechanism]:
        """Determine appropriate transfer mechanisms for cross-border transfers"""

        mechanisms = {}

        for transfer in transfers:
            transfer_key = f"{transfer['source_jurisdiction']}_{transfer['target_jurisdiction']}"

            if transfer["adequacy_status"] == "adequate":
                mechanisms[transfer_key] = DataTransferMechanism.ADEQUACY_DECISION
            else:
                # Default to Standard Contractual Clauses
                mechanisms[transfer_key] = DataTransferMechanism.STANDARD_CONTRACTUAL_CLAUSES

        return mechanisms

    async def _check_data_sovereignty(self, ai_system_data: dict[str, Any], jurisdictions: list[Jurisdiction]) -> bool:
        """Check data sovereignty compliance"""

        # Check for data localization requirements
        for jurisdiction in jurisdictions:
            profile = self.jurisdiction_profiles.get(jurisdiction)
            if profile and profile.data_localization_required:
                # Check if data is properly localized
                if not ai_system_data.get(f"data_localized_{jurisdiction.value}", False):
                    return False

        return True

    def _calculate_overall_compliance_score(
        self, compliance_scores: dict[ComplianceFramework, float], jurisdictions: list[Jurisdiction]
    ) -> float:
        """Calculate weighted overall compliance score"""

        if not compliance_scores:
            return 0.0

        weighted_score = 0.0
        total_weight = 0.0

        for framework, score in compliance_scores.items():
            weight = self.framework_weights.get(framework, 0.05)  # Default low weight
            weighted_score += score * weight
            total_weight += weight

        # Adjust for jurisdiction coverage
        jurisdiction_coverage = min(len(jurisdictions) / 3.0, 1.0)  # Normalize to max 3 jurisdictions

        return (weighted_score / max(total_weight, 1.0)) * jurisdiction_coverage

    def _determine_global_compliance_status(self, overall_score: float) -> ComplianceStatus:
        """Determine global compliance status from overall score"""

        if overall_score >= self.compliance_thresholds[ComplianceStatus.COMPLIANT]:
            return ComplianceStatus.COMPLIANT
        elif overall_score >= self.compliance_thresholds[ComplianceStatus.PARTIALLY_COMPLIANT]:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT

    async def _identify_compliance_gaps(
        self,
        framework_compliance: dict[ComplianceFramework, ComplianceStatus],
        compliance_scores: dict[ComplianceFramework, float],
    ) -> list[dict[str, Any]]:
        """Identify specific compliance gaps"""

        gaps = []

        for framework, status in framework_compliance.items():
            if status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT]:
                gap = {
                    "framework": framework.value,
                    "status": status.value,
                    "score": compliance_scores.get(framework, 0.0),
                    "gap_size": 1.0 - compliance_scores.get(framework, 0.0),
                    "priority": "high" if status == ComplianceStatus.NON_COMPLIANT else "medium",
                    "estimated_effort": self._estimate_gap_effort(framework, status),
                }
                gaps.append(gap)

        return sorted(gaps, key=lambda x: x["gap_size"], reverse=True)

    async def _identify_harmonization_conflicts(
        self, jurisdictions: list[Jurisdiction], ai_system_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Identify conflicts between jurisdictional requirements"""

        conflicts = []

        # Check for common conflict areas
        conflict_areas = [
            "data_localization",
            "cross_border_transfers",
            "consent_mechanisms",
            "algorithmic_transparency",
            "automated_decision_making",
        ]

        for area in conflict_areas:
            area_conflicts = self._check_area_conflicts(area, jurisdictions, ai_system_data)
            conflicts.extend(area_conflicts)

        return conflicts

    def _check_area_conflicts(
        self, area: str, jurisdictions: list[Jurisdiction], ai_system_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Check for conflicts in specific area"""

        conflicts = []

        if area == "data_localization":
            # EU allows cross-border with adequacy, US generally allows, China requires localization
            for jurisdiction in jurisdictions:
                profile = self.jurisdiction_profiles.get(jurisdiction)
                if profile and profile.data_localization_required:
                    # Check if conflicts with other jurisdictions
                    for other_jurisdiction in jurisdictions:
                        if other_jurisdiction != jurisdiction:
                            other_profile = self.jurisdiction_profiles.get(other_jurisdiction)
                            if other_profile and not other_profile.data_localization_required:
                                conflicts.append(
                                    {
                                        "area": area,
                                        "conflicting_jurisdictions": [jurisdiction.value, other_jurisdiction.value],
                                        "conflict_description": "Data localization requirement conflict",
                                        "resolution_strategy": "jurisdiction_specific_deployment",
                                    }
                                )

        return conflicts

    def _generate_priority_actions(
        self, gaps: list[dict[str, Any]], conflicts: list[dict[str, Any]], global_status: ComplianceStatus
    ) -> list[str]:
        """Generate priority actions for compliance remediation"""

        actions = []

        # Address high-priority gaps first
        high_priority_gaps = [g for g in gaps if g["priority"] == "high"]
        for gap in high_priority_gaps[:3]:  # Top 3 gaps
            actions.append(f"Address {gap['framework']} compliance gap (score: {gap['score']:.2f})")

        # Address harmonization conflicts
        for conflict in conflicts[:2]:  # Top 2 conflicts
            actions.append(
                f"Resolve {conflict['area']} conflict between {', '.join(conflict['conflicting_jurisdictions'])}"
            )

        # Global status specific actions
        if global_status == ComplianceStatus.NON_COMPLIANT:
            actions.insert(0, "Implement immediate compliance remediation plan")
        elif global_status == ComplianceStatus.PARTIALLY_COMPLIANT:
            actions.append("Enhance existing compliance measures to full compliance")

        return actions

    def _estimate_remediation_time(self, gaps: list[dict[str, Any]], global_status: ComplianceStatus) -> int:
        """Estimate remediation time in days"""

        base_time = {
            ComplianceStatus.COMPLIANT: 0,
            ComplianceStatus.PARTIALLY_COMPLIANT: 30,
            ComplianceStatus.NON_COMPLIANT: 90,
        }.get(global_status, 60)

        # Add time for each gap
        gap_time = sum(gap.get("estimated_effort", 10) for gap in gaps)

        return base_time + gap_time

    def _estimate_gap_effort(self, framework: ComplianceFramework, status: ComplianceStatus) -> int:
        """Estimate effort to close compliance gap in days"""

        effort_matrix = {
            ComplianceFramework.EU_AI_ACT_2024: {
                ComplianceStatus.NON_COMPLIANT: 60,
                ComplianceStatus.PARTIALLY_COMPLIANT: 30,
            },
            ComplianceFramework.GDPR_2018: {
                ComplianceStatus.NON_COMPLIANT: 45,
                ComplianceStatus.PARTIALLY_COMPLIANT: 20,
            },
            ComplianceFramework.NIST_AI_RMF_2023: {
                ComplianceStatus.NON_COMPLIANT: 30,
                ComplianceStatus.PARTIALLY_COMPLIANT: 15,
            },
        }

        return effort_matrix.get(framework, {}).get(status, 20)

    def _determine_regulatory_notifications(
        self,
        jurisdictions: list[Jurisdiction],
        ai_system_data: dict[str, Any],
        framework_compliance: dict[ComplianceFramework, ComplianceStatus],
    ) -> list[str]:
        """Determine required regulatory notifications"""

        notifications = []

        for jurisdiction in jurisdictions:
            profile = self.jurisdiction_profiles.get(jurisdiction)
            if profile:

                # EU AI Act high-risk system registration
                if jurisdiction == Jurisdiction.EUROPEAN_UNION and ai_system_data.get("eu_high_risk_system", False):
                    notifications.append("EU AI Act high-risk system registration required")

                # CCPA consumer data processing notification
                if jurisdiction == Jurisdiction.CALIFORNIA and ai_system_data.get(
                    "processes_california_consumer_data", False
                ):
                    notifications.append("CCPA consumer data processing notification required")

        return notifications

    def _calculate_next_review(self, global_status: ComplianceStatus) -> datetime:
        """Calculate next compliance review date"""

        review_intervals = {
            ComplianceStatus.COMPLIANT: 180,  # 6 months
            ComplianceStatus.PARTIALLY_COMPLIANT: 90,  # 3 months
            ComplianceStatus.NON_COMPLIANT: 30,  # 1 month
            ComplianceStatus.UNDER_REVIEW: 14,  # 2 weeks
        }

        days = review_intervals.get(global_status, 90)
        return datetime.now(timezone.utc) + timedelta(days=days)

    def _generate_assessment_id(self, ai_system_data: dict[str, Any]) -> str:
        """Generate unique global assessment ID"""

        system_name = ai_system_data.get("name", "system")[:10]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"GLOBAL_COMPLIANCE_{timestamp}_{system_name}"

    async def monitor_regulatory_changes(self) -> list[RegulatoryChange]:
        """Monitor and track regulatory changes across jurisdictions"""

        try:
            # In production: integrate with regulatory monitoring services
            # For now, return example regulatory changes

            changes = []

            # Example: EU AI Act implementation guidance
            eu_change = RegulatoryChange(
                change_id="EU_AI_ACT_2024_GUIDANCE_001",
                jurisdiction=Jurisdiction.EUROPEAN_UNION,
                framework=ComplianceFramework.EU_AI_ACT_2024,
                change_type="guidance",
                effective_date=datetime.now(timezone.utc) + timedelta(days=30),
                impact_assessment="medium",
                affected_systems=["generative_ai", "high_risk_classification"],
                required_actions=[
                    "Review GPAI model registration requirements",
                    "Update conformity assessment procedures",
                ],
                compliance_deadline=datetime.now(timezone.utc) + timedelta(days=90),
            )
            changes.append(eu_change)

            # Store changes
            for change in changes:
                self.regulatory_changes[change.change_id] = change

            self.logger.info(f"Monitored {len(changes)} regulatory changes")

            return changes

        except Exception as e:
            self.logger.error(f"Regulatory change monitoring failed: {e!s}")
            return []

    def get_global_compliance_status(self) -> dict[str, Any]:
        """Get current global compliance status overview"""

        assessments = list(self.global_assessments.values())

        return {
            "manager_version": "1.0.0",
            "total_assessments": len(assessments),
            "jurisdictions_covered": len(set().union(*[a.applicable_jurisdictions for a in assessments])),
            "frameworks_assessed": len(set().union(*[a.framework_compliance.keys() for a in assessments])),
            "global_compliance_distribution": {
                status.value: len([a for a in assessments if a.global_compliance_status == status])
                for status in ComplianceStatus
            },
            "average_compliance_score": sum(a.overall_compliance_score for a in assessments) / max(len(assessments), 1),
            "cross_border_systems": len([a for a in assessments if a.cross_border_transfers]),
            "regulatory_changes_tracked": len(self.regulatory_changes),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    def generate_multi_jurisdictional_report(self) -> dict[str, Any]:
        """Generate comprehensive multi-jurisdictional compliance report"""

        assessments = list(self.global_assessments.values())

        return {
            "report_id": f"MULTI_JURISDICTIONAL_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "executive_summary": {
                "total_ai_systems_assessed": len(assessments),
                "jurisdictions_covered": list(set().union(*[a.applicable_jurisdictions for a in assessments])),
                "overall_compliance_rate": len(
                    [a for a in assessments if a.global_compliance_status == ComplianceStatus.COMPLIANT]
                )
                / max(len(assessments), 1),
                "systems_requiring_immediate_attention": len(
                    [a for a in assessments if a.global_compliance_status == ComplianceStatus.NON_COMPLIANT]
                ),
                "cross_border_compliance_challenges": len([a for a in assessments if a.harmonization_conflicts]),
            },
            "jurisdiction_breakdown": self._generate_jurisdiction_breakdown(assessments),
            "framework_compliance_matrix": self._generate_framework_matrix(assessments),
            "cross_border_transfer_analysis": self._generate_transfer_analysis(assessments),
            "harmonization_challenges": self._generate_harmonization_report(assessments),
            "remediation_roadmap": self._generate_remediation_roadmap(assessments),
            "regulatory_change_impact": self._assess_regulatory_change_impact(),
            "recommendations": {
                "immediate_actions": self._generate_immediate_actions(assessments),
                "strategic_initiatives": self._generate_strategic_initiatives(assessments),
                "governance_improvements": self._generate_governance_improvements(assessments),
            },
        }

    def _generate_jurisdiction_breakdown(self, assessments: list[GlobalComplianceAssessment]) -> dict[str, Any]:
        """Generate jurisdiction-specific breakdown"""

        breakdown = {}

        for jurisdiction in Jurisdiction:
            relevant_assessments = [a for a in assessments if jurisdiction in a.applicable_jurisdictions]

            if relevant_assessments:
                breakdown[jurisdiction.value] = {
                    "systems_assessed": len(relevant_assessments),
                    "compliance_rate": len(
                        [a for a in relevant_assessments if a.global_compliance_status == ComplianceStatus.COMPLIANT]
                    )
                    / len(relevant_assessments),
                    "average_compliance_score": sum(a.overall_compliance_score for a in relevant_assessments)
                    / len(relevant_assessments),
                    "data_subjects_affected": sum(
                        a.data_subject_locations.get(jurisdiction, 0) for a in relevant_assessments
                    ),
                    "priority_actions": len([a for a in relevant_assessments if a.priority_actions]),
                }

        return breakdown

    def _generate_framework_matrix(self, assessments: list[GlobalComplianceAssessment]) -> dict[str, Any]:
        """Generate framework compliance matrix"""

        matrix = {}

        for framework in ComplianceFramework:
            framework_assessments = [a for a in assessments if framework in a.framework_compliance]

            if framework_assessments:
                matrix[framework.value] = {
                    "systems_assessed": len(framework_assessments),
                    "compliance_distribution": {
                        status.value: len(
                            [a for a in framework_assessments if a.framework_compliance[framework] == status]
                        )
                        for status in ComplianceStatus
                    },
                    "average_score": sum(a.compliance_scores.get(framework, 0.0) for a in framework_assessments)
                    / len(framework_assessments),
                }

        return matrix

    def _generate_transfer_analysis(self, assessments: list[GlobalComplianceAssessment]) -> dict[str, Any]:
        """Generate cross-border transfer analysis"""

        transfer_systems = [a for a in assessments if a.cross_border_transfers]

        return {
            "systems_with_transfers": len(transfer_systems),
            "transfer_compliance_rate": len([a for a in transfer_systems if a.data_sovereignty_compliance])
            / max(len(transfer_systems), 1),
            "common_transfer_mechanisms": self._analyze_transfer_mechanisms(transfer_systems),
            "adequacy_decision_usage": self._analyze_adequacy_decisions(transfer_systems),
            "compliance_challenges": self._analyze_transfer_challenges(transfer_systems),
        }

    def _generate_harmonization_report(self, assessments: list[GlobalComplianceAssessment]) -> dict[str, Any]:
        """Generate harmonization challenges report"""

        conflicts = []
        for assessment in assessments:
            conflicts.extend(assessment.harmonization_conflicts)

        return {
            "total_conflicts_identified": len(conflicts),
            "conflict_areas": list(set(c.get("area", "unknown") for c in conflicts)),
            "most_conflicted_jurisdictions": self._identify_most_conflicted_jurisdictions(conflicts),
            "resolution_strategies": self._analyze_resolution_strategies(conflicts),
        }

    def _generate_remediation_roadmap(self, assessments: list[GlobalComplianceAssessment]) -> dict[str, Any]:
        """Generate comprehensive remediation roadmap"""

        all_gaps = []
        for assessment in assessments:
            all_gaps.extend(assessment.compliance_gaps)

        return {
            "total_gaps_identified": len(all_gaps),
            "high_priority_gaps": len([g for g in all_gaps if g.get("priority") == "high"]),
            "estimated_total_remediation_time": sum(g.get("estimated_effort", 0) for g in all_gaps),
            "remediation_phases": self._plan_remediation_phases(all_gaps),
            "resource_requirements": self._estimate_remediation_resources(all_gaps),
        }

    def _assess_regulatory_change_impact(self) -> dict[str, Any]:
        """Assess impact of tracked regulatory changes"""

        changes = list(self.regulatory_changes.values())

        return {
            "total_changes_tracked": len(changes),
            "high_impact_changes": len([c for c in changes if c.impact_assessment == "high"]),
            "upcoming_deadlines": len(
                [
                    c
                    for c in changes
                    if c.compliance_deadline
                    and c.compliance_deadline <= datetime.now(timezone.utc) + timedelta(days=90)
                ]
            ),
            "affected_systems_count": len(set().union(*[c.affected_systems for c in changes])),
        }

    def _generate_immediate_actions(self, assessments: list[GlobalComplianceAssessment]) -> list[str]:
        """Generate immediate action recommendations"""

        actions = []

        # Non-compliant systems
        non_compliant_count = len(
            [a for a in assessments if a.global_compliance_status == ComplianceStatus.NON_COMPLIANT]
        )
        if non_compliant_count > 0:
            actions.append(
                f"Implement immediate compliance remediation for {non_compliant_count} non-compliant systems"
            )

        # High-priority gaps
        high_priority_gaps = sum(
            len([g for g in a.compliance_gaps if g.get("priority") == "high"]) for a in assessments
        )
        if high_priority_gaps > 0:
            actions.append(f"Address {high_priority_gaps} high-priority compliance gaps")

        return actions

    def _generate_strategic_initiatives(self, assessments: list[GlobalComplianceAssessment]) -> list[str]:
        """Generate strategic initiative recommendations"""

        initiatives = [
            "Implement unified global compliance management platform",
            "Establish cross-jurisdictional compliance governance framework",
            "Develop automated regulatory change monitoring and adaptation",
            "Create harmonized compliance assessment methodology",
            "Implement proactive compliance risk management",
        ]

        return initiatives

    def _generate_governance_improvements(self, assessments: list[GlobalComplianceAssessment]) -> list[str]:
        """Generate governance improvement recommendations"""

        improvements = [
            "Establish global compliance oversight committee",
            "Implement multi-jurisdictional compliance review processes",
            "Create compliance escalation and incident response procedures",
            "Develop compliance training and awareness programs",
            "Establish third-party compliance audit framework",
        ]

        return improvements

    # Helper methods for report generation
    def _analyze_transfer_mechanisms(self, transfer_systems: list[GlobalComplianceAssessment]) -> dict[str, int]:
        """Analyze usage of transfer mechanisms"""
        mechanism_counts = {}
        for system in transfer_systems:
            for mechanism in system.transfer_mechanisms.values():
                mechanism_counts[mechanism.value] = mechanism_counts.get(mechanism.value, 0) + 1
        return mechanism_counts

    def _analyze_adequacy_decisions(self, transfer_systems: list[GlobalComplianceAssessment]) -> dict[str, int]:
        """Analyze adequacy decision usage"""
        adequacy_usage = {}
        for system in transfer_systems:
            for transfer in system.cross_border_transfers:
                adequacy = transfer.get("adequacy_status", "unknown")
                adequacy_usage[adequacy] = adequacy_usage.get(adequacy, 0) + 1
        return adequacy_usage

    def _analyze_transfer_challenges(self, transfer_systems: list[GlobalComplianceAssessment]) -> list[str]:
        """Analyze common transfer challenges"""
        return [
            "Inadequate cross-border data protection mechanisms",
            "Conflict between data localization and transfer requirements",
            "Lack of real-time transfer compliance monitoring",
            "Complex multi-hop data transfer compliance tracking",
        ]

    def _identify_most_conflicted_jurisdictions(self, conflicts: list[dict[str, Any]]) -> list[str]:
        """Identify jurisdictions with most conflicts"""
        jurisdiction_conflicts = {}
        for conflict in conflicts:
            for jurisdiction in conflict.get("conflicting_jurisdictions", []):
                jurisdiction_conflicts[jurisdiction] = jurisdiction_conflicts.get(jurisdiction, 0) + 1

        return sorted(jurisdiction_conflicts.keys(), key=lambda x: jurisdiction_conflicts[x], reverse=True)[:5]

    def _analyze_resolution_strategies(self, conflicts: list[dict[str, Any]]) -> dict[str, int]:
        """Analyze resolution strategies"""
        strategies = {}
        for conflict in conflicts:
            strategy = conflict.get("resolution_strategy", "unknown")
            strategies[strategy] = strategies.get(strategy, 0) + 1
        return strategies

    def _plan_remediation_phases(self, gaps: list[dict[str, Any]]) -> dict[str, list[str]]:
        """Plan remediation in phases"""
        return {
            "phase_1_immediate": [g["framework"] for g in gaps if g.get("priority") == "high"][:5],
            "phase_2_short_term": [g["framework"] for g in gaps if g.get("priority") == "medium"][:5],
            "phase_3_long_term": [g["framework"] for g in gaps if g.get("priority") == "low"][:5],
        }

    def _estimate_remediation_resources(self, gaps: list[dict[str, Any]]) -> dict[str, Any]:
        """Estimate resources needed for remediation"""
        return {
            "total_estimated_days": sum(g.get("estimated_effort", 0) for g in gaps),
            "legal_expertise_required": len([g for g in gaps if "legal" in g.get("framework", "")]),
            "technical_implementation_required": len([g for g in gaps if "technical" in str(g)]),
            "third_party_audit_required": len([g for g in gaps if g.get("priority") == "high"]),
        }
