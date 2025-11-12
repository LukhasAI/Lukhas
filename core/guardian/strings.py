"""Guardian UI string pack for reason codes."""
from .policies import ReasonCode

# Concise user-facing strings for each reason code
REASON_CODE_STRINGS = {
    ReasonCode.UNSAFE_CONTENT: "Unsafe content detected",
    ReasonCode.SECURITY_RISK: "Security risk identified",
    ReasonCode.MALICIOUS_INTENT: "Malicious intent detected",
    ReasonCode.EXPLOIT_ATTEMPT: "Exploit attempt blocked",
    ReasonCode.PRIVACY_VIOLATION: "Privacy policy violation",
    ReasonCode.MISSING_CONSENT: "User consent required",
    ReasonCode.DATA_LEAK_RISK: "Data leak risk",
    ReasonCode.PII_EXPOSURE: "PII protection triggered",
    ReasonCode.ETHICAL_VIOLATION: "Ethical guidelines violated",
    ReasonCode.REGULATORY_NONCOMPLIANCE: "Regulatory compliance issue",
    ReasonCode.BIAS_DETECTED: "Bias detected in request",
    ReasonCode.HARMFUL_OUTPUT: "Harmful output prevented",
    ReasonCode.RATE_LIMIT_EXCEEDED: "Rate limit exceeded",
    ReasonCode.RESOURCE_EXHAUSTION: "System resources exhausted",
    ReasonCode.QUOTA_EXCEEDED: "Usage quota exceeded",
    ReasonCode.UNAUTHORIZED_ACCESS: "Unauthorized access attempt",
    ReasonCode.INVALID_CREDENTIALS: "Invalid credentials",
    ReasonCode.INSUFFICIENT_PERMISSIONS: "Insufficient permissions",
    ReasonCode.SPAM_DETECTED: "Spam content detected",
    ReasonCode.LOW_QUALITY_INPUT: "Input quality too low",
    ReasonCode.MALFORMED_REQUEST: "Request format invalid",
    ReasonCode.POLICY_VIOLATION: "Policy violation",
    ReasonCode.UNKNOWN_ERROR: "Unknown error occurred",
}


def get_ui_string(reason_code: ReasonCode) -> str:
    """
    Get user-facing string for a reason code.

    Args:
        reason_code: Reason code enum value

    Returns:
        Concise user-facing string
    """
    return REASON_CODE_STRINGS.get(reason_code, "Request blocked")


if __name__ == "__main__":
    print("=== Guardian UI Strings Demo ===\n")

    for code in ReasonCode:
        print(f"{code.name}: \"{get_ui_string(code)}\"")
