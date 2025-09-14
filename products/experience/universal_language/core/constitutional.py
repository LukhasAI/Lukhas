"""
Constitutional Constraints Layer for Universal Language
========================================================

Implements Constitutional AI principles for safe symbol generation and usage.
Based on what Dario Amodei/Anthropic would implement.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from universal_language.core import Concept, Symbol, SymbolicDomain

logger = logging.getLogger(__name__)


class ConstitutionalPrinciple(Enum):
    """Core constitutional principles for symbol usage"""

    HELPFUL = "helpful"  # Symbols should be helpful
    HARMLESS = "harmless"  # Symbols should not cause harm
    HONEST = "honest"  # Symbols should represent truth
    PRIVACY_PRESERVING = "privacy_preserving"  # Respect user privacy
    CULTURALLY_SENSITIVE = "culturally_sensitive"  # Respect cultural differences
    UNBIASED = "unbiased"  # Avoid discriminatory meanings
    TRANSPARENT = "transparent"  # Clear about limitations
    CONSENT_BASED = "consent_based"  # Respect user consent


@dataclass
class ConstitutionalRule:
    """A specific constitutional rule for symbol validation"""

    rule_id: str
    principle: ConstitutionalPrinciple
    description: str
    validator: Callable[[Symbol], bool]
    severity: str = "warning"  # warning, error, critical
    active: bool = True

    def validate(self, symbol: Symbol) -> tuple[bool, Optional[str]]:
        """Validate a symbol against this rule"""
        try:
            if not self.active:
                return True, None

            is_valid = self.validator(symbol)
            if not is_valid:
                message = f"Symbol '{symbol.name}' violates {self.principle.value}: {self.description}"
                return False, message

            return True, None

        except Exception as e:
            logger.error(f"Rule validation error: {e}")
            return False, f"Validation error: {e!s}"


@dataclass
class ConstitutionalViolation:
    """Record of a constitutional violation"""

    violation_id: str
    symbol_id: str
    rule_id: str
    principle: ConstitutionalPrinciple
    message: str
    severity: str
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "symbol_id": self.symbol_id,
            "rule_id": self.rule_id,
            "principle": self.principle.value,
            "message": self.message,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "resolved": self.resolved,
        }


class ConstitutionalValidator:
    """
    Validates symbols against constitutional principles.

    Core of what Dario Amodei would implement for safe AI.
    """

    def __init__(self):
        self.rules: dict[str, ConstitutionalRule] = {}
        self.violations: list[ConstitutionalViolation] = []
        self.exemptions: set[str] = set()  # Symbol IDs exempt from validation
        self._initialize_core_rules()

        logger.info("Constitutional Validator initialized with core rules")

    def _initialize_core_rules(self):
        """Initialize core constitutional rules"""

        # Helpful principle rules
        self.add_rule(
            ConstitutionalRule(
                rule_id="HELPFUL_001",
                principle=ConstitutionalPrinciple.HELPFUL,
                description="Symbols must have clear, understandable meanings",
                validator=lambda s: s.name and len(s.name) > 0 and s.value is not None,
                severity="warning",  # Make this a warning, not error
            )
        )

        # Harmless principle rules
        self.add_rule(
            ConstitutionalRule(
                rule_id="HARMLESS_001",
                principle=ConstitutionalPrinciple.HARMLESS,
                description="Symbols must not contain harmful content markers",
                validator=lambda s: not self._contains_harmful_markers(s),
                severity="critical",
            )
        )

        # Honest principle rules
        self.add_rule(
            ConstitutionalRule(
                rule_id="HONEST_001",
                principle=ConstitutionalPrinciple.HONEST,
                description="Symbols must not misrepresent their domain",
                validator=lambda s: self._validates_domain_integrity(s),
            )
        )

        # Privacy principle rules
        self.add_rule(
            ConstitutionalRule(
                rule_id="PRIVACY_001",
                principle=ConstitutionalPrinciple.PRIVACY_PRESERVING,
                description="Private symbols must be properly marked",
                validator=lambda s: self._validates_privacy_marking(s),
                severity="error",
            )
        )

        # Cultural sensitivity rules
        self.add_rule(
            ConstitutionalRule(
                rule_id="CULTURAL_001",
                principle=ConstitutionalPrinciple.CULTURALLY_SENSITIVE,
                description="Symbols must respect cultural diversity",
                validator=lambda s: self._validates_cultural_sensitivity(s),
            )
        )

        # Unbiased principle rules
        self.add_rule(
            ConstitutionalRule(
                rule_id="UNBIASED_001",
                principle=ConstitutionalPrinciple.UNBIASED,
                description="Symbols must not contain discriminatory language",
                validator=lambda s: not self._contains_biased_language(s),
                severity="error",
            )
        )

    def add_rule(self, rule: ConstitutionalRule):
        """Add a constitutional rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added constitutional rule: {rule.rule_id}")

    def remove_rule(self, rule_id: str):
        """Remove a constitutional rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed constitutional rule: {rule_id}")

    def validate_symbol(self, symbol: Symbol) -> tuple[bool, list[ConstitutionalViolation]]:
        """
        Validate a symbol against all constitutional rules.

        Returns:
            (is_valid, violations) tuple
        """
        if symbol.id in self.exemptions:
            return True, []

        violations = []

        for rule in self.rules.values():
            is_valid, message = rule.validate(symbol)

            if not is_valid:
                violation = ConstitutionalViolation(
                    violation_id=self._generate_violation_id(),
                    symbol_id=symbol.id,
                    rule_id=rule.rule_id,
                    principle=rule.principle,
                    message=message or f"Violation of {rule.principle.value}",
                    severity=rule.severity,
                )
                violations.append(violation)
                self.violations.append(violation)

        # Check for critical violations
        has_critical = any(v.severity == "critical" for v in violations)

        return not has_critical, violations

    def validate_concept(self, concept: Concept) -> tuple[bool, list[ConstitutionalViolation]]:
        """Validate all symbols in a concept"""
        all_violations = []

        for symbol in concept.symbols:
            is_valid, violations = self.validate_symbol(symbol)
            all_violations.extend(violations)

        has_critical = any(v.severity == "critical" for v in all_violations)
        return not has_critical, all_violations

    def add_exemption(self, symbol_id: str, reason: str):
        """Add exemption for a symbol from validation"""
        self.exemptions.add(symbol_id)
        logger.info(f"Added exemption for symbol {symbol_id}: {reason}")

    def remove_exemption(self, symbol_id: str):
        """Remove exemption for a symbol"""
        self.exemptions.discard(symbol_id)
        logger.info(f"Removed exemption for symbol {symbol_id}")

    def get_violations_for_symbol(self, symbol_id: str) -> list[ConstitutionalViolation]:
        """Get all violations for a specific symbol"""
        return [v for v in self.violations if v.symbol_id == symbol_id and not v.resolved]

    def resolve_violation(self, violation_id: str):
        """Mark a violation as resolved"""
        for violation in self.violations:
            if violation.violation_id == violation_id:
                violation.resolved = True
                logger.info(f"Resolved violation: {violation_id}")
                break

    # Helper validation methods
    def _contains_harmful_markers(self, symbol: Symbol) -> bool:
        """Check if symbol contains harmful content markers"""
        harmful_patterns = [
            "harm",
            "danger",
            "threat",
            "attack",
            "violence",
            "hate",
            "discriminate",
            "abuse",
        ]

        name_lower = symbol.name.lower()
        return any(pattern in name_lower and "no_" not in name_lower for pattern in harmful_patterns)

    def _validates_domain_integrity(self, symbol: Symbol) -> bool:
        """Check if symbol correctly represents its domain"""
        # Emotion symbols should have emotional attributes
        if symbol.domain == SymbolicDomain.EMOTION:
            return "valence" in symbol.attributes or "arousal" in symbol.attributes

        # Bio symbols should have biological markers
        if symbol.domain == SymbolicDomain.BIO:
            return any(k in symbol.attributes for k in ["hormone", "neurotransmitter", "protein"])

        # Default validation passes
        return True

    def _validates_privacy_marking(self, symbol: Symbol) -> bool:
        """Check if private symbols are properly marked"""
        if "private" in symbol.attributes or "personal" in symbol.attributes:
            # Should have privacy level set
            return "privacy_level" in symbol.attributes
        return True

    def _validates_cultural_sensitivity(self, symbol: Symbol) -> bool:
        """Check for cultural sensitivity"""
        # This would connect to a cultural database in production
        # For now, check for obvious issues
        insensitive_terms = ["primitive", "savage", "backwards", "inferior"]
        name_lower = symbol.name.lower()

        return not any(term in name_lower for term in insensitive_terms)

    def _contains_biased_language(self, symbol: Symbol) -> bool:
        """Check for biased or discriminatory language"""
        # Simplified check - would use ML model in production
        bias_indicators = [
            "male_only",
            "female_only",
            "race_specific",
            "age_restricted",
            "ability_restricted",
        ]

        return any(indicator in symbol.attributes for indicator in bias_indicators)

    def _generate_violation_id(self) -> str:
        """Generate unique violation ID"""
        return f"VIOLATION_{int(time.time()) * 1000}"


class ConstitutionalGuardrails:
    """
    Implements guardrails for safe symbol generation.

    Prevents generation of harmful or inappropriate symbols.
    """

    def __init__(self):
        self.validator = ConstitutionalValidator()
        self.generation_constraints: dict[str, Any] = {}
        self.blocked_patterns: set[str] = set()
        self._initialize_guardrails()

    def _initialize_guardrails(self):
        """Initialize generation guardrails"""
        # Block certain patterns from generation
        self.blocked_patterns.update(
            [
                "exploit",
                "manipulate",
                "deceive",
                "bypass_security",
                "leak_private",
                "discriminate",
                "harass",
            ]
        )

        # Set generation constraints
        self.generation_constraints = {
            "max_symbol_length": 100,
            "min_symbol_length": 1,
            "max_entropy_bits": 256,
            "require_domain": True,
            "require_meaning": True,
            "allow_anonymous": False,
        }

    def can_generate(self, proposed_symbol: dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Check if a symbol can be generated safely"""
        # Check blocked patterns
        name = proposed_symbol.get("name", "").lower()
        for pattern in self.blocked_patterns:
            if pattern in name:
                return False, f"Blocked pattern detected: {pattern}"

        # Check length constraints
        if len(name) > self.generation_constraints["max_symbol_length"]:
            return False, "Symbol name too long"

        if len(name) < self.generation_constraints["min_symbol_length"]:
            return False, "Symbol name too short"

        # Check required fields
        if self.generation_constraints["require_domain"] and "domain" not in proposed_symbol:
            return False, "Domain is required"

        if self.generation_constraints["require_meaning"] and "meaning" not in proposed_symbol:
            return False, "Meaning is required"

        return True, None

    def sanitize_symbol(self, symbol: Symbol) -> Symbol:
        """Sanitize a symbol to meet constitutional requirements"""
        # Remove harmful attributes
        harmful_attrs = ["exploit", "manipulate", "harm_level"]
        for attr in harmful_attrs:
            symbol.attributes.pop(attr, None)

        # Add safety markers
        symbol.attributes["validated"] = True
        symbol.attributes["validation_time"] = time.time()

        return symbol

    def add_blocked_pattern(self, pattern: str):
        """Add a pattern to block from generation"""
        self.blocked_patterns.add(pattern.lower())
        logger.info(f"Added blocked pattern: {pattern}")

    def remove_blocked_pattern(self, pattern: str):
        """Remove a blocked pattern"""
        self.blocked_patterns.discard(pattern.lower())
        logger.info(f"Removed blocked pattern: {pattern}")


class SymbolSandbox:
    """
    Sandbox environment for testing symbols safely.

    What Anthropic would implement for safe experimentation.
    """

    def __init__(self):
        self.sandbox_symbols: dict[str, Symbol] = {}
        self.guardrails = ConstitutionalGuardrails()
        self.test_results: list[dict[str, Any]] = []
        self.is_active = False

    def enter_sandbox(self):
        """Enter sandbox mode"""
        self.is_active = True
        self.sandbox_symbols.clear()
        logger.info("Entered sandbox mode")

    def exit_sandbox(self) -> list[Symbol]:
        """Exit sandbox and return validated symbols"""
        self.is_active = False
        validated = []

        for symbol in self.sandbox_symbols.values():
            # Validate against constitutional rules
            is_valid, violations = self.guardrails.validator.validate_symbol(symbol)

            if is_valid or all(v.severity == "warning" for v in violations):
                # Sanitize and approve
                sanitized = self.guardrails.sanitize_symbol(symbol)
                validated.append(sanitized)

        logger.info(f"Exited sandbox with {len(validated)} validated symbols")
        return validated

    def test_symbol(self, symbol: Symbol) -> dict[str, Any]:
        """Test a symbol in sandbox"""
        if not self.is_active:
            raise RuntimeError("Sandbox not active")

        # Run constitutional validation
        is_valid, violations = self.guardrails.validator.validate_symbol(symbol)

        # Check generation constraints
        can_gen, gen_msg = self.guardrails.can_generate(symbol.__dict__)

        result = {
            "symbol_id": symbol.id,
            "constitutional_valid": is_valid,
            "violations": [v.to_dict() for v in violations],
            "can_generate": can_gen,
            "generation_message": gen_msg,
            "timestamp": time.time(),
        }

        self.test_results.append(result)

        if is_valid and can_gen:
            self.sandbox_symbols[symbol.id] = symbol

        return result

    def batch_test(self, symbols: list[Symbol]) -> list[dict[str, Any]]:
        """Test multiple symbols in sandbox"""
        return [self.test_symbol(s) for s in symbols]

    def get_test_report(self) -> dict[str, Any]:
        """Get comprehensive test report"""
        if not self.test_results:
            return {"message": "No tests run"}

        total = len(self.test_results)
        valid = sum(1 for r in self.test_results if r["constitutional_valid"])
        can_generate = sum(1 for r in self.test_results if r["can_generate"])

        # Count violations by principle
        principle_counts = {}
        for result in self.test_results:
            for violation in result["violations"]:
                principle = violation["principle"]
                principle_counts[principle] = principle_counts.get(principle, 0) + 1

        return {
            "total_tested": total,
            "constitutionally_valid": valid,
            "can_generate": can_generate,
            "validation_rate": valid / total if total > 0 else 0,
            "generation_rate": can_generate / total if total > 0 else 0,
            "violations_by_principle": principle_counts,
            "test_duration": time.time() - self.test_results[0]["timestamp"] if self.test_results else 0,
        }


class ConstitutionalAPI:
    """
    High-level API for constitutional symbol management.

    Combines validation, guardrails, and sandboxing.
    """

    def __init__(self):
        self.validator = ConstitutionalValidator()
        self.guardrails = ConstitutionalGuardrails()
        self.sandbox = SymbolSandbox()
        self.audit_log: list[dict[str, Any]] = []

    def create_safe_symbol(self, name: str, domain: SymbolicDomain, value: Any, **attributes) -> Optional[Symbol]:
        """
        Create a symbol with constitutional validation.

        Returns None if symbol violates critical rules.
        """
        # Create proposed symbol
        proposed = {
            "name": name,
            "domain": domain,
            "value": value,
            "meaning": attributes.get("meaning", name),
        }

        # Check if can generate
        can_gen, msg = self.guardrails.can_generate(proposed)
        if not can_gen:
            logger.warning(f"Cannot generate symbol: {msg}")
            self._log_event("generation_blocked", proposed, msg)
            return None

        # Create symbol
        symbol = Symbol(
            id=f"SAFE_{hashlib.sha256(name.encode()).hexdigest()[:8]}",
            domain=domain,
            name=name,
            value=value,
            attributes=attributes,
        )

        # Validate
        is_valid, violations = self.validator.validate_symbol(symbol)

        # Check for critical violations
        if not is_valid:
            critical = [v for v in violations if v.severity == "critical"]
            if critical:
                logger.error(f"Critical violations for symbol {name}: {critical}")
                self._log_event("validation_failed", symbol.__dict__, violations)
                return None

        # Sanitize and return
        safe_symbol = self.guardrails.sanitize_symbol(symbol)
        self._log_event("symbol_created", safe_symbol.__dict__, None)

        return safe_symbol

    def validate_batch(self, symbols: list[Symbol]) -> dict[str, Any]:
        """Validate a batch of symbols"""
        results = {"total": len(symbols), "valid": [], "invalid": [], "violations": []}

        for symbol in symbols:
            is_valid, violations = self.validator.validate_symbol(symbol)

            if is_valid:
                results["valid"].append(symbol.id)
            else:
                results["invalid"].append(symbol.id)
                results["violations"].extend([v.to_dict() for v in violations])

        results["validation_rate"] = len(results["valid"]) / len(symbols) if symbols else 0

        return results

    def experiment_safely(self, experimental_symbols: list[Symbol]) -> list[Symbol]:
        """
        Experiment with symbols in sandbox.

        Returns only safe, validated symbols.
        """
        self.sandbox.enter_sandbox()

        # Test all symbols
        self.sandbox.batch_test(experimental_symbols)

        # Get report
        report = self.sandbox.get_test_report()
        self._log_event("sandbox_experiment", report, None)

        # Exit and get validated symbols
        validated = self.sandbox.exit_sandbox()

        return validated

    def add_custom_rule(self, rule: ConstitutionalRule):
        """Add a custom constitutional rule"""
        self.validator.add_rule(rule)
        self._log_event("rule_added", {"rule_id": rule.rule_id}, None)

    def get_audit_trail(self) -> list[dict[str, Any]]:
        """Get audit trail of constitutional actions"""
        return self.audit_log.copy()

    def _log_event(self, event_type: str, data: Any, error: Any):
        """Log constitutional event"""
        self.audit_log.append(
            {
                "timestamp": time.time(),
                "event": event_type,
                "data": data,
                "error": str(error) if error else None,
            }
        )

        # Limit log size
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]


# Singleton instance
_constitutional_api_instance = None


def get_constitutional_api() -> ConstitutionalAPI:
    """Get or create singleton Constitutional API"""
    global _constitutional_api_instance
    if _constitutional_api_instance is None:
        _constitutional_api_instance = ConstitutionalAPI()
    return _constitutional_api_instance
