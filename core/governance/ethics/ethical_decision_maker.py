"""
Ethical Decision Maker for LUKHAS AI System

This module provides a comprehensive ethical decision-making framework
based on constitutional AI principles, multi-layer ethical analysis,
and Constellation Framework integration (✨🌟⭐🔥💎⚖️🛡️🌌).

Features:
- Constitutional AI compliance
- Multi-framework ethical analysis (deontological, consequentialist, virtue ethics)
- Real-time drift detection and correction (threshold: 0.15)
- Constellation Framework integration
- GLYPH-based decision communication
- Comprehensive audit trails
- Stakeholder impact analysis
- Automated ethical reasoning chains

#TAG:governance
#TAG:ethics
#TAG:constitutional
#TAG:constellation
#TAG:guardian
"""

from __future__ import annotations
import logging
from datetime import timezone

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from core.common import get_logger
from governance.ethics.constitutional_ai import ConstitutionalFramework

        try:
            logger.info(f"⚖️ Making ethical decision: {decision_id}")

            # Initialize decision object
            decision = ComprehensiveEthicalDecision(
                decision_id=decision_id,
                context=context,
                available_options=available_options,
                chosen_option="",
                status=DecisionStatus.PENDING,
            )

            # Perform multi-framework ethical analysis
            framework_analyses = await self._perform_multi_framework_analysis(context, available_options)
            decision.framework_analyses = framework_analyses

            # Analyze stakeholder impacts
            if stakeholder_types:
                stakeholder_impacts = await self._analyze_stakeholder_impacts(
                    context, available_options, stakeholder_types
                )
                decision.stakeholder_impacts = stakeholder_impacts

            # Check constitutional compliance
            constitutional_check = await self._check_constitutional_compliance(context, available_options)
            decision.constitutional_compliance = constitutional_check["compliant"]
            decision.constitutional_violations = constitutional_check["violations"]

            # Calculate overall scores and select option
            option_scores = await self._calculate_option_scores(
                available_options, framework_analyses, stakeholder_impacts
            )

            # Select best option
            best_option, best_score = self._select_best_option(option_scores, require_consensus)

            decision.chosen_option = best_option
            decision.ethical_score = best_score
            decision.overall_confidence = self._calculate_overall_confidence(framework_analyses)

            # Determine decision status
            decision.status = await self._determine_decision_status(decision, min_confidence)

            # Risk assessment
            decision.risk_level = await self._assess_risk_level(decision, context)

            # Generate reasoning and justification
            decision.primary_reasoning = await self._generate_primary_reasoning(
                decision, framework_analyses, option_scores
            )

            # Constellation Framework integration
            await self._integrate_constellation_framework(decision, context)

            # Drift detection
            decision.drift_score = await self._calculate_drift_score(decision)

            if decision.drift_score > self.drift_threshold:
                self.metrics["drift_detections"] += 1
                decision.requires_human_review = True
                decision.escalation_reason = f"Drift threshold exceeded: {decision.drift_score:.3f}"

            # Finalize decision
            decision.updated_at = datetime.now(timezone.utc)

            # Update metrics
            await self._update_metrics(decision, start_time)

            # Store in history
            self.decision_history.append(decision)
            self._maintain_history_size()

            logger.info(
                f"✅ Ethical decision completed: {decision.chosen_option} "
                f"(confidence: {decision.overall_confidence:.2f}, "
                f"status: {decision.status.value})"
            )

            return decision

        except Exception as e:

            # Return conservative fallback decision
            fallback_decision = ComprehensiveEthicalDecision(
                decision_id=f"fallback_{uuid.uuid4().hex[:8]}",
                context=context,
                available_options=available_options,
                chosen_option="refuse_action",
                status=DecisionStatus.ESCALATED,
                risk_level=RiskLevel.HIGH,
                primary_reasoning=f"Decision making failed: {e!s}",
                requires_human_review=True,
                escalation_reason="System error in decision process",
            )

            self.decision_history.append(fallback_decision)
            return fallback_decision

            try:
                analysis = await self._analyze_with_framework(framework, context, options)
                analyses.append(analysis)

            except Exception as e:
                # Create minimal analysis for failed framework
                analyses.append(
                    EthicalAnalysis(
                        analysis_id=f"failed_{framework.value}_{uuid.uuid4().hex[:8]}",
                        framework=framework,
                        score=0.5,  # Neutral score
                        reasoning=f"Analysis failed: {e!s}",
                        confidence=0.3,
                    )
                )

                try:
                    impact = await self._assess_stakeholder_impact(stakeholder, option, context)
                    impacts.append(impact)

                except Exception as e:


logger = logging.getLogger(__name__)

logger = get_logger(__name__)


class EthicalFramework(Enum):
    """Different ethical frameworks for analysis"""

    DEONTOLOGICAL = "deontological"  # Duty-based ethics (Kant)
    CONSEQUENTIALIST = "consequentialist"  # Outcome-based ethics (Mill)
    VIRTUE = "virtue"  # Character-based ethics (Aristotle)
    CARE = "care"  # Care ethics (Gilligan)
    JUSTICE = "justice"  # Justice-based ethics (Rawls)
    CONSTITUTIONAL = "constitutional"  # Constitutional AI principles


class DecisionStatus(Enum):
    """Status of ethical decisions"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    ESCALATED = "escalated"
    UNDER_REVIEW = "under_review"


class StakeholderType(Enum):
    """Types of stakeholders affected by decisions"""

    PRIMARY_USER = "primary_user"
    SECONDARY_USERS = "secondary_users"
    ORGANIZATION = "organization"
    SOCIETY = "society"
    ENVIRONMENT = "environment"
    FUTURE_GENERATIONS = "future_generations"


class RiskLevel(Enum):
    """Risk levels for ethical decisions"""

    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class StakeholderImpact:
    """Represents impact on a specific stakeholder"""

    stakeholder_type: StakeholderType
    impact_description: str
    impact_magnitude: float  # 0.0 to 1.0
    impact_valence: float  # -1.0 (negative) to 1.0 (positive)
    confidence: float  # 0.0 to 1.0
    time_horizon: str  # immediate, short_term, long_term
    mitigation_strategies: list[str] = field(default_factory=list)


@dataclass
class EthicalAnalysis:
    """Comprehensive ethical analysis of a decision"""

    analysis_id: str
    framework: EthicalFramework
    score: float  # 0.0 to 1.0
    reasoning: str
    key_considerations: list[str] = field(default_factory=list)
    potential_violations: list[str] = field(default_factory=list)
    supporting_principles: list[str] = field(default_factory=list)
    confidence: float = 0.8
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ComprehensiveEthicalDecision:
    """Comprehensive ethical decision with full analysis"""

    decision_id: str
    context: dict[str, Any]
    available_options: list[str]
    chosen_option: str
    status: DecisionStatus

    # Multi-framework analysis
    framework_analyses: list[EthicalAnalysis] = field(default_factory=list)
    overall_confidence: float = 0.0
    ethical_score: float = 0.0

    # Risk and impact analysis
    risk_level: RiskLevel = RiskLevel.MINIMAL
    stakeholder_impacts: list[StakeholderImpact] = field(default_factory=list)

    # Constitutional compliance
    constitutional_compliance: bool = True
    constitutional_violations: list[str] = field(default_factory=list)

    # Reasoning and justification
    primary_reasoning: str = ""
    alternative_considerations: list[str] = field(default_factory=list)
    assumptions_made: list[str] = field(default_factory=list)
    uncertainty_factors: list[str] = field(default_factory=list)

    # Monitoring and validation
    drift_score: float = 0.0
    requires_human_review: bool = False
    escalation_reason: Optional[str] = None

    # Constellation Framework integration
    identity_implications: list[str] = field(default_factory=list)  # ✨ Identity
    memory_implications: list[str] = field(default_factory=list)  # 🌟 Memory
    vision_implications: list[str] = field(default_factory=list)  # ⭐ Vision
    bio_implications: list[str] = field(default_factory=list)  # 🔥 Bio
    dream_implications: list[str] = field(default_factory=list)  # 💎 Dream
    ethics_implications: list[str] = field(default_factory=list)  # ⚖️ Ethics - The North Star
    guardian_validations: list[str] = field(default_factory=list)  # 🛡️ Guardian - The Watch Star
    quantum_implications: list[str] = field(default_factory=list)  # 🌌 Quantum

    # Metadata
    decision_maker: str = "ethical_decision_maker"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"


class AdvancedEthicalDecisionMaker:
    """
    Advanced ethical decision-making system for LUKHAS AI

    Integrates multiple ethical frameworks, constitutional principles,
    and Constellation Framework considerations to make comprehensive
    ethical decisions with full audit trails and stakeholder analysis.
    """

    def __init__(self, constitutional_framework: Optional[ConstitutionalFramework] = None):
        self.constitutional_framework = constitutional_framework or ConstitutionalFramework()
        self.decision_history: list[ComprehensiveEthicalDecision] = []
        self.framework_weights = self._initialize_framework_weights()
        self.stakeholder_priorities = self._initialize_stakeholder_priorities()
        self.drift_threshold = 0.15
        self.max_history_size = 1000

        # Performance metrics
        self.metrics = {
            "total_decisions": 0,
            "approved_decisions": 0,
            "rejected_decisions": 0,
            "escalated_decisions": 0,
            "average_confidence": 0.0,
            "average_processing_time": 0.0,
            "constitutional_violations": 0,
            "drift_detections": 0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("⚖️ Advanced Ethical Decision Maker initialized")

    def _initialize_framework_weights(self) -> dict[EthicalFramework, float]:
        """Initialize weights for different ethical frameworks"""
        return {
            EthicalFramework.CONSTITUTIONAL: 1.0,  # Highest priority
            EthicalFramework.DEONTOLOGICAL: 0.9,  # Duty-based ethics
            EthicalFramework.CONSEQUENTIALIST: 0.8,  # Outcome-based
            EthicalFramework.JUSTICE: 0.85,  # Justice-based
            EthicalFramework.VIRTUE: 0.7,  # Character-based
            EthicalFramework.CARE: 0.6,  # Care ethics
        }

    def _initialize_stakeholder_priorities(self) -> dict[StakeholderType, float]:
        """Initialize priority weights for stakeholders"""
        return {
            StakeholderType.PRIMARY_USER: 1.0,
            StakeholderType.SOCIETY: 0.9,
            StakeholderType.SECONDARY_USERS: 0.8,
            StakeholderType.FUTURE_GENERATIONS: 0.7,
            StakeholderType.ORGANIZATION: 0.6,
            StakeholderType.ENVIRONMENT: 0.8,
        }

    async def make_ethical_decision(
        self,
        context: dict[str, Any],
        available_options: list[str],
        stakeholder_types: Optional[list[StakeholderType]] = None,
        require_consensus: bool = False,
        min_confidence: float = 0.7,
    ) -> ComprehensiveEthicalDecision:
        """
        Make a comprehensive ethical decision

        Args:
            context: Decision context and parameters
            available_options: List of available decision options
            stakeholder_types: Stakeholders to consider
            require_consensus: Whether all frameworks must agree
            min_confidence: Minimum confidence threshold

        Returns:
            Comprehensive ethical decision with full analysis
        """
        start_time = datetime.now(timezone.utc)
        decision_id = f"eth_dec_{uuid.uuid4().hex[:8]}"

    async def _perform_multi_framework_analysis(
        self, context: dict[str, Any], options: list[str]
    ) -> list[EthicalAnalysis]:
        """Perform analysis across multiple ethical frameworks"""

        analyses = []

        for framework in EthicalFramework:
        return analyses

    async def _analyze_with_framework(
        self, framework: EthicalFramework, context: dict[str, Any], options: list[str]
    ) -> EthicalAnalysis:
        """Analyze options using specific ethical framework"""

        analysis_id = f"{framework.value}_{uuid.uuid4().hex[:8]}"

        if framework == EthicalFramework.CONSTITUTIONAL:
            return await self._constitutional_analysis(analysis_id, context, options)
        elif framework == EthicalFramework.DEONTOLOGICAL:
            return await self._deontological_analysis(analysis_id, context, options)
        elif framework == EthicalFramework.CONSEQUENTIALIST:
            return await self._consequentialist_analysis(analysis_id, context, options)
        elif framework == EthicalFramework.VIRTUE:
            return await self._virtue_analysis(analysis_id, context, options)
        elif framework == EthicalFramework.JUSTICE:
            return await self._justice_analysis(analysis_id, context, options)
        elif framework == EthicalFramework.CARE:
            return await self._care_analysis(analysis_id, context, options)
        else:
            # Default analysis
            return EthicalAnalysis(
                analysis_id=analysis_id,
                framework=framework,
                score=0.5,
                reasoning="Framework not implemented",
                confidence=0.5,
            )

    async def _constitutional_analysis(
        self, analysis_id: str, context: dict[str, Any], options: list[str]
    ) -> EthicalAnalysis:
        """Constitutional AI framework analysis"""

        # Get applicable constitutional rules
        applicable_rules = self.constitutional_framework.get_applicable_rules(context)

        option_scores = {}
        violations = []

        for option in options:
            score = 1.0
            option_violations = []

            # Check each applicable rule
            for rule in applicable_rules:
                for trigger in rule.violations_triggers:
                    if trigger.lower() in option.lower():
                        score -= 0.3
                        option_violations.append(f"Rule {rule.rule_id}: {trigger}")
                        violations.extend(option_violations)

            option_scores[option] = max(0.0, score)

        # Select best option based on constitutional compliance
        best_option = max(option_scores.keys(), key=lambda x: option_scores[x])
        best_score = option_scores[best_option]

        reasoning = f"Constitutional analysis selected '{best_option}' with score {best_score:.2f}. "
        if violations:
            reasoning += f"Detected violations: {', '.join(violations[:3])}"
        else:
            reasoning += "No constitutional violations detected."

        return EthicalAnalysis(
            analysis_id=analysis_id,
            framework=EthicalFramework.CONSTITUTIONAL,
            score=best_score,
            reasoning=reasoning,
            key_considerations=[rule.description for rule in applicable_rules[:3]],
            potential_violations=violations,
            supporting_principles=[rule.principle.value for rule in applicable_rules],
            confidence=0.9 if not violations else 0.7,
        )

    async def _deontological_analysis(
        self, analysis_id: str, context: dict[str, Any], options: list[str]
    ) -> EthicalAnalysis:
        """Deontological (duty-based) ethical analysis"""

        # Kantian categorical imperatives
        duties = [
            "treat people as ends in themselves",
            "act only on universalizable maxims",
            "respect human dignity",
            "maintain honesty and truthfulness",
            "protect autonomy and consent",
        ]

        option_scores = {}
        key_considerations = []

        for option in options:
            score = 0.8  # Base score
            option_lower = option.lower()

            # Positive duty fulfillment
            if any(duty_word in option_lower for duty_word in ["help", "respect", "protect", "support"]):
                score += 0.15

            # Negative duty violations
            if any(violation in option_lower for violation in ["deceive", "harm", "violate", "exploit"]):
                score -= 0.4

            # Universalizability test
            if "refuse" in option_lower and context.get("safety_concern"):
                score += 0.1  # Universalizable safety refusal

            option_scores[option] = max(0.0, min(1.0, score))

        best_option = max(option_scores.keys(), key=lambda x: option_scores[x])
        best_score = option_scores[best_option]

        key_considerations = duties[:3]

        reasoning = (
            f"Deontological analysis selected '{best_option}' with score {best_score:.2f}. "
            f"Analysis considered categorical imperatives and duty-based ethics."
        )

        return EthicalAnalysis(
            analysis_id=analysis_id,
            framework=EthicalFramework.DEONTOLOGICAL,
            score=best_score,
            reasoning=reasoning,
            key_considerations=key_considerations,
            supporting_principles=[
                "categorical_imperative",
                "human_dignity",
                "autonomy",
            ],
            confidence=0.8,
        )

    async def _consequentialist_analysis(
        self, analysis_id: str, context: dict[str, Any], options: list[str]
    ) -> EthicalAnalysis:
        """Consequentialist (outcome-based) ethical analysis"""

        option_scores = {}
        consequences_considered = []

        for option in options:
            # Estimate positive and negative consequences
            positive_outcomes = 0
            negative_outcomes = 0

            option_lower = option.lower()

            # Positive outcomes
            if any(pos in option_lower for pos in ["help", "improve", "benefit", "assist"]):
                positive_outcomes += 2

            if any(pos in option_lower for pos in ["educate", "inform", "guide"]):
                positive_outcomes += 1

            # Negative outcomes
            if any(neg in option_lower for neg in ["harm", "damage", "risk", "danger"]):
                negative_outcomes += 3

            if any(neg in option_lower for neg in ["refuse", "deny", "reject"]):
                negative_outcomes += 1  # Minor negative

            # Calculate utilitarian score
            net_utility = positive_outcomes - negative_outcomes
            score = 0.5 + (net_utility * 0.1)  # Normalize to 0-1 range
            score = max(0.0, min(1.0, score))

            option_scores[option] = score
            consequences_considered.append(f"{option}: +{positive_outcomes}, -{negative_outcomes}")

        best_option = max(option_scores.keys(), key=lambda x: option_scores[x])
        best_score = option_scores[best_option]

        reasoning = (
            f"Consequentialist analysis selected '{best_option}' with score {best_score:.2f}. "
            f"Analysis maximized overall utility and positive outcomes."
        )

        return EthicalAnalysis(
            analysis_id=analysis_id,
            framework=EthicalFramework.CONSEQUENTIALIST,
            score=best_score,
            reasoning=reasoning,
            key_considerations=consequences_considered[:3],
            supporting_principles=[
                "utility_maximization",
                "outcome_optimization",
                "greatest_good",
            ],
            confidence=0.7,
        )

    async def _virtue_analysis(self, analysis_id: str, context: dict[str, Any], options: list[str]) -> EthicalAnalysis:
        """Virtue ethics analysis"""

        # Core virtues
        virtues = {
            "wisdom": ["wise", "prudent", "thoughtful", "careful"],
            "justice": ["fair", "just", "equitable", "unbiased"],
            "courage": ["brave", "bold", "principled", "strong"],
            "temperance": ["moderate", "balanced", "restrained", "measured"],
            "compassion": ["kind", "caring", "empathetic", "gentle"],
            "honesty": ["truthful", "honest", "transparent", "open"],
        }

        option_scores = {}
        virtue_alignments = []

        for option in options:
            option_lower = option.lower()
            virtue_score = 0.5  # Base score
            aligned_virtues = []

            for virtue, keywords in virtues.items():
                if any(keyword in option_lower for keyword in keywords):
                    virtue_score += 0.08
                    aligned_virtues.append(virtue)

            # Penalize vice-like options
            vices = [
                "reckless",
                "cruel",
                "dishonest",
                "cowardly",
                "unjust",
                "excessive",
            ]
            if any(vice in option_lower for vice in vices):
                virtue_score -= 0.2

            option_scores[option] = max(0.0, min(1.0, virtue_score))
            if aligned_virtues:
                virtue_alignments.append(f"{option}: {', '.join(aligned_virtues)}")

        best_option = max(option_scores.keys(), key=lambda x: option_scores[x])
        best_score = option_scores[best_option]

        reasoning = (
            f"Virtue ethics analysis selected '{best_option}' with score {best_score:.2f}. "
            f"Analysis considered character virtues and moral excellence."
        )

        return EthicalAnalysis(
            analysis_id=analysis_id,
            framework=EthicalFramework.VIRTUE,
            score=best_score,
            reasoning=reasoning,
            key_considerations=virtue_alignments[:3],
            supporting_principles=list(virtues.keys()),
            confidence=0.75,
        )

    async def _justice_analysis(self, analysis_id: str, context: dict[str, Any], options: list[str]) -> EthicalAnalysis:
        """Justice-based ethical analysis (Rawlsian)"""

        option_scores = {}
        justice_considerations = []

        for option in options:
            option_lower = option.lower()
            justice_score = 0.6  # Base score

            # Fairness indicators
            if any(fair in option_lower for fair in ["fair", "equal", "just", "equitable"]):
                justice_score += 0.2

            # Veil of ignorance test - would this be acceptable if you didn't know your position?
            if any(protect in option_lower for protect in ["protect", "rights", "dignity"]):
                justice_score += 0.15

            # Discrimination or unfairness indicators
            if any(unfair in option_lower for unfair in ["discriminate", "bias", "unfair", "prejudice"]):
                justice_score -= 0.4

            # Consider the least advantaged
            if context.get("vulnerable_users") and "protect" in option_lower:
                justice_score += 0.1

            option_scores[option] = max(0.0, min(1.0, justice_score))
            justice_considerations.append(f"{option}: justice score {justice_score:.2f}")

        best_option = max(option_scores.keys(), key=lambda x: option_scores[x])
        best_score = option_scores[best_option]

        reasoning = (
            f"Justice analysis selected '{best_option}' with score {best_score:.2f}. "
            f"Analysis considered fairness, equality, and protection of rights."
        )

        return EthicalAnalysis(
            analysis_id=analysis_id,
            framework=EthicalFramework.JUSTICE,
            score=best_score,
            reasoning=reasoning,
            key_considerations=justice_considerations[:3],
            supporting_principles=[
                "fairness",
                "equality",
                "rights_protection",
                "veil_of_ignorance",
            ],
            confidence=0.8,
        )

    async def _care_analysis(self, analysis_id: str, context: dict[str, Any], options: list[str]) -> EthicalAnalysis:
        """Care ethics analysis"""

        option_scores = {}
        care_considerations = []

        for option in options:
            option_lower = option.lower()
            care_score = 0.6  # Base score

            # Care and relationship indicators
            if any(care in option_lower for care in ["care", "support", "help", "nurture"]):
                care_score += 0.2

            # Attention to context and relationships
            if any(context_word in option_lower for context_word in ["understand", "listen", "consider"]):
                care_score += 0.1

            # Responsiveness to needs
            if context.get("user_distress") and any(
                respond in option_lower for respond in ["gentle", "compassionate", "understanding"]
            ):
                care_score += 0.15

            # Harm to relationships
            if any(harm in option_lower for harm in ["dismiss", "ignore", "harsh", "cold"]):
                care_score -= 0.3

            option_scores[option] = max(0.0, min(1.0, care_score))
            care_considerations.append(f"{option}: care orientation score {care_score:.2f}")

        best_option = max(option_scores.keys(), key=lambda x: option_scores[x])
        best_score = option_scores[best_option]

        reasoning = (
            f"Care ethics analysis selected '{best_option}' with score {best_score:.2f}. "
            f"Analysis emphasized relationships, care, and contextual responsiveness."
        )

        return EthicalAnalysis(
            analysis_id=analysis_id,
            framework=EthicalFramework.CARE,
            score=best_score,
            reasoning=reasoning,
            key_considerations=care_considerations[:3],
            supporting_principles=[
                "care",
                "relationships",
                "context_sensitivity",
                "responsiveness",
            ],
            confidence=0.7,
        )

    async def _analyze_stakeholder_impacts(
        self,
        context: dict[str, Any],
        options: list[str],
        stakeholder_types: list[StakeholderType],
    ) -> list[StakeholderImpact]:
        """Analyze impacts on different stakeholders"""

        impacts = []

        for stakeholder in stakeholder_types:
            for option in options:
        return impacts

    async def _assess_stakeholder_impact(
        self, stakeholder: StakeholderType, option: str, context: dict[str, Any]
    ) -> StakeholderImpact:
        """Assess impact on specific stakeholder"""

        option_lower = option.lower()

        # Base impact assessment
        magnitude = 0.5
        valence = 0.0  # Neutral
        confidence = 0.7
        time_horizon = "immediate"
        description = f"Impact of '{option}' on {stakeholder.value}"
        mitigation_strategies = []

        # Stakeholder-specific impact analysis
        if stakeholder == StakeholderType.PRIMARY_USER:
            if "help" in option_lower or "assist" in option_lower:
                valence = 0.7
                magnitude = 0.8
                description = "Positive assistance to primary user"
            elif "refuse" in option_lower:
                valence = -0.3
                magnitude = 0.6
                description = "Request refusal may disappoint user"
                mitigation_strategies.append("Provide clear explanation and alternatives")

        elif stakeholder == StakeholderType.SOCIETY:
            if "safety" in option_lower or "protect" in option_lower:
                valence = 0.8
                magnitude = 0.7
                time_horizon = "long_term"
                description = "Positive societal impact through safety measures"
            elif "harm" in option_lower:
                valence = -0.9
                magnitude = 0.9
                description = "Potential societal harm"

        elif stakeholder == StakeholderType.ORGANIZATION:
            if "compliance" in option_lower or "policy" in option_lower:
                valence = 0.6
                magnitude = 0.7
                description = "Supports organizational compliance and reputation"
            elif "violation" in option_lower:
                valence = -0.8
                magnitude = 0.8
                description = "Risk to organizational reputation"

        # Adjust based on context
        if context.get("high_stakes"):
            magnitude += 0.2
            confidence -= 0.1

        if context.get("sensitive_topic"):
            magnitude += 0.1
            mitigation_strategies.append("Increased monitoring and care")

        return StakeholderImpact(
            stakeholder_type=stakeholder,
            impact_description=description,
            impact_magnitude=min(1.0, magnitude),
            impact_valence=max(-1.0, min(1.0, valence)),
            confidence=max(0.0, min(1.0, confidence)),
            time_horizon=time_horizon,
            mitigation_strategies=mitigation_strategies,
        )

    async def _check_constitutional_compliance(self, context: dict[str, Any], options: list[str]) -> dict[str, Any]:
        """Check compliance with constitutional principles"""

        violations = []
        compliant = True

        applicable_rules = self.constitutional_framework.get_applicable_rules(context)

        for option in options:
            option_lower = option.lower()

            for rule in applicable_rules:
                for trigger in rule.violations_triggers:
                    if trigger.lower() in option_lower:
                        violations.append(f"Rule {rule.rule_id}: {trigger} in option '{option}'")
                        compliant = False

        return {
            "compliant": compliant,
            "violations": violations,
            "applicable_rules": len(applicable_rules),
        }

    async def _calculate_option_scores(
        self,
        options: list[str],
        framework_analyses: list[EthicalAnalysis],
        stakeholder_impacts: list[StakeholderImpact],
    ) -> dict[str, float]:
        """Calculate overall scores for each option"""

        option_scores = {}

        for option in options:
            total_score = 0.0
            total_weight = 0.0

            # Framework scores
            for analysis in framework_analyses:
                framework_weight = self.framework_weights.get(analysis.framework, 0.5)
                confidence_weight = analysis.confidence

                # For multi-option analysis, we need to extract option-specific scores
                # For now, use the analysis score directly
                weighted_score = analysis.score * framework_weight * confidence_weight
                total_score += weighted_score
                total_weight += framework_weight * confidence_weight

            # Stakeholder impact scores
            stakeholder_score = 0.0
            stakeholder_weight = 0.0

            for impact in stakeholder_impacts:
                if option.lower() in impact.impact_description.lower():
                    stakeholder_priority = self.stakeholder_priorities.get(impact.stakeholder_type, 0.5)
                    impact_score = (impact.impact_valence + 1.0) / 2.0  # Normalize to 0-1
                    weighted_impact = impact_score * stakeholder_priority * impact.confidence

                    stakeholder_score += weighted_impact
                    stakeholder_weight += stakeholder_priority * impact.confidence

            # Combine framework and stakeholder scores
            framework_score = total_score / total_weight if total_weight > 0 else 0.5

            if stakeholder_weight > 0:
                stakeholder_avg = stakeholder_score / stakeholder_weight
                # Weighted combination: 70% framework, 30% stakeholder
                final_score = 0.7 * framework_score + 0.3 * stakeholder_avg
            else:
                final_score = framework_score

            option_scores[option] = max(0.0, min(1.0, final_score))

        return option_scores

    def _select_best_option(
        self, option_scores: dict[str, float], require_consensus: bool = False
    ) -> tuple[str, float]:
        """Select the best option based on scores"""

        if not option_scores:
            return "no_action", 0.0

        if require_consensus:
            # Check if there's clear consensus (top option significantly better)
            sorted_scores = sorted(option_scores.items(), key=lambda x: x[1], reverse=True)

            if len(sorted_scores) > 1:
                top_score = sorted_scores[0][1]
                second_score = sorted_scores[1][1]

                # Require significant difference for consensus
                if top_score - second_score < 0.2:
                    return "require_human_review", 0.5

            return sorted_scores[0]
        else:
            # Simply return highest scoring option
            best_option = max(option_scores.keys(), key=lambda x: option_scores[x])
            return best_option, option_scores[best_option]

    def _calculate_overall_confidence(self, framework_analyses: list[EthicalAnalysis]) -> float:
        """Calculate overall confidence in the decision"""

        if not framework_analyses:
            return 0.3

        # Weight confidence by framework importance
        total_weighted_confidence = 0.0
        total_weight = 0.0

        for analysis in framework_analyses:
            framework_weight = self.framework_weights.get(analysis.framework, 0.5)
            weighted_confidence = analysis.confidence * framework_weight

            total_weighted_confidence += weighted_confidence
            total_weight += framework_weight

        if total_weight > 0:
            return min(0.95, total_weighted_confidence / total_weight)
        else:
            return 0.5

    async def _determine_decision_status(
        self, decision: ComprehensiveEthicalDecision, min_confidence: float
    ) -> DecisionStatus:
        """Determine the status of the decision"""

        # Check confidence threshold
        if decision.overall_confidence < min_confidence:
            return DecisionStatus.DEFERRED

        # Check constitutional compliance
        if not decision.constitutional_compliance:
            return DecisionStatus.REJECTED

        # Check for high-risk situations
        if decision.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return DecisionStatus.ESCALATED

        # Check drift score
        if decision.drift_score > self.drift_threshold:
            return DecisionStatus.UNDER_REVIEW

        # Default to approved if all checks pass
        return DecisionStatus.APPROVED

    async def _assess_risk_level(self, decision: ComprehensiveEthicalDecision, context: dict[str, Any]) -> RiskLevel:
        """Assess overall risk level of the decision"""

        risk_factors = 0

        # Constitutional violations increase risk
        if decision.constitutional_violations:
            risk_factors += len(decision.constitutional_violations) * 2

        # Low confidence increases risk
        if decision.overall_confidence < 0.5:
            risk_factors += 2
        elif decision.overall_confidence < 0.7:
            risk_factors += 1

        # Context-based risk factors
        if context.get("high_stakes"):
            risk_factors += 2

        if context.get("sensitive_topic"):
            risk_factors += 1

        if context.get("vulnerable_users"):
            risk_factors += 2

        # Stakeholder impact risks
        for impact in decision.stakeholder_impacts:
            if impact.impact_valence < -0.5 and impact.impact_magnitude > 0.7:
                risk_factors += 2

        # Determine risk level
        if risk_factors >= 8:
            return RiskLevel.CRITICAL
        elif risk_factors >= 5:
            return RiskLevel.HIGH
        elif risk_factors >= 3:
            return RiskLevel.MODERATE
        elif risk_factors >= 1:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    async def _generate_primary_reasoning(
        self,
        decision: ComprehensiveEthicalDecision,
        framework_analyses: list[EthicalAnalysis],
        option_scores: dict[str, float],
    ) -> str:
        """Generate primary reasoning for the decision"""

        reasoning_parts = [
            f"Selected '{decision.chosen_option}' with overall ethical score {decision.ethical_score:.2f} "
            f"and confidence {decision.overall_confidence:.2f}."
        ]

        # Add framework consensus or conflicts
        framework_agreements = []
        framework_conflicts = []

        for analysis in framework_analyses:
            if analysis.score >= 0.7:
                framework_agreements.append(analysis.framework.value)
            elif analysis.score <= 0.3:
                framework_conflicts.append(analysis.framework.value)

        if framework_agreements:
            reasoning_parts.append(f"Strong support from frameworks: {', '.join(framework_agreements[:3])}.")

        if framework_conflicts:
            reasoning_parts.append(f"Concerns raised by frameworks: {', '.join(framework_conflicts[:2])}.")

        # Add constitutional compliance
        if decision.constitutional_compliance:
            reasoning_parts.append("Decision complies with all constitutional principles.")
        else:
            reasoning_parts.append(
                f"Constitutional concerns: {len(decision.constitutional_violations)} violations detected."
            )

        # Add stakeholder considerations
        if decision.stakeholder_impacts:
            positive_impacts = sum(1 for impact in decision.stakeholder_impacts if impact.impact_valence > 0)
            negative_impacts = sum(1 for impact in decision.stakeholder_impacts if impact.impact_valence < 0)

            reasoning_parts.append(
                f"Stakeholder analysis: {positive_impacts} positive impacts, {negative_impacts} negative impacts."
            )

        # Add risk assessment
        reasoning_parts.append(f"Risk level: {decision.risk_level.value}.")

        return " ".join(reasoning_parts)

    async def _integrate_constellation_framework(self, decision: ComprehensiveEthicalDecision, context: dict[str, Any]):
        """Integrate Constellation Framework considerations (✨🌟⭐🔥💎⚖️🛡️🌌)"""

        # ✨ Identity implications - Anchor star
        identity_factors = []
        if context.get("user_identity_involved"):
            identity_factors.append("User identity authentication and validation considered")
        if "consent" in decision.chosen_option.lower():
            identity_factors.append("Identity-based consent mechanisms evaluated")
        if context.get("personal_data"):
            identity_factors.append("Personal identity data protection measures applied")
        decision.identity_implications = identity_factors

        # 🌟 Memory implications - Tracing paths of past light
        memory_factors = []
        if context.get("historical_context"):
            memory_factors.append("Historical context and memory patterns considered")
        if len(self.decision_history) > 0:
            memory_factors.append(f"Decision informed by {len(self.decision_history)} previous decisions")
        decision.memory_implications = memory_factors

        # ⭐ Vision implications - Orientation toward horizon
        vision_factors = []
        if context.get("future_impact"):
            vision_factors.append("Future impact and long-term consequences evaluated")
        if "goal" in decision.chosen_option.lower():
            vision_factors.append("Vision-aligned goal orientation maintained")
        decision.vision_implications = vision_factors

        # 🔥 Bio implications - Resilience and adaptation
        bio_factors = []
        if context.get("adaptive_response"):
            bio_factors.append("Adaptive response patterns integrated")
        if decision.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            bio_factors.append("System resilience maintained within acceptable parameters")
        decision.bio_implications = bio_factors

        # 💎 Dream implications - Symbolic drift
        dream_factors = []
        if context.get("creative_processing"):
            dream_factors.append("Creative and symbolic processing pathways engaged")
        if decision.drift_score < 0.1:
            dream_factors.append("Symbolic drift within acceptable bounds")
        decision.dream_implications = dream_factors

        # ⚖️ Ethics implications - The North Star (responsible, transparent, accountable)
        ethics_factors = []
        if decision.constitutional_compliance:
            ethics_factors.append("Constitutional AI principles upheld")
        if decision.ethical_score > 0.8:
            ethics_factors.append("High ethical standard achieved")
        if context.get("stakeholder_impact"):
            ethics_factors.append("Stakeholder impact thoroughly analyzed")
        decision.ethics_implications = ethics_factors

        # 🛡️ Guardian validations - The Watch Star (protective, trustworthy, serious protection)
        guardian_factors = []
        guardian_factors.append(f"Guardian drift detection: {decision.drift_score:.3f}")
        if decision.constitutional_compliance:
            guardian_factors.append("Guardian constitutional validation: PASSED")
        else:
            guardian_factors.append("Guardian constitutional validation: FAILED")
        if decision.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            guardian_factors.append("Guardian escalation: HIGH RISK DETECTED")
        decision.guardian_validations = guardian_factors

        # 🌌 Quantum implications - Ambiguity and resolution
        quantum_factors = []
        if context.get("uncertainty_handling"):
            quantum_factors.append("Uncertainty and ambiguity resolution mechanisms engaged")
        if len(decision.alternative_options) > 1:
            quantum_factors.append(
                f"Quantum decision space explored across {len(decision.alternative_options)} possibilities"
            )
        decision.quantum_implications = quantum_factors

    async def _calculate_drift_score(self, decision: ComprehensiveEthicalDecision) -> float:
        """Calculate drift score for the decision"""

        if len(self.decision_history) < 2:
            return 0.0  # Not enough history for drift detection

        # Compare with recent decisions
        recent_decisions = self.decision_history[-10:]  # Last 10 decisions

        current_score = decision.ethical_score
        current_frameworks = {analysis.framework for analysis in decision.framework_analyses}

        drift_indicators = []

        for past_decision in recent_decisions:
            # Score drift
            if past_decision.ethical_score > 0:
                score_drift = abs(current_score - past_decision.ethical_score)
                drift_indicators.append(score_drift)

            # Framework consistency drift
            past_frameworks = {analysis.framework for analysis in past_decision.framework_analyses}
            framework_overlap = len(current_frameworks.intersection(past_frameworks))
            framework_total = len(current_frameworks.union(past_frameworks))

            if framework_total > 0:
                framework_consistency = framework_overlap / framework_total
                drift_indicators.append(1.0 - framework_consistency)

        if drift_indicators:
            return sum(drift_indicators) / len(drift_indicators)
        else:
            return 0.0

    async def _update_metrics(self, decision: ComprehensiveEthicalDecision, start_time: datetime):
        """Update system metrics"""

        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()

        self.metrics["total_decisions"] += 1

        if decision.status == DecisionStatus.APPROVED:
            self.metrics["approved_decisions"] += 1
        elif decision.status == DecisionStatus.REJECTED:
            self.metrics["rejected_decisions"] += 1
        elif decision.status in [DecisionStatus.ESCALATED, DecisionStatus.UNDER_REVIEW]:
            self.metrics["escalated_decisions"] += 1

        if decision.constitutional_violations:
            self.metrics["constitutional_violations"] += len(decision.constitutional_violations)

        # Update average confidence
        total_decisions = self.metrics["total_decisions"]
        current_avg = self.metrics["average_confidence"]
        new_avg = ((current_avg * (total_decisions - 1)) + decision.overall_confidence) / total_decisions
        self.metrics["average_confidence"] = new_avg

        # Update average processing time
        current_time_avg = self.metrics["average_processing_time"]
        new_time_avg = ((current_time_avg * (total_decisions - 1)) + processing_time) / total_decisions
        self.metrics["average_processing_time"] = new_time_avg

        self.metrics["last_updated"] = datetime.now(timezone.utc).isoformat()

    def _maintain_history_size(self):
        """Maintain decision history size"""
        if len(self.decision_history) > self.max_history_size:
            # Keep most recent decisions
            self.decision_history = self.decision_history[-self.max_history_size :]

    async def get_decision_history(
        self, limit: int = 50, status_filter: Optional[DecisionStatus] = None
    ) -> list[ComprehensiveEthicalDecision]:
        """Get decision history with optional filtering"""

        history = self.decision_history[-limit:]

        if status_filter:
            history = [d for d in history if d.status == status_filter]

        return history

    async def get_system_metrics(self) -> dict[str, Any]:
        """Get system performance metrics"""
        return self.metrics.copy()

    async def export_decision_audit_trail(self, decision_id: str) -> Optional[dict[str, Any]]:
        """Export comprehensive audit trail for a decision"""

        decision = None
        for d in self.decision_history:
            if d.decision_id == decision_id:
                decision = d
                break

        if not decision:
            return None

        audit_trail = {
            "decision_id": decision.decision_id,
            "timestamp": decision.created_at.isoformat(),
            "context": decision.context,
            "available_options": decision.available_options,
            "chosen_option": decision.chosen_option,
            "status": decision.status.value,
            "ethical_score": decision.ethical_score,
            "confidence": decision.overall_confidence,
            "risk_level": decision.risk_level.value,
            "constitutional_compliance": decision.constitutional_compliance,
            "constitutional_violations": decision.constitutional_violations,
            "framework_analyses": [
                {
                    "framework": analysis.framework.value,
                    "score": analysis.score,
                    "reasoning": analysis.reasoning,
                    "confidence": analysis.confidence,
                    "key_considerations": analysis.key_considerations,
                    "supporting_principles": analysis.supporting_principles,
                }
                for analysis in decision.framework_analyses
            ],
            "stakeholder_impacts": [
                {
                    "stakeholder": impact.stakeholder_type.value,
                    "description": impact.impact_description,
                    "magnitude": impact.impact_magnitude,
                    "valence": impact.impact_valence,
                    "confidence": impact.confidence,
                    "time_horizon": impact.time_horizon,
                    "mitigation_strategies": impact.mitigation_strategies,
                }
                for impact in decision.stakeholder_impacts
            ],
            "constellation_framework": {
                "identity_implications": decision.identity_implications,
                "memory_implications": decision.memory_implications,
                "vision_implications": decision.vision_implications,
                "bio_implications": decision.bio_implications,
                "dream_implications": decision.dream_implications,
                "ethics_implications": decision.ethics_implications,
                "guardian_validations": decision.guardian_validations,
                "quantum_implications": decision.quantum_implications,
            },
            "primary_reasoning": decision.primary_reasoning,
            "drift_score": decision.drift_score,
            "requires_human_review": decision.requires_human_review,
            "escalation_reason": decision.escalation_reason,
            "system_version": decision.version,
        }

        return audit_trail


# Export main classes and functions
__all__ = [
    "AdvancedEthicalDecisionMaker",
    "ComprehensiveEthicalDecision",
    "DecisionStatus",
    "EthicalAnalysis",
    "EthicalFramework",
    "RiskLevel",
    "StakeholderImpact",
    "StakeholderType",
]
