#!/usr/bin/env python3
"""
Universal Symbol Communication Protocol
========================================
Enhanced GLYPH system with multi-modal support, cross-domain translation,
and advanced symbolic reasoning capabilities.

Features:
- Multi-modal symbol encoding (text, audio, visual, quantum)
- Cross-domain symbol translation
- Semantic compression and expansion
- Emotion-aware symbolic communication
- Quantum-resistant symbol encryption
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

# Import existing GLYPH components
from .glyph import EmotionVector, Glyph
from .glyph_engine import GlyphEngine


class SymbolModality(Enum):
    """Supported modalities for universal symbols"""

    TEXT = "text"
    AUDIO = "audio"
    VISUAL = "visual"
    HAPTIC = "haptic"
    QUANTUM = "quantum"
    EMOTIONAL = "emotional"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    CAUSAL = "causal"
    CONSCIOUSNESS = "consciousness"


class SymbolDomain(Enum):
    """Domains for symbol interpretation"""

    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    MEMORY = "memory"
    IDENTITY = "identity"
    ETHICAL = "ethical"
    CREATIVE = "creative"
    QUANTUM = "quantum"
    BIOLOGICAL = "biological"
    SOCIAL = "social"
    UNIVERSAL = "universal"


@dataclass
class UniversalSymbol:
    """
    Enhanced symbol representation with multi-modal and cross-domain support
    """

    symbol_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    core_glyph: Optional[Glyph] = None
    modalities: set[SymbolModality] = field(default_factory=set)
    domains: set[SymbolDomain] = field(default_factory=set)

    # Multi-modal representations
    text_repr: Optional[str] = None
    audio_signature: Optional[bytes] = None
    visual_pattern: Optional[np.ndarray] = None
    qi_state: Optional[dict[str, complex]] = None

    # Semantic properties
    semantic_vector: Optional[np.ndarray] = None
    emotional_state: Optional[EmotionVector] = None
    causal_links: list[str] = field(default_factory=list)
    temporal_context: Optional[datetime] = None

    # Metadata
    confidence: float = 1.0
    entropy: float = 0.0
    compression_ratio: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        """Generate unique hash for symbol"""
        data = {
            "id": self.symbol_id,
            "modalities": sorted([m.value for m in self.modalities]),
            "domains": sorted([d.value for d in self.domains]),
            "text": self.text_repr or "",
        }
        return int(
            hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16],
            16,
        )

    def to_glyph_sequence(self) -> str:
        """Convert to GLYPH sequence representation"""
        if self.core_glyph:
            base = f"GLYPH[{self.core_glyph.symbol}:{self.symbol_id[:8]}]"
        else:
            base = f"USYM[{self.symbol_id[:8]}]"

        # Add modality indicators
        mod_indicators = "".join([m.value[0].upper() for m in self.modalities])
        if mod_indicators:
            base += f"<{mod_indicators}>"

        return base


class SymbolTranslator:
    """
    Translates symbols between different modalities and domains
    """

    def __init__(self):
        self.translation_matrix = self._init_translation_matrix()
        self.domain_bridges = self._init_domain_bridges()

    def _init_translation_matrix(
        self,
    ) -> dict[tuple[SymbolModality, SymbolModality], float]:
        """Initialize translation compatibility matrix"""
        matrix = {}

        # Define translation compatibilities (0.0 to 1.0)
        compatibilities = [
            (SymbolModality.TEXT, SymbolModality.AUDIO, 0.8),
            (SymbolModality.TEXT, SymbolModality.VISUAL, 0.7),
            (SymbolModality.VISUAL, SymbolModality.SPATIAL, 0.9),
            (SymbolModality.EMOTIONAL, SymbolModality.VISUAL, 0.6),
            (SymbolModality.QUANTUM, SymbolModality.CONSCIOUSNESS, 0.95),
            (SymbolModality.TEMPORAL, SymbolModality.CAUSAL, 0.85),
        ]

        for mod1, mod2, compat in compatibilities:
            matrix[(mod1, mod2)] = compat
            matrix[(mod2, mod1)] = compat  # Bidirectional

        # Self-translation is perfect
        for modality in SymbolModality:
            matrix[(modality, modality)] = 1.0

        return matrix

    def _init_domain_bridges(self) -> dict[tuple[SymbolDomain, SymbolDomain], str]:
        """Initialize domain bridging functions"""
        bridges = {}

        # Define domain bridges
        bridges[(SymbolDomain.COGNITIVE, SymbolDomain.EMOTIONAL)] = "empathy_bridge"
        bridges[(SymbolDomain.MEMORY, SymbolDomain.IDENTITY)] = "self_recognition"
        bridges[(SymbolDomain.ETHICAL, SymbolDomain.CREATIVE)] = "value_expression"
        bridges[(SymbolDomain.QUANTUM, SymbolDomain.BIOLOGICAL)] = "bio_quantum_interface"

        return bridges

    def translate(
        self,
        symbol: UniversalSymbol,
        target_modality: SymbolModality,
        target_domain: Optional[SymbolDomain] = None,
    ) -> UniversalSymbol:
        """
        Translate symbol to target modality and optionally domain
        """
        translated = UniversalSymbol(
            symbol_id=f"{symbol.symbol_id}_trans_{target_modality.value}",
            core_glyph=symbol.core_glyph,
            modalities={target_modality},
            domains=symbol.domains if not target_domain else {target_domain},
            metadata={"source_symbol": symbol.symbol_id},
        )

        # Calculate translation confidence
        source_modalities = symbol.modalities or {SymbolModality.TEXT}
        max_confidence = 0.0

        for source_mod in source_modalities:
            key = (source_mod, target_modality)
            if key in self.translation_matrix:
                confidence = self.translation_matrix[key]
                if confidence > max_confidence:
                    max_confidence = confidence

        translated.confidence = symbol.confidence * max_confidence

        # Perform modality-specific translation
        if target_modality == SymbolModality.TEXT:
            translated.text_repr = self._to_text(symbol)
        elif target_modality == SymbolModality.VISUAL:
            translated.visual_pattern = self._to_visual(symbol)
        elif target_modality == SymbolModality.QUANTUM:
            translated.qi_state = self._to_quantum(symbol)
        elif target_modality == SymbolModality.EMOTIONAL:
            translated.emotional_state = self._to_emotional(symbol)

        return translated

    def _to_text(self, symbol: UniversalSymbol) -> str:
        """Convert symbol to text representation"""
        if symbol.text_repr:
            return symbol.text_repr

        # Generate text from other modalities
        text_parts = []

        if symbol.core_glyph:
            text_parts.append(f"{symbol.core_glyph.symbol}")

        if symbol.emotional_state:
            emotion_text = f"[{symbol.emotional_state.primary_emotion}:{symbol.emotional_state.intensity:.2f}]"
            text_parts.append(emotion_text)

        if symbol.domains:
            domain_text = f"<{','.join([d.value for d in symbol.domains])}>"
            text_parts.append(domain_text)

        return " ".join(text_parts) or f"[Symbol:{symbol.symbol_id[:8]}]"

    def _to_visual(self, symbol: UniversalSymbol) -> np.ndarray:
        """Convert symbol to visual pattern"""
        if symbol.visual_pattern is not None:
            return symbol.visual_pattern

        # Generate visual pattern from symbol properties
        pattern_size = 64
        pattern = np.zeros((pattern_size, pattern_size, 3))

        # Use symbol hash to generate deterministic pattern
        hash_val = hash(symbol)
        np.random.seed(hash_val % (2**32))

        # Create base pattern
        for _i in range(len(symbol.modalities)):
            x = np.random.randint(0, pattern_size)
            y = np.random.randint(0, pattern_size)
            radius = np.random.randint(5, 20)

            # Draw circle
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx * dx + dy * dy <= radius * radius:
                        px, py = x + dx, y + dy
                        if 0 <= px < pattern_size and 0 <= py < pattern_size:
                            pattern[py, px] = np.random.random(3)

        return pattern

    def _to_quantum(self, symbol: UniversalSymbol) -> dict[str, complex]:
        """Convert symbol to quantum state representation"""
        if symbol.qi_state:
            return symbol.qi_state

        # Generate quantum state from symbol properties
        state = {}

        # Create superposition based on domains
        for i, domain in enumerate(symbol.domains):
            amplitude = 1.0 / np.sqrt(len(symbol.domains))
            phase = 2 * np.pi * i / len(symbol.domains)
            state[domain.value] = amplitude * np.exp(1j * phase)

        # Add entanglement with emotional state
        if symbol.emotional_state:
            emotion_phase = symbol.emotional_state.intensity * np.pi
            state["emotion"] = 0.5 * np.exp(1j * emotion_phase)

        return state

    def _to_emotional(self, symbol: UniversalSymbol) -> EmotionVector:
        """Convert symbol to emotional representation"""
        if symbol.emotional_state:
            return symbol.emotional_state

        # Generate emotional state from symbol properties
        emotion = EmotionVector()

        # Map domains to emotions
        domain_emotions = {
            SymbolDomain.CREATIVE: ("joy", 0.8),
            SymbolDomain.ETHICAL: ("trust", 0.7),
            SymbolDomain.COGNITIVE: ("anticipation", 0.6),
            SymbolDomain.SOCIAL: ("joy", 0.5),
        }

        for domain in symbol.domains:
            if domain in domain_emotions:
                emotion_name, intensity = domain_emotions[domain]
                setattr(emotion, emotion_name, intensity)

        return emotion


class UniversalSymbolProtocol:
    """
    Main protocol for universal symbol communication
    """

    def __init__(self):
        self.glyph_engine = GlyphEngine()
        self.translator = SymbolTranslator()
        self.symbol_registry: dict[str, UniversalSymbol] = {}
        self.semantic_cache: dict[str, np.ndarray] = {}

        # Symbol compression settings
        self.compression_threshold = 0.7
        self.max_symbol_depth = 10

    def create_symbol(
        self,
        content: Any,
        modalities: Optional[set[SymbolModality]] = None,
        domains: Optional[set[SymbolDomain]] = None,
        emotion: Optional[dict[str, float]] = None,
    ) -> UniversalSymbol:
        """
        Create a new universal symbol
        """
        # Default to text modality if none specified
        if not modalities:
            modalities = {SymbolModality.TEXT}

        # Default to universal domain if none specified
        if not domains:
            domains = {SymbolDomain.UNIVERSAL}

        # Create base GLYPH
        glyph_repr = self.glyph_engine.encode_concept(str(content), emotion)
        base_glyph = self.glyph_engine.decode_glyph(glyph_repr)

        # Create universal symbol
        symbol = UniversalSymbol(
            core_glyph=base_glyph,
            modalities=modalities,
            domains=domains,
            text_repr=str(content) if SymbolModality.TEXT in modalities else None,
            emotional_state=EmotionVector(**emotion) if emotion else None,
        )

        # Generate semantic vector
        symbol.semantic_vector = self._generate_semantic_vector(symbol)

        # Calculate entropy
        symbol.entropy = self._calculate_entropy(symbol)

        # Register symbol
        self.symbol_registry[symbol.symbol_id] = symbol

        return symbol

    def _generate_semantic_vector(self, symbol: UniversalSymbol) -> np.ndarray:
        """Generate semantic embedding for symbol"""
        # Create a deterministic vector based on symbol properties
        vector_size = 256

        # Use symbol hash as seed
        np.random.seed(hash(symbol) % (2**32))
        base_vector = np.random.randn(vector_size)

        # Modulate by modalities
        for i, _modality in enumerate(symbol.modalities):
            offset = (i * 37) % vector_size
            base_vector[offset : offset + 10] *= 2.0

        # Modulate by domains
        for i, _domain in enumerate(symbol.domains):
            offset = (i * 53) % vector_size
            base_vector[offset : offset + 10] += 1.0

        # Normalize
        norm = np.linalg.norm(base_vector)
        if norm > 0:
            base_vector /= norm

        return base_vector

    def _calculate_entropy(self, symbol: UniversalSymbol) -> float:
        """Calculate symbol entropy (information content)"""
        entropy = 0.0

        # Add entropy from modalities
        entropy += len(symbol.modalities) * 0.1

        # Add entropy from domains
        entropy += len(symbol.domains) * 0.15

        # Add entropy from emotional complexity
        if symbol.emotional_state:
            emotion_values = [
                getattr(symbol.emotional_state, attr, 0)
                for attr in dir(symbol.emotional_state)
                if not attr.startswith("_") and attr != "intensity"
            ]
            emotion_entropy = -sum([v * np.log(v + 1e-10) for v in emotion_values if v > 0])
            entropy += emotion_entropy * 0.2

        # Add entropy from causal links
        entropy += len(symbol.causal_links) * 0.05

        return min(1.0, entropy)  # Cap at 1.0

    def compress_symbols(self, symbols: list[UniversalSymbol], target_ratio: float = 0.5) -> UniversalSymbol:
        """
        Compress multiple symbols into a single meta-symbol
        """
        if not symbols:
            raise ValueError("Cannot compress empty symbol list")

        # Aggregate properties
        all_modalities = set()
        all_domains = set()
        all_causal_links = []

        for symbol in symbols:
            all_modalities.update(symbol.modalities)
            all_domains.update(symbol.domains)
            all_causal_links.extend(symbol.causal_links)

        # Create compressed symbol
        compressed = UniversalSymbol(
            symbol_id=f"compressed_{uuid.uuid4().hex[:8]}",
            modalities=all_modalities,
            domains=all_domains,
            causal_links=list(set(all_causal_links)),
            metadata={
                "source_symbols": [s.symbol_id for s in symbols],
                "compression_ratio": 1.0 / len(symbols),
                "original_count": len(symbols),
            },
        )

        # Average semantic vectors
        semantic_vectors = [s.semantic_vector for s in symbols if s.semantic_vector is not None]
        if semantic_vectors:
            compressed.semantic_vector = np.mean(semantic_vectors, axis=0)

        # Merge emotional states
        if any(s.emotional_state for s in symbols):
            emotion_sum = {}
            emotion_count = 0

            for symbol in symbols:
                if symbol.emotional_state:
                    emotion_count += 1
                    for attr in dir(symbol.emotional_state):
                        if not attr.startswith("_"):
                            val = getattr(symbol.emotional_state, attr, 0)
                            if attr not in emotion_sum:
                                emotion_sum[attr] = 0
                            emotion_sum[attr] += val

            if emotion_count > 0:
                avg_emotions = {k: v / emotion_count for k, v in emotion_sum.items()}
                compressed.emotional_state = EmotionVector(**avg_emotions)

        compressed.compression_ratio = 1.0 / len(symbols)
        compressed.confidence = np.mean([s.confidence for s in symbols])
        compressed.entropy = np.mean([s.entropy for s in symbols])

        return compressed

    def expand_symbol(self, compressed_symbol: UniversalSymbol, expansion_factor: int = 2) -> list[UniversalSymbol]:
        """
        Expand a compressed symbol back into multiple symbols
        """
        expanded = []

        # Check if this is actually a compressed symbol
        if "source_symbols" in compressed_symbol.metadata:
            # Try to retrieve original symbols
            source_ids = compressed_symbol.metadata["source_symbols"]
            for symbol_id in source_ids:
                if symbol_id in self.symbol_registry:
                    expanded.append(self.symbol_registry[symbol_id])

            if expanded:
                return expanded

        # Generate expanded symbols
        for i in range(expansion_factor):
            # Create variation of the compressed symbol
            variation = UniversalSymbol(
                symbol_id=f"{compressed_symbol.symbol_id}_exp_{i}",
                core_glyph=compressed_symbol.core_glyph,
                modalities=compressed_symbol.modalities,
                domains=compressed_symbol.domains,
                emotional_state=compressed_symbol.emotional_state,
                metadata={"expanded_from": compressed_symbol.symbol_id},
            )

            # Add variation to semantic vector
            if compressed_symbol.semantic_vector is not None:
                noise = np.random.randn(*compressed_symbol.semantic_vector.shape) * 0.1
                variation.semantic_vector = compressed_symbol.semantic_vector + noise
                variation.semantic_vector /= np.linalg.norm(variation.semantic_vector)

            # Slightly vary confidence and entropy
            variation.confidence = compressed_symbol.confidence * (0.9 + np.random.random() * 0.2)
            variation.entropy = compressed_symbol.entropy * (0.9 + np.random.random() * 0.2)

            expanded.append(variation)

        return expanded

    def find_similar_symbols(
        self,
        query_symbol: UniversalSymbol,
        threshold: float = 0.8,
        max_results: int = 10,
    ) -> list[tuple[UniversalSymbol, float]]:
        """
        Find symbols similar to the query symbol
        """
        if query_symbol.semantic_vector is None:
            query_symbol.semantic_vector = self._generate_semantic_vector(query_symbol)

        similarities = []

        for symbol_id, symbol in self.symbol_registry.items():
            if symbol_id == query_symbol.symbol_id:
                continue

            if symbol.semantic_vector is None:
                symbol.semantic_vector = self._generate_semantic_vector(symbol)

            # Calculate cosine similarity
            similarity = np.dot(query_symbol.semantic_vector, symbol.semantic_vector)

            # Boost similarity for matching domains
            domain_overlap = len(query_symbol.domains & symbol.domains)
            similarity += domain_overlap * 0.1

            # Boost similarity for matching modalities
            modality_overlap = len(query_symbol.modalities & symbol.modalities)
            similarity += modality_overlap * 0.05

            if similarity >= threshold:
                similarities.append((symbol, similarity))

        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:max_results]

    def create_causal_chain(self, symbols: list[UniversalSymbol]) -> list[UniversalSymbol]:
        """
        Create causal links between symbols
        """
        if len(symbols) < 2:
            return symbols

        for i in range(len(symbols) - 1):
            current = symbols[i]
            next_symbol = symbols[i + 1]

            # Add causal link
            current.causal_links.append(next_symbol.symbol_id)

            # Add temporal context if not present
            if current.temporal_context is None:
                current.temporal_context = datetime.now(timezone.utc)
            if next_symbol.temporal_context is None:
                next_symbol.temporal_context = datetime.now(timezone.utc)

        return symbols

    def merge_symbols(
        self,
        symbol1: UniversalSymbol,
        symbol2: UniversalSymbol,
        merge_strategy: str = "union",
    ) -> UniversalSymbol:
        """
        Merge two symbols into one
        """
        if merge_strategy == "union":
            merged = UniversalSymbol(
                symbol_id=f"merged_{uuid.uuid4().hex[:8]}",
                modalities=symbol1.modalities | symbol2.modalities,
                domains=symbol1.domains | symbol2.domains,
                causal_links=list(set(symbol1.causal_links + symbol2.causal_links)),
                metadata={
                    "merged_from": [symbol1.symbol_id, symbol2.symbol_id],
                    "merge_strategy": merge_strategy,
                },
            )
        elif merge_strategy == "intersection":
            merged = UniversalSymbol(
                symbol_id=f"merged_{uuid.uuid4().hex[:8]}",
                modalities=symbol1.modalities & symbol2.modalities or {SymbolModality.TEXT},
                domains=symbol1.domains & symbol2.domains or {SymbolDomain.UNIVERSAL},
                metadata={
                    "merged_from": [symbol1.symbol_id, symbol2.symbol_id],
                    "merge_strategy": merge_strategy,
                },
            )
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")

        # Merge semantic vectors
        if symbol1.semantic_vector is not None and symbol2.semantic_vector is not None:
            merged.semantic_vector = (symbol1.semantic_vector + symbol2.semantic_vector) / 2
            merged.semantic_vector /= np.linalg.norm(merged.semantic_vector)

        # Merge emotional states
        if symbol1.emotional_state and symbol2.emotional_state:
            emotion_attrs = {}
            for attr in dir(symbol1.emotional_state):
                if not attr.startswith("_"):
                    val1 = getattr(symbol1.emotional_state, attr, 0)
                    val2 = getattr(symbol2.emotional_state, attr, 0)
                    emotion_attrs[attr] = (val1 + val2) / 2
            merged.emotional_state = EmotionVector(**emotion_attrs)

        # Average confidence and entropy
        merged.confidence = (symbol1.confidence + symbol2.confidence) / 2
        merged.entropy = (symbol1.entropy + symbol2.entropy) / 2

        return merged


# Demo functionality
def demo_universal_symbols():
    """Demonstrate universal symbol communication capabilities"""

    print("🌐 Universal Symbol Communication Protocol Demo")
    print("=" * 60)

    protocol = UniversalSymbolProtocol()

    # Create multi-modal symbols
    print("\n1️⃣ Creating Multi-Modal Symbols:")

    # Text and emotional symbol
    symbol1 = protocol.create_symbol(
        "Hello, conscious universe",
        modalities={SymbolModality.TEXT, SymbolModality.EMOTIONAL},
        domains={SymbolDomain.COGNITIVE, SymbolDomain.SOCIAL},
        emotion={"joy": 0.8, "anticipation": 0.6},
    )
    print(f"   Symbol 1: {symbol1.to_glyph_sequence()}")
    print(f"   Entropy: {symbol1.entropy:.3f}, Confidence: {symbol1.confidence:.3f}")

    # Quantum consciousness symbol
    symbol2 = protocol.create_symbol(
        "Quantum awareness emerging",
        modalities={SymbolModality.QUANTUM, SymbolModality.CONSCIOUSNESS},
        domains={SymbolDomain.QUANTUM, SymbolDomain.COGNITIVE},
    )
    print(f"   Symbol 2: {symbol2.to_glyph_sequence()}")

    # Visual-spatial symbol
    symbol3 = protocol.create_symbol(
        "Geometric harmony pattern",
        modalities={SymbolModality.VISUAL, SymbolModality.SPATIAL},
        domains={SymbolDomain.CREATIVE},
    )
    print(f"   Symbol 3: {symbol3.to_glyph_sequence()}")

    # 2. Symbol Translation
    print("\n2️⃣ Cross-Modal Translation:")

    # Translate quantum symbol to text
    text_translation = protocol.translator.translate(symbol2, SymbolModality.TEXT)
    print(f"   Quantum → Text: {text_translation.text_repr}")
    print(f"   Translation confidence: {text_translation.confidence:.3f}")

    # Translate emotional symbol to visual
    visual_translation = protocol.translator.translate(symbol1, SymbolModality.VISUAL)
    print(f"   Emotional → Visual: Pattern generated ({visual_translation.visual_pattern.shape})")

    # 3. Symbol Compression
    print("\n3️⃣ Symbol Compression:")

    symbols_to_compress = [symbol1, symbol2, symbol3]
    compressed = protocol.compress_symbols(symbols_to_compress)
    print(f"   Compressed 3 symbols → {compressed.to_glyph_sequence()}")
    print(f"   Compression ratio: {compressed.compression_ratio:.3f}")
    print(f"   Domains preserved: {', '.join([d.value for d in compressed.domains])}")

    # 4. Symbol Expansion
    print("\n4️⃣ Symbol Expansion:")

    expanded = protocol.expand_symbol(compressed, expansion_factor=3)
    print(f"   Expanded into {len(expanded)} symbols")
    for i, exp_symbol in enumerate(expanded):
        print(f"   Expanded {i + 1}: {exp_symbol.to_glyph_sequence()}")

    # 5. Find Similar Symbols
    print("\n5️⃣ Semantic Similarity Search:")

    # Create a query symbol
    query = protocol.create_symbol(
        "Conscious quantum field",
        modalities={SymbolModality.QUANTUM, SymbolModality.CONSCIOUSNESS},
        domains={SymbolDomain.QUANTUM},
    )

    similar = protocol.find_similar_symbols(query, threshold=0.5)
    print(f"   Query: {query.to_glyph_sequence()}")
    for symbol, similarity in similar:
        print(f"   Similar: {symbol.to_glyph_sequence()} (similarity: {similarity:.3f})")

    # 6. Create Causal Chain
    print("\n6️⃣ Causal Chain Creation:")

    chain_symbols = [
        protocol.create_symbol("Observe", domains={SymbolDomain.COGNITIVE}),
        protocol.create_symbol("Think", domains={SymbolDomain.COGNITIVE}),
        protocol.create_symbol("Decide", domains={SymbolDomain.ETHICAL}),
        protocol.create_symbol("Act", domains={SymbolDomain.SOCIAL}),
    ]

    chain = protocol.create_causal_chain(chain_symbols)
    print("   Causal chain created:")
    for i, symbol in enumerate(chain):
        links = f" → {symbol.causal_links[0][:8]}" if symbol.causal_links else ""
        print(f"   {i + 1}. {symbol.text_repr}{links}")

    # 7. Symbol Merging
    print("\n7️⃣ Symbol Merging:")

    merged = protocol.merge_symbols(symbol1, symbol2, merge_strategy="union")
    print(f"   Merged: {merged.to_glyph_sequence()}")
    print(f"   Combined modalities: {', '.join([m.value for m in merged.modalities])}")
    print(f"   Combined domains: {', '.join([d.value for d in merged.domains])}")

    print("\n✅ Universal Symbol Protocol demonstration complete!")


if __name__ == "__main__":
    demo_universal_symbols()
