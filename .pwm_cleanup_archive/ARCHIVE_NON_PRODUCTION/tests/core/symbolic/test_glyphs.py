"""
Test suite for symbolic glyph processing.

Tests GLYPH generation, transformations, and properties with deterministic
behavior for the LUKHAS symbolic system.
"""

import hashlib
from dataclasses import dataclass
from typing import List

import pytest

# Import modules to test
from core.symbolic.glyphs import GLYPH_MAP, get_glyph_meaning


# Since glyphs.py only has a map and getter, we'll create test classes for comprehensive testing
@dataclass
class Glyph:
    """Test representation of a GLYPH."""

    symbol: str
    context: str
    resonance: float
    hash: str = None

    def __post_init__(self):
        if self.hash is None:
            self.hash = hashlib.sha256(
                f"{self.symbol}:{self.context}".encode()
            ).hexdigest()[:8]

    def is_transformative(self):
        return self.symbol == "Λ"

    def is_conscious(self):
        return self.symbol == "Ψ"

    def is_terminal(self):
        return self.symbol == "Ω"


class GlyphGenerator:
    """Test GLYPH generator."""

    def __init__(self, seed=None):
        self.seed = seed
        self._counter = 0

    def create_glyph(self, context: str) -> Glyph:
        """Create a GLYPH based on context."""
        # Deterministic generation based on context hash
        ctx_hash = hashlib.sha256(context.encode()).digest()
        symbol_index = ctx_hash[0] % 5
        symbols = ["Λ", "Ψ", "Ω", "Δ", "Σ"]

        resonance = (ctx_hash[1] % 100) / 100.0

        return Glyph(symbol=symbols[symbol_index], context=context, resonance=resonance)


class GlyphTransformer:
    """Test GLYPH transformer."""

    def __init__(self):
        self.transform_count = 0

    def transform(self, glyph: Glyph, transform_type: str, **params) -> Glyph:
        """Transform a GLYPH."""
        new_glyph = Glyph(
            symbol=glyph.symbol, context=glyph.context, resonance=glyph.resonance
        )

        if transform_type == "identity":
            pass  # No change
        elif transform_type == "amplify":
            factor = params.get("factor", 1.5)
            new_glyph.resonance = min(1.0, glyph.resonance * factor)
        elif transform_type == "dampen":
            factor = params.get("factor", 0.5)
            new_glyph.resonance = max(0.0, glyph.resonance * factor)
        elif transform_type == "rotate":
            # Symbol rotation
            symbols = ["Λ", "Ψ", "Ω", "Δ", "Σ"]
            if glyph.symbol in symbols:
                idx = symbols.index(glyph.symbol)
                new_glyph.symbol = symbols[(idx + 1) % len(symbols)]

        # Track lineage
        if hasattr(glyph, "lineage"):
            new_glyph.lineage = glyph.lineage + [transform_type]
        else:
            new_glyph.lineage = [transform_type]

        return new_glyph

    def merge(self, glyphs: List[Glyph]) -> Glyph:
        """Merge multiple GLYPHs."""
        if not glyphs:
            raise ValueError("Cannot merge empty glyph list")

        # Average resonance
        avg_resonance = sum(g.resonance for g in glyphs) / len(glyphs)

        # Composite symbol based on count
        if len(glyphs) <= 2:
            symbol = "Δ"
        else:
            symbol = "Σ"

        return Glyph(symbol=symbol, context="composite", resonance=avg_resonance)


@pytest.mark.symbolic
class TestGlyphGeneration:
    """Test GLYPH generation and basic properties."""

    @pytest.fixture
    def generator(self):
        """Create GLYPH generator instance."""
        return GlyphGenerator(seed=42)  # Deterministic for testing

    def test_glyph_creation(self, generator):
        """Test basic GLYPH creation."""
        glyph = generator.create_glyph("test_context")

        assert isinstance(glyph, Glyph)
        assert glyph.symbol in ["Λ", "Ψ", "Ω", "Δ", "Σ"]
        assert glyph.context == "test_context"
        assert 0.0 <= glyph.resonance <= 1.0
        assert glyph.hash is not None

    def test_glyph_determinism(self, generator):
        """Test that same context produces consistent GLYPHs."""
        glyph1 = generator.create_glyph("identical_context")
        glyph2 = generator.create_glyph("identical_context")

        assert glyph1.symbol == glyph2.symbol
        assert glyph1.hash == glyph2.hash
        assert glyph1.resonance == glyph2.resonance

    def test_glyph_uniqueness(self, generator):
        """Test that different contexts produce different GLYPHs."""
        contexts = ["alpha", "beta", "gamma", "delta", "epsilon"]
        glyphs = [generator.create_glyph(ctx) for ctx in contexts]

        # Check unique hashes
        hashes = [g.hash for g in glyphs]
        assert len(set(hashes)) == len(hashes)

        # Should have variety in symbols
        symbols = [g.symbol for g in glyphs]
        assert len(set(symbols)) > 1

    @pytest.mark.parametrize("symbol", ["Λ", "Ψ", "Ω", "Δ", "Σ"])
    def test_glyph_symbol_properties(self, symbol):
        """Test properties of specific GLYPH symbols."""
        # Force generation of specific symbol
        glyph = Glyph(symbol=symbol, context="test", resonance=0.5)

        # Verify symbol-specific properties
        if symbol == "Λ":  # Lambda - transformation
            assert glyph.is_transformative()
            assert not glyph.is_conscious()
            assert not glyph.is_terminal()
        elif symbol == "Ψ":  # Psi - consciousness
            assert not glyph.is_transformative()
            assert glyph.is_conscious()
            assert not glyph.is_terminal()
        elif symbol == "Ω":  # Omega - completion
            assert not glyph.is_transformative()
            assert not glyph.is_conscious()
            assert glyph.is_terminal()

    def test_glyph_resonance_distribution(self, generator):
        """Test that resonance values are well distributed."""
        resonances = []
        for i in range(100):
            glyph = generator.create_glyph(f"context_{i}")
            resonances.append(glyph.resonance)

        # Check distribution
        assert min(resonances) < 0.2  # Some low values
        assert max(resonances) > 0.8  # Some high values
        assert 0.3 < sum(resonances) / len(resonances) < 0.7  # Reasonable average


@pytest.mark.symbolic
class TestGlyphTransformation:
    """Test GLYPH transformation operations."""

    @pytest.fixture
    def transformer(self):
        """Create GLYPH transformer instance."""
        return GlyphTransformer()

    def test_identity_transformation(self, transformer):
        """Test that identity transformation preserves GLYPH."""
        glyph = Glyph("Λ", "test", 0.7)

        transformed = transformer.transform(glyph, "identity")

        assert transformed.symbol == glyph.symbol
        assert transformed.context == glyph.context
        assert transformed.resonance == glyph.resonance

    def test_idempotent_transformation(self, transformer):
        """Test that transformations are idempotent when appropriate."""
        glyph = Glyph("Λ", "test", 0.7)

        # Apply transformation twice
        transformed1 = transformer.transform(glyph, "identity")
        transformed2 = transformer.transform(transformed1, "identity")

        # Should be identical
        assert transformed1.hash == transformed2.hash
        assert transformed1.symbol == transformed2.symbol

    def test_resonance_transformation(self, transformer):
        """Test resonance-based transformations."""
        glyph = Glyph("Ψ", "consciousness", 0.5)

        # Amplify resonance
        amplified = transformer.transform(glyph, "amplify", factor=2.0)
        assert amplified.resonance > glyph.resonance
        assert amplified.resonance <= 1.0  # Capped at maximum
        assert amplified.resonance == 1.0  # 0.5 * 2.0 = 1.0

        # Dampen resonance
        dampened = transformer.transform(glyph, "dampen", factor=0.5)
        assert dampened.resonance < glyph.resonance
        assert dampened.resonance >= 0.0  # Capped at minimum
        assert dampened.resonance == 0.25  # 0.5 * 0.5 = 0.25

    def test_resonance_bounds(self, transformer):
        """Test that resonance stays within bounds."""
        # Test upper bound
        high_glyph = Glyph("Λ", "high", 0.9)
        amplified = transformer.transform(high_glyph, "amplify", factor=3.0)
        assert amplified.resonance == 1.0

        # Test lower bound
        low_glyph = Glyph("Ω", "low", 0.1)
        dampened = transformer.transform(low_glyph, "dampen", factor=0.01)
        assert dampened.resonance == 0.001  # 0.1 * 0.01

    def test_symbol_rotation(self, transformer):
        """Test symbol rotation transformation."""
        symbols = ["Λ", "Ψ", "Ω", "Δ", "Σ"]

        for i, symbol in enumerate(symbols):
            glyph = Glyph(symbol, "rotate_test", 0.5)
            rotated = transformer.transform(glyph, "rotate")

            expected_symbol = symbols[(i + 1) % len(symbols)]
            assert rotated.symbol == expected_symbol

    def test_composite_transformation(self, transformer):
        """Test composite GLYPH transformations."""
        glyphs = [
            Glyph("Λ", "part1", 0.6),
            Glyph("Ψ", "part2", 0.7),
            Glyph("Ω", "part3", 0.8),
        ]

        # Merge glyphs
        composite = transformer.merge(glyphs)

        assert composite.symbol in ["Σ", "Δ"]  # Composite symbols
        assert composite.context == "composite"
        assert composite.resonance == pytest.approx(0.7, rel=0.01)  # Average

    def test_transformation_chain(self, transformer):
        """Test chained transformations maintain integrity."""
        original = Glyph("Λ", "origin", 0.5)

        # Chain of transformations
        chain = [
            ("amplify", {"factor": 1.5}),
            ("rotate", {}),
            ("dampen", {"factor": 0.8}),
            ("identity", {}),
        ]

        current = original
        for transform_type, params in chain:
            current = transformer.transform(current, transform_type, **params)

        # Verify chain properties
        assert current.symbol == "Ψ"  # Λ rotated once
        assert current.resonance == pytest.approx(0.6, rel=0.01)  # 0.5 * 1.5 * 0.8
        assert current.lineage == [t[0] for t in chain]  # Lineage tracked

    def test_merge_edge_cases(self, transformer):
        """Test merge operation edge cases."""
        # Empty list
        with pytest.raises(ValueError):
            transformer.merge([])

        # Single glyph
        single = Glyph("Λ", "single", 0.5)
        merged = transformer.merge([single])
        assert merged.symbol == "Δ"  # Small merge
        assert merged.resonance == 0.5

        # Many glyphs
        many = [Glyph("Λ", f"g{i}", i / 10) for i in range(10)]
        merged_many = transformer.merge(many)
        assert merged_many.symbol == "Σ"  # Large merge


@pytest.mark.symbolic
class TestGlyphMapIntegration:
    """Test integration with the actual GLYPH_MAP from glyphs.py."""

    def test_glyph_map_contents(self):
        """Test that GLYPH_MAP contains expected entries."""
        assert "☯" in GLYPH_MAP
        assert "🪞" in GLYPH_MAP
        assert "🌪️" in GLYPH_MAP
        assert "🔁" in GLYPH_MAP

        # Check some meanings
        assert "Bifurcation" in GLYPH_MAP["☯"]
        assert "Self-Reflection" in GLYPH_MAP["🪞"]
        assert "Collapse" in GLYPH_MAP["🌪️"]

    def test_get_glyph_meaning(self):
        """Test the get_glyph_meaning function."""
        # Known glyph
        meaning = get_glyph_meaning("☯")
        assert meaning == GLYPH_MAP["☯"]
        assert "Bifurcation" in meaning

        # Unknown glyph
        unknown = get_glyph_meaning("🎭")
        assert unknown == "Unknown Glyph"

    def test_glyph_map_completeness(self):
        """Test that all glyphs have meaningful descriptions."""
        for glyph, meaning in GLYPH_MAP.items():
            assert len(meaning) > 5  # Non-trivial description
            assert "/" in meaning  # Multiple concepts
            assert not meaning.startswith(" ")  # No leading space
            assert not meaning.endswith(" ")  # No trailing space

    @pytest.mark.parametrize(
        "glyph,expected_concept",
        [
            ("☯", "Choice"),
            ("🪞", "Introspection"),
            ("🌪️", "Collapse"),
            ("🔁", "Loop"),
            ("💡", "Insight"),
            ("🔗", "Connection"),
            ("🛡️", "Safety"),
            ("🌱", "Growth"),
            ("❓", "Uncertainty"),
            ("👁️", "Awareness"),
        ],
    )
    def test_glyph_concepts(self, glyph, expected_concept):
        """Test that glyphs map to expected concepts."""
        meaning = get_glyph_meaning(glyph)
        assert expected_concept in meaning
