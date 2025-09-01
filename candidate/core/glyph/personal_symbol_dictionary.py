#!/usr/bin/env python3
"""
Personal Symbol Dictionary for LUKHAS
======================================
User-specific symbolic communication and personalization.
Based on GPT5 audit recommendations.
"""

import pickle
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class SymbolType(Enum):
    """Types of personal symbols"""

    CONCEPT = "concept"  # Abstract concepts
    EMOTION = "emotion"  # Emotional states
    ACTION = "action"  # Actions/commands
    OBJECT = "object"  # Physical/digital objects
    RELATIONSHIP = "relationship"  # Connections between concepts
    MODIFIER = "modifier"  # Modifies other symbols
    PERSONAL = "personal"  # User-specific meanings


@dataclass
class PersonalSymbol:
    """
    A personal symbol with user-specific meaning.
    Evolves based on usage and feedback.
    """

    symbol_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""

    # Symbol definition
    symbol: str = ""  # The symbol itself (emoji, word, glyph)
    symbol_type: SymbolType = SymbolType.CONCEPT
    meaning: str = ""  # Primary meaning

    # Semantic information
    embeddings: Optional[np.ndarray] = None  # Semantic embedding
    synonyms: list[str] = field(default_factory=list)
    antonyms: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)

    # Context and usage
    contexts: list[str] = field(default_factory=list)  # Usage contexts
    examples: list[str] = field(default_factory=list)  # Example uses
    frequency: int = 0  # Usage frequency
    last_used: Optional[float] = None

    # Evolution
    confidence: float = 0.5  # Confidence in meaning
    stability: float = 0.5  # How stable the meaning is
    variations: dict[str, float] = field(default_factory=dict)  # Meaning variations

    # Emotional associations
    emotional_valence: float = 0.0  # -1 (negative) to 1 (positive)
    emotional_arousal: float = 0.0  # 0 (calm) to 1 (excited)
    emotional_dominance: float = 0.0  # 0 (submissive) to 1 (dominant)

    # Metadata
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    source: str = "user"  # user, system, learned
    tags: set[str] = field(default_factory=set)

    def update_usage(self):
        """Update usage statistics"""
        self.frequency += 1
        self.last_used = time.time()
        self.modified_at = time.time()

        # Increase stability with usage
        self.stability = min(1.0, self.stability + 0.01)

    def evolve_meaning(self, new_context: str, feedback: float):
        """
        Evolve symbol meaning based on new usage.

        Args:
            new_context: New context where symbol was used
            feedback: Feedback score (-1 to 1)
        """
        # Add context
        if new_context not in self.contexts:
            self.contexts.append(new_context)

        # Adjust confidence based on feedback
        self.confidence = max(0, min(1, self.confidence + feedback * 0.1))

        # Adjust stability
        if feedback < -0.5:
            # Negative feedback decreases stability
            self.stability = max(0, self.stability - 0.05)
        elif feedback > 0.5:
            # Positive feedback increases stability
            self.stability = min(1, self.stability + 0.02)

        self.modified_at = time.time()


class PersonalSymbolDictionary:
    """
    Manages personal symbol dictionaries for users.
    Enables personalized communication and learning.
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        embedding_model: Optional[Any] = None,
        max_symbols_per_user: int = 1000,
    ):
        """
        Initialize personal symbol dictionary.

        Args:
            storage_path: Path for persistent storage
            embedding_model: Model for generating embeddings
            max_symbols_per_user: Maximum symbols per user
        """
        self.storage_path = storage_path or Path("data/personal_symbols")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.embedding_model = embedding_model
        self.max_symbols_per_user = max_symbols_per_user

        # User dictionaries
        self.dictionaries: dict[str, dict[str, PersonalSymbol]] = defaultdict(dict)

        # Global symbol registry (shared meanings)
        self.global_symbols: dict[str, PersonalSymbol] = {}

        # Symbol evolution tracking
        self.evolution_history: dict[str, list[dict[str, Any]]] = defaultdict(list)

        # Load existing dictionaries
        self._load_dictionaries()

        # Initialize default global symbols
        self._init_global_symbols()

    def _init_global_symbols(self):
        """Initialize default global symbols"""
        defaults = [
            ("🔮", SymbolType.CONCEPT, "mystery, prediction, future"),
            ("🧬", SymbolType.CONCEPT, "DNA, evolution, life"),
            ("⚡", SymbolType.ACTION, "fast, immediate, energy"),
            ("🌊", SymbolType.EMOTION, "flow, change, emotion"),
            ("🔗", SymbolType.RELATIONSHIP, "connection, link, bond"),
            ("✨", SymbolType.MODIFIER, "special, enhanced, magical"),
            ("🎯", SymbolType.ACTION, "goal, target, focus"),
            ("💭", SymbolType.CONCEPT, "thought, idea, contemplation"),
            ("🔄", SymbolType.ACTION, "repeat, cycle, refresh"),
            ("🛡️", SymbolType.CONCEPT, "protection, safety, defense"),
        ]

        for symbol, sym_type, meaning in defaults:
            if symbol not in self.global_symbols:
                self.global_symbols[symbol] = PersonalSymbol(
                    symbol=symbol,
                    symbol_type=sym_type,
                    meaning=meaning,
                    source="system",
                    confidence=0.9,
                    stability=0.9,
                )

    def add_symbol(
        self,
        user_id: str,
        symbol: str,
        meaning: str,
        symbol_type: SymbolType = SymbolType.CONCEPT,
        examples: Optional[list[str]] = None,
        **kwargs,
    ) -> PersonalSymbol:
        """
        Add a personal symbol for a user.

        Args:
            user_id: User identifier
            symbol: The symbol
            meaning: Symbol meaning
            symbol_type: Type of symbol
            examples: Usage examples
            **kwargs: Additional symbol properties

        Returns:
            Created personal symbol
        """
        # Check user limit
        if len(self.dictionaries[user_id]) >= self.max_symbols_per_user:
            # Remove least used symbol
            self._cleanup_user_symbols(user_id)

        # Create symbol
        personal_symbol = PersonalSymbol(
            user_id=user_id,
            symbol=symbol,
            meaning=meaning,
            symbol_type=symbol_type,
            examples=examples or [],
            **kwargs,
        )

        # Generate embedding if model available
        if self.embedding_model:
            personal_symbol.embeddings = self._generate_embedding(f"{symbol} {meaning}")

        # Add to user dictionary
        self.dictionaries[user_id][symbol] = personal_symbol

        # Track evolution
        self.evolution_history[f"{user_id}:{symbol}"].append(
            {"timestamp": time.time(), "action": "created", "meaning": meaning}
        )

        # Save
        self._save_user_dictionary(user_id)

        return personal_symbol

    def get_symbol(self, user_id: str, symbol: str, create_if_missing: bool = False) -> Optional[PersonalSymbol]:
        """
        Get a symbol from user's dictionary.

        Args:
            user_id: User identifier
            symbol: Symbol to retrieve
            create_if_missing: Create from global if not found

        Returns:
            Personal symbol or None
        """
        # Check user dictionary
        if symbol in self.dictionaries[user_id]:
            return self.dictionaries[user_id][symbol]

        # Check global dictionary
        if symbol in self.global_symbols and create_if_missing:
            # Copy global symbol for user
            global_sym = self.global_symbols[symbol]
            user_sym = PersonalSymbol(
                user_id=user_id,
                symbol=symbol,
                symbol_type=global_sym.symbol_type,
                meaning=global_sym.meaning,
                source="global",
                confidence=global_sym.confidence * 0.8,  # Slightly lower confidence
            )

            self.dictionaries[user_id][symbol] = user_sym
            return user_sym

        return None

    def interpret_symbols(self, user_id: str, text: str, context: Optional[str] = None) -> dict[str, Any]:
        """
        Interpret symbols in text using user's dictionary.

        Args:
            user_id: User identifier
            text: Text containing symbols
            context: Optional context

        Returns:
            Interpretation with meanings
        """
        interpretation = {
            "original": text,
            "symbols_found": [],
            "meanings": [],
            "translated": text,
            "confidence": 1.0,
        }

        user_dict = self.dictionaries.get(user_id, {})

        # Find all symbols in text
        for symbol, personal_sym in user_dict.items():
            if symbol in text:
                interpretation["symbols_found"].append(symbol)
                interpretation["meanings"].append(
                    {
                        "symbol": symbol,
                        "meaning": personal_sym.meaning,
                        "type": personal_sym.symbol_type.value,
                        "confidence": personal_sym.confidence,
                    }
                )

                # Update usage
                personal_sym.update_usage()

                # Replace in translated text
                interpretation["translated"] = interpretation["translated"].replace(symbol, f"[{personal_sym.meaning}]")

                # Adjust confidence
                interpretation["confidence"] *= personal_sym.confidence

        # Also check global symbols
        for symbol, global_sym in self.global_symbols.items():
            if symbol in text and symbol not in interpretation["symbols_found"]:
                interpretation["symbols_found"].append(symbol)
                interpretation["meanings"].append(
                    {
                        "symbol": symbol,
                        "meaning": global_sym.meaning,
                        "type": global_sym.symbol_type.value,
                        "confidence": global_sym.confidence,
                        "source": "global",
                    }
                )

        return interpretation

    def suggest_symbols(self, user_id: str, concept: str, limit: int = 5) -> list[PersonalSymbol]:
        """
        Suggest symbols for a concept.

        Args:
            user_id: User identifier
            concept: Concept to symbolize
            limit: Maximum suggestions

        Returns:
            List of suggested symbols
        """
        suggestions = []

        # Generate embedding for concept
        if self.embedding_model:
            concept_embedding = self._generate_embedding(concept)

            # Find similar symbols from user dictionary
            user_symbols = []
            for symbol in self.dictionaries[user_id].values():
                if symbol.embeddings is not None:
                    similarity = cosine_similarity(concept_embedding.reshape(1, -1), symbol.embeddings.reshape(1, -1))[
                        0, 0
                    ]
                    user_symbols.append((symbol, similarity))

            # Sort by similarity
            user_symbols.sort(key=lambda x: x[1], reverse=True)
            suggestions.extend([s[0] for s in user_symbols[:limit]])

        # If not enough suggestions, add from global
        if len(suggestions) < limit:
            for symbol in self.global_symbols.values():
                if concept.lower() in symbol.meaning.lower():
                    suggestions.append(symbol)
                    if len(suggestions) >= limit:
                        break

        return suggestions[:limit]

    def learn_from_usage(self, user_id: str, symbol: str, context: str, success: bool):
        """
        Learn from symbol usage.

        Args:
            user_id: User identifier
            symbol: Symbol used
            context: Usage context
            success: Whether usage was successful
        """
        personal_sym = self.get_symbol(user_id, symbol, create_if_missing=True)

        if personal_sym:
            # Evolve meaning based on feedback
            feedback = 0.5 if success else -0.5
            personal_sym.evolve_meaning(context, feedback)

            # Track evolution
            self.evolution_history[f"{user_id}:{symbol}"].append(
                {
                    "timestamp": time.time(),
                    "action": "learned",
                    "context": context,
                    "success": success,
                    "confidence": personal_sym.confidence,
                }
            )

            # Save periodically
            if len(self.evolution_history[f"{user_id}:{symbol}"]) % 10 == 0:
                self._save_user_dictionary(user_id)

    def merge_symbols(self, user_id: str, symbols: list[str], new_symbol: str, new_meaning: str) -> PersonalSymbol:
        """
        Merge multiple symbols into a new compound symbol.

        Args:
            user_id: User identifier
            symbols: Symbols to merge
            new_symbol: New compound symbol
            new_meaning: Meaning of compound

        Returns:
            New compound symbol
        """
        # Get component symbols
        components = []
        for sym in symbols:
            personal_sym = self.get_symbol(user_id, sym, create_if_missing=True)
            if personal_sym:
                components.append(personal_sym)

        # Create compound symbol
        compound = self.add_symbol(
            user_id=user_id,
            symbol=new_symbol,
            meaning=new_meaning,
            symbol_type=SymbolType.CONCEPT,
            related=symbols,
        )

        # Inherit properties from components
        if components:
            compound.emotional_valence = np.mean([c.emotional_valence for c in components])
            compound.emotional_arousal = np.mean([c.emotional_arousal for c in components])
            compound.confidence = np.mean([c.confidence for c in components]) * 0.8

        return compound

    def _cleanup_user_symbols(self, user_id: str):
        """Remove least used symbols to maintain limit"""
        user_dict = self.dictionaries[user_id]

        # Sort by frequency and recency
        symbols_sorted = sorted(user_dict.items(), key=lambda x: (x[1].frequency, x[1].last_used or 0))

        # Remove bottom 10%
        to_remove = max(1, len(symbols_sorted) // 10)
        for symbol, _ in symbols_sorted[:to_remove]:
            del user_dict[symbol]

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if self.embedding_model:
            # This would use the actual embedding model
            # For demo, return random embedding
            return np.random.randn(384)  # Standard embedding size
        return np.zeros(384)

    def _save_user_dictionary(self, user_id: str):
        """Save user's dictionary to disk"""
        user_file = self.storage_path / f"{user_id}.pkl"

        # Convert to serializable format
        data = {
            "symbols": self.dictionaries[user_id],
            "history": self.evolution_history.get(user_id, []),
        }

        with open(user_file, "wb") as f:
            pickle.dump(data, f)

    def _load_dictionaries(self):
        """Load all user dictionaries from disk"""
        for user_file in self.storage_path.glob("*.pkl"):
            user_id = user_file.stem

            try:
                with open(user_file, "rb") as f:
                    data = pickle.load(f)

                self.dictionaries[user_id] = data.get("symbols", {})

                # Rebuild evolution history
                if "history" in data:
                    for entry in data["history"]:
                        key = f"{user_id}:{entry.get('symbol', '')}"
                        self.evolution_history[key].append(entry)

            except Exception as e:
                print(f"Failed to load dictionary for {user_id}: {e}")

    def export_dictionary(self, user_id: str) -> dict[str, Any]:
        """Export user's dictionary as JSON"""
        user_dict = self.dictionaries.get(user_id, {})

        export = {
            "user_id": user_id,
            "symbols": [],
            "statistics": {
                "total_symbols": len(user_dict),
                "most_used": [],
                "most_stable": [],
                "recently_added": [],
            },
        }

        # Export symbols
        for symbol, personal_sym in user_dict.items():
            export["symbols"].append(
                {
                    "symbol": symbol,
                    "meaning": personal_sym.meaning,
                    "type": personal_sym.symbol_type.value,
                    "frequency": personal_sym.frequency,
                    "confidence": personal_sym.confidence,
                    "stability": personal_sym.stability,
                    "examples": personal_sym.examples,
                }
            )

        # Calculate statistics
        sorted_by_freq = sorted(user_dict.values(), key=lambda x: x.frequency, reverse=True)
        export["statistics"]["most_used"] = [{"symbol": s.symbol, "frequency": s.frequency} for s in sorted_by_freq[:5]]

        sorted_by_stability = sorted(user_dict.values(), key=lambda x: x.stability, reverse=True)
        export["statistics"]["most_stable"] = [
            {"symbol": s.symbol, "stability": s.stability} for s in sorted_by_stability[:5]
        ]

        sorted_by_recent = sorted(user_dict.values(), key=lambda x: x.created_at, reverse=True)
        export["statistics"]["recently_added"] = [
            {"symbol": s.symbol, "meaning": s.meaning} for s in sorted_by_recent[:5]
        ]

        return export

    def import_dictionary(self, user_id: str, data: dict[str, Any]):
        """Import user dictionary from JSON"""
        for symbol_data in data.get("symbols", []):
            self.add_symbol(
                user_id=user_id,
                symbol=symbol_data["symbol"],
                meaning=symbol_data["meaning"],
                symbol_type=SymbolType(symbol_data.get("type", "concept")),
                examples=symbol_data.get("examples", []),
                confidence=symbol_data.get("confidence", 0.5),
                stability=symbol_data.get("stability", 0.5),
            )


# Example usage
if __name__ == "__main__":
    # Create dictionary manager
    dictionary = PersonalSymbolDictionary()

    print("📚 Personal Symbol Dictionary Demo")
    print("=" * 40)

    user_id = "demo_user"

    # Add personal symbols
    symbol1 = dictionary.add_symbol(
        user_id=user_id,
        symbol="🌟",
        meaning="excellent work",
        symbol_type=SymbolType.EMOTION,
        examples=["🌟 Great job on the project!", "Your code is 🌟"],
    )
    print(f"Added symbol: {symbol1.symbol} = {symbol1.meaning}")

    symbol2 = dictionary.add_symbol(
        user_id=user_id,
        symbol="🔨",
        meaning="needs fixing",
        symbol_type=SymbolType.ACTION,
        examples=["This function 🔨", "🔨 the bug in line 42"],
    )
    print(f"Added symbol: {symbol2.symbol} = {symbol2.meaning}")

    # Interpret text with symbols
    text = "Your code is 🌟 but this part 🔨"
    interpretation = dictionary.interpret_symbols(user_id, text)
    print(f"\nOriginal: {interpretation['original']}")
    print(f"Translated: {interpretation['translated']}")
    print(f"Confidence: {interpretation['confidence']:.1%}")

    # Learn from usage
    dictionary.learn_from_usage(user_id=user_id, symbol="🌟", context="praising good code", success=True)
    print(f"\n🌟 confidence after positive feedback: {symbol1.confidence:.2f}")

    # Suggest symbols
    suggestions = dictionary.suggest_symbols(user_id=user_id, concept="problem", limit=3)
    print("\nSuggestions for 'problem':")
    for sym in suggestions:
        print(f"  • {sym.symbol}: {sym.meaning}")

    # Merge symbols
    compound = dictionary.merge_symbols(
        user_id=user_id, symbols=["🌟", "🔨"], new_symbol="🌟🔨", new_meaning="excellent fix"
    )
    print(f"\nCreated compound: {compound.symbol} = {compound.meaning}")

    # Export dictionary
    export = dictionary.export_dictionary(user_id)
    print("\nExported dictionary:")
    print(f"  Total symbols: {export['statistics']['total_symbols']}")
    print(f"  Most used: {export['statistics']['most_used']}")
