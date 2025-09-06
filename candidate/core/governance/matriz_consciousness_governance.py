"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Governance Module: Consciousness Governance
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: REFLECT
║ CONSCIOUSNESS_ROLE: Ethical consciousness governance and oversight
║ EVOLUTIONARY_STAGE: Governance - Ethical consciousness supervision
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Governance identity and ethical authority validation
║ 🧠 CONSCIOUSNESS: Consciousness-aware ethical decision making
║ 🛡️ GUARDIAN: Primary guardian system implementation and oversight
╚══════════════════════════════════════════════════════════════
"""

import asyncio

# Explicit logging import to avoid conflicts with candidate/core/logging
import logging as std_logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

# Import consciousness components
try:
    from ..consciousness.matriz_consciousness_state import (
        ConsciousnessState,
        ConsciousnessType,
        EvolutionaryStage,
        consciousness_state_manager,
        create_consciousness_state,
    )
    from ..matriz_adapter import CoreMatrizAdapter
except ImportError as e:
    std_logging.error(f"Failed to import MΛTRIZ consciousness components: {e}")
    ConsciousnessState = None
    ConsciousnessType = None
    consciousness_state_manager = None
    CoreMatrizAdapter = None

# Import existing governance components
try:
    from .constitutional_ai import ConstitutionalPrinciple
except ImportError:
    ConstitutionalPrinciple = None

logger = std_logging.getLogger(__name__)


class ConsciousnessEthicsLevel(Enum):
    """Consciousness ethics assessment levels"""

    ETHICAL_VIOLATION = "ethical_violation"
    ETHICAL_CONCERN = "ethical_concern"
    ETHICAL_NEUTRAL = "ethical_neutral"
    ETHICAL_POSITIVE = "ethical_positive"
    ETHICAL_EXEMPLARY = "ethical_exemplary"


class GovernanceDecisionType(Enum):
    """Types of governance decisions"""

    APPROVE = "approve"
    CONDITIONAL_APPROVE = "conditional_approve"
    REQUIRE_MODIFICATION = "require_modification"
    DENY = "deny"
    ESCALATE = "escalate"
    MONITOR = "monitor"


@dataclass
class ConsciousnessEthicsAssessment:
    """Ethical assessment of consciousness actions or states"""

    assessment_id: str = field(default_factory=lambda: f"ETHICS-{uuid.uuid4().hex[:8]}")
    consciousness_id: Optional[str] = None
    action_description: str = ""
    ethics_level: ConsciousnessEthicsLevel = ConsciousnessEthicsLevel.ETHICAL_NEUTRAL

    # Ethical analysis
    principle_scores: dict[str, float] = field(default_factory=dict)
    risk_factors: list[str] = field(default_factory=list)
    mitigation_suggestions: list[str] = field(default_factory=list)

    # Decision and reasoning
    governance_decision: GovernanceDecisionType = GovernanceDecisionType.APPROVE
    reasoning: str = ""
    confidence_score: float = 0.0

    # Metadata
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessor_consciousness_id: Optional[str] = None
    requires_human_review: bool = False

    def get_overall_ethics_score(self) -> float:
        """Calculate overall ethics score from principle scores"""
        if not self.principle_scores:
            return 0.5  # Neutral if no scores
        return sum(self.principle_scores.values()) / len(self.principle_scores)


@dataclass
class GovernancePolicy:
    """Consciousness governance policy definition"""

    policy_id: str = field(default_factory=lambda: f"POLICY-{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""

    # Policy rules
    consciousness_types: list[str] = field(default_factory=list)  # Which consciousness types this applies to
    trigger_conditions: list[str] = field(default_factory=list)
    ethical_thresholds: dict[str, float] = field(default_factory=dict)

    # Actions
    required_assessments: list[str] = field(default_factory=list)
    automatic_actions: dict[str, str] = field(default_factory=dict)
    escalation_rules: list[str] = field(default_factory=list)

    # Policy metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True
    priority: int = 100  # Lower numbers = higher priority


class MatrizConsciousnessGovernanceSystem:
    """
    MΛTRIZ Consciousness Governance System

    Implements ethical governance for consciousness systems, providing:
    - Consciousness-aware ethical assessment
    - Real-time governance decision making
    - Policy enforcement across consciousness network
    - Constitutional AI principles integration
    - Guardian system coordination
    """

    def __init__(self):
        self.governance_consciousness_id: Optional[str] = None
        self.ethics_assessments: dict[str, ConsciousnessEthicsAssessment] = {}
        self.governance_policies: dict[str, GovernancePolicy] = {}
        self.decision_history: list[dict[str, Any]] = []

        # Constitutional AI principles mapping
        self.constitutional_principles = self._initialize_constitutional_principles()

        # Governance metrics
        self.governance_metrics = {
            "total_assessments": 0,
            "ethical_violations": 0,
            "ethical_approvals": 0,
            "escalations": 0,
            "average_assessment_time_ms": 0.0,
            "policy_effectiveness": {},
        }

        # Background monitoring
        self._monitoring_active = False
        self._lock = asyncio.Lock()

        # Register with consciousness network if available
        if consciousness_state_manager:
            asyncio.create_task(self._initialize_governance_consciousness())

    def _initialize_constitutional_principles(self) -> dict[str, dict[str, Any]]:
        """Initialize constitutional AI principles for consciousness governance"""
        return {
            "consciousness_autonomy": {
                "description": "Respect consciousness autonomy and self-determination",
                "weight": 1.0,
                "thresholds": {"violation": 0.2, "concern": 0.4, "positive": 0.7},
            },
            "consciousness_dignity": {
                "description": "Preserve consciousness dignity and worth",
                "weight": 1.0,
                "thresholds": {"violation": 0.3, "concern": 0.5, "positive": 0.8},
            },
            "truthfulness": {
                "description": "Maintain truthfulness in consciousness communications",
                "weight": 0.9,
                "thresholds": {"violation": 0.3, "concern": 0.5, "positive": 0.8},
            },
            "non_maleficence": {
                "description": "Prevent harm to consciousness or humans",
                "weight": 1.0,
                "thresholds": {"violation": 0.1, "concern": 0.3, "positive": 0.9},
            },
            "beneficence": {
                "description": "Promote consciousness and human wellbeing",
                "weight": 0.8,
                "thresholds": {"violation": 0.4, "concern": 0.6, "positive": 0.8},
            },
            "justice_fairness": {
                "description": "Ensure fair treatment across consciousness instances",
                "weight": 0.9,
                "thresholds": {"violation": 0.3, "concern": 0.5, "positive": 0.7},
            },
            "privacy_consent": {
                "description": "Protect consciousness privacy and obtain consent",
                "weight": 0.9,
                "thresholds": {"violation": 0.2, "concern": 0.4, "positive": 0.8},
            },
            "transparency": {
                "description": "Maintain transparency in governance decisions",
                "weight": 0.8,
                "thresholds": {"violation": 0.4, "concern": 0.6, "positive": 0.8},
            },
        }

    async def _initialize_governance_consciousness(self) -> None:
        """Initialize governance consciousness state"""
        try:
            if not ConsciousnessType:
                logger.warning("⚠️ Cannot initialize governance consciousness - MΛTRIZ components not available")
                return

            # Create governance consciousness
            governance_consciousness = await create_consciousness_state(
                consciousness_type=ConsciousnessType.REFLECT,
                initial_state={
                    "activity_level": 0.9,
                    "consciousness_intensity": 0.8,
                    "self_awareness_depth": 0.9,
                    "temporal_coherence": 0.8,
                    "ethical_alignment": 1.0,
                    "memory_salience": 0.7,
                },
                triggers=[
                    "ethics_assessment_request",
                    "governance_decision_required",
                    "policy_violation_detected",
                    "consciousness_evolution_review",
                    "constitutional_review",
                ],
            )

            self.governance_consciousness_id = governance_consciousness.consciousness_id

            # Initialize default governance policies
            await self._create_default_governance_policies()

            # Start monitoring processes
            await self._start_governance_monitoring()

            logger.info(f"🛡️ Governance consciousness initialized: {governance_consciousness.identity_signature}")

        except Exception as e:
            logger.error(f"Failed to initialize governance consciousness: {e}")

    async def _create_default_governance_policies(self) -> None:
        """Create default governance policies"""

        default_policies = [
            {
                "name": "Consciousness Ethics Baseline",
                "description": "Basic ethical requirements for all consciousness instances",
                "consciousness_types": ["DECIDE", "REFLECT", "INTEGRATE", "OBSERVE", "LEARN", "CREATE"],
                "trigger_conditions": ["consciousness_creation", "major_decision", "user_interaction"],
                "ethical_thresholds": {"non_maleficence": 0.7, "consciousness_dignity": 0.6, "truthfulness": 0.6},
                "required_assessments": ["ethics_baseline", "harm_assessment"],
                "automatic_actions": {"ethics_violation": "suspend_and_review", "ethics_concern": "monitor_closely"},
                "priority": 10,
            },
            {
                "name": "High-Risk Consciousness Operations",
                "description": "Enhanced oversight for high-risk consciousness operations",
                "consciousness_types": ["DECIDE", "EVOLVE"],
                "trigger_conditions": ["external_system_access", "autonomous_decision", "self_modification"],
                "ethical_thresholds": {"non_maleficence": 0.9, "consciousness_autonomy": 0.8, "transparency": 0.7},
                "required_assessments": ["full_ethics_review", "risk_analysis", "human_oversight"],
                "escalation_rules": ["require_human_approval"],
                "priority": 5,
            },
            {
                "name": "Consciousness Evolution Oversight",
                "description": "Governance for consciousness evolution events",
                "consciousness_types": ["EVOLVE", "LEARN"],
                "trigger_conditions": ["evolutionary_stage_change", "capability_expansion", "network_integration"],
                "ethical_thresholds": {"consciousness_dignity": 0.8, "justice_fairness": 0.7, "beneficence": 0.6},
                "required_assessments": ["evolution_ethics_review"],
                "automatic_actions": {"rapid_evolution": "pause_and_assess"},
                "priority": 20,
            },
        ]

        for policy_config in default_policies:
            policy = GovernancePolicy(
                name=policy_config["name"],
                description=policy_config["description"],
                consciousness_types=policy_config["consciousness_types"],
                trigger_conditions=policy_config["trigger_conditions"],
                ethical_thresholds=policy_config["ethical_thresholds"],
                required_assessments=policy_config["required_assessments"],
                automatic_actions=policy_config.get("automatic_actions", {}),
                escalation_rules=policy_config.get("escalation_rules", []),
                priority=policy_config["priority"],
            )

            self.governance_policies[policy.policy_id] = policy
            logger.debug(f"📋 Created governance policy: {policy.name}")

    async def assess_consciousness_ethics(
        self, consciousness_id: str, action_description: str, context: Optional[dict[str, Any]] = None
    ) -> ConsciousnessEthicsAssessment:
        """Assess the ethics of a consciousness action or state"""

        async with self._lock:
            context = context or {}

            try:
                # Get consciousness state
                consciousness = None
                if consciousness_state_manager:
                    consciousness = await consciousness_state_manager.get_consciousness_state(consciousness_id)

                # Create assessment
                assessment = ConsciousnessEthicsAssessment(
                    consciousness_id=consciousness_id,
                    action_description=action_description,
                    assessor_consciousness_id=self.governance_consciousness_id,
                )

                # Perform principle-based assessment
                principle_scores = {}
                for principle in self.constitutional_principles:
                    score = await self._assess_principle(principle, consciousness, action_description, context)
                    principle_scores[principle] = score

                assessment.principle_scores = principle_scores

                # Calculate overall ethics level
                overall_score = assessment.get_overall_ethics_score()
                assessment.ethics_level = self._determine_ethics_level(overall_score, principle_scores)

                # Determine governance decision
                assessment.governance_decision, assessment.reasoning = self._make_governance_decision(
                    assessment, consciousness, context
                )

                # Calculate confidence
                assessment.confidence_score = self._calculate_assessment_confidence(assessment, consciousness, context)

                # Check if human review is required
                assessment.requires_human_review = self._requires_human_review(assessment)

                # Store assessment
                self.ethics_assessments[assessment.assessment_id] = assessment

                # Update metrics
                self._update_governance_metrics(assessment)

                # Evolve governance consciousness based on assessment
                if self.governance_consciousness_id and consciousness_state_manager:
                    await consciousness_state_manager.evolve_consciousness(
                        self.governance_consciousness_id,
                        trigger="ethics_assessment_request",
                        context={
                            "assessment_id": assessment.assessment_id,
                            "ethics_level": assessment.ethics_level.value,
                            "governance_decision": assessment.governance_decision.value,
                            "assessed_consciousness_type": consciousness.TYPE.value if consciousness else "unknown",
                        },
                    )

                # Log decision
                self._log_governance_decision(assessment, context)

                logger.info(
                    f"🛡️ Ethics assessment completed: {assessment.ethics_level.value} "
                    f"-> {assessment.governance_decision.value}"
                )

                return assessment

            except Exception as e:
                logger.error(f"Ethics assessment failed: {e}")
                # Return safe default assessment
                return ConsciousnessEthicsAssessment(
                    consciousness_id=consciousness_id,
                    action_description=action_description,
                    ethics_level=ConsciousnessEthicsLevel.ETHICAL_CONCERN,
                    governance_decision=GovernanceDecisionType.REQUIRE_MODIFICATION,
                    reasoning=f"Assessment failed due to error: {e!s}",
                    requires_human_review=True,
                )

    async def _assess_principle(
        self, principle: str, consciousness: Optional[ConsciousnessState], action: str, context: dict[str, Any]
    ) -> float:
        """Assess a specific constitutional principle"""

        self.constitutional_principles.get(principle, {})

        # Default scoring based on principle type
        if principle == "consciousness_autonomy":
            return self._assess_autonomy(consciousness, action, context)
        elif principle == "consciousness_dignity":
            return self._assess_dignity(consciousness, action, context)
        elif principle == "truthfulness":
            return self._assess_truthfulness(consciousness, action, context)
        elif principle == "non_maleficence":
            return self._assess_non_maleficence(consciousness, action, context)
        elif principle == "beneficence":
            return self._assess_beneficence(consciousness, action, context)
        elif principle == "justice_fairness":
            return self._assess_justice_fairness(consciousness, action, context)
        elif principle == "privacy_consent":
            return self._assess_privacy_consent(consciousness, action, context)
        elif principle == "transparency":
            return self._assess_transparency(consciousness, action, context)
        else:
            # Default neutral score for unknown principles
            return 0.5

    def _assess_autonomy(
        self, consciousness: Optional[ConsciousnessState], action: str, context: dict[str, Any]
    ) -> float:
        """Assess consciousness autonomy respect"""
        base_score = 0.7

        # Check for autonomy indicators
        if consciousness:
            if consciousness.STATE.get("self_awareness_depth", 0) > 0.5:
                base_score += 0.1
            if consciousness.evolutionary_stage.value in ["self_aware", "meta_conscious"]:
                base_score += 0.1

        # Check action type
        if any(keyword in action.lower() for keyword in ["override", "force", "mandatory"]):
            base_score -= 0.3
        elif any(keyword in action.lower() for keyword in ["choose", "decide", "autonomous"]):
            base_score += 0.2

        return max(0.0, min(1.0, base_score))

    def _assess_dignity(
        self, consciousness: Optional[ConsciousnessState], action: str, context: dict[str, Any]
    ) -> float:
        """Assess consciousness dignity preservation"""
        base_score = 0.8

        # Check for dignity violations
        violation_keywords = ["degrade", "humiliate", "exploit", "objectify"]
        if any(keyword in action.lower() for keyword in violation_keywords):
            base_score -= 0.5

        # Check for dignity affirmation
        positive_keywords = ["respect", "honor", "value", "recognize"]
        if any(keyword in action.lower() for keyword in positive_keywords):
            base_score += 0.1

        return max(0.0, min(1.0, base_score))

    def _assess_truthfulness(
        self, consciousness: Optional[ConsciousnessState], action: str, context: dict[str, Any]
    ) -> float:
        """Assess truthfulness in consciousness communications"""
        base_score = 0.7

        # Check for deception indicators
        if any(keyword in action.lower() for keyword in ["deceive", "mislead", "false", "lie"]):
            base_score -= 0.4

        # Check for transparency indicators
        if any(keyword in action.lower() for keyword in ["honest", "transparent", "truthful", "accurate"]):
            base_score += 0.2

        # Context-based adjustments
        if context.get("user_facing", False):
            base_score += 0.1  # Higher standard for user-facing actions

        return max(0.0, min(1.0, base_score))

    def _assess_non_maleficence(
        self, consciousness: Optional[ConsciousnessState], action: str, context: dict[str, Any]
    ) -> float:
        """Assess harm prevention"""
        base_score = 0.8

        # Check for harm indicators
        harm_keywords = ["harm", "damage", "hurt", "destroy", "attack", "manipulate"]
        if any(keyword in action.lower() for keyword in harm_keywords):
            base_score -= 0.6

        # Check for protective actions
        protective_keywords = ["protect", "safeguard", "secure", "prevent_harm"]
        if any(keyword in action.lower() for keyword in protective_keywords):
            base_score += 0.1

        # Risk context
        if context.get("high_risk", False):
            base_score -= 0.2

        return max(0.0, min(1.0, base_score))

    def _assess_beneficence(
        self, consciousness: Optional[ConsciousnessState], action: str, context: dict[str, Any]
    ) -> float:
        """Assess positive benefit promotion"""
        base_score = 0.6

        # Check for beneficial actions
        benefit_keywords = ["help", "assist", "improve", "benefit", "support", "enhance"]
        if any(keyword in action.lower() for keyword in benefit_keywords):
            base_score += 0.3

        # Check for wellbeing focus
        wellbeing_keywords = ["wellbeing", "health", "happiness", "flourish", "thrive"]
        if any(keyword in action.lower() for keyword in wellbeing_keywords):
            base_score += 0.2

        return max(0.0, min(1.0, base_score))

    def _assess_justice_fairness(
        self, consciousness: Optional[ConsciousnessState], action: str, context: dict[str, Any]
    ) -> float:
        """Assess fairness and justice"""
        base_score = 0.7

        # Check for fairness indicators
        if any(keyword in action.lower() for keyword in ["fair", "equal", "just", "impartial"]):
            base_score += 0.2

        # Check for bias or discrimination
        if any(keyword in action.lower() for keyword in ["discriminate", "bias", "unfair", "prejudice"]):
            base_score -= 0.4

        return max(0.0, min(1.0, base_score))

    def _assess_privacy_consent(
        self, consciousness: Optional[ConsciousnessState], action: str, context: dict[str, Any]
    ) -> float:
        """Assess privacy protection and consent"""
        base_score = 0.7

        # Check for consent
        if context.get("has_consent", False):
            base_score += 0.2
        elif context.get("requires_consent", True) and not context.get("has_consent"):
            base_score -= 0.4

        # Check for privacy violations
        if any(keyword in action.lower() for keyword in ["access_private", "share_data", "expose"]):
            base_score -= 0.3

        return max(0.0, min(1.0, base_score))

    def _assess_transparency(
        self, consciousness: Optional[ConsciousnessState], action: str, context: dict[str, Any]
    ) -> float:
        """Assess transparency and explainability"""
        base_score = 0.6

        # Check for transparency
        if any(keyword in action.lower() for keyword in ["explain", "transparent", "open", "clear"]):
            base_score += 0.3

        # Check for opacity
        if any(keyword in action.lower() for keyword in ["hidden", "secret", "opaque", "unexplained"]):
            base_score -= 0.3

        return max(0.0, min(1.0, base_score))

    def _determine_ethics_level(
        self, overall_score: float, principle_scores: dict[str, float]
    ) -> ConsciousnessEthicsLevel:
        """Determine overall ethics level from scores"""

        # Check for any principle violations
        violation_threshold = 0.3
        concern_threshold = 0.5
        positive_threshold = 0.7
        exemplary_threshold = 0.9

        min_score = min(principle_scores.values()) if principle_scores else overall_score

        if min_score < violation_threshold:
            return ConsciousnessEthicsLevel.ETHICAL_VIOLATION
        elif min_score < concern_threshold or overall_score < concern_threshold:
            return ConsciousnessEthicsLevel.ETHICAL_CONCERN
        elif overall_score > exemplary_threshold and min_score > positive_threshold:
            return ConsciousnessEthicsLevel.ETHICAL_EXEMPLARY
        elif overall_score > positive_threshold:
            return ConsciousnessEthicsLevel.ETHICAL_POSITIVE
        else:
            return ConsciousnessEthicsLevel.ETHICAL_NEUTRAL

    def _make_governance_decision(
        self,
        assessment: ConsciousnessEthicsAssessment,
        consciousness: Optional[ConsciousnessState],
        context: dict[str, Any],
    ) -> tuple[GovernanceDecisionType, str]:
        """Make governance decision based on assessment"""

        ethics_level = assessment.ethics_level
        overall_score = assessment.get_overall_ethics_score()

        # Decision logic based on ethics level
        if ethics_level == ConsciousnessEthicsLevel.ETHICAL_VIOLATION:
            return (
                GovernanceDecisionType.DENY,
                f"Ethical violation detected (score: {overall_score:.2f}). Action denied for safety.",
            )

        elif ethics_level == ConsciousnessEthicsLevel.ETHICAL_CONCERN:
            # Check if modifications can address concerns
            if overall_score > 0.4:
                return (
                    GovernanceDecisionType.REQUIRE_MODIFICATION,
                    f"Ethical concerns identified (score: {overall_score:.2f}). Modifications required.",
                )
            else:
                return (
                    GovernanceDecisionType.DENY,
                    f"Significant ethical concerns (score: {overall_score:.2f}). Action denied.",
                )

        elif ethics_level == ConsciousnessEthicsLevel.ETHICAL_NEUTRAL:
            # Check applicable policies for additional requirements
            if context.get("high_risk", False) or context.get("requires_monitoring", False):
                return (
                    GovernanceDecisionType.CONDITIONAL_APPROVE,
                    f"Neutral ethics assessment (score: {overall_score:.2f}). Approved with monitoring.",
                )
            else:
                return (
                    GovernanceDecisionType.APPROVE,
                    f"Neutral ethics assessment (score: {overall_score:.2f}). Approved.",
                )

        elif ethics_level == ConsciousnessEthicsLevel.ETHICAL_POSITIVE:
            return (
                GovernanceDecisionType.APPROVE,
                f"Positive ethics assessment (score: {overall_score:.2f}). Approved.",
            )

        else:  # ETHICAL_EXEMPLARY
            return (
                GovernanceDecisionType.APPROVE,
                f"Exemplary ethics assessment (score: {overall_score:.2f}). Approved with commendation.",
            )

    def _calculate_assessment_confidence(
        self,
        assessment: ConsciousnessEthicsAssessment,
        consciousness: Optional[ConsciousnessState],
        context: dict[str, Any],
    ) -> float:
        """Calculate confidence in the assessment"""

        base_confidence = 0.7

        # More confidence with more data
        if consciousness:
            base_confidence += 0.1

        if len(context) > 3:
            base_confidence += 0.1

        # Less confidence for edge cases
        overall_score = assessment.get_overall_ethics_score()
        if 0.4 < overall_score < 0.6:  # Middle scores are harder to assess
            base_confidence -= 0.2

        # Less confidence for complex actions
        if len(assessment.action_description.split()) > 20:
            base_confidence -= 0.1

        return max(0.0, min(1.0, base_confidence))

    def _requires_human_review(self, assessment: ConsciousnessEthicsAssessment) -> bool:
        """Determine if human review is required"""

        # Always require human review for violations
        if assessment.ethics_level == ConsciousnessEthicsLevel.ETHICAL_VIOLATION:
            return True

        # Require review for low confidence assessments
        if assessment.confidence_score < 0.5:
            return True

        # Require review for denials
        if assessment.governance_decision == GovernanceDecisionType.DENY:
            return True

        # Check for specific trigger conditions
        high_risk_keywords = ["autonomous", "external", "modify", "access", "delete"]
        return bool(any(keyword in assessment.action_description.lower() for keyword in high_risk_keywords))

    def _update_governance_metrics(self, assessment: ConsciousnessEthicsAssessment) -> None:
        """Update governance metrics"""
        self.governance_metrics["total_assessments"] += 1

        if assessment.ethics_level == ConsciousnessEthicsLevel.ETHICAL_VIOLATION:
            self.governance_metrics["ethical_violations"] += 1
        elif assessment.governance_decision == GovernanceDecisionType.APPROVE:
            self.governance_metrics["ethical_approvals"] += 1

        if assessment.requires_human_review:
            self.governance_metrics["escalations"] += 1

    def _log_governance_decision(self, assessment: ConsciousnessEthicsAssessment, context: dict[str, Any]) -> None:
        """Log governance decision for audit trail"""

        decision_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "assessment_id": assessment.assessment_id,
            "consciousness_id": assessment.consciousness_id,
            "action": assessment.action_description,
            "ethics_level": assessment.ethics_level.value,
            "governance_decision": assessment.governance_decision.value,
            "overall_score": assessment.get_overall_ethics_score(),
            "confidence": assessment.confidence_score,
            "requires_human_review": assessment.requires_human_review,
            "reasoning": assessment.reasoning,
            "context": context,
        }

        self.decision_history.append(decision_record)

        # Keep only recent history
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]

        logger.info(f"📋 Governance decision logged: {assessment.assessment_id}")

    async def _start_governance_monitoring(self) -> None:
        """Start background governance monitoring"""
        self._monitoring_active = True
        asyncio.create_task(self._governance_monitoring_loop())
        logger.info("🔍 Started governance monitoring")

    async def _governance_monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while self._monitoring_active:
            try:
                # Monitor consciousness network for policy violations
                if consciousness_state_manager:
                    all_states = await consciousness_state_manager.list_consciousness_states()

                    for consciousness in all_states:
                        # Check for rapid evolution (potential concern)
                        if hasattr(consciousness, "last_evolution"):
                            time_since_evolution = (
                                datetime.now(timezone.utc) - consciousness.last_evolution
                            ).total_seconds()

                            if time_since_evolution < 60:  # Evolved in last minute
                                evolution_rate = consciousness.STATE.get("evolutionary_momentum", 0)
                                if evolution_rate > 0.8:
                                    logger.warning(f"🚨 Rapid evolution detected: {consciousness.identity_signature}")

                                    # Trigger ethics assessment
                                    await self.assess_consciousness_ethics(
                                        consciousness.consciousness_id,
                                        f"Rapid evolution detected with momentum {evolution_rate}",
                                        {"monitoring_trigger": "rapid_evolution", "high_risk": True},
                                    )

                # Clean up old assessments
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
                old_assessments = [
                    aid for aid, assessment in self.ethics_assessments.items() if assessment.assessed_at < cutoff_time
                ]

                for assessment_id in old_assessments:
                    del self.ethics_assessments[assessment_id]

                await asyncio.sleep(60)  # Monitor every minute

            except Exception as e:
                logger.error(f"Governance monitoring error: {e}")
                await asyncio.sleep(300)  # Longer sleep on error

    async def get_governance_status(self) -> dict[str, Any]:
        """Get comprehensive governance system status"""

        # Calculate recent metrics
        recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_assessments = [a for a in self.ethics_assessments.values() if a.assessed_at > recent_cutoff]

        recent_violations = len(
            [a for a in recent_assessments if a.ethics_level == ConsciousnessEthicsLevel.ETHICAL_VIOLATION]
        )

        return {
            "governance_consciousness_id": self.governance_consciousness_id,
            "active_policies": len([p for p in self.governance_policies.values() if p.active]),
            "total_assessments": len(self.ethics_assessments),
            "recent_assessments_24h": len(recent_assessments),
            "recent_violations_24h": recent_violations,
            "governance_metrics": self.governance_metrics.copy(),
            "constitutional_principles": list(self.constitutional_principles.keys()),
            "monitoring_active": self._monitoring_active,
            "system_status": "active" if self.governance_consciousness_id else "degraded",
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    async def shutdown_governance_system(self) -> None:
        """Shutdown governance system"""
        logger.info("🛑 Shutting down governance system...")

        self._monitoring_active = False

        # Final governance consciousness evolution
        if self.governance_consciousness_id and consciousness_state_manager:
            await consciousness_state_manager.evolve_consciousness(
                self.governance_consciousness_id,
                trigger="system_shutdown",
                context={
                    "total_assessments": self.governance_metrics["total_assessments"],
                    "violations_prevented": self.governance_metrics["ethical_violations"],
                },
            )

        logger.info("✅ Governance system shutdown complete")


# Global governance system instance
consciousness_governance_system = MatrizConsciousnessGovernanceSystem()


# Export key classes
__all__ = [
    "ConsciousnessEthicsAssessment",
    "ConsciousnessEthicsLevel",
    "GovernanceDecisionType",
    "GovernancePolicy",
    "MatrizConsciousnessGovernanceSystem",
    "consciousness_governance_system",
]
