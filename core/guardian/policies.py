"""Guardian policy system with structured veto reason codes."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class ReasonCode(str, Enum):
    """
    Structured reason codes for Guardian policy vetoes.

    Each code represents a specific category of policy violation.
    """
    # Safety & Security
    UNSAFE_CONTENT = "UNSAFE_CONTENT"
    SECURITY_RISK = "SECURITY_RISK"
    MALICIOUS_INTENT = "MALICIOUS_INTENT"
    EXPLOIT_ATTEMPT = "EXPLOIT_ATTEMPT"

    # Privacy & Consent
    PRIVACY_VIOLATION = "PRIVACY_VIOLATION"
    MISSING_CONSENT = "MISSING_CONSENT"
    DATA_LEAK_RISK = "DATA_LEAK_RISK"
    PII_EXPOSURE = "PII_EXPOSURE"

    # Ethics & Compliance
    ETHICAL_VIOLATION = "ETHICAL_VIOLATION"
    REGULATORY_NONCOMPLIANCE = "REGULATORY_NONCOMPLIANCE"
    BIAS_DETECTED = "BIAS_DETECTED"
    HARMFUL_OUTPUT = "HARMFUL_OUTPUT"

    # Rate Limiting & Resource
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"

    # Authentication & Authorization
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Content Quality
    SPAM_DETECTED = "SPAM_DETECTED"
    LOW_QUALITY_INPUT = "LOW_QUALITY_INPUT"
    MALFORMED_REQUEST = "MALFORMED_REQUEST"

    # General
    POLICY_VIOLATION = "POLICY_VIOLATION"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class VetoEvent:
    """Represents a Guardian veto event with reason code."""

    def __init__(
        self,
        reason_code: ReasonCode,
        policy_name: str,
        context: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a veto event.

        Args:
            reason_code: Structured reason code for the veto
            policy_name: Name of the policy that triggered the veto
            context: Additional context about the veto
            message: Human-readable message
            timestamp: When the veto occurred (defaults to now)
        """
        self.reason_code = reason_code
        self.policy_name = policy_name
        self.context = context or {}
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert veto event to dictionary."""
        return {
            "reason_code": self.reason_code.value,
            "policy_name": self.policy_name,
            "context": self.context,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


class Policy:
    """Base class for Guardian policies."""

    def __init__(self, name: str, reason_code: ReasonCode):
        """
        Initialize a policy.

        Args:
            name: Policy name
            reason_code: Reason code to use when this policy triggers a veto
        """
        self.name = name
        self.reason_code = reason_code
        self.enabled = True

    def evaluate(self, context: Dict[str, Any]) -> Optional[VetoEvent]:
        """
        Evaluate the policy against a context.

        Args:
            context: Context to evaluate

        Returns:
            VetoEvent if policy is violated, None otherwise
        """
        if not self.enabled:
            return None

        violation = self._check_violation(context)
        if violation:
            return self._create_veto_event(context, violation)

        return None

    def _check_violation(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Check if the policy is violated.

        Args:
            context: Context to check

        Returns:
            Violation message if violated, None otherwise
        """
        # Override in subclasses
        return None

    def _create_veto_event(self, context: Dict[str, Any], violation: str) -> VetoEvent:
        """Create a veto event for this policy."""
        return VetoEvent(
            reason_code=self.reason_code,
            policy_name=self.name,
            context=context,
            message=violation
        )


class SafeContentPolicy(Policy):
    """Policy to ensure content safety."""

    def __init__(self):
        super().__init__("SafeContentPolicy", ReasonCode.UNSAFE_CONTENT)

    def _check_violation(self, context: Dict[str, Any]) -> Optional[str]:
        """Check for unsafe content."""
        content = context.get("content", "")
        if not content:
            return None

        # Simple keyword-based check (in production, use ML models)
        unsafe_keywords = ["exploit", "hack", "malware", "virus"]
        content_lower = content.lower()

        for keyword in unsafe_keywords:
            if keyword in content_lower:
                return f"Unsafe content detected: contains '{keyword}'"

        return None


class PrivacyPolicy(Policy):
    """Policy to protect user privacy."""

    def __init__(self):
        super().__init__("PrivacyPolicy", ReasonCode.PRIVACY_VIOLATION)

    def _check_violation(self, context: Dict[str, Any]) -> Optional[str]:
        """Check for privacy violations."""
        # Check for PII exposure
        content = context.get("content", "")
        if not content:
            return None

        # Simple pattern check for email addresses (example)
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, content):
            return "Privacy violation: PII (email) detected in content"

        return None


class RateLimitPolicy(Policy):
    """Policy to enforce rate limits."""

    def __init__(self, max_requests: int = 100):
        super().__init__("RateLimitPolicy", ReasonCode.RATE_LIMIT_EXCEEDED)
        self.max_requests = max_requests
        self.request_counts: Dict[str, int] = {}

    def _check_violation(self, context: Dict[str, Any]) -> Optional[str]:
        """Check for rate limit violations."""
        user_id = context.get("user_id", "anonymous")

        # Increment counter
        current_count = self.request_counts.get(user_id, 0) + 1
        self.request_counts[user_id] = current_count

        if current_count > self.max_requests:
            return f"Rate limit exceeded: {current_count}/{self.max_requests} requests"

        return None


class ConsentPolicy(Policy):
    """Policy to ensure user consent."""

    def __init__(self):
        super().__init__("ConsentPolicy", ReasonCode.MISSING_CONSENT)

    def _check_violation(self, context: Dict[str, Any]) -> Optional[str]:
        """Check for missing consent."""
        consent_given = context.get("consent_given", False)
        requires_consent = context.get("requires_consent", True)

        if requires_consent and not consent_given:
            return "Missing required user consent"

        return None


class PolicyEngine:
    """Guardian policy engine with reason code support."""

    def __init__(self):
        """Initialize the policy engine."""
        self.policies: List[Policy] = []
        self.veto_history: List[VetoEvent] = []

    def register_policy(self, policy: Policy) -> None:
        """
        Register a policy with the engine.

        Args:
            policy: Policy to register
        """
        self.policies.append(policy)

    def evaluate(self, context: Dict[str, Any]) -> Optional[VetoEvent]:
        """
        Evaluate all policies against a context.

        Args:
            context: Context to evaluate

        Returns:
            First VetoEvent if any policy is violated, None otherwise
        """
        for policy in self.policies:
            veto = policy.evaluate(context)
            if veto:
                self.veto_history.append(veto)
                return veto

        return None

    def get_veto_history(self) -> List[Dict[str, Any]]:
        """Get complete veto history."""
        return [veto.to_dict() for veto in self.veto_history]

    def get_vetoes_by_reason(self, reason_code: ReasonCode) -> List[Dict[str, Any]]:
        """Get all vetoes for a specific reason code."""
        return [
            veto.to_dict()
            for veto in self.veto_history
            if veto.reason_code == reason_code
        ]


if __name__ == "__main__":
    # Demonstration
    print("=== Guardian Policy Engine with Reason Codes Demo ===\n")

    # Initialize engine and register policies
    engine = PolicyEngine()
    engine.register_policy(SafeContentPolicy())
    engine.register_policy(PrivacyPolicy())
    engine.register_policy(ConsentPolicy())
    engine.register_policy(RateLimitPolicy(max_requests=3))

    # Test cases
    test_contexts = [
        {
            "content": "Hello, this is safe content",
            "consent_given": True,
            "user_id": "user_001"
        },
        {
            "content": "I want to hack the system",
            "consent_given": True,
            "user_id": "user_002"
        },
        {
            "content": "Contact me at test@example.com",
            "consent_given": True,
            "user_id": "user_003"
        },
        {
            "content": "Process my data",
            "consent_given": False,
            "requires_consent": True,
            "user_id": "user_004"
        },
    ]

    print("Evaluating test contexts:\n")
    for i, context in enumerate(test_contexts, 1):
        veto = engine.evaluate(context)
        if veto:
            print(f"Test {i}: ❌ VETOED")
            print(f"  Reason Code: {veto.reason_code.value}")
            print(f"  Policy: {veto.policy_name}")
            print(f"  Message: {veto.message}\n")
        else:
            print(f"Test {i}: ✓ PASSED\n")

    # Show veto statistics
    print("Veto History Summary:")
    print(f"Total vetoes: {len(engine.veto_history)}")
    print("\nVetoes by reason code:")
    for reason_code in ReasonCode:
        vetoes = engine.get_vetoes_by_reason(reason_code)
        if vetoes:
            print(f"  {reason_code.value}: {len(vetoes)}")
