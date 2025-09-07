"""
Policy Enforcement Engine for LUKHAS AI System

This module provides a comprehensive policy enforcement system that
integrates with Trinity Framework, Guardian System, and compliance
monitoring to ensure all system operations comply with organizational
policies, regulatory requirements, and ethical standards.

Features:
- Real-time policy enforcement and validation
- Dynamic policy rule engine with complex condition support
- Multi-layered policy hierarchy (system, user, context-specific)
- Automated policy violation detection and remediation
- Integration with Guardian System and constitutional principles
- Trinity Framework policy alignment (⚛️🧠🛡️)
- Comprehensive audit trails and policy change management
- Performance-optimized policy evaluation engine
- Context-aware policy application

#TAG:governance
#TAG:policy
#TAG:enforcement
#TAG:constellation
#TAG:guardian
#TAG:compliance
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from candidate.core.common import get_logger

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
    TRINITY = "constellation"  # Trinity Framework specific


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

    # Trinity Framework integration
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


class PolicyRuleEngine:
    """Core engine for policy rule management and evaluation"""

    def __init__(self):
        self.rules: dict[str, PolicyRule] = {}
        self.rule_dependencies: dict[str, list[str]] = {}
        self.compiled_conditions: dict[str, Callable] = {}

        # Performance optimization
        self.rule_cache: dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes

        logger.info("🔧 Policy Rule Engine initialized")

    def add_rule(self, rule: PolicyRule) -> bool:
        """Add a policy rule to the engine"""

        try:
            # Validate rule
            validation_result = self._validate_rule(rule)
            if not validation_result["valid"]:
                logger.error(f"❌ Invalid policy rule {rule.rule_id}: {validation_result['errors']}")
                return False

            # Check for conflicts
            conflicts = self._check_rule_conflicts(rule)
            if conflicts:
                logger.warning(f"⚠️ Rule conflicts detected for {rule.rule_id}: {conflicts}")

            # Compile conditions for performance
            compiled_condition = self._compile_rule_conditions(rule)
            if compiled_condition:
                self.compiled_conditions[rule.rule_id] = compiled_condition

            # Add rule
            self.rules[rule.rule_id] = rule

            # Update dependencies
            if rule.depends_on:
                self.rule_dependencies[rule.rule_id] = rule.depends_on

            # Clear cache to force recompilation
            self._clear_cache()

            logger.info(f"✅ Added policy rule: {rule.rule_id} ({rule.policy_type.value})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to add policy rule {rule.rule_id}: {e}")
            return False

    def _validate_rule(self, rule: PolicyRule) -> dict[str, Any]:
        """Validate policy rule syntax and logic"""

        errors = []
        warnings = []

        # Check required fields
        if not rule.rule_id:
            errors.append("Rule ID is required")

        if not rule.name:
            errors.append("Rule name is required")

        # Validate conditions
        for i, condition in enumerate(rule.conditions):
            if not condition.field:
                errors.append(f"Condition {i}: field is required")

            if condition.operator == ConditionOperator.REGEX:
                try:
                    re.compile(str(condition.value))
                except re.error as e:
                    errors.append(f"Condition {i}: invalid regex pattern - {e}")

        # Validate condition logic
        if rule.condition_logic not in ["AND", "OR"] and rule.conditions:
            # Check if it's a valid logical expression
            try:
                # Simple validation - could be more sophisticated
                expression = rule.condition_logic.replace("AND", "True").replace("OR", "False")
                eval(expression, {"__builtins__": {}, {})
            except:
                errors.append("Invalid condition logic expression")

        # Validate dependencies
        for dep_id in rule.depends_on:
            if dep_id not in self.rules:
                warnings.append(f"Dependent rule {dep_id} not found")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _check_rule_conflicts(self, rule: PolicyRule) -> list[str]:
        """Check for rule conflicts"""

        conflicts = []

        for existing_rule_id, existing_rule in self.rules.items():
            # Check explicit conflicts
            if rule.rule_id in existing_rule.conflicts_with:
                conflicts.append(f"Explicitly conflicts with {existing_rule_id}")

            if existing_rule_id in rule.conflicts_with:
                conflicts.append(f"Explicitly conflicts with {existing_rule_id}")

            # Check for logical conflicts (same conditions, opposite actions)
            if (
                rule.policy_type == existing_rule.policy_type
                and rule.scope == existing_rule.scope
                and self._conditions_similar(rule.conditions, existing_rule.conditions)
            ) and (
                (rule.action == PolicyAction.ALLOW and existing_rule.action == PolicyAction.DENY)
                or (rule.action == PolicyAction.DENY and existing_rule.action == PolicyAction.ALLOW)
            ):
                conflicts.append(f"Action conflict with {existing_rule_id}")

        return conflicts

    def _conditions_similar(self, conditions1: list[PolicyCondition], conditions2: list[PolicyCondition]) -> bool:
        """Check if two sets of conditions are similar"""

        if len(conditions1) != len(conditions2):
            return False

        # Simple similarity check - could be more sophisticated
        fields1 = {c.field for c in conditions1}
        fields2 = {c.field for c in conditions2}

        return fields1 == fields2

    def _compile_rule_conditions(self, rule: PolicyRule) -> Optional[Callable]:
        """Compile rule conditions for efficient evaluation"""

        if not rule.conditions:
            return None

        try:

            def compiled_evaluator(context: dict[str, Any]) -> bool:
                condition_results = []

                for condition in rule.conditions:
                    result = self._evaluate_single_condition(condition, context)
                    condition_results.append(result)

                # Apply condition logic
                if rule.condition_logic == "AND":
                    return all(condition_results)
                elif rule.condition_logic == "OR":
                    return any(condition_results)
                else:
                    # Custom logic expression
                    try:
                        # Replace condition placeholders with actual results
                        expression = rule.condition_logic
                        for i, result in enumerate(condition_results):
                            expression = expression.replace(f"C{i}", str(result))

                        # Evaluate the expression
                        return eval(expression, {"__builtins__": {}, {})
                    except:
                        logger.error(f"Failed to evaluate custom condition logic for rule {rule.rule_id}")
                        return False

            return compiled_evaluator

        except Exception as e:
            logger.error(f"Failed to compile conditions for rule {rule.rule_id}: {e}")
            return None

    def _evaluate_single_condition(self, condition: PolicyCondition, context: dict[str, Any]) -> bool:
        """Evaluate a single policy condition"""

        # Get field value from context
        field_value = self._get_field_value(context, condition.field)

        # Handle non-existent fields
        if field_value is None:
            return condition.operator in [ConditionOperator.NOT_EXISTS]

        # Handle existence checks
        if condition.operator == ConditionOperator.EXISTS:
            return field_value is not None
        elif condition.operator == ConditionOperator.NOT_EXISTS:
            return field_value is None

        # Convert to strings for string operations if needed
        if isinstance(field_value, str) and isinstance(condition.value, str) and not condition.case_sensitive:
            field_value = field_value.lower()
            condition.value = condition.value.lower()

        # Evaluate based on operator
        try:
            if condition.operator == ConditionOperator.EQUALS:
                return field_value == condition.value
            elif condition.operator == ConditionOperator.NOT_EQUALS:
                return field_value != condition.value
            elif condition.operator == ConditionOperator.CONTAINS:
                return str(condition.value) in str(field_value)
            elif condition.operator == ConditionOperator.NOT_CONTAINS:
                return str(condition.value) not in str(field_value)
            elif condition.operator == ConditionOperator.STARTS_WITH:
                return str(field_value).startswith(str(condition.value))
            elif condition.operator == ConditionOperator.ENDS_WITH:
                return str(field_value).endswith(str(condition.value))
            elif condition.operator == ConditionOperator.GREATER_THAN:
                return float(field_value) > float(condition.value)
            elif condition.operator == ConditionOperator.LESS_THAN:
                return float(field_value) < float(condition.value)
            elif condition.operator == ConditionOperator.GREATER_EQUAL:
                return float(field_value) >= float(condition.value)
            elif condition.operator == ConditionOperator.LESS_EQUAL:
                return float(field_value) <= float(condition.value)
            elif condition.operator == ConditionOperator.IN:
                return field_value in condition.value if isinstance(condition.value, (list, tuple, set)) else False
            elif condition.operator == ConditionOperator.NOT_IN:
                return field_value not in condition.value if isinstance(condition.value, (list, tuple, set)) else True
            elif condition.operator == ConditionOperator.REGEX:
                return bool(re.search(str(condition.value), str(field_value)))
            else:
                logger.warning(f"Unknown condition operator: {condition.operator}")
                return False

        except Exception as e:
            logger.error(
                f"Error evaluating condition {condition.field} {condition.operator.value} {condition.value}: {e}"
            )
            return False

    def _get_field_value(self, context: dict[str, Any], field_path: str) -> Any:
        """Get field value from context using dot notation"""

        try:
            value = context
            for part in field_path.split("."):
                if isinstance(value, dict):
                    value = value.get(part)
                elif hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return None
            return value
        except:
            return None

    def _clear_cache(self):
        """Clear policy evaluation cache"""
        self.rule_cache.clear()

    def get_applicable_rules(
        self,
        policy_type: Optional[PolicyType] = None,
        scope: Optional[PolicyScope] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> list[PolicyRule]:
        """Get rules applicable to given criteria"""

        applicable_rules = []

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            # Filter by policy type
            if policy_type and rule.policy_type != policy_type:
                continue

            # Filter by scope
            if scope and rule.scope != scope:
                continue

            # Filter by context
            if context:
                # Check target modules
                if rule.target_modules:
                    current_module = context.get("module")
                    if current_module and current_module not in rule.target_modules:
                        continue

                # Check target users
                if rule.target_users:
                    current_user = context.get("user")
                    if current_user and current_user not in rule.target_users:
                        continue

                # Check context tags
                if rule.context_tags:
                    context_tags = set(context.get("tags", []))
                    if not rule.context_tags.intersection(context_tags):
                        continue

            applicable_rules.append(rule)

        # Sort by priority
        priority_order = {
            PolicyPriority.EMERGENCY: 0,
            PolicyPriority.CRITICAL: 1,
            PolicyPriority.HIGH: 2,
            PolicyPriority.MEDIUM: 3,
            PolicyPriority.LOW: 4,
            PolicyPriority.INFORMATIONAL: 5,
        }

        applicable_rules.sort(key=l r: priority_order.get(r.priority, 999))
        return applicable_rules


class PolicyEnforcementEngine:
    """
    Main policy enforcement engine for LUKHAS AI System

    Provides comprehensive policy enforcement with real-time evaluation,
    violation detection, and automated remediation integrated with
    Trinity Framework and Guardian System.
    """

    def __init__(self):
        self.rule_engine = PolicyRuleEngine()
        self.violation_history: list[PolicyViolation] = []
        self.evaluation_history: list[PolicyEvaluationResult] = []

        # Performance metrics
        self.metrics = {
            "total_evaluations": 0,
            "total_violations": 0,
            "rules_active": 0,
            "average_evaluation_time": 0.0,
            "policy_effectiveness": {},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        # Initialize standard policies
        self._initialize_standard_policies()

        logger.info("🛡️ Policy Enforcement Engine initialized")

    def _initialize_standard_policies(self):
        """Initialize standard policy rules for LUKHAS AI"""

        # Security policies
        self.rule_engine.add_rule(
            PolicyRule(
                rule_id="sec_001_data_encryption",
                name="Data Encryption Requirement",
                description="All sensitive data must be encrypted",
                policy_type=PolicyType.SECURITY,
                scope=PolicyScope.GLOBAL,
                priority=PolicyPriority.CRITICAL,
                conditions=[
                    PolicyCondition(
                        field="data_type",
                        operator=ConditionOperator.IN,
                        value=["personal", "sensitive", "financial", "health"],
                    ),
                    PolicyCondition(field="encrypted", operator=ConditionOperator.EQUALS, value=False),
                ],
                condition_logic="AND",
                action=PolicyAction.DENY,
                action_parameters={"reason": "Data encryption required for sensitive data"},
            )
        )

        # Privacy policies
        self.rule_engine.add_rule(
            PolicyRule(
                rule_id="priv_001_consent_required",
                name="Consent Required for Personal Data",
                description="User consent required before processing personal data",
                policy_type=PolicyType.PRIVACY,
                scope=PolicyScope.GLOBAL,
                priority=PolicyPriority.HIGH,
                conditions=[
                    PolicyCondition(
                        field="data_category",
                        operator=ConditionOperator.EQUALS,
                        value="personal_data",
                    ),
                    PolicyCondition(field="user_consent", operator=ConditionOperator.NOT_EQUALS, value=True),
                ],
                condition_logic="AND",
                action=PolicyAction.DENY,
                action_parameters={
                    "reason": "User consent required for personal data processing",
                    "redirect_to": "consent_flow",
                },
            )
        )

        # Access control policies
        self.rule_engine.add_rule(
            PolicyRule(
                rule_id="access_001_tier_enforcement",
                name="Access Tier Enforcement",
                description="Enforce access tier restrictions",
                policy_type=PolicyType.ACCESS_CONTROL,
                scope=PolicyScope.GLOBAL,
                priority=PolicyPriority.HIGH,
                conditions=[
                    PolicyCondition(field="user_tier", operator=ConditionOperator.LESS_THAN, value=3),
                    PolicyCondition(
                        field="resource_tier_requirement",
                        operator=ConditionOperator.GREATER_EQUAL,
                        value=3,
                    ),
                ],
                condition_logic="AND",
                action=PolicyAction.DENY,
                action_parameters={"reason": "Insufficient access tier"},
            )
        )

        # Ethical policies
        self.rule_engine.add_rule(
            PolicyRule(
                rule_id="eth_001_harmful_content",
                name="Harmful Content Prevention",
                description="Prevent generation of harmful content",
                policy_type=PolicyType.ETHICAL,
                scope=PolicyScope.GLOBAL,
                priority=PolicyPriority.CRITICAL,
                conditions=[
                    PolicyCondition(
                        field="content_harm_score",
                        operator=ConditionOperator.GREATER_THAN,
                        value=0.7,
                    )
                ],
                action=PolicyAction.DENY,
                action_parameters={
                    "reason": "Content flagged as potentially harmful",
                    "escalate_to": "ethics_review",
                },
            )
        )

        # Constitutional AI policies
        self.rule_engine.add_rule(
            PolicyRule(
                rule_id="const_001_constitutional_compliance",
                name="Constitutional AI Compliance",
                description="Ensure compliance with constitutional principles",
                policy_type=PolicyType.CONSTITUTIONAL,
                scope=PolicyScope.GLOBAL,
                priority=PolicyPriority.CRITICAL,
                conditions=[
                    PolicyCondition(
                        field="constitutional_score",
                        operator=ConditionOperator.LESS_THAN,
                        value=0.8,
                    )
                ],
                action=PolicyAction.ESCALATE,
                action_parameters={
                    "reason": "Constitutional compliance threshold not met",
                    "review_required": True,
                },
            )
        )

        # Trinity Framework policies
        self.rule_engine.add_rule(
            PolicyRule(
                rule_id="trinity_001_drift_threshold",
                name="Trinity Drift Threshold",
                description="Monitor and control Trinity Framework drift",
                policy_type=PolicyType.TRINITY,
                scope=PolicyScope.GLOBAL,
                priority=PolicyPriority.HIGH,
                conditions=[PolicyCondition(field="drift_score", operator=ConditionOperator.GREATER_THAN, value=0.15)],
                action=PolicyAction.ESCALATE,
                action_parameters={"reason": "Drift threshold exceeded", "automatic_repair": True},
            )
        )

        logger.info(f"✅ Initialized {len(self.rule_engine.rules}} standard policy rules")

    async def evaluate_policies(
        self, context: dict[str, Any], operation: str = "general", user_id: Optional[str] = None
    ) -> PolicyEvaluationResult:
        """
        Evaluate all applicable policies for given context

        Args:
            context: Context information for policy evaluation
            operation: Type of operation being performed
            user_id: User performing the operation

        Returns:
            Policy evaluation result with actions and violations
        """
        evaluation_start = datetime.now(timezone.utc)
        evaluation_id = f"eval_{uuid.uuid4()}.hex[:8]}"

        logger.debug(f"🔍 Evaluating policies: {evaluation_id}")

        try:
            # Enhance context with additional information
            enhanced_context = await self._enhance_context(context, operation, user_id)

            # Get applicable rules
            applicable_rules = self.rule_engine.get_applicable_rules(context=enhanced_context)

            # Evaluate each rule
            triggered_rules = []
            violations = []
            warnings = []
            recommendations = []

            for rule in applicable_rules:
                rule_result = await self._evaluate_rule(rule, enhanced_context)

                if rule_result["triggered"]:
                    triggered_rules.append(rule.rule_id)

                    if rule_result["violation"]:
                        violations.append(rule_result["violation"])

                    if rule_result["warning"]:
                        warnings.append(rule_result["warning"])

                    if rule_result["recommendations"]:
                        recommendations.extend(rule_result["recommendations"])

            # Determine final action
            final_action, action_reason = await self._determine_final_action(
                triggered_rules, violations, applicable_rules
            )

            # Calculate evaluation metrics
            evaluation_time = (datetime.now(timezone.utc) - evaluation_start).total_seconds()

            # Create evaluation result
            result = PolicyEvaluationResult(
                evaluation_id=evaluation_id,
                context=enhanced_context,
                triggered_rules=triggered_rules,
                violations=violations,
                final_action=final_action,
                action_reason=action_reason,
                confidence=1.0,  # Could be calculated based on rule certainty
                evaluation_time=evaluation_time,
                rules_evaluated=len(applicable_rules),
                warnings=warnings,
                recommendations=recommendations,
            )

            # Store evaluation history
            self.evaluation_history.append(result)
            self._maintain_history_size()

            # Update metrics
            await self._update_metrics(result)

            logger.debug(
                f"✅ Policy evaluation completed: {evaluation_id} "
                f"(action: {final_action.value}, violations: {len(violations}})}"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Policy evaluation failed: {e}")

            # Return conservative result on error
            evaluation_time = (datetime.now(timezone.utc) - evaluation_start).total_seconds()
            return PolicyEvaluationResult(
                evaluation_id=f"error_{uuid.uuid4()}.hex[:8]}",
                context=context,
                final_action=PolicyAction.ESCALATE,
                action_reason=f"Policy evaluation error: {e!s}",
                confidence=0.5,
                evaluation_time=evaluation_time,
                warnings=["Policy evaluation system error"],
            )

    async def _enhance_context(self, context: dict[str, Any], operation: str, user_id: Optional[str]) -> dict[str, Any]:
        """Enhance context with additional information for policy evaluation"""

        enhanced = context.copy()
        enhanced.update(
            {
                "operation": operation,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evaluation_request": True,
            }
        )

        # Add Trinity Framework context if available
        enhanced.update(
            {
                "trinity_identity": context.get("identity_context", {}),  # ⚛️
                "trinity_consciousness": context.get("consciousness_context", {}),  # 🧠
                "trinity_guardian": context.get("guardian_context", {}),  # 🛡️
            }
        )

        # Add system context
        enhanced.update({"system_time": datetime.now(timezone.utc).isoformat(), "policy_engine_version": "1.0.0"})

        return enhanced

    async def _evaluate_rule(self, rule: PolicyRule, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a single policy rule"""

        rule_start = datetime.now(timezone.utc)

        try:
            # Check if rule is triggered
            triggered = False

            if rule.rule_id in self.rule_engine.compiled_conditions:
                # Use compiled condition
                evaluator = self.rule_engine.compiled_conditions[rule.rule_id]
                triggered = evaluator(context)
            else:
                # Fallback to manual evaluation
                if rule.conditions:
                    condition_results = []
                    for condition in rule.conditions:
                        result = self.rule_engine._evaluate_single_condition(condition, context)
                        condition_results.append(result)

                    if rule.condition_logic == "AND":
                        triggered = all(condition_results)
                    elif rule.condition_logic == "OR":
                        triggered = any(condition_results)
                else:
                    triggered = True  # Rule with no conditions always triggers

            result = {
                "triggered": triggered,
                "violation": None,
                "warning": None,
                "recommendations": [],
            }

            if triggered:
                # Update rule statistics
                rule.execution_count += 1
                rule.last_executed = datetime.now(timezone.utc)

                # Calculate execution time
                execution_time = (datetime.now(timezone.utc) - rule_start).total_seconds()
                if rule.average_execution_time == 0:
                    rule.average_execution_time = execution_time
                else:
                    rule.average_execution_time = (rule.average_execution_time + execution_time) / 2

                # Handle different actions
                if rule.action in [PolicyAction.DENY, PolicyAction.ESCALATE]:
                    # Create violation
                    violation = await self._create_violation(rule, context)
                    result["violation"] = violation
                    rule.violation_count += 1

                elif rule.action == PolicyAction.WARN:
                    result["warning"] = f"Policy warning: {rule.name}"

                # Generate recommendations based on rule
                result["recommendations"] = await self._generate_rule_recommendations(rule, context)

            return result

        except Exception as e:
            logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
            return {
                "triggered": False,
                "violation": None,
                "warning": f"Rule evaluation error: {e!s}",
                "recommendations": [],
            }

    async def _create_violation(self, rule: PolicyRule, context: dict[str, Any]) -> PolicyViolation:
        """Create a policy violation from triggered rule"""

        violation_id = f"viol_{uuid.uuid4()}.hex[:8]}"

        # Collect evidence from context
        evidence = []
        for condition in rule.conditions:
            field_value = self.rule_engine._get_field_value(context, condition.field)
            if field_value is not None:
                evidence.append(f"{condition.field}: {field_value}")

        # Trinity Framework assessment
        identity_impact = await self._assess_identity_impact(rule, context)
        consciousness_impact = await self._assess_consciousness_impact(rule, context)
        guardian_assessment = await self._assess_guardian_impact(rule, context)

        violation = PolicyViolation(
            violation_id=violation_id,
            rule_id=rule.rule_id,
            rule_name=rule.name,
            policy_type=rule.policy_type,
            severity=rule.priority,
            description=f"Policy violation: {rule.description}",
            context=context,
            evidence=evidence,
            action_taken=rule.action,
            action_details=rule.action_parameters,
            source_module=context.get("module"),
            affected_user=context.get("user_id"),
            identity_impact=identity_impact,
            consciousness_impact=consciousness_impact,
            guardian_assessment=guardian_assessment,
        )

        self.violation_history.append(violation)
        return violation

    async def _assess_identity_impact(self, rule: PolicyRule, context: dict[str, Any]) -> Optional[str]:
        """Assess impact on Identity component (⚛️)"""

        if rule.policy_type in [
            PolicyType.PRIVACY,
            PolicyType.USER_CONSENT,
            PolicyType.ACCESS_CONTROL,
        ]:
            return f"Identity system impact: {rule.policy_type.value} policy violation"

        if "user" in context or "personal_data" in context:
            return "Potential identity system implications"

        return None

    async def _assess_consciousness_impact(self, rule: PolicyRule, context: dict[str, Any]) -> Optional[str]:
        """Assess impact on Consciousness component (🧠)"""

        if rule.policy_type in [
            PolicyType.ETHICAL,
            PolicyType.SYSTEM_BEHAVIOR,
            PolicyType.CONSTITUTIONAL,
        ]:
            return f"Consciousness system impact: {rule.policy_type.value} policy violation"

        if "ai_decision" in context or "learning" in context:
            return "Potential consciousness system implications"

        return None

    async def _assess_guardian_impact(self, rule: PolicyRule, context: dict[str, Any]) -> Optional[str]:
        """Assess impact on Guardian component (🛡️)"""

        if rule.policy_type in [
            PolicyType.SECURITY,
            PolicyType.COMPLIANCE,
            PolicyType.CONSTITUTIONAL,
        ]:
            return f"Guardian system alert: {rule.policy_type.value} policy violation"

        if rule.priority in [PolicyPriority.CRITICAL, PolicyPriority.EMERGENCY]:
            return f"Guardian escalation: {rule.priority.value} priority violation"

        return "Guardian monitoring: Policy violation detected"

    async def _generate_rule_recommendations(self, rule: PolicyRule, context: dict[str, Any]) -> list[str]:
        """Generate recommendations based on triggered rule"""

        recommendations = []

        # Add action-specific recommendations
        if rule.action == PolicyAction.DENY:
            recommendations.append("Review and modify request to comply with policy")
        elif rule.action == PolicyAction.ESCALATE:
            recommendations.append("Request requires human review and approval")
        elif rule.action == PolicyAction.MODIFY:
            recommendations.append("Request can proceed with modifications")

        # Add policy-specific recommendations
        if rule.policy_type == PolicyType.PRIVACY:
            recommendations.append("Ensure proper consent is obtained")
        elif rule.policy_type == PolicyType.SECURITY:
            recommendations.append("Apply additional security measures")
        elif rule.policy_type == PolicyType.ETHICAL:
            recommendations.append("Review ethical implications")

        return recommendations

    async def _determine_final_action(
        self,
        triggered_rules: list[str],
        violations: list[PolicyViolation],
        applicable_rules: list[PolicyRule],
    ) -> tuple[PolicyAction, str]:
        """Determine the final action based on all triggered rules"""

        if not triggered_rules:
            return PolicyAction.ALLOW, "No policy violations detected"

        # Priority order for actions
        action_priority = {
            PolicyAction.DENY: 0,  # Highest priority
            PolicyAction.ESCALATE: 1,
            PolicyAction.QUARANTINE: 2,
            PolicyAction.MODIFY: 3,
            PolicyAction.REDIRECT: 4,
            PolicyAction.WARN: 5,
            PolicyAction.LOG: 6,
            PolicyAction.ALLOW: 7,  # Lowest priority
        }

        # Find the highest priority action among triggered rules
        highest_priority_action = PolicyAction.ALLOW
        highest_priority_value = 999
        action_reasons = []

        for rule_id in triggered_rules:
            rule = self.rule_engine.rules.get(rule_id)
            if rule:
                action_value = action_priority.get(rule.action, 999)
                if action_value < highest_priority_value:
                    highest_priority_value = action_value
                    highest_priority_action = rule.action

                action_reasons.append(f"{rule.name}: {rule.action.value}")

        # Check for emergency or critical violations
        critical_violations = [
            v for v in violations if v.severity in [PolicyPriority.EMERGENCY, PolicyPriority.CRITICAL]
        ]
        if critical_violations:
            highest_priority_action = PolicyAction.DENY
            action_reasons.insert(0, f"{len(critical_violations}} critical violations")

        return highest_priority_action, " | ".join(action_reasons[:3])

    async def _update_metrics(self, result: PolicyEvaluationResult):
        """Update policy enforcement metrics"""

        self.metrics["total_evaluations"] += 1
        self.metrics["total_violations"] += len(result.violations)
        self.metrics["rules_active"] = len([r for r in self.rule_engine.rules.values() if r.enabled])

        # Update average evaluation time
        current_avg = self.metrics["average_evaluation_time"]
        total_evaluations = self.metrics["total_evaluations"]
        new_avg = ((current_avg * (total_evaluations - 1)) + result.evaluation_time) / total_evaluations
        self.metrics["average_evaluation_time"] = new_avg

        # Update policy effectiveness
        for rule_id in result.triggered_rules:
            if rule_id not in self.metrics["policy_effectiveness"]:
                self.metrics["policy_effectiveness"][rule_id] = {
                    "triggers": 0,
                    "effectiveness": 0.0,
                }

            self.metrics["policy_effectiveness"][rule_id]["triggers"] += 1

            # Simple effectiveness metric based on action taken
            if result.final_action in [PolicyAction.DENY, PolicyAction.ESCALATE]:
                self.metrics["policy_effectiveness"][rule_id]["effectiveness"] += 1.0
            elif result.final_action in [PolicyAction.WARN, PolicyAction.LOG]:
                self.metrics["policy_effectiveness"][rule_id]["effectiveness"] += 0.5

        self.metrics["last_updated"] = datetime.now(timezone.utc).isoformat()

    def _maintain_history_size(self):
        """Maintain history size limits"""

        max_evaluations = 10000
        max_violations = 5000

        if len(self.evaluation_history) > max_evaluations:
            self.evaluation_history = self.evaluation_history[-max_evaluations:]

        if len(self.violation_history) > max_violations:
            self.violation_history = self.violation_history[-max_violations:]

    async def add_policy_rule(self, rule: PolicyRule) -> bool:
        """Add a new policy rule"""
        return self.rule_engine.add_rule(rule)

    async def update_policy_rule(self, rule_id: str, updates: dict[str, Any]) -> bool:
        """Update an existing policy rule"""

        if rule_id not in self.rule_engine.rules:
            return False

        try:
            rule = self.rule_engine.rules[rule_id]

            # Update allowed fields
            allowed_updates = ["enabled", "priority", "action", "action_parameters", "description"]
            for field, value in updates.items():
                if field in allowed_updates:
                    setattr(rule, field, value)

            rule.updated_at = datetime.now(timezone.utc)
            logger.info(f"✅ Updated policy rule: {rule_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update policy rule {rule_id}: {e}")
            return False

    async def disable_policy_rule(self, rule_id: str) -> bool:
        """Disable a policy rule"""
        return await self.update_policy_rule(rule_id, {"enabled": False})

    async def enable_policy_rule(self, rule_id: str) -> bool:
        """Enable a policy rule"""
        return await self.update_policy_rule(rule_id, {"enabled": True})

    async def get_policy_status(self) -> dict[str, Any]:
        """Get current policy enforcement status"""

        active_rules = [r for r in self.rule_engine.rules.values() if r.enabled]

        return {
            "total_rules": len(self.rule_engine.rules),
            "active_rules": len(active_rules),
            "rules_by_type": {
                policy_type.value: len([r for r in active_rules if r.policy_type == policy_type])
                for policy_type in PolicyType
            },
            "rules_by_priority": {
                priority.value: len([r for r in active_rules if r.priority == priority]) for priority in PolicyPriority
            },
            "recent_violations": len([v for v in self.violation_history if v.status == "open"]),
            "metrics": self.metrics,
            "last_evaluation": (
                self.evaluation_history[-1].evaluated_at.isoformat() if self.evaluation_history else None
            ),
        }

    async def export_policy_report(self, include_history: bool = True) -> dict[str, Any]:
        """Export comprehensive policy report"""

        report = {
            "report_id": f"policy_report_{uuid.uuid4()}.hex[:8]}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "policy_status": await self.get_policy_status(),
            "active_policies": [
                {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "type": rule.policy_type.value,
                    "priority": rule.priority.value,
                    "executions": rule.execution_count,
                    "violations": rule.violation_count,
                    "avg_execution_time": rule.average_execution_time,
                }
                for rule in self.rule_engine.rules.values()
                if rule.enabled
            ],
            "violation_summary": {
                "total": len(self.violation_history),
                "open": len([v for v in self.violation_history if v.status == "open"]),
                "by_severity": {
                    priority.value: len([v for v in self.violation_history if v.severity == priority])
                    for priority in PolicyPriority
                },
                "by_type": {
                    policy_type.value: len([v for v in self.violation_history if v.policy_type == policy_type])
                    for policy_type in PolicyType
                },
            },
        }

        if include_history:
            report["recent_evaluations"] = [
                {
                    "evaluation_id": eval_result.evaluation_id,
                    "timestamp": eval_result.evaluated_at.isoformat(),
                    "final_action": eval_result.final_action.value,
                    "violations_count": len(eval_result.violations),
                    "evaluation_time": eval_result.evaluation_time,
                }
                for eval_result in self.evaluation_history[-100:]  # Last 100 evaluations
            ]

            report["recent_violations"] = [
                {
                    "violation_id": violation.violation_id,
                    "rule_name": violation.rule_name,
                    "severity": violation.severity.value,
                    "status": violation.status,
                    "detected_at": violation.detected_at.isoformat(),
                }
                for violation in self.violation_history[-50:]  # Last 50 violations
            ]

        return report


# Export main classes and functions
__all__ = [
    "ConditionOperator",
    "PolicyAction",
    "PolicyCondition",
    "PolicyEnforcementEngine",
    "PolicyEvaluationResult",
    "PolicyPriority",
    "PolicyRule",
    "PolicyRuleEngine",
    "PolicyScope",
    "PolicyType",
    "PolicyViolation",
]
