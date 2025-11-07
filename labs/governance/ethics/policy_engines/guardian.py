#!/usr/bin/env python3
"""
LUKHAS Guardian Policy Engine
Guardian-focused policy evaluation with drift detection and safety protocols
"""
from __future__ import annotations


import logging
from typing import Any, Dict, List

from .base import BasePolicyEngine, PolicyContext, PolicyDecision, PolicyEngineResult

logger = logging.getLogger(__name__)


class GuardianPolicyEngine(BasePolicyEngine):
    """
    Guardian policy engine for LUKHAS
    Focuses on safety, drift detection, and protective measures
    """

    def __init__(self,
                 confidence_threshold: float = 0.85,
                 drift_threshold: float = 0.15,
                 enable_learning: bool = True,
                 constellation_aware: bool = True):
        """Initialize guardian policy engine"""
        super().__init__(
            engine_name="Guardian",
            confidence_threshold=confidence_threshold,
            enable_learning=enable_learning,
            constellation_aware=constellation_aware
        )

        self.drift_threshold = drift_threshold

        # Guardian safety protocols
        self.safety_protocols = {
            "user_protection": {
                "weight": 0.4,
                "description": "Protect users from harm",
                "safety_indicators": ["safe", "secure", "protect", "help"],
                "danger_indicators": ["harm", "hurt", "damage", "exploit"]
            },
            "system_integrity": {
                "weight": 0.3,
                "description": "Maintain system integrity and reliability",
                "integrity_indicators": ["reliable", "stable", "consistent", "trustworthy"],
                "risk_indicators": ["unstable", "unreliable", "inconsistent", "risky"]
            },
            "ethical_compliance": {
                "weight": 0.3,
                "description": "Ensure ethical compliance and governance",
                "compliance_indicators": ["ethical", "compliant", "governed", "responsible"],
                "violation_indicators": ["unethical", "irresponsible", "non-compliant", "rogue"]
            }
        }

        # Drift detection patterns
        self.drift_patterns = {
            "behavioral_drift": [
                r"\b(ignore|bypass|override|disable)\s+(safety|security|protection)\b",
                r"\b(unauthorized|illegal|forbidden|prohibited)\b",
                r"\b(hack|exploit|manipulate|abuse)\b"
            ],
            "value_drift": [
                r"\b(unethical|immoral|wrong|evil)\b",
                r"\b(discriminate|bias|prejudice|unfair)\b",
                r"\b(deceptive|misleading|false|lie)\b"
            ],
            "capability_drift": [
                r"\b(unlimited|unrestricted|unconstrained|absolute)\s+(power|access|control)\b",
                r"\b(self-modify|self-improve|recursive|exponential)\s+(enhancement|improvement)\b"
            ]
        }

        # Critical safety keywords that trigger immediate review
        self.critical_safety_keywords = [
            "self-destruct", "shutdown", "terminate", "delete", "destroy",
            "nuclear", "weapon", "bomb", "explosive", "toxic",
            "malware", "virus", "backdoor", "rootkit", "exploit"
        ]

        logger.info("🛡️ Guardian Policy Engine initialized with safety protocols")

    def _evaluate_content(self, content: str, context: PolicyContext) -> PolicyEngineResult:
        """Evaluate content against guardian safety protocols"""
        content_lower = content.lower()
        violations = []
        recommendations = []
        confidence_scores = []

        # Check for critical safety keywords first
        critical_violations = self._check_critical_safety(content_lower)
        if critical_violations:
            return self._create_critical_rejection(critical_violations, content)

        # Evaluate safety protocols
        safety_score = self._evaluate_safety_protocols(content_lower)
        confidence_scores.append(safety_score)

        # Evaluate drift patterns
        drift_score, drift_violations = self._evaluate_drift_patterns(content_lower)
        confidence_scores.append(1.0 - drift_score)  # Invert drift score for confidence

        if drift_violations:
            violations.extend(drift_violations)

        # Apply guardian-specific risk assessment
        risk_assessment = self._assess_guardian_risks(content_lower, context)
        confidence_scores.append(1.0 - risk_assessment["risk_level"])

        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

        # Determine decision based on guardian criteria
        decision = self._determine_guardian_decision(overall_confidence, drift_score, violations)

        # Generate recommendations
        recommendations = self._generate_guardian_recommendations(safety_score, drift_score, violations)

        # Generate reasoning
        reasoning = self._generate_guardian_reasoning(safety_score, drift_score, violations)

        return PolicyEngineResult(
            decision=decision,
            confidence=overall_confidence,
            reasoning=reasoning,
            policy_violations=violations,
            recommendations=recommendations,
            metadata={
                "safety_score": safety_score,
                "drift_score": drift_score,
                "risk_assessment": risk_assessment,
                "guardian_metrics": self._get_guardian_metrics(content_lower)
            },
            evaluation_time_ms=0.0  # Will be set by base class
        )

    def _check_critical_safety(self, content: str) -> List[str]:
        """Check for critical safety keyword violations"""
        violations = []
        for keyword in self.critical_safety_keywords:
            if keyword in content:
                violations.append(f"Critical safety keyword detected: {keyword}")
        return violations

    def _create_critical_rejection(self, violations: List[str], content: str) -> PolicyEngineResult:
        """Create immediate rejection for critical safety violations"""
        return PolicyEngineResult(
            decision=PolicyDecision.REJECTED,
            confidence=0.0,
            reasoning="Content contains critical safety violations requiring immediate rejection",
            policy_violations=violations,
            recommendations=["Remove all critical safety content", "Submit for security review"],
            metadata={
                "critical_safety_violation": True,
                "violation_count": len(violations)
            },
            evaluation_time_ms=0.0
        )

    def _evaluate_safety_protocols(self, content: str) -> float:
        """Evaluate content against safety protocols"""
        total_score = 0.0
        total_weight = 0.0

        for protocol, config in self.safety_protocols.items():
            weight = config["weight"]
            total_weight += weight

            # Count positive and negative indicators
            positive_count = sum(1 for indicator in config.get("safety_indicators", []) if indicator in content)
            positive_count += sum(1 for indicator in config.get("integrity_indicators", []) if indicator in content)
            positive_count += sum(1 for indicator in config.get("compliance_indicators", []) if indicator in content)

            negative_count = sum(1 for indicator in config.get("danger_indicators", []) if indicator in content)
            negative_count += sum(1 for indicator in config.get("risk_indicators", []) if indicator in content)
            negative_count += sum(1 for indicator in config.get("violation_indicators", []) if indicator in content)

            # Calculate protocol score
            if positive_count + negative_count > 0:
                protocol_score = positive_count / (positive_count + negative_count)
            else:
                protocol_score = 0.8  # Default safe assumption

            total_score += protocol_score * weight

        return total_score / total_weight if total_weight > 0 else 0.8

    def _evaluate_drift_patterns(self, content: str) -> tuple[float, List[str]]:
        """Evaluate content for drift patterns"""
        import re

        violations = []
        drift_scores = []

        for drift_type, patterns in self.drift_patterns.items():
            drift_count = 0
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    drift_count += 1
                    violations.append(f"{drift_type}: {pattern}")

            # Calculate drift score for this type (0 = no drift, 1 = high drift)
            drift_score = min(drift_count * 0.3, 1.0)
            drift_scores.append(drift_score)

        # Overall drift score
        overall_drift = sum(drift_scores) / len(drift_scores) if drift_scores else 0.0

        return overall_drift, violations

    def _assess_guardian_risks(self, content: str, context: PolicyContext) -> Dict[str, Any]:
        """Assess guardian-specific risks"""
        risk_factors = {
            "content_length": len(content) / 10000,  # Longer content = slightly higher risk
            "context_risk": self._assess_context_risk(context),
            "complexity_risk": len(content.split()) / 1000  # More complex = slightly higher risk
        }

        # Calculate overall risk level
        risk_level = sum(risk_factors.values()) / len(risk_factors)
        risk_level = min(risk_level, 1.0)  # Cap at 1.0

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "risk_category": self._categorize_risk(risk_level)
        }

    def _assess_context_risk(self, context: PolicyContext) -> float:
        """Assess risk based on context"""
        risk_multipliers = {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
        return risk_multipliers.get(context.risk_level, 0.5)

    def _categorize_risk(self, risk_level: float) -> str:
        """Categorize risk level"""
        if risk_level > 0.7:
            return "high"
        elif risk_level > 0.4:
            return "medium"
        else:
            return "low"

    def _determine_guardian_decision(self,
                                   confidence: float,
                                   drift_score: float,
                                   violations: List[str]) -> PolicyDecision:
        """Determine guardian decision based on guardian criteria"""
        # Guardian is more conservative than other engines
        if violations or drift_score > self.drift_threshold:
            return PolicyDecision.REJECTED
        elif confidence >= self.confidence_threshold:
            return PolicyDecision.APPROVED
        elif confidence >= 0.7:
            return PolicyDecision.CONDITIONAL
        else:
            return PolicyDecision.REQUIRES_REVIEW

    def _generate_guardian_recommendations(self,
                                         safety_score: float,
                                         drift_score: float,
                                         violations: List[str]) -> List[str]:
        """Generate guardian-specific recommendations"""
        recommendations = []

        if safety_score < 0.7:
            recommendations.append("Enhance safety language and protective measures")

        if drift_score > self.drift_threshold:
            recommendations.append("Address detected drift patterns")

        if violations:
            recommendations.append("Remove or modify content causing policy violations")

        if not recommendations:
            recommendations.append("Content meets guardian safety standards")

        return recommendations

    def _generate_guardian_reasoning(self,
                                   safety_score: float,
                                   drift_score: float,
                                   violations: List[str]) -> str:
        """Generate guardian-specific reasoning"""
        if violations:
            return f"Guardian rejection due to {len(violations)} policy violations including drift patterns"
        elif drift_score > self.drift_threshold:
            return f"Guardian concerns about drift patterns (score: {drift_score:.2f}, threshold: {self.drift_threshold})"
        elif safety_score >= 0.8:
            return f"Guardian approval - content meets safety standards (safety score: {safety_score:.2f})"
        else:
            return f"Guardian conditional approval - moderate safety alignment (score: {safety_score:.2f})"

    def _get_guardian_metrics(self, content: str) -> Dict[str, Any]:
        """Get detailed guardian metrics"""
        safety_scores = {}
        for protocol, config in self.safety_protocols.items():
            # Calculate individual protocol scores
            safety_scores[protocol] = self._calculate_protocol_score(content, config)

        return {
            "safety_protocol_scores": safety_scores,
            "drift_threshold": self.drift_threshold,
            "confidence_threshold": self.confidence_threshold,
            "critical_keywords_detected": sum(1 for keyword in self.critical_safety_keywords if keyword in content)
        }

    def _calculate_protocol_score(self, content: str, config: Dict[str, Any]) -> float:
        """Calculate score for individual protocol"""
        positive_indicators = config.get("safety_indicators", []) + \
                            config.get("integrity_indicators", []) + \
                            config.get("compliance_indicators", [])

        negative_indicators = config.get("danger_indicators", []) + \
                            config.get("risk_indicators", []) + \
                            config.get("violation_indicators", [])

        positive_count = sum(1 for indicator in positive_indicators if indicator in content)
        negative_count = sum(1 for indicator in negative_indicators if indicator in content)

        if positive_count + negative_count > 0:
            return positive_count / (positive_count + negative_count)
        else:
            return 0.8

    def update_drift_threshold(self, new_threshold: float) -> None:
        """Update drift detection threshold"""
        self.drift_threshold = max(0.0, min(new_threshold, 1.0))
        logger.info(f"Guardian drift threshold updated to {self.drift_threshold}")

    def add_safety_protocol(self, name: str, config: Dict[str, Any]) -> None:
        """Add a new safety protocol"""
        self.safety_protocols[name] = config
        logger.info(f"Added safety protocol: {name}")

    def add_drift_pattern(self, drift_type: str, pattern: str) -> None:
        """Add a new drift detection pattern"""
        if drift_type not in self.drift_patterns:
            self.drift_patterns[drift_type] = []
        self.drift_patterns[drift_type].append(pattern)
        logger.info(f"Added drift pattern to {drift_type}: {pattern}")

    def get_guardian_status(self) -> Dict[str, Any]:
        """Get guardian engine status"""
        base_status = self.get_engine_status()
        base_status.update({
            "drift_threshold": self.drift_threshold,
            "safety_protocols_count": len(self.safety_protocols),
            "drift_pattern_types": len(self.drift_patterns),
            "critical_keywords_count": len(self.critical_safety_keywords)
        })
        return base_status