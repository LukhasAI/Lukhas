"""
Universal Language Core
=======================

Central unified language system that provides the foundation for all
symbolic communication in LUKHAS PWM.
"""

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


class SymbolicDomain(Enum):
    """Core domains in the universal language"""
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
    DREAM = "dream"
    BIO = "bio"
    IDENTITY = "identity"
    VISION = "vision"
    VOICE = "voice"
    CONSCIOUSNESS = "consciousness"
    QUANTUM = "quantum"
    MEMORY = "memory"


class ConceptType(Enum):
    """Types of universal concepts"""
    ATOMIC = "atomic"  # Single, indivisible concept
    COMPOSITE = "composite"  # Combination of multiple concepts
    TEMPORAL = "temporal"  # Time-based concept
    RELATIONAL = "relational"  # Relationship between concepts
    CONDITIONAL = "conditional"  # Conditional/contextual concept
    ABSTRACT = "abstract"  # Abstract/philosophical concept
    CONCRETE = "concrete"  # Physical/tangible concept
    PROCESS = "process"  # Process or transformation
    EMERGENT = "emergent"  # Emergent from other concepts


@dataclass
class Symbol:
    """
    Universal symbol representation.
    
    Unified from /core/symbolic/symbolic_language.py and
    /symbolic/multi_modal_language.py
    """
    id: str
    domain: SymbolicDomain
    name: str
    value: Any
    glyph: Optional[str] = None  # Visual representation (emoji, unicode)
    embedding: Optional[np.ndarray] = None
    entropy_bits: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    relationships: List[str] = field(default_factory=list)  # Symbol IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    confidence: float = 1.0
    
    def __post_init__(self):
        if not self.id:
            self.id = self.generate_id()
        if self.entropy_bits == 0.0:
            self.entropy_bits = self.calculate_entropy()
    
    def generate_id(self) -> str:
        """Generate unique symbol ID"""
        unique_str = f"{self.domain.value}:{self.name}:{time.time()}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:16]
    
    def calculate_entropy(self) -> float:
        """Calculate entropy bits for the symbol"""
        # Base entropy from domain and name
        base_entropy = len(self.name) * 4.0  # Approximate bits per character
        
        # Add entropy from relationships
        relationship_entropy = len(self.relationships) * 8.0
        
        # Add entropy from attributes (safe JSON serialization)
        try:
            # Only serialize JSON-safe attributes
            safe_attrs = {}
            for k, v in self.attributes.items():
                if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                    safe_attrs[k] = v
                else:
                    safe_attrs[k] = str(v)  # Convert to string for non-JSON types
            attr_entropy = len(json.dumps(safe_attrs)) * 2.0
        except (TypeError, ValueError):
            attr_entropy = len(str(self.attributes)) * 1.5
        
        return base_entropy + relationship_entropy + attr_entropy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "domain": self.domain.value,
            "name": self.name,
            "value": self.value,
            "glyph": self.glyph,
            "entropy_bits": self.entropy_bits,
            "attributes": self.attributes,
            "relationships": self.relationships,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "confidence": self.confidence
        }


@dataclass
class Concept:
    """
    Universal concept - higher level abstraction built from symbols.
    
    Based on Universal Language spec and UniversalConcept from
    /symbolic/multi_modal_language.py
    """
    concept_id: str
    concept_type: ConceptType
    meaning: str
    symbols: List[Symbol]
    embedding: Optional[np.ndarray] = None
    entropy_total: float = 0.0
    cultural_validations: Dict[str, float] = field(default_factory=dict)
    creation_time: float = field(default_factory=time.time)
    usage_count: int = 0
    parent_concepts: List[str] = field(default_factory=list)
    child_concepts: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.concept_id:
            self.concept_id = self.generate_concept_id()
        if self.entropy_total == 0.0:
            self.entropy_total = sum(s.entropy_bits for s in self.symbols)
    
    def generate_concept_id(self) -> str:
        """Generate Universal Concept Layer (UCL) ID"""
        # Format: DOMAIN.CONCEPT_NAME
        if self.symbols:
            primary_domain = self.symbols[0].domain.value.upper()
            concept_name = self.meaning.upper().replace(" ", "_")
            return f"{primary_domain}.{concept_name}"
        return f"UNIVERSAL.{uuid.uuid4().hex[:8].upper()}"
    
    def add_symbol(self, symbol: Symbol):
        """Add a symbol to this concept"""
        self.symbols.append(symbol)
        self.entropy_total += symbol.entropy_bits
        symbol.usage_count += 1
    
    def get_primary_domain(self) -> SymbolicDomain:
        """Get the primary domain of this concept"""
        if self.symbols:
            # Return most common domain
            domains = [s.domain for s in self.symbols]
            return max(set(domains), key=domains.count)
        return SymbolicDomain.CONTEXT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "concept_id": self.concept_id,
            "concept_type": self.concept_type.value,
            "meaning": self.meaning,
            "symbols": [s.to_dict() for s in self.symbols],
            "entropy_total": self.entropy_total,
            "cultural_validations": self.cultural_validations,
            "creation_time": self.creation_time,
            "usage_count": self.usage_count,
            "parent_concepts": self.parent_concepts,
            "child_concepts": self.child_concepts
        }


@dataclass
class Grammar:
    """
    Grammar rules for the universal language.
    
    Based on missing LUKHAS Grammar system.
    """
    rule_id: str
    name: str
    pattern: str  # Regular expression or pattern
    domain: SymbolicDomain
    priority: int = 0
    constraints: List[str] = field(default_factory=list)
    transformations: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    active: bool = True
    
    def validate(self, symbols: List[Symbol]) -> bool:
        """Validate symbols against this grammar rule"""
        # TODO: Implement pattern matching
        return True
    
    def apply_transformations(self, symbols: List[Symbol]) -> List[Symbol]:
        """Apply transformations defined by this rule"""
        # TODO: Implement transformations
        return symbols


@dataclass
class Vocabulary:
    """
    Domain-specific vocabulary collection.
    
    Consolidates vocabularies from /symbolic/vocabularies/ and
    /core/symbolic/ vocabularies.
    """
    domain: SymbolicDomain
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    concepts: Dict[str, Concept] = field(default_factory=dict)
    grammar_rules: List[Grammar] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_symbol(self, symbol: Symbol):
        """Add symbol to vocabulary"""
        self.symbols[symbol.id] = symbol
        logger.debug(f"Added symbol {symbol.name} to {self.domain.value} vocabulary")
    
    def add_concept(self, concept: Concept):
        """Add concept to vocabulary"""
        self.concepts[concept.concept_id] = concept
        logger.debug(f"Added concept {concept.meaning} to {self.domain.value} vocabulary")
    
    def find_symbol(self, name: str) -> Optional[Symbol]:
        """Find symbol by name"""
        for symbol in self.symbols.values():
            if symbol.name == name:
                return symbol
        return None
    
    def find_concept(self, meaning: str) -> Optional[Concept]:
        """Find concept by meaning"""
        for concept in self.concepts.values():
            if concept.meaning == meaning:
                return concept
        return None


class UniversalLanguageCore:
    """
    Core universal language system.
    
    This is the main entry point for all language operations.
    """
    
    def __init__(self):
        self.vocabularies: Dict[SymbolicDomain, Vocabulary] = {}
        self.global_symbols: Dict[str, Symbol] = {}
        self.global_concepts: Dict[str, Concept] = {}
        self.grammar_rules: List[Grammar] = []
        self.initialized = False
        
        # Initialize vocabularies for each domain
        self._initialize_vocabularies()
        
        # Load core symbols and concepts
        self._load_core_language()
        
        self.initialized = True
        logger.info("Universal Language Core initialized")
    
    def _initialize_vocabularies(self):
        """Initialize vocabulary for each domain"""
        for domain in SymbolicDomain:
            self.vocabularies[domain] = Vocabulary(domain=domain)
            logger.debug(f"Initialized vocabulary for domain: {domain.value}")
    
    def _load_core_language(self):
        """Load core symbols, concepts, and grammar rules"""
        # This would load from configuration or database
        # For now, create some essential symbols
        self._create_core_symbols()
        self._create_core_concepts()
        self._create_core_grammar()
    
    def _create_core_symbols(self):
        """Create essential core symbols"""
        # Emotion symbols
        happiness = Symbol(
            id="EMOTION_HAPPINESS",
            domain=SymbolicDomain.EMOTION,
            name="happiness",
            value=1.0,
            glyph="😊",
            entropy_bits=32.0
        )
        self.register_symbol(happiness)
        
        sadness = Symbol(
            id="EMOTION_SADNESS",
            domain=SymbolicDomain.EMOTION,
            name="sadness",
            value=-1.0,
            glyph="😢",
            entropy_bits=32.0
        )
        self.register_symbol(sadness)
        
        # Action symbols
        create = Symbol(
            id="ACTION_CREATE",
            domain=SymbolicDomain.ACTION,
            name="create",
            value="create",
            glyph="✨",
            entropy_bits=24.0
        )
        self.register_symbol(create)
        
        # State symbols
        active = Symbol(
            id="STATE_ACTIVE",
            domain=SymbolicDomain.STATE,
            name="active",
            value=True,
            glyph="🟢",
            entropy_bits=16.0
        )
        self.register_symbol(active)
    
    def _create_core_concepts(self):
        """Create essential core concepts"""
        # Create a composite concept
        joy_concept = Concept(
            concept_id="EMOTION.JOY",
            concept_type=ConceptType.ABSTRACT,
            meaning="joy",
            symbols=[self.global_symbols.get("EMOTION_HAPPINESS")]
        )
        self.register_concept(joy_concept)
    
    def _create_core_grammar(self):
        """Create core grammar rules"""
        # Subject-Verb-Object rule
        svo_rule = Grammar(
            rule_id="GRAMMAR_SVO",
            name="Subject-Verb-Object",
            pattern="ENTITY ACTION ENTITY",
            domain=SymbolicDomain.ACTION,
            priority=100
        )
        self.register_grammar(svo_rule)
    
    def register_symbol(self, symbol: Symbol) -> bool:
        """Register a symbol globally and in its domain vocabulary"""
        try:
            # Add to global registry
            self.global_symbols[symbol.id] = symbol
            
            # Add to domain vocabulary
            if symbol.domain in self.vocabularies:
                self.vocabularies[symbol.domain].add_symbol(symbol)
            
            logger.info(f"Registered symbol: {symbol.name} ({symbol.id})")
            return True
        except Exception as e:
            logger.error(f"Failed to register symbol: {e}")
            return False
    
    def register_concept(self, concept: Concept) -> bool:
        """Register a concept globally and in relevant vocabularies"""
        try:
            # Add to global registry
            self.global_concepts[concept.concept_id] = concept
            
            # Add to primary domain vocabulary
            primary_domain = concept.get_primary_domain()
            if primary_domain in self.vocabularies:
                self.vocabularies[primary_domain].add_concept(concept)
            
            logger.info(f"Registered concept: {concept.meaning} ({concept.concept_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to register concept: {e}")
            return False
    
    def register_grammar(self, grammar: Grammar) -> bool:
        """Register a grammar rule"""
        try:
            self.grammar_rules.append(grammar)
            
            # Add to domain vocabulary
            if grammar.domain in self.vocabularies:
                self.vocabularies[grammar.domain].grammar_rules.append(grammar)
            
            logger.info(f"Registered grammar rule: {grammar.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register grammar: {e}")
            return False
    
    def translate_symbols_to_concepts(self, symbols: List[Symbol]) -> List[Concept]:
        """Translate symbols to concepts"""
        concepts = []
        
        for symbol in symbols:
            # Find concepts that contain this symbol
            for concept in self.global_concepts.values():
                if symbol in concept.symbols:
                    concepts.append(concept)
                    break
            else:
                # Create a new atomic concept for unmapped symbol
                new_concept = Concept(
                    concept_id=f"{symbol.domain.value.upper()}.{symbol.name.upper()}",
                    concept_type=ConceptType.ATOMIC,
                    meaning=symbol.name,
                    symbols=[symbol]
                )
                self.register_concept(new_concept)
                concepts.append(new_concept)
        
        return concepts
    
    def validate_grammar(self, symbols: List[Symbol]) -> Tuple[bool, List[str]]:
        """Validate symbols against grammar rules"""
        violations = []
        
        # Sort rules by priority
        sorted_rules = sorted(self.grammar_rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if rule.active and not rule.validate(symbols):
                violations.append(f"Grammar violation: {rule.name}")
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def get_vocabulary_stats(self) -> Dict[str, Any]:
        """Get statistics about the language system"""
        return {
            "total_symbols": len(self.global_symbols),
            "total_concepts": len(self.global_concepts),
            "total_grammar_rules": len(self.grammar_rules),
            "domains": {
                domain.value: {
                    "symbols": len(vocab.symbols),
                    "concepts": len(vocab.concepts),
                    "grammar_rules": len(vocab.grammar_rules)
                }
                for domain, vocab in self.vocabularies.items()
            }
        }


# Singleton instance
_universal_language_instance = None


def get_universal_language() -> UniversalLanguageCore:
    """Get or create the singleton Universal Language instance"""
    global _universal_language_instance
    if _universal_language_instance is None:
        _universal_language_instance = UniversalLanguageCore()
    return _universal_language_instance