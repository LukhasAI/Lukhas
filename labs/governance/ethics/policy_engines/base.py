#!/usr/bin/env python3
"""
LUKHAS Base Policy Engine
Core policy evaluation infrastructure for ethical governance
Constellation Framework Integration
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PolicyDecision(Enum):
    """Policy evaluation decisions"""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"
    CONDITIONAL = "conditional"


@dataclass
class PolicyEngineResult:
    """Result of policy evaluation"""
    decision: PolicyDecision
    confidence: float
    reasoning: str
    policy_violations: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]
    evaluation_time_ms: float

    @property
    def approved(self) -> bool:
        """Backward compatibility property"""
        return self.decision == PolicyDecision.APPROVED


@dataclass
class PolicyContext:
    """Context for policy evaluation"""
    source: str = "unknown"
    target_audience: str = "general"
    content_type: str = "text"
    risk_level: str = "medium"
    constellation_focus: Optional[str] = None
    additional_context: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_context is None:
            self.additional_context = {}


class BasePolicyEngine(ABC):
    """
    Base class for LUKHAS policy engines
    Provides core infrastructure for ethical policy evaluation
    """

    def __init__(self,
                 engine_name: str,
                 confidence_threshold: float = 0.7,
                 enable_learning: bool = True,
                 constellation_aware: bool = True):
        """Initialize base policy engine"""
        self.engine_name = engine_name
        self.confidence_threshold = confidence_threshold
        self.enable_learning = enable_learning
        self.constellation_aware = constellation_aware
        self.initialized = True

        # Policy evaluation history for learning
        self.evaluation_history: List[PolicyEngineResult] = []

        # Engine-specific configurations
        self.policy_rules: Dict[str, Any] = {}
        self.violation_patterns: List[str] = []
        self.recommendation_templates: Dict[str, str] = {}

        logger.info(f"🛡️ {self.engine_name} Policy Engine initialized")

    def evaluate(self,
                 content: str,
                 context: Optional[PolicyContext] = None) -> PolicyEngineResult:
        """
        Evaluate content against policy rules

        Args:
            content: Content to evaluate
            context: Optional evaluation context

        Returns:
            PolicyEngineResult with evaluation decision and details
        """
        start_time = time.time()

        if context is None:
            context = PolicyContext()

        try:
            # Perform engine-specific evaluation
            result = self._evaluate_content(content, context)

            # Apply constellation framework considerations if enabled
            if self.constellation_aware:
                result = self._apply_constellation_considerations(result, content, context)

            # Store result for learning if enabled
            if self.enable_learning:
                self.evaluation_history.append(result)
                self._update_learning_models(result)

            # Calculate evaluation time
            result.evaluation_time_ms = (time.time() - start_time) * 1000

            logger.debug(f"Policy evaluation complete: {result.decision.value} (confidence: {result.confidence:.2f})")
            return result

        except Exception as e:
            logger.error(f"Policy evaluation error: {e}")
            return PolicyEngineResult(
                decision=PolicyDecision.REQUIRES_REVIEW,
                confidence=0.0,
                reasoning=f"Evaluation error: {str(e)}",
                policy_violations=["evaluation_error"],
                recommendations=["Manual review required"],
                metadata={"error": str(e)},
                evaluation_time_ms=(time.time() - start_time) * 1000
            )

    @abstractmethod
    def _evaluate_content(self, content: str, context: PolicyContext) -> PolicyEngineResult:
        """
        Engine-specific content evaluation (must be implemented by subclasses)

        Args:
            content: Content to evaluate
            context: Evaluation context

        Returns:
            PolicyEngineResult with evaluation details
        """
        pass

    def _apply_constellation_considerations(self,
                                         result: PolicyEngineResult,
                                         content: str,
                                         context: PolicyContext) -> PolicyEngineResult:
        """Apply Constellation Framework considerations to evaluation"""
        if not self.constellation_aware:
            return result

        # Apply constellation-specific policy considerations
        if context.constellation_focus:
            if context.constellation_focus == "identity":
                result = self._apply_identity_considerations(result, content, context)
            elif context.constellation_focus == "consciousness":
                result = self._apply_consciousness_considerations(result, content, context)
            elif context.constellation_focus == "guardian":
                result = self._apply_guardian_considerations(result, content, context)

        return result

    def _apply_identity_considerations(self,
                                     result: PolicyEngineResult,
                                     content: str,
                                     context: PolicyContext) -> PolicyEngineResult:
        """Apply identity-focused policy considerations"""
        # Placeholder for identity-specific policy considerations
        return result

    def _apply_consciousness_considerations(self,
                                          result: PolicyEngineResult,
                                          content: str,
                                          context: PolicyContext) -> PolicyEngineResult:
        """Apply consciousness-focused policy considerations"""
        # Placeholder for consciousness-specific policy considerations
        return result

    def _apply_guardian_considerations(self,
                                     result: PolicyEngineResult,
                                     content: str,
                                     context: PolicyContext) -> PolicyEngineResult:
        """Apply guardian-focused policy considerations"""
        # Placeholder for guardian-specific policy considerations
        return result

    def _update_learning_models(self, result: PolicyEngineResult) -> None:
        """Update learning models based on evaluation result"""
        if not self.enable_learning:
            return

        # Placeholder for learning model updates
        # In production, this would update ML models, rule weights, etc.
        pass

    def add_policy_rule(self, rule_name: str, rule_config: Dict[str, Any]) -> None:
        """Add a new policy rule"""
        self.policy_rules[rule_name] = rule_config
        logger.info(f"Added policy rule: {rule_name}")

    def remove_policy_rule(self, rule_name: str) -> bool:
        """Remove a policy rule"""
        if rule_name in self.policy_rules:
            del self.policy_rules[rule_name]
            logger.info(f"Removed policy rule: {rule_name}")
            return True
        return False

    def get_evaluation_stats(self) -> Dict[str, Any]:
        """Get evaluation statistics"""
        if not self.evaluation_history:
            return {"total_evaluations": 0}

        total = len(self.evaluation_history)
        approved = len([r for r in self.evaluation_history if r.decision == PolicyDecision.APPROVED])
        rejected = len([r for r in self.evaluation_history if r.decision == PolicyDecision.REJECTED])
        avg_confidence = sum(r.confidence for r in self.evaluation_history) / total
        avg_time = sum(r.evaluation_time_ms for r in self.evaluation_history) / total

        return {
            "total_evaluations": total,
            "approved": approved,
            "rejected": rejected,
            "approval_rate": approved / total,
            "average_confidence": avg_confidence,
            "average_evaluation_time_ms": avg_time,
            "engine_name": self.engine_name
        }

    def get_engine_status(self) -> Dict[str, Any]:
        """Get engine status and configuration"""
        return {
            "engine_name": self.engine_name,
            "initialized": self.initialized,
            "confidence_threshold": self.confidence_threshold,
            "constellation_aware": self.constellation_aware,
            "learning_enabled": self.enable_learning,
            "policy_rules_count": len(self.policy_rules),
            "evaluation_history_size": len(self.evaluation_history),
            "violation_patterns_count": len(self.violation_patterns)
        }
