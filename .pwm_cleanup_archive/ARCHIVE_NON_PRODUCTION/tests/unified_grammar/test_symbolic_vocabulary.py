"""
Test suite for LUKHAS Unified Grammar Symbolic Vocabulary System.

Tests vocabulary definitions, validation, and usage patterns.
"""

import json
from pathlib import Path

import pytest

from symbolic.vocabularies import (
    bio_vocabulary,
    dream_vocabulary,
    get_symbol,
    identity_vocabulary,
    vision_vocabulary,
    voice_vocabulary,
)


class TestSymbolicVocabularyStructure:
    """Test vocabulary structure and schema compliance."""

    def test_vocabulary_schema(self):
        """Test all vocabularies follow the correct schema."""
        # Load bio vocabulary as example
        bio_vocab = bio_vocabulary.BIO_VOCABULARY

        for key, entry in bio_vocab.items():
            # Required fields
            assert "emoji" in entry, f"Missing emoji in {key}"
            assert "symbol" in entry, f"Missing symbol in {key}"
            assert "meaning" in entry, f"Missing meaning in {key}"
            assert "guardian_weight" in entry, f"Missing guardian_weight in {key}"

            # Symbol format: 3-4 chars + ◊
            assert entry["symbol"].endswith(
                "◊"
            ), f"Symbol must end with ◊: {entry['symbol']}"
            assert (
                4 <= len(entry["symbol"]) <= 5
            ), f"Symbol wrong length: {entry['symbol']}"

            # Guardian weight range
            assert (
                0.0 <= entry["guardian_weight"] <= 1.0
            ), f"Invalid guardian weight: {entry['guardian_weight']}"

            # Optional fields
            if "contexts" in entry:
                assert isinstance(
                    entry["contexts"], list
                ), f"Contexts must be list: {key}"

    def test_dream_vocabulary_completeness(self):
        """Test dream vocabulary has all required symbols."""
        # Check phase symbols
        assert hasattr(dream_vocabulary, "DREAM_PHASE_SYMBOLS")
        phases = dream_vocabulary.DREAM_PHASE_SYMBOLS

        required_phases = [
            "initiation",
            "pattern",
            "deep_symbolic",
            "creative",
            "integration",
        ]
        for phase in required_phases:
            assert phase in phases, f"Missing dream phase: {phase}"

        # Check type symbols
        assert hasattr(dream_vocabulary, "DREAM_TYPE_SYMBOLS")
        types = dream_vocabulary.DREAM_TYPE_SYMBOLS

        required_types = [
            "consolidation",
            "pattern",
            "creative",
            "ethical",
            "predictive",
        ]
        for dream_type in required_types:
            assert dream_type in types, f"Missing dream type: {dream_type}"

    def test_bio_vocabulary_completeness(self):
        """Test bio vocabulary has all required symbols."""
        bio_vocab = bio_vocabulary.BIO_VOCABULARY

        # Check for critical bio operations
        required_ops = ["heartbeat", "authenticate", "health_check", "biometric_scan"]
        for op in required_ops:
            assert op in bio_vocab, f"Missing bio operation: {op}"

        # Check biometric types
        assert hasattr(bio_vocabulary, "BIOMETRIC_SYMBOLS")
        biometrics = bio_vocabulary.BIOMETRIC_SYMBOLS

        required_biometrics = ["fingerprint", "face", "voice", "iris", "dna"]
        for biometric in required_biometrics:
            assert biometric in biometrics, f"Missing biometric type: {biometric}"


class TestSymbolicVocabularyUsage:
    """Test vocabulary usage patterns and helper functions."""

    def test_get_symbol_function(self):
        """Test the global get_symbol helper."""
        # Test valid symbols
        symbol = get_symbol("dream", "initiation")
        assert symbol == "🌅 Gentle Awakening"

        symbol = get_symbol("bio", "heartbeat")
        assert "💓" in symbol  # Should contain heart emoji

        # Test default fallback
        symbol = get_symbol("unknown", "unknown", "🤷")
        assert symbol == "🤷"

    def test_dream_helper_functions(self):
        """Test dream vocabulary helper functions."""
        # Test dream cycle start
        cycle_symbol = dream_vocabulary.dream_cycle_start("creative")
        assert "🌙" in cycle_symbol
        assert "Creative" in cycle_symbol or "Imagination" in cycle_symbol

        # Test phase transition
        transition = dream_vocabulary.dream_phase_transition("initiation", "pattern")
        assert "→" in transition
        assert "🌅" in transition  # initiation symbol
        assert "🔮" in transition  # pattern symbol

        # Test pattern discovery
        pattern = dream_vocabulary.pattern_discovered("temporal", 0.9)
        assert "🔥" in pattern  # High confidence
        assert "Time" in pattern or "⏰" in pattern

        # Test emotional context
        emotion = dream_vocabulary.emotional_context("joyful", 0.7)
        assert "⭐" in emotion  # Medium intensity
        assert "🌈" in emotion  # Joyful symbol

    def test_bio_helper_functions(self):
        """Test bio vocabulary helper functions."""
        # Test health status
        health = bio_vocabulary.health_status_symbol("excellent", 98)
        assert "💚" in health  # Excellent health

        health = bio_vocabulary.health_status_symbol("warning", 75)
        assert "💛" in health  # Warning

        # Test authentication result
        auth = bio_vocabulary.auth_result_symbol(True, 0.95)
        assert "✅" in auth or "🔐" in auth  # Success

        auth = bio_vocabulary.auth_result_symbol(False, 0.3)
        assert "❌" in auth or "🚫" in auth  # Failure

    def test_identity_vocabulary_tiers(self):
        """Test identity vocabulary tier symbols."""
        tiers = identity_vocabulary.TIER_SYMBOLS

        # All 5 tiers should exist
        for i in range(1, 6):
            assert i in tiers, f"Missing tier {i}"
            assert "Tier" in str(tiers[i]) or "◊" in str(tiers[i])

        # Test tier symbol helper
        tier_sym = identity_vocabulary.tier_symbol(3)
        assert "👤" in tier_sym or "T3◊" in tier_sym


class TestVocabularyIntegration:
    """Test vocabulary integration with modules."""

    @pytest.mark.asyncio
    async def test_vocabulary_in_module(self):
        """Test vocabulary usage in actual module."""
        from core_unified_grammar.dream.core import LucasDreamModule

        module = LucasDreamModule()
        await module.startup()

        # Module should use vocabulary for logging
        # This would be verified through log inspection in real test
        await module.shutdown()

    def test_vocabulary_serialization(self):
        """Test vocabularies can be serialized."""
        # Test a vocabulary can be JSON serialized
        bio_vocab = bio_vocabulary.BIO_VOCABULARY

        # Should be JSON serializable
        json_str = json.dumps(bio_vocab, indent=2)
        assert json_str

        # Can be loaded back
        loaded = json.loads(json_str)
        assert loaded == bio_vocab

    def test_vocabulary_uniqueness(self):
        """Test symbol uniqueness across vocabularies."""
        all_symbols = set()

        # Collect all symbols
        vocabularies = [
            bio_vocabulary.BIO_VOCABULARY,
            identity_vocabulary.IDENTITY_VOCABULARY,
            voice_vocabulary.VOICE_VOCABULARY,
            vision_vocabulary.VISION_VOCABULARY,
        ]

        for vocab in vocabularies:
            for entry in vocab.values():
                symbol = entry.get("symbol", "")
                if symbol:
                    # Symbols should be unique
                    assert symbol not in all_symbols, f"Duplicate symbol: {symbol}"
                    all_symbols.add(symbol)


class TestVocabularyDocumentation:
    """Test vocabulary documentation and examples."""

    def test_vocabulary_has_examples(self):
        """Test vocabularies include usage examples."""
        # Check dream vocabulary has examples
        dream_examples = dream_vocabulary.DREAM_NARRATIVES
        assert len(dream_examples) > 0

        # Check visual hints
        visual_hints = dream_vocabulary.VISUAL_HINTS
        assert len(visual_hints) > 0

        for phase, hints in visual_hints.items():
            assert len(hints) > 0, f"No visual hints for phase: {phase}"

    def test_vocabulary_readme_exists(self):
        """Test vocabulary documentation exists."""
        vocab_path = Path(
            "/Users/agi_dev/Downloads/Consolidation-Repo/lukhas/symbolic/vocabularies"
        )

        assert (vocab_path / "README.md").exists()
        assert (vocab_path / "VALUABLE_ASSET_NOTICE.md").exists()
        assert (vocab_path / "VOCABULARY_DEVELOPMENT_PLAN.md").exists()
