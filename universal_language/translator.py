"""
Universal Translator for Cross-Modal and Cross-Domain Translation
==================================================================

Enables translation between different representations, modalities,
and domains within the Universal Language system.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from universal_language.core import Concept, ConceptType, Symbol, SymbolicDomain
from universal_language.glyph import GLYPHSequence, GLYPHToken, get_glyph_engine
from universal_language.vocabulary import get_unified_vocabulary

logger = logging.getLogger(__name__)


class TranslationType(Enum):
    """Types of translations supported"""

    SYMBOL_TO_CONCEPT = "symbol_to_concept"
    CONCEPT_TO_SYMBOL = "concept_to_symbol"
    GLYPH_TO_SYMBOL = "glyph_to_symbol"
    SYMBOL_TO_GLYPH = "symbol_to_glyph"
    CROSS_DOMAIN = "cross_domain"
    CROSS_MODAL = "cross_modal"
    PRIVATE_TO_UNIVERSAL = "private_to_universal"
    UNIVERSAL_TO_PRIVATE = "universal_to_private"


@dataclass
class TranslationResult:
    """Result of a translation operation"""

    source: Any
    target: Any
    translation_type: TranslationType
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    trace: list[str] = field(default_factory=list)

    def is_successful(self) -> bool:
        """Check if translation was successful"""
        return self.target is not None and self.confidence > 0.5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "source": str(self.source),
            "target": str(self.target),
            "type": self.translation_type.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "trace": self.trace,
            "successful": self.is_successful(),
        }


class ConceptMapper:
    """
    Maps between symbols and concepts.
    """

    def __init__(self):
        self.vocabulary = get_unified_vocabulary()
        self.concept_cache: dict[str, Concept] = {}
        self.symbol_cache: dict[str, Symbol] = {}

    def symbol_to_concept(self, symbol: Symbol) -> Optional[Concept]:
        """Convert a symbol to its corresponding concept"""
        # Check cache
        if symbol.id in self.concept_cache:
            return self.concept_cache[symbol.id]

        # Create atomic concept for the symbol
        concept = Concept(
            concept_id=f"{symbol.domain.value.upper()}.{symbol.name.upper()}",
            concept_type=ConceptType.ATOMIC,
            meaning=symbol.name,
            symbols=[symbol],
            entropy_total=symbol.entropy_bits,
        )

        # Cache and return
        self.concept_cache[symbol.id] = concept
        return concept

    def symbols_to_composite_concept(self, symbols: list[Symbol]) -> Concept:
        """Combine multiple symbols into a composite concept"""
        # Determine primary domain
        domains = [s.domain for s in symbols]
        primary_domain = max(set(domains), key=domains.count)

        # Create composite meaning
        meanings = [s.name for s in symbols]
        composite_meaning = " + ".join(meanings)

        # Create composite concept
        concept = Concept(
            concept_id=f"{primary_domain.value.upper()}.COMPOSITE_{hashlib.sha256(composite_meaning.encode()).hexdigest()[:8]}",
            concept_type=ConceptType.COMPOSITE,
            meaning=composite_meaning,
            symbols=symbols,
            entropy_total=sum(s.entropy_bits for s in symbols),
        )

        return concept

    def concept_to_symbols(self, concept: Concept) -> list[Symbol]:
        """Extract symbols from a concept"""
        if concept.symbols:
            return concept.symbols

        # Try to find or create symbols for the concept
        symbols = []

        # Parse concept ID to determine domain
        if "." in concept.concept_id:
            domain_str, concept_name = concept.concept_id.split(".", 1)
            try:
                domain = SymbolicDomain[domain_str]
            except KeyError:
                domain = SymbolicDomain.CONTEXT
        else:
            domain = SymbolicDomain.CONTEXT

        # Create a symbol for the concept
        symbol = Symbol(
            id=f"SYMBOL_{concept.concept_id}",
            domain=domain,
            name=concept.meaning,
            value=concept.meaning,
            entropy_bits=concept.entropy_total / max(1, len(concept.symbols)),
        )
        symbols.append(symbol)

        return symbols

    def find_related_concepts(self, concept: Concept, max_depth: int = 2) -> list[Concept]:
        """Find concepts related to a given concept"""
        related = []

        # Get parent concepts
        for parent_id in concept.parent_concepts:
            parent_concept = self.lookup_concept_by_id(parent_id)
            if parent_concept and parent_concept not in related:
                related.append(parent_concept)
                # Recursively find related concepts if within depth limit
                if max_depth > 1:
                    nested = self.find_related_concepts(parent_concept, max_depth - 1)
                    related.extend([c for c in nested if c not in related])

        # Get child concepts
        for child_id in concept.child_concepts:
            child_concept = self.lookup_concept_by_id(child_id)
            if child_concept and child_concept not in related:
                related.append(child_concept)
                # Recursively find related concepts if within depth limit
                if max_depth > 1:
                    nested = self.find_related_concepts(child_concept, max_depth - 1)
                    related.extend([c for c in nested if c not in related])

        return related

    def lookup_concept_by_id(self, concept_id: str) -> Optional[Concept]:
        """Look up a concept by its ID"""
        # Check cache first
        if concept_id in self.concept_cache:
            return self.concept_cache[concept_id]

        # Try to find in vocabulary
        try:
            # Parse concept ID for domain lookup
            if "." in concept_id:
                domain_str, name = concept_id.split(".", 1)
                try:
                    domain = SymbolicDomain[domain_str]
                    # Search for symbol with matching concept in that domain
                    domain_vocab = self.vocabulary.manager.get_vocabulary(domain)
                    for symbol in domain_vocab.symbols:
                        if symbol.name.upper() in name.upper() or name.upper() in symbol.name.upper():
                            concept = self.symbol_to_concept(symbol)
                            self.concept_cache[concept_id] = concept
                            return concept
                except KeyError:
                    pass

            # Fallback: search all vocabularies
            for domain in SymbolicDomain:
                domain_vocab = self.vocabulary.manager.get_vocabulary(domain)
                for symbol in domain_vocab.symbols:
                    if symbol.id == concept_id or concept_id in symbol.name:
                        concept = self.symbol_to_concept(symbol)
                        self.concept_cache[concept_id] = concept
                        return concept

        except Exception as e:
            logger.warning(f"Error looking up concept {concept_id}: {e}")

        return None


class CrossModalTranslator:
    """
    Translates between different modalities (text, visual, audio, etc.).
    """

    def __init__(self):
        self.glyph_engine = get_glyph_engine()
        self.vocabulary = get_unified_vocabulary()
        self.modality_mappings = self._initialize_mappings()

    def _initialize_mappings(self) -> dict[str, dict[str, Any]]:
        """Initialize modality mappings"""
        return {
            "text_to_glyph": {},
            "glyph_to_text": {},
            "emotion_to_color": {
                "happiness": "#FFD700",  # Gold
                "sadness": "#4169E1",  # Blue
                "anger": "#FF0000",  # Red
                "fear": "#800080",  # Purple
                "love": "#FF69B4",  # Pink
                "surprise": "#FFA500",  # Orange
            },
            "color_to_emotion": {
                "#FFD700": "happiness",
                "#4169E1": "sadness",
                "#FF0000": "anger",
                "#800080": "fear",
                "#FF69B4": "love",
                "#FFA500": "surprise",
            },
        }

    def text_to_glyphs(self, text: str) -> GLYPHSequence:
        """Convert text to GLYPH representation"""
        # Parse text to extract concepts
        concepts = text.lower().split()

        # Translate concepts to GLYPHs
        return self.glyph_engine.translate_to_glyphs(concepts)

    def glyphs_to_text(self, sequence: GLYPHSequence) -> str:
        """Convert GLYPH sequence to text"""
        return sequence.to_meaning()

    def symbol_to_glyph(self, symbol: Symbol) -> Optional[GLYPHToken]:
        """Convert a symbol to its GLYPH representation"""
        if symbol.glyph:
            return self.glyph_engine.create_token(symbol.glyph, symbol.name)

        # Try to find a matching GLYPH
        glyph = self.glyph_engine.find_glyph_for_concept(symbol.name)
        if glyph:
            return self.glyph_engine.create_token(glyph, symbol.name)

        return None

    def glyph_to_symbol(self, glyph_token: GLYPHToken) -> Optional[Symbol]:
        """Convert a GLYPH token to a symbol"""
        # Search for symbol with matching glyph
        symbol = self.vocabulary.manager.find_symbol(glyph_token.meaning)
        if symbol:
            return symbol

        # Create new symbol for the glyph
        symbol = Symbol(
            id=f"GLYPH_{glyph_token.hash()}",
            domain=SymbolicDomain.CONTEXT,
            name=glyph_token.meaning,
            value=glyph_token.meaning,
            glyph=glyph_token.glyph,
        )

        return symbol

    def emotion_to_color(self, emotion: str) -> Optional[str]:
        """Convert emotion to color representation"""
        return self.modality_mappings["emotion_to_color"].get(emotion.lower())

    def color_to_emotion(self, color: str) -> Optional[str]:
        """Convert color to emotion"""
        return self.modality_mappings["color_to_emotion"].get(color.upper())


class UniversalTranslator:
    """
    Main translator combining all translation capabilities.

    Based on Universal Language spec for private → universal → private translation.
    """

    def __init__(self):
        self.concept_mapper = ConceptMapper()
        self.cross_modal = CrossModalTranslator()
        self.vocabulary = get_unified_vocabulary()
        self.glyph_engine = get_glyph_engine()
        self.translation_cache: dict[str, TranslationResult] = {}
        logger.info("Universal Translator initialized")

    def translate(self, source: Any, target_type: str, context: Optional[dict[str, Any]] = None) -> TranslationResult:
        """
        Translate from any source to target type.

        Args:
            source: The source to translate (Symbol, Concept, GLYPHToken, etc.)
            target_type: Target type ("symbol", "concept", "glyph", "text", etc.)
            context: Optional context for translation

        Returns:
            TranslationResult with translated target
        """
        trace = []

        # Determine source type
        source_type = self._detect_source_type(source)
        trace.append(f"Detected source type: {source_type}")

        # Check cache
        cache_key = f"{source_type}:{source!s}:{target_type}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        # Perform translation based on types
        result = self._perform_translation(source, source_type, target_type, trace, context)

        # Cache result
        self.translation_cache[cache_key] = result

        return result

    def _detect_source_type(self, source: Any) -> str:
        """Detect the type of the source"""
        if isinstance(source, Symbol):
            return "symbol"
        elif isinstance(source, Concept):
            return "concept"
        elif isinstance(source, GLYPHToken):
            return "glyph"
        elif isinstance(source, GLYPHSequence):
            return "glyph_sequence"
        elif isinstance(source, str):
            return "text"
        elif isinstance(source, list):
            return "list"
        else:
            return "unknown"

    def _perform_translation(
        self,
        source: Any,
        source_type: str,
        target_type: str,
        trace: list[str],
        context: Optional[dict[str, Any]],
    ) -> TranslationResult:
        """Perform the actual translation"""
        target = None
        translation_type = None
        confidence = 1.0

        # Symbol translations
        if source_type == "symbol" and target_type == "concept":
            target = self.concept_mapper.symbol_to_concept(source)
            translation_type = TranslationType.SYMBOL_TO_CONCEPT
            trace.append("Translated symbol to concept")

        elif source_type == "symbol" and target_type == "glyph":
            target = self.cross_modal.symbol_to_glyph(source)
            translation_type = TranslationType.SYMBOL_TO_GLYPH
            trace.append("Translated symbol to GLYPH")

        # Concept translations
        elif source_type == "concept" and target_type == "symbol":
            symbols = self.concept_mapper.concept_to_symbols(source)
            target = symbols[0] if symbols else None
            translation_type = TranslationType.CONCEPT_TO_SYMBOL
            trace.append("Translated concept to symbol")

        # GLYPH translations
        elif source_type == "glyph" and target_type == "symbol":
            target = self.cross_modal.glyph_to_symbol(source)
            translation_type = TranslationType.GLYPH_TO_SYMBOL
            trace.append("Translated GLYPH to symbol")

        # Text translations
        elif source_type == "text" and target_type == "glyph":
            target = self.cross_modal.text_to_glyphs(source)
            translation_type = TranslationType.CROSS_MODAL
            trace.append("Translated text to GLYPHs")

        elif source_type == "glyph_sequence" and target_type == "text":
            target = self.cross_modal.glyphs_to_text(source)
            translation_type = TranslationType.CROSS_MODAL
            trace.append("Translated GLYPHs to text")

        # List translations
        elif source_type == "list":
            if all(isinstance(item, Symbol) for item in source):
                if target_type == "concept":
                    target = self.concept_mapper.symbols_to_composite_concept(source)
                    translation_type = TranslationType.SYMBOL_TO_CONCEPT
                    trace.append("Translated symbol list to composite concept")

        # Cross-domain translation
        elif source_type == "symbol" and target_type == "cross_domain":
            target_domain = context.get("target_domain") if context else None
            if target_domain:
                target = self._translate_cross_domain(source, target_domain)
                translation_type = TranslationType.CROSS_DOMAIN
                trace.append(f"Translated across domains to {target_domain}")

        # Create result
        result = TranslationResult(
            source=source,
            target=target,
            translation_type=translation_type or TranslationType.CROSS_MODAL,
            confidence=confidence if target else 0.0,
            metadata=context or {},
            trace=trace,
        )

        return result

    def _translate_cross_domain(self, symbol: Symbol, target_domain: SymbolicDomain) -> Optional[Symbol]:
        """Translate a symbol to a different domain"""
        # Find equivalent symbol in target domain
        target_vocab = self.vocabulary.manager.get_vocabulary(target_domain)
        if target_vocab:
            # Look for similar meaning
            for target_symbol in target_vocab.symbols.values():
                if target_symbol.name == symbol.name:
                    return target_symbol

        # Create new symbol in target domain
        new_symbol = Symbol(
            id=f"{target_domain.value.upper()}_{symbol.name.upper()}",
            domain=target_domain,
            name=symbol.name,
            value=symbol.value,
            glyph=symbol.glyph,
            attributes=symbol.attributes.copy(),
        )

        return new_symbol

    def private_to_universal(self, private_tokens: list[Any]) -> list[str]:
        """
        Translate private tokens to universal concept IDs.

        Based on Universal Language spec for privacy-preserving translation.
        """
        concept_ids = []

        for token in private_tokens:
            # Translate to symbol
            if isinstance(token, str):
                symbol = self.vocabulary.manager.find_symbol(token)
            else:
                symbol = token if isinstance(token, Symbol) else None

            if symbol:
                # Convert to concept
                concept = self.concept_mapper.symbol_to_concept(symbol)
                if concept:
                    concept_ids.append(concept.concept_id)
                else:
                    # Use symbol ID as fallback
                    concept_ids.append(f"SYMBOL.{symbol.id}")
            else:
                # Unknown token - create placeholder
                concept_ids.append(f"UNKNOWN.{hashlib.sha256(str(token).encode()).hexdigest()[:8]}")

        return concept_ids

    def universal_to_private(
        self, concept_ids: list[str], user_preferences: Optional[dict[str, Any]] = None
    ) -> list[Any]:
        """
        Translate universal concept IDs to user's private representation.

        Based on Universal Language spec for personalized rendering.
        """
        private_tokens = []

        for concept_id in concept_ids:
            # Look up concept using the concept registry
            concept = self.concept_mapper.lookup_concept_by_id(concept_id)

            if concept:
                # Use the actual concept for private representation
                if concept.symbols:
                    symbol = concept.symbols[0]  # Use primary symbol
                    # Use user preference if available
                    if user_preferences and "render_mode" in user_preferences:
                        if user_preferences["render_mode"] == "glyph" and symbol.glyph:
                            private_tokens.append(symbol.glyph)
                        else:
                            private_tokens.append(symbol.name)
                    else:
                        private_tokens.append(symbol)
                else:
                    private_tokens.append(concept.meaning)
            # Fallback to parsing concept ID if lookup fails
            elif "." in concept_id:
                domain_str, concept_name = concept_id.split(".", 1)

                # Find matching symbol
                symbol = self.vocabulary.manager.find_symbol(concept_name.lower())
                if symbol:
                    # Use user preference if available
                    if user_preferences and "render_mode" in user_preferences:
                        if user_preferences["render_mode"] == "glyph" and symbol.glyph:
                            private_tokens.append(symbol.glyph)
                        else:
                            private_tokens.append(symbol.name)
                    else:
                        private_tokens.append(symbol)
                else:
                    # Fallback to concept name
                    private_tokens.append(concept_name.lower().replace("_", " "))
            else:
                private_tokens.append(concept_id)

        return private_tokens

    def get_translation_stats(self) -> dict[str, Any]:
        """Get translation statistics"""
        successful = sum(1 for r in self.translation_cache.values() if r.is_successful())
        failed = len(self.translation_cache) - successful

        translation_types = {}
        for r in self.translation_cache.values():
            if r.translation_type:
                type_name = r.translation_type.value
                translation_types[type_name] = translation_types.get(type_name, 0) + 1

        return {
            "total_translations": len(self.translation_cache),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / max(1, len(self.translation_cache)),
            "cache_size": len(self.translation_cache),
            "translation_types": translation_types,
        }


from functools import lru_cache


@lru_cache(maxsize=1)
def get_universal_translator() -> UniversalTranslator:
    """Get or create the singleton Universal Translator instance"""
    return UniversalTranslator()
