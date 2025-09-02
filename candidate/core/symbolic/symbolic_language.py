"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

Unified Symbolic Language Framework

Common symbolic representation language for DAST, ABAS, and NIAS
to reduce translation overhead and improve interoperability.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SymbolicDomain(Enum):
    """Core domains in the symbolic language"""

    TASK = "task"
    EMOTION = "emotion"
    ETHICS = "ethics"
    CONTEXT = "context"
    ACTION = "action"
    STATE = "state"
    CONSENT = "consent"
    RESOURCE = "resource"
    CONFLICT = "conflict"
    RECOMMENDATION = "recommendation"


class SymbolicType(Enum):
    """Types of symbolic representations"""

    ATOMIC = "atomic"  # Single, indivisible symbol
    COMPOSITE = "composite"  # Combination of multiple symbols
    TEMPORAL = "temporal"  # Time-based symbol
    RELATIONAL = "relational"  # Relationship between symbols
    CONDITIONAL = "conditional"  # Conditional/contextual symbol


@dataclass
class SymbolicAttribute:
    """Attribute that can be attached to symbols"""

    name: str
    value: Any
    confidence: float = 1.0
    source: str = "system"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Symbol:
    """
    Base symbolic representation unit.

    This is the fundamental building block of the unified symbolic language,
    used by DAST, ABAS, and NIAS for communication.
    """

    id: str
    domain: SymbolicDomain
    type: SymbolicType
    name: str
    value: Any
    attributes: dict[str, SymbolicAttribute] = field(default_factory=dict)
    relationships: list["SymbolicRelation"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def add_attribute(
        self,
        name: str,
        value: Any,
        confidence: float = 1.0,
        source: str = "system",
    ):
        """Add an attribute to the symbol"""
        self.attributes[name] = SymbolicAttribute(name, value, confidence, source)

    def get_attribute(self, name: str) -> Optional[Any]:
        """Get attribute value by name"""
        attr = self.attributes.get(name)
        return attr.value if attr else None

    def to_dict(self) -> dict[str, Any]:
        """Convert symbol to dictionary representation"""
        return {
            "id": self.id,
            "domain": self.domain.value,
            "type": self.type.value,
            "name": self.name,
            "value": self.value,
            "attributes": {
                name: {
                    "value": attr.value,
                    "confidence": attr.confidence,
                    "source": attr.source,
                    "timestamp": attr.timestamp.isoformat(),
                }
                for name, attr in self.attributes.items()
            },
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SymbolicRelation:
    """Relationship between symbols"""

    source_id: str
    target_id: str
    relation_type: str
    strength: float = 1.0
    bidirectional: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class SymbolicExpression:
    """
    Complex symbolic expression combining multiple symbols.
    Used for representing complex states, conditions, or intentions.
    """

    def __init__(self, root_symbol: Symbol):
        self.root = root_symbol
        self.symbols: dict[str, Symbol] = {root_symbol.id: root_symbol}
        self.relations: list[SymbolicRelation] = []
        self.context: dict[str, Any] = {}

    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to the expression"""
        self.symbols[symbol.id] = symbol

    def add_relation(self, relation: SymbolicRelation) -> None:
        """Add a relationship between symbols"""
        # Verify both symbols exist in the expression
        if relation.source_id in self.symbols and relation.target_id in self.symbols:
            self.relations.append(relation)
        else:
            raise ValueError(
                "Both symbols must be in the expression before adding relation"
            )

    def evaluate(self, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Evaluate the expression in a given context"""
        eval_context = self.context.copy()
        if context:
            eval_context.update(context)

        # Build evaluation result
        result = {
            "root_value": self.root.value,
            "expression_type": self.root.type.value,
            "domain": self.root.domain.value,
            "symbols": len(self.symbols),
            "relations": len(self.relations),
            "context": eval_context,
        }

        # Add computed properties based on expression type
        if self.root.type == SymbolicType.CONDITIONAL:
            result["conditions_met"] = self._evaluate_conditions(eval_context)
        elif self.root.type == SymbolicType.RELATIONAL:
            result["relation_strength"] = self._compute_relation_strength()

        return result

    def _evaluate_conditions(self, context: dict[str, Any]) -> bool:
        """Evaluate conditional expressions"""
        # Simplified condition evaluation
        conditions = self.root.get_attribute("conditions")
        if not conditions:
            return True

        # Check each condition
        return all(
            self._check_condition(condition, context) for condition in conditions
        )

    def _check_condition(
        self, condition: dict[str, Any], context: dict[str, Any]
    ) -> bool:
        """Check a single condition"""
        # Simple condition checking logic
        field = condition.get("field")
        operator = condition.get("operator", "equals")
        value = condition.get("value")

        context_value = context.get(field)

        if operator == "equals":
            return context_value == value
        elif operator == "greater_than":
            return context_value > value
        elif operator == "contains":
            return value in context_value
        else:
            return True

    def _compute_relation_strength(self) -> float:
        """Compute overall relationship strength"""
        if not self.relations:
            return 0.0

        total_strength = sum(rel.strength for rel in self.relations)
        return total_strength / len(self.relations)

    def to_dict(self) -> dict[str, Any]:
        """Convert expression to dictionary"""
        return {
            "root_id": self.root.id,
            "symbols": {sid: s.to_dict() for sid, s in self.symbols.items()},
            "relations": [
                {
                    "source": r.source_id,
                    "target": r.target_id,
                    "type": r.relation_type,
                    "strength": r.strength,
                    "bidirectional": r.bidirectional,
                    "metadata": r.metadata,
                }
                for r in self.relations
            ],
            "context": self.context,
        }


class SymbolicTranslator:
    """
    Translator between different symbolic representations.
    Enables DAST, ABAS, and NIAS to communicate using their native formats.
    """

    def __init__(self):
        self.translation_rules: dict[str, dict[str, Any]] = {}
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default translation rules"""
        # DAST task symbols to ABAS conflict symbols
        self.translation_rules["dast_to_abas"] = {
            "task_priority": {
                "high": Symbol(
                    "urgent_conflict",
                    SymbolicDomain.CONFLICT,
                    SymbolicType.ATOMIC,
                    "urgent",
                    1.0,
                ),
                "medium": Symbol(
                    "normal_conflict",
                    SymbolicDomain.CONFLICT,
                    SymbolicType.ATOMIC,
                    "normal",
                    0.5,
                ),
                "low": Symbol(
                    "defer_conflict",
                    SymbolicDomain.CONFLICT,
                    SymbolicType.ATOMIC,
                    "defer",
                    0.1,
                ),
            }
        }

        # NIAS recommendation symbols to DAST context
        self.translation_rules["nias_to_dast"] = {
            "recommendation_type": {
                "product": Symbol(
                    "shopping_task",
                    SymbolicDomain.TASK,
                    SymbolicType.ATOMIC,
                    "shopping",
                    "active",
                ),
                "content": Symbol(
                    "reading_task",
                    SymbolicDomain.TASK,
                    SymbolicType.ATOMIC,
                    "reading",
                    "active",
                ),
                "service": Symbol(
                    "service_task",
                    SymbolicDomain.TASK,
                    SymbolicType.ATOMIC,
                    "service",
                    "active",
                ),
            }
        }

        # ABAS decisions to NIAS filters
        self.translation_rules["abas_to_nias"] = {
            "decision": {
                "allow": Symbol(
                    "filter_pass",
                    SymbolicDomain.ACTION,
                    SymbolicType.ATOMIC,
                    "pass",
                    True,
                ),
                "block": Symbol(
                    "filter_block",
                    SymbolicDomain.ACTION,
                    SymbolicType.ATOMIC,
                    "block",
                    False,
                ),
                "defer": Symbol(
                    "filter_defer",
                    SymbolicDomain.ACTION,
                    SymbolicType.TEMPORAL,
                    "defer",
                    "later",
                ),
            }
        }

    def translate(
        self, symbol: Symbol, source_system: str, target_system: str
    ) -> Symbol:
        """Translate a symbol from one system format to another"""
        rule_key = f"{source_system}_to_{target_system}"

        if rule_key not in self.translation_rules:
            # No translation needed or direct pass-through
            return symbol

        rules = self.translation_rules[rule_key]

        # Check if we have a specific translation rule
        for mappings in rules.values():
            if symbol.name in mappings:
                translated = mappings[symbol.name]
                # Preserve original attributes
                translated.attributes.update(symbol.attributes)
                translated.metadata["original_system"] = source_system
                translated.metadata["original_symbol_id"] = symbol.id
                return translated

        # Default translation - change domain if needed
        translated = Symbol(
            id=f"{target_system}_{symbol.id}",
            domain=symbol.domain,
            type=symbol.type,
            name=symbol.name,
            value=symbol.value,
            attributes=symbol.attributes.copy(),
            metadata=symbol.metadata.copy(),
        )
        translated.metadata["translated_from"] = source_system

        return translated

    def batch_translate(
        self, symbols: list[Symbol], source_system: str, target_system: str
    ) -> list[Symbol]:
        """Translate multiple symbols at once"""
        return [self.translate(s, source_system, target_system) for s in symbols]


class SymbolicLanguageFramework:
    """
    Main framework for symbolic language operations.
    Provides pattern registration, decision encoding, and trace generation.
    """

    def __init__(self):
        self.translator = SymbolicTranslator()
        self.vocabulary = SymbolicVocabulary()
        self.registered_patterns: dict[str, dict[str, Any]] = {}
        self.decision_traces: dict[str, list[Symbol]] = {}
        logger.info("SymbolicLanguageFramework initialized")

    async def register_patterns(
        self, component_name: str, patterns: dict[str, Any]
    ) -> None:
        """Register symbolic patterns for a component"""
        self.registered_patterns[component_name] = patterns
        logger.info(f"Registered {len(patterns)} patterns for {component_name}")

        # Create symbols for each pattern
        for pattern_name, pattern_data in patterns.items():
            symbol = Symbol(
                id=f"{component_name}_{pattern_name}",
                domain=SymbolicDomain.CONTEXT,
                type=SymbolicType.COMPOSITE,
                name=pattern_name,
                value=pattern_data,
                metadata={"component": component_name},
            )
            self.vocabulary.add_symbol(symbol)

    async def encode_decision_flow(self, context: Any, outcome: Any) -> str:
        """
        Generate symbolic representation of decision flow.
        Used for audit trail generation and traceability.
        """
        # Create decision symbol
        decision_symbol = Symbol(
            id=f"decision_{context.decision_id}",
            domain=SymbolicDomain.ACTION,
            type=SymbolicType.TEMPORAL,
            name="decision_flow",
            value={
                "decision_type": str(context.decision_type),
                "timestamp": str(context.timestamp),
                "stakeholders": [str(s) for s in context.stakeholders],
            },
        )

        # Add outcome attributes
        decision_symbol.add_attribute("outcome", str(outcome.decision_made))
        decision_symbol.add_attribute("confidence", outcome.confidence_score)
        decision_symbol.add_attribute("reasoning", outcome.reasoning_chain)

        # Create expression for the decision flow
        expression = SymbolicExpression(decision_symbol)

        # Add context symbols
        for constraint in context.constraints:
            constraint_symbol = Symbol(
                id=f"constraint_{constraint}",
                domain=SymbolicDomain.ETHICS,
                type=SymbolicType.ATOMIC,
                name="constraint",
                value=constraint,
            )
            expression.add_symbol(constraint_symbol)
            expression.add_relation(
                SymbolicRelation(
                    decision_symbol.id, constraint_symbol.id, "constrained_by"
                )
            )

        # Store trace
        if context.decision_id not in self.decision_traces:
            self.decision_traces[context.decision_id] = []
        self.decision_traces[context.decision_id].append(decision_symbol)

        # Return symbolic trace as JSON string
        return json.dumps(expression.to_dict(), default=str)

    def get_patterns(self, component_name: str) -> Optional[dict[str, Any]]:
        """Get registered patterns for a component"""
        return self.registered_patterns.get(component_name)

    def get_decision_trace(self, decision_id: str) -> list[Symbol]:
        """Get symbolic trace for a decision"""
        return self.decision_traces.get(decision_id, [])


class SymbolicVocabulary:
    """
    Shared vocabulary of common symbols used across DAST, ABAS, and NIAS.
    Ensures consistent interpretation of core concepts.
    """

    def __init__(self):
        self.vocabulary: dict[str, Symbol] = {}
        self._initialize_core_vocabulary()

    def _initialize_core_vocabulary(self):
        """Initialize core shared symbols"""
        # Task-related symbols
        self.vocabulary["task_active"] = Symbol(
            "task_active",
            SymbolicDomain.TASK,
            SymbolicType.ATOMIC,
            "active_task",
            True,
        )
        self.vocabulary["task_completed"] = Symbol(
            "task_completed",
            SymbolicDomain.TASK,
            SymbolicType.ATOMIC,
            "completed_task",
            True,
        )
        self.vocabulary["task_blocked"] = Symbol(
            "task_blocked",
            SymbolicDomain.TASK,
            SymbolicType.ATOMIC,
            "blocked_task",
            False,
        )

        # Emotion-related symbols
        self.vocabulary["emotion_positive"] = Symbol(
            "emotion_positive",
            SymbolicDomain.EMOTION,
            SymbolicType.ATOMIC,
            "positive",
            1.0,
        )
        self.vocabulary["emotion_negative"] = Symbol(
            "emotion_negative",
            SymbolicDomain.EMOTION,
            SymbolicType.ATOMIC,
            "negative",
            -1.0,
        )
        self.vocabulary["emotion_neutral"] = Symbol(
            "emotion_neutral",
            SymbolicDomain.EMOTION,
            SymbolicType.ATOMIC,
            "neutral",
            0.0,
        )

        # Ethics-related symbols
        self.vocabulary["ethics_approved"] = Symbol(
            "ethics_approved",
            SymbolicDomain.ETHICS,
            SymbolicType.ATOMIC,
            "approved",
            True,
        )
        self.vocabulary["ethics_violation"] = Symbol(
            "ethics_violation",
            SymbolicDomain.ETHICS,
            SymbolicType.ATOMIC,
            "violation",
            False,
        )
        self.vocabulary["ethics_review"] = Symbol(
            "ethics_review",
            SymbolicDomain.ETHICS,
            SymbolicType.ATOMIC,
            "review_required",
            None,
        )

        # Action symbols
        self.vocabulary["action_allow"] = Symbol(
            "action_allow",
            SymbolicDomain.ACTION,
            SymbolicType.ATOMIC,
            "allow",
            True,
        )
        self.vocabulary["action_block"] = Symbol(
            "action_block",
            SymbolicDomain.ACTION,
            SymbolicType.ATOMIC,
            "block",
            False,
        )
        self.vocabulary["action_defer"] = Symbol(
            "action_defer",
            SymbolicDomain.ACTION,
            SymbolicType.TEMPORAL,
            "defer",
            "pending",
        )

        # Context symbols
        self.vocabulary["context_focus"] = Symbol(
            "context_focus",
            SymbolicDomain.CONTEXT,
            SymbolicType.ATOMIC,
            "focus_mode",
            True,
        )
        self.vocabulary["context_rest"] = Symbol(
            "context_rest",
            SymbolicDomain.CONTEXT,
            SymbolicType.ATOMIC,
            "rest_mode",
            True,
        )
        self.vocabulary["context_emergency"] = Symbol(
            "context_emergency",
            SymbolicDomain.CONTEXT,
            SymbolicType.ATOMIC,
            "emergency",
            True,
        )

    def get_symbol(self, name: str) -> Optional[Symbol]:
        """Get a symbol from the vocabulary"""
        return self.vocabulary.get(name)

    def add_symbol(self, symbol: Symbol) -> None:
        """Add a new symbol to the vocabulary"""
        self.vocabulary[symbol.name] = symbol

    def get_symbols_by_domain(self, domain: SymbolicDomain) -> list[Symbol]:
        """Get all symbols in a specific domain"""
        return [s for s in self.vocabulary.values() if s.domain == domain]


# Global instances
_translator = None
_vocabulary = None


def get_symbolic_translator() -> SymbolicTranslator:
    """Get or create symbolic translator instance"""
    global _translator
    if _translator is None:
        _translator = SymbolicTranslator()
    return _translator


def get_symbolic_vocabulary() -> SymbolicVocabulary:
    """Get or create symbolic vocabulary instance"""
    global _vocabulary
    if _vocabulary is None:
        _vocabulary = SymbolicVocabulary()
    return _vocabulary


__all__ = [
    "Symbol",
    "SymbolicAttribute",
    "SymbolicDomain",
    "SymbolicExpression",
    "SymbolicRelation",
    "SymbolicTranslator",
    "SymbolicType",
    "SymbolicVocabulary",
    "get_symbolic_translator",
    "get_symbolic_vocabulary",
]
