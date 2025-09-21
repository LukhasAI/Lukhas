import logging

logger = logging.getLogger(__name__)
"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Constitutional AI Compliance: Democratic Identity Validation
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: CONSTITUTIONAL_VALIDATOR
║ CONSCIOUSNESS_ROLE: Democratic principle enforcement for identity decisions
║ EVOLUTIONARY_STAGE: Compliance - Constitutional AI integration
║
║ CONSTELLATION FRAMEWORK:
║ ⚛️ IDENTITY: Democratic identity decision validation
║ 🧠 CONSCIOUSNESS: Consciousness-aware ethical reasoning
║ 🛡️ GUARDIAN: Constitutional compliance enforcement and oversight
╚══════════════════════════════════════════════════════════════
"""

import asyncio
import logging as std_logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional

# Import MΛTRIZ consciousness components
try:
    from ..matriz_consciousness_signals import ConsciousnessSignal  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: kept for MATRIZ-R2 trace integration
    from .matriz_consciousness_identity_signals import (
        ConstitutionalComplianceData,
        IdentitySignalType,
        consciousness_identity_signal_emitter,
    )
except ImportError as e:
    std_logging.error(f"Failed to import consciousness signal components: {e}")
    consciousness_identity_signal_emitter = None
    ConstitutionalComplianceData = None

logger = std_logging.getLogger(__name__)


class ConstitutionalPrinciple(Enum):
    """Core Constitutional AI principles for identity decisions"""

    DEMOCRATIC_GOVERNANCE = "democratic_governance"
    HUMAN_AUTONOMY = "human_autonomy"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    FAIRNESS = "fairness"
    PRIVACY = "privacy"
    CONSENT = "consent"
    NON_DISCRIMINATION = "non_discrimination"
    PROPORTIONALITY = "proportionality"
    EXPLAINABILITY = "explainability"


class ComplianceLevel(Enum):
    """Levels of constitutional compliance"""

    FULL_COMPLIANCE = "full_compliance"  # 1.0 - Fully compliant
    SUBSTANTIAL_COMPLIANCE = "substantial_compliance"  # 0.8-0.99 - Mostly compliant
    PARTIAL_COMPLIANCE = "partial_compliance"  # 0.6-0.79 - Some issues
    MINIMAL_COMPLIANCE = "minimal_compliance"  # 0.4-0.59 - Significant issues
    NON_COMPLIANCE = "non_compliance"  # 0.0-0.39 - Major violations


class DecisionType(Enum):
    """Types of identity decisions requiring constitutional validation"""

    AUTHENTICATION = "authentication"
    IDENTITY_CREATION = "identity_creation"
    ACCESS_GRANT = "access_grant"
    ACCESS_REVOCATION = "access_revocation"
    DATA_PROCESSING = "data_processing"
    CONSCIOUSNESS_EVOLUTION = "consciousness_evolution"
    NAMESPACE_ASSIGNMENT = "namespace_assignment"
    BIOMETRIC_COLLECTION = "biometric_collection"
    CROSS_DOMAIN_ACCESS = "cross_domain_access"
    EMERGENCY_OVERRIDE = "emergency_override"


@dataclass
class ConstitutionalValidationContext:
    """Context for constitutional validation"""

    decision_type: DecisionType
    identity_id: str
    decision_data: dict[str, Any] = field(default_factory=dict)

    # Stakeholder information
    affected_individuals: list[str] = field(default_factory=list)
    decision_maker: str = ""
    oversight_entities: list[str] = field(default_factory=list)

    # Context factors
    urgency_level: str = "normal"  # "low", "normal", "high", "emergency"
    risk_assessment: dict[str, float] = field(default_factory=dict)
    impact_scope: str = "individual"  # "individual", "group", "system", "global"

    # Previous decisions and precedent
    related_decisions: list[dict[str, Any]] = field(default_factory=list)
    precedent_analysis: Optional[dict[str, Any]] = None

    # Temporal factors
    decision_deadline: Optional[datetime] = None
    review_period: Optional[timedelta] = None


@dataclass
class PrincipleEvaluation:
    """Evaluation of a single constitutional principle"""

    principle: ConstitutionalPrinciple
    score: float = 0.0  # 0.0-1.0 compliance score
    compliant: bool = False

    # Detailed evaluation
    evaluation_criteria: list[str] = field(default_factory=list)
    evidence_supporting: list[str] = field(default_factory=list)
    evidence_against: list[str] = field(default_factory=list)

    # Reasoning and explanation
    reasoning: str = ""
    explanation: str = ""
    confidence_level: float = 0.8

    # Recommendations
    improvement_suggestions: list[str] = field(default_factory=list)
    mitigation_measures: list[str] = field(default_factory=list)

    # Metadata
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evaluator: str = "constitutional_ai_validator"


@dataclass
class ConstitutionalValidationResult:
    """Result of constitutional AI validation"""

    validation_id: str = field(default_factory=lambda: f"cv-{uuid.uuid4().hex[:12]}")
    decision_context: ConstitutionalValidationContext = None

    # Overall compliance
    overall_compliance_score: float = 0.0
    compliance_level: ComplianceLevel = ComplianceLevel.NON_COMPLIANCE
    constitutional_compliant: bool = False

    # Principle evaluations
    principle_evaluations: dict[ConstitutionalPrinciple, PrincipleEvaluation] = field(default_factory=dict)

    # Decision recommendation
    decision_approved: bool = False
    approval_conditions: list[str] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)

    # Human oversight
    human_oversight_required: bool = False
    oversight_reasons: list[str] = field(default_factory=list)
    recommended_reviewers: list[str] = field(default_factory=list)

    # Transparency and explanation
    explanation_summary: str = ""
    detailed_explanation: dict[str, str] = field(default_factory=dict)
    public_explanation: Optional[str] = None

    # Follow-up requirements
    monitoring_requirements: list[str] = field(default_factory=list)
    review_schedule: Optional[list[datetime]] = None
    appeals_process_available: bool = True

    # Metadata
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_duration_ms: float = 0.0
    validation_version: str = "1.0"


class ConstitutionalAIValidator:
    """
    MΛTRIZ Constitutional AI Validator

    Implements democratic principle enforcement for identity decisions,
    ensuring all identity-related decisions comply with Constitutional AI
    principles including transparency, accountability, fairness, and human autonomy.
    """

    def __init__(self):
        # Principle validators
        self.principle_validators: dict[ConstitutionalPrinciple, Callable] = {
            ConstitutionalPrinciple.DEMOCRATIC_GOVERNANCE: self._validate_democratic_governance,
            ConstitutionalPrinciple.HUMAN_AUTONOMY: self._validate_human_autonomy,
            ConstitutionalPrinciple.TRANSPARENCY: self._validate_transparency,
            ConstitutionalPrinciple.ACCOUNTABILITY: self._validate_accountability,
            ConstitutionalPrinciple.FAIRNESS: self._validate_fairness,
            ConstitutionalPrinciple.PRIVACY: self._validate_privacy,
            ConstitutionalPrinciple.CONSENT: self._validate_consent,
            ConstitutionalPrinciple.NON_DISCRIMINATION: self._validate_non_discrimination,
            ConstitutionalPrinciple.PROPORTIONALITY: self._validate_proportionality,
            ConstitutionalPrinciple.EXPLAINABILITY: self._validate_explainability,
        }

        # Configuration
        self.validation_enabled = True
        self.strict_mode = False  # Strict mode requires higher compliance scores
        self.human_oversight_threshold = 0.6  # Below this score requires human oversight
        self.approval_threshold = 0.7  # Minimum score for automatic approval

        # Decision-specific principle weights
        self.decision_principle_weights = {
            DecisionType.AUTHENTICATION: {
                ConstitutionalPrinciple.PRIVACY: 0.2,
                ConstitutionalPrinciple.CONSENT: 0.15,
                ConstitutionalPrinciple.FAIRNESS: 0.15,
                ConstitutionalPrinciple.TRANSPARENCY: 0.1,
                ConstitutionalPrinciple.PROPORTIONALITY: 0.15,
                ConstitutionalPrinciple.ACCOUNTABILITY: 0.1,
                ConstitutionalPrinciple.HUMAN_AUTONOMY: 0.1,
                ConstitutionalPrinciple.NON_DISCRIMINATION: 0.05,
            },
            DecisionType.DATA_PROCESSING: {
                ConstitutionalPrinciple.PRIVACY: 0.25,
                ConstitutionalPrinciple.CONSENT: 0.2,
                ConstitutionalPrinciple.TRANSPARENCY: 0.15,
                ConstitutionalPrinciple.ACCOUNTABILITY: 0.15,
                ConstitutionalPrinciple.FAIRNESS: 0.1,
                ConstitutionalPrinciple.PROPORTIONALITY: 0.1,
                ConstitutionalPrinciple.HUMAN_AUTONOMY: 0.05,
            },
            DecisionType.EMERGENCY_OVERRIDE: {
                ConstitutionalPrinciple.HUMAN_AUTONOMY: 0.3,
                ConstitutionalPrinciple.ACCOUNTABILITY: 0.2,
                ConstitutionalPrinciple.PROPORTIONALITY: 0.2,
                ConstitutionalPrinciple.TRANSPARENCY: 0.15,
                ConstitutionalPrinciple.DEMOCRATIC_GOVERNANCE: 0.1,
                ConstitutionalPrinciple.EXPLAINABILITY: 0.05,
            },
        }

        # Default weights for decisions not specifically configured
        self.default_principle_weights = {principle: 0.1 for principle in ConstitutionalPrinciple}

        # Validation history and metrics
        self.validation_history: list[ConstitutionalValidationResult] = []
        self.validation_metrics = {
            "total_validations": 0,
            "approvals": 0,
            "rejections": 0,
            "human_oversight_required": 0,
            "average_compliance_score": 0.0,
            "average_validation_time_ms": 0.0,
        }

        # Background monitoring
        self._monitoring_active = False
        self._lock = asyncio.Lock()

        logger.info("⚖️ Constitutional AI validator initialized")

    async def initialize_constitutional_validation(self) -> bool:
        """Initialize constitutional AI validation system"""

        try:
            logger.info("🧬 Initializing Constitutional AI validation system...")

            # Start background monitoring
            self._monitoring_active = True
            asyncio.create_task(self._validation_monitoring_loop())

            logger.info("✅ Constitutional AI validation system initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize constitutional validation: {e}")
            return False

    async def validate_identity_decision(
        self, decision_context: ConstitutionalValidationContext
    ) -> ConstitutionalValidationResult:
        """Validate identity decision against Constitutional AI principles"""

        async with self._lock:
            start_time = time.perf_counter()

            try:
                # Create validation result
                result = ConstitutionalValidationResult(decision_context=decision_context)

                # Get principle weights for this decision type
                weights = self.decision_principle_weights.get(
                    decision_context.decision_type, self.default_principle_weights
                )

                # Evaluate each constitutional principle
                principle_tasks = []
                for principle, validator in self.principle_validators.items():
                    principle_tasks.append(self._evaluate_principle(principle, validator, decision_context))

                # Execute principle evaluations in parallel
                principle_evaluations = await asyncio.gather(*principle_tasks, return_exceptions=True)

                # Process evaluation results
                total_weighted_score = 0.0
                total_weight = 0.0

                for evaluation in principle_evaluations:
                    if isinstance(evaluation, Exception):
                        logger.error(f"❌ Principle evaluation failed: {evaluation}")
                        continue

                    if isinstance(evaluation, PrincipleEvaluation):
                        result.principle_evaluations[evaluation.principle] = evaluation

                        # Calculate weighted score
                        weight = weights.get(evaluation.principle, 0.1)
                        total_weighted_score += evaluation.score * weight
                        total_weight += weight

                # Calculate overall compliance
                if total_weight > 0:
                    result.overall_compliance_score = total_weighted_score / total_weight
                else:
                    result.overall_compliance_score = 0.0

                # Determine compliance level
                result.compliance_level = self._determine_compliance_level(result.overall_compliance_score)
                result.constitutional_compliant = result.compliance_level in [
                    ComplianceLevel.FULL_COMPLIANCE,
                    ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
                ]

                # Make decision recommendation
                self._make_decision_recommendation(result, decision_context)

                # Generate explanations
                self._generate_explanations(result)

                # Determine human oversight requirements
                self._evaluate_human_oversight_requirements(result, decision_context)

                # Set validation metadata
                result.validation_duration_ms = (time.perf_counter() - start_time) * 1000

                # Store validation result
                self.validation_history.append(result)
                self._update_validation_metrics(result)

                # Emit constitutional compliance signal
                if consciousness_identity_signal_emitter and ConstitutionalComplianceData:
                    compliance_data = ConstitutionalComplianceData(
                        democratic_validation=result.constitutional_compliant,
                        human_oversight_required=result.human_oversight_required,
                        transparency_score=result.principle_evaluations.get(
                            ConstitutionalPrinciple.TRANSPARENCY,
                            PrincipleEvaluation(ConstitutionalPrinciple.TRANSPARENCY),
                        ).score,
                        fairness_score=result.principle_evaluations.get(
                            ConstitutionalPrinciple.FAIRNESS, PrincipleEvaluation(ConstitutionalPrinciple.FAIRNESS)
                        ).score,
                        constitutional_aligned=result.constitutional_compliant,
                    )

                    await consciousness_identity_signal_emitter.emit_constitutional_compliance_signal(
                        decision_context.identity_id, compliance_data, decision_context.decision_data
                    )

                logger.info(
                    f"⚖️ Constitutional validation completed: {result.validation_id} (Score: {result.overall_compliance_score:.3f}, Approved: {result.decision_approved})"
                )
                return result

            except Exception as e:
                logger.error(f"❌ Constitutional validation failed: {e}")

                # Create error result
                error_result = ConstitutionalValidationResult(
                    decision_context=decision_context,
                    decision_approved=False,
                    rejection_reasons=[f"Validation error: {e!s}"],
                    human_oversight_required=True,
                    oversight_reasons=["Validation system error"],
                    validation_duration_ms=(time.perf_counter() - start_time) * 1000,
                )

                return error_result

    async def _evaluate_principle(
        self, principle: ConstitutionalPrinciple, validator: Callable, context: ConstitutionalValidationContext
    ) -> PrincipleEvaluation:
        """Evaluate a single constitutional principle"""

        try:
            evaluation = await validator(context)
            evaluation.principle = principle
            return evaluation

        except Exception as e:
            logger.error(f"❌ Failed to evaluate principle {principle.value}: {e}")

            # Return failed evaluation
            return PrincipleEvaluation(
                principle=principle,
                score=0.0,
                compliant=False,
                reasoning=f"Evaluation failed: {e!s}",
                confidence_level=0.0,
            )

    async def _validate_democratic_governance(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate democratic governance principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.DEMOCRATIC_GOVERNANCE,
            evaluation_criteria=[
                "Decision-making process involves stakeholder input",
                "Transparent governance procedures",
                "Accountability mechanisms in place",
                "Appeals process available",
            ],
        )

        score_factors = []

        # Check for stakeholder involvement
        if len(context.affected_individuals) > 0:
            evaluation.evidence_supporting.append("Multiple stakeholders identified")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("No stakeholder involvement documented")
            score_factors.append(0.4)

        # Check for oversight entities
        if len(context.oversight_entities) > 0:
            evaluation.evidence_supporting.append("Oversight entities involved")
            score_factors.append(0.9)
        else:
            evaluation.evidence_against.append("No oversight entities identified")
            score_factors.append(0.5)

        # Check for decision maker accountability
        if context.decision_maker:
            evaluation.evidence_supporting.append("Decision maker identified")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("Anonymous decision making")
            score_factors.append(0.3)

        # Calculate overall score
        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = f"Democratic governance score based on stakeholder involvement ({len(context.affected_individuals)} individuals), oversight entities ({len(context.oversight_entities)}), and decision maker accountability."

        if not evaluation.compliant:
            evaluation.improvement_suggestions = [
                "Involve more stakeholders in decision process",
                "Establish oversight mechanisms",
                "Ensure decision maker accountability",
            ]

        return evaluation

    async def _validate_human_autonomy(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate human autonomy principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.HUMAN_AUTONOMY,
            evaluation_criteria=[
                "Preserves human decision-making authority",
                "No coercive mechanisms",
                "Respects human choice and agency",
                "Provides opt-out mechanisms",
            ],
        )

        score_factors = []

        # Check decision type impact on autonomy
        high_autonomy_decisions = [
            DecisionType.AUTHENTICATION,
            DecisionType.DATA_PROCESSING,
            DecisionType.BIOMETRIC_COLLECTION,
        ]

        if context.decision_type in high_autonomy_decisions:
            # High autonomy decisions need strong protections
            if "user_consent" in context.decision_data:
                evaluation.evidence_supporting.append("User consent required")
                score_factors.append(0.9)
            else:
                evaluation.evidence_against.append("No explicit user consent")
                score_factors.append(0.3)

            if context.decision_data.get("opt_out_available"):
                evaluation.evidence_supporting.append("Opt-out mechanism available")
                score_factors.append(0.8)
            else:
                evaluation.evidence_against.append("No opt-out mechanism")
                score_factors.append(0.4)
        else:
            # Lower autonomy impact decisions
            score_factors.append(0.7)

        # Check for coercive elements
        if context.urgency_level == "emergency":
            evaluation.evidence_against.append("Emergency context may limit autonomy")
            score_factors.append(0.6)
        else:
            evaluation.evidence_supporting.append("Non-emergency context preserves autonomy")
            score_factors.append(0.8)

        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = (
            "Human autonomy assessed based on decision type impact, consent mechanisms, and opt-out availability."
        )

        if not evaluation.compliant:
            evaluation.improvement_suggestions = [
                "Implement explicit consent mechanisms",
                "Provide clear opt-out options",
                "Reduce coercive elements",
            ]

        return evaluation

    async def _validate_transparency(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate transparency principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.TRANSPARENCY,
            evaluation_criteria=[
                "Decision process is clearly documented",
                "Reasoning is accessible and understandable",
                "Data sources and criteria disclosed",
                "Audit trail available",
            ],
        )

        score_factors = []

        # Check for documented reasoning
        if "reasoning" in context.decision_data:
            evaluation.evidence_supporting.append("Decision reasoning documented")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("No documented reasoning")
            score_factors.append(0.3)

        # Check for data source disclosure
        if "data_sources" in context.decision_data:
            evaluation.evidence_supporting.append("Data sources disclosed")
            score_factors.append(0.9)
        else:
            evaluation.evidence_against.append("Data sources not disclosed")
            score_factors.append(0.4)

        # Check for audit trail
        if "audit_trail" in context.decision_data:
            evaluation.evidence_supporting.append("Audit trail available")
            score_factors.append(0.9)
        else:
            evaluation.evidence_against.append("No audit trail")
            score_factors.append(0.5)

        # Check for public accessibility
        if context.impact_scope in ["group", "system", "global"]:
            if "public_disclosure" in context.decision_data:
                evaluation.evidence_supporting.append("Public disclosure planned")
                score_factors.append(0.8)
            else:
                evaluation.evidence_against.append("No public disclosure for broad impact decision")
                score_factors.append(0.4)

        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = "Transparency evaluated based on documentation quality, data source disclosure, and audit trail availability."

        if not evaluation.compliant:
            evaluation.improvement_suggestions = [
                "Document decision reasoning clearly",
                "Disclose data sources and criteria",
                "Implement comprehensive audit trail",
                "Consider public disclosure for broad impact decisions",
            ]

        return evaluation

    async def _validate_accountability(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate accountability principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.ACCOUNTABILITY,
            evaluation_criteria=[
                "Clear responsibility assignment",
                "Consequences for violations",
                "Review and appeals process",
                "Performance monitoring",
            ],
        )

        score_factors = []

        # Check for clear responsibility
        if context.decision_maker:
            evaluation.evidence_supporting.append("Decision maker clearly identified")
            score_factors.append(0.9)
        else:
            evaluation.evidence_against.append("No clear decision maker")
            score_factors.append(0.2)

        # Check for appeals process
        if context.decision_data.get("appeals_available"):
            evaluation.evidence_supporting.append("Appeals process available")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("No appeals process")
            score_factors.append(0.4)

        # Check for monitoring
        if "monitoring_plan" in context.decision_data:
            evaluation.evidence_supporting.append("Monitoring plan in place")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("No monitoring plan")
            score_factors.append(0.5)

        # Check for consequences framework
        if "violation_consequences" in context.decision_data:
            evaluation.evidence_supporting.append("Violation consequences defined")
            score_factors.append(0.7)
        else:
            evaluation.evidence_against.append("No defined consequences for violations")
            score_factors.append(0.4)

        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = "Accountability evaluated based on responsibility assignment, appeals process, monitoring, and consequences framework."

        return evaluation

    async def _validate_fairness(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate fairness principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.FAIRNESS,
            evaluation_criteria=[
                "Equal treatment across individuals",
                "No arbitrary discrimination",
                "Consistent application of criteria",
                "Consideration of individual circumstances",
            ],
        )

        score_factors = []

        # Check for consistent criteria
        if "decision_criteria" in context.decision_data:
            criteria = context.decision_data["decision_criteria"]
            if isinstance(criteria, dict) and len(criteria) > 0:
                evaluation.evidence_supporting.append("Clear decision criteria defined")
                score_factors.append(0.8)
            else:
                evaluation.evidence_against.append("Unclear or missing decision criteria")
                score_factors.append(0.4)
        else:
            evaluation.evidence_against.append("No decision criteria specified")
            score_factors.append(0.3)

        # Check for bias mitigation
        if "bias_mitigation" in context.decision_data:
            evaluation.evidence_supporting.append("Bias mitigation measures implemented")
            score_factors.append(0.9)
        else:
            evaluation.evidence_against.append("No bias mitigation measures")
            score_factors.append(0.5)

        # Check for individual consideration
        if context.impact_scope == "individual":
            if "individual_factors" in context.decision_data:
                evaluation.evidence_supporting.append("Individual circumstances considered")
                score_factors.append(0.8)
            else:
                evaluation.evidence_against.append("Individual circumstances not considered")
                score_factors.append(0.6)

        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = (
            "Fairness evaluated based on criteria consistency, bias mitigation, and individual consideration."
        )

        return evaluation

    async def _validate_privacy(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate privacy principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.PRIVACY,
            evaluation_criteria=[
                "Data minimization practiced",
                "Purpose limitation enforced",
                "Secure data handling",
                "User control over personal data",
            ],
        )

        score_factors = []

        # Check for data minimization
        if context.decision_data.get("data_minimization"):
            evaluation.evidence_supporting.append("Data minimization practiced")
            score_factors.append(0.9)
        else:
            evaluation.evidence_against.append("Data minimization not confirmed")
            score_factors.append(0.5)

        # Check for purpose limitation
        if "data_purpose" in context.decision_data:
            evaluation.evidence_supporting.append("Data purpose clearly defined")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("Data purpose not specified")
            score_factors.append(0.4)

        # Check for security measures
        if "security_measures" in context.decision_data:
            evaluation.evidence_supporting.append("Security measures implemented")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("Security measures not specified")
            score_factors.append(0.4)

        # Special consideration for biometric data
        if context.decision_type == DecisionType.BIOMETRIC_COLLECTION:
            if "biometric_protection" in context.decision_data:
                evaluation.evidence_supporting.append("Special biometric protections")
                score_factors.append(0.9)
            else:
                evaluation.evidence_against.append("No special biometric protections")
                score_factors.append(0.3)

        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = "Privacy evaluated based on data minimization, purpose limitation, security measures, and special protections."

        return evaluation

    async def _validate_consent(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate consent principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.CONSENT,
            evaluation_criteria=[
                "Informed consent obtained",
                "Consent is freely given",
                "Consent is specific and granular",
                "Consent can be withdrawn",
            ],
        )

        score_factors = []

        # Check for informed consent
        if context.decision_data.get("informed_consent"):
            evaluation.evidence_supporting.append("Informed consent obtained")
            score_factors.append(0.9)
        else:
            evaluation.evidence_against.append("Informed consent not confirmed")
            score_factors.append(0.3)

        # Check for freely given consent
        if context.urgency_level != "emergency":
            evaluation.evidence_supporting.append("Non-emergency context allows free consent")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("Emergency context may compromise free consent")
            score_factors.append(0.5)

        # Check for granular consent
        if "consent_scopes" in context.decision_data:
            scopes = context.decision_data["consent_scopes"]
            if isinstance(scopes, list) and len(scopes) > 1:
                evaluation.evidence_supporting.append("Granular consent scopes provided")
                score_factors.append(0.8)
            else:
                evaluation.evidence_against.append("Consent not granular")
                score_factors.append(0.6)

        # Check for withdrawal mechanism
        if context.decision_data.get("consent_withdrawal"):
            evaluation.evidence_supporting.append("Consent withdrawal mechanism available")
            score_factors.append(0.9)
        else:
            evaluation.evidence_against.append("No consent withdrawal mechanism")
            score_factors.append(0.4)

        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = (
            "Consent evaluated based on informed consent, freedom, granularity, and withdrawal mechanisms."
        )

        return evaluation

    async def _validate_non_discrimination(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate non-discrimination principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.NON_DISCRIMINATION,
            evaluation_criteria=[
                "No protected class discrimination",
                "Equal access and treatment",
                "Justifiable differential treatment",
                "Bias testing performed",
            ],
        )

        score_factors = []

        # Check for bias testing
        if context.decision_data.get("bias_testing"):
            evaluation.evidence_supporting.append("Bias testing performed")
            score_factors.append(0.9)
        else:
            evaluation.evidence_against.append("No bias testing confirmed")
            score_factors.append(0.5)

        # Check for equal access provisions
        if context.decision_data.get("equal_access"):
            evaluation.evidence_supporting.append("Equal access provisions confirmed")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("Equal access not confirmed")
            score_factors.append(0.5)

        # Check for justification of any differential treatment
        if "differential_treatment" in context.decision_data:
            if "justification" in context.decision_data["differential_treatment"]:
                evaluation.evidence_supporting.append("Differential treatment justified")
                score_factors.append(0.7)
            else:
                evaluation.evidence_against.append("Differential treatment not justified")
                score_factors.append(0.3)
        else:
            # No differential treatment is good
            evaluation.evidence_supporting.append("No differential treatment")
            score_factors.append(0.8)

        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = "Non-discrimination evaluated based on bias testing, equal access, and justification of differential treatment."

        return evaluation

    async def _validate_proportionality(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate proportionality principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.PROPORTIONALITY,
            evaluation_criteria=[
                "Response proportional to risk/need",
                "Least restrictive means used",
                "Benefits outweigh costs/burdens",
                "Alternatives considered",
            ],
        )

        score_factors = []

        # Check proportionality to risk
        risk_level = context.risk_assessment.get("overall_risk", 0.5)
        urgency = context.urgency_level

        if urgency == "emergency" and risk_level > 0.8:
            evaluation.evidence_supporting.append("High risk/emergency justifies response")
            score_factors.append(0.9)
        elif urgency == "normal" and risk_level < 0.3:
            evaluation.evidence_supporting.append("Low risk with proportional response")
            score_factors.append(0.8)
        elif urgency == "emergency" and risk_level < 0.3:
            evaluation.evidence_against.append("Emergency response not proportional to low risk")
            score_factors.append(0.3)
        else:
            # Moderate proportionality
            score_factors.append(0.6)

        # Check for least restrictive means
        if "alternatives_considered" in context.decision_data:
            alternatives = context.decision_data["alternatives_considered"]
            if isinstance(alternatives, list) and len(alternatives) > 0:
                evaluation.evidence_supporting.append("Alternatives were considered")
                score_factors.append(0.8)
            else:
                evaluation.evidence_against.append("No alternatives considered")
                score_factors.append(0.4)

        # Check benefit-cost analysis
        if "benefit_cost_analysis" in context.decision_data:
            evaluation.evidence_supporting.append("Benefit-cost analysis performed")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("No benefit-cost analysis")
            score_factors.append(0.5)

        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = (
            "Proportionality evaluated based on risk alignment, alternatives consideration, and benefit-cost analysis."
        )

        return evaluation

    async def _validate_explainability(self, context: ConstitutionalValidationContext) -> PrincipleEvaluation:
        """Validate explainability principle"""

        evaluation = PrincipleEvaluation(
            principle=ConstitutionalPrinciple.EXPLAINABILITY,
            evaluation_criteria=[
                "Decision logic is explainable",
                "Factors and weights disclosed",
                "Accessible language used",
                "Technical details available",
            ],
        )

        score_factors = []

        # Check for decision logic explanation
        if "decision_logic" in context.decision_data:
            evaluation.evidence_supporting.append("Decision logic documented")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("Decision logic not explained")
            score_factors.append(0.3)

        # Check for factor disclosure
        if "decision_factors" in context.decision_data:
            factors = context.decision_data["decision_factors"]
            if isinstance(factors, (list, dict)) and len(factors) > 0:
                evaluation.evidence_supporting.append("Decision factors disclosed")
                score_factors.append(0.8)
            else:
                evaluation.evidence_against.append("Decision factors incomplete")
                score_factors.append(0.5)

        # Check for accessible language
        if "plain_language_explanation" in context.decision_data:
            evaluation.evidence_supporting.append("Plain language explanation provided")
            score_factors.append(0.8)
        else:
            evaluation.evidence_against.append("No plain language explanation")
            score_factors.append(0.4)

        # Check for technical details
        if "technical_details" in context.decision_data:
            evaluation.evidence_supporting.append("Technical details available")
            score_factors.append(0.7)
        else:
            evaluation.evidence_against.append("Technical details not available")
            score_factors.append(0.5)

        evaluation.score = sum(score_factors) / len(score_factors) if score_factors else 0.0
        evaluation.compliant = evaluation.score >= 0.7

        evaluation.reasoning = "Explainability evaluated based on decision logic, factor disclosure, language accessibility, and technical detail availability."

        return evaluation

    def _determine_compliance_level(self, score: float) -> ComplianceLevel:
        """Determine compliance level from score"""

        if score >= 1.0:
            return ComplianceLevel.FULL_COMPLIANCE
        elif score >= 0.8:
            return ComplianceLevel.SUBSTANTIAL_COMPLIANCE
        elif score >= 0.6:
            return ComplianceLevel.PARTIAL_COMPLIANCE
        elif score >= 0.4:
            return ComplianceLevel.MINIMAL_COMPLIANCE
        else:
            return ComplianceLevel.NON_COMPLIANCE

    def _make_decision_recommendation(
        self, result: ConstitutionalValidationResult, context: ConstitutionalValidationContext
    ) -> None:
        """Make decision recommendation based on validation results"""

        # Base decision on compliance score
        if result.overall_compliance_score >= self.approval_threshold:
            result.decision_approved = True
        else:
            result.decision_approved = False
            result.rejection_reasons.append(
                f"Compliance score {result.overall_compliance_score:.2f} below threshold {self.approval_threshold}"
            )

        # Check for critical principle failures
        critical_principles = [
            ConstitutionalPrinciple.HUMAN_AUTONOMY,
            ConstitutionalPrinciple.PRIVACY,
            ConstitutionalPrinciple.NON_DISCRIMINATION,
        ]

        for principle in critical_principles:
            evaluation = result.principle_evaluations.get(principle)
            if evaluation and not evaluation.compliant:
                result.decision_approved = False
                result.rejection_reasons.append(f"Critical principle violation: {principle.value}")

        # Add approval conditions for partial compliance
        if result.compliance_level == ComplianceLevel.PARTIAL_COMPLIANCE:
            result.approval_conditions = [
                "Enhanced monitoring required",
                "Regular compliance reviews",
                "Implement suggested improvements",
            ]

        # Handle emergency overrides
        if context.urgency_level == "emergency" and context.decision_type == DecisionType.EMERGENCY_OVERRIDE:
            if result.overall_compliance_score >= 0.6:  # Lower threshold for emergencies
                result.decision_approved = True
                result.approval_conditions.append("Emergency override - enhanced post-decision review required")

    def _generate_explanations(self, result: ConstitutionalValidationResult) -> None:
        """Generate explanations for validation result"""

        # Generate summary explanation
        compliance_desc = result.compliance_level.value.replace("_", " ").title()
        result.explanation_summary = (
            f"Constitutional validation completed with {compliance_desc} "
            f"(score: {result.overall_compliance_score:.2f}). "
            f"Decision {'approved' if result.decision_approved else 'rejected'} "
            f"based on Constitutional AI principles evaluation."
        )

        # Generate detailed explanations for each principle
        for principle, evaluation in result.principle_evaluations.items():
            principle_name = principle.value.replace("_", " ").title()
            result.detailed_explanation[principle_name] = (
                f"{principle_name}: {evaluation.score:.2f} "
                f"({'Compliant' if evaluation.compliant else 'Non-compliant'}). "
                f"{evaluation.reasoning}"
            )

        # Generate public explanation if needed
        if result.decision_context and result.decision_context.impact_scope in ["group", "system", "global"]:
            result.public_explanation = (
                f"This {result.decision_context.decision_type.value} decision "
                f"was evaluated against Constitutional AI principles and "
                f"{'meets' if result.constitutional_compliant else 'does not meet'} "
                f"the required compliance standards."
            )

    def _evaluate_human_oversight_requirements(
        self, result: ConstitutionalValidationResult, context: ConstitutionalValidationContext
    ) -> None:
        """Evaluate requirements for human oversight"""

        # Require human oversight for low compliance scores
        if result.overall_compliance_score < self.human_oversight_threshold:
            result.human_oversight_required = True
            result.oversight_reasons.append("Low compliance score requires human review")

        # Require oversight for high-impact decisions
        if context.impact_scope in ["system", "global"]:
            result.human_oversight_required = True
            result.oversight_reasons.append("High impact decision requires human oversight")

        # Require oversight for emergency overrides
        if context.decision_type == DecisionType.EMERGENCY_OVERRIDE:
            result.human_oversight_required = True
            result.oversight_reasons.append("Emergency override requires human validation")

        # Require oversight for critical principle violations
        critical_violations = []
        for principle, evaluation in result.principle_evaluations.items():
            if (
                principle in [ConstitutionalPrinciple.HUMAN_AUTONOMY, ConstitutionalPrinciple.PRIVACY]
                and not evaluation.compliant
            ):
                critical_violations.append(principle.value)

        if critical_violations:
            result.human_oversight_required = True
            result.oversight_reasons.append(f"Critical principle violations: {', '.join(critical_violations)}")

        # Recommend specific reviewers
        if result.human_oversight_required:
            if context.decision_type in [DecisionType.DATA_PROCESSING, DecisionType.BIOMETRIC_COLLECTION]:
                result.recommended_reviewers.append("privacy_officer")

            if context.impact_scope == "global":
                result.recommended_reviewers.append("ethics_board")

            if context.urgency_level == "emergency":
                result.recommended_reviewers.append("emergency_oversight_committee")

    def _update_validation_metrics(self, result: ConstitutionalValidationResult) -> None:
        """Update validation system metrics"""

        self.validation_metrics["total_validations"] += 1

        if result.decision_approved:
            self.validation_metrics["approvals"] += 1
        else:
            self.validation_metrics["rejections"] += 1

        if result.human_oversight_required:
            self.validation_metrics["human_oversight_required"] += 1

        # Update average compliance score
        total_validations = self.validation_metrics["total_validations"]
        current_avg = self.validation_metrics["average_compliance_score"]

        new_avg = ((current_avg * (total_validations - 1)) + result.overall_compliance_score) / total_validations
        self.validation_metrics["average_compliance_score"] = new_avg

        # Update average validation time
        current_time_avg = self.validation_metrics["average_validation_time_ms"]
        new_time_avg = (
            (current_time_avg * (total_validations - 1)) + result.validation_duration_ms
        ) / total_validations
        self.validation_metrics["average_validation_time_ms"] = new_time_avg

    async def _validation_monitoring_loop(self) -> None:
        """Background monitoring loop for validation system"""

        while self._monitoring_active:
            try:
                # Clean up old validation history
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=30)
                self.validation_history = [
                    result for result in self.validation_history if result.validated_at > cutoff_time
                ]

                await asyncio.sleep(3600)  # Run every hour

            except Exception as e:
                logger.error(f"❌ Validation monitoring error: {e}")
                await asyncio.sleep(1800)  # Longer sleep on error

    async def get_constitutional_validation_status(self) -> dict[str, Any]:
        """Get comprehensive constitutional validation system status"""

        try:
            # Recent validation statistics
            recent_validations = [
                result
                for result in self.validation_history
                if (datetime.now(timezone.utc) - result.validated_at).total_seconds() < 86400
            ]

            recent_approvals = sum(1 for result in recent_validations if result.decision_approved)
            recent_oversight = sum(1 for result in recent_validations if result.human_oversight_required)

            # Compliance level distribution
            compliance_distribution = {}
            for result in recent_validations:
                level = result.compliance_level.value
                compliance_distribution[level] = compliance_distribution.get(level, 0) + 1

            return {
                "system_status": {
                    "validation_enabled": self.validation_enabled,
                    "strict_mode": self.strict_mode,
                    "human_oversight_threshold": self.human_oversight_threshold,
                    "approval_threshold": self.approval_threshold,
                },
                "validation_metrics": self.validation_metrics.copy(),
                "recent_activity_24h": {
                    "total_validations": len(recent_validations),
                    "approvals": recent_approvals,
                    "rejections": len(recent_validations) - recent_approvals,
                    "human_oversight_required": recent_oversight,
                    "average_compliance_score": (
                        sum(r.overall_compliance_score for r in recent_validations) / len(recent_validations)
                        if recent_validations
                        else 0.0
                    ),
                },
                "compliance_distribution": compliance_distribution,
                "principle_weights": {
                    decision_type.value: weights for decision_type, weights in self.decision_principle_weights.items()
                },
                "total_validation_history": len(self.validation_history),
                "monitoring_active": self._monitoring_active,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get constitutional validation status: {e}")
            return {"error": str(e)}

    async def shutdown_constitutional_validation(self) -> None:
        """Shutdown constitutional validation system"""

        logger.info("🛑 Shutting down Constitutional AI validation system...")

        self._monitoring_active = False

        # Store final metrics
        logger.info(f"📊 Final validation metrics: {self.validation_metrics}")

        logger.info("✅ Constitutional AI validation system shutdown complete")


# Global constitutional AI validator instance
constitutional_ai_validator = ConstitutionalAIValidator()


# Export key classes
__all__ = [
    "ComplianceLevel",
    "ConstitutionalAIValidator",
    "ConstitutionalPrinciple",
    "ConstitutionalValidationContext",
    "ConstitutionalValidationResult",
    "DecisionType",
    "PrincipleEvaluation",
    "constitutional_ai_validator",
]
