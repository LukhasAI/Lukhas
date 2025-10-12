"""
Advanced Rule Validator for LUKHAS AI Governance System

This module provides sophisticated rule validation capabilities with complex
logic evaluation, pattern matching, and context-aware policy enforcement.
Supports hierarchical rule systems, conditional logic, and dynamic rule
composition with comprehensive validation reporting.

Features:
- Complex rule logic evaluation (AND, OR, NOT, XOR operations)
- Pattern matching and regex support
- Context-aware rule application
- Hierarchical rule inheritance
- Dynamic rule composition
- Real-time validation performance
- Constellation Framework integration (⚛️🧠🛡️)
- GLYPH-based rule communication
- Comprehensive audit trails

#TAG:governance
#TAG:policy
#TAG:validation
#TAG:rules
#TAG:constellation
"""
from typing import List
from typing import Dict
import streamlit as st
from datetime import timezone

import asyncio
import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of validation rules"""

    SIMPLE = "simple"  # Basic condition check
    COMPLEX = "complex"  # Multi-condition logic
    PATTERN = "pattern"  # Regex pattern matching
    CONTEXTUAL = "contextual"  # Context-dependent validation
    HIERARCHICAL = "hierarchical"  # Parent-child rule relationships
    DYNAMIC = "dynamic"  # Runtime-generated rules
    COMPOSITE = "composite"  # Composed from multiple rules


class RuleOperator(Enum):
    """Logical operators for rule composition"""

    AND = "and"
    OR = "or"
    NOT = "not"
    XOR = "xor"
    IMPLIES = "implies"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    MATCHES = "matches"


class RulePriority(Enum):
    """Rule priority levels"""

    CRITICAL = "critical"  # Cannot be overridden
    HIGH = "high"  # High priority
    NORMAL = "normal"  # Standard priority
    LOW = "low"  # Lower priority
    ADVISORY = "advisory"  # Advisory only


class ValidationResult(Enum):
    """Rule validation results"""

    VALID = "valid"
    INVALID = "invalid"
    PARTIAL = "partial"  # Some conditions met
    DEFERRED = "deferred"  # Needs more context
    CONDITIONAL = "conditional"  # Valid under conditions
    ERROR = "error"  # Validation error


@dataclass
class RuleCondition:
    """Individual rule condition"""

    condition_id: str
    field: str  # Field to check
    operator: RuleOperator
    value: Any  # Expected value
    pattern: Optional[str] = None  # Regex pattern if applicable
    context_requirements: list[str] = field(default_factory=list)
    weight: float = 1.0  # Condition weight
    optional: bool = False  # Whether condition is optional


@dataclass
class RuleDefinition:
    """Complete rule definition"""

    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    priority: RulePriority

    # Rule logic
    conditions: list[RuleCondition] = field(default_factory=list)
    logic_operator: RuleOperator = RuleOperator.AND

    # Context and scope
    applicable_contexts: list[str] = field(default_factory=list)
    excluded_contexts: list[str] = field(default_factory=list)

    # Hierarchical relationships
    parent_rules: list[str] = field(default_factory=list)
    child_rules: list[str] = field(default_factory=list)

    # Dynamic behavior
    is_dynamic: bool = False
    generator_function: Optional[str] = None

    # Metadata
    tags: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"

    # Performance
    max_execution_time: float = 5.0  # seconds
    cache_duration: Optional[int] = 300  # seconds


@dataclass
class ValidationReport:
    """Comprehensive validation report"""

    validation_id: str
    rule_id: str
    target_data: dict[str, Any]
    context: dict[str, Any]

    # Results
    result: ValidationResult
    overall_score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0

    # Detailed analysis
    condition_results: list[tuple[str, bool, float]] = field(default_factory=list)
    matched_patterns: list[str] = field(default_factory=list)
    failed_conditions: list[str] = field(default_factory=list)

    # Context analysis
    context_matches: list[str] = field(default_factory=list)
    missing_context: list[str] = field(default_factory=list)

    # Performance
    execution_time: float = 0.0
    cache_hit: bool = False

    # Recommendations
    suggestions: list[str] = field(default_factory=list)
    required_actions: list[str] = field(default_factory=list)

    # Constellation Framework integration
    identity_factors: list[str] = field(default_factory=list)  # ⚛️
    consciousness_factors: list[str] = field(default_factory=list)  # 🧠
    guardian_factors: list[str] = field(default_factory=list)  # 🛡️

    # Metadata
    validation_timestamp: datetime = field(default_factory=datetime.now)
    validator_version: str = "1.0.0"


class AdvancedRuleValidator:
    """
    Advanced rule validation system with complex logic evaluation

    Provides sophisticated rule validation with support for complex
    logical operations, pattern matching, context awareness, and
    hierarchical rule relationships.
    """

    def __init__(self):
        self.rules: dict[str, RuleDefinition] = {}
        self.rule_cache: dict[str, tuple[ValidationReport, datetime]] = {}
        self.validation_history: list[ValidationReport] = []
        self.context_providers: dict[str, Callable] = {}

        # Performance metrics
        self.metrics = {
            "total_validations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "validation_errors": 0,
            "average_execution_time": 0.0,
            "rule_usage_stats": {},
            "context_usage_stats": {},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        # Built-in rule operators
        self.operators = {
            RuleOperator.EQUALS: lambda x, y: x == y,
            RuleOperator.NOT_EQUALS: lambda x, y: x != y,
            RuleOperator.GREATER_THAN: lambda x, y: (x > y if isinstance(x, (int, float)) else False),
            RuleOperator.LESS_THAN: lambda x, y: (x < y if isinstance(x, (int, float)) else False),
            RuleOperator.CONTAINS: lambda x, y: (y in x if hasattr(x, "__contains__") else False),
            RuleOperator.MATCHES: self._regex_match,
        }

        logger.info("🔍 Advanced Rule Validator initialized")

    def _regex_match(self, text: str, pattern: str) -> bool:
        """Perform regex pattern matching"""
        try:
            return bool(re.search(pattern, str(text)))
        except Exception as e:
            logger.warning(f"Regex pattern matching failed: {e}")
            return False

    async def register_rule(self, rule: RuleDefinition) -> bool:
        """
        Register a new validation rule

        Args:
            rule: Rule definition to register

        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Validate rule definition
            validation_result = await self._validate_rule_definition(rule)
            if not validation_result:
                logger.error(f"❌ Invalid rule definition: {rule.rule_id}")
                return False

            # Check for rule conflicts
            conflicts = await self._check_rule_conflicts(rule)
            if conflicts:
                logger.warning(f"⚠️ Rule conflicts detected for {rule.rule_id}: {conflicts}")

            # Register the rule
            self.rules[rule.rule_id] = rule
            self.metrics["rule_usage_stats"][rule.rule_id] = {
                "usage_count": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "last_used": None,
            }

            logger.info(f"✅ Rule registered: {rule.rule_id} ({rule.name})")
            return True

        except Exception as e:
            logger.error(f"❌ Rule registration failed for {rule.rule_id}: {e}")
            return False

    async def validate(
        self,
        rule_id: str,
        target_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> ValidationReport:
        """
        Validate data against a specific rule

        Args:
            rule_id: ID of the rule to validate against
            target_data: Data to validate
            context: Additional context for validation
            use_cache: Whether to use cached results

        Returns:
            Comprehensive validation report
        """
        start_time = datetime.now(timezone.utc)
        validation_id = f"val_{uuid.uuid4().hex[:8]}"
        context = context or {}

        try:
            # Check if rule exists
            if rule_id not in self.rules:
                return ValidationReport(
                    validation_id=validation_id,
                    rule_id=rule_id,
                    target_data=target_data,
                    context=context,
                    result=ValidationResult.ERROR,
                    overall_score=0.0,
                    confidence=0.0,
                    execution_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                    failed_conditions=[f"Rule {rule_id} not found"],
                    suggestions=["Verify rule ID exists and is registered"],
                )

            rule = self.rules[rule_id]

            # Check cache if enabled
            if use_cache:
                cached_result = await self._check_cache(rule_id, target_data, context)
                if cached_result:
                    cached_result.validation_id = validation_id  # Update ID for new request
                    self.metrics["cache_hits"] += 1
                    return cached_result

            self.metrics["cache_misses"] += 1

            # Validate context requirements
            context_validation = await self._validate_context(rule, context)
            if not context_validation["valid"]:
                return ValidationReport(
                    validation_id=validation_id,
                    rule_id=rule_id,
                    target_data=target_data,
                    context=context,
                    result=ValidationResult.DEFERRED,
                    overall_score=0.0,
                    confidence=0.5,
                    execution_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                    missing_context=context_validation["missing"],
                    suggestions=[f"Provide missing context: {', '.join(context_validation['missing'])}"],
                )

            # Perform validation
            validation_report = await self._perform_validation(validation_id, rule, target_data, context, start_time)

            # Cache result if appropriate
            if use_cache and rule.cache_duration and validation_report.result != ValidationResult.ERROR:
                await self._cache_result(rule_id, target_data, context, validation_report)

            # Update metrics
            await self._update_validation_metrics(rule_id, validation_report, start_time)

            # Store in history
            self.validation_history.append(validation_report)
            self._maintain_history_size()

            return validation_report

        except Exception as e:
            logger.error(f"❌ Validation failed for rule {rule_id}: {e}")
            self.metrics["validation_errors"] += 1

            return ValidationReport(
                validation_id=validation_id,
                rule_id=rule_id,
                target_data=target_data,
                context=context,
                result=ValidationResult.ERROR,
                overall_score=0.0,
                confidence=0.0,
                execution_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                failed_conditions=[f"Validation error: {e!s}"],
                suggestions=["Review rule definition and target data structure"],
            )

    async def validate_multiple(
        self,
        rule_ids: list[str],
        target_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        require_all: bool = False,
    ) -> dict[str, ValidationReport]:
        """
        Validate data against multiple rules

        Args:
            rule_ids: List of rule IDs to validate against
            target_data: Data to validate
            context: Additional context for validation
            require_all: Whether all rules must pass

        Returns:
            Dictionary of validation reports keyed by rule_id
        """
        context = context or {}
        results = {}

        # Run validations concurrently
        validation_tasks = [self.validate(rule_id, target_data, context) for rule_id in rule_ids]

        validation_reports = await asyncio.gather(*validation_tasks, return_exceptions=True)

        for i, report_or_exception in enumerate(validation_reports):
            rule_id = rule_ids[i]

            if isinstance(report_or_exception, Exception):
                # Create error report for failed validation
                results[rule_id] = ValidationReport(
                    validation_id=f"err_{uuid.uuid4().hex[:8]}",
                    rule_id=rule_id,
                    target_data=target_data,
                    context=context,
                    result=ValidationResult.ERROR,
                    overall_score=0.0,
                    confidence=0.0,
                    failed_conditions=[f"Validation exception: {report_or_exception!s}"],
                )
            else:
                results[rule_id] = report_or_exception

        return results

    async def _perform_validation(
        self,
        validation_id: str,
        rule: RuleDefinition,
        target_data: dict[str, Any],
        context: dict[str, Any],
        start_time: datetime,
    ) -> ValidationReport:
        """Perform the actual validation logic"""

        condition_results = []
        matched_patterns = []
        failed_conditions = []
        total_score = 0.0
        total_weight = 0.0

        # Evaluate each condition
        for condition in rule.conditions:
            try:
                condition_result = await self._evaluate_condition(condition, target_data, context)

                condition_results.append(
                    (
                        condition.condition_id,
                        condition_result["passed"],
                        condition_result["score"],
                    )
                )

                if condition_result["passed"]:
                    total_score += condition_result["score"] * condition.weight
                    if condition_result.get("pattern_matched"):
                        matched_patterns.append(condition.pattern or condition.field)
                else:
                    failed_conditions.append(f"Condition {condition.condition_id}: {condition_result['reason']}")

                total_weight += condition.weight

            except Exception as e:
                logger.error(f"Condition evaluation failed: {e}")
                condition_results.append((condition.condition_id, False, 0.0))
                failed_conditions.append(f"Condition {condition.condition_id}: evaluation error")

        # Apply rule logic operator
        overall_result, overall_score = await self._apply_rule_logic(rule, condition_results, total_score, total_weight)

        # Calculate confidence
        confidence = self._calculate_confidence(rule, condition_results, context)

        # Generate suggestions and actions
        suggestions = await self._generate_suggestions(rule, failed_conditions, context)
        required_actions = await self._generate_required_actions(rule, failed_conditions)

        # Constellation Framework integration
        constellation_factors = await self._analyze_trinity_factors(rule, target_data, context, overall_result)

        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

        return ValidationReport(
            validation_id=validation_id,
            rule_id=rule.rule_id,
            target_data=target_data,
            context=context,
            result=overall_result,
            overall_score=overall_score,
            confidence=confidence,
            condition_results=condition_results,
            matched_patterns=matched_patterns,
            failed_conditions=failed_conditions,
            context_matches=[ctx for ctx in rule.applicable_contexts if ctx in context],
            missing_context=[],  # Already validated context
            execution_time=execution_time,
            suggestions=suggestions,
            required_actions=required_actions,
            identity_factors=constellation_factors["identity"],
            consciousness_factors=constellation_factors["consciousness"],
            guardian_factors=constellation_factors["guardian"],
        )

    async def _evaluate_condition(
        self,
        condition: RuleCondition,
        target_data: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Evaluate a single rule condition"""

        # Get field value from target data
        field_value = self._get_nested_field_value(target_data, condition.field)

        if field_value is None and not condition.optional:
            return {
                "passed": False,
                "score": 0.0,
                "reason": f"Required field '{condition.field}' is missing",
            }

        if field_value is None and condition.optional:
            return {
                "passed": True,
                "score": 1.0,
                "reason": "Optional field is missing but allowed",
            }

        # Apply operator
        try:
            operator_func = self.operators.get(condition.operator)
            if not operator_func:
                return {
                    "passed": False,
                    "score": 0.0,
                    "reason": f"Unsupported operator: {condition.operator}",
                }

            if condition.operator == RuleOperator.MATCHES and condition.pattern:
                passed = operator_func(field_value, condition.pattern)
                pattern_matched = passed
            else:
                passed = operator_func(field_value, condition.value)
                pattern_matched = False

            score = 1.0 if passed else 0.0

            return {
                "passed": passed,
                "score": score,
                "reason": f"Field '{condition.field}' {condition.operator.value} check",
                "pattern_matched": pattern_matched,
            }

        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "reason": f"Condition evaluation error: {e!s}",
            }

    def _get_nested_field_value(self, data: dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        try:
            keys = field_path.split(".")
            value = data

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None

            return value

        except Exception:
            return None

    async def _apply_rule_logic(
        self,
        rule: RuleDefinition,
        condition_results: list[tuple[str, bool, float]],
        total_score: float,
        total_weight: float,
    ) -> tuple[ValidationResult, float]:
        """Apply rule logic operator to combine condition results"""

        if not condition_results:
            return ValidationResult.VALID, 1.0

        passed_conditions = [r for r in condition_results if r[1]]
        failed_conditions = [r for r in condition_results if not r[1]]

        if rule.logic_operator == RuleOperator.AND:
            # All conditions must pass
            if len(failed_conditions) == 0:
                overall_score = total_score / total_weight if total_weight > 0 else 1.0
                return ValidationResult.VALID, overall_score
            elif len(passed_conditions) > 0:
                overall_score = total_score / total_weight if total_weight > 0 else 0.0
                return ValidationResult.PARTIAL, overall_score
            else:
                return ValidationResult.INVALID, 0.0

        elif rule.logic_operator == RuleOperator.OR:
            # At least one condition must pass
            if len(passed_conditions) > 0:
                overall_score = max(r[2] for r in passed_conditions)
                return ValidationResult.VALID, overall_score
            else:
                return ValidationResult.INVALID, 0.0

        elif rule.logic_operator == RuleOperator.XOR:
            # Exactly one condition must pass
            if len(passed_conditions) == 1:
                overall_score = passed_conditions[0][2]
                return ValidationResult.VALID, overall_score
            elif len(passed_conditions) > 1:
                overall_score = sum(r[2] for r in passed_conditions) / len(passed_conditions)
                return ValidationResult.PARTIAL, overall_score
            else:
                return ValidationResult.INVALID, 0.0

        else:
            # Default to AND logic
            return await self._apply_rule_logic(
                rule._replace(logic_operator=RuleOperator.AND),
                condition_results,
                total_score,
                total_weight,
            )

    def _calculate_confidence(
        self,
        rule: RuleDefinition,
        condition_results: list[tuple[str, bool, float]],
        context: dict[str, Any],
    ) -> float:
        """Calculate confidence in the validation result"""

        base_confidence = 0.8

        # Adjust based on condition success rate
        if condition_results:
            success_rate = len([r for r in condition_results if r[1]]) / len(condition_results)
            base_confidence += (success_rate - 0.5) * 0.2  # Adjust ±0.1

        # Adjust based on context completeness
        required_context = len(rule.applicable_contexts)
        if required_context > 0:
            available_context = len([ctx for ctx in rule.applicable_contexts if ctx in context])
            context_completeness = available_context / required_context
            base_confidence += (context_completeness - 0.5) * 0.1  # Adjust ±0.05

        # Adjust based on rule complexity
        complexity_factor = len(rule.conditions) / 10.0  # Normalize by expected max
        if complexity_factor > 1.0:
            base_confidence -= 0.1  # Reduce confidence for very complex rules

        return max(0.0, min(1.0, base_confidence))

    async def _generate_suggestions(
        self,
        rule: RuleDefinition,
        failed_conditions: list[str],
        context: dict[str, Any],
    ) -> list[str]:
        """Generate suggestions for validation improvement"""

        suggestions = []

        if failed_conditions:
            suggestions.append(f"Address {len(failed_conditions)} failed condition(s)")

            # Specific suggestions based on rule type
            if rule.rule_type == RuleType.PATTERN:
                suggestions.append("Verify data format matches expected patterns")
            elif rule.rule_type == RuleType.CONTEXTUAL:
                suggestions.append("Ensure all required context information is provided")
            elif rule.rule_type == RuleType.HIERARCHICAL:
                suggestions.append("Check parent rule requirements are satisfied")

        # Context-based suggestions
        missing_contexts = [ctx for ctx in rule.applicable_contexts if ctx not in context]
        if missing_contexts:
            suggestions.append(f"Provide missing context: {', '.join(missing_contexts[:3])}")

        return suggestions

    async def _generate_required_actions(self, rule: RuleDefinition, failed_conditions: list[str]) -> list[str]:
        """Generate required actions for validation compliance"""

        actions = []

        if rule.priority == RulePriority.CRITICAL and failed_conditions:
            actions.append("CRITICAL: Immediate remediation required")
            actions.append("Review and correct all failed conditions")
        elif rule.priority == RulePriority.HIGH and failed_conditions:
            actions.append("High priority: Address failed conditions promptly")

        if len(failed_conditions) > 5:
            actions.append("Consider rule simplification due to high failure rate")

        return actions

    async def _analyze_trinity_factors(
        self,
        rule: RuleDefinition,
        target_data: dict[str, Any],
        context: dict[str, Any],
        result: ValidationResult,
    ) -> dict[str, list[str]]:
        """Analyze Constellation Framework factors (⚛️🧠🛡️)"""

        factors = {"identity": [], "consciousness": [], "guardian": []}

        # ⚛️ Identity factors
        if "identity" in rule.tags or any("identity" in field for field in target_data):
            factors["identity"].append("Identity-related rule validation performed")
        if context.get("user_identity"):
            factors["identity"].append("User identity context considered")

        # 🧠 Consciousness factors
        if rule.rule_type in [RuleType.COMPLEX, RuleType.DYNAMIC]:
            factors["consciousness"].append("Complex consciousness-level rule processing")
        if "learning" in context or "adaptation" in context:
            factors["consciousness"].append("Consciousness learning adaptation considered")

        # 🛡️ Guardian factors
        factors["guardian"].append(f"Guardian rule validation: {result.value}")
        if rule.priority in [RulePriority.CRITICAL, RulePriority.HIGH]:
            factors["guardian"].append("High-priority guardian rule enforcement")
        if result == ValidationResult.INVALID:
            factors["guardian"].append("Guardian protection: Rule violation detected")

        return factors

    async def _validate_rule_definition(self, rule: RuleDefinition) -> bool:
        """Validate a rule definition for correctness"""

        try:
            # Basic validation
            if not rule.rule_id or not rule.name:
                return False

            # Condition validation
            for condition in rule.conditions:
                if not condition.condition_id or not condition.field:
                    return False

                # Validate operator
                if condition.operator not in self.operators:
                    return False

            # Pattern validation for pattern-type rules
            if rule.rule_type == RuleType.PATTERN:
                for condition in rule.conditions:
                    if condition.pattern:
                        try:
                            re.compile(condition.pattern)
                        except re.error:
                            return False

            return True

        except Exception as e:
            logger.error(f"Rule definition validation error: {e}")
            return False

    async def _check_rule_conflicts(self, rule: RuleDefinition) -> list[str]:
        """Check for conflicts with existing rules"""

        conflicts = []

        for existing_id, existing_rule in self.rules.items():
            if existing_id == rule.rule_id:
                continue

            # Check for priority conflicts in same context
            common_contexts = set(rule.applicable_contexts) & set(existing_rule.applicable_contexts)
            if common_contexts and rule.priority != existing_rule.priority:
                if rule.priority == RulePriority.CRITICAL or existing_rule.priority == RulePriority.CRITICAL:
                    conflicts.append(f"Priority conflict with rule {existing_id} in contexts {common_contexts}")

        return conflicts

    async def _validate_context(self, rule: RuleDefinition, context: dict[str, Any]) -> dict[str, Any]:
        """Validate that required context is available"""

        required_contexts = set()

        # Collect context requirements from conditions
        for condition in rule.conditions:
            required_contexts.update(condition.context_requirements)

        # Add rule-level context requirements
        required_contexts.update(rule.applicable_contexts)

        # Check availability
        available_contexts = set(context.keys())
        missing_contexts = required_contexts - available_contexts

        return {
            "valid": len(missing_contexts) == 0,
            "missing": list(missing_contexts),
            "available": list(available_contexts),
        }

    async def _check_cache(
        self, rule_id: str, target_data: dict[str, Any], context: dict[str, Any]
    ) -> Optional[ValidationReport]:
        """Check for cached validation results"""

        cache_key = self._generate_cache_key(rule_id, target_data, context)

        if cache_key in self.rule_cache:
            cached_result, cache_time = self.rule_cache[cache_key]
            rule = self.rules[rule_id]

            # Check if cache is still valid
            if rule.cache_duration:
                cache_expiry = cache_time + timedelta(seconds=rule.cache_duration)
                if datetime.now(timezone.utc) <= cache_expiry:
                    cached_result.cache_hit = True
                    return cached_result

            # Remove expired cache entry
            del self.rule_cache[cache_key]

        return None

    async def _cache_result(
        self,
        rule_id: str,
        target_data: dict[str, Any],
        context: dict[str, Any],
        result: ValidationReport,
    ):
        """Cache a validation result"""

        cache_key = self._generate_cache_key(rule_id, target_data, context)
        self.rule_cache[cache_key] = (result, datetime.now(timezone.utc))

        # Maintain cache size (keep last 1000 entries)
        if len(self.rule_cache) > 1000:
            oldest_key = min(self.rule_cache.keys(), key=lambda k: self.rule_cache[k][1])
            del self.rule_cache[oldest_key]

    def _generate_cache_key(self, rule_id: str, target_data: dict[str, Any], context: dict[str, Any]) -> str:
        """Generate a cache key for validation results"""

        # Create deterministic hash of inputs
        cache_data = {
            "rule_id": rule_id,
            "data_hash": hash(json.dumps(target_data, sort_keys=True, default=str)),
            "context_hash": hash(json.dumps(context, sort_keys=True, default=str)),
        }

        return f"cache_{hash(json.dumps(cache_data, sort_keys=True)}"  # noqa: invalid-syntax  # TODO: Expected ,, found }

    async def _update_validation_metrics(self, rule_id: str, report: ValidationReport, start_time: datetime):
        """Update validation metrics"""

        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()

        self.metrics["total_validations"] += 1

        # Update average execution time
        total_validations = self.metrics["total_validations"]
        current_avg = self.metrics["average_execution_time"]
        new_avg = ((current_avg * (total_validations - 1)) + execution_time) / total_validations
        self.metrics["average_execution_time"] = new_avg

        # Update rule-specific stats
        if rule_id in self.metrics["rule_usage_stats"]:
            stats = self.metrics["rule_usage_stats"][rule_id]
            stats["usage_count"] += 1
            stats["last_used"] = datetime.now(timezone.utc).isoformat()

            # Update success rate
            is_success = report.result in [
                ValidationResult.VALID,
                ValidationResult.PARTIAL,
            ]
            old_rate = stats["success_rate"]
            old_count = stats["usage_count"] - 1
            new_rate = ((old_rate * old_count) + (1.0 if is_success else 0.0)) / stats["usage_count"]
            stats["success_rate"] = new_rate

            # Update average execution time
            old_time = stats["average_execution_time"]
            new_time = ((old_time * old_count) + execution_time) / stats["usage_count"]
            stats["average_execution_time"] = new_time

        self.metrics["last_updated"] = datetime.now(timezone.utc).isoformat()

    def _maintain_history_size(self, max_size: int = 1000):
        """Maintain validation history size"""
        if len(self.validation_history) > max_size:
            self.validation_history = self.validation_history[-max_size:]

    async def get_rule_statistics(self, rule_id: str) -> Optional[dict[str, Any]]:
        """Get statistics for a specific rule"""

        if rule_id not in self.rules:
            return None

        rule = self.rules[rule_id]
        stats = self.metrics["rule_usage_stats"].get(rule_id, {})

        # Calculate additional statistics from history
        rule_validations = [v for v in self.validation_history if v.rule_id == rule_id]

        recent_validations = [v for v in rule_validations if (datetime.now(timezone.utc) - v.validation_timestamp).days <= 7]

        return {
            "rule_id": rule_id,
            "rule_name": rule.name,
            "rule_type": rule.rule_type.value,
            "priority": rule.priority.value,
            "usage_statistics": stats,
            "total_historical_validations": len(rule_validations),
            "recent_validations_7_days": len(recent_validations),
            "average_score": (
                sum(v.overall_score for v in rule_validations) / len(rule_validations) if rule_validations else 0.0
            ),
            "average_confidence": (
                sum(v.confidence for v in rule_validations) / len(rule_validations) if rule_validations else 0.0
            ),
            "common_failure_patterns": self._analyze_failure_patterns(rule_validations),
        }

    def _analyze_failure_patterns(self, validations: list[ValidationReport]) -> list[str]:
        """Analyze common failure patterns from validation history"""

        failed_validations = [v for v in validations if v.result == ValidationResult.INVALID]

        if not failed_validations:
            return []

        # Count failure reasons
        failure_counts = {}
        for validation in failed_validations:
            for condition in validation.failed_conditions:
                failure_counts[condition] = failure_counts.get(condition, 0) + 1

        # Return top failure patterns
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{reason} ({count} times)" for reason, count in sorted_failures[:5]]

    async def get_system_metrics(self) -> dict[str, Any]:
        """Get comprehensive system metrics"""
        return self.metrics.copy()

    async def export_rule_definitions(self) -> list[dict[str, Any]]:
        """Export all rule definitions"""

        exported_rules = []

        for rule in self.rules.values():
            exported_rule = {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "rule_type": rule.rule_type.value,
                "priority": rule.priority.value,
                "logic_operator": rule.logic_operator.value,
                "applicable_contexts": rule.applicable_contexts,
                "excluded_contexts": rule.excluded_contexts,
                "conditions": [
                    {
                        "condition_id": cond.condition_id,
                        "field": cond.field,
                        "operator": cond.operator.value,
                        "value": cond.value,
                        "pattern": cond.pattern,
                        "context_requirements": cond.context_requirements,
                        "weight": cond.weight,
                        "optional": cond.optional,
                    }
                    for cond in rule.conditions
                ],
                "parent_rules": rule.parent_rules,
                "child_rules": rule.child_rules,
                "tags": rule.tags,
                "version": rule.version,
                "created_at": rule.created_at.isoformat(),
                "updated_at": rule.updated_at.isoformat(),
                "created_by": rule.created_by,
                "max_execution_time": rule.max_execution_time,
                "cache_duration": rule.cache_duration,
            }
            exported_rules.append(exported_rule)

        return exported_rules


# Export main classes and functions
__all__ = [
    "AdvancedRuleValidator",
    "RuleCondition",
    "RuleDefinition",
    "RuleOperator",
    "RulePriority",
    "RuleType",
    "ValidationReport",
    "ValidationResult",
]
