"""
Grammar Engine for Universal Language
======================================

Implements the missing LUKHAS Grammar system with syntax rules,
validation, and parsing capabilities.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union

from universal_language.core import Concept, Symbol, SymbolicDomain

logger = logging.getLogger(__name__)


class SyntaxType(Enum):
    """Types of syntactic structures"""

    STATEMENT = "statement"  # Declarative statement
    QUESTION = "question"  # Interrogative
    COMMAND = "command"  # Imperative
    EXCLAMATION = "exclamation"  # Exclamatory
    CONDITIONAL = "conditional"  # If-then structure
    SEQUENCE = "sequence"  # Sequential actions
    PARALLEL = "parallel"  # Parallel actions
    RECURSIVE = "recursive"  # Self-referential


class GrammaticalRole(Enum):
    """Grammatical roles for symbols/concepts"""

    SUBJECT = "subject"  # Actor/agent
    VERB = "verb"  # Action/process
    OBJECT = "object"  # Target/patient
    MODIFIER = "modifier"  # Adjective/adverb
    CONNECTOR = "connector"  # Conjunction/preposition
    DELIMITER = "delimiter"  # Punctuation/separator
    CONTEXT = "context"  # Background/setting
    QUANTIFIER = "quantifier"  # Amount/degree


@dataclass
class SyntaxRule:
    """
    Individual syntax rule for the grammar system.

    Based on patterns from the missing LUKHAS Grammar.
    """

    rule_id: str
    name: str
    pattern: str  # Pattern using grammatical roles
    syntax_type: SyntaxType
    domains: list[SymbolicDomain]
    required_roles: list[GrammaticalRole]
    optional_roles: list[GrammaticalRole] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    priority: int = 0
    active: bool = True

    def matches_pattern(self, roles: list[GrammaticalRole]) -> bool:
        """Check if a sequence of roles matches this rule's pattern"""
        # Convert pattern to regex
        pattern_regex = self.pattern_to_regex()

        # Convert roles to string
        roles_str = " ".join(r.value for r in roles)

        # Check match
        return bool(re.match(pattern_regex, roles_str))

    def pattern_to_regex(self) -> str:
        """Convert pattern to regex for matching"""
        # Replace role placeholders with regex patterns
        regex = self.pattern
        regex = regex.replace("SUBJECT", r"(subject)")
        regex = regex.replace("VERB", r"(verb)")
        regex = regex.replace("OBJECT", r"(object)")
        regex = regex.replace("MODIFIER", r"(modifier)")
        regex = regex.replace("CONNECTOR", r"(connector)")
        regex = regex.replace("*", r".*")  # Wildcard
        regex = regex.replace("+", r".+")  # One or more
        regex = regex.replace("?", r".?")  # Optional

        return f"^{regex}$"


@dataclass
class ParsedStructure:
    """Result of parsing a sequence of symbols/concepts"""

    syntax_type: SyntaxType
    elements: list[Union[Symbol, Concept]]
    roles: list[GrammaticalRole]
    rule_applied: Optional[SyntaxRule] = None
    confidence: float = 1.0
    violations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if the parsed structure is valid"""
        return len(self.violations) == 0 and self.confidence > 0.5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "syntax_type": self.syntax_type.value,
            "elements": [e.to_dict() if hasattr(e, "to_dict") else str(e) for e in self.elements],
            "roles": [r.value for r in self.roles],
            "rule": self.rule_applied.name if self.rule_applied else None,
            "confidence": self.confidence,
            "violations": self.violations,
            "valid": self.is_valid(),
        }


class GrammarValidator:
    """
    Validates sequences against grammar rules.
    """

    def __init__(self):
        self.rules: list[SyntaxRule] = []
        self._initialize_rules()

    def _initialize_rules(self):
        """Initialize core grammar rules"""
        # Subject-Verb-Object (SVO)
        svo_rule = SyntaxRule(
            rule_id="SVO",
            name="Subject-Verb-Object",
            pattern="subject verb object",
            syntax_type=SyntaxType.STATEMENT,
            domains=[SymbolicDomain.ACTION],
            required_roles=[GrammaticalRole.SUBJECT, GrammaticalRole.VERB, GrammaticalRole.OBJECT],
            priority=100,
        )
        self.rules.append(svo_rule)

        # Subject-Verb (SV)
        sv_rule = SyntaxRule(
            rule_id="SV",
            name="Subject-Verb",
            pattern="subject verb",
            syntax_type=SyntaxType.STATEMENT,
            domains=[SymbolicDomain.ACTION, SymbolicDomain.STATE],
            required_roles=[GrammaticalRole.SUBJECT, GrammaticalRole.VERB],
            priority=90,
        )
        self.rules.append(sv_rule)

        # Question structure
        question_rule = SyntaxRule(
            rule_id="QUESTION",
            name="Question",
            pattern="verb subject object?",
            syntax_type=SyntaxType.QUESTION,
            domains=[SymbolicDomain.CONTEXT],
            required_roles=[GrammaticalRole.VERB, GrammaticalRole.SUBJECT],
            optional_roles=[GrammaticalRole.OBJECT],
            priority=80,
        )
        self.rules.append(question_rule)

        # Conditional structure
        conditional_rule = SyntaxRule(
            rule_id="CONDITIONAL",
            name="If-Then",
            pattern="connector subject verb object connector subject verb object",
            syntax_type=SyntaxType.CONDITIONAL,
            domains=[SymbolicDomain.CONTEXT, SymbolicDomain.ACTION],
            required_roles=[
                GrammaticalRole.CONNECTOR,
                GrammaticalRole.SUBJECT,
                GrammaticalRole.VERB,
            ],
            priority=70,
        )
        self.rules.append(conditional_rule)

    def add_rule(self, rule: SyntaxRule):
        """Add a new syntax rule"""
        self.rules.append(rule)
        logger.info(f"Added grammar rule: {rule.name}")

    def validate(self, elements: list[Union[Symbol, Concept]], roles: list[GrammaticalRole]) -> tuple[bool, list[str]]:
        """Validate a sequence against all rules"""
        violations = []

        # Check length match
        if len(elements) != len(roles):
            violations.append("Element count doesn't match role count")
            return False, violations

        # Sort rules by priority
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)

        # Check each active rule
        for rule in sorted_rules:
            if not rule.active:
                continue

            # Check if required roles are present
            for required_role in rule.required_roles:
                if required_role not in roles:
                    violations.append(f"Missing required role: {required_role.value}")

        # If no violations, sequence is valid
        is_valid = len(violations) == 0
        return is_valid, violations

    def find_matching_rules(self, roles: list[GrammaticalRole]) -> list[SyntaxRule]:
        """Find all rules that match a role sequence"""
        matching_rules = []

        for rule in self.rules:
            if rule.active and rule.matches_pattern(roles):
                matching_rules.append(rule)

        # Sort by priority
        return sorted(matching_rules, key=lambda r: r.priority, reverse=True)


class LanguageParser:
    """
    Parses sequences of symbols/concepts into grammatical structures.
    """

    def __init__(self):
        self.validator = GrammarValidator()
        self.role_patterns = self._initialize_role_patterns()

    def _initialize_role_patterns(self) -> dict[str, GrammaticalRole]:
        """Initialize patterns for detecting grammatical roles"""
        return {
            # Subjects (entities, actors)
            r"^(agent|actor|entity|self|user|system)": GrammaticalRole.SUBJECT,
            # Verbs (actions, processes)
            r"^(create|destroy|modify|process|think|feel|do|be|have)": GrammaticalRole.VERB,
            # Objects (targets, patients)
            r"^(target|goal|object|data|result|output)": GrammaticalRole.OBJECT,
            # Modifiers
            r"^(very|much|little|fast|slow|good|bad)": GrammaticalRole.MODIFIER,
            # Connectors
            r"^(and|or|but|if|then|when|while)": GrammaticalRole.CONNECTOR,
            # Quantifiers
            r"^(all|some|none|many|few|one|two|three)": GrammaticalRole.QUANTIFIER,
        }

    def detect_role(self, element: Union[Symbol, Concept]) -> GrammaticalRole:
        """Detect the grammatical role of an element"""
        # Get the name/meaning to check
        if isinstance(element, Symbol):
            check_text = element.name.lower()
            domain = element.domain
        elif isinstance(element, Concept):
            check_text = element.meaning.lower()
            domain = element.get_primary_domain()
        else:
            check_text = str(element).lower()
            domain = SymbolicDomain.CONTEXT

        # Check patterns
        for pattern, role in self.role_patterns.items():
            if re.match(pattern, check_text):
                return role

        # Domain-based defaults
        domain_defaults = {
            SymbolicDomain.ACTION: GrammaticalRole.VERB,
            SymbolicDomain.TASK: GrammaticalRole.VERB,
            SymbolicDomain.STATE: GrammaticalRole.MODIFIER,
            SymbolicDomain.EMOTION: GrammaticalRole.MODIFIER,
            SymbolicDomain.ETHICS: GrammaticalRole.CONTEXT,
            SymbolicDomain.CONTEXT: GrammaticalRole.CONTEXT,
        }

        return domain_defaults.get(domain, GrammaticalRole.CONTEXT)

    def parse(self, elements: list[Union[Symbol, Concept]]) -> ParsedStructure:
        """Parse a sequence of elements into a grammatical structure"""
        # Detect roles for each element
        roles = [self.detect_role(elem) for elem in elements]

        # Find matching rules
        matching_rules = self.validator.find_matching_rules(roles)

        # Validate against rules
        is_valid, violations = self.validator.validate(elements, roles)

        # Determine syntax type
        if matching_rules:
            rule = matching_rules[0]  # Use highest priority rule
            syntax_type = rule.syntax_type
            confidence = 1.0 if is_valid else 0.5
        else:
            # Default to sequence if no rule matches
            syntax_type = SyntaxType.SEQUENCE
            confidence = 0.3
            violations.append("No matching grammar rule found")

        # Create parsed structure
        parsed = ParsedStructure(
            syntax_type=syntax_type,
            elements=elements,
            roles=roles,
            rule_applied=matching_rules[0] if matching_rules else None,
            confidence=confidence,
            violations=violations,
        )

        return parsed

    def parse_with_correction(self, elements: list[Union[Symbol, Concept]]) -> ParsedStructure:
        """Parse and attempt to correct grammatical errors"""
        # Initial parse
        parsed = self.parse(elements)

        # If invalid, try to correct
        if not parsed.is_valid():
            corrected = self.attempt_correction(parsed)
            if corrected and corrected.is_valid():
                return corrected

        return parsed

    def attempt_correction(self, parsed: ParsedStructure) -> Optional[ParsedStructure]:
        """Attempt to correct grammatical errors"""
        # Common corrections
        corrections = []

        # Check for missing subject
        if GrammaticalRole.SUBJECT not in parsed.roles:
            # Insert default subject at beginning
            default_subject = Symbol(id="DEFAULT_SUBJECT", domain=SymbolicDomain.CONTEXT, name="system", value="system")
            corrected_elements = [default_subject, *parsed.elements]
            corrected_roles = [GrammaticalRole.SUBJECT, *parsed.roles]
            corrections.append((corrected_elements, corrected_roles))

        # Check for missing verb
        if GrammaticalRole.VERB not in parsed.roles:
            # Insert default verb after subject
            default_verb = Symbol(id="DEFAULT_VERB", domain=SymbolicDomain.ACTION, name="process", value="process")
            # Find subject position
            if GrammaticalRole.SUBJECT in parsed.roles:
                subject_idx = parsed.roles.index(GrammaticalRole.SUBJECT)
                corrected_elements = (
                    parsed.elements[: subject_idx + 1] + [default_verb] + parsed.elements[subject_idx + 1 :]
                )
                corrected_roles = (
                    parsed.roles[: subject_idx + 1] + [GrammaticalRole.VERB] + parsed.roles[subject_idx + 1 :]
                )
                corrections.append((corrected_elements, corrected_roles))

        # Try each correction
        for corrected_elements, corrected_roles in corrections:
            corrected_parsed = ParsedStructure(
                syntax_type=parsed.syntax_type, elements=corrected_elements, roles=corrected_roles
            )

            # Validate correction
            is_valid, violations = self.validator.validate(corrected_elements, corrected_roles)
            if is_valid:
                corrected_parsed.violations = []
                corrected_parsed.confidence = 0.7  # Lower confidence for corrections
                corrected_parsed.metadata["corrected"] = True
                return corrected_parsed

        return None


class GrammarEngine:
    """
    Main grammar engine combining validation and parsing.
    """

    def __init__(self):
        self.validator = GrammarValidator()
        self.parser = LanguageParser()
        self.custom_rules: list[SyntaxRule] = []
        logger.info("Grammar Engine initialized")

    def add_custom_rule(self, rule: SyntaxRule) -> bool:
        """Add a custom grammar rule"""
        try:
            self.custom_rules.append(rule)
            self.validator.add_rule(rule)
            self.parser.validator.add_rule(rule)
            logger.info(f"Added custom grammar rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom rule: {e}")
            return False

    def validate_sequence(self, elements: list[Union[Symbol, Concept]]) -> tuple[bool, list[str]]:
        """Validate a sequence of elements"""
        # Detect roles
        roles = [self.parser.detect_role(elem) for elem in elements]

        # Validate
        return self.validator.validate(elements, roles)

    def parse_sequence(self, elements: list[Union[Symbol, Concept]], auto_correct: bool = False) -> ParsedStructure:
        """Parse a sequence of elements"""
        if auto_correct:
            return self.parser.parse_with_correction(elements)
        else:
            return self.parser.parse(elements)

    def get_syntax_rules(self, syntax_type: Optional[SyntaxType] = None) -> list[SyntaxRule]:
        """Get all syntax rules, optionally filtered by type"""
        all_rules = self.validator.rules + self.custom_rules

        if syntax_type:
            return [r for r in all_rules if r.syntax_type == syntax_type]

        return all_rules

    def get_grammar_stats(self) -> dict[str, Any]:
        """Get statistics about the grammar system"""
        all_rules = self.validator.rules + self.custom_rules

        return {
            "total_rules": len(all_rules),
            "core_rules": len(self.validator.rules),
            "custom_rules": len(self.custom_rules),
            "syntax_types": {st.value: len([r for r in all_rules if r.syntax_type == st]) for st in SyntaxType},
            "active_rules": len([r for r in all_rules if r.active]),
            "inactive_rules": len([r for r in all_rules if not r.active]),
        }


# Singleton instance
_grammar_engine_instance = None


def get_grammar_engine() -> GrammarEngine:
    """Get or create the singleton Grammar Engine instance"""
    global _grammar_engine_instance
    if _grammar_engine_instance is None:
        _grammar_engine_instance = GrammarEngine()
    return _grammar_engine_instance
