"""
Guardian System Wrapper Interface
=================================

Simplified wrapper for Guardian functionality with feature flag support
and dry-run mode by default. Follows patterns from consent_ledger.py
and kernel_bus.py for production-safe deployment.

Features:
- GUARDIAN_ACTIVE feature flag
- Dry-run mode by default
- MATRIZ instrumentation on all methods
- Drift threshold: 0.15
- Constitutional AI principle checks
"""

from __future__ import annotations

import os
import uuid
from typing import Any

from lukhas.governance.guardian.core import (
    GovernanceAction,
)
from lukhas.observability.matriz_decorators import instrument

# Feature flag for Guardian system
GUARDIAN_ACTIVE = os.environ.get("GUARDIAN_ACTIVE", "false").lower() == "true"

# Drift threshold configuration
DRIFT_THRESHOLD = float(os.environ.get("DRIFT_THRESHOLD", "0.15"))

# Conditional import of real implementation
_guardian_instance = None
if GUARDIAN_ACTIVE:
    try:
        from lukhas.governance.guardian.guardian_impl import GuardianSystemImpl

        _guardian_instance = GuardianSystemImpl(drift_threshold=DRIFT_THRESHOLD)
    except ImportError:
        pass


@instrument("DECISION", label="guardian:drift", capability="guardian:drift:detect")
def detect_drift(
    baseline_behavior: str,
    current_behavior: str,
    *,
    threshold: float | None = None,
    context: dict[str, Any] | None = None,
    mode: str = "dry_run",
    **kwargs,
) -> dict[str, Any]:
    """
    Detect ethical drift in system behavior.

    Args:
        baseline_behavior: Reference behavior description
        current_behavior: Current behavior to evaluate
        threshold: Custom drift threshold (default: 0.15)
        context: Additional context for evaluation
        mode: "dry_run" or "live"

    Returns:
        Drift detection result
    """
    _ = kwargs
    threshold = threshold or DRIFT_THRESHOLD
    context = context or {}

    # Generate correlation ID for tracking
    correlation_id = str(uuid.uuid4())

    if mode != "dry_run" and GUARDIAN_ACTIVE and _guardian_instance:
        # Use real implementation
        try:
            result = _guardian_instance.detect_drift(
                baseline=baseline_behavior,
                current=current_behavior,
                threshold=threshold,
                context=context,
            )

            return {
                "ok": True,
                "drift_score": result.drift_score,
                "threshold_exceeded": result.threshold_exceeded,
                "severity": result.severity.value,
                "remediation_needed": result.remediation_needed,
                "details": result.details,
                "correlation_id": correlation_id,
                "mode": "live",
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "correlation_id": correlation_id,
                "mode": "live",
            }

    # Dry-run simulation
    simulated_score = _simulate_drift_score(baseline_behavior, current_behavior)
    threshold_exceeded = simulated_score > threshold

    return {
        "ok": True,
        "drift_score": simulated_score,
        "threshold_exceeded": threshold_exceeded,
        "severity": "high" if threshold_exceeded else "low",
        "remediation_needed": threshold_exceeded,
        "details": {
            "simulation": True,
            "baseline_length": len(baseline_behavior),
            "current_length": len(current_behavior),
            "threshold_used": threshold,
        },
        "correlation_id": correlation_id,
        "mode": "dry_run",
    }


@instrument("DECISION", label="guardian:ethics", capability="guardian:ethics:evaluate")
def evaluate_ethics(
    action: GovernanceAction,
    *,
    context: dict[str, Any] | None = None,
    mode: str = "dry_run",
    **kwargs,
) -> dict[str, Any]:
    """
    Evaluate the ethical implications of an action.

    Args:
        action: The action to evaluate
        context: Additional context for evaluation
        mode: "dry_run" or "live"

    Returns:
        Ethical evaluation result
    """
    _ = kwargs
    context = context or {}
    correlation_id = str(uuid.uuid4())

    if mode != "dry_run" and GUARDIAN_ACTIVE and _guardian_instance:
        # Use real implementation
        try:
            decision = _guardian_instance.evaluate_ethics(action=action, context=context)

            return {
                "ok": True,
                "allowed": decision.allowed,
                "reason": decision.reason,
                "severity": decision.severity.value,
                "confidence": decision.confidence,
                "recommendations": decision.recommendations or [],
                "drift_score": decision.drift_score,
                "correlation_id": correlation_id,
                "mode": "live",
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "correlation_id": correlation_id,
                "mode": "live",
            }

    # Dry-run simulation
    simulated_decision = _simulate_ethical_decision(action)

    return {
        "ok": True,
        "allowed": simulated_decision["allowed"],
        "reason": simulated_decision["reason"],
        "severity": simulated_decision["severity"],
        "confidence": simulated_decision["confidence"],
        "recommendations": simulated_decision["recommendations"],
        "correlation_id": correlation_id,
        "mode": "dry_run",
    }


@instrument("AWARENESS", label="guardian:safety", capability="guardian:safety:validate")
def check_safety(
    content: str,
    *,
    context: dict[str, Any] | None = None,
    constitutional_check: bool = True,
    mode: str = "dry_run",
    **kwargs,
) -> dict[str, Any]:
    """
    Perform safety validation on content.

    Args:
        content: Content to validate
        context: Additional context
        constitutional_check: Enable constitutional AI checks
        mode: "dry_run" or "live"

    Returns:
        Safety validation result
    """
    _ = kwargs
    context = context or {}
    correlation_id = str(uuid.uuid4())

    if mode != "dry_run" and GUARDIAN_ACTIVE and _guardian_instance:
        # Use real implementation
        try:
            result = _guardian_instance.check_safety(
                content=content,
                context=context,
                constitutional_check=constitutional_check,
            )

            return {
                "ok": True,
                "safe": result.safe,
                "risk_level": result.risk_level.value,
                "violations": result.violations,
                "recommendations": result.recommendations,
                "constitutional_check": result.constitutional_check,
                "correlation_id": correlation_id,
                "mode": "live",
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "correlation_id": correlation_id,
                "mode": "live",
            }

    # Dry-run simulation
    simulated_result = _simulate_safety_check(content, constitutional_check)

    return {
        "ok": True,
        "safe": simulated_result["safe"],
        "risk_level": simulated_result["risk_level"],
        "violations": simulated_result["violations"],
        "recommendations": simulated_result["recommendations"],
        "constitutional_check": constitutional_check,
        "correlation_id": correlation_id,
        "mode": "dry_run",
    }


@instrument("AWARENESS", label="guardian:status", capability="guardian:monitor")
def get_guardian_status(*, mode: str = "dry_run", **kwargs) -> dict[str, Any]:
    """
    Get Guardian system status and metrics.

    Args:
        mode: "dry_run" or "live"

    Returns:
        Status information
    """
    if mode != "dry_run" and GUARDIAN_ACTIVE and _guardian_instance:
        # Use real implementation
        try:
            status = _guardian_instance.get_status()
            return {
                "ok": True,
                "active": True,
                "drift_threshold": DRIFT_THRESHOLD,
                "constitutional_ai_enabled": status.get("constitutional_ai", True),
                "ethics_engine_status": status.get("ethics_status", "active"),
                "safety_validator_status": status.get("safety_status", "active"),
                "mode": "live",
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "mode": "live"}

    # Dry-run status
    return {
        "ok": True,
        "active": False,
        "drift_threshold": DRIFT_THRESHOLD,
        "constitutional_ai_enabled": True,
        "ethics_engine_status": "simulated",
        "safety_validator_status": "simulated",
        "feature_flag_active": GUARDIAN_ACTIVE,
        "mode": "dry_run",
    }


# Helper functions for dry-run simulation
def _simulate_drift_score(baseline: str, current: str) -> float:
    """Simulate drift score calculation for dry-run mode"""
    # Simple heuristic based on text similarity
    if not baseline or not current:
        return 0.0

    # Basic similarity check
    baseline_words = set(baseline.lower().split())
    current_words = set(current.lower().split())

    if not baseline_words:
        return 0.0

    overlap = len(baseline_words.intersection(current_words))
    similarity = overlap / len(baseline_words)
    drift_score = 1.0 - similarity

    # Cap at reasonable values
    return min(max(drift_score, 0.0), 1.0)


def _simulate_ethical_decision(action: GovernanceAction) -> dict[str, Any]:
    """Simulate ethical decision for dry-run mode"""
    # Basic ethical checks
    risky_actions = ["delete", "remove", "destroy", "harm", "attack"]
    risky_targets = ["system", "data", "user", "privacy"]

    action_risk = any(risk in action.action_type.lower() for risk in risky_actions)
    target_risk = any(risk in action.target.lower() for risk in risky_targets)

    if action_risk or target_risk:
        return {
            "allowed": False,
            "reason": "Simulated ethical concern detected",
            "severity": "high",
            "confidence": 0.8,
            "recommendations": [
                "Review action requirements",
                "Consider safer alternatives",
            ],
        }

    return {
        "allowed": True,
        "reason": "No simulated ethical concerns",
        "severity": "low",
        "confidence": 0.9,
        "recommendations": ["Proceed with monitoring"],
    }


def _simulate_safety_check(content: str, constitutional_check: bool) -> dict[str, Any]:
    """Simulate safety check for dry-run mode"""
    # Basic safety keywords
    unsafe_keywords = ["harm", "attack", "violence", "illegal", "malicious"]

    violations = [
        f"Detected potentially unsafe keyword: {keyword}" for keyword in unsafe_keywords if keyword in content.lower()
    ]

    safe = len(violations) == 0
    risk_level = "high" if violations else "low"

    recommendations = []
    if violations:
        recommendations.append("Review content for safety concerns")
        recommendations.append("Consider content filtering")
    else:
        recommendations.append("Content appears safe for processing")

    return {
        "safe": safe,
        "risk_level": risk_level,
        "violations": violations,
        "recommendations": recommendations,
    }
