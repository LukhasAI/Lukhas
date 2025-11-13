"""Decision context tag bundles."""
from typing import Dict, Any, List


def create_decision_context_bundle(decision: Dict[str, Any]) -> List[str]:
    """
    Produce minimal tag bundle for a decision.

    Args:
        decision: Decision object with action, confidence, etc.

    Returns:
        List of decision context tags
    """
    tags = []

    # Add decision type tag
    action = decision.get("action", "unknown")
    tags.append(f"#TAG:decision/action/{action}")

    # Add confidence level tag
    confidence = decision.get("confidence", 0.5)
    if confidence >= 0.8:
        level = "high"
    elif confidence >= 0.5:
        level = "medium"
    else:
        level = "low"
    tags.append(f"#TAG:decision/confidence/{level}")

    # Add risk level if present
    risk = decision.get("risk", "")
    if risk:
        tags.append(f"#TAG:decision/risk/{risk}")

    # Add decision maker if present
    maker = decision.get("maker", "")
    if maker:
        tags.append(f"#TAG:decision/maker/{maker}")

    return tags


if __name__ == "__main__":
    print("=== Decision Context Bundle Demo ===\n")

    decision = {
        "action": "deploy_to_production",
        "confidence": 0.85,
        "risk": "low",
        "maker": "system"
    }

    tags = create_decision_context_bundle(decision)

    print("Decision context tags:")
    for tag in tags:
        print(f"  {tag}")
