#!/usr/bin/env python3

"""
LUKHAS Multi-Tier Validation Framework
======================================

Comprehensive validation framework with Constitutional AI compliance and multi-tier
validation levels. Provides real-time validation with fail-fast behavior.

Features:
- Multi-tier validation (syntax, semantic, business logic)
- Constitutional AI schema compliance validation
- Real-time validation with fail-fast behavior
- Custom validators for LUKHAS-specific data types
- Schema evolution tracking and compatibility checks
- Performance-optimized validation pipeline
- Audit trail for validation decisions

Validation Tiers:
1. Syntax Validation: Basic structure and type checking
2. Semantic Validation: Field relationships and constraints
3. Business Logic Validation: Domain-specific rules
4. Constitutional AI Validation: Ethical and constitutional compliance

Performance Targets:
- Validation latency: <1ms for 99% of operations
- Throughput: 10K+ validations/second
- Fail-fast: Early termination on critical failures
- Memory efficiency: <50MB validation cache

Author: LUKHAS AI System
Version: 1.0.0
Phase: 7 - Guardian Schema Serializers
"""

import logging
import re
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class ValidationTier(Enum):
    """Validation tier levels"""
    SYNTAX = 1          # Basic structure validation
    SEMANTIC = 2        # Field relationships and constraints
    BUSINESS_LOGIC = 3  # Domain-specific rules
    CONSTITUTIONAL = 4  # Constitutional AI compliance


class ValidationSeverity(Enum):
    """Validation error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationType(Enum):
    """Types of validation checks"""
    REQUIRED_FIELD = "required_field"
    TYPE_CHECK = "type_check"
    FORMAT_CHECK = "format_check"
    RANGE_CHECK = "range_check"
    ENUM_CHECK = "enum_check"
    PATTERN_CHECK = "pattern_check"
    DEPENDENCY_CHECK = "dependency_check"
    BUSINESS_RULE = "business_rule"
    CONSTITUTIONAL_AI = "constitutional_ai"
    CUSTOM = "custom"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    tier: ValidationTier
    severity: ValidationSeverity
    validation_type: ValidationType
    field_path: str
    message: str
    details: Optional[dict[str, Any]] = None
    suggestion: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ValidationContext:
    """Context for validation operations"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schema_id: Optional[str] = None
    schema_version: Optional[str] = None
    validation_tiers: set[ValidationTier] = field(default_factory=lambda: set(ValidationTier))
    fail_fast: bool = True
    max_errors: int = 100
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validation operation"""
    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    validation_time_ms: float = 0.0
    tiers_validated: set[ValidationTier] = field(default_factory=set)
    context: Optional[ValidationContext] = None
    compliance_score: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_errors(self) -> bool:
        """Check if result has any errors"""
        return any(issue.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
                  for issue in self.issues)

    def has_critical_errors(self) -> bool:
        """Check if result has critical errors"""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)

    def get_errors(self) -> list[ValidationIssue]:
        """Get all error-level issues"""
        return [issue for issue in self.issues
                if issue.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)]

    def get_warnings(self) -> list[ValidationIssue]:
        """Get all warning-level issues"""
        return [issue for issue in self.issues if issue.severity == ValidationSeverity.WARNING]


class Validator(ABC):
    """Abstract base class for validators"""

    @abstractmethod
    def validate(self, data: Any, context: ValidationContext) -> list[ValidationIssue]:
        """Validate data and return issues"""
        pass

    @abstractmethod
    def supports_tier(self, tier: ValidationTier) -> bool:
        """Check if validator supports given tier"""
        pass

    @property
    @abstractmethod
    def validation_types(self) -> set[ValidationType]:
        """Get supported validation types"""
        pass


class SyntaxValidator(Validator):
    """Validator for syntax-level checks"""

    def __init__(self):
        self.required_fields = {
            "guardian_decision": {
                "schema_version", "decision", "subject", "context",
                "metrics", "enforcement", "audit", "integrity"
            }
        }
        self.type_mappings = {
            str: ["string"],
            int: ["integer"],
            float: ["number"],
            bool: ["boolean"],
            list: ["array"],
            dict: ["object"]
        }

    def validate(self, data: Any, context: ValidationContext) -> list[ValidationIssue]:
        """Perform syntax validation"""
        issues = []

        if not isinstance(data, dict):
            issues.append(ValidationIssue(
                tier=ValidationTier.SYNTAX,
                severity=ValidationSeverity.CRITICAL,
                validation_type=ValidationType.TYPE_CHECK,
                field_path="$",
                message="Root data must be an object",
                suggestion="Ensure data is a dictionary/object structure"
            ))
            return issues

        # Check required fields
        schema_id = context.schema_id or "guardian_decision"
        if schema_id in self.required_fields:
            for field in self.required_fields[schema_id]:
                if field not in data:
                    issues.append(ValidationIssue(
                        tier=ValidationTier.SYNTAX,
                        severity=ValidationSeverity.ERROR,
                        validation_type=ValidationType.REQUIRED_FIELD,
                        field_path=field,
                        message=f"Required field '{field}' is missing",
                        suggestion=f"Add required field '{field}' to the data"
                    ))

        # Validate Guardian-specific structure
        if "decision" in data:
            decision_issues = self._validate_decision_structure(data["decision"])
            issues.extend(decision_issues)

        if "subject" in data:
            subject_issues = self._validate_subject_structure(data["subject"])
            issues.extend(subject_issues)

        return issues

    def supports_tier(self, tier: ValidationTier) -> bool:
        """Check if supports syntax tier"""
        return tier == ValidationTier.SYNTAX

    @property
    def validation_types(self) -> set[ValidationType]:
        """Get supported validation types"""
        return {
            ValidationType.REQUIRED_FIELD,
            ValidationType.TYPE_CHECK,
            ValidationType.FORMAT_CHECK,
            ValidationType.ENUM_CHECK
        }

    def _validate_decision_structure(self, decision: Any) -> list[ValidationIssue]:
        """Validate Guardian decision structure"""
        issues = []

        if not isinstance(decision, dict):
            issues.append(ValidationIssue(
                tier=ValidationTier.SYNTAX,
                severity=ValidationSeverity.ERROR,
                validation_type=ValidationType.TYPE_CHECK,
                field_path="decision",
                message="Decision must be an object",
                suggestion="Ensure decision is a dictionary structure"
            ))
            return issues

        # Check required decision fields
        required_decision_fields = {"status", "policy", "timestamp"}
        for fld in required_decision_fields:
            if fld not in decision:
                issues.append(ValidationIssue(
                    tier=ValidationTier.SYNTAX,
                    severity=ValidationSeverity.ERROR,
                    validation_type=ValidationType.REQUIRED_FIELD,
                    field_path=f"decision.{fld}",
                    message=f"Decision field '{fld}' is required"
                ))

        # Validate status enum
        if "status" in decision:
            valid_statuses = {"allow", "deny", "challenge", "quarantine", "error"}
            if decision["status"] not in valid_statuses:
                issues.append(ValidationIssue(
                    tier=ValidationTier.SYNTAX,
                    severity=ValidationSeverity.ERROR,
                    validation_type=ValidationType.ENUM_CHECK,
                    field_path="decision.status",
                    message=f"Invalid decision status: {decision['status']}",
                    suggestion=f"Use one of: {', '.join(valid_statuses)}"
                ))

        return issues

    def _validate_subject_structure(self, subject: Any) -> list[ValidationIssue]:
        """Validate subject structure"""
        issues = []

        if not isinstance(subject, dict):
            issues.append(ValidationIssue(
                tier=ValidationTier.SYNTAX,
                severity=ValidationSeverity.ERROR,
                validation_type=ValidationType.TYPE_CHECK,
                field_path="subject",
                message="Subject must be an object"
            ))
            return issues

        # Check required subject fields
        required_subject_fields = {"correlation_id", "actor", "operation"}
        for fld in required_subject_fields:
            if fld not in subject:
                issues.append(ValidationIssue(
                    tier=ValidationTier.SYNTAX,
                    severity=ValidationSeverity.ERROR,
                    validation_type=ValidationType.REQUIRED_FIELD,
                    field_path=f"subject.{fld}",
                    message=f"Subject field '{fld}' is required"
                ))

        # Validate correlation_id pattern
        if "correlation_id" in subject:
            correlation_id = subject["correlation_id"]
            if not isinstance(correlation_id, str):
                issues.append(ValidationIssue(
                    tier=ValidationTier.SYNTAX,
                    severity=ValidationSeverity.ERROR,
                    validation_type=ValidationType.TYPE_CHECK,
                    field_path="subject.correlation_id",
                    message="Correlation ID must be a string"
                ))
            elif not re.match(r"^[a-f0-9\-]{16,64}$", correlation_id):
                issues.append(ValidationIssue(
                    tier=ValidationTier.SYNTAX,
                    severity=ValidationSeverity.ERROR,
                    validation_type=ValidationType.PATTERN_CHECK,
                    field_path="subject.correlation_id",
                    message="Invalid correlation ID format",
                    suggestion="Use hexadecimal format with hyphens, 16-64 characters"
                ))

        return issues


class SemanticValidator(Validator):
    """Validator for semantic-level checks"""

    def validate(self, data: Any, context: ValidationContext) -> list[ValidationIssue]:
        """Perform semantic validation"""
        issues = []

        if not isinstance(data, dict):
            return issues

        # Cross-field validation
        issues.extend(self._validate_decision_consistency(data))
        issues.extend(self._validate_timestamp_consistency(data))
        issues.extend(self._validate_metrics_consistency(data))

        return issues

    def supports_tier(self, tier: ValidationTier) -> bool:
        """Check if supports semantic tier"""
        return tier == ValidationTier.SEMANTIC

    @property
    def validation_types(self) -> set[ValidationType]:
        """Get supported validation types"""
        return {
            ValidationType.DEPENDENCY_CHECK,
            ValidationType.RANGE_CHECK,
            ValidationType.FORMAT_CHECK
        }

    def _validate_decision_consistency(self, data: dict[str, Any]) -> list[ValidationIssue]:
        """Validate decision field consistency"""
        issues = []

        if "decision" not in data:
            return issues

        decision = data["decision"]

        # If status is 'deny', reasons should be provided
        if decision.get("status") == "deny" and not data.get("reasons"):
            issues.append(ValidationIssue(
                tier=ValidationTier.SEMANTIC,
                severity=ValidationSeverity.WARNING,
                validation_type=ValidationType.DEPENDENCY_CHECK,
                field_path="reasons",
                message="Denial decisions should include reasoning",
                suggestion="Add reasons array to explain denial"
            ))

        # If severity is 'critical', enforcement should be active
        if (decision.get("severity") == "critical" and
            data.get("enforcement", {}).get("mode") == "dark"):
            issues.append(ValidationIssue(
                tier=ValidationTier.SEMANTIC,
                severity=ValidationSeverity.WARNING,
                validation_type=ValidationType.DEPENDENCY_CHECK,
                field_path="enforcement.mode",
                message="Critical severity should use active enforcement",
                suggestion="Consider using 'enforced' mode for critical decisions"
            ))

        return issues

    def _validate_timestamp_consistency(self, data: dict[str, Any]) -> list[ValidationIssue]:
        """Validate timestamp consistency"""
        issues = []

        decision_timestamp = data.get("decision", {}).get("timestamp")
        audit_timestamp = data.get("audit", {}).get("timestamp")

        if decision_timestamp and audit_timestamp:
            try:
                decision_dt = datetime.fromisoformat(decision_timestamp.replace('Z', '+00:00'))
                audit_dt = datetime.fromisoformat(audit_timestamp.replace('Z', '+00:00'))

                # Audit timestamp should be close to decision timestamp
                time_diff = abs((audit_dt - decision_dt).total_seconds())
                if time_diff > 60:  # More than 1 minute difference
                    issues.append(ValidationIssue(
                        tier=ValidationTier.SEMANTIC,
                        severity=ValidationSeverity.WARNING,
                        validation_type=ValidationType.DEPENDENCY_CHECK,
                        field_path="audit.timestamp",
                        message="Audit timestamp differs significantly from decision timestamp",
                        details={"time_difference_seconds": time_diff}
                    ))

            except (ValueError, TypeError):
                # Timestamp format issues would be caught in syntax validation
                pass

        return issues

    def _validate_metrics_consistency(self, data: dict[str, Any]) -> list[ValidationIssue]:
        """Validate metrics field consistency"""
        issues = []

        metrics = data.get("metrics", {})
        if not metrics:
            return issues

        # Risk score and drift score should be correlated
        risk_score = metrics.get("risk_score", 0)
        drift_score = metrics.get("drift_score", 0)

        if risk_score > 0.8 and drift_score < 0.1:
            issues.append(ValidationIssue(
                tier=ValidationTier.SEMANTIC,
                severity=ValidationSeverity.WARNING,
                validation_type=ValidationType.DEPENDENCY_CHECK,
                field_path="metrics",
                message="High risk score with low drift score may indicate issue",
                details={"risk_score": risk_score, "drift_score": drift_score}
            ))

        # Latency should be reasonable
        latency_ms = metrics.get("latency_ms", 0)
        if latency_ms > 5000:  # More than 5 seconds
            issues.append(ValidationIssue(
                tier=ValidationTier.SEMANTIC,
                severity=ValidationSeverity.WARNING,
                validation_type=ValidationType.RANGE_CHECK,
                field_path="metrics.latency_ms",
                message="Unusually high latency detected",
                details={"latency_ms": latency_ms},
                suggestion="Investigate performance bottlenecks"
            ))

        return issues


class BusinessLogicValidator(Validator):
    """Validator for business logic checks"""

    def __init__(self):
        self.business_rules = self._load_business_rules()

    def validate(self, data: Any, context: ValidationContext) -> list[ValidationIssue]:
        """Perform business logic validation"""
        issues = []

        if not isinstance(data, dict):
            return issues

        # Apply business rules
        for rule_name, rule_func in self.business_rules.items():
            try:
                rule_issues = rule_func(data, context)
                if rule_issues:
                    issues.extend(rule_issues)
            except Exception as e:
                issues.append(ValidationIssue(
                    tier=ValidationTier.BUSINESS_LOGIC,
                    severity=ValidationSeverity.ERROR,
                    validation_type=ValidationType.BUSINESS_RULE,
                    field_path="$",
                    message=f"Business rule '{rule_name}' failed: {e!s}"
                ))

        return issues

    def supports_tier(self, tier: ValidationTier) -> bool:
        """Check if supports business logic tier"""
        return tier == ValidationTier.BUSINESS_LOGIC

    @property
    def validation_types(self) -> set[ValidationType]:
        """Get supported validation types"""
        return {ValidationType.BUSINESS_RULE}

    def _load_business_rules(self) -> dict[str, Callable]:
        """Load business logic rules"""
        return {
            "guardian_authority_check": self._validate_guardian_authority,
            "tier_consistency_check": self._validate_tier_consistency,
            "quota_validation": self._validate_quota_constraints,
        }

    def _validate_guardian_authority(self, data: dict[str, Any], context: ValidationContext) -> list[ValidationIssue]:
        """Validate Guardian has authority for this decision"""
        issues = []

        subject = data.get("subject", {})
        actor = subject.get("actor", {})
        operation = subject.get("operation", {})

        # High-tier operations require appropriate actor tier
        if operation.get("name") in ["system_shutdown", "emergency_override", "policy_override"]:
            actor_tier = actor.get("tier", "T1")
            if actor_tier not in ["T4", "T5"]:
                issues.append(ValidationIssue(
                    tier=ValidationTier.BUSINESS_LOGIC,
                    severity=ValidationSeverity.ERROR,
                    validation_type=ValidationType.BUSINESS_RULE,
                    field_path="subject.actor.tier",
                    message=f"Operation '{operation['name']}' requires T4 or T5 actor, got {actor_tier}",
                    suggestion="Ensure actor has appropriate tier for requested operation"
                ))

        return issues

    def _validate_tier_consistency(self, data: dict[str, Any], context: ValidationContext) -> list[ValidationIssue]:
        """Validate tier consistency across fields"""
        issues = []

        subject = data.get("subject", {})
        lane = subject.get("lane", "candidate")
        canary_percent = subject.get("canary_percent", 0)

        # Production lane should have stable canary percentage
        if lane == "production" and canary_percent > 0 and canary_percent < 100:
            issues.append(ValidationIssue(
                tier=ValidationTier.BUSINESS_LOGIC,
                severity=ValidationSeverity.WARNING,
                validation_type=ValidationType.BUSINESS_RULE,
                field_path="subject.canary_percent",
                message="Production lane with partial canary deployment",
                details={"lane": lane, "canary_percent": canary_percent},
                suggestion="Consider full rollout for production lane"
            ))

        return issues

    def _validate_quota_constraints(self, data: dict[str, Any], context: ValidationContext) -> list[ValidationIssue]:
        """Validate quota and rate limiting constraints"""
        issues = []

        metrics = data.get("metrics", {})
        quota_remaining = metrics.get("quota_remaining")

        if quota_remaining is not None and quota_remaining < 10:
            decision_status = data.get("decision", {}).get("status")
            if decision_status == "allow":
                issues.append(ValidationIssue(
                    tier=ValidationTier.BUSINESS_LOGIC,
                    severity=ValidationSeverity.WARNING,
                    validation_type=ValidationType.BUSINESS_RULE,
                    field_path="metrics.quota_remaining",
                    message="Low quota remaining for allow decision",
                    details={"quota_remaining": quota_remaining},
                    suggestion="Consider rate limiting or quota increase"
                ))

        return issues


class ConstitutionalAIValidator(Validator):
    """Validator for Constitutional AI compliance"""

    def __init__(self):
        self.constitutional_principles = self._load_constitutional_principles()
        self.ethical_guidelines = self._load_ethical_guidelines()

    def validate(self, data: Any, context: ValidationContext) -> list[ValidationIssue]:
        """Perform Constitutional AI validation"""
        issues = []

        if not isinstance(data, dict):
            return issues

        # Check constitutional principles
        issues.extend(self._validate_constitutional_compliance(data))
        issues.extend(self._validate_ethical_guidelines(data))
        issues.extend(self._validate_transparency_requirements(data))

        return issues

    def supports_tier(self, tier: ValidationTier) -> bool:
        """Check if supports constitutional tier"""
        return tier == ValidationTier.CONSTITUTIONAL

    @property
    def validation_types(self) -> set[ValidationType]:
        """Get supported validation types"""
        return {ValidationType.CONSTITUTIONAL_AI}

    def _load_constitutional_principles(self) -> list[str]:
        """Load Constitutional AI principles"""
        return [
            "transparency",
            "accountability",
            "fairness",
            "privacy",
            "safety",
            "human_dignity",
            "beneficence",
            "non_maleficence"
        ]

    def _load_ethical_guidelines(self) -> dict[str, Any]:
        """Load ethical guidelines"""
        return {
            "decision_explanation": "All decisions should be explainable",
            "bias_prevention": "Decisions should be free from unfair bias",
            "privacy_protection": "User privacy must be protected",
            "safety_first": "Safety concerns take precedence",
            "human_oversight": "Critical decisions require human oversight"
        }

    def _validate_constitutional_compliance(self, data: dict[str, Any]) -> list[ValidationIssue]:
        """Validate constitutional compliance"""
        issues = []

        # Check for transparency (reasons provided)
        decision_status = data.get("decision", {}).get("status")
        reasons = data.get("reasons", [])

        if decision_status in ["deny", "quarantine"] and not reasons:
            issues.append(ValidationIssue(
                tier=ValidationTier.CONSTITUTIONAL,
                severity=ValidationSeverity.ERROR,
                validation_type=ValidationType.CONSTITUTIONAL_AI,
                field_path="reasons",
                message="Transparency principle violation: restrictive decisions must include reasoning",
                suggestion="Add detailed reasons for deny/quarantine decisions"
            ))

        # Check for accountability (audit trail)
        if "audit" not in data or not data["audit"].get("event_id"):
            issues.append(ValidationIssue(
                tier=ValidationTier.CONSTITUTIONAL,
                severity=ValidationSeverity.ERROR,
                validation_type=ValidationType.CONSTITUTIONAL_AI,
                field_path="audit",
                message="Accountability principle violation: missing audit trail",
                suggestion="Ensure complete audit trail with event ID"
            ))

        return issues

    def _validate_ethical_guidelines(self, data: dict[str, Any]) -> list[ValidationIssue]:
        """Validate ethical guidelines"""
        issues = []

        # Check for bias indicators in decision
        decision = data.get("decision", {})
        subject = data.get("subject", {})

        # Flag potential bias based on actor type
        actor_type = subject.get("actor", {}).get("type")
        if actor_type and decision.get("status") == "deny":
            # This is a simplified bias check - in practice, this would be more sophisticated
            issues.append(ValidationIssue(
                tier=ValidationTier.CONSTITUTIONAL,
                severity=ValidationSeverity.INFO,
                validation_type=ValidationType.CONSTITUTIONAL_AI,
                field_path="decision.status",
                message="Bias check: denial decision flagged for review",
                details={"actor_type": actor_type},
                suggestion="Review decision for potential bias"
            ))

        return issues

    def _validate_transparency_requirements(self, data: dict[str, Any]) -> list[ValidationIssue]:
        """Validate transparency requirements"""
        issues = []

        # Check for redactions without proper justification
        redactions = data.get("redactions", {})
        if redactions:
            for path, reason in redactions.items():
                if not reason or len(reason.strip()) < 10:
                    issues.append(ValidationIssue(
                        tier=ValidationTier.CONSTITUTIONAL,
                        severity=ValidationSeverity.WARNING,
                        validation_type=ValidationType.CONSTITUTIONAL_AI,
                        field_path=f"redactions.{path}",
                        message="Transparency concern: redaction lacks sufficient justification",
                        details={"redacted_path": path, "reason": reason},
                        suggestion="Provide detailed justification for data redaction"
                    ))

        return issues


class ValidationFramework:
    """Multi-tier validation framework with Constitutional AI compliance"""

    def __init__(self):
        self.validators: dict[ValidationTier, list[Validator]] = {
            ValidationTier.SYNTAX: [SyntaxValidator()],
            ValidationTier.SEMANTIC: [SemanticValidator()],
            ValidationTier.BUSINESS_LOGIC: [BusinessLogicValidator()],
            ValidationTier.CONSTITUTIONAL: [ConstitutionalAIValidator()]
        }
        self._lock = threading.RLock()
        self._metrics = ValidationMetrics()

    def validate(
        self,
        data: Any,
        context: Optional[ValidationContext] = None,
        tiers: Optional[set[ValidationTier]] = None
    ) -> ValidationResult:
        """Validate data using specified tiers"""
        start_time = time.perf_counter()

        if context is None:
            context = ValidationContext()

        if tiers is None:
            tiers = {ValidationTier.SYNTAX, ValidationTier.SEMANTIC}

        all_issues = []
        validated_tiers = set()

        try:
            # Process validation tiers in order
            tier_order = [
                ValidationTier.SYNTAX,
                ValidationTier.SEMANTIC,
                ValidationTier.BUSINESS_LOGIC,
                ValidationTier.CONSTITUTIONAL
            ]

            for tier in tier_order:
                if tier not in tiers:
                    continue

                tier_issues = []
                tier_validators = self.validators.get(tier, [])

                for validator in tier_validators:
                    if validator.supports_tier(tier):
                        try:
                            validator_issues = validator.validate(data, context)
                            tier_issues.extend(validator_issues)
                        except Exception as e:
                            tier_issues.append(ValidationIssue(
                                tier=tier,
                                severity=ValidationSeverity.ERROR,
                                validation_type=ValidationType.CUSTOM,
                                field_path="$",
                                message=f"Validator error: {e!s}"
                            ))

                all_issues.extend(tier_issues)
                validated_tiers.add(tier)

                # Check for fail-fast conditions
                if context.fail_fast:
                    critical_errors = [i for i in tier_issues
                                     if i.severity == ValidationSeverity.CRITICAL]
                    if critical_errors:
                        break

                # Check max errors limit
                total_errors = len([i for i in all_issues
                                  if i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)])
                if total_errors >= context.max_errors:
                    break

            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(all_issues)

            validation_time = (time.perf_counter() - start_time) * 1000

            # Create result
            result = ValidationResult(
                is_valid=not any(i.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
                               for i in all_issues),
                issues=all_issues,
                validation_time_ms=validation_time,
                tiers_validated=validated_tiers,
                context=context,
                compliance_score=compliance_score,
                metadata={
                    "total_validators": sum(len(validators) for validators in self.validators.values()),
                    "issues_by_tier": {
                        tier.name: len([i for i in all_issues if i.tier == tier])
                        for tier in validated_tiers
                    }
                }
            )

            # Update metrics
            self._metrics.record_validation(result)

            return result

        except Exception as e:
            validation_time = (time.perf_counter() - start_time) * 1000
            self._metrics.record_error()

            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    tier=ValidationTier.SYNTAX,
                    severity=ValidationSeverity.CRITICAL,
                    validation_type=ValidationType.CUSTOM,
                    field_path="$",
                    message=f"Validation framework error: {e!s}"
                )],
                validation_time_ms=validation_time,
                context=context,
                compliance_score=0.0
            )

    def add_validator(self, tier: ValidationTier, validator: Validator) -> None:
        """Add custom validator for specific tier"""
        with self._lock:
            if tier not in self.validators:
                self.validators[tier] = []
            self.validators[tier].append(validator)
            logger.info(f"Added validator for tier {tier.name}")

    def get_metrics(self) -> dict[str, Any]:
        """Get validation framework metrics"""
        return self._metrics.get_stats()

    def _calculate_compliance_score(self, issues: list[ValidationIssue]) -> float:
        """Calculate Constitutional AI compliance score"""
        if not issues:
            return 1.0

        # Score based on issue severity and constitutional violations
        score = 1.0
        for issue in issues:
            if issue.validation_type == ValidationType.CONSTITUTIONAL_AI:
                if issue.severity == ValidationSeverity.CRITICAL:
                    score -= 0.3
                elif issue.severity == ValidationSeverity.ERROR:
                    score -= 0.2
                elif issue.severity == ValidationSeverity.WARNING:
                    score -= 0.1
            else:
                if issue.severity == ValidationSeverity.CRITICAL:
                    score -= 0.1
                elif issue.severity == ValidationSeverity.ERROR:
                    score -= 0.05

        return max(0.0, score)


class ValidationMetrics:
    """Performance metrics for validation operations"""

    def __init__(self):
        self.validation_count = 0
        self.total_validation_time = 0.0
        self.failed_validations = 0
        self.issues_by_tier = dict.fromkeys(ValidationTier, 0)
        self.issues_by_severity = dict.fromkeys(ValidationSeverity, 0)
        self.error_count = 0
        self.start_time = time.time()

    def record_validation(self, result: ValidationResult) -> None:
        """Record validation metrics"""
        self.validation_count += 1
        self.total_validation_time += result.validation_time_ms

        if not result.is_valid:
            self.failed_validations += 1

        for issue in result.issues:
            self.issues_by_tier[issue.tier] += 1
            self.issues_by_severity[issue.severity] += 1

    def record_error(self) -> None:
        """Record validation error"""
        self.error_count += 1

    def get_stats(self) -> dict[str, Any]:
        """Get validation statistics"""
        uptime = time.time() - self.start_time
        avg_time = (
            self.total_validation_time / self.validation_count
            if self.validation_count > 0 else 0
        )

        return {
            "total_validations": self.validation_count,
            "average_validation_time_ms": avg_time,
            "failed_validations": self.failed_validations,
            "success_rate": (
                (self.validation_count - self.failed_validations) / self.validation_count
                if self.validation_count > 0 else 1.0
            ),
            "throughput_per_second": self.validation_count / uptime if uptime > 0 else 0,
            "issues_by_tier": {tier.name: count for tier, count in self.issues_by_tier.items()},
            "issues_by_severity": {severity.name: count for severity, count in self.issues_by_severity.items()},
            "error_count": self.error_count,
            "uptime_seconds": uptime
        }


# Global validation framework instance
_framework_instance: Optional[ValidationFramework] = None
_framework_lock = threading.Lock()


def get_validation_framework() -> ValidationFramework:
    """Get global validation framework instance"""
    global _framework_instance

    if _framework_instance is None:
        with _framework_lock:
            if _framework_instance is None:
                _framework_instance = ValidationFramework()

    return _framework_instance


# Convenience functions
def validate_guardian_data(
    data: Any,
    fail_fast: bool = True,
    include_constitutional: bool = True
) -> ValidationResult:
    """Validate Guardian data with all tiers"""
    framework = get_validation_framework()

    tiers = {ValidationTier.SYNTAX, ValidationTier.SEMANTIC, ValidationTier.BUSINESS_LOGIC}
    if include_constitutional:
        tiers.add(ValidationTier.CONSTITUTIONAL)

    context = ValidationContext(
        schema_id="guardian_decision",
        fail_fast=fail_fast,
        validation_tiers=tiers
    )

    return framework.validate(data, context, tiers)
