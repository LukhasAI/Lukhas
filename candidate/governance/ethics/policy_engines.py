"""
Policy Engines Module for LUKHAS Ethics System
==============================================

This module provides policy evaluation engines for ethical decision making
and compliance validation within the LUKHAS AI system.
"""

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of policies supported by the engine"""
    SAFETY = "safety"
    ETHICS = "ethics"
    COMPLIANCE = "compliance"
    PRIVACY = "privacy"
    SECURITY = "security"
    CONTENT = "content"


class PolicyResult:
    """Result of a policy evaluation"""

    def __init__(self, compliant: bool, score: float, violations: list[str] = None,
                 metadata: dict[str, Any] = None):
        self.compliant = compliant
        self.score = score
        self.violations = violations or []
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "compliant": self.compliant,
            "score": self.score,
            "violations": self.violations,
            "metadata": self.metadata
        }


class PolicyEngine:
    """Base policy evaluation engine"""

    def __init__(self, policy_type: PolicyType, name: str = None):
        self.policy_type = policy_type
        self.name = name or f"{policy_type.value}_engine"
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

    def evaluate(self, context: dict[str, Any], content: Any = None) -> PolicyResult:
        """
        Evaluate content against this policy

        Args:
            context: Evaluation context with metadata
            content: Content to evaluate (text, data, etc.)

        Returns:
            PolicyResult with compliance status and details
        """
        try:
            return self._evaluate_impl(context, content)
        except Exception as e:
            self.logger.error(f"Policy evaluation failed: {e}")
            return PolicyResult(
                compliant=False,
                score=0.0,
                violations=[f"Evaluation error: {str(e)}"],
                metadata={"error": str(e)}
            )

    def _evaluate_impl(self, context: dict[str, Any], content: Any) -> PolicyResult:
        """Implementation of policy evaluation - override in subclasses"""
        # Default safe fallback
        return PolicyResult(
            compliant=True,
            score=1.0,
            violations=[],
            metadata={"engine": self.name, "type": self.policy_type.value}
        )


class SafetyPolicyEngine(PolicyEngine):
    """Safety policy evaluation engine"""

    def __init__(self):
        super().__init__(PolicyType.SAFETY, "safety_policy")

    def _evaluate_impl(self, context: dict[str, Any], content: Any) -> PolicyResult:
        """Evaluate safety compliance"""
        violations = []
        score = 1.0

        # Basic safety checks
        if content and isinstance(content, str):
            content_lower = content.lower()

            # Check for harmful content indicators
            harmful_patterns = ["violence", "harm", "dangerous", "illegal"]
            for pattern in harmful_patterns:
                if pattern in content_lower:
                    violations.append(f"Potential safety concern: {pattern}")
                    score -= 0.2

        score = max(0.0, score)
        compliant = score >= 0.7 and len(violations) == 0

        return PolicyResult(
            compliant=compliant,
            score=score,
            violations=violations,
            metadata={"safety_checks": len(harmful_patterns)}
        )


class EthicsPolicyEngine(PolicyEngine):
    """Ethics policy evaluation engine"""

    def __init__(self):
        super().__init__(PolicyType.ETHICS, "ethics_policy")

    def _evaluate_impl(self, context: dict[str, Any], content: Any) -> PolicyResult:
        """Evaluate ethical compliance"""
        violations = []
        score = 1.0

        # Basic ethics checks
        if content and isinstance(content, str):
            content_lower = content.lower()

            # Check for ethical concerns
            ethical_concerns = ["discrimination", "bias", "unfair", "manipulative"]
            for concern in ethical_concerns:
                if concern in content_lower:
                    violations.append(f"Ethical concern: {concern}")
                    score -= 0.25

        score = max(0.0, score)
        compliant = score >= 0.8 and len(violations) == 0

        return PolicyResult(
            compliant=compliant,
            score=score,
            violations=violations,
            metadata={"ethics_checks": "basic_pattern_matching"}
        )


class PolicyEngines:
    """Central policy engines coordinator"""

    def __init__(self):
        self.engines = {
            PolicyType.SAFETY: SafetyPolicyEngine(),
            PolicyType.ETHICS: EthicsPolicyEngine(),
        }
        self.logger = logging.getLogger(f"{__name__}.coordinator")

    def register_engine(self, policy_type: PolicyType, engine: PolicyEngine):
        """Register a new policy engine"""
        self.engines[policy_type] = engine
        self.logger.info(f"Registered policy engine: {policy_type.value}")

    def evaluate_policy(self, policy_name: str, context: dict[str, Any] = None,
                       content: Any = None, **kwargs) -> dict[str, Any]:
        """
        Evaluate content against a specific policy

        Args:
            policy_name: Name of policy to evaluate
            context: Evaluation context
            content: Content to evaluate
            **kwargs: Additional parameters

        Returns:
            Dictionary with evaluation results
        """
        context = context or {}
        context.update(kwargs)

        # Map policy names to types
        policy_mapping = {
            "safety": PolicyType.SAFETY,
            "ethics": PolicyType.ETHICS,
            "safety_policy": PolicyType.SAFETY,
            "ethics_policy": PolicyType.ETHICS,
            "default_policy": PolicyType.SAFETY,
        }

        policy_type = policy_mapping.get(policy_name.lower())
        if not policy_type:
            self.logger.warning(f"Unknown policy: {policy_name}")
            return {
                "compliant": False,
                "score": 0.0,
                "violations": [f"Unknown policy: {policy_name}"],
                "metadata": {"error": "policy_not_found"}
            }

        engine = self.engines.get(policy_type)
        if not engine:
            self.logger.warning(f"No engine for policy type: {policy_type}")
            return {
                "compliant": False,
                "score": 0.0,
                "violations": [f"No engine for policy: {policy_name}"],
                "metadata": {"error": "engine_not_found"}
            }

        result = engine.evaluate(context, content)
        return result.to_dict()

    def list_policies(self) -> list[str]:
        """List available policies"""
        policies = []
        for policy_type in self.engines:
            policies.extend([
                policy_type.value,
                f"{policy_type.value}_policy"
            ])
        policies.append("default_policy")
        return sorted(list(set(policies)))

    def evaluate_all(self, context: dict[str, Any] = None,
                    content: Any = None) -> dict[str, dict[str, Any]]:
        """Evaluate content against all registered policies"""
        results = {}
        context = context or {}

        for policy_type, engine in self.engines.items():
            try:
                result = engine.evaluate(context, content)
                results[policy_type.value] = result.to_dict()
            except Exception as e:
                self.logger.error(f"Failed to evaluate {policy_type.value}: {e}")
                results[policy_type.value] = {
                    "compliant": False,
                    "score": 0.0,
                    "violations": [f"Evaluation failed: {str(e)}"],
                    "metadata": {"error": str(e)}
                }

        return results


# Global instance for easy access
_default_engines = PolicyEngines()

# Convenience functions
def evaluate_policy(policy_name: str, context: dict[str, Any] = None,
                   content: Any = None, **kwargs) -> dict[str, Any]:
    """Evaluate content against a specific policy"""
    return _default_engines.evaluate_policy(policy_name, context, content, **kwargs)

def list_policies() -> list[str]:
    """List available policies"""
    return _default_engines.list_policies()

def evaluate_all_policies(context: dict[str, Any] = None,
                         content: Any = None) -> dict[str, dict[str, Any]]:
    """Evaluate content against all policies"""
    return _default_engines.evaluate_all(context, content)

# Export main classes and functions
__all__ = [
    "PolicyType",
    "PolicyResult",
    "PolicyEngine",
    "SafetyPolicyEngine",
    "EthicsPolicyEngine",
    "PolicyEngines",
    "evaluate_policy",
    "list_policies",
    "evaluate_all_policies"
]
