#!/usr/bin/env python3
"""
Enhanced GLYPH Engine with Universal Symbol Integration
========================================================
Core GLYPH engine deeply integrated with Universal Symbol Protocol,
providing the foundation for all symbolic communication in LUKHAS.

This replaces the basic glyph_engine.py with full multi-modal support.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, cast

from core.events.contracts import GlyphCreated, SymbolTranslated

# Import event system for integration
from core.events.typed_event_bus import get_typed_event_bus

# Import existing GLYPH components
from .glyph import EmotionVector, Glyph, GlyphFactory, GlyphType

# Import Universal Symbol Protocol
from .universal_symbol_protocol import (
    SymbolDomain,
    SymbolModality,
    SymbolTranslator,
    UniversalSymbol,
    UniversalSymbolProtocol,
)


class EnhancedGlyphEngine:
    """
    Enhanced GLYPH engine with full Universal Symbol Protocol integration.
    This is the core symbolic processing engine for all LUKHAS modules.
    """

    def __init__(self):
        """Initialize the enhanced GLYPH engine"""
        # Original GLYPH components
        self.factory = GlyphFactory()
        self._glyph_cache = {}

        # Universal Symbol Protocol
        self.universal_protocol = UniversalSymbolProtocol()
        self.translator = SymbolTranslator()

        # Event bus for system-wide integration
        self.event_bus = get_typed_event_bus()

        # Cross-module symbol registry
        self.global_symbol_registry = {}

        # Performance metrics
        self.stats = {
            "glyphs_created": 0,
            "symbols_translated": 0,
            "cross_module_links": 0,
            "compression_ratio": 1.0,
        }

    def encode_concept(
        self,
        concept: str,
        emotion: Optional[Dict[str, float]] = None,
        modalities: Optional[Set[SymbolModality]] = None,
        domains: Optional[Set[SymbolDomain]] = None,
        source_module: Optional[str] = None,
    ) -> UniversalSymbol:
        """
        Encode a concept into a Universal Symbol with GLYPH core.
        This is the primary interface for all LUKHAS modules.

        Args:
            concept: The concept to encode
            emotion: Optional emotional context
            modalities: Symbol modalities (defaults to TEXT)
            domains: Symbol domains (defaults to UNIVERSAL)
            source_module: Module creating the symbol (for tracking)

        Returns:
            UniversalSymbol that can be used across all systems
        """
        # Create base GLYPH using original logic
        emotion_vector = None
        if emotion:
            # Use robust parsing to ignore unknown keys
            try:
                emotion_vector = EmotionVector.from_dict(emotion)
            except Exception:
                emotion_vector = EmotionVector()

        # Determine GLYPH type based on concept
        if any(word in concept.lower() for word in ["remember", "memory", "recall"]):
            glyph = self.factory.create_memory_glyph(concept, emotion_vector)
        elif any(word in concept.lower() for word in ["feel", "emotion", "mood"]):
            glyph = self.factory.create_emotion_glyph(
                emotion_vector or EmotionVector(intensity=0.5)
            )
        elif any(
            word in concept.lower() for word in ["think", "consciousness", "aware"]
        ):
            glyph = Glyph(
                glyph_type=GlyphType.CAUSAL,
                symbol="🧠",
                emotion_vector=emotion_vector or EmotionVector(),
                semantic_tags={concept},
            )
        else:
            # Use factory with alias-compatible parameters
            glyph = self.factory.create_action_glyph(
                action_type=concept,
                parameters={},
                required_tier=1,
            )

        # Create Universal Symbol with GLYPH core
        symbol = self.universal_protocol.create_symbol(
            content=concept,
            modalities=modalities or {SymbolModality.TEXT},
            domains=domains or {SymbolDomain.UNIVERSAL},
            emotion=emotion,
        )
        symbol.core_glyph = glyph

        # Register globally for cross-module access
        self.global_symbol_registry[symbol.symbol_id] = {
            "symbol": symbol,
            "source_module": source_module or "unknown",
            "created_at": datetime.now(timezone.utc),
        }

        # Emit event for system-wide awareness
        if self.event_bus:
            # Fire-and-forget publish; tolerate absence of running loop
            event = GlyphCreated(
                glyph_id=glyph.id,
                symbol_id=symbol.symbol_id,
                concept=concept,
                source_module=source_module or "unknown",
            )
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.event_bus.publish(event))
            except RuntimeError:
                # No running loop; best-effort synchronous dispatch
                asyncio.run(self.event_bus.publish(event))

        self.stats["glyphs_created"] += 1

        return symbol

    def translate_for_module(
        self, symbol: UniversalSymbol, target_module: str
    ) -> UniversalSymbol:
        """
        Translate a symbol for optimal use by a specific module.

        Module-specific optimizations:
        - consciousness: CONSCIOUSNESS + EMOTIONAL modalities
        - memory: TEMPORAL + CAUSAL modalities
        - quantum: QUANTUM modality
        - colony: SOCIAL domain
        - dream: CREATIVE + EMOTIONAL domains
        """
        # Determine optimal modality/domain for target module
        module_preferences = {
            "consciousness": (
                {SymbolModality.CONSCIOUSNESS, SymbolModality.EMOTIONAL},
                {SymbolDomain.COGNITIVE, SymbolDomain.EMOTIONAL},
            ),
            "memory": (
                {SymbolModality.TEMPORAL, SymbolModality.CAUSAL},
                {SymbolDomain.MEMORY},
            ),
            "quantum": ({SymbolModality.QUANTUM}, {SymbolDomain.QUANTUM}),
            "colony": ({SymbolModality.TEXT}, {SymbolDomain.SOCIAL}),
            "dream": (
                {SymbolModality.VISUAL, SymbolModality.EMOTIONAL},
                {SymbolDomain.CREATIVE, SymbolDomain.EMOTIONAL},
            ),
            "governance": ({SymbolModality.TEXT}, {SymbolDomain.ETHICAL}),
        }

        if target_module in module_preferences:
            target_modalities, target_domains = module_preferences[target_module]

            # Translate to preferred modality
            primary_modality = list(target_modalities)[0]
            translated = self.translator.translate(
                symbol, primary_modality, list(target_domains)[0]
            )

            # Add all preferred modalities and domains
            translated.modalities = target_modalities
            translated.domains = target_domains

            # Emit translation event
            if self.event_bus:
                event = SymbolTranslated(
                    original_id=symbol.symbol_id,
                    translated_id=translated.symbol_id,
                    target_module=target_module,
                )
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self.event_bus.publish(event))
                except RuntimeError:
                    asyncio.run(self.event_bus.publish(event))

            self.stats["symbols_translated"] += 1

            return translated

        return symbol

    def create_cross_module_link(
        self,
        symbol1: UniversalSymbol,
        symbol2: UniversalSymbol,
        link_type: str = "causal",
    ):
        """
        Create a link between symbols from different modules.
        This enables cross-module communication and reasoning.
        """
        # Add causal links
        symbol1.causal_links.append(symbol2.symbol_id)
        symbol2.causal_links.append(symbol1.symbol_id)

        # Track in global registry
        if symbol1.symbol_id in self.global_symbol_registry:
            reg1 = self.global_symbol_registry[symbol1.symbol_id]
            if "links" not in reg1:
                reg1["links"] = []
            reg1["links"].append({"target": symbol2.symbol_id, "type": link_type})

        if symbol2.symbol_id in self.global_symbol_registry:
            reg2 = self.global_symbol_registry[symbol2.symbol_id]
            if "links" not in reg2:
                reg2["links"] = []
            reg2["links"].append({"target": symbol1.symbol_id, "type": link_type})

        self.stats["cross_module_links"] += 1

    def get_module_symbols(self, module_name: str) -> List[UniversalSymbol]:
        """Get all symbols created by a specific module"""
        module_symbols = []
        for _, reg_entry in self.global_symbol_registry.items():
            if reg_entry["source_module"] == module_name:
                module_symbols.append(reg_entry["symbol"])
        return module_symbols

    def compress_module_state(self, module_name: str) -> UniversalSymbol:
        """
        Compress all symbols from a module into a single meta-symbol.
        Useful for checkpointing and state transfer.
        """
        module_symbols = self.get_module_symbols(module_name)

        if not module_symbols:
            # Create empty state symbol
            return self.encode_concept(
                f"{module_name}_empty_state", source_module=module_name
            )

        # Compress using universal protocol
        compressed = self.universal_protocol.compress_symbols(module_symbols)
        compressed.metadata["module"] = module_name
        compressed.metadata["compression_time"] = datetime.now(timezone.utc).isoformat()

        # Update stats
        self.stats["compression_ratio"] = compressed.compression_ratio

        return compressed

    def expand_module_state(
        self, compressed_state: UniversalSymbol
    ) -> List[UniversalSymbol]:
        """
        Expand a compressed module state back to individual symbols.
        """
        return self.universal_protocol.expand_symbol(compressed_state)

    def find_related_symbols(
        self, query_symbol: UniversalSymbol, max_depth: int = 2
    ) -> Dict[str, List[UniversalSymbol]]:
        """
        Find symbols related to the query across all modules.
        Returns symbols grouped by module.
        """
        related_by_module = {}
        visited = set()

        def traverse(symbol: UniversalSymbol, depth: int):
            if depth > max_depth or symbol.symbol_id in visited:
                return

            visited.add(symbol.symbol_id)

            # Find similar symbols
            similar = self.universal_protocol.find_similar_symbols(
                symbol, threshold=0.7, max_results=10
            )

            for sim_symbol, _ in similar:
                # Find source module
                if sim_symbol.symbol_id in self.global_symbol_registry:
                    source_module = self.global_symbol_registry[sim_symbol.symbol_id][
                        "source_module"
                    ]

                    if source_module not in related_by_module:
                        related_by_module[source_module] = []

                    if sim_symbol not in related_by_module[source_module]:
                        related_by_module[source_module].append(sim_symbol)

                # Traverse causal links
                for link_id in sim_symbol.causal_links:
                    if link_id in self.universal_protocol.symbol_registry:
                        linked_symbol = self.universal_protocol.symbol_registry[link_id]
                        traverse(linked_symbol, depth + 1)

        traverse(query_symbol, 0)

        return related_by_module

    def create_cognitive_chain(
        self, concepts: List[str], source_module: str = "consciousness"
    ) -> List[UniversalSymbol]:
        """
        Create a chain of causally linked symbols representing a cognitive process.
        Used by consciousness and reasoning modules.
        """
        symbols: List[UniversalSymbol] = []
        for concept in concepts:
            # Determine domains based on concept type
            if "decide" in concept.lower() or "choose" in concept.lower():
                domains = {SymbolDomain.ETHICAL, SymbolDomain.COGNITIVE}
            elif "feel" in concept.lower() or "emotion" in concept.lower():
                domains = {SymbolDomain.EMOTIONAL}
            elif "remember" in concept.lower() or "recall" in concept.lower():
                domains = {SymbolDomain.MEMORY}
            else:
                domains = {SymbolDomain.COGNITIVE}

            symbol = self.encode_concept(
                concept,
                domains=domains,
                source_module=source_module,
            )
            symbols.append(symbol)

        # Create causal chain
        return self.universal_protocol.create_causal_chain(symbols)

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about symbol usage"""
        module_stats = {}

        # Count symbols per module
        for reg_entry in self.global_symbol_registry.values():
            module = reg_entry["source_module"]
            if module not in module_stats:
                module_stats[module] = {"count": 0, "links": 0}
            module_stats[module]["count"] += 1

            if "links" in reg_entry:
                module_stats[module]["links"] += len(reg_entry["links"])

        return {
            **self.stats,
            "total_symbols": len(self.global_symbol_registry),
            "modules_active": len(module_stats),
            "module_breakdown": module_stats,
            "cache_size": len(self._glyph_cache),
            "universal_symbols": len(self.universal_protocol.symbol_registry),
        }

    # Backward compatibility methods
    def decode_glyph(self, glyph_repr: str) -> Optional[Glyph]:
        """Backward compatibility with original GLYPH engine"""
        return self._glyph_cache.get(glyph_repr)

    def create_memory_glyph(
        self, memory_content: str, emotion: Optional[Dict[str, float]] = None
    ) -> Glyph:
        """Backward compatibility method"""
        symbol = self.encode_concept(
            memory_content,
            emotion=emotion,
            domains={SymbolDomain.MEMORY},
        )
        return cast(Glyph, symbol.core_glyph)

    def create_emotion_glyph(self, emotion: Dict[str, float]) -> Glyph:
        """Backward compatibility method"""
        symbol = self.encode_concept(
            "emotional_state",
            emotion=emotion,
            domains={SymbolDomain.EMOTIONAL},
        )
        return cast(Glyph, symbol.core_glyph)


# Global singleton instance
_enhanced_engine = None


def get_enhanced_glyph_engine() -> EnhancedGlyphEngine:
    """Get the global enhanced GLYPH engine instance"""
    global _enhanced_engine
    if _enhanced_engine is None:
        _enhanced_engine = EnhancedGlyphEngine()
    return _enhanced_engine


# Make enhanced engine the default
GlyphEngine = EnhancedGlyphEngine

__all__ = ["EnhancedGlyphEngine", "GlyphEngine", "get_enhanced_glyph_engine"]
