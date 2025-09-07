#!/usr/bin/env python3
"""
Symbol Generator for ΛLens
Converts parsed content into GLYPH symbols
"""
import streamlit as st

import math
from typing import Any

from .glyph_types import GlyphSymbol, SymbolType


class SymbolGenerator:
    """Generates GLYPH symbols from parsed content"""

    def __init__(self):
        self.symbol_cache = {}

    async def generate(self, content: dict, symbol_style: str = "modern", max_symbols: int = 1000) -> list[GlyphSymbol]:
        """Generate symbols from parsed content"""
        symbols = []

        # Extract symbols based on content type
        if "text" in content:
            symbols.extend(await self._extract_text_symbols(content["text"]))
        if "code" in content:
            symbols.extend(await self._extract_code_symbols(content["code"]))
        if "data" in content:
            symbols.extend(await self._extract_data_symbols(content["data"]))

        # Apply symbol style transformations
        symbols = await self._apply_style(symbols, symbol_style)

        # Limit number of symbols
        if len(symbols) > max_symbols:
            # Prioritize by confidence
            symbols.sort(key=lambda s: s.confidence, reverse=True)
            symbols = symbols[:max_symbols]

        # Assign 3D positions for AR/VR
        self._assign_positions(symbols)

        return symbols

    async def _extract_text_symbols(self, text: str) -> list[GlyphSymbol]:
        """Extract symbols from text content"""
        symbols = []

        # Split into paragraphs
        paragraphs = text.split("\n\n")

        for i, para in enumerate(paragraphs[:10]):  # Limit to first 10
            if para.strip():
                # Create document symbol
                symbol = GlyphSymbol.create(
                    symbol_type=SymbolType.DOCUMENT,
                    content=para[:200],  # Truncate long paragraphs
                    metadata={"index": i, "length": len(para), "word_count": len(para.split())},
                    confidence=0.8,
                )
                symbols.append(symbol)

                # Extract key concepts (simple keyword extraction)
                concepts = self._extract_key_concepts(para)
                for concept in concepts:
                    concept_symbol = GlyphSymbol.create(
                        symbol_type=SymbolType.CONCEPT,
                        content=concept,
                        metadata={"source_paragraph": i},
                        confidence=0.6,
                    )
                    symbols.append(concept_symbol)

        return symbols

    async def _extract_code_symbols(self, code: str) -> list[GlyphSymbol]:
        """Extract symbols from code content"""
        symbols = []

        # Extract functions/classes (simplified)
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("def ") or line.strip().startswith("class "):
                # Determine symbol type
                symbol_type = SymbolType.CODE
                if "def " in line:
                    symbol_type = SymbolType.PROCESS  # Functions as processes

                symbol = GlyphSymbol.create(
                    symbol_type=symbol_type,
                    content=line.strip(),
                    metadata={"line_number": i + 1, "language": self._detect_language_from_code(code)},
                    confidence=0.9,
                )
                symbols.append(symbol)

        return symbols

    async def _extract_data_symbols(self, data: Any) -> list[GlyphSymbol]:
        """Extract symbols from data content"""
        symbols = []

        if isinstance(data, dict):
            for key, value in data.items():
                symbol = GlyphSymbol.create(
                    symbol_type=SymbolType.DATA,
                    content=f"{key}: {str(value}[:100]}",
                    metadata={"key": key, "type": type(value).__name__, "value_preview": str(value)[:50]},
                    confidence=0.7,
                )
                symbols.append(symbol)

        elif isinstance(data, list):
            # Create summary symbol for arrays
            symbol = GlyphSymbol.create(
                symbol_type=SymbolType.DATA,
                content=f"Array with {len(data} items",
                metadata={"length": len(data), "item_types": list(set(type(item).__name__ for item in data[:10]))},
                confidence=0.8,
            )
            symbols.append(symbol)

        return symbols

    async def _apply_style(self, symbols: list[GlyphSymbol], style: str) -> list[GlyphSymbol]:
        """Apply visual style to symbols"""
        if style == "modern":
            # Modern style: clean, minimal
            for symbol in symbols:
                symbol.metadata["style"] = "modern"
                symbol.metadata["icon"] = self._get_modern_icon(symbol.type)

        elif style == "classic":
            # Classic style: traditional symbols
            for symbol in symbols:
                symbol.metadata["style"] = "classic"
                symbol.metadata["icon"] = self._get_classic_icon(symbol.type)

        return symbols

    def _get_modern_icon(self, symbol_type: SymbolType) -> str:
        """Get modern icon for symbol type"""
        icon_map = {
            SymbolType.DOCUMENT: "📄",
            SymbolType.CODE: "💻",
            SymbolType.DATA: "📊",
            SymbolType.CONCEPT: "💡",
            SymbolType.ENTITY: "👤",
            SymbolType.RELATIONSHIP: "🔗",
            SymbolType.WARNING: "⚠️",
            SymbolType.SUCCESS: "✅",
            SymbolType.PROCESS: "🔄",
            SymbolType.GLYPH: "🔮",
        }
        return icon_map.get(symbol_type, "🔮")

    def _get_classic_icon(self, symbol_type: SymbolType) -> str:
        """Get classic icon for symbol type"""
        icon_map = {
            SymbolType.DOCUMENT: "📜",
            SymbolType.CODE: "⚙️",
            SymbolType.DATA: "📈",
            SymbolType.CONCEPT: "💭",
            SymbolType.ENTITY: "👥",
            SymbolType.RELATIONSHIP: "⟷",
            SymbolType.WARNING: "🚨",
            SymbolType.SUCCESS: "✔️",
            SymbolType.PROCESS: "⚡",
            SymbolType.GLYPH: "✨",
        }
        return icon_map.get(symbol_type, "✨")

    def _extract_key_concepts(self, text: str) -> list[str]:
        """Extract key concepts from text (simple implementation)"""
        # Simple keyword extraction - in production use NLP
        words = text.lower().split()
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}

        # Filter out short words and stop words
        concepts = [word for word in words if len(word) > 4 and word not in stop_words]

        # Return unique concepts
        return list(set(concepts))[:5]  # Limit to 5 concepts

    def _detect_language_from_code(self, code: str) -> str:
        """Detect programming language from code content"""
        code_lower = code.lower()

        if "def " in code_lower or "import " in code_lower:
            return "python"
        elif "function" in code_lower or "const " in code_lower:
            return "javascript"
        elif "public class" in code_lower or "system.out" in code_lower:
            return "java"
        else:
            return "unknown"

    def _assign_positions(self, symbols: list[GlyphSymbol]):
        """Assign 3D positions for AR/VR rendering"""
        if not symbols:
            return

        # Arrange symbols in a sphere for 3D visualization
        num_symbols = len(symbols)

        # Golden ratio for even distribution
        golden_ratio = (1 + math.sqrt(5)) / 2

        for i, symbol in enumerate(symbols):
            # Calculate spherical coordinates
            theta = 2 * math.pi * i / golden_ratio
            phi = math.acos(1 - 2 * (i + 0.5) / num_symbols)

            # Convert to Cartesian coordinates
            radius = 5.0  # Base radius
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)

            symbol.set_position(x, y, z)
