"""
Unified Vocabulary System for Universal Language
=================================================

Consolidates all domain vocabularies from scattered implementations.
"""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from universal_language.core import Concept, Symbol, SymbolicDomain
from universal_language.glyph import get_glyph_engine

logger = logging.getLogger(__name__)


@dataclass
class DomainVocabulary:
    """
    Domain-specific vocabulary collection.

    Consolidates vocabularies from /symbolic/vocabularies/ and /core/symbolic/.
    """

    domain: SymbolicDomain
    symbols: dict[str, Symbol] = field(default_factory=dict)
    concepts: dict[str, Concept] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)  # alias -> symbol_id
    relationships: dict[str, list[str]] = field(default_factory=dict)  # symbol_id -> related_ids
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_symbol(self, symbol: Symbol) -> bool:
        """Add a symbol to the vocabulary"""
        try:
            self.symbols[symbol.id] = symbol

            # Add name as alias
            self.aliases[symbol.name.lower()] = symbol.id

            logger.debug(f"Added symbol {symbol.name} to {self.domain.value} vocabulary")
            return True
        except Exception as e:
            logger.error(f"Failed to add symbol: {e}")
            return False

    def add_concept(self, concept: Concept) -> bool:
        """Add a concept to the vocabulary"""
        try:
            self.concepts[concept.concept_id] = concept

            # Add meaning as alias
            self.aliases[concept.meaning.lower()] = concept.concept_id

            logger.debug(f"Added concept {concept.meaning} to {self.domain.value} vocabulary")
            return True
        except Exception as e:
            logger.error(f"Failed to add concept: {e}")
            return False

    def find_by_name(self, name: str) -> Optional[Symbol]:
        """Find symbol by name or alias"""
        name_lower = name.lower()

        # Check aliases first
        if name_lower in self.aliases:
            symbol_id = self.aliases[name_lower]
            return self.symbols.get(symbol_id)

        # Check direct name match
        for symbol in self.symbols.values():
            if symbol.name.lower() == name_lower:
                return symbol

        return None

    def find_concept_by_meaning(self, meaning: str) -> Optional[Concept]:
        """Find concept by meaning"""
        meaning_lower = meaning.lower()

        # Check aliases
        if meaning_lower in self.aliases:
            concept_id = self.aliases[meaning_lower]
            return self.concepts.get(concept_id)

        # Check direct meaning match
        for concept in self.concepts.values():
            if concept.meaning.lower() == meaning_lower:
                return concept

        return None

    def get_related_symbols(self, symbol_id: str) -> list[Symbol]:
        """Get symbols related to a given symbol"""
        related_ids = self.relationships.get(symbol_id, [])
        return [self.symbols[sid] for sid in related_ids if sid in self.symbols]


class VocabularyManager:
    """
    Manages all domain vocabularies centrally.
    """

    def __init__(self):
        self.vocabularies: dict[SymbolicDomain, DomainVocabulary] = {}
        self.global_index: dict[str, SymbolicDomain] = {}  # symbol_id -> domain
        self._initialize_vocabularies()
        self._load_core_vocabularies()

    def _initialize_vocabularies(self):
        """Initialize vocabulary for each domain"""
        for domain in SymbolicDomain:
            self.vocabularies[domain] = DomainVocabulary(domain=domain)
            logger.debug(f"Initialized vocabulary for domain: {domain.value}")

    def _load_core_vocabularies(self):
        """Load core vocabularies for each domain"""
        # Emotion vocabulary
        self._load_emotion_vocabulary()

        # Bio vocabulary
        self._load_bio_vocabulary()

        # Dream vocabulary
        self._load_dream_vocabulary()

        # Identity vocabulary
        self._load_identity_vocabulary()

        # Vision vocabulary
        self._load_vision_vocabulary()

        # Voice vocabulary
        self._load_voice_vocabulary()

        # Action vocabulary
        self._load_action_vocabulary()

        # State vocabulary
        self._load_state_vocabulary()

    def _load_emotion_vocabulary(self):
        """Load emotion domain vocabulary"""
        vocab = self.vocabularies[SymbolicDomain.EMOTION]

        # Core emotions with GLYPHs
        emotions = [
            ("happiness", "😊", 1.0, "Positive emotional state"),
            ("sadness", "😢", -1.0, "Negative emotional state"),
            ("anger", "😡", -0.8, "Intense negative emotion"),
            ("fear", "😨", -0.6, "Anxiety and uncertainty"),
            ("love", "😍", 0.9, "Strong positive connection"),
            ("surprise", "😮", 0.0, "Unexpected emotional response"),
            ("disgust", "🤢", -0.7, "Rejection response"),
            ("contempt", "😒", -0.5, "Superiority feeling"),
            ("joy", "😄", 0.95, "Intense happiness"),
            ("trust", "🤝", 0.7, "Confidence in reliability"),
        ]

        for name, glyph, value, description in emotions:
            symbol = Symbol(
                id=f"EMOTION_{name.upper()}",
                domain=SymbolicDomain.EMOTION,
                name=name,
                value=value,
                glyph=glyph,
                attributes={"description": description, "valence": value},
            )
            vocab.add_symbol(symbol)
            self.global_index[symbol.id] = SymbolicDomain.EMOTION

    def _load_bio_vocabulary(self):
        """Load biological domain vocabulary"""
        vocab = self.vocabularies[SymbolicDomain.BIO]

        bio_terms = [
            ("neuron", "🧠", "Basic unit of neural processing"),
            ("synapse", "🔗", "Connection between neurons"),
            ("hormone", "💉", "Chemical messenger"),
            ("dna", "🧬", "Genetic information"),
            ("cell", "🦠", "Basic unit of life"),
            ("heart", "🫀", "Circulatory center"),
            ("evolution", "🦋", "Adaptive change over time"),
            ("metabolism", "🔥", "Energy processing"),
            ("homeostasis", "⚖️", "Balance maintenance"),
            ("adaptation", "🌱", "Environmental adjustment"),
        ]

        for name, glyph, description in bio_terms:
            symbol = Symbol(
                id=f"BIO_{name.upper()}",
                domain=SymbolicDomain.BIO,
                name=name,
                value=name,
                glyph=glyph,
                attributes={"description": description},
            )
            vocab.add_symbol(symbol)
            self.global_index[symbol.id] = SymbolicDomain.BIO

    def _load_dream_vocabulary(self):
        """Load dream domain vocabulary"""
        vocab = self.vocabularies[SymbolicDomain.DREAM]

        dream_terms = [
            ("lucid", "👁️", "Conscious dreaming"),
            ("nightmare", "😱", "Negative dream experience"),
            ("symbol", "🔮", "Dream symbolism"),
            ("archetype", "🎭", "Universal dream pattern"),
            ("unconscious", "🌑", "Hidden mental processes"),
            ("rem", "👀", "Rapid eye movement sleep"),
            ("fantasy", "🦄", "Imaginative creation"),
            ("vision", "✨", "Prophetic or insightful dream"),
            ("recursion", "🔁", "Self-referential dream"),
            ("inception", "🌀", "Dream within dream"),
        ]

        for name, glyph, description in dream_terms:
            symbol = Symbol(
                id=f"DREAM_{name.upper()}",
                domain=SymbolicDomain.DREAM,
                name=name,
                value=name,
                glyph=glyph,
                attributes={"description": description},
            )
            vocab.add_symbol(symbol)
            self.global_index[symbol.id] = SymbolicDomain.DREAM

    def _load_identity_vocabulary(self):
        """Load identity domain vocabulary"""
        vocab = self.vocabularies[SymbolicDomain.IDENTITY]

        identity_terms = [
            ("self", "🪞", "Core identity"),
            ("user", "👤", "System user"),
            ("agent", "🤖", "Autonomous actor"),
            ("role", "🎭", "Functional identity"),
            ("permission", "🔑", "Access right"),
            ("authentication", "🔐", "Identity verification"),
            ("signature", "✍️", "Unique identifier"),
            ("profile", "📋", "Identity attributes"),
            ("avatar", "👾", "Digital representation"),
            ("persona", "🎨", "Projected identity"),
        ]

        for name, glyph, description in identity_terms:
            symbol = Symbol(
                id=f"IDENTITY_{name.upper()}",
                domain=SymbolicDomain.IDENTITY,
                name=name,
                value=name,
                glyph=glyph,
                attributes={"description": description},
            )
            vocab.add_symbol(symbol)
            self.global_index[symbol.id] = SymbolicDomain.IDENTITY

    def _load_vision_vocabulary(self):
        """Load vision domain vocabulary"""
        vocab = self.vocabularies[SymbolicDomain.VISION]

        vision_terms = [
            ("see", "👁️", "Visual perception"),
            ("color", "🎨", "Chromatic property"),
            ("shape", "⬛", "Geometric form"),
            ("pattern", "🔲", "Visual arrangement"),
            ("brightness", "☀️", "Light intensity"),
            ("contrast", "◼️", "Visual difference"),
            ("focus", "🔍", "Visual attention"),
            ("perspective", "🖼️", "Visual viewpoint"),
            ("recognition", "👀", "Visual identification"),
            ("illusion", "🌀", "Visual deception"),
        ]

        for name, glyph, description in vision_terms:
            symbol = Symbol(
                id=f"VISION_{name.upper()}",
                domain=SymbolicDomain.VISION,
                name=name,
                value=name,
                glyph=glyph,
                attributes={"description": description},
            )
            vocab.add_symbol(symbol)
            self.global_index[symbol.id] = SymbolicDomain.VISION

    def _load_voice_vocabulary(self):
        """Load voice domain vocabulary"""
        vocab = self.vocabularies[SymbolicDomain.VOICE]

        voice_terms = [
            ("speak", "🗣️", "Vocal expression"),
            ("listen", "👂", "Auditory perception"),
            ("whisper", "🤫", "Quiet speech"),
            ("shout", "📢", "Loud speech"),
            ("sing", "🎵", "Musical vocalization"),
            ("silence", "🤐", "Absence of sound"),
            ("echo", "🔊", "Sound reflection"),
            ("tone", "🎶", "Voice quality"),
            ("accent", "🗨️", "Speech pattern"),
            ("harmony", "🎼", "Sound agreement"),
        ]

        for name, glyph, description in voice_terms:
            symbol = Symbol(
                id=f"VOICE_{name.upper()}",
                domain=SymbolicDomain.VOICE,
                name=name,
                value=name,
                glyph=glyph,
                attributes={"description": description},
            )
            vocab.add_symbol(symbol)
            self.global_index[symbol.id] = SymbolicDomain.VOICE

    def _load_action_vocabulary(self):
        """Load action domain vocabulary"""
        vocab = self.vocabularies[SymbolicDomain.ACTION]

        action_terms = [
            ("create", "✨", "Bring into existence"),
            ("destroy", "💥", "Remove from existence"),
            ("modify", "🔧", "Change properties"),
            ("connect", "🔗", "Establish relationship"),
            ("disconnect", "✂️", "Break relationship"),
            ("start", "▶️", "Begin process"),
            ("stop", "⏹️", "End process"),
            ("pause", "⏸️", "Suspend process"),
            ("continue", "⏯️", "Resume process"),
            ("transform", "🔄", "Change form"),
        ]

        for name, glyph, description in action_terms:
            symbol = Symbol(
                id=f"ACTION_{name.upper()}",
                domain=SymbolicDomain.ACTION,
                name=name,
                value=name,
                glyph=glyph,
                attributes={"description": description},
            )
            vocab.add_symbol(symbol)
            self.global_index[symbol.id] = SymbolicDomain.ACTION

    def _load_state_vocabulary(self):
        """Load state domain vocabulary"""
        vocab = self.vocabularies[SymbolicDomain.STATE]

        state_terms = [
            ("active", "🟢", "Currently operating"),
            ("inactive", "⚫", "Not operating"),
            ("pending", "🟡", "Awaiting action"),
            ("error", "🔴", "Failed state"),
            ("success", "✅", "Completed successfully"),
            ("warning", "⚠️", "Caution state"),
            ("stable", "⚖️", "Balanced state"),
            ("unstable", "🌪️", "Chaotic state"),
            ("transitioning", "🔄", "Changing state"),
            ("unknown", "❓", "Undefined state"),
        ]

        for name, glyph, description in state_terms:
            symbol = Symbol(
                id=f"STATE_{name.upper()}",
                domain=SymbolicDomain.STATE,
                name=name,
                value=name,
                glyph=glyph,
                attributes={"description": description},
            )
            vocab.add_symbol(symbol)
            self.global_index[symbol.id] = SymbolicDomain.STATE

    def get_vocabulary(self, domain: SymbolicDomain) -> DomainVocabulary:
        """Get vocabulary for a specific domain"""
        return self.vocabularies.get(domain)

    def find_symbol(self, name: str, domain: Optional[SymbolicDomain] = None) -> Optional[Symbol]:
        """Find a symbol by name, optionally within a specific domain"""
        if domain:
            vocab = self.vocabularies.get(domain)
            if vocab:
                return vocab.find_by_name(name)
        else:
            # Search all domains
            for vocab in self.vocabularies.values():
                symbol = vocab.find_by_name(name)
                if symbol:
                    return symbol

        return None

    def find_concept(self, meaning: str, domain: Optional[SymbolicDomain] = None) -> Optional[Concept]:
        """Find a concept by meaning"""
        if domain:
            vocab = self.vocabularies.get(domain)
            if vocab:
                return vocab.find_concept_by_meaning(meaning)
        else:
            # Search all domains
            for vocab in self.vocabularies.values():
                concept = vocab.find_concept_by_meaning(meaning)
                if concept:
                    return concept

        return None

    def get_all_symbols(self) -> list[Symbol]:
        """Get all symbols across all domains"""
        all_symbols = []
        for vocab in self.vocabularies.values():
            all_symbols.extend(vocab.symbols.values())
        return all_symbols

    def get_all_concepts(self) -> list[Concept]:
        """Get all concepts across all domains"""
        all_concepts = []
        for vocab in self.vocabularies.values():
            all_concepts.extend(vocab.concepts.values())
        return all_concepts

    def get_statistics(self) -> dict[str, Any]:
        """Get vocabulary statistics"""
        stats = {
            "total_symbols": sum(len(v.symbols) for v in self.vocabularies.values()),
            "total_concepts": sum(len(v.concepts) for v in self.vocabularies.values()),
            "domains": {},
        }

        for domain, vocab in self.vocabularies.items():
            stats["domains"][domain.value] = {
                "symbols": len(vocab.symbols),
                "concepts": len(vocab.concepts),
                "aliases": len(vocab.aliases),
                "relationships": len(vocab.relationships),
            }

        return stats


class UnifiedVocabulary:
    """
    Unified vocabulary system combining all domain vocabularies.

    This is the main interface for vocabulary operations.
    """

    def __init__(self):
        self.manager = VocabularyManager()
        self.glyph_engine = get_glyph_engine()
        logger.info("Unified Vocabulary initialized")

    def register_symbol(self, symbol: Symbol) -> bool:
        """Register a new symbol"""
        vocab = self.manager.get_vocabulary(symbol.domain)
        if vocab:
            success = vocab.add_symbol(symbol)
            if success:
                # Also register GLYPH if present
                if symbol.glyph:
                    self.glyph_engine.register_custom_glyph(symbol.glyph, symbol.name)
            return success
        return False

    def register_concept(self, concept: Concept) -> bool:
        """Register a new concept"""
        primary_domain = concept.get_primary_domain()
        vocab = self.manager.get_vocabulary(primary_domain)
        if vocab:
            return vocab.add_concept(concept)
        return False

    def lookup(self, term: str) -> dict[str, Any]:
        """Look up a term in the vocabulary"""
        results = {"term": term, "symbols": [], "concepts": [], "glyphs": []}

        # Search for symbols
        symbol = self.manager.find_symbol(term)
        if symbol:
            results["symbols"].append(symbol.to_dict())
            if symbol.glyph:
                results["glyphs"].append(symbol.glyph)

        # Search for concepts
        concept = self.manager.find_concept(term)
        if concept:
            results["concepts"].append(concept.to_dict())

        # Search in GLYPH map
        glyph = self.glyph_engine.find_glyph_for_concept(term)
        if glyph:
            results["glyphs"].append(glyph)

        return results

    def get_domain_vocabulary(self, domain: SymbolicDomain) -> dict[str, Any]:
        """Get all vocabulary for a domain"""
        vocab = self.manager.get_vocabulary(domain)
        if vocab:
            return {
                "domain": domain.value,
                "symbols": [s.to_dict() for s in vocab.symbols.values()],
                "concepts": [c.to_dict() for c in vocab.concepts.values()],
                "aliases": vocab.aliases,
                "metadata": vocab.metadata,
            }
        return {}

    def export_vocabulary(self, path: Optional[Path] = None) -> dict[str, Any]:
        """Export the entire vocabulary"""
        export_data = {
            "version": "1.0.0",
            "statistics": self.manager.get_statistics(),
            "domains": {},
        }

        for domain in SymbolicDomain:
            export_data["domains"][domain.value] = self.get_domain_vocabulary(domain)

        if path:
            with open(path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

        return export_data

    def import_vocabulary(self, data: dict[str, Any]) -> bool:
        """Import vocabulary data"""
        try:
            # Import domain vocabularies
            if "domains" in data:
                for _domain_name, _domain_data in data["domains"].items():
                    # TODO: Implement import logic
                    pass

            logger.info("Vocabulary import completed")
            return True
        except Exception as e:
            logger.error(f"Failed to import vocabulary: {e}")
            return False


# Singleton instance
_unified_vocabulary_instance = None


def get_unified_vocabulary() -> UnifiedVocabulary:
    """Get or create the singleton Unified Vocabulary instance"""
    global _unified_vocabulary_instance
    if _unified_vocabulary_instance is None:
        _unified_vocabulary_instance = UnifiedVocabulary()
    return _unified_vocabulary_instance
