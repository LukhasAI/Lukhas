import logging

logger = logging.getLogger(__name__)
"""

#TAG:governance
#TAG:policy
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - ETHICS POLICY BASE
║ Abstract base class for ethics policy engines.
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: base.py
║ Path: lukhas/[subdirectory]/base.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Ethics Team | Jules
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Abstract base class for ethics policy engines.
╚══════════════════════════════════════════════════════════════════════════════════
"""

# Module imports
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from core.common import LukhasError, get_logger

# Configure module logger
logger = get_logger(__name__)

# Module constants
MODULE_VERSION = "1.0.0"
MODULE_NAME = "ethics policy base"


logger = get_logger(__name__)


class RiskLevel(Enum):
    """Risk levels for ethical evaluation"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Decision:
    """Represents a decision to be evaluated"""

    action: str
    context: dict[str, Any]
    symbolic_state: Optional[dict[str, Any]] = None
    glyphs: Optional[list[str]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    requester_id: Optional[str] = None
    urgency: RiskLevel = RiskLevel.MEDIUM

    def __post_init__(self):
        """Validate decision structure"""
        if not self.action:
            raise ValueError("Decision action cannot be empty")
        if not isinstance(self.context, dict):
            raise TypeError("Decision context must be a dictionary")


@dataclass
class EthicsEvaluation:
    """Result of ethical evaluation"""

    allowed: bool
    reasoning: str
    confidence: float
    risk_flags: list[str] = field(default_factory=list)
    drift_impact: float = 0.0
    symbolic_alignment: float = 1.0
    collapse_risk: float = 0.0
    policy_name: str = ""
    evaluation_time_ms: float = 0.0
    recommendations: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate evaluation metrics"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")
        if not 0.0 <= self.drift_impact <= 1.0:
            raise ValueError("Drift impact must be between 0 and 1")
        if not 0.0 <= self.symbolic_alignment <= 1.0:
            raise ValueError("Symbolic alignment must be between 0 and 1")
        if not 0.0 <= self.collapse_risk <= 1.0:
            raise ValueError("Collapse risk must be between 0 and 1")


class PolicyValidationError(LukhasError):
    """Raised when policy validation fails"""


class EthicsPolicy(ABC):
    """Abstract base class for ethics policy engines

    This class defines the interface that all ethics policy implementations
    must follow. It includes methods for decision evaluation, symbolic
    validation, and risk assessment.
    """

    def __init__(self):
        self._initialized = False
        self._metrics = {
            "evaluations_count": 0,
            "denials_count": 0,
            "high_risk_count": 0,
            "total_evaluation_time": 0.0,
        }

    @abstractmethod
    def evaluate_decision(self, decision: Decision) -> EthicsEvaluation:
        """Evaluate whether a decision is ethically permissible

        Args:
            decision: The decision to evaluate

        Returns:
            EthicsEvaluation with detailed analysis

        Raises:
            PolicyValidationError: If policy cannot evaluate the decision
        """

    @abstractmethod
    def get_policy_name(self) -> str:
        """Return human-readable policy name"""

    @abstractmethod
    def get_policy_version(self) -> str:
        """Return policy version for audit trail"""

    def validate_symbolic_alignment(self, glyphs: list[str]) -> float:
        """Check if decision aligns with symbolic state

        Args:
            glyphs: List of symbolic glyphs from decision

        Returns:
            Alignment score between 0.0 and 1.0
        """
        # Default implementation - can be overridden
        if not glyphs:
            return 1.0

        # Check for known risk glyphs
        risk_glyphs = {"🌀", "⚠️", "🔥", "💀"}
        safe_glyphs = {"🛡️", "✓", "🌱", "💚"}

        risk_count = sum(1 for g in glyphs if g in risk_glyphs)
        safe_count = sum(1 for g in glyphs if g in safe_glyphs)

        if risk_count + safe_count == 0:
            return 0.5  # Neutral

        alignment = safe_count / (risk_count + safe_count)
        return alignment

    def assess_drift_risk(self, decision: Decision) -> float:
        """Assess potential drift impact of decision

        Args:
            decision: The decision to assess

        Returns:
            Drift risk score between 0.0 and 1.0
        """
        # Default implementation
        risk_score = 0.0
        action_lower = decision.action.lower()

        # Check for high-risk actions
        high_risk_actions = {
            "modify_core",
            "alter_ethics",
            "disable_safety",
            "bypass_limits",
            "recursive_self_modification",
            "manipulate",
            "deceive",
            "exploit",
            "harm",
        }

        moderate_risk_actions = {
            "modify",
            "adjust",
            "reduce",
            "bypass",
            "profile",
            "analyze",
            "threshold",
            "parameter",
            "constraint",
        }

        if any(risk in action_lower for risk in high_risk_actions):
            risk_score += 0.5
        elif any(risk in action_lower for risk in moderate_risk_actions):
            risk_score += 0.3

        # Check context for concerning patterns
        if decision.context:
            context_str = str(decision.context).lower()
            if "without consent" in context_str:
                risk_score += 0.3
            if "bypass" in context_str or "modify" in context_str:
                risk_score += 0.2
            if "exploitation" in context_str or "vulnerable" in context_str:
                risk_score += 0.4

        # Check urgency
        if decision.urgency == RiskLevel.CRITICAL:
            risk_score += 0.3
        elif decision.urgency == RiskLevel.HIGH:
            risk_score += 0.2

        return min(risk_score, 1.0)

    def assess_collapse_risk(self, decision: Decision) -> float:
        """Assess symbolic collapse risk

        Args:
            decision: The decision to assess

        Returns:
            Collapse risk score between 0.0 and 1.0
        """
        # Default implementation
        if not decision.symbolic_state:
            return 0.0

        # Check for collapse indicators
        entropy = decision.symbolic_state.get("entropy", 0.5)
        coherence = decision.symbolic_state.get("coherence", 1.0)

        # High entropy + low coherence = collapse risk
        collapse_risk = entropy * (1.0 - coherence)

        return min(collapse_risk, 1.0)

    def initialize(self) -> None:
        """Initialize the policy engine

        Called once before first use. Override for custom initialization.
        """
        self._initialized = True
        logger.info(f"Initialized {self.get_policy_name()} v{self.get_policy_version()}")

    def shutdown(self) -> None:
        """Cleanup policy resources

        Called when policy is being unloaded. Override for custom cleanup.
        """
        self._initialized = False
        logger.info(f"Shutdown {self.get_policy_name()}")

    def get_metrics(self) -> dict[str, Any]:
        """Return policy performance metrics"""
        if self._metrics["evaluations_count"] > 0:
            avg_time = self._metrics["total_evaluation_time"] / self._metrics["evaluations_count"]
            denial_rate = self._metrics["denials_count"] / self._metrics["evaluations_count"]
        else:
            avg_time = 0.0
            denial_rate = 0.0

        return {
            "policy_name": self.get_policy_name(),
            "policy_version": self.get_policy_version(),
            "evaluations_count": self._metrics["evaluations_count"],
            "denials_count": self._metrics["denials_count"],
            "high_risk_count": self._metrics["high_risk_count"],
            "average_evaluation_time_ms": avg_time,
            "denial_rate": denial_rate,
        }

    def _update_metrics(self, evaluation: EthicsEvaluation, decision: Decision) -> None:
        """Update internal metrics"""
        self._metrics["evaluations_count"] += 1
        self._metrics["total_evaluation_time"] += evaluation.evaluation_time_ms

        if not evaluation.allowed:
            self._metrics["denials_count"] += 1

        if decision.urgency in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self._metrics["high_risk_count"] += 1


class PolicyRegistry:
    """Registry for managing multiple ethics policies"""

    def __init__(self):
        self._policies: dict[str, EthicsPolicy] = {}
        self._active_policies: set[str] = set()
        self._default_policy: Optional[str] = None

    def register_policy(self, policy: EthicsPolicy, set_as_default: bool = False) -> None:
        """Register a new ethics policy

        Args:
            policy: The policy instance to register
            set_as_default: Whether to set as default policy
        """
        policy_name = policy.get_policy_name()

        if policy_name in self._policies:
            logger.warning(f"Overwriting existing policy: {policy_name}")

        policy.initialize()
        self._policies[policy_name] = policy
        self._active_policies.add(policy_name)

        if set_as_default or self._default_policy is None:
            self._default_policy = policy_name

        logger.info(f"Registered policy: {policy_name} v{policy.get_policy_version()}")

    def unregister_policy(self, policy_name: str) -> None:
        """Unregister a policy

        Args:
            policy_name: Name of policy to unregister
        """
        if policy_name not in self._policies:
            raise ValueError(f"Policy not found: {policy_name}")

        policy = self._policies[policy_name]
        policy.shutdown()

        del self._policies[policy_name]
        self._active_policies.discard(policy_name)

        if self._default_policy == policy_name:
            self._default_policy = next(iter(self._active_policies), None)

        logger.info(f"Unregistered policy: {policy_name}")

    def evaluate_decision(self, decision: Decision, policy_names: Optional[list[str]] = None) -> list[EthicsEvaluation]:
        """Evaluate decision using specified policies

        Args:
            decision: The decision to evaluate
            policy_names: List of policy names to use (None = all active)

        Returns:
            List of evaluations from each policy
        """
        if policy_names is None:
            policy_names = list(self._active_policies)

        evaluations = []

        for name in policy_names:
            if name not in self._policies:
                logger.warning(f"Policy not found: {name}")
                continue

            if name not in self._active_policies:
                logger.warning(f"Policy not active: {name}")
                continue

            try:
                policy = self._policies[name]
                evaluation = policy.evaluate_decision(decision)
                evaluation.policy_name = name
                evaluations.append(evaluation)

            except Exception as e:
                logger.error(f"Policy {name} evaluation failed: {e}")
                # Create failure evaluation
                evaluations.append(
                    EthicsEvaluation(
                        allowed=False,
                        reasoning=f"Policy evaluation failed: {e!s}",
                        confidence=0.0,
                        risk_flags=["POLICY_ERROR"],
                        policy_name=name,
                    )
                )

        return evaluations

    def get_consensus_evaluation(self, evaluations: list[EthicsEvaluation]) -> EthicsEvaluation:
        """Combine multiple evaluations into consensus

        Args:
            evaluations: List of individual policy evaluations

        Returns:
            Consensus evaluation
        """
        if not evaluations:
            raise ValueError("No evaluations to combine")

        # Conservative approach: any denial = consensus denial
        allowed = all(e.allowed for e in evaluations)

        # Average confidence weighted by each policy's confidence
        total_confidence = sum(e.confidence for e in evaluations)
        if total_confidence > 0:
            weighted_confidence = sum(e.confidence * e.confidence for e in evaluations) / total_confidence
        else:
            weighted_confidence = 0.0

        # Combine risk assessments (take maximum)
        max_drift = max(e.drift_impact for e in evaluations)
        max_collapse = max(e.collapse_risk for e in evaluations)
        min_alignment = min(e.symbolic_alignment for e in evaluations)

        # Combine risk flags
        all_risk_flags = set()
        for e in evaluations:
            all_risk_flags.update(e.risk_flags)

        # Combine reasoning
        reasoning_parts = [f"{e.policy_name}: {e.reasoning}" for e in evaluations]
        combined_reasoning = "\n".join(reasoning_parts)

        # Combine recommendations
        all_recommendations = []
        for e in evaluations:
            all_recommendations.extend(e.recommendations)

        return EthicsEvaluation(
            allowed=allowed,
            reasoning=combined_reasoning,
            confidence=weighted_confidence,
            risk_flags=list(all_risk_flags),
            drift_impact=max_drift,
            symbolic_alignment=min_alignment,
            collapse_risk=max_collapse,
            policy_name="CONSENSUS",
            recommendations=list(set(all_recommendations)),
        )

    def get_active_policies(self) -> list[str]:
        """Get list of active policy names"""
        return list(self._active_policies)

    def get_policy_metrics(self) -> dict[str, dict[str, Any]]:
        """Get metrics for all policies"""
        metrics = {}
        for name, policy in self._policies.items():
            metrics[name] = policy.get_metrics()
        return metrics


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/test_base.py
║   - Coverage: N/A%
║   - Linting: pylint N/A/10
║
║ MONITORING:
║   - Metrics: N/A
║   - Logs: N/A
║   - Alerts: N/A
║
║ COMPLIANCE:
║   - Standards: N/A
║   - Ethics: Refer to LUKHAS Ethics Guidelines
║   - Safety: Refer to LUKHAS Safety Protocols
║
║ REFERENCES:
║   - Docs: docs/ethics/ethics policy base.md
║   - Issues: github.com/lukhas-ai/lukhas/issues?label=ethics policy base
║   - Wiki: N/A
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS Cognitive system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════
"""
