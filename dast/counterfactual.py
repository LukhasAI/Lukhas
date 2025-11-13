"""Counterfactual decision generation."""
from typing import Dict, Any
from datetime import datetime


def generate_counterfactual(decision: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate counterfactual alternative for a decision.

    This is a placeholder implementation with no external calls.
    In production, this would use more sophisticated analysis.

    Args:
        decision: Original decision context

    Returns:
        Structured counterfactual alternative
    """
    # Extract decision components
    action = decision.get("action", "unknown")
    rationale = decision.get("rationale", "")
    confidence = decision.get("confidence", 0.5)

    # Generate alternative
    alternative_action = f"alternative_to_{action}"
    alternative_rationale = f"Instead of {action}, consider {alternative_action}"

    # Compute alternative confidence (inverse heuristic)
    alternative_confidence = 1.0 - confidence

    # Generate alternative outcomes
    original_outcomes = decision.get("expected_outcomes", [])
    alternative_outcomes = [
        f"alternative_{outcome}" for outcome in original_outcomes
    ]

    return {
        "original_decision": {
            "action": action,
            "confidence": confidence,
            "rationale": rationale
        },
        "counterfactual": {
            "action": alternative_action,
            "confidence": alternative_confidence,
            "rationale": alternative_rationale,
            "expected_outcomes": alternative_outcomes
        },
        "comparison": {
            "confidence_delta": alternative_confidence - confidence,
            "risk_assessment": "lower" if alternative_confidence > confidence else "higher"
        },
        "generated_at": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    print("=== Counterfactual Generation Demo ===\n")

    # Example decision
    decision = {
        "action": "deploy_to_production",
        "rationale": "All tests passed",
        "confidence": 0.85,
        "expected_outcomes": ["increased_traffic", "improved_performance"]
    }

    counterfactual = generate_counterfactual(decision)

    print("Original Decision:")
    print(f"  Action: {counterfactual['original_decision']['action']}")
    print(f"  Confidence: {counterfactual['original_decision']['confidence']}\n")

    print("Counterfactual:")
    print(f"  Action: {counterfactual['counterfactual']['action']}")
    print(f"  Confidence: {counterfactual['counterfactual']['confidence']}")
    print(f"  Rationale: {counterfactual['counterfactual']['rationale']}\n")

    print("Comparison:")
    print(f"  Confidence delta: {counterfactual['comparison']['confidence_delta']:.2f}")
    print(f"  Risk: {counterfactual['comparison']['risk_assessment']}")
