"""
Policy Validator for LUKHAS AI System

This module provides comprehensive policy validation capabilities
for the LUKHAS AI consciousness system, ensuring all policies comply
with Constellation Framework principles and organizational standards.

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony

Features:
- Real-time policy validation and verification
- Policy syntax and semantic checking
- Conflict detection between policies
- Dependency validation
- Performance impact assessment
- Constellation Framework compliance validation
- Policy lifecycle management
- Version compatibility checking

Rehabilitated: 2025-09-10 from quarantine status
"""
import logging

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

try:
    from core.common import get_logger
    from governance.ethics.policy_engine import (
        ConditionOperator,
        PolicyAction,
        PolicyCondition,
        PolicyPriority,
        PolicyRule,
        PolicyScope,
        PolicyType,
    )
except ImportError:
    def get_logger(name):
        import logging
        return logging.getLogger(name)

    # Fallback minimal classes if imports fail
    class PolicyRule:
        pass
    class PolicyCondition:
        pass
    class PolicyType(Enum):
        SECURITY = "security"
        PRIVACY = "privacy"
        ETHICAL = "ethical"
    class PolicyScope(Enum):
        GLOBAL = "global"
        MODULE = "module"
    class PolicyPriority(Enum):
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
    class PolicyAction(Enum):
        ALLOW = "allow"
        DENY = "deny"
    class ConditionOperator(Enum):
        EQUALS = "eq"
        CONTAINS = "contains"

logger = get_logger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"      # Must be fixed
    WARNING = "warning"  # Should be reviewed
    INFO = "info"        # Informational
    SUGGESTION = "suggestion"  # Optional improvement


class ValidationCategory(Enum):
    """Categories of validation checks"""
    SYNTAX = "syntax"           # Syntax errors
    SEMANTIC = "semantic"       # Semantic issues
    PERFORMANCE = "performance" # Performance concerns
    SECURITY = "security"       # Security implications
    COMPLIANCE = "compliance"   # Compliance with standards
    CONFLICT = "conflict"       # Conflicts with other policies
    DEPENDENCY = "dependency"   # Dependency issues
    CONSTELLATION = "constellation"         # Constellation Framework compliance


@dataclass
class ValidationIssue:
    """Represents a validation issue"""

    issue_id: str
    category: ValidationCategory
    severity: ValidationSeverity
    title: str
    description: str

    # Location information
    rule_id: Optional[str] = None
    field_path: Optional[str] = None
    line_number: Optional[int] = None

    # Resolution information
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    fix_function: Optional[str] = None

    # Context
    affected_rules: list[str] = field(default_factory=list)
    related_issues: list[str] = field(default_factory=list)

    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)
    validator_version: str = "1.0.0"


@dataclass
class ValidationResult:
    """Result of policy validation"""

    validation_id: str
    policy_count: int
    issues: list[ValidationIssue] = field(default_factory=list)

    # Summary statistics
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    suggestion_count: int = 0

    # Validation metadata
    validation_time: float = 0.0
    validator_version: str = "1.0.0"
    validated_at: datetime = field(default_factory=datetime.now)

    # Overall result
    is_valid: bool = True
    can_deploy: bool = True
    compliance_score: float = 1.0


class PolicyValidator:
    """
    Comprehensive policy validation engine for LUKHAS AI
    
    Provides validation capabilities for policy rules, ensuring they meet
    Constellation Framework standards and organizational requirements.
    """

    def __init__(self):
        self.logger = logger
        self.version = "1.0.0"

        # Validation configuration
        self.max_condition_depth = 10
        self.max_rule_complexity = 100
        self.performance_threshold_ms = 50

        # Constellation Framework validation weights
        self.constellation_weights = {
            "identity": 0.3,      # ⚛️
            "consciousness": 0.4,  # 🧠
            "guardian": 0.3       # 🛡️
        }

        # Validation rules
        self._init_validation_rules()

        logger.info("🛡️ Policy Validator initialized with Constellation Framework compliance")

    def _init_validation_rules(self):
        """Initialize validation rules"""

        # Required fields for policy rules
        self.required_fields = {
            "rule_id", "name", "description", "policy_type",
            "scope", "priority", "action"
        }

        # Valid field patterns
        self.field_patterns = {
            "rule_id": r"^[a-zA-Z0-9_-]+$",
            "name": r"^.{1,100}$",
            "version": r"^\d+\.\d+\.\d+$"
        }

        # Conflict detection rules
        self.conflict_patterns = [
            # Actions that conflict
            ("ALLOW", "DENY"),
            ("APPROVE", "REJECT"),
        ]

        # Constellation Framework required tags
        self.constellation_required_tags = {
            PolicyType.ETHICAL: ["identity", "consciousness", "guardian"],
            PolicyType.SECURITY: ["guardian"],
            PolicyType.PRIVACY: ["identity", "guardian"]
        }

    def validate_policies(self, policies: list[PolicyRule]) -> ValidationResult:
        """
        Validate a collection of policy rules
        
        Args:
            policies: List of policy rules to validate
            
        Returns:
            Comprehensive validation result
        """
        start_time = datetime.now()
        validation_id = f"validation_{start_time.strftime('%Y%m%d_%H%M%S')}"

        issues = []

        try:
            # Individual policy validation
            for policy in policies:
                policy_issues = self._validate_single_policy(policy)
                issues.extend(policy_issues)

            # Cross-policy validation
            cross_issues = self._validate_policy_interactions(policies)
            issues.extend(cross_issues)

            # Performance validation
            perf_issues = self._validate_performance_impact(policies)
            issues.extend(perf_issues)

            # Constellation Framework compliance
            constellation_issues = self._validate_trinity_compliance(policies)
            issues.extend(constellation_issues)

            # Calculate summary statistics
            error_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.ERROR)
            warning_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.WARNING)
            info_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.INFO)
            suggestion_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.SUGGESTION)

            # Determine overall validation status
            is_valid = error_count == 0
            can_deploy = error_count == 0 and warning_count < 5
            compliance_score = self._calculate_compliance_score(issues, len(policies))

            validation_time = (datetime.now() - start_time).total_seconds()

            result = ValidationResult(
                validation_id=validation_id,
                policy_count=len(policies),
                issues=issues,
                error_count=error_count,
                warning_count=warning_count,
                info_count=info_count,
                suggestion_count=suggestion_count,
                validation_time=validation_time,
                validator_version=self.version,
                is_valid=is_valid,
                can_deploy=can_deploy,
                compliance_score=compliance_score
            )

            logger.info(f"Policy validation completed: {len(policies)} policies, "
                       f"{error_count} errors, {warning_count} warnings")

            return result

        except Exception as e:
            logger.error(f"Policy validation failed: {e}")

            # Return failed validation result
            return ValidationResult(
                validation_id=validation_id,
                policy_count=len(policies),
                issues=[
                    ValidationIssue(
                        issue_id="validation_error",
                        category=ValidationCategory.SYNTAX,
                        severity=ValidationSeverity.ERROR,
                        title="Validation Failed",
                        description=f"Validation process failed: {e!s}"
                    )
                ],
                error_count=1,
                validation_time=(datetime.now() - start_time).total_seconds(),
                is_valid=False,
                can_deploy=False,
                compliance_score=0.0
            )

    def _validate_single_policy(self, policy: PolicyRule) -> list[ValidationIssue]:
        """Validate a single policy rule"""

        issues = []

        # Basic structure validation
        issues.extend(self._validate_structure(policy))

        # Field validation
        issues.extend(self._validate_fields(policy))

        # Condition validation
        issues.extend(self._validate_conditions(policy))

        # Action validation
        issues.extend(self._validate_actions(policy))

        # Metadata validation
        issues.extend(self._validate_metadata(policy))

        return issues

    def _validate_structure(self, policy: PolicyRule) -> list[ValidationIssue]:
        """Validate basic policy structure"""

        issues = []

        # Check required fields
        if hasattr(policy, "__dict__"):
            policy_dict = policy.__dict__
        else:
            policy_dict = {}

        for field in self.required_fields:
            if field not in policy_dict or policy_dict[field] is None:
                issues.append(
                    ValidationIssue(
                        issue_id=f"missing_field_{field}",
                        category=ValidationCategory.SYNTAX,
                        severity=ValidationSeverity.ERROR,
                        title=f"Missing Required Field: {field}",
                        description=f"Policy is missing required field '{field}'",
                        rule_id=getattr(policy, "rule_id", "unknown"),
                        field_path=field,
                        suggestion=f"Add required field '{field}' to policy definition",
                        auto_fixable=False
                    )
                )

        return issues

    def _validate_fields(self, policy: PolicyRule) -> list[ValidationIssue]:
        """Validate individual policy fields"""

        issues = []

        # Validate field patterns
        if hasattr(policy, "__dict__"):
            policy_dict = policy.__dict__

            for field, pattern in self.field_patterns.items():
                if field in policy_dict and policy_dict[field] is not None:
                    value = str(policy_dict[field])
                    if not re.match(pattern, value):
                        issues.append(
                            ValidationIssue(
                                issue_id=f"invalid_field_{field}",
                                category=ValidationCategory.SYNTAX,
                                severity=ValidationSeverity.ERROR,
                                title=f"Invalid Field Format: {field}",
                                description=f"Field '{field}' value '{value}' does not match required pattern",
                                rule_id=getattr(policy, "rule_id", "unknown"),
                                field_path=field,
                                suggestion=f"Ensure '{field}' matches pattern: {pattern}",
                                auto_fixable=False
                            )
                        )

        # Validate enum fields
        if hasattr(policy, "policy_type") and policy.policy_type:
            if not isinstance(policy.policy_type, PolicyType):
                issues.append(
                    ValidationIssue(
                        issue_id="invalid_policy_type",
                        category=ValidationCategory.SYNTAX,
                        severity=ValidationSeverity.ERROR,
                        title="Invalid Policy Type",
                        description="Policy type must be a valid PolicyType enum value",
                        rule_id=getattr(policy, "rule_id", "unknown"),
                        field_path="policy_type"
                    )
                )

        return issues

    def _validate_conditions(self, policy: PolicyRule) -> list[ValidationIssue]:
        """Validate policy conditions"""

        issues = []

        if hasattr(policy, "conditions") and policy.conditions:
            for i, condition in enumerate(policy.conditions):
                condition_issues = self._validate_single_condition(condition, policy.rule_id, i)
                issues.extend(condition_issues)

        # Check condition complexity
        if hasattr(policy, "conditions") and len(policy.conditions) > self.max_condition_depth:
            issues.append(
                ValidationIssue(
                    issue_id="excessive_conditions",
                    category=ValidationCategory.PERFORMANCE,
                    severity=ValidationSeverity.WARNING,
                    title="Too Many Conditions",
                    description=f"Policy has {len(policy.conditions)} conditions, exceeds recommended maximum of {self.max_condition_depth}",
                    rule_id=getattr(policy, "rule_id", "unknown"),
                    suggestion="Consider breaking into multiple simpler policies"
                )
            )

        return issues

    def _validate_single_condition(self, condition: PolicyCondition, rule_id: str, index: int) -> list[ValidationIssue]:
        """Validate a single condition"""

        issues = []

        # Check required condition fields
        if not hasattr(condition, "field") or not condition.field:
            issues.append(
                ValidationIssue(
                    issue_id=f"missing_condition_field_{index}",
                    category=ValidationCategory.SYNTAX,
                    severity=ValidationSeverity.ERROR,
                    title="Missing Condition Field",
                    description=f"Condition {index} is missing required 'field' attribute",
                    rule_id=rule_id,
                    field_path=f"conditions[{index}].field"
                )
            )

        if not hasattr(condition, "operator") or not condition.operator:
            issues.append(
                ValidationIssue(
                    issue_id=f"missing_condition_operator_{index}",
                    category=ValidationCategory.SYNTAX,
                    severity=ValidationSeverity.ERROR,
                    title="Missing Condition Operator",
                    description=f"Condition {index} is missing required 'operator' attribute",
                    rule_id=rule_id,
                    field_path=f"conditions[{index}].operator"
                )
            )

        # Validate operator type
        if hasattr(condition, "operator") and condition.operator:
            if not isinstance(condition.operator, ConditionOperator):
                issues.append(
                    ValidationIssue(
                        issue_id=f"invalid_condition_operator_{index}",
                        category=ValidationCategory.SYNTAX,
                        severity=ValidationSeverity.ERROR,
                        title="Invalid Condition Operator",
                        description=f"Condition {index} operator must be a valid ConditionOperator enum value",
                        rule_id=rule_id,
                        field_path=f"conditions[{index}].operator"
                    )
                )

        # Validate regex patterns
        if (hasattr(condition, "operator") and
            condition.operator == ConditionOperator.REGEX and
            hasattr(condition, "value")):
            try:
                re.compile(condition.value)
            except re.error as e:
                issues.append(
                    ValidationIssue(
                        issue_id=f"invalid_regex_{index}",
                        category=ValidationCategory.SYNTAX,
                        severity=ValidationSeverity.ERROR,
                        title="Invalid Regular Expression",
                        description=f"Condition {index} has invalid regex pattern: {e!s}",
                        rule_id=rule_id,
                        field_path=f"conditions[{index}].value"
                    )
                )

        return issues

    def _validate_actions(self, policy: PolicyRule) -> list[ValidationIssue]:
        """Validate policy actions"""

        issues = []

        # Validate action type
        if hasattr(policy, "action") and policy.action:
            if not isinstance(policy.action, PolicyAction):
                issues.append(
                    ValidationIssue(
                        issue_id="invalid_action_type",
                        category=ValidationCategory.SYNTAX,
                        severity=ValidationSeverity.ERROR,
                        title="Invalid Action Type",
                        description="Policy action must be a valid PolicyAction enum value",
                        rule_id=getattr(policy, "rule_id", "unknown"),
                        field_path="action"
                    )
                )

        # Validate action parameters
        if hasattr(policy, "action_parameters") and policy.action_parameters:
            param_issues = self._validate_action_parameters(policy.action, policy.action_parameters, policy.rule_id)
            issues.extend(param_issues)

        return issues

    def _validate_action_parameters(self, action: PolicyAction, parameters: dict[str, Any], rule_id: str) -> list[ValidationIssue]:
        """Validate action-specific parameters"""

        issues = []

        # Action-specific validation
        if action == PolicyAction.REDIRECT:
            if "target_url" not in parameters:
                issues.append(
                    ValidationIssue(
                        issue_id="missing_redirect_target",
                        category=ValidationCategory.SEMANTIC,
                        severity=ValidationSeverity.ERROR,
                        title="Missing Redirect Target",
                        description="REDIRECT action requires 'target_url' parameter",
                        rule_id=rule_id,
                        field_path="action_parameters.target_url"
                    )
                )

        elif action == PolicyAction.MODIFY:
            if "modification_rules" not in parameters:
                issues.append(
                    ValidationIssue(
                        issue_id="missing_modification_rules",
                        category=ValidationCategory.SEMANTIC,
                        severity=ValidationSeverity.WARNING,
                        title="Missing Modification Rules",
                        description="MODIFY action should specify 'modification_rules'",
                        rule_id=rule_id,
                        field_path="action_parameters.modification_rules"
                    )
                )

        return issues

    def _validate_metadata(self, policy: PolicyRule) -> list[ValidationIssue]:
        """Validate policy metadata"""

        issues = []

        # Check version format
        if hasattr(policy, "version") and policy.version:
            if not re.match(r"^\d+\.\d+\.\d+$", policy.version):
                issues.append(
                    ValidationIssue(
                        issue_id="invalid_version_format",
                        category=ValidationCategory.SYNTAX,
                        severity=ValidationSeverity.WARNING,
                        title="Invalid Version Format",
                        description=f"Version '{policy.version}' should follow semantic versioning (x.y.z)",
                        rule_id=getattr(policy, "rule_id", "unknown"),
                        field_path="version",
                        suggestion="Use semantic versioning format (e.g., 1.0.0)"
                    )
                )

        # Check timestamps
        if hasattr(policy, "created_at") and hasattr(policy, "updated_at"):
            if policy.created_at and policy.updated_at and policy.updated_at < policy.created_at:
                issues.append(
                    ValidationIssue(
                        issue_id="invalid_timestamps",
                        category=ValidationCategory.SEMANTIC,
                        severity=ValidationSeverity.ERROR,
                        title="Invalid Timestamps",
                        description="Updated timestamp cannot be before created timestamp",
                        rule_id=getattr(policy, "rule_id", "unknown"),
                        field_path="updated_at"
                    )
                )

        return issues

    def _validate_policy_interactions(self, policies: list[PolicyRule]) -> list[ValidationIssue]:
        """Validate interactions between policies"""

        issues = []

        # Check for duplicate rule IDs
        rule_ids = [policy.rule_id for policy in policies if hasattr(policy, "rule_id")]
        duplicate_ids = set([id for id in rule_ids if rule_ids.count(id) > 1])

        for duplicate_id in duplicate_ids:
            issues.append(
                ValidationIssue(
                    issue_id=f"duplicate_rule_id_{duplicate_id}",
                    category=ValidationCategory.CONFLICT,
                    severity=ValidationSeverity.ERROR,
                    title="Duplicate Rule ID",
                    description=f"Multiple policies have the same rule_id: {duplicate_id}",
                    rule_id=duplicate_id,
                    suggestion="Ensure each policy has a unique rule_id"
                )
            )

        # Check for action conflicts
        conflicts = self._detect_action_conflicts(policies)
        issues.extend(conflicts)

        # Check dependencies
        dependency_issues = self._validate_dependencies(policies)
        issues.extend(dependency_issues)

        return issues

    def _detect_action_conflicts(self, policies: list[PolicyRule]) -> list[ValidationIssue]:
        """Detect conflicting actions between policies"""

        issues = []

        # Group policies by scope and target
        policy_groups = {}

        for policy in policies:
            if not hasattr(policy, "scope") or not hasattr(policy, "action"):
                continue

            key = (policy.scope, getattr(policy, "target_modules", ""), getattr(policy, "target_users", ""))
            if key not in policy_groups:
                policy_groups[key] = []
            policy_groups[key].append(policy)

        # Check for conflicts within each group
        for group_key, group_policies in policy_groups.items():
            if len(group_policies) < 2:
                continue

            for i, policy1 in enumerate(group_policies):
                for policy2 in group_policies[i+1:]:
                    if self._policies_conflict(policy1, policy2):
                        issues.append(
                            ValidationIssue(
                                issue_id=f"action_conflict_{policy1.rule_id}_{policy2.rule_id}",
                                category=ValidationCategory.CONFLICT,
                                severity=ValidationSeverity.WARNING,
                                title="Conflicting Policy Actions",
                                description=f"Policies {policy1.rule_id} and {policy2.rule_id} have conflicting actions",
                                affected_rules=[policy1.rule_id, policy2.rule_id],
                                suggestion="Review policies for overlapping conditions with conflicting actions"
                            )
                        )

        return issues

    def _policies_conflict(self, policy1: PolicyRule, policy2: PolicyRule) -> bool:
        """Check if two policies have conflicting actions"""

        if not hasattr(policy1, "action") or not hasattr(policy2, "action"):
            return False

        action1 = policy1.action.value if hasattr(policy1.action, "value") else str(policy1.action)
        action2 = policy2.action.value if hasattr(policy2.action, "value") else str(policy2.action)

        # Check known conflict patterns
        for conflict_pair in self.conflict_patterns:
            if (action1.upper(), action2.upper()) == conflict_pair or (action2.upper(), action1.upper()) == conflict_pair:
                return True

        return False

    def _validate_dependencies(self, policies: list[PolicyRule]) -> list[ValidationIssue]:
        """Validate policy dependencies"""

        issues = []
        rule_ids = set(policy.rule_id for policy in policies if hasattr(policy, "rule_id"))

        for policy in policies:
            if hasattr(policy, "depends_on") and policy.depends_on:
                for dependency in policy.depends_on:
                    if dependency not in rule_ids:
                        issues.append(
                            ValidationIssue(
                                issue_id=f"missing_dependency_{dependency}",
                                category=ValidationCategory.DEPENDENCY,
                                severity=ValidationSeverity.ERROR,
                                title="Missing Dependency",
                                description=f"Policy {policy.rule_id} depends on {dependency} which is not found",
                                rule_id=policy.rule_id,
                                suggestion="Either add the dependency policy or remove the dependency reference"
                            )
                        )

        return issues

    def _validate_performance_impact(self, policies: list[PolicyRule]) -> list[ValidationIssue]:
        """Validate performance impact of policies"""

        issues = []

        # Check for performance-heavy patterns
        for policy in policies:
            if hasattr(policy, "conditions") and policy.conditions:
                for i, condition in enumerate(policy.conditions):
                    if (hasattr(condition, "operator") and
                        condition.operator == ConditionOperator.REGEX and
                        hasattr(condition, "value")):

                        # Check for potentially slow regex patterns
                        pattern = condition.value
                        if self._is_slow_regex(pattern):
                            issues.append(
                                ValidationIssue(
                                    issue_id=f"slow_regex_{policy.rule_id}_{i}",
                                    category=ValidationCategory.PERFORMANCE,
                                    severity=ValidationSeverity.WARNING,
                                    title="Potentially Slow Regex",
                                    description=f"Regex pattern in condition {i} may have poor performance",
                                    rule_id=policy.rule_id,
                                    field_path=f"conditions[{i}].value",
                                    suggestion="Consider optimizing regex pattern or using simpler operators"
                                )
                            )

        return issues

    def _is_slow_regex(self, pattern: str) -> bool:
        """Check if regex pattern is potentially slow"""

        # Simple heuristics for slow patterns
        slow_patterns = [
            r"\.\*\.\*",  # Multiple .* patterns
            r"\(\.\*\)\+",  # Nested quantifiers
            r"\[\^.*\]\*",  # Character class negation with *
        ]

        for slow_pattern in slow_patterns:
            if re.search(slow_pattern, pattern):
                return True

        return False

    def _validate_trinity_compliance(self, policies: list[PolicyRule]) -> list[ValidationIssue]:
        """Validate Constellation Framework compliance"""

        issues = []

        for policy in policies:
            if not hasattr(policy, "policy_type"):
                continue

            policy_type = policy.policy_type

            # Check for required Constellation tags
            if policy_type in self.constellation_required_tags:
                required_tags = self.constellation_required_tags[policy_type]
                policy_tags = getattr(policy, "context_tags", set())

                missing_tags = set(required_tags) - policy_tags
                if missing_tags:
                    issues.append(
                        ValidationIssue(
                            issue_id=f"missing_trinity_tags_{policy.rule_id}",
                            category=ValidationCategory.CONSTELLATION,
                            severity=ValidationSeverity.WARNING,
                            title="Missing Constellation Framework Tags",
                            description=f"Policy type {policy_type.value} requires Constellation tags: {', '.join(missing_tags)}",
                            rule_id=getattr(policy, "rule_id", "unknown"),
                            suggestion=f"Add Constellation Framework tags: {', '.join(missing_tags)}"
                        )
                    )

        return issues

    def _calculate_compliance_score(self, issues: list[ValidationIssue], policy_count: int) -> float:
        """Calculate overall compliance score"""

        if policy_count == 0:
            return 1.0

        # Weight different severity levels
        error_weight = 1.0
        warning_weight = 0.5
        info_weight = 0.1
        suggestion_weight = 0.05

        total_penalty = 0.0

        for issue in issues:
            if issue.severity == ValidationSeverity.ERROR:
                total_penalty += error_weight
            elif issue.severity == ValidationSeverity.WARNING:
                total_penalty += warning_weight
            elif issue.severity == ValidationSeverity.INFO:
                total_penalty += info_weight
            elif issue.severity == ValidationSeverity.SUGGESTION:
                total_penalty += suggestion_weight

        # Calculate score (higher is better)
        max_penalty = policy_count * error_weight
        score = max(0.0, 1.0 - (total_penalty / max_penalty))

        return score

    def get_validation_summary(self, result: ValidationResult) -> str:
        """Generate human-readable validation summary"""

        summary_parts = [
            "Policy Validation Summary",
            "========================",
            f"Policies Validated: {result.policy_count}",
            f"Validation Status: {'PASSED' if result.is_valid else 'FAILED'}",
            f"Deployment Ready: {'YES' if result.can_deploy else 'NO'}",
            f"Compliance Score: {result.compliance_score:.2f}",
            "",
            "Issues Found:",
            f"  Errors: {result.error_count}",
            f"  Warnings: {result.warning_count}",
            f"  Info: {result.info_count}",
            f"  Suggestions: {result.suggestion_count}",
            "",
            f"Validation Time: {result.validation_time:.2f}s"
        ]

        if result.issues:
            summary_parts.extend([
                "",
                "Top Issues:"
            ])

            # Show top 5 most severe issues
            sorted_issues = sorted(result.issues,
                                 key=lambda x: (x.severity.value, x.category.value))

            for issue in sorted_issues[:5]:
                summary_parts.append(
                    f"  [{issue.severity.value.upper()}] {issue.title}: {issue.description[:100]}..."
                )

        return "\n".join(summary_parts)


# Export main classes
__all__ = [
    "ValidationSeverity",
    "ValidationCategory",
    "ValidationIssue",
    "ValidationResult",
    "PolicyValidator"
]

#TAG:ethics
#TAG:neuroplastic
#TAG:colony