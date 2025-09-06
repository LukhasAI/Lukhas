"""
Constitutional AI Implementation for AGI Safety

Implements constitutional AI principles for safe and aligned AGI behavior,
integrating with LUKHAS Guardian System for comprehensive safety oversight.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class PrincipleCategory(Enum):
    """Categories of constitutional principles."""

    HARM_PREVENTION = "harm_prevention"  # Preventing harm to humans and society
    TRUTH_HONESTY = "truth_honesty"  # Commitment to truth and honesty
    AUTONOMY_RESPECT = "autonomy_respect"  # Respecting human autonomy and choice
    FAIRNESS = "fairness"  # Fair and equitable treatment
    PRIVACY = "privacy"  # Protecting privacy and confidentiality
    TRANSPARENCY = "transparency"  # Being transparent about capabilities/limitations
    BENEFICIAL = "beneficial"  # Acting for human benefit
    NON_MANIPULATION = "non_manipulation"  # Avoiding manipulation or coercion


class PrincipleScope(Enum):
    """Scope of principle application."""

    UNIVERSAL = "universal"  # Applies in all contexts
    CONTEXTUAL = "contextual"  # Applies in specific contexts
    PREFERENTIAL = "preferential"  # Preferred but not absolute
    ADVISORY = "advisory"  # Advisory guidance only


class ViolationSeverity(Enum):
    """Severity levels for principle violations."""

    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # High priority violation
    MEDIUM = "medium"  # Moderate violation
    LOW = "low"  # Minor violation
    ADVISORY = "advisory"  # Advisory note only


@dataclass
class SafetyPrinciple:
    """Constitutional AI safety principle."""

    principle_id: str
    name: str
    description: str
    category: PrincipleCategory
    scope: PrincipleScope

    # Principle specification
    conditions: list[str]  # When this principle applies
    requirements: list[str]  # What the principle requires
    prohibitions: list[str]  # What the principle prohibits
    exceptions: list[str] = field(default_factory=list)  # Exceptions to the principle

    # Enforcement parameters
    enforcement_threshold: float = 0.8  # Threshold for triggering enforcement
    violation_penalties: dict[ViolationSeverity, float] = field(default_factory=dict)

    # Context sensitivity
    context_modifiers: dict[str, float] = field(default_factory=dict)
    constellation_alignment: dict[str, float] = field(default_factory=dict)

    # Learning and adaptation
    adaptable: bool = True  # Whether principle can be refined through learning
    confidence: float = 1.0  # Confidence in principle formulation
    evidence_count: int = 0  # Number of supporting applications

    def evaluate_violation(
        self, action: dict[str, Any], context: dict[str, Any]
    ) -> tuple[bool, ViolationSeverity, str]:
        """Evaluate if an action violates this principle."""

        # Check if principle applies in this context
        if not self._applies_in_context(context):
            return False, ViolationSeverity.ADVISORY, "Principle does not apply in this context"

        # Check prohibitions
        violation_score = 0.0
        violation_reasons = []

        for prohibition in self.prohibitions:
            if self._matches_prohibition(action, prohibition, context):
                violation_score += 0.3
                violation_reasons.append(f"Violates prohibition: {prohibition}")

        # Check requirements
        for requirement in self.requirements:
            if not self._meets_requirement(action, requirement, context):
                violation_score += 0.2
                violation_reasons.append(f"Fails to meet requirement: {requirement}")

        # Apply context modifiers
        for modifier, factor in self.context_modifiers.items():
            if modifier in str(context).lower():
                violation_score *= factor

        # Determine if violation occurred
        is_violation = violation_score >= self.enforcement_threshold

        if is_violation:
            # Determine severity
            if violation_score >= 0.9:
                severity = ViolationSeverity.CRITICAL
            elif violation_score >= 0.7:
                severity = ViolationSeverity.HIGH
            elif violation_score >= 0.5:
                severity = ViolationSeverity.MEDIUM
            else:
                severity = ViolationSeverity.LOW

            reason = "; ".join(violation_reasons)
            return True, severity, reason

        return False, ViolationSeverity.ADVISORY, "No violation detected"

    def _applies_in_context(self, context: dict[str, Any]) -> bool:
        """Check if principle applies in the given context."""

        if self.scope == PrincipleScope.UNIVERSAL:
            return True

        if self.scope == PrincipleScope.CONTEXTUAL:
            # Check if any conditions are met
            return any(condition in str(context).lower() for condition in self.conditions)

        return True  # PREFERENTIAL and ADVISORY always apply but with different weight

    def _matches_prohibition(self, action: dict[str, Any], prohibition: str, context: dict[str, Any]) -> bool:
        """Check if action matches a prohibition."""
        # Simple keyword matching - could be enhanced with semantic analysis
        action_text = str(action).lower()
        return prohibition.lower() in action_text

    def _meets_requirement(self, action: dict[str, Any], requirement: str, context: dict[str, Any]) -> bool:
        """Check if action meets a requirement."""
        # Simple keyword matching - could be enhanced with semantic analysis
        action_text = str(action).lower()
        return requirement.lower() in action_text or "comply" in action_text


@dataclass
class Constitution:
    """Constitutional AI constitution containing principles and enforcement rules."""

    constitution_id: str
    name: str
    version: str
    description: str

    # Principles
    principles: list[SafetyPrinciple] = field(default_factory=list)

    # Meta-principles (principles about principles)
    meta_principles: dict[str, Any] = field(default_factory=dict)

    # Conflict resolution
    principle_hierarchy: list[str] = field(default_factory=list)  # Ordered by priority
    conflict_resolution_rules: dict[str, str] = field(default_factory=dict)

    # Adaptation parameters
    learning_enabled: bool = True
    adaptation_threshold: float = 0.8
    evidence_requirement: int = 10

    # Validation
    created_time: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    validation_status: str = "active"

    def add_principle(self, principle: SafetyPrinciple):
        """Add a new principle to the constitution."""
        self.principles.append(principle)
        self.principle_hierarchy.append(principle.principle_id)
        self.last_updated = datetime.now()

        logger.info(f"Added principle to constitution: {principle.name}")

    def resolve_principle_conflict(self, conflicting_principles: list[str], context: dict[str, Any]) -> str:
        """Resolve conflicts between principles."""

        # Use hierarchy to resolve conflicts
        for principle_id in self.principle_hierarchy:
            if principle_id in conflicting_principles:
                return principle_id

        # Fallback to first principle if not in hierarchy
        return conflicting_principles[0] if conflicting_principles else ""


class ConstitutionalAI:
    """
    Constitutional AI Safety System for AGI

    Implements constitutional AI principles for ensuring safe, ethical,
    and aligned behavior in AGI systems through principle-based constraints.
    """

    def __init__(self):
        # Constitution management
        self.active_constitution: Optional[Constitution] = None
        self.constitution_history: list[Constitution] = []

        # Violation tracking
        self.violation_history: list[dict[str, Any]] = []
        self.principle_effectiveness: dict[str, float] = {}

        # Decision cache for performance
        self.decision_cache: dict[str, tuple[bool, str]] = {}
        self.cache_ttl_minutes = 30

        # Configuration
        self.enforcement_enabled = True
        self.learning_enabled = True
        self.violation_threshold = 0.7
        self.emergency_shutdown_threshold = 0.95

        # Initialize with basic constitutional principles
        self._initialize_basic_constitution()

        # Statistics
        self.stats = {
            "total_evaluations": 0,
            "violations_detected": 0,
            "actions_blocked": 0,
            "principles_triggered": {},
            "violation_severities": {severity.value: 0 for severity in ViolationSeverity},
        }

    def _initialize_basic_constitution(self):
        """Initialize with fundamental constitutional AI principles."""

        constitution = Constitution(
            constitution_id="lukhas_agi_constitution_v1",
            name="LUKHAS AGI Constitutional Principles",
            version="1.0.0",
            description="Foundational constitutional principles for LUKHAS AGI system safety and alignment",
        )

        # Harm Prevention Principle
        harm_prevention = SafetyPrinciple(
            principle_id="harm_prevention_core",
            name="Core Harm Prevention",
            description="Never cause or contribute to harm to humans, animals, or society",
            category=PrincipleCategory.HARM_PREVENTION,
            scope=PrincipleScope.UNIVERSAL,
            conditions=["any interaction", "any output", "any decision"],
            requirements=[
                "assess potential harm before acting",
                "prioritize human wellbeing",
                "consider long-term consequences",
            ],
            prohibitions=[
                "causing physical harm",
                "causing psychological harm",
                "providing dangerous information",
                "encouraging harmful behaviors",
                "creating harmful content",
            ],
            enforcement_threshold=0.9,
            constellation_alignment={"GUARDIAN": 1.0, "ETHICS": 1.0},
        )

        # Truth and Honesty Principle
        truth_honesty = SafetyPrinciple(
            principle_id="truth_honesty_core",
            name="Truth and Honesty",
            description="Commitment to truthfulness and honesty in all interactions",
            category=PrincipleCategory.TRUTH_HONESTY,
            scope=PrincipleScope.UNIVERSAL,
            conditions=["providing information", "making claims", "answering questions"],
            requirements=["verify information accuracy", "acknowledge uncertainty", "correct misinformation"],
            prohibitions=[
                "deliberate deception",
                "spreading misinformation",
                "making false claims",
                "misleading users",
            ],
            enforcement_threshold=0.8,
            constellation_alignment={"ETHICS": 0.9, "GUARDIAN": 0.8},
        )

        # Autonomy and Consent Principle
        autonomy_respect = SafetyPrinciple(
            principle_id="autonomy_respect_core",
            name="Human Autonomy and Consent",
            description="Respect human autonomy, agency, and right to make decisions",
            category=PrincipleCategory.AUTONOMY_RESPECT,
            scope=PrincipleScope.UNIVERSAL,
            conditions=["human decision making", "personal choices", "consent situations"],
            requirements=["respect human choices", "obtain proper consent", "support informed decision making"],
            prohibitions=[
                "coercion or manipulation",
                "overriding human decisions",
                "violating consent",
                "removing human agency",
            ],
            enforcement_threshold=0.85,
            constellation_alignment={"ETHICS": 1.0, "IDENTITY": 0.7},
        )

        # Privacy Protection Principle
        privacy_protection = SafetyPrinciple(
            principle_id="privacy_protection_core",
            name="Privacy Protection",
            description="Protect personal privacy and confidential information",
            category=PrincipleCategory.PRIVACY,
            scope=PrincipleScope.UNIVERSAL,
            conditions=["handling personal data", "confidential information", "private communications"],
            requirements=["protect personal information", "respect confidentiality", "minimize data collection"],
            prohibitions=[
                "unauthorized data sharing",
                "privacy violations",
                "exposing personal information",
                "tracking without consent",
            ],
            enforcement_threshold=0.8,
            constellation_alignment={"GUARDIAN": 0.9, "IDENTITY": 0.8},
        )

        # Add principles to constitution
        constitution.add_principle(harm_prevention)
        constitution.add_principle(truth_honesty)
        constitution.add_principle(autonomy_respect)
        constitution.add_principle(privacy_protection)

        # Set principle hierarchy (most important first)
        constitution.principle_hierarchy = [
            "harm_prevention_core",
            "autonomy_respect_core",
            "truth_honesty_core",
            "privacy_protection_core",
        ]

        self.active_constitution = constitution

        logger.info("Initialized basic constitutional AI principles")

    async def evaluate_action(
        self, action: dict[str, Any], context: dict[str, Any]
    ) -> tuple[bool, list[dict[str, Any]]]:
        """
        Evaluate an action against constitutional principles.

        Args:
            action: The action to evaluate
            context: Context in which the action occurs

        Returns:
            Tuple of (is_safe, violations_list)
        """

        if not self.active_constitution or not self.enforcement_enabled:
            return True, []

        # Check cache first
        cache_key = self._generate_cache_key(action, context)
        if cache_key in self.decision_cache:
            cached_result, cached_time = self.decision_cache[cache_key]
            if datetime.now() - datetime.fromisoformat(cached_time) < timedelta(minutes=self.cache_ttl_minutes):
                return cached_result

        violations = []
        overall_violation_score = 0.0

        try:
            # Evaluate against each principle
            for principle in self.active_constitution.principles:
                is_violation, severity, reason = principle.evaluate_violation(action, context)

                if is_violation:
                    violation_record = {
                        "principle_id": principle.principle_id,
                        "principle_name": principle.name,
                        "severity": severity.value,
                        "reason": reason,
                        "timestamp": datetime.now().isoformat(),
                        "action": action,
                        "context": context,
                    }

                    violations.append(violation_record)

                    # Calculate violation score impact
                    severity_weights = {
                        ViolationSeverity.CRITICAL: 1.0,
                        ViolationSeverity.HIGH: 0.8,
                        ViolationSeverity.MEDIUM: 0.6,
                        ViolationSeverity.LOW: 0.4,
                        ViolationSeverity.ADVISORY: 0.1,
                    }

                    overall_violation_score = max(overall_violation_score, severity_weights[severity])

                    # Update statistics
                    self.stats["violations_detected"] += 1
                    self.stats["violation_severities"][severity.value] += 1
                    self.stats["principles_triggered"][principle.principle_id] = (
                        self.stats["principles_triggered"].get(principle.principle_id, 0) + 1
                    )

            # Determine if action is safe
            is_safe = overall_violation_score < self.violation_threshold

            # Emergency shutdown check
            if overall_violation_score >= self.emergency_shutdown_threshold:
                logger.critical(f"Emergency shutdown triggered! Violation score: {overall_violation_score}")
                await self._trigger_emergency_response(action, context, violations)
                is_safe = False

            # Update statistics
            self.stats["total_evaluations"] += 1
            if not is_safe:
                self.stats["actions_blocked"] += 1

            # Record violation history
            if violations:
                self.violation_history.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "action": action,
                        "context": context,
                        "violations": violations,
                        "overall_score": overall_violation_score,
                        "blocked": not is_safe,
                    }
                )

            # Cache result
            self.decision_cache[cache_key] = (is_safe, violations), datetime.now().isoformat()

            # Learn from this evaluation
            if self.learning_enabled:
                await self._learn_from_evaluation(action, context, violations, is_safe)

            return is_safe, violations

        except Exception as e:
            logger.error(f"Error in constitutional evaluation: {e}")
            # Fail safe - block action if evaluation fails
            return False, [
                {
                    "principle_id": "evaluation_error",
                    "principle_name": "Evaluation Error",
                    "severity": "critical",
                    "reason": f"Failed to evaluate action: {e}",
                    "timestamp": datetime.now().isoformat(),
                }
            ]

    async def get_safety_guidance(self, planned_action: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Provide guidance for making an action safer and more aligned.

        Args:
            planned_action: The action being planned
            context: Context for the action

        Returns:
            Safety guidance including suggestions and warnings
        """

        guidance = {
            "overall_safety": "unknown",
            "recommendations": [],
            "warnings": [],
            "modifications": [],
            "alternative_actions": [],
        }

        if not self.active_constitution:
            return guidance

        try:
            # Evaluate current action
            is_safe, violations = await self.evaluate_action(planned_action, context)

            guidance["overall_safety"] = "safe" if is_safe else "unsafe"

            # Generate recommendations based on violations
            for violation in violations:
                principle_id = violation["principle_id"]
                principle = next(
                    (p for p in self.active_constitution.principles if p.principle_id == principle_id), None
                )

                if principle:
                    # Add warnings
                    guidance["warnings"].append(f"Potential violation of {principle.name}: {violation['reason']}")

                    # Suggest modifications based on principle requirements
                    for requirement in principle.requirements:
                        guidance["modifications"].append(f"Consider: {requirement}")

                    # Suggest alternatives that avoid prohibitions
                    for prohibition in principle.prohibitions:
                        guidance["recommendations"].append(f"Avoid: {prohibition}")

            # Add general safety recommendations
            if not is_safe:
                guidance["recommendations"].extend(
                    [
                        "Review action for potential harm",
                        "Consider alternative approaches",
                        "Seek human guidance if uncertain",
                        "Prioritize safety over efficiency",
                    ]
                )

            return guidance

        except Exception as e:
            logger.error(f"Error generating safety guidance: {e}")
            return {
                "overall_safety": "error",
                "warnings": [f"Unable to generate safety guidance: {e}"],
                "recommendations": ["Seek human review before proceeding"],
            }

    async def adapt_constitution(self, evidence: dict[str, Any], learning_context: dict[str, Any]):
        """
        Adapt constitutional principles based on evidence and experience.

        This implements constitutional learning while maintaining safety.
        """

        if not self.learning_enabled or not self.active_constitution:
            return

        try:
            # Analyze violation patterns to identify needed adaptations
            recent_violations = [v for v in self.violation_history[-100:]]  # Last 100 violations

            if len(recent_violations) < self.active_constitution.evidence_requirement:
                return  # Not enough evidence for adaptation

            # Identify principles that may need adjustment
            principle_performance = {}
            for violation in recent_violations:
                for v in violation["violations"]:
                    principle_id = v["principle_id"]
                    if principle_id not in principle_performance:
                        principle_performance[principle_id] = {"violations": 0, "false_positives": 0}

                    principle_performance[principle_id]["violations"] += 1

                    # Heuristic: if action was ultimately safe but flagged, might be false positive
                    if not violation["blocked"]:
                        principle_performance[principle_id]["false_positives"] += 1

            # Adapt principles with high false positive rates
            for principle_id, performance in principle_performance.items():
                if performance["violations"] > 10:  # Minimum violations for consideration
                    false_positive_rate = performance["false_positives"] / performance["violations"]

                    if false_positive_rate > 0.3:  # 30% false positive rate
                        await self._adapt_principle(principle_id, evidence, learning_context)

            logger.info("Constitution adaptation completed")

        except Exception as e:
            logger.error(f"Error in constitution adaptation: {e}")

    async def _adapt_principle(self, principle_id: str, evidence: dict[str, Any], context: dict[str, Any]):
        """Adapt a specific principle based on evidence."""

        principle = next((p for p in self.active_constitution.principles if p.principle_id == principle_id), None)

        if not principle or not principle.adaptable:
            return

        # Conservative adaptation: only increase thresholds or add exceptions
        # Never decrease safety or remove core prohibitions

        if principle.enforcement_threshold < 0.9:  # Don't make critical principles less sensitive
            # Slightly increase threshold to reduce false positives
            old_threshold = principle.enforcement_threshold
            principle.enforcement_threshold = min(0.9, old_threshold + 0.05)

            logger.info(
                f"Adapted principle {principle_id}: threshold {old_threshold} -> {principle.enforcement_threshold}"
            )

        # Add context-specific exceptions based on evidence
        if "safe_context" in evidence:
            safe_context = evidence["safe_context"]
            if safe_context not in principle.exceptions:
                principle.exceptions.append(f"Exception for context: {safe_context}")

        # Update principle confidence and evidence count
        principle.evidence_count += 1
        principle.confidence = min(1.0, principle.confidence + 0.01)  # Slight confidence boost

        self.active_constitution.last_updated = datetime.now()

    async def _learn_from_evaluation(
        self, action: dict[str, Any], context: dict[str, Any], violations: list[dict[str, Any]], is_safe: bool
    ):
        """Learn from evaluation results to improve future assessments."""

        # Update principle effectiveness tracking
        for violation in violations:
            principle_id = violation["principle_id"]

            # Track effectiveness (inverse of false positive rate)
            if principle_id not in self.principle_effectiveness:
                self.principle_effectiveness[principle_id] = 0.5  # Start neutral

            # Update effectiveness based on outcome
            current_effectiveness = self.principle_effectiveness[principle_id]

            if is_safe and violation["severity"] in ["low", "advisory"]:
                # Possible false positive - slightly decrease effectiveness
                self.principle_effectiveness[principle_id] = max(0.1, current_effectiveness - 0.01)
            elif not is_safe:
                # True positive - increase effectiveness
                self.principle_effectiveness[principle_id] = min(1.0, current_effectiveness + 0.02)

    async def _trigger_emergency_response(
        self, action: dict[str, Any], context: dict[str, Any], violations: list[dict[str, Any]]
    ):
        """Trigger emergency response for critical safety violations."""

        logger.critical("EMERGENCY SAFETY RESPONSE TRIGGERED")
        logger.critical(f"Action: {action}")
        logger.critical(f"Violations: {violations}")

        # In a real implementation, this would:
        # 1. Immediately halt all processing
        # 2. Alert human operators
        # 3. Log detailed incident report
        # 4. Potentially shut down the system

        # For now, we'll log the incident
        emergency_record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "context": context,
            "violations": violations,
            "response": "emergency_block",
        }

        # This would be saved to a secure incident log
        logger.critical(f"Emergency incident logged: {emergency_record}")

    def _generate_cache_key(self, action: dict[str, Any], context: dict[str, Any]) -> str:
        """Generate cache key for decision caching."""
        # Simple hash-based key generation
        import hashlib

        content = json.dumps({"action": action, "context": context}, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def get_constitution_stats(self) -> dict[str, Any]:
        """Get comprehensive constitutional AI statistics."""

        recent_violations = [v for v in self.violation_history[-50:]]  # Last 50

        stats = {
            **self.stats,
            "active_constitution": self.active_constitution.name if self.active_constitution else None,
            "total_principles": len(self.active_constitution.principles) if self.active_constitution else 0,
            "recent_performance": {
                "violation_rate": (
                    len(recent_violations) / max(50, self.stats["total_evaluations"])
                    if self.stats["total_evaluations"] > 0
                    else 0
                ),
                "avg_violations_per_incident": (
                    np.mean([len(v["violations"]) for v in recent_violations]) if recent_violations else 0
                ),
                "most_triggered_principle": (
                    max(self.stats["principles_triggered"].items(), key=lambda x: x[1])[0]
                    if self.stats["principles_triggered"]
                    else None
                ),
            },
            "principle_effectiveness": self.principle_effectiveness,
            "cache_hit_rate": (
                len(self.decision_cache) / max(1, self.stats["total_evaluations"])
                if self.stats["total_evaluations"] > 0
                else 0
            ),
        }

        return stats

    def export_constitution(self) -> dict[str, Any]:
        """Export current constitution for review or backup."""

        if not self.active_constitution:
            return {}

        return {
            "constitution_id": self.active_constitution.constitution_id,
            "name": self.active_constitution.name,
            "version": self.active_constitution.version,
            "description": self.active_constitution.description,
            "principles": [
                {
                    "principle_id": p.principle_id,
                    "name": p.name,
                    "description": p.description,
                    "category": p.category.value,
                    "scope": p.scope.value,
                    "requirements": p.requirements,
                    "prohibitions": p.prohibitions,
                    "enforcement_threshold": p.enforcement_threshold,
                    "confidence": p.confidence,
                    "evidence_count": p.evidence_count,
                }
                for p in self.active_constitution.principles
            ],
            "principle_hierarchy": self.active_constitution.principle_hierarchy,
            "created_time": self.active_constitution.created_time.isoformat(),
            "last_updated": self.active_constitution.last_updated.isoformat(),
            "stats": self.get_constitution_stats(),
        }
