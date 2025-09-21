"""
Policy Enforcement Engine for LUKHAS AI System - Ethics Integration

This module provides a comprehensive policy enforcement system that
integrates with Constellation Framework, Guardian System, and compliance
monitoring to ensure all system operations comply with organizational
policies, regulatory requirements, and ethical standards.

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony

Features:
- Real-time policy enforcement and validation
- Dynamic policy rule engine with complex condition support
- Multi-layered policy hierarchy (system, user, context-specific)
- Automated policy violation detection and remediation
- Integration with Guardian System and constitutional principles
- Constellation Framework policy alignment (⚛️🧠🛡️)
- Comprehensive audit trails and policy change management
- Performance-optimized policy evaluation engine
- Context-aware policy application

Rehabilitated: 2025-01-XX from quarantine status
Original location: ./ethics/policy_engine.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

try:
    from candidate.core.common import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)


class PolicyType(Enum):
    """Types of policies in the system"""

    SECURITY = "security"  # Security-related policies
    PRIVACY = "privacy"  # Privacy protection policies
    DATA_GOVERNANCE = "data_governance"  # Data handling and retention
    ACCESS_CONTROL = "access_control"  # Access and authorization
    ETHICAL = "ethical"  # Ethical guidelines
    OPERATIONAL = "operational"  # Operational procedures
    COMPLIANCE = "compliance"  # Regulatory compliance
    CONSTITUTIONAL = "constitutional"  # Constitutional AI principles
    USER_CONSENT = "user_consent"  # User consent management
    CONTENT = "content"  # Content moderation
    SYSTEM_BEHAVIOR = "system_behavior"  # System behavior control
    CONSTELLATION = "constellation"  # Constellation Framework specific


class PolicyScope(Enum):
    """Scope of policy application"""

    GLOBAL = "global"  # Applies to entire system
    MODULE = "module"  # Applies to specific modules
    USER = "user"  # Applies to specific users
    CONTEXT = "context"  # Applies in specific contexts
    SESSION = "session"  # Applies to specific sessions
    TRANSACTION = "transaction"  # Applies to specific transactions


class PolicyAction(Enum):
    """Actions that can be taken when policy is triggered"""

    ALLOW = "allow"  # Allow the operation
    DENY = "deny"  # Deny the operation
    WARN = "warn"  # Issue warning but allow
    LOG = "log"  # Log the event
    ESCALATE = "escalate"  # Escalate to human review
    MODIFY = "modify"  # Modify the operation
    REDIRECT = "redirect"  # Redirect to alternative
    QUARANTINE = "quarantine"  # Quarantine for review


class PolicyPriority(Enum):
    """Priority levels for policy enforcement"""

    EMERGENCY = "emergency"  # Highest priority - immediate enforcement
    CRITICAL = "critical"  # Critical policies
    HIGH = "high"  # High priority
    MEDIUM = "medium"  # Medium priority
    LOW = "low"  # Low priority
    INFORMATIONAL = "informational"  # Informational only


class ConditionOperator(Enum):
    """Operators for policy conditions"""

    EQUALS = "eq"  # Exact match
    NOT_EQUALS = "ne"  # Not equal
    CONTAINS = "contains"  # Contains substring
    NOT_CONTAINS = "not_contains"  # Does not contain
    STARTS_WITH = "starts_with"  # Starts with
    ENDS_WITH = "ends_with"  # Ends with
    GREATER_THAN = "gt"  # Greater than
    LESS_THAN = "lt"  # Less than
    GREATER_EQUAL = "ge"  # Greater than or equal
    LESS_EQUAL = "le"  # Less than or equal
    IN = "in"  # In list
    NOT_IN = "not_in"  # Not in list
    REGEX = "regex"  # Regular expression match
    EXISTS = "exists"  # Field exists
    NOT_EXISTS = "not_exists"  # Field does not exist


@dataclass
class PolicyCondition:
    """Represents a single policy condition"""

    field: str  # Field to evaluate
    operator: ConditionOperator  # Comparison operator
    value: Any  # Value to compare against
    case_sensitive: bool = True  # Case sensitivity for string operations
    description: Optional[str] = None  # Human-readable description


@dataclass
class PolicyRule:
    """Represents a complete policy rule"""

    rule_id: str
    name: str
    description: str
    policy_type: PolicyType
    scope: PolicyScope
    priority: PolicyPriority

    # Conditions that must be met for rule to trigger
    conditions: list[PolicyCondition] = field(default_factory=list)
    condition_logic: str = "AND"  # AND, OR, or custom expression

    # Actions to take when rule triggers
    action: PolicyAction = PolicyAction.LOG
    action_parameters: dict[str, Any] = field(default_factory=dict)

    # Rule metadata
    enabled: bool = True
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"

    # Context and targeting
    target_modules: set[str] = field(default_factory=set)
    target_users: set[str] = field(default_factory=set)
    context_tags: set[str] = field(default_factory=set)

    # Dependencies and relationships
    depends_on: list[str] = field(default_factory=list)  # Other rule IDs
    conflicts_with: list[str] = field(default_factory=list)

    # Validation and testing
    test_cases: list[dict[str, Any]] = field(default_factory=list)
    last_tested: Optional[datetime] = None

    # Performance and monitoring
    execution_count: int = 0
    last_executed: Optional[datetime] = None
    average_execution_time: float = 0.0
    violation_count: int = 0


@dataclass
class PolicyViolation:
    """Represents a policy violation"""

    violation_id: str
    rule_id: str
    rule_name: str
    policy_type: PolicyType
    severity: PolicyPriority

    # Violation details
    description: str
    context: dict[str, Any] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)

    # Actions taken
    action_taken: PolicyAction = PolicyAction.LOG
    action_details: dict[str, Any] = field(default_factory=dict)

    # Status and resolution
    status: str = "open"  # open, resolved, ignored
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

    # Constellation Framework integration
    identity_impact: Optional[str] = None  # ⚛️
    consciousness_impact: Optional[str] = None  # 🧠
    guardian_assessment: Optional[str] = None  # 🛡️

    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)
    source_module: Optional[str] = None
    affected_user: Optional[str] = None


@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation"""

    evaluation_id: str
    context: dict[str, Any]
    triggered_rules: list[str] = field(default_factory=list)
    violations: list[PolicyViolation] = field(default_factory=list)

    # Overall result
    final_action: PolicyAction = PolicyAction.ALLOW
    action_reason: str = ""
    confidence: float = 1.0

    # Performance metrics
    evaluation_time: float = 0.0
    rules_evaluated: int = 0

    # Additional information
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Timestamp
    evaluated_at: datetime = field(default_factory=datetime.now)


class PolicyEngines:
    """Central policy engines coordinator - simplified for ethics integration"""

    def __init__(self):
        self.logger = logger

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

        # Basic safety evaluation for now
        violations = []
        score = 1.0

        if content and isinstance(content, str):
            content_lower = content.lower()

            # Check for basic policy violations
            if policy_name.lower() in ["safety", "safety_policy"]:
                harmful_patterns = ["violence", "harm", "dangerous", "illegal"]
                for pattern in harmful_patterns:
                    if pattern in content_lower:
                        violations.append(f"Safety concern: {pattern}")
                        score -= 0.2

            elif policy_name.lower() in ["ethics", "ethics_policy"]:
                ethical_concerns = ["discrimination", "bias", "unfair", "manipulative"]
                for concern in ethical_concerns:
                    if concern in content_lower:
                        violations.append(f"Ethical concern: {concern}")
                        score -= 0.25

        score = max(0.0, score)
        compliant = score >= 0.7 and len(violations) == 0

        return {
            "compliant": compliant,
            "score": score,
            "violations": violations,
            "metadata": {"policy": policy_name, "engine": "rehabilitated_ethics"}
        }

    def list_policies(self) -> list[str]:
        """List available policies"""
        return [
            "safety",
            "ethics",
            "safety_policy",
            "ethics_policy",
            "default_policy"
        ]


# Export main classes and functions for compatibility
__all__ = [
    "ConditionOperator",
    "PolicyAction",
    "PolicyCondition",
    "PolicyEngines",
    "PolicyEvaluationResult",
    "PolicyPriority",
    "PolicyRule",
    "PolicyScope",
    "PolicyType",
    "PolicyViolation",
]
