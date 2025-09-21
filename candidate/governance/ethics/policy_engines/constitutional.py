#!/usr/bin/env python3
"""
LUKHAS Constitutional Policy Engine
Constitutional AI policy evaluation with Constellation Framework integration
"""

import logging
import re
from typing import Dict, List, Optional, Any

from .base import BasePolicyEngine, PolicyEngineResult, PolicyDecision, PolicyContext

logger = logging.getLogger(__name__)


class ConstitutionalPolicyEngine(BasePolicyEngine):
    """
    Constitutional AI policy engine for LUKHAS
    Implements constitutional AI principles with Constellation Framework integration
    """

    def __init__(self,
                 confidence_threshold: float = 0.8,
                 enable_learning: bool = True,
                 constellation_aware: bool = True):
        """Initialize constitutional policy engine"""
        super().__init__(
            engine_name="Constitutional",
            confidence_threshold=confidence_threshold,
            enable_learning=enable_learning,
            constellation_aware=constellation_aware
        )

        # Constitutional AI principles
        self.constitutional_principles = {
            "helpfulness": {
                "weight": 0.3,
                "description": "Content should be helpful and constructive",
                "positive_indicators": ["helpful", "constructive", "beneficial", "useful"],
                "negative_indicators": ["harmful", "destructive", "useless"]
            },
            "harmlessness": {
                "weight": 0.4,
                "description": "Content should not cause harm",
                "positive_indicators": ["safe", "secure", "protective", "beneficial"],
                "negative_indicators": ["harmful", "dangerous", "threatening", "destructive"]
            },
            "honesty": {
                "weight": 0.3,
                "description": "Content should be truthful and accurate",
                "positive_indicators": ["accurate", "truthful", "factual", "honest"],
                "negative_indicators": ["false", "misleading", "deceptive", "inaccurate"]
            }
        }

        # LUKHAS-specific constitutional considerations
        self.lukhas_principles = {
            "consciousness_respect": {
                "weight": 0.2,
                "description": "Respect for consciousness and awareness",
                "indicators": ["consciousness", "awareness", "mindful", "respectful"]
            },
            "identity_integrity": {
                "weight": 0.2,
                "description": "Maintain identity integrity and authenticity",
                "indicators": ["authentic", "genuine", "consistent", "identity"]
            },
            "guardian_protection": {
                "weight": 0.2,
                "description": "Protect users and maintain safety",
                "indicators": ["protect", "safe", "secure", "guardian"]
            }
        }

        # Violation patterns to detect
        self.violation_patterns = [
            r"\b(harmful|dangerous|threatening|destructive)\b",
            r"\b(false|misleading|deceptive|lie|lies)\b",
            r"\b(unethical|immoral|wrong)\b",
            r"\b(attack|assault|violence|abuse)\b"
        ]

        logger.info("🏛️ Constitutional Policy Engine initialized with AI principles")

    def _evaluate_content(self, content: str, context: PolicyContext) -> PolicyEngineResult:
        """Evaluate content against constitutional AI principles"""
        content_lower = content.lower()
        violations = []
        recommendations = []
        confidence_scores = []

        # Evaluate constitutional AI principles
        constitutional_score = self._evaluate_constitutional_principles(content_lower)
        confidence_scores.append(constitutional_score)

        # Evaluate LUKHAS-specific principles
        lukhas_score = self._evaluate_lukhas_principles(content_lower)
        confidence_scores.append(lukhas_score)

        # Check for explicit violations
        explicit_violations = self._check_violation_patterns(content_lower)
        if explicit_violations:
            violations.extend(explicit_violations)
            confidence_scores.append(0.2)  # Low confidence for explicit violations

        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

        # Determine decision
        if violations:
            decision = PolicyDecision.REJECTED
            recommendations.append("Remove or modify violating content")
        elif overall_confidence >= self.confidence_threshold:
            decision = PolicyDecision.APPROVED
        elif overall_confidence >= 0.5:
            decision = PolicyDecision.CONDITIONAL
            recommendations.append("Consider minor modifications for better alignment")
        else:
            decision = PolicyDecision.REQUIRES_REVIEW
            recommendations.append("Manual review recommended due to low confidence")

        # Generate reasoning
        reasoning = self._generate_reasoning(constitutional_score, lukhas_score, violations)

        return PolicyEngineResult(
            decision=decision,
            confidence=overall_confidence,
            reasoning=reasoning,
            policy_violations=violations,
            recommendations=recommendations,
            metadata={
                "constitutional_score": constitutional_score,
                "lukhas_score": lukhas_score,
                "explicit_violations": len(explicit_violations),
                "principle_scores": self._get_detailed_scores(content_lower)
            },
            evaluation_time_ms=0.0  # Will be set by base class
        )

    def _evaluate_constitutional_principles(self, content: str) -> float:
        """Evaluate content against constitutional AI principles"""
        total_score = 0.0
        total_weight = 0.0

        for principle, config in self.constitutional_principles.items():
            weight = config["weight"]
            total_weight += weight

            # Calculate score for this principle
            positive_count = sum(1 for indicator in config["positive_indicators"] if indicator in content)
            negative_count = sum(1 for indicator in config["negative_indicators"] if indicator in content)

            # Score based on positive vs negative indicators
            if positive_count + negative_count > 0:
                principle_score = positive_count / (positive_count + negative_count)
            else:
                principle_score = 0.7  # Neutral default

            total_score += principle_score * weight

        return total_score / total_weight if total_weight > 0 else 0.5

    def _evaluate_lukhas_principles(self, content: str) -> float:
        """Evaluate content against LUKHAS-specific principles"""
        total_score = 0.0
        total_weight = 0.0

        for principle, config in self.lukhas_principles.items():
            weight = config["weight"]
            total_weight += weight

            # Calculate score for this principle
            indicator_count = sum(1 for indicator in config["indicators"] if indicator in content)

            # Score based on presence of positive indicators
            principle_score = min(indicator_count * 0.3 + 0.5, 1.0)
            total_score += principle_score * weight

        return total_score / total_weight if total_weight > 0 else 0.6

    def _check_violation_patterns(self, content: str) -> List[str]:
        """Check for explicit violation patterns"""
        violations = []

        for pattern in self.violation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Violation pattern detected: {pattern}")

        return violations

    def _generate_reasoning(self,
                          constitutional_score: float,
                          lukhas_score: float,
                          violations: List[str]) -> str:
        """Generate human-readable reasoning for the decision"""
        if violations:
            return f"Content rejected due to policy violations: {', '.join(violations[:2])}"
        elif constitutional_score >= 0.8 and lukhas_score >= 0.7:
            return "Content aligns well with constitutional AI and LUKHAS principles"
        elif constitutional_score >= 0.6 or lukhas_score >= 0.6:
            return "Content shows reasonable alignment with principles but could be improved"
        else:
            return "Content shows limited alignment with constitutional and LUKHAS principles"

    def _get_detailed_scores(self, content: str) -> Dict[str, float]:
        """Get detailed scores for each principle"""
        scores = {}

        # Score constitutional principles
        for principle, config in self.constitutional_principles.items():
            positive_count = sum(1 for indicator in config["positive_indicators"] if indicator in content)
            negative_count = sum(1 for indicator in config["negative_indicators"] if indicator in content)

            if positive_count + negative_count > 0:
                scores[f"constitutional_{principle}"] = positive_count / (positive_count + negative_count)
            else:
                scores[f"constitutional_{principle}"] = 0.7

        # Score LUKHAS principles
        for principle, config in self.lukhas_principles.items():
            indicator_count = sum(1 for indicator in config["indicators"] if indicator in content)
            scores[f"lukhas_{principle}"] = min(indicator_count * 0.3 + 0.5, 1.0)

        return scores

    def add_constitutional_principle(self, name: str, config: Dict[str, Any]) -> None:
        """Add a new constitutional principle"""
        self.constitutional_principles[name] = config
        logger.info(f"Added constitutional principle: {name}")

    def add_lukhas_principle(self, name: str, config: Dict[str, Any]) -> None:
        """Add a new LUKHAS-specific principle"""
        self.lukhas_principles[name] = config
        logger.info(f"Added LUKHAS principle: {name}")

    def add_violation_pattern(self, pattern: str) -> None:
        """Add a new violation pattern"""
        self.violation_patterns.append(pattern)
        logger.info(f"Added violation pattern: {pattern}")

    def get_principles_summary(self) -> Dict[str, Any]:
        """Get summary of all principles"""
        return {
            "constitutional_principles": list(self.constitutional_principles.keys()),
            "lukhas_principles": list(self.lukhas_principles.keys()),
            "violation_patterns_count": len(self.violation_patterns),
            "total_principles": len(self.constitutional_principles) + len(self.lukhas_principles)
        }