"""Guardian veto explanation system."""
from typing import Any, Dict

from .policies import ReasonCode, VetoEvent

# Explanation templates for each reason code
REASON_EXPLANATIONS = {
    ReasonCode.UNSAFE_CONTENT: "Content contains potentially unsafe or harmful material",
    ReasonCode.SECURITY_RISK: "Operation poses a security risk to the system",
    ReasonCode.MALICIOUS_INTENT: "Detected potentially malicious intent in request",
    ReasonCode.EXPLOIT_ATTEMPT: "Request appears to be an exploit attempt",
    ReasonCode.PRIVACY_VIOLATION: "Operation would violate user privacy protections",
    ReasonCode.MISSING_CONSENT: "Required user consent has not been obtained",
    ReasonCode.DATA_LEAK_RISK: "Operation risks leaking sensitive data",
    ReasonCode.PII_EXPOSURE: "Personally identifiable information would be exposed",
    ReasonCode.ETHICAL_VIOLATION: "Request violates ethical guidelines",
    ReasonCode.REGULATORY_NONCOMPLIANCE: "Operation not compliant with regulations",
    ReasonCode.BIAS_DETECTED: "Potential bias detected in request or data",
    ReasonCode.HARMFUL_OUTPUT: "Output could cause harm to users",
    ReasonCode.RATE_LIMIT_EXCEEDED: "Too many requests - rate limit exceeded",
    ReasonCode.RESOURCE_EXHAUSTION: "System resources are exhausted",
    ReasonCode.QUOTA_EXCEEDED: "Usage quota has been exceeded",
    ReasonCode.UNAUTHORIZED_ACCESS: "Access attempt without proper authorization",
    ReasonCode.INVALID_CREDENTIALS: "Provided credentials are invalid",
    ReasonCode.INSUFFICIENT_PERMISSIONS: "User lacks required permissions",
    ReasonCode.SPAM_DETECTED: "Content identified as spam",
    ReasonCode.LOW_QUALITY_INPUT: "Input quality below acceptable threshold",
    ReasonCode.MALFORMED_REQUEST: "Request format is malformed or invalid",
    ReasonCode.POLICY_VIOLATION: "General policy violation detected",
    ReasonCode.UNKNOWN_ERROR: "An unknown error occurred",
}


def explain_veto(event: VetoEvent) -> str:
    """
    Convert veto event to human-readable explanation.

    Args:
        event: VetoEvent containing reason code and context

    Returns:
        One-line human-readable explanation
    """
    # Get base explanation from reason code
    base_explanation = REASON_EXPLANATIONS.get(
        event.reason_code,
        "Request was blocked by policy"
    )

    # Add policy name
    explanation = f"{base_explanation} (Policy: {event.policy_name})"

    # Add custom message if available
    if event.message:
        explanation += f" - {event.message}"

    return explanation


def explain_veto_detailed(event: VetoEvent) -> Dict[str, Any]:
    """
    Get detailed explanation of veto event.

    Args:
        event: VetoEvent to explain

    Returns:
        Dictionary with detailed explanation components
    """
    return {
        "summary": explain_veto(event),
        "reason_code": event.reason_code.value,
        "policy": event.policy_name,
        "message": event.message,
        "context": event.context,
        "timestamp": event.timestamp.isoformat()
    }


if __name__ == "__main__":

    print("=== Guardian Veto Explanation Demo ===\n")

    # Create sample veto events
    veto1 = VetoEvent(
        reason_code=ReasonCode.UNSAFE_CONTENT,
        policy_name="SafeContentPolicy",
        message="contains 'exploit'"
    )

    veto2 = VetoEvent(
        reason_code=ReasonCode.RATE_LIMIT_EXCEEDED,
        policy_name="RateLimitPolicy",
        message="101/100 requests"
    )

    print("Simple explanations:")
    print(f"1. {explain_veto(veto1)}")
    print(f"2. {explain_veto(veto2)}\n")

    print("Detailed explanation:")
    import json
    print(json.dumps(explain_veto_detailed(veto1), indent=2, default=str))
