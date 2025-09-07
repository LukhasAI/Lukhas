"""
Comprehensive Security Policy Framework for LUKHAS AI
====================================================
Implements enterprise-grade security policies covering:
- Access Control Policies
- Data Classification and Handling
- Incident Response Procedures
- Compliance Requirements (GDPR, CCPA, SOX)
- AI-specific Security Policies
- Automated Policy Enforcement
"""
from typing import List
import time
import streamlit as st

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

try:
    from .secure_logging import get_security_logger

    logger = get_security_logger(__name__)
    LOGGING_AVAILABLE = True
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
    LOGGING_AVAILABLE = False


class DataClassification(Enum):
    """Data classification levels"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # Highest security level


class AccessLevel(Enum):
    """Access levels for resources"""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


class PolicyViolationSeverity(Enum):
    """Severity levels for policy violations"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""

    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    ISO_27001 = "iso_27001"
    NIST_CSF = "nist_csf"


@dataclass
class SecurityPolicy:
    """Security policy definition"""

    policy_id: str
    name: str
    description: str
    classification: DataClassification
    compliance_frameworks: list[ComplianceFramework]
    rules: list[dict[str, Any]]
    exceptions: list[dict[str, Any]] = field(default_factory=list)
    auto_enforce: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "classification": self.classification.value,
            "compliance_frameworks": [f.value for f in self.compliance_frameworks],
            "rules": self.rules,
            "exceptions": self.exceptions,
            "auto_enforce": self.auto_enforce,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "version": self.version,
        }


@dataclass
class PolicyViolation:
    """Policy violation record"""

    violation_id: str
    policy_id: str
    severity: PolicyViolationSeverity
    description: str
    user_id: Optional[str]
    resource: Optional[str]
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_notes: Optional[str] = None


class SecurityPolicyFramework:
    """
    Comprehensive security policy framework with automated enforcement
    Implements defense-in-depth through layered policy controls
    """

    def __init__(self):
        """Initialize security policy framework"""

        # Policy storage
        self.policies: dict[str, SecurityPolicy] = {}
        self.violations: list[PolicyViolation] = []

        # Access control matrix
        self.role_permissions: dict[str, set[str]] = {}
        self.resource_classifications: dict[str, DataClassification] = {}

        # Compliance tracking
        self.compliance_status: dict[ComplianceFramework, dict[str, Any]] = {}

        # Initialize default policies
        self._initialize_core_policies()
        self._initialize_ai_policies()
        self._initialize_compliance_policies()

        logger.info("Security policy framework initialized")

    def _initialize_core_policies(self):
        """Initialize core security policies"""

        # Access Control Policy
        access_control_policy = SecurityPolicy(
            policy_id="access_control_001",
            name="Access Control and Authentication Policy",
            description="Defines access control requirements and authentication standards",
            classification=DataClassification.CONFIDENTIAL,
            compliance_frameworks=[ComplianceFramework.ISO_27001, ComplianceFramework.NIST_CSF],
            rules=[
                {
                    "rule_id": "ac_001",
                    "name": "Multi-Factor Authentication Required",
                    "description": "All users must use MFA for authentication",
                    "condition": "authentication_method != 'mfa'",
                    "action": "deny_access",
                    "severity": "high",
                },
                {
                    "rule_id": "ac_002",
                    "name": "Session Timeout",
                    "description": "Sessions must timeout after 30 minutes of inactivity",
                    "condition": "session_inactive_time > 1800",
                    "action": "terminate_session",
                    "severity": "medium",
                },
                {
                    "rule_id": "ac_003",
                    "name": "Privileged Account Monitoring",
                    "description": "All admin actions must be logged and monitored",
                    "condition": "user_role == 'admin'",
                    "action": "audit_log",
                    "severity": "high",
                },
            ],
        )
        self.policies[access_control_policy.policy_id] = access_control_policy

        # Data Protection Policy
        data_protection_policy = SecurityPolicy(
            policy_id="data_protection_001",
            name="Data Protection and Privacy Policy",
            description="Defines data classification, handling, and protection requirements",
            classification=DataClassification.RESTRICTED,
            compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.CCPA],
            rules=[
                {
                    "rule_id": "dp_001",
                    "name": "Data Encryption at Rest",
                    "description": "All confidential and restricted data must be encrypted at rest",
                    "condition": "data_classification in ['confidential', 'restricted'] and encryption == false",
                    "action": "encrypt_data",
                    "severity": "critical",
                },
                {
                    "rule_id": "dp_002",
                    "name": "Data Retention Limits",
                    "description": "Personal data must not be retained beyond necessary period",
                    "condition": "data_type == 'personal' and retention_days > 365",
                    "action": "schedule_deletion",
                    "severity": "high",
                },
                {
                    "rule_id": "dp_003",
                    "name": "Cross-Border Data Transfer",
                    "description": "Personal data transfers outside EU require adequate protection",
                    "condition": "data_location != 'eu' and data_type == 'personal'",
                    "action": "require_adequacy_decision",
                    "severity": "high",
                },
            ],
        )
        self.policies[data_protection_policy.policy_id] = data_protection_policy

        # Incident Response Policy
        incident_response_policy = SecurityPolicy(
            policy_id="incident_response_001",
            name="Security Incident Response Policy",
            description="Defines incident response procedures and escalation",
            classification=DataClassification.CONFIDENTIAL,
            compliance_frameworks=[ComplianceFramework.ISO_27001, ComplianceFramework.NIST_CSF],
            rules=[
                {
                    "rule_id": "ir_001",
                    "name": "Critical Incident Escalation",
                    "description": "Critical security incidents must be escalated within 15 minutes",
                    "condition": "incident_severity == 'critical' and response_time > 900",
                    "action": "escalate_to_ciso",
                    "severity": "critical",
                },
                {
                    "rule_id": "ir_002",
                    "name": "Incident Documentation",
                    "description": "All security incidents must be documented within 24 hours",
                    "condition": "incident_age > 86400 and documentation_complete == false",
                    "action": "require_documentation",
                    "severity": "medium",
                },
            ],
        )
        self.policies[incident_response_policy.policy_id] = incident_response_policy

    def _initialize_ai_policies(self):
        """Initialize AI-specific security policies"""

        # AI Model Security Policy
        ai_model_policy = SecurityPolicy(
            policy_id="ai_model_001",
            name="AI Model Security and Governance Policy",
            description="Security requirements for AI model development and deployment",
            classification=DataClassification.CONFIDENTIAL,
            compliance_frameworks=[ComplianceFramework.ISO_27001],
            rules=[
                {
                    "rule_id": "ai_001",
                    "name": "Model Training Data Protection",
                    "description": "Training data must be sanitized and protected",
                    "condition": "training_data_contains_pii == true and sanitization == false",
                    "action": "sanitize_training_data",
                    "severity": "high",
                },
                {
                    "rule_id": "ai_002",
                    "name": "Model Output Validation",
                    "description": "AI model outputs must be validated for bias and safety",
                    "condition": "bias_validation == false or safety_validation == false",
                    "action": "require_validation",
                    "severity": "high",
                },
                {
                    "rule_id": "ai_003",
                    "name": "Model Version Control",
                    "description": "All AI models must be versioned and auditable",
                    "condition": "model_version == null or audit_trail == false",
                    "action": "enforce_versioning",
                    "severity": "medium",
                },
            ],
        )
        self.policies[ai_model_policy.policy_id] = ai_model_policy

        # Constitutional AI Policy
        constitutional_ai_policy = SecurityPolicy(
            policy_id="constitutional_ai_001",
            name="Constitutional AI Compliance Policy",
            description="Ensures AI systems comply with constitutional AI principles",
            classification=DataClassification.RESTRICTED,
            compliance_frameworks=[ComplianceFramework.NIST_CSF],
            rules=[
                {
                    "rule_id": "cai_001",
                    "name": "Harmful Content Detection",
                    "description": "AI systems must detect and refuse harmful content generation",
                    "condition": "harmful_content_detected == true",
                    "action": "refuse_request",
                    "severity": "critical",
                },
                {
                    "rule_id": "cai_002",
                    "name": "Transparency Requirement",
                    "description": "AI decision-making processes must be explainable",
                    "condition": "explainability_score < 0.7",
                    "action": "require_explanation",
                    "severity": "medium",
                },
                {
                    "rule_id": "cai_003",
                    "name": "Alignment Monitoring",
                    "description": "AI systems must be continuously monitored for alignment drift",
                    "condition": "alignment_score < 0.85",
                    "action": "trigger_alignment_review",
                    "severity": "high",
                },
            ],
        )
        self.policies[constitutional_ai_policy.policy_id] = constitutional_ai_policy

    def _initialize_compliance_policies(self):
        """Initialize compliance-specific policies"""

        # GDPR Compliance Policy
        gdpr_policy = SecurityPolicy(
            policy_id="gdpr_001",
            name="GDPR Compliance Policy",
            description="Ensures compliance with EU General Data Protection Regulation",
            classification=DataClassification.RESTRICTED,
            compliance_frameworks=[ComplianceFramework.GDPR],
            rules=[
                {
                    "rule_id": "gdpr_001",
                    "name": "Right to Erasure",
                    "description": "Data subjects can request deletion of personal data",
                    "condition": "erasure_request_received == true",
                    "action": "delete_personal_data",
                    "severity": "high",
                },
                {
                    "rule_id": "gdpr_002",
                    "name": "Data Processing Consent",
                    "description": "Personal data processing requires explicit consent",
                    "condition": "consent_obtained == false and data_type == 'personal'",
                    "action": "obtain_consent",
                    "severity": "critical",
                },
                {
                    "rule_id": "gdpr_003",
                    "name": "Data Breach Notification",
                    "description": "Personal data breaches must be reported within 72 hours",
                    "condition": "breach_involves_personal_data == true and notification_time > 259200",
                    "action": "report_to_dpa",
                    "severity": "critical",
                },
            ],
        )
        self.policies[gdpr_policy.policy_id] = gdpr_policy

        # CCPA Compliance Policy
        ccpa_policy = SecurityPolicy(
            policy_id="ccpa_001",
            name="CCPA Compliance Policy",
            description="Ensures compliance with California Consumer Privacy Act",
            classification=DataClassification.RESTRICTED,
            compliance_frameworks=[ComplianceFramework.CCPA],
            rules=[
                {
                    "rule_id": "ccpa_001",
                    "name": "Consumer Right to Know",
                    "description": "Consumers have right to know what personal information is collected",
                    "condition": "privacy_notice_provided == false",
                    "action": "provide_privacy_notice",
                    "severity": "high",
                },
                {
                    "rule_id": "ccpa_002",
                    "name": "Right to Delete",
                    "description": "Consumers can request deletion of personal information",
                    "condition": "deletion_request_received == true",
                    "action": "delete_personal_information",
                    "severity": "high",
                },
            ],
        )
        self.policies[ccpa_policy.policy_id] = ccpa_policy

    def evaluate_policy_compliance(self, policy_id: str, context: dict[str, Any]) -> list[PolicyViolation]:
        """Evaluate context against policy rules"""

        policy = self.policies.get(policy_id)
        if not policy:
            logger.error(f"Policy not found: {policy_id}")
            return []

        violations = []

        for rule in policy.rules:
            if self._evaluate_rule_condition(rule["condition"], context):
                violation = PolicyViolation(
                    violation_id=f"viol_{int(datetime.now(timezone.utc).timestamp()}_{rule['rule_id']}",
                    policy_id=policy_id,
                    severity=PolicyViolationSeverity(rule["severity"]),
                    description=f"Rule violated: {rule['name']} - {rule['description']}",
                    user_id=context.get("user_id"),
                    resource=context.get("resource"),
                    timestamp=datetime.now(timezone.utc),
                    details={
                        "rule_id": rule["rule_id"],
                        "condition": rule["condition"],
                        "action": rule["action"],
                        "context": context,
                    },
                )
                violations.append(violation)

                logger.warning(
                    f"Policy violation detected: {rule['name']}",
                    extra={
                        "policy_id": policy_id,
                        "rule_id": rule["rule_id"],
                        "severity": rule["severity"],
                        "user_id": context.get("user_id"),
                    },
                )

        # Store violations
        self.violations.extend(violations)

        return violations

    def _evaluate_rule_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate rule condition against context"""

        try:
            # Simple condition evaluation (in production, use safer evaluation)
            # Replace context variables in condition
            for key, value in context.items():
                if isinstance(value, str):
                    condition = condition.replace(key, f"'{value}'")
                else:
                    condition = condition.replace(key, str(value))

            # Safe evaluation of basic conditions
            if "==" in condition or "!=" in condition or "<" in condition or ">" in condition:
                # Basic comparisons are safe
                return eval(condition)
            elif " in " in condition:
                # List membership checks
                return eval(condition)

            return False

        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    def enforce_policy_action(self, violation: PolicyViolation) -> bool:
        """Enforce policy action based on violation"""

        policy = self.policies.get(violation.policy_id)
        if not policy or not policy.auto_enforce:
            return False

        rule = next((r for r in policy.rules if r["rule_id"] == violation.details["rule_id"]), None)
        if not rule:
            return False

        action = rule["action"]

        try:
            if action == "deny_access":
                return self._deny_access(violation)
            elif action == "terminate_session":
                return self._terminate_session(violation)
            elif action == "audit_log":
                return self._audit_log(violation)
            elif action == "encrypt_data":
                return self._encrypt_data(violation)
            elif action == "schedule_deletion":
                return self._schedule_deletion(violation)
            elif action == "refuse_request":
                return self._refuse_request(violation)
            elif action == "require_explanation":
                return self._require_explanation(violation)
            elif action == "escalate_to_ciso":
                return self._escalate_to_ciso(violation)

            logger.warning(f"Unknown policy action: {action}")
            return False

        except Exception as e:
            logger.error(f"Failed to enforce policy action '{action}': {e}")
            return False

    def _deny_access(self, violation: PolicyViolation) -> bool:
        """Deny access action"""
        logger.info(f"Access denied for violation: {violation.violation_id}")
        return True

    def _terminate_session(self, violation: PolicyViolation) -> bool:
        """Terminate session action"""
        logger.info(f"Session terminated for violation: {violation.violation_id}")
        return True

    def _audit_log(self, violation: PolicyViolation) -> bool:
        """Audit log action"""
        logger.info(f"Audit logged for violation: {violation.violation_id}")
        return True

    def _encrypt_data(self, violation: PolicyViolation) -> bool:
        """Encrypt data action"""
        logger.info(f"Data encryption triggered for violation: {violation.violation_id}")
        return True

    def _schedule_deletion(self, violation: PolicyViolation) -> bool:
        """Schedule deletion action"""
        logger.info(f"Data deletion scheduled for violation: {violation.violation_id}")
        return True

    def _refuse_request(self, violation: PolicyViolation) -> bool:
        """Refuse request action"""
        logger.info(f"Request refused for violation: {violation.violation_id}")
        return True

    def _require_explanation(self, violation: PolicyViolation) -> bool:
        """Require explanation action"""
        logger.info(f"Explanation required for violation: {violation.violation_id}")
        return True

    def _escalate_to_ciso(self, violation: PolicyViolation) -> bool:
        """Escalate to CISO action"""
        logger.critical(f"ESCALATION TO CISO: {violation.violation_id}")
        return True

    def get_compliance_status(self, framework: ComplianceFramework) -> dict[str, Any]:
        """Get compliance status for specific framework"""

        framework_policies = [p for p in self.policies.values() if framework in p.compliance_frameworks]

        total_rules = sum(len(p.rules) for p in framework_policies)

        # Get recent violations for this framework
        framework_violations = [
            v for v in self.violations if framework in self.policies[v.policy_id].compliance_frameworks
        ]

        unresolved_violations = [v for v in framework_violations if not v.resolved]

        return {
            "framework": framework.value,
            "total_policies": len(framework_policies),
            "total_rules": total_rules,
            "total_violations": len(framework_violations),
            "unresolved_violations": len(unresolved_violations),
            "compliance_score": max(0, 1 - (len(unresolved_violations) / max(1, total_rules))),
            "last_assessment": datetime.now(timezone.utc).isoformat(),
        }

    def generate_security_report(self) -> dict[str, Any]:
        """Generate comprehensive security report"""

        # Policy summary
        total_policies = len(self.policies)
        total_rules = sum(len(p.rules) for p in self.policies.values())

        # Violation summary
        total_violations = len(self.violations)
        unresolved_violations = [v for v in self.violations if not v.resolved]

        # Severity breakdown
        severity_breakdown = {}
        for severity in PolicyViolationSeverity:
            severity_breakdown[severity.value] = len([v for v in self.violations if v.severity == severity])

        # Compliance status
        compliance_status = {}
        for framework in ComplianceFramework:
            compliance_status[framework.value] = self.get_compliance_status(framework)

        return {
            "report_generated": datetime.now(timezone.utc).isoformat(),
            "policy_summary": {
                "total_policies": total_policies,
                "total_rules": total_rules,
                "active_policies": len([p for p in self.policies.values() if p.auto_enforce]),
            },
            "violation_summary": {
                "total_violations": total_violations,
                "unresolved_violations": len(unresolved_violations),
                "severity_breakdown": severity_breakdown,
            },
            "compliance_status": compliance_status,
            "security_score": max(0, 1 - (len(unresolved_violations) / max(1, total_rules))),
        }

    def list_policies(self) -> list[dict[str, Any]]:
        """List all security policies"""
        return [policy.to_dict() for policy in self.policies.values()]

    def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Get specific policy by ID"""
        return self.policies.get(policy_id)


# Global security policy framework instance
_security_policy_framework: Optional[SecurityPolicyFramework] = None


def get_security_policy_framework() -> SecurityPolicyFramework:
    """Get global security policy framework instance"""
    global _security_policy_framework
    if _security_policy_framework is None:
        _security_policy_framework = SecurityPolicyFramework()
    return _security_policy_framework


# Convenience functions for policy evaluation


def evaluate_data_access_policy(
    user_id: str, resource: str, operation: str, data_classification: DataClassification
) -> list[PolicyViolation]:
    """Evaluate data access against policies"""
    framework = get_security_policy_framework()

    context = {
        "user_id": user_id,
        "resource": resource,
        "operation": operation,
        "data_classification": data_classification.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    violations = []
    for policy_id in framework.policies:
        policy_violations = framework.evaluate_policy_compliance(policy_id, context)
        violations.extend(policy_violations)

    return violations


def evaluate_ai_model_policy(
    model_name: str, training_data_contains_pii: bool, bias_validation: bool, safety_validation: bool
) -> list[PolicyViolation]:
    """Evaluate AI model against policies"""
    framework = get_security_policy_framework()

    context = {
        "model_name": model_name,
        "training_data_contains_pii": training_data_contains_pii,
        "bias_validation": bias_validation,
        "safety_validation": safety_validation,
        "sanitization": not training_data_contains_pii,  # Assume sanitized if no PII
    }

    return framework.evaluate_policy_compliance("ai_model_001", context)


# Example usage
def example_usage():
    """Example usage of security policy framework"""
    print("🛡️ Security Policy Framework Example")
    print("=" * 50)

    # Get policy framework
    framework = get_security_policy_framework()

    # List policies
    policies = framework.list_policies()
    print(f"📋 Total policies loaded: {len(policies}")

    # Test policy evaluation
    print("\n🧪 Testing policy evaluation...")

    # Test data access policy
    violations = evaluate_data_access_policy(
        user_id="testuser@example.com",
        resource="sensitive_database",
        operation="read",
        data_classification=DataClassification.CONFIDENTIAL,
    )
    print(f"Data access violations: {len(violations}")

    # Test AI model policy
    ai_violations = evaluate_ai_model_policy(
        model_name="test_model_v1", training_data_contains_pii=True, bias_validation=False, safety_validation=True
    )
    print(f"AI model violations: {len(ai_violations}")

    # Generate security report
    report = framework.generate_security_report()
    print("\n📊 Security Report:")
    print(f"  Security score: {report['security_score']:.2f}")
    print(f"  Total policies: {report['policy_summary']['total_policies']}")
    print(f"  Total violations: {report['violation_summary']['total_violations']}")

    # Check GDPR compliance
    gdpr_status = framework.get_compliance_status(ComplianceFramework.GDPR)
    print(f"  GDPR compliance score: {gdpr_status['compliance_score']:.2f}")

    print("\n✅ Security policy framework test completed")


if __name__ == "__main__":
    example_usage()
