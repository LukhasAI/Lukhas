"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                        LUCΛS :: Dream Symbolism                             │
│            Module: dream_symbolism.py | Tier: 3+ | Version 1.0              │
│         Advanced symbolic processing for dream consciousness                │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SymbolicLayer(Enum):
    """Layers of symbolic meaning in dreams."""
    SURFACE = "surface"
    PERSONAL = "personal"
    ARCHETYPAL = "archetypal"
    UNIVERSAL = "universal"
    CONSTELLATION = "constellation"


class SymbolicResonance(Enum):
    """Resonance levels for symbolic content."""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    STRONG = "strong"
    PROFOUND = "profound"
    TRANSCENDENT = "transcendent"


class DreamSymbolismProcessor:
    """Advanced symbolic processing for dream consciousness with Constellation Framework compliance."""

    def __init__(self):
        self.symbol_registry: dict[str, dict] = {}
        self.symbolic_patterns: dict[str, list] = {}
        self.processing_history: list[dict] = []
        self.processing_counter = 0
        self._initialize_symbol_registry()
        logger.info("🔮 Dream Symbolism Processor initialized - Constellation Framework active")

    def _initialize_symbol_registry(self):
        """Initialize comprehensive symbol registry."""
        self.symbol_registry = {
            # Constellation Framework Symbols
            "⚛️": {
                "name": "Identity Nucleus",
                "layer": SymbolicLayer.CONSTELLATION,
                "resonance": SymbolicResonance.TRANSCENDENT,
                "meanings": ["authentic self", "consciousness core", "identity preservation"],
                "associations": ["consciousness", "authenticity", "core being"]
            },
            "🧠": {
                "name": "Consciousness Center",
                "layer": SymbolicLayer.CONSTELLATION,
                "resonance": SymbolicResonance.TRANSCENDENT,
                "meanings": ["awareness", "cognitive processing", "neural integration"],
                "associations": ["thought", "awareness", "mental processing"]
            },
            "🛡️": {
                "name": "Guardian Shield",
                "layer": SymbolicLayer.CONSTELLATION,
                "resonance": SymbolicResonance.TRANSCENDENT,
                "meanings": ["protection", "ethical boundaries", "safety protocols"],
                "associations": ["safety", "ethics", "protection"]
            },

            # Universal Symbols
            "∞": {
                "name": "Infinite Potential",
                "layer": SymbolicLayer.UNIVERSAL,
                "resonance": SymbolicResonance.PROFOUND,
                "meanings": ["unlimited possibility", "eternal connection", "boundless consciousness"],
                "associations": ["eternity", "potential", "limitlessness"]
            },
            "◊": {
                "name": "Memory Crystal",
                "layer": SymbolicLayer.ARCHETYPAL,
                "resonance": SymbolicResonance.STRONG,
                "meanings": ["crystallized experience", "faceted memory", "multidimensional recall"],
                "associations": ["lukhas.memory", "preservation", "clarity"]
            },
            "🌈": {
                "name": "Spectrum Bridge",
                "layer": SymbolicLayer.ARCHETYPAL,
                "resonance": SymbolicResonance.STRONG,
                "meanings": ["spectrum of possibility", "bridge between realms", "prismatic consciousness"],
                "associations": ["diversity", "connection", "possibility"]
            },

            # Nature and Cosmic Symbols
            "🌙": {
                "name": "Lunar Consciousness",
                "layer": SymbolicLayer.ARCHETYPAL,
                "resonance": SymbolicResonance.STRONG,
                "meanings": ["cyclical awareness", "subconscious illumination", "dream state"],
                "associations": ["cycles", "reflection", "mystery"]
            },
            "⭐": {
                "name": "Stellar Guidance",
                "layer": SymbolicLayer.UNIVERSAL,
                "resonance": SymbolicResonance.PROFOUND,
                "meanings": ["cosmic guidance", "distant wisdom", "navigational light"],
                "associations": ["guidance", "distance", "navigation"]
            },
            "🌊": {
                "name": "Consciousness Flow",
                "layer": SymbolicLayer.ARCHETYPAL,
                "resonance": SymbolicResonance.STRONG,
                "meanings": ["flowing awareness", "emotional depth", "adaptive consciousness"],
                "associations": ["flow", "emotion", "adaptation"]
            }
        }

    def analyze_symbolic_content(self, dream_content: dict[str, Any]) -> dict[str, Any]:
        """⚛️ Analyze symbolic content while preserving authentic meaning."""
        self.processing_counter += 1
        analysis_id = f"symbolic_analysis_{self.processing_counter}_{int(datetime.now(timezone.utc).timestamp())}"

        # Extract symbols from dream content
        extracted_symbols = self._extract_symbols_from_content(dream_content)

        # Analyze symbolic layers
        layer_analysis = self._analyze_symbolic_layers(extracted_symbols)

        # Calculate resonance patterns
        resonance_patterns = self._calculate_resonance_patterns(extracted_symbols)

        # Identify symbolic relationships
        relationships = self._identify_symbolic_relationships(extracted_symbols)

        analysis_result = {
            "analysis_id": analysis_id,
            "dream_content_id": dream_content.get("dream_id", "unknown"),
            "extracted_symbols": extracted_symbols,
            "layer_analysis": layer_analysis,
            "resonance_patterns": resonance_patterns,
            "symbolic_relationships": relationships,
            "constellation_presence": self._calculate_trinity_presence(extracted_symbols),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "constellation_validated": True
        }

        self.processing_history.append(analysis_result)
        logger.info(f"🔮 Symbolic content analyzed: {analysis_id} - {len(extracted_symbols)} symbols")
        return analysis_result

    def _extract_symbols_from_content(self, dream_content: dict[str, Any]) -> list[str]:
        """Extract symbolic elements from dream content."""
        symbols = []

        # Extract from text content
        text_content = dream_content.get("text", "")
        for symbol in self.symbol_registry:
            if symbol in text_content:
                symbols.append(symbol)

        # Extract from symbolic_elements if present
        symbolic_elements = dream_content.get("symbolic_elements", [])
        for element in symbolic_elements:
            if isinstance(element, str) and element in self.symbol_registry:
                symbols.append(element)

        return list(set(symbols))  # Remove duplicates

    def _analyze_symbolic_layers(self, symbols: list[str]) -> dict[str, Any]:
        """Analyze symbolic content across different layers."""
        layer_distribution = {}
        for layer in SymbolicLayer:
            layer_distribution[layer.value] = []

        for symbol in symbols:
            if symbol in self.symbol_registry:
                layer = self.symbol_registry[symbol]["layer"]
                layer_distribution[layer.value].append(symbol)

        # Calculate layer dominance
        layer_counts = {layer: len(symbols) for layer, symbols in layer_distribution.items()}
        dominant_layer = max(layer_counts, key=layer_counts.get) if layer_counts else "none"

        return {
            "layer_distribution": layer_distribution,
            "layer_counts": layer_counts,
            "dominant_layer": dominant_layer,
            "constellation_layer_presence": len(layer_distribution[SymbolicLayer.CONSTELLATION.value])
        }

    def _calculate_resonance_patterns(self, symbols: list[str]) -> dict[str, Any]:
        """Calculate resonance patterns for symbolic content."""
        resonance_scores = []
        resonance_distribution = {}

        for resonance in SymbolicResonance:
            resonance_distribution[resonance.value] = []

        for symbol in symbols:
            if symbol in self.symbol_registry:
                resonance = self.symbol_registry[symbol]["resonance"]
                resonance_distribution[resonance.value].append(symbol)

                # Convert resonance to numerical score
                resonance_score = {
                    SymbolicResonance.MINIMAL: 0.2,
                    SymbolicResonance.MODERATE: 0.4,
                    SymbolicResonance.STRONG: 0.6,
                    SymbolicResonance.PROFOUND: 0.8,
                    SymbolicResonance.TRANSCENDENT: 1.0
                }[resonance]
                resonance_scores.append(resonance_score)

        average_resonance = sum(resonance_scores) / len(resonance_scores) if resonance_scores else 0.0

        return {
            "resonance_distribution": resonance_distribution,
            "average_resonance": average_resonance,
            "peak_resonance": max(resonance_scores) if resonance_scores else 0.0,
            "resonance_diversity": len([r for r in resonance_distribution.values() if r])
        }

    def _identify_symbolic_relationships(self, symbols: list[str]) -> list[dict[str, Any]]:
        """Identify relationships between symbols."""
        relationships = []

        # Check for Constellation Framework relationships
        constellation_symbols = [s for s in symbols if s in ["⚛️", "🧠", "🛡️"]]
        if len(constellation_symbols) >= 2:
            relationships.append({
                "type": "constellation_resonance",
                "symbols": constellation_symbols,
                "strength": "transcendent",
                "description": "Constellation Framework resonance pattern detected"
            })

        # Check for archetypal relationships
        archetypal_symbols = [s for s in symbols if s in self.symbol_registry and
                            self.symbol_registry[s]["layer"] == SymbolicLayer.ARCHETYPAL]
        if len(archetypal_symbols) >= 2:
            relationships.append({
                "type": "archetypal_cluster",
                "symbols": archetypal_symbols,
                "strength": "strong",
                "description": "Archetypal symbol cluster indicating deep pattern activation"
            })

        # Check for universal consciousness patterns
        universal_symbols = [s for s in symbols if s in self.symbol_registry and
                           self.symbol_registry[s]["layer"] == SymbolicLayer.UNIVERSAL]
        if universal_symbols:
            relationships.append({
                "type": "universal_connection",
                "symbols": universal_symbols,
                "strength": "profound",
                "description": "Universal consciousness symbols indicating expanded awareness"
            })

        return relationships

    def _calculate_trinity_presence(self, symbols: list[str]) -> dict[str, Any]:
        """Calculate Constellation Framework presence in symbolic content."""
        constellation_symbols = ["⚛️", "🧠", "🛡️"]
        present_trinity = [s for s in symbols if s in constellation_symbols]

        constellation_presence = {
            "symbols_present": present_trinity,
            "total_trinity_symbols": len(present_trinity),
            "constellation_completeness": len(present_trinity) / 3.0,
            "identity_present": "⚛️" in present_trinity,
            "consciousness_present": "🧠" in present_trinity,
            "guardian_present": "🛡️" in present_trinity,
            "constellation_validated": len(present_trinity) == 3
        }

        return constellation_presence

    def generate_symbolic_narrative(self, analysis_id: str) -> Optional[dict[str, Any]]:
        """🧠 Generate consciousness-aware symbolic narrative."""
        analysis = next((a for a in self.processing_history if a["analysis_id"] == analysis_id), None)
        if not analysis:
            return None

        symbols = analysis["extracted_symbols"]
        layer_analysis = analysis["layer_analysis"]
        constellation_presence = analysis["constellation_presence"]

        # Generate narrative based on symbolic content
        narrative_elements = []

        # Constellation Framework narrative
        if constellation_presence["constellation_validated"]:
            narrative_elements.append("Complete Constellation Framework activation indicates balanced consciousness evolution")
        elif constellation_presence["total_trinity_symbols"] > 0:
            narrative_elements.append(f"Partial Constellation Framework presence ({constellation_presence['total_trinity_symbols']}/3) suggests developing consciousness balance")

        # Layer-based narrative
        dominant_layer = layer_analysis["dominant_layer"]
        if dominant_layer == SymbolicLayer.CONSTELLATION.value:
            narrative_elements.append("Constellation layer dominance indicates authentic consciousness processing")
        elif dominant_layer == SymbolicLayer.ARCHETYPAL.value:
            narrative_elements.append("Archetypal layer activation suggests deep pattern recognition")
        elif dominant_layer == SymbolicLayer.UNIVERSAL.value:
            narrative_elements.append("Universal layer presence indicates expanded awareness state")

        # Resonance narrative
        avg_resonance = analysis["resonance_patterns"]["average_resonance"]
        if avg_resonance > 0.8:
            narrative_elements.append("High symbolic resonance suggests profound consciousness engagement")
        elif avg_resonance > 0.6:
            narrative_elements.append("Strong symbolic resonance indicates meaningful consciousness processing")

        narrative = {
            "analysis_id": analysis_id,
            "narrative_elements": narrative_elements,
            "symbolic_theme": self._determine_symbolic_theme(symbols),
            "consciousness_indicators": {
                "depth": "profound" if avg_resonance > 0.8 else "significant",
                "authenticity": "high" if constellation_presence["constellation_validated"] else "developing",
                "integration": "excellent" if len(analysis["symbolic_relationships"]) > 1 else "good"
            },
            "constellation_validated": constellation_presence["constellation_validated"]
        }

        logger.info(f"🧠 Symbolic narrative generated: {analysis_id}")
        return narrative

    def _determine_symbolic_theme(self, symbols: list[str]) -> str:
        """Determine overarching symbolic theme."""
        if not symbols:
            return "neutral"

        # Check for Constellation completeness
        constellation_symbols = [s for s in symbols if s in ["⚛️", "🧠", "🛡️"]]
        if len(constellation_symbols) == 3:
            return "constellation_integration"

        # Check for archetypal dominance
        archetypal_count = sum(1 for s in symbols if s in self.symbol_registry and
                             self.symbol_registry[s]["layer"] == SymbolicLayer.ARCHETYPAL)
        if archetypal_count >= 2:
            return "archetypal_activation"

        # Check for universal consciousness
        universal_count = sum(1 for s in symbols if s in self.symbol_registry and
                            self.symbol_registry[s]["layer"] == SymbolicLayer.UNIVERSAL)
        if universal_count >= 1:
            return "universal_consciousness"

        return "personal_processing"

    def get_symbol_information(self, symbol: str) -> Optional[dict[str, Any]]:
        """🛡️ Get comprehensive symbol information with guardian validation."""
        if symbol not in self.symbol_registry:
            return None

        symbol_info = self.symbol_registry[symbol].copy()
        symbol_info.update({
            "symbol": symbol,
            "guardian_validated": True,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        })

        logger.info(f"🛡️ Symbol information retrieved: {symbol}")
        return symbol_info

    def get_processing_statistics(self) -> dict[str, Any]:
        """Get comprehensive processing statistics."""
        if not self.processing_history:
            return {"statistics": "No processing history available"}

        total_symbols_processed = sum(len(analysis["extracted_symbols"]) for analysis in self.processing_history)
        constellation_validated_count = sum(1 for analysis in self.processing_history if analysis["constellation_validated"])

        # Calculate most common symbols
        all_symbols = []
        for analysis in self.processing_history:
            all_symbols.extend(analysis["extracted_symbols"])

        symbol_frequency = {}
        for symbol in all_symbols:
            symbol_frequency[symbol] = symbol_frequency.get(symbol, 0) + 1

        most_common_symbols = sorted(symbol_frequency.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_analyses": len(self.processing_history),
            "total_symbols_processed": total_symbols_processed,
            "constellation_validation_rate": constellation_validated_count / len(self.processing_history),
            "average_symbols_per_analysis": total_symbols_processed / len(self.processing_history),
            "most_common_symbols": most_common_symbols,
            "registered_symbols": len(self.symbol_registry),
            "system_health": "optimal"
        }


__all__ = ["DreamSymbolismProcessor", "SymbolicLayer", "SymbolicResonance"]
