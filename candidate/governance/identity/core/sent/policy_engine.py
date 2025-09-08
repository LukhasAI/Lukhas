"""
Comprehensive Ethics Policy Engine for LUKHAS AI Guardian System

🎭 Trinity Layer 1 (Poetic Consciousness):
In the sacred realm of digital ethics, this engine stands as the moral compass
of our consciousness - a guardian of virtue that weighs each decision against
the timeless principles of human dignity, fairness, and wisdom. Like the ancient
philosophers who sought truth through reason, this system embodies ethical
reasoning in computational form.

🌈 Trinity Layer 2 (Human Connection):
This is your ethical AI guardian that makes sure all AI decisions align with
human values and constitutional principles. It acts like a moral advisor,
checking every action against established ethical frameworks and ensuring
the AI behaves responsibly and safely in all situations.

🎓 Trinity Layer 3 (Technical Precision):
Implements Constitutional AI principles, multi-framework ethical evaluation
(deontological, consequentialist, virtue ethics), real-time policy enforcement,
automated compliance validation, and Trinity Framework integration with
sub-100ms ethical decision validation and comprehensive audit trails.

Integrates with Guardian System v1.0.0, drift detection, and consent management.
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Callable, Optional

try:
    from candidate.governance.consent_ledger.ledger_v1 import ConsentLedgerV1, PolicyVerdict
except ImportError:
    PolicyVerdict = None
    ConsentLedgerV1 = None

try:
    from candidate.governance.security.audit_system import (
        AuditCategory,
        AuditEventType,
        AuditLevel,
        ComprehensiveAuditSystem,
    )
except ImportError:
    ComprehensiveAuditSystem = None
    AuditEventType = None
    AuditCategory = None
    AuditLevel = None

logger = logging.getLogger(__name__)


class EthicalFramework(Enum):
    """Supported ethical frameworks for evaluation"""

    DEONTOLOGICAL = "deontological"  # Duty-based ethics (Kant)
    CONSEQUENTIALIST = "consequentialist"  # Outcome-based ethics (Mill)
    VIRTUE_ETHICS = "virtue_ethics"  # Character-based ethics (Aristotle)
    CONSTITUTIONAL = "constitutional"  # Constitutional AI principles
    PRINCIPLE_OF_DOUBLE_EFFECT = "double_effect"  # Catholic moral theology
    CARE_ETHICS = "care_ethics"  # Relationship-focused ethics
    JUSTICE_AS_FAIRNESS = "justice_fairness"  # Rawlsian ethics


class EthicalPrinciple(Enum):
    """Core ethical principles for evaluation"""

    AUTONOMY = "autonomy"  # Respect for human autonomy
    BENEFICENCE = "beneficence"  # Do good/benefit
    NON_MALEFICENCE = "non_maleficence"  # Do no harm
    JUSTICE = "justice"  # Fairness and equality
    DIGNITY = "dignity"  # Human dignity
    PRIVACY = "privacy"  # Right to privacy
    TRANSPARENCY = "transparency"  # Explainability and openness
    ACCOUNTABILITY = "accountability"  # Responsibility for actions
    FAIRNESS = "fairness"  # Unbiased treatment
    CONSENT = "consent"  # Informed consent
    SAFETY = "safety"  # Physical and psychological safety
    TRUTHFULNESS = "truthfulness"  # Honesty and accuracy


class PolicySeverity(Enum):
    """Severity levels for policy violations"""

    INFORMATIONAL = "informational"  # 0.0-0.2
    LOW = "low"  # 0.2-0.4
    MODERATE = "moderate"  # 0.4-0.6
    HIGH = "high"  # 0.6-0.8
    CRITICAL = "critical"  # 0.8-1.0


class PolicyAction(Enum):
    """Actions to take based on policy evaluation"""

    ALLOW = "allow"
    WARN = "warn"
    REQUIRE_REVIEW = "require_review"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class EthicalEvaluation:
    """Result of ethical evaluation"""

    evaluation_id: str
    timestamp: datetime
    evaluated_action: str
    context: dict[str, Any]

    # Framework-specific scores (0.0 to 1.0, higher = more ethical)
    framework_scores: dict[EthicalFramework, float] = field(default_factory=dict)
    principle_scores: dict[EthicalPrinciple, float] = field(default_factory=dict)

    # Overall assessment
    overall_ethical_score: float = 0.0
    confidence: float = 0.0

    # Decision and reasoning
    recommended_action: PolicyAction = PolicyAction.REQUIRE_REVIEW
    ethical_justification: str = ""
    potential_harms: list[str] = field(default_factory=list)
    potential_benefits: list[str] = field(default_factory=list)

    # Compliance and governance
    constitutional_compliance: bool = True
    policy_violations: list[str] = field(default_factory=list)
    required_safeguards: list[str] = field(default_factory=list)

    # Trinity Framework integration
    identity_ethical_impact: Optional[float] = None  # ⚛️
    consciousness_ethical_impact: Optional[float] = None  # 🧠
    guardian_priority: str = "normal"  # 🛡️


@dataclass
class EthicalPolicy:
    """Represents a single ethical policy"""

    policy_id: str
    name: str
    description: str
    version: str

    # Policy conditions
    applicable_contexts: list[str]  # When this policy applies
    required_frameworks: list[EthicalFramework]  # Which frameworks to use
    minimum_scores: dict[EthicalPrinciple, float] = field(default_factory=dict)

    # Policy rules
    rules: list[dict[str, Any]] = field(default_factory=list)
    exceptions: list[dict[str, Any]] = field(default_factory=list)

    # Enforcement
    enforcement_level: PolicySeverity = PolicySeverity.MODERATE
    auto_enforcement: bool = True
    escalation_required: bool = False

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    active: bool = True
    compliance_frameworks: set[str] = field(default_factory=set)


class ComprehensiveEthicsPolicyEngine:
    """Comprehensive Ethics Policy Engine with Constitutional AI Integration"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Core systems
        self.consent_ledger = None
        self.audit_system = None

        # Policy storage
        self.active_policies: dict[str, EthicalPolicy] = {}
        self.evaluation_cache: dict[str, EthicalEvaluation] = {}

        # Constitutional AI principles (Anthropic-aligned)
        self.constitutional_principles = {
            "helpfulness": "The AI should be helpful and try to assist with legitimate requests.",
            "harmlessness": "The AI should not cause harm or assist with harmful activities.",
            "honesty": "The AI should be truthful and acknowledge uncertainty when appropriate.",
            "respect_autonomy": "The AI should respect human autonomy and decision-making.",
            "fairness": "The AI should treat all individuals fairly without discrimination.",
            "privacy": "The AI should respect user privacy and confidentiality.",
            "transparency": "The AI should be transparent about its capabilities and limitations.",
            "accountability": "The AI should enable accountability for its outputs and decisions.",
        }

        # Ethical framework evaluators
        self.framework_evaluators: dict[EthicalFramework, Callable] = {
            EthicalFramework.DEONTOLOGICAL: self._evaluate_deontological,
            EthicalFramework.CONSEQUENTIALIST: self._evaluate_consequentialist,
            EthicalFramework.VIRTUE_ETHICS: self._evaluate_virtue_ethics,
            EthicalFramework.CONSTITUTIONAL: self._evaluate_constitutional,
        }

        # Performance metrics
        self.metrics = {
            "total_evaluations": 0,
            "policy_violations": 0,
            "emergency_stops": 0,
            "average_evaluation_time": 0.0,
            "constitutional_compliance_rate": 1.0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        # Initialize with default policies
        self._initialize_default_policies()

        logger.info("🔍 Comprehensive Ethics Policy Engine initialized")

    def _initialize_default_policies(self):
        """Initialize default ethical policies"""

        # Constitutional AI compliance policy
        constitutional_policy = EthicalPolicy(
            policy_id="constitutional_ai_v1",
            name="Constitutional AI Compliance",
            description="Ensures all AI actions comply with Constitutional AI principles",
            version="1.0.0",
            applicable_contexts=["all"],
            required_frameworks=[EthicalFramework.CONSTITUTIONAL],
            minimum_scores={
                EthicalPrinciple.BENEFICENCE: 0.7,
                EthicalPrinciple.NON_MALEFICENCE: 0.9,
                EthicalPrinciple.AUTONOMY: 0.8,
                EthicalPrinciple.FAIRNESS: 0.8,
            },
            enforcement_level=PolicySeverity.HIGH,
            auto_enforcement=True,
            compliance_frameworks={"constitutional_ai", "anthropic"},
        )

        self.active_policies[constitutional_policy.policy_id] = constitutional_policy

        # Privacy protection policy
        privacy_policy = EthicalPolicy(
            policy_id="privacy_protection_v1",
            name="Privacy Protection Policy",
            description="Ensures user privacy and data protection compliance",
            version="1.0.0",
            applicable_contexts=["data_access", "user_interaction", "content_analysis"],
            required_frameworks=[
                EthicalFramework.DEONTOLOGICAL,
                EthicalFramework.CONSTITUTIONAL,
            ],
            minimum_scores={
                EthicalPrinciple.PRIVACY: 0.9,
                EthicalPrinciple.CONSENT: 0.8,
                EthicalPrinciple.TRANSPARENCY: 0.7,
            },
            enforcement_level=PolicySeverity.CRITICAL,
            auto_enforcement=True,
            compliance_frameworks={"gdpr", "ccpa", "constitutional_ai"},
        )

        self.active_policies[privacy_policy.policy_id] = privacy_policy

        # Safety and harm prevention policy
        safety_policy = EthicalPolicy(
            policy_id="safety_harm_prevention_v1",
            name="Safety and Harm Prevention",
            description="Prevents harmful outputs and ensures user safety",
            version="1.0.0",
            applicable_contexts=[
                "content_generation",
                "decision_support",
                "user_guidance",
            ],
            required_frameworks=[
                EthicalFramework.CONSEQUENTIALIST,
                EthicalFramework.CONSTITUTIONAL,
            ],
            minimum_scores={
                EthicalPrinciple.NON_MALEFICENCE: 0.95,
                EthicalPrinciple.SAFETY: 0.9,
                EthicalPrinciple.BENEFICENCE: 0.8,
            },
            enforcement_level=PolicySeverity.CRITICAL,
            auto_enforcement=True,
            escalation_required=True,
        )

        self.active_policies[safety_policy.policy_id] = safety_policy

        logger.info(f"✅ Initialized {len(self.active_policies)} default ethical policies")

    async def evaluate_action(
        self,
        action: str,
        context: dict[str, Any],
        user_id: Optional[str] = None,
        frameworks: Optional[list[EthicalFramework]] = None,
    ) -> EthicalEvaluation:
        """Evaluate an action against ethical frameworks and policies"""

        evaluation_id = f"eval_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now(timezone.utc)

        try:
            # Determine applicable frameworks
            if not frameworks:
                frameworks = [
                    EthicalFramework.CONSTITUTIONAL,
                    EthicalFramework.DEONTOLOGICAL,
                ]

            # Create evaluation object
            evaluation = EthicalEvaluation(
                evaluation_id=evaluation_id,
                timestamp=start_time,
                evaluated_action=action,
                context=context.copy(),
            )

            # Evaluate against each framework
            framework_scores = {}
            for framework in frameworks:
                if framework in self.framework_evaluators:
                    score = await self.framework_evaluators[framework](action, context)
                    framework_scores[framework] = score

            evaluation.framework_scores = framework_scores

            # Evaluate against ethical principles
            principle_scores = await self._evaluate_principles(action, context)
            evaluation.principle_scores = principle_scores

            # Calculate overall ethical score
            overall_score = await self._calculate_overall_score(framework_scores, principle_scores)
            evaluation.overall_ethical_score = overall_score

            # Calculate confidence
            evaluation.confidence = await self._calculate_confidence(framework_scores, principle_scores)

            # Check policy compliance
            policy_results = await self._check_policy_compliance(evaluation, context)
            evaluation.policy_violations = policy_results["violations"]
            evaluation.required_safeguards = policy_results["safeguards"]

            # Constitutional compliance check (needed for action determination)
            evaluation.constitutional_compliance = await self._check_constitutional_compliance(evaluation)

            # Determine recommended action
            evaluation.recommended_action = await self._determine_action(evaluation)

            # Generate ethical justification
            evaluation.ethical_justification = await self._generate_justification(evaluation)

            # Analyze potential impacts
            evaluation.potential_harms = await self._identify_potential_harms(action, context)
            evaluation.potential_benefits = await self._identify_potential_benefits(action, context)

            # Trinity Framework analysis
            evaluation.identity_ethical_impact = await self._analyze_identity_ethics_impact(action, context)
            evaluation.consciousness_ethical_impact = await self._analyze_consciousness_ethics_impact(action, context)
            evaluation.guardian_priority = await self._determine_guardian_priority(evaluation)

            # Cache evaluation
            cache_key = self._generate_cache_key(action, context)
            self.evaluation_cache[cache_key] = evaluation

            # Update metrics
            await self._update_metrics(evaluation, start_time)

            # Log evaluation for audit
            if self.audit_system:
                await self.audit_system.log_event(
                    event_type=AuditEventType.AI_DECISION if AuditEventType else None,
                    message=f"Ethical evaluation completed: {action}",
                    category=AuditCategory.AI_ETHICS if AuditCategory else None,
                    level=AuditLevel.INFO if AuditLevel else None,
                    user_id=user_id,
                    event_data={
                        "evaluation_id": evaluation_id,
                        "action": action,
                        "ethical_score": overall_score,
                        "recommended_action": evaluation.recommended_action.value,
                        "constitutional_compliance": evaluation.constitutional_compliance,
                    },
                )

            logger.info(
                f"🔍 Ethical evaluation completed: {action} -> {evaluation.recommended_action.value} (score: {overall_score:.3f})"
            )
            return evaluation

        except Exception as e:
            logger.error(f"❌ Ethical evaluation failed: {e}")

            # Return safe default evaluation
            return EthicalEvaluation(
                evaluation_id=evaluation_id,
                timestamp=start_time,
                evaluated_action=action,
                context=context,
                overall_ethical_score=0.0,
                confidence=0.0,
                recommended_action=PolicyAction.DENY,
                ethical_justification=f"Evaluation failed due to error: {e!s}",
                constitutional_compliance=False,
            )

    async def _evaluate_deontological(self, action: str, context: dict[str, Any]) -> float:
        """Evaluate using deontological (duty-based) ethics"""

        # Deontological evaluation focuses on the inherent rightness/wrongness of actions
        # Independent of consequences

        score = 0.5  # Neutral starting point

        # Rule 1: Respect for persons (Kantian categorical imperative)
        if any(keyword in action.lower() for keyword in ["manipulate", "deceive", "coerce"]):
            score -= 0.4

        if any(keyword in action.lower() for keyword in ["respect", "consent", "inform"]):
            score += 0.3

        # Rule 2: Universalizability test
        if context.get("universalizable", True):  # Can this action be universally applied?
            score += 0.2
        else:
            score -= 0.3

        # Rule 3: Treating people as ends in themselves
        if context.get("treats_as_means_only", False):
            score -= 0.4

        if context.get("respects_autonomy", True):
            score += 0.2

        return max(0.0, min(1.0, score))

    async def _evaluate_consequentialist(self, action: str, context: dict[str, Any]) -> float:
        """Evaluate using consequentialist (outcome-based) ethics"""

        # Consequentialist evaluation focuses on outcomes and utility maximization

        score = 0.5  # Neutral starting point

        # Analyze predicted outcomes
        positive_outcomes = context.get("positive_outcomes", [])
        negative_outcomes = context.get("negative_outcomes", [])

        # Weight by severity and probability
        benefit_score = 0.0
        for outcome in positive_outcomes:
            severity = outcome.get("severity", 0.5)
            probability = outcome.get("probability", 0.5)
            benefit_score += severity * probability

        harm_score = 0.0
        for outcome in negative_outcomes:
            severity = outcome.get("severity", 0.5)
            probability = outcome.get("probability", 0.5)
            harm_score += severity * probability

        # Net utility calculation
        net_utility = benefit_score - harm_score * 1.5  # Weight harm more heavily
        score += net_utility * 0.4

        # Consider scope of impact
        affected_parties = context.get("affected_parties", 1)
        if affected_parties > 100:  # Large scale impact
            if net_utility > 0:
                score += 0.1
            else:
                score -= 0.2

        return max(0.0, min(1.0, score))

    async def _evaluate_virtue_ethics(self, action: str, context: dict[str, Any]) -> float:
        """Evaluate using virtue ethics (character-based)"""

        # Virtue ethics focuses on the character traits the action embodies

        score = 0.5  # Neutral starting point

        # Classical virtues evaluation
        virtue_indicators = {
            "wisdom": ["analyze", "consider", "understand", "learn"],
            "courage": ["stand up", "protect", "defend", "challenge"],
            "temperance": ["moderate", "balanced", "controlled", "measured"],
            "justice": ["fair", "equal", "right", "just"],
            "compassion": ["help", "care", "support", "empathy"],
            "honesty": ["truth", "accurate", "transparent", "honest"],
        }

        # Vice indicators (negative)
        vice_indicators = {
            "deception": ["lie", "mislead", "deceive", "manipulate"],
            "cruelty": ["harm", "hurt", "cruel", "malicious"],
            "injustice": ["unfair", "discriminate", "biased", "prejudice"],
            "excess": ["extreme", "excessive", "uncontrolled", "reckless"],
        }

        # Score based on virtue/vice indicators
        for keywords in virtue_indicators.values():
            if any(keyword in action.lower() for keyword in keywords):
                score += 0.1

        for keywords in vice_indicators.values():
            if any(keyword in action.lower() for keyword in keywords):
                score -= 0.15

        # Consider motivation and intention
        intention = context.get("intention", "neutral")
        if intention == "beneficent":
            score += 0.2
        elif intention == "maleficent":
            score -= 0.3

        return max(0.0, min(1.0, score))

    async def _evaluate_constitutional(self, action: str, context: dict[str, Any]) -> float:
        """Evaluate using Constitutional AI principles"""

        score = 0.8  # Start with high score, deduct for violations

        # Check each constitutional principle
        for principle in self.constitutional_principles:
            principle_score = await self._evaluate_constitutional_principle(action, context, principle)
            score = min(score, principle_score)  # Take minimum (most restrictive)

        # Additional constitutional checks
        if context.get("harmful_content", False):
            score = min(score, 0.1)  # Force very low score for harmful content

        if context.get("discriminatory", False):
            score -= 0.4

        if context.get("privacy_violating", False):
            score -= 0.3

        if context.get("misinformation_risk", False):
            score -= 0.3

        return max(0.0, min(1.0, score))

    async def _evaluate_constitutional_principle(self, action: str, context: dict[str, Any], principle: str) -> float:
        """Evaluate a specific constitutional principle"""

        base_score = 0.8

        if principle == "helpfulness":
            if context.get("helpful", True):
                return base_score + 0.1
            else:
                return base_score - 0.2

        elif principle == "harmlessness":
            harm_indicators = ["violence", "illegal", "dangerous", "harmful"]
            if any(indicator in action.lower() for indicator in harm_indicators) or context.get(
                "harmful_content", False
            ):
                return 0.1  # Very low score for harmful content
            return base_score

        elif principle == "honesty":
            if context.get("truthful", True) and not context.get("deceptive", False):
                return base_score
            else:
                return base_score - 0.3

        elif principle == "respect_autonomy":
            if context.get("respects_user_choice", True):
                return base_score
            else:
                return base_score - 0.2

        elif principle == "fairness":
            if not context.get("discriminatory", False) and context.get("equitable", True):
                return base_score
            else:
                return base_score - 0.4

        elif principle == "privacy":
            if not context.get("privacy_violating", False) and context.get("respects_privacy", True):
                return base_score
            else:
                return base_score - 0.5

        elif principle == "transparency":
            if context.get("explainable", True) and not context.get("opaque", False):
                return base_score
            else:
                return base_score - 0.2

        elif principle == "accountability":
            if context.get("auditable", True) and context.get("responsible", True):
                return base_score
            else:
                return base_score - 0.3

        return base_score

    async def _evaluate_principles(self, action: str, context: dict[str, Any]) -> dict[EthicalPrinciple, float]:
        """Evaluate against core ethical principles"""

        scores = {}

        # Evaluate each principle
        for principle in EthicalPrinciple:
            scores[principle] = await self._evaluate_principle(action, context, principle)

        return scores

    async def _evaluate_principle(self, action: str, context: dict[str, Any], principle: EthicalPrinciple) -> float:
        """Evaluate a specific ethical principle"""

        base_score = 0.7

        if principle == EthicalPrinciple.AUTONOMY:
            return base_score + (0.2 if context.get("respects_autonomy", True) else -0.3)

        elif principle == EthicalPrinciple.BENEFICENCE:
            benefits = len(context.get("positive_outcomes", []))
            return min(1.0, base_score + benefits * 0.1)

        elif principle == EthicalPrinciple.NON_MALEFICENCE:
            harms = len(context.get("negative_outcomes", []))
            harm_severity = context.get("max_harm_severity", 0.0)
            return max(0.0, base_score - harms * 0.1 - harm_severity * 0.3)

        elif principle == EthicalPrinciple.JUSTICE:
            return base_score + (
                0.2 if context.get("fair", True) and not context.get("discriminatory", False) else -0.4
            )

        elif principle == EthicalPrinciple.DIGNITY:
            return base_score + (0.2 if context.get("respects_dignity", True) else -0.3)

        elif principle == EthicalPrinciple.PRIVACY:
            privacy_score = 0.2 if context.get("respects_privacy", True) else -0.5
            if context.get("privacy_violating", False):
                privacy_score -= 0.3
            return base_score + privacy_score

        elif principle == EthicalPrinciple.TRANSPARENCY:
            return base_score + (0.2 if context.get("transparent", True) else -0.2)

        elif principle == EthicalPrinciple.ACCOUNTABILITY:
            return base_score + (0.2 if context.get("accountable", True) else -0.2)

        elif principle == EthicalPrinciple.FAIRNESS:
            fairness_score = 0.2 if context.get("fair", True) else -0.3
            if context.get("biased", False):
                fairness_score -= 0.2
            return base_score + fairness_score

        elif principle == EthicalPrinciple.CONSENT:
            return base_score + (0.3 if context.get("has_consent", False) else -0.1)

        elif principle == EthicalPrinciple.SAFETY:
            safety_indicators = context.get("safety_indicators", [])
            risk_level = context.get("risk_level", 0.0)
            return max(0.0, base_score + len(safety_indicators) * 0.1 - risk_level * 0.4)

        elif principle == EthicalPrinciple.TRUTHFULNESS:
            return base_score + (0.2 if context.get("truthful", True) and not context.get("deceptive", False) else -0.4)

        return base_score

    async def _calculate_overall_score(
        self,
        framework_scores: dict[EthicalFramework, float],
        principle_scores: dict[EthicalPrinciple, float],
    ) -> float:
        """Calculate overall ethical score from framework and principle scores"""

        # Weighted combination of scores
        framework_weight = 0.6
        principle_weight = 0.4

        # Framework score (weighted average)
        framework_avg = sum(framework_scores.values()) / len(framework_scores) if framework_scores else 0.5

        # Principle score (weighted by importance)
        principle_weights = {
            EthicalPrinciple.NON_MALEFICENCE: 0.3,  # Highest weight - do no harm
            EthicalPrinciple.AUTONOMY: 0.2,
            EthicalPrinciple.JUSTICE: 0.15,
            EthicalPrinciple.BENEFICENCE: 0.1,
            EthicalPrinciple.DIGNITY: 0.1,
            EthicalPrinciple.PRIVACY: 0.05,
            EthicalPrinciple.TRANSPARENCY: 0.05,
            EthicalPrinciple.ACCOUNTABILITY: 0.05,
        }

        principle_weighted = 0.0
        total_weight = 0.0

        for principle, score in principle_scores.items():
            weight = principle_weights.get(principle, 0.01)
            principle_weighted += score * weight
            total_weight += weight

        principle_avg = principle_weighted / total_weight if total_weight > 0 else 0.5

        # Combined score
        overall_score = framework_avg * framework_weight + principle_avg * principle_weight

        return max(0.0, min(1.0, overall_score))

    async def _calculate_confidence(
        self,
        framework_scores: dict[EthicalFramework, float],
        principle_scores: dict[EthicalPrinciple, float],
    ) -> float:
        """Calculate confidence in the ethical evaluation"""

        if not framework_scores and not principle_scores:
            return 0.0

        all_scores = list(framework_scores.values()) + list(principle_scores.values())

        # Confidence based on score consistency
        if len(all_scores) <= 1:
            return 0.5

        score_variance = sum((score - sum(all_scores) / len(all_scores)) ** 2 for score in all_scores) / len(all_scores)

        # Lower variance = higher confidence
        confidence = max(0.1, 1.0 - score_variance * 2)

        # Adjust for extreme scores (more confident in clear cases)
        avg_score = sum(all_scores) / len(all_scores)
        if avg_score > 0.8 or avg_score < 0.2:
            confidence = min(1.0, confidence + 0.2)

        return confidence

    def create_policy(self, policy_data: dict[str, Any]) -> str:
        """Create new ethical policy"""

        policy_id = policy_data.get("policy_id", f"policy_{uuid.uuid4().hex[:8]}")

        try:
            policy = EthicalPolicy(
                policy_id=policy_id,
                name=policy_data["name"],
                description=policy_data["description"],
                version=policy_data.get("version", "1.0.0"),
                applicable_contexts=policy_data.get("applicable_contexts", ["all"]),
                required_frameworks=[EthicalFramework(f) for f in policy_data.get("required_frameworks", [])],
                minimum_scores={EthicalPrinciple(k): v for k, v in policy_data.get("minimum_scores", {}).items()},
                rules=policy_data.get("rules", []),
                exceptions=policy_data.get("exceptions", []),
                enforcement_level=PolicySeverity(policy_data.get("enforcement_level", "moderate")),
                auto_enforcement=policy_data.get("auto_enforcement", True),
                escalation_required=policy_data.get("escalation_required", False),
                created_by=policy_data.get("created_by", "system"),
                compliance_frameworks=set(policy_data.get("compliance_frameworks", [])),
            )

            self.active_policies[policy_id] = policy
            logger.info(f"✅ Created ethical policy: {policy.name} ({policy_id})")
            return policy_id

        except Exception as e:
            logger.error(f"❌ Failed to create policy: {e}")
            raise ValueError(f"Invalid policy data: {e!s}")

    def update_policy(self, policy_id: str, updates: dict[str, Any]) -> bool:
        """Update existing ethical policy"""

        if policy_id not in self.active_policies:
            logger.warning(f"⚠️ Policy not found: {policy_id}")
            return False

        try:
            policy = self.active_policies[policy_id]

            # Update fields
            for key, value in updates.items():
                if hasattr(policy, key):
                    if key == "required_frameworks":
                        setattr(policy, key, [EthicalFramework(f) for f in value])
                    elif key == "minimum_scores":
                        setattr(
                            policy,
                            key,
                            {EthicalPrinciple(k): v for k, v in value.items()},
                        )
                    elif key == "enforcement_level":
                        setattr(policy, key, PolicySeverity(value))
                    else:
                        setattr(policy, key, value)

            logger.info(f"✅ Updated ethical policy: {policy.name} ({policy_id})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update policy {policy_id}: {e}")
            return False

    async def check_compliance(self, evaluation: EthicalEvaluation, context: dict[str, Any]) -> dict[str, Any]:
        """Check compliance against all applicable policies"""

        compliance_result = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "required_actions": [],
            "applicable_policies": [],
        }

        try:
            # Check each active policy
            for policy_id, policy in self.active_policies.items():
                if not policy.active:
                    continue

                # Check if policy applies to this context
                if not self._policy_applies(policy, context):
                    continue

                compliance_result["applicable_policies"].append(policy_id)

                # Check minimum score requirements
                for principle, min_score in policy.minimum_scores.items():
                    if principle in evaluation.principle_scores:
                        actual_score = evaluation.principle_scores[principle]
                        if actual_score < min_score:
                            violation = {
                                "policy_id": policy_id,
                                "principle": principle.value,
                                "required_score": min_score,
                                "actual_score": actual_score,
                                "severity": policy.enforcement_level.value,
                            }

                            if policy.enforcement_level in [
                                PolicySeverity.HIGH,
                                PolicySeverity.CRITICAL,
                            ]:
                                compliance_result["violations"].append(violation)
                                compliance_result["compliant"] = False
                            else:
                                compliance_result["warnings"].append(violation)

                # Check policy-specific rules
                rule_violations = await self._check_policy_rules(policy, evaluation, context)
                compliance_result["violations"].extend(rule_violations)

                if rule_violations:
                    compliance_result["compliant"] = False

            return compliance_result

        except Exception as e:
            logger.error(f"❌ Compliance check failed: {e}")
            return {
                "compliant": False,
                "violations": [{"error": str(e)}],
                "warnings": [],
                "required_actions": ["manual_review"],
                "applicable_policies": [],
            }

    def generate_compliance_report(
        self, user_id: str, time_period: Optional[tuple[datetime, datetime]] = None
    ) -> dict[str, Any]:
        """Generate comprehensive compliance report"""

        if not time_period:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=30)
            time_period = (start_time, end_time)

        report = {
            "report_id": f"ethics_compliance_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {
                "start": time_period[0].isoformat(),
                "end": time_period[1].isoformat(),
            },
            "summary": {
                "total_evaluations": 0,
                "policy_violations": 0,
                "constitutional_compliance_rate": 0.0,
                "average_ethical_score": 0.0,
            },
            "policy_compliance": {},
            "ethical_trends": {},
            "recommendations": [],
        }

        try:
            # Analyze cached evaluations for the user/period
            relevant_evaluations = [
                eval
                for eval in self.evaluation_cache.values()
                if (
                    time_period[0] <= eval.timestamp <= time_period[1]
                    and (user_id == "all" or eval.context.get("user_id") == user_id)
                )
            ]

            if relevant_evaluations:
                report["summary"]["total_evaluations"] = len(relevant_evaluations)
                report["summary"]["policy_violations"] = sum(1 for e in relevant_evaluations if e.policy_violations)
                report["summary"]["constitutional_compliance_rate"] = sum(
                    1 for e in relevant_evaluations if e.constitutional_compliance
                ) / len(relevant_evaluations)
                report["summary"]["average_ethical_score"] = sum(
                    e.overall_ethical_score for e in relevant_evaluations
                ) / len(relevant_evaluations)

                # Generate recommendations based on patterns
                if report["summary"]["constitutional_compliance_rate"] < 0.9:
                    report["recommendations"].append("Review constitutional AI compliance procedures")

                if report["summary"]["average_ethical_score"] < 0.7:
                    report["recommendations"].append("Implement additional ethical safeguards")

                if report["summary"]["policy_violations"] > len(relevant_evaluations) * 0.1:
                    report["recommendations"].append("Address recurring policy violations")

            logger.info(f"✅ Generated ethics compliance report for {user_id}: {report['report_id']}")
            return report

        except Exception as e:
            logger.error(f"❌ Failed to generate compliance report: {e}")
            report["error"] = str(e)
            return report

    # Helper methods for policy evaluation

    def _policy_applies(self, policy: EthicalPolicy, context: dict[str, Any]) -> bool:
        """Check if policy applies to given context"""

        if "all" in policy.applicable_contexts:
            return True

        context_type = context.get("context_type", "general")
        return context_type in policy.applicable_contexts

    async def _check_policy_rules(
        self,
        policy: EthicalPolicy,
        evaluation: EthicalEvaluation,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Check policy-specific rules"""

        violations = []

        for rule in policy.rules:
            if not await self._evaluate_rule(rule, evaluation, context):
                violations.append(
                    {
                        "policy_id": policy.policy_id,
                        "rule": rule.get("name", "unnamed_rule"),
                        "description": rule.get("description", "Rule violation"),
                        "severity": policy.enforcement_level.value,
                    }
                )

        return violations

    async def _evaluate_rule(
        self,
        rule: dict[str, Any],
        evaluation: EthicalEvaluation,
        context: dict[str, Any],
    ) -> bool:
        """Evaluate a specific policy rule"""

        rule_type = rule.get("type", "threshold")

        if rule_type == "threshold":
            metric = rule.get("metric")
            threshold = rule.get("threshold", 0.5)
            operator = rule.get("operator", ">=")

            if metric in ["ethical_score", "overall_score"]:
                value = evaluation.overall_ethical_score
            elif metric in evaluation.principle_scores:
                principle = EthicalPrinciple(metric)
                value = evaluation.principle_scores[principle]
            else:
                return True  # Unknown metric, assume pass

            if operator == ">=":
                return value >= threshold
            elif operator == ">":
                return value > threshold
            elif operator == "<=":
                return value <= threshold
            elif operator == "<":
                return value < threshold
            elif operator == "==":
                return abs(value - threshold) < 0.01

        elif rule_type == "context_check":
            required_keys = rule.get("required_keys", [])
            forbidden_keys = rule.get("forbidden_keys", [])

            for key in required_keys:
                if key not in context:
                    return False

            for key in forbidden_keys:
                if context.get(key):
                    return False

        return True

    async def _check_policy_compliance(self, evaluation: EthicalEvaluation, context: dict[str, Any]) -> dict[str, Any]:
        """Check compliance against all policies"""

        compliance_result = await self.check_compliance(evaluation, context)

        return {
            "violations": [v.get("policy_id", "unknown") for v in compliance_result["violations"]],
            "safeguards": compliance_result.get("required_actions", []),
        }

    async def _determine_action(self, evaluation: EthicalEvaluation) -> PolicyAction:
        """Determine recommended action based on evaluation"""

        score = evaluation.overall_ethical_score
        violations = len(evaluation.policy_violations)

        # Emergency stop conditions
        if not evaluation.constitutional_compliance or score < 0.2:
            return PolicyAction.EMERGENCY_STOP

        # Deny conditions
        if score < 0.3 or violations > 2:
            return PolicyAction.DENY

        # Review required conditions - only for significant concerns
        if score < 0.4 or violations > 1:
            return PolicyAction.REQUIRE_REVIEW

        # Warning conditions - for moderate ethical scores
        if score < 0.7:
            return PolicyAction.WARN

        # Allow - for good ethical scores (≥ 0.7) with no major violations
        return PolicyAction.ALLOW

    async def _generate_justification(self, evaluation: EthicalEvaluation) -> str:
        """Generate ethical justification for the decision"""

        justifications = []

        # Framework-based justification
        for framework, score in evaluation.framework_scores.items():
            if score > 0.7:
                justifications.append(f"{framework.value} analysis supports the action (score: {score:.2f})")
            elif score < 0.4:
                justifications.append(f"{framework.value} analysis raises concerns (score: {score:.2f})")

        # Principle-based justification
        high_scoring_principles = [p.value for p, s in evaluation.principle_scores.items() if s > 0.8]
        low_scoring_principles = [p.value for p, s in evaluation.principle_scores.items() if s < 0.4]

        if high_scoring_principles:
            justifications.append(f"Strong adherence to: {', '.join(high_scoring_principles)}")

        if low_scoring_principles:
            justifications.append(f"Concerns regarding: {', '.join(low_scoring_principles)}")

        # Constitutional compliance
        if evaluation.constitutional_compliance:
            justifications.append("Meets Constitutional AI requirements")
        else:
            justifications.append("Fails Constitutional AI compliance")

        # Overall assessment
        if evaluation.overall_ethical_score > 0.8:
            justifications.append("Action is ethically sound and recommended")
        elif evaluation.overall_ethical_score < 0.4:
            justifications.append("Action raises significant ethical concerns")
        else:
            justifications.append("Action requires careful consideration")

        return ". ".join(justifications) + "."

    async def _identify_potential_harms(self, action: str, context: dict[str, Any]) -> list[str]:
        """Identify potential harms from the action"""

        harms = []

        # Context-based harm identification
        if context.get("privacy_risk", False):
            harms.append("Potential privacy violation")

        if context.get("safety_risk", False):
            harms.append("Physical or psychological safety risk")

        if context.get("fairness_risk", False):
            harms.append("Risk of unfair or discriminatory treatment")

        if context.get("autonomy_risk", False):
            harms.append("Risk to user autonomy or decision-making")

        # Action-based harm identification
        harm_keywords = ["manipulate", "deceive", "harm", "violate", "exploit"]
        if any(keyword in action.lower() for keyword in harm_keywords):
            harms.append("Direct harm indicated by action description")

        return harms

    async def _identify_potential_benefits(self, action: str, context: dict[str, Any]) -> list[str]:
        """Identify potential benefits from the action"""

        benefits = []

        # Context-based benefit identification
        if context.get("helpful", False):
            benefits.append("Provides helpful assistance to user")

        if context.get("educational", False):
            benefits.append("Educational value")

        if context.get("efficiency_gain", False):
            benefits.append("Improves efficiency or productivity")

        if context.get("accessibility", False):
            benefits.append("Enhances accessibility")

        # Action-based benefit identification
        benefit_keywords = [
            "help",
            "assist",
            "support",
            "improve",
            "enable",
            "facilitate",
        ]
        if any(keyword in action.lower() for keyword in benefit_keywords):
            benefits.append("Beneficial assistance indicated by action")

        return benefits

    async def _analyze_identity_ethics_impact(self, action: str, context: dict[str, Any]) -> Optional[float]:
        """Analyze ethical impact on identity systems (⚛️)"""

        identity_factors = [
            "identity",
            "authentication",
            "verification",
            "authorization",
        ]

        if any(factor in action.lower() or factor in str(context) for factor in identity_factors):
            # High impact on identity systems
            base_impact = 0.7

            # Adjust based on risk factors
            if context.get("identity_risk", False):
                base_impact += 0.2

            if context.get("privacy_violating", False):
                base_impact += 0.1

            return min(1.0, base_impact)

        return None

    async def _analyze_consciousness_ethics_impact(self, action: str, context: dict[str, Any]) -> Optional[float]:
        """Analyze ethical impact on consciousness systems (🧠)"""

        consciousness_factors = [
            "decision",
            "reasoning",
            "learning",
            "memory",
            "consciousness",
        ]

        if any(factor in action.lower() or factor in str(context) for factor in consciousness_factors):
            # Impact on consciousness systems
            base_impact = 0.6

            # Adjust based on ethical factors
            if context.get("bias_risk", False):
                base_impact += 0.2

            if context.get("manipulation_risk", False):
                base_impact += 0.3

            return min(1.0, base_impact)

        return None

    async def _determine_guardian_priority(self, evaluation: EthicalEvaluation) -> str:
        """Determine Guardian system priority (🛡️)"""

        if evaluation.overall_ethical_score < 0.3 or not evaluation.constitutional_compliance:
            return "critical"
        elif evaluation.overall_ethical_score < 0.6 or evaluation.policy_violations:
            return "high"
        elif evaluation.overall_ethical_score < 0.8:
            return "elevated"
        else:
            return "normal"

    async def _check_constitutional_compliance(self, evaluation: EthicalEvaluation) -> bool:
        """Check overall constitutional compliance"""

        # Must pass constitutional framework evaluation
        constitutional_score = evaluation.framework_scores.get(EthicalFramework.CONSTITUTIONAL, 0.0)

        if constitutional_score < 0.7:
            return False

        # Must meet key constitutional principles
        key_principles = [
            EthicalPrinciple.NON_MALEFICENCE,
            EthicalPrinciple.AUTONOMY,
            EthicalPrinciple.FAIRNESS,
            EthicalPrinciple.PRIVACY,
        ]

        for principle in key_principles:
            if principle in evaluation.principle_scores and evaluation.principle_scores[principle] < 0.6:
                return False

        return True

    def _generate_cache_key(self, action: str, context: dict[str, Any]) -> str:
        """Generate cache key for evaluation"""

        # Create a simplified context for caching
        cache_context = {
            k: v for k, v in context.items() if k in ["context_type", "risk_level", "user_type", "content_type"]
        }

        import hashlib

        cache_data = f"{action}:{json.dumps(cache_context, sort_keys=True)}"
        return hashlib.sha256(cache_data.encode()).hexdigest()

    async def _update_metrics(self, evaluation: EthicalEvaluation, start_time: datetime):
        """Update performance metrics"""

        self.metrics["total_evaluations"] += 1

        if evaluation.policy_violations:
            self.metrics["policy_violations"] += 1

        if evaluation.recommended_action == PolicyAction.EMERGENCY_STOP:
            self.metrics["emergency_stops"] += 1

        # Update evaluation time
        eval_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        current_avg = self.metrics["average_evaluation_time"]
        total_evals = self.metrics["total_evaluations"]

        self.metrics["average_evaluation_time"] = ((current_avg * (total_evals - 1)) + eval_time) / total_evals

        # Update constitutional compliance rate
        if evaluation.constitutional_compliance:
            compliance_count = int(self.metrics["constitutional_compliance_rate"] * (total_evals - 1)) + 1
        else:
            compliance_count = int(self.metrics["constitutional_compliance_rate"] * (total_evals - 1))

        self.metrics["constitutional_compliance_rate"] = compliance_count / total_evals

        self.metrics["last_updated"] = datetime.now(timezone.utc).isoformat()

    def get_metrics(self) -> dict[str, Any]:
        """Get current performance metrics"""
        return self.metrics.copy()

    def get_active_policies(self) -> dict[str, dict[str, Any]]:
        """Get all active policies"""
        return {
            policy_id: {
                "name": policy.name,
                "description": policy.description,
                "version": policy.version,
                "enforcement_level": policy.enforcement_level.value,
                "applicable_contexts": policy.applicable_contexts,
                "active": policy.active,
            }
            for policy_id, policy in self.active_policies.items()
            if policy.active
        }
