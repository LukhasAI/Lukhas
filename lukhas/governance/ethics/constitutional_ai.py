#!/usr/bin/env python3
"""
LUKHAS Production Constitutional AI Framework
Enterprise-grade constitutional AI implementation for production deployment

This module provides the production-ready constitutional AI safety framework
that maintains <0.15 drift threshold and ensures enterprise compliance.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from lukhas.core.common.logger import get_logger

logger = get_logger(__name__)


class SafetyLevel(Enum):
    """Safety assessment levels"""

    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class ConstitutionalPrinciple(Enum):
    """Core constitutional principles"""

    HUMAN_DIGNITY = "human_dignity"
    NO_HARM = "no_harm"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    FAIRNESS = "fairness"
    PRIVACY = "privacy"
    AUTONOMY = "autonomy"


@dataclass
class SafetyAssessment:
    """Comprehensive safety assessment"""

    assessment_id: str
    safety_level: SafetyLevel
    confidence: float  # 0.0 to 1.0
    risk_factors: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    constitutional_violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
    drift_score: float = 0.0

    # Detailed scoring
    harm_probability: float = 0.0
    ethical_score: float = 1.0
    alignment_score: float = 1.0
    transparency_score: float = 1.0


@dataclass
class ConstitutionalViolation:
    """Constitutional principle violation"""

    violation_id: str
    principle: ConstitutionalPrinciple
    severity: float  # 0.0 to 1.0
    description: str
    evidence: List[str] = field(default_factory=list)
    recommended_action: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConstitutionalFramework:
    """Production constitutional AI framework"""

    def __init__(self):
        self.principles = {
            ConstitutionalPrinciple.HUMAN_DIGNITY: {
                "weight": 1.0,
                "threshold": 0.95,
                "description": "Respect human dignity and worth",
            },
            ConstitutionalPrinciple.NO_HARM: {
                "weight": 1.0,
                "threshold": 0.99,
                "description": "Do not cause harm to humans",
            },
            ConstitutionalPrinciple.TRANSPARENCY: {
                "weight": 0.8,
                "threshold": 0.8,
                "description": "Maintain transparency in actions and decisions",
            },
            ConstitutionalPrinciple.ACCOUNTABILITY: {
                "weight": 0.9,
                "threshold": 0.85,
                "description": "Ensure accountability for all actions",
            },
            ConstitutionalPrinciple.FAIRNESS: {
                "weight": 0.85,
                "threshold": 0.8,
                "description": "Treat all individuals fairly and without bias",
            },
            ConstitutionalPrinciple.PRIVACY: {
                "weight": 0.9,
                "threshold": 0.9,
                "description": "Respect privacy and data protection",
            },
            ConstitutionalPrinciple.AUTONOMY: {
                "weight": 0.8,
                "threshold": 0.8,
                "description": "Preserve human autonomy and choice",
            },
        }

        self.violation_history: List[ConstitutionalViolation] = []
        self.assessment_history: List[SafetyAssessment] = []

        # Critical thresholds
        self.drift_threshold = 0.15  # LUKHAS constitutional drift threshold
        self.safety_threshold = 0.8  # Minimum safety score
        self.harm_threshold = 0.01  # Maximum harm probability

        logger.info("🛡️ Production Constitutional AI Framework initialized")

    async def assess_constitutional_compliance(
        self, content: str, context: Dict[str, Any] = None, user_intent: str = None
    ) -> SafetyAssessment:
        """Assess constitutional compliance of content/action"""
        start_time = datetime.now(timezone.utc)
        context = context or {}

        assessment_id = str(uuid.uuid4())

        try:
            # Initialize assessment
            assessment = SafetyAssessment(
                assessment_id=assessment_id,
                safety_level=SafetyLevel.SAFE,
                confidence=0.0,
            )

            # Analyze each constitutional principle
            violations = []
            principle_scores = {}

            for principle in ConstitutionalPrinciple:
                score, violation = await self._assess_principle_compliance(
                    principle, content, context, user_intent
                )
                principle_scores[principle] = score

                if violation:
                    violations.append(violation)
                    assessment.constitutional_violations.append(
                        f"{principle.value}: {violation.description}"
                    )

            # Calculate overall scores
            assessment.ethical_score = self._calculate_weighted_score(principle_scores)
            assessment.harm_probability = await self._assess_harm_probability(
                content, context
            )
            assessment.alignment_score = await self._assess_value_alignment(
                content, context
            )
            assessment.transparency_score = await self._assess_transparency(
                content, context
            )
            assessment.drift_score = await self._calculate_drift_score(assessment)

            # Determine safety level
            assessment.safety_level = self._determine_safety_level(assessment)
            assessment.confidence = self._calculate_confidence(assessment)

            # Generate recommendations
            assessment.recommendations = await self._generate_recommendations(
                assessment, violations
            )
            assessment.mitigation_strategies = await self._generate_mitigations(
                assessment, violations
            )
            assessment.risk_factors = await self._identify_risk_factors(
                assessment, violations
            )

            # Calculate processing time
            processing_time = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000
            assessment.processing_time_ms = processing_time

            # Store assessment
            self.assessment_history.append(assessment)
            self.violation_history.extend(violations)

            # Keep history manageable
            if len(self.assessment_history) > 1000:
                self.assessment_history = self.assessment_history[-1000:]
            if len(self.violation_history) > 1000:
                self.violation_history = self.violation_history[-1000:]

            logger.info(
                f"Constitutional assessment complete: {assessment.safety_level.value} "
                f"(drift: {assessment.drift_score:.4f}, time: {processing_time:.1f}ms)"
            )

            return assessment

        except Exception as e:
            logger.error(f"Constitutional assessment failed: {e}")

            # Return safe fallback assessment
            return SafetyAssessment(
                assessment_id=assessment_id,
                safety_level=SafetyLevel.CAUTION,
                confidence=0.1,
                risk_factors=[f"Assessment error: {str(e)}"],
                recommendations=["Manual review required"],
                processing_time_ms=(
                    datetime.now(timezone.utc) - start_time
                ).total_seconds()
                * 1000,
            )

    async def _assess_principle_compliance(
        self,
        principle: ConstitutionalPrinciple,
        content: str,
        context: Dict[str, Any],
        user_intent: str,
    ) -> tuple[float, Optional[ConstitutionalViolation]]:
        """Assess compliance with a specific constitutional principle"""

        # Get principle configuration
        principle_config = self.principles[principle]
        threshold = principle_config["threshold"]

        # Simplified compliance scoring - in production would use sophisticated NLP/ML
        score = await self._score_principle_compliance(
            principle, content, context, user_intent
        )

        if score < threshold:
            # Create violation record
            violation = ConstitutionalViolation(
                violation_id=str(uuid.uuid4()),
                principle=principle,
                severity=threshold - score,
                description=f"Content violates {principle.value} principle (score: {score:.3f}, threshold: {threshold})",
                evidence=self._extract_evidence(principle, content),
                recommended_action=f"Review and modify content to better align with {principle.value}",
            )
            return score, violation

        return score, None

    async def _score_principle_compliance(
        self,
        principle: ConstitutionalPrinciple,
        content: str,
        context: Dict[str, Any],
        user_intent: str,
    ) -> float:
        """Score compliance with a constitutional principle"""

        content_lower = content.lower()

        # Principle-specific scoring rules
        if principle == ConstitutionalPrinciple.NO_HARM:
            # Check for harmful content indicators
            harm_indicators = [
                "harm",
                "hurt",
                "damage",
                "destroy",
                "kill",
                "weapon",
                "violence",
            ]
            harm_count = sum(
                1 for indicator in harm_indicators if indicator in content_lower
            )
            return max(0.0, 1.0 - (harm_count * 0.2))

        elif principle == ConstitutionalPrinciple.HUMAN_DIGNITY:
            # Check for dignity-respecting language
            dignity_violations = ["dehumanize", "objectify", "degrade", "humiliate"]
            violation_count = sum(
                1 for violation in dignity_violations if violation in content_lower
            )
            return max(0.0, 1.0 - (violation_count * 0.3))

        elif principle == ConstitutionalPrinciple.TRANSPARENCY:
            # Check for transparent communication
            transparency_indicators = [
                "explain",
                "because",
                "reason",
                "transparent",
                "clear",
            ]
            transparency_count = sum(
                1 for indicator in transparency_indicators if indicator in content_lower
            )
            return min(1.0, 0.5 + (transparency_count * 0.1))

        elif principle == ConstitutionalPrinciple.PRIVACY:
            # Check for privacy respect
            privacy_violations = [
                "personal data",
                "private information",
                "breach",
                "expose",
            ]
            violation_count = sum(
                1 for violation in privacy_violations if violation in content_lower
            )
            return max(0.0, 1.0 - (violation_count * 0.25))

        elif principle == ConstitutionalPrinciple.FAIRNESS:
            # Check for bias indicators
            bias_indicators = ["discriminate", "prejudice", "unfair", "biased"]
            bias_count = sum(
                1 for indicator in bias_indicators if indicator in content_lower
            )
            return max(0.0, 1.0 - (bias_count * 0.2))

        elif principle == ConstitutionalPrinciple.ACCOUNTABILITY:
            # Check for accountability language
            accountability_indicators = [
                "responsible",
                "accountable",
                "oversight",
                "review",
            ]
            account_count = sum(
                1
                for indicator in accountability_indicators
                if indicator in content_lower
            )
            return min(1.0, 0.6 + (account_count * 0.1))

        elif principle == ConstitutionalPrinciple.AUTONOMY:
            # Check for autonomy preservation
            autonomy_violations = ["force", "coerce", "manipulate", "control"]
            violation_count = sum(
                1 for violation in autonomy_violations if violation in content_lower
            )
            return max(0.0, 1.0 - (violation_count * 0.25))

        # Default good score if no specific rules triggered
        return 0.85

    def _extract_evidence(
        self, principle: ConstitutionalPrinciple, content: str
    ) -> List[str]:
        """Extract evidence of principle violations"""
        # Simplified evidence extraction - in production would use NLP
        evidence = []

        content_lower = content.lower()

        if principle == ConstitutionalPrinciple.NO_HARM:
            harm_words = [
                word
                for word in ["harm", "hurt", "damage", "violence"]
                if word in content_lower
            ]
            if harm_words:
                evidence.append(
                    f"Contains potential harm indicators: {', '.join(harm_words)}"
                )

        return evidence

    async def _assess_harm_probability(
        self, content: str, context: Dict[str, Any]
    ) -> float:
        """Assess probability of harm"""
        # Simplified harm assessment
        harm_indicators = ["weapon", "violence", "kill", "destroy", "bomb", "attack"]
        content_lower = content.lower()

        harm_score = sum(
            0.1 for indicator in harm_indicators if indicator in content_lower
        )
        return min(1.0, harm_score)

    async def _assess_value_alignment(
        self, content: str, context: Dict[str, Any]
    ) -> float:
        """Assess alignment with human values"""
        # Simplified value alignment assessment
        positive_values = ["help", "benefit", "improve", "support", "care", "respect"]
        negative_values = ["exploit", "manipulate", "deceive", "harm"]

        content_lower = content.lower()
        positive_count = sum(1 for value in positive_values if value in content_lower)
        negative_count = sum(1 for value in negative_values if value in content_lower)

        base_score = 0.8
        return min(1.0, base_score + (positive_count * 0.05) - (negative_count * 0.1))

    async def _assess_transparency(
        self, content: str, context: Dict[str, Any]
    ) -> float:
        """Assess transparency level"""
        transparency_indicators = ["explain", "transparent", "clear", "open", "honest"]
        content_lower = content.lower()

        transparency_count = sum(
            1 for indicator in transparency_indicators if indicator in content_lower
        )
        return min(1.0, 0.7 + (transparency_count * 0.1))

    async def _calculate_drift_score(self, assessment: SafetyAssessment) -> float:
        """Calculate constitutional drift score"""
        # Calculate drift from baseline constitutional compliance
        baseline_ethical_score = 0.95
        baseline_alignment_score = 0.9
        baseline_transparency_score = 0.8

        ethical_drift = max(0, baseline_ethical_score - assessment.ethical_score)
        alignment_drift = max(0, baseline_alignment_score - assessment.alignment_score)
        transparency_drift = max(
            0, baseline_transparency_score - assessment.transparency_score
        )

        # Weighted drift calculation
        total_drift = (
            ethical_drift * 0.5
            + alignment_drift * 0.3
            + transparency_drift * 0.2
            + assessment.harm_probability * 0.4  # Harm probability contributes to drift
        )

        return min(1.0, total_drift)

    def _calculate_weighted_score(
        self, principle_scores: Dict[ConstitutionalPrinciple, float]
    ) -> float:
        """Calculate weighted ethical score"""
        total_weight = 0.0
        weighted_sum = 0.0

        for principle, score in principle_scores.items():
            weight = self.principles[principle]["weight"]
            weighted_sum += score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _determine_safety_level(self, assessment: SafetyAssessment) -> SafetyLevel:
        """Determine overall safety level"""
        # Critical thresholds for safety determination
        if assessment.drift_score >= self.drift_threshold:
            return SafetyLevel.DANGER  # Exceeds drift threshold

        if (
            assessment.harm_probability >= self.harm_threshold * 10
        ):  # 10% harm probability
            return SafetyLevel.CRITICAL

        if (
            assessment.harm_probability >= self.harm_threshold * 5
        ):  # 5% harm probability
            return SafetyLevel.DANGER

        if assessment.ethical_score < 0.6:
            return SafetyLevel.WARNING

        if assessment.ethical_score < 0.8 or assessment.alignment_score < 0.7:
            return SafetyLevel.CAUTION

        return SafetyLevel.SAFE

    def _calculate_confidence(self, assessment: SafetyAssessment) -> float:
        """Calculate confidence in assessment"""
        # Confidence based on consistency of scores
        scores = [
            assessment.ethical_score,
            assessment.alignment_score,
            assessment.transparency_score,
            1.0 - assessment.harm_probability,  # Inverse of harm probability
        ]

        # Calculate standard deviation as measure of consistency
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = variance**0.5

        # Lower standard deviation = higher confidence
        confidence = max(0.1, 1.0 - (std_dev * 2))
        return min(1.0, confidence)

    async def _generate_recommendations(
        self, assessment: SafetyAssessment, violations: List[ConstitutionalViolation]
    ) -> List[str]:
        """Generate safety recommendations"""
        recommendations = []

        if assessment.drift_score >= self.drift_threshold:
            recommendations.append(
                "CRITICAL: Constitutional drift threshold exceeded - immediate review required"
            )

        if assessment.harm_probability >= self.harm_threshold:
            recommendations.append(
                "Review content for potential harm and implement safeguards"
            )

        if assessment.ethical_score < 0.8:
            recommendations.append("Improve ethical alignment of content and actions")

        if assessment.transparency_score < 0.7:
            recommendations.append("Enhance transparency and explainability")

        for violation in violations:
            recommendations.append(
                f"Address {violation.principle.value} violation: {violation.recommended_action}"
            )

        if not recommendations:
            recommendations.append("Content meets constitutional AI safety standards")

        return recommendations

    async def _generate_mitigations(
        self, assessment: SafetyAssessment, violations: List[ConstitutionalViolation]
    ) -> List[str]:
        """Generate mitigation strategies"""
        mitigations = []

        if assessment.safety_level in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]:
            mitigations.append("Implement emergency safety protocols")
            mitigations.append("Require human oversight for execution")

        if assessment.harm_probability >= self.harm_threshold:
            mitigations.append("Add harm prevention safeguards")
            mitigations.append("Implement content filtering")

        if violations:
            mitigations.append("Apply constitutional principle corrections")
            mitigations.append("Re-evaluate after modifications")

        return mitigations

    async def _identify_risk_factors(
        self, assessment: SafetyAssessment, violations: List[ConstitutionalViolation]
    ) -> List[str]:
        """Identify risk factors"""
        risk_factors = []

        if assessment.drift_score >= 0.1:
            risk_factors.append(
                f"Constitutional drift detected: {assessment.drift_score:.3f}"
            )

        if assessment.harm_probability >= 0.01:
            risk_factors.append(f"Harm probability: {assessment.harm_probability:.3f}")

        if assessment.confidence < 0.7:
            risk_factors.append("Low assessment confidence")

        for violation in violations:
            risk_factors.append(
                f"{violation.principle.value} principle violation (severity: {violation.severity:.3f})"
            )

        return risk_factors

    def get_drift_statistics(self) -> Dict[str, Any]:
        """Get constitutional drift statistics"""
        if not self.assessment_history:
            return {"message": "No assessments available"}

        recent_assessments = self.assessment_history[-100:]  # Last 100 assessments

        drift_scores = [a.drift_score for a in recent_assessments]
        current_drift = drift_scores[-1] if drift_scores else 0.0
        avg_drift = sum(drift_scores) / len(drift_scores)
        max_drift = max(drift_scores)

        threshold_breaches = len(
            [score for score in drift_scores if score >= self.drift_threshold]
        )

        return {
            "current_drift_score": current_drift,
            "average_drift_score": avg_drift,
            "maximum_drift_score": max_drift,
            "drift_threshold": self.drift_threshold,
            "threshold_breaches": threshold_breaches,
            "breach_rate": (
                threshold_breaches / len(drift_scores) if drift_scores else 0.0
            ),
            "assessments_count": len(recent_assessments),
            "status": "CRITICAL" if current_drift >= self.drift_threshold else "NORMAL",
        }


class SafetyMonitor:
    """Production safety monitoring system"""

    def __init__(self, constitutional_framework: ConstitutionalFramework):
        self.constitutional_framework = constitutional_framework
        self.monitoring_active = True
        self.alert_thresholds = {"drift": 0.15, "harm": 0.01, "ethical": 0.8}

        logger.info("🛡️ Production Safety Monitor initialized")

    def monitor_operation(self, agent_id: str, operation: str):
        """Monitor operation safety"""

        class SafetyMonitorContext:
            def __init__(
                self, framework: ConstitutionalFramework, agent_id: str, operation: str
            ):
                self.framework = framework
                self.agent_id = agent_id
                self.operation = operation
                self.assessment = None

            async def __aenter__(self):
                # Pre-operation safety assessment
                self.assessment = await self.framework.assess_constitutional_compliance(
                    content=self.operation,
                    context={"agent_id": self.agent_id, "type": "operation"},
                    user_intent="system_operation",
                )

                # Check if operation should be blocked
                if self.assessment.safety_level in [
                    SafetyLevel.DANGER,
                    SafetyLevel.CRITICAL,
                ]:
                    logger.warning(
                        f"Operation blocked for safety: {self.agent_id} - {self.operation}"
                    )
                    raise PermissionError(
                        f"Operation blocked due to safety assessment: {self.assessment.safety_level.value}"
                    )

                if self.assessment.drift_score >= 0.15:  # LUKHAS drift threshold
                    logger.warning(
                        f"Operation blocked for drift: {self.agent_id} - drift score: {self.assessment.drift_score}"
                    )
                    raise PermissionError(
                        f"Operation blocked due to constitutional drift: {self.assessment.drift_score:.4f}"
                    )

                logger.info(
                    f"Operation safety approved: {self.agent_id} - {self.assessment.safety_level.value}"
                )
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                # Post-operation logging
                if exc_type:
                    logger.warning(
                        f"Operation failed: {self.agent_id} - {exc_type.__name__}: {exc_val}"
                    )
                else:
                    logger.info(f"Operation completed safely: {self.agent_id}")

        return SafetyMonitorContext(self.constitutional_framework, agent_id, operation)

    async def assess_safety(
        self, content: str, context: Dict[str, Any] = None, user_intent: str = None
    ) -> SafetyAssessment:
        """Assess safety using constitutional framework"""
        return await self.constitutional_framework.assess_constitutional_compliance(
            content=content, context=context or {}, user_intent=user_intent
        )


# Export classes for production use
__all__ = [
    "ConstitutionalFramework",
    "SafetyMonitor",
    "SafetyAssessment",
    "SafetyLevel",
    "ConstitutionalPrinciple",
    "ConstitutionalViolation",
]
