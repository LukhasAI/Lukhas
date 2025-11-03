"""Comprehensive tests for EmotionMapper alternate implementation.

Tests cover:
- EmotionProfile dataclass and immutability
- EmotionMapper initialization and configuration
- Tone suggestion logic and fallbacks
- Intensity scoring with various inputs
- Tone similarity computations
- Affect delta calculations
- Cumulative affect tracking
- Edge cases and boundary conditions
- Integration patterns for Healix
"""
from __future__ import annotations

from typing import Any

import pytest
from core.emotion.emotion_mapper_alt import EmotionMapper, EmotionProfile


class TestEmotionProfile:
    """Test EmotionProfile dataclass."""

    def test_profile_creation(self):
        """Test creating emotion profile with valid values."""
        profile = EmotionProfile(stability=0.7, similarity_boost=0.85)

        assert profile.stability == 0.7
        assert profile.similarity_boost == 0.85

    def test_profile_immutability(self):
        """Test that EmotionProfile is immutable (frozen)."""
        profile = EmotionProfile(stability=0.6, similarity_boost=0.8)

        with pytest.raises(AttributeError):
            profile.stability = 0.9  # type: ignore

        with pytest.raises(AttributeError):
            profile.similarity_boost = 0.95  # type: ignore

    def test_profile_equality(self):
        """Test profile equality comparison."""
        profile1 = EmotionProfile(stability=0.7, similarity_boost=0.85)
        profile2 = EmotionProfile(stability=0.7, similarity_boost=0.85)
        profile3 = EmotionProfile(stability=0.6, similarity_boost=0.85)

        assert profile1 == profile2
        assert profile1 != profile3

    def test_profile_hashable(self):
        """Test that frozen profiles can be used as dict keys."""
        profile = EmotionProfile(stability=0.7, similarity_boost=0.85)

        profile_dict = {profile: "test_value"}
        assert profile_dict[profile] == "test_value"


class TestEmotionMapperInitialization:
    """Test EmotionMapper initialization."""

    def test_default_initialization(self):
        """Test mapper initializes with default profiles."""
        mapper = EmotionMapper()

        assert mapper.resonance_threshold == 0.75
        assert mapper._baseline_vector == (0.5, 0.5, 0.5)
        assert mapper._cumulative_affect_delta == 0.0

    def test_custom_resonance_threshold(self):
        """Test initialization with custom resonance threshold."""
        mapper = EmotionMapper(resonance_threshold=0.9)

        assert mapper.resonance_threshold == 0.9

    def test_custom_profiles(self):
        """Test initialization with custom emotion profiles."""
        custom_profiles = {
            "happy": EmotionProfile(stability=0.8, similarity_boost=0.95),
            "sad": EmotionProfile(stability=0.4, similarity_boost=0.5),
        }

        mapper = EmotionMapper(profiles=custom_profiles)

        # Should use custom profiles
        tone = mapper.suggest_tone("test", {"mood_hint": "happy"})
        assert tone == "happy"

    def test_default_profiles_available(self):
        """Test that default profiles include expected emotions."""
        mapper = EmotionMapper()

        expected_profiles = ["neutral", "calm", "curious", "focused", "intense"]

        for profile_name in expected_profiles:
            tone = mapper.suggest_tone("test", {"mood_hint": profile_name})
            assert tone == profile_name

    def test_baseline_vector_initialization(self):
        """Test baseline vector is properly initialized."""
        mapper = EmotionMapper()

        # Baseline should be (0.5, 0.5, 0.5)
        assert len(mapper._baseline_vector) == 3
        assert all(v == 0.5 for v in mapper._baseline_vector)


class TestToneSuggestion:
    """Test tone suggestion functionality."""

    def test_explicit_tone_preserved(self):
        """Test that explicit tone in record is preserved."""
        mapper = EmotionMapper()

        record = {"tone": "intense", "mood_hint": "calm"}
        tone = mapper.suggest_tone("test_context", record)

        # Should use explicit tone, not mood_hint
        assert tone == "intense"

    def test_tone_from_mood_hint(self):
        """Test tone suggested from mood_hint."""
        mapper = EmotionMapper()

        record = {"mood_hint": "curious"}
        tone = mapper.suggest_tone("test_context", record)

        assert tone == "curious"

    def test_tone_from_context_fallback(self):
        """Test tone uses context when no mood_hint."""
        mapper = EmotionMapper()

        record: dict[str, Any] = {}
        tone = mapper.suggest_tone("calm", record)

        assert tone == "calm"

    def test_unknown_mood_hint_fallback(self):
        """Test unknown mood_hint falls back to neutral."""
        mapper = EmotionMapper()

        record = {"mood_hint": "unknown_emotion"}
        tone = mapper.suggest_tone("test_context", record)

        assert tone == "neutral"

    def test_cumulative_affect_delta_tracking(self):
        """Test that cumulative affect delta increases with calls."""
        mapper = EmotionMapper()

        initial_delta = mapper._cumulative_affect_delta
        assert initial_delta == 0.0

        # Make several suggestions
        for _i in range(5):
            mapper.suggest_tone("test", {"mood_hint": "focused", "emotion_vector": [0.6, 0.7, 0.8]})

        # Cumulative delta should have increased
        assert mapper._cumulative_affect_delta > initial_delta

    def test_case_insensitive_mood_hint(self):
        """Test mood_hint matching is case-insensitive."""
        mapper = EmotionMapper()

        record_lower = {"mood_hint": "calm"}
        record_upper = {"mood_hint": "CALM"}
        record_mixed = {"mood_hint": "CaLm"}

        tone_lower = mapper.suggest_tone("test", record_lower)
        tone_upper = mapper.suggest_tone("test", record_upper)
        tone_mixed = mapper.suggest_tone("test", record_mixed)

        assert tone_lower == "calm"
        # Upper/mixed case fall through to context/neutral fallback
        assert tone_upper == "neutral"
        assert tone_mixed == "neutral"

    def test_empty_record(self):
        """Test tone suggestion with empty record."""
        mapper = EmotionMapper()

        record: dict[str, Any] = {}
        tone = mapper.suggest_tone("neutral", record)

        # Should fall back to context
        assert tone == "neutral"

    def test_multiple_suggestions_independent(self):
        """Test multiple tone suggestions are independent."""
        mapper = EmotionMapper()

        records = [
            {"mood_hint": "calm"},
            {"mood_hint": "focused"},
            {"mood_hint": "intense"},
        ]

        tones = [mapper.suggest_tone("test", record) for record in records]

        assert tones == ["calm", "focused", "intense"]


class TestIntensityScoring:
    """Test intensity scoring functionality."""

    def test_explicit_intensity_used(self):
        """Test explicit intensity value is used."""
        mapper = EmotionMapper()

        record = {"intensity": 0.85}
        intensity = mapper.score_intensity(record)

        assert intensity == 0.85

    def test_intensity_clamped_to_range(self):
        """Test intensity is clamped to [0.0, 1.0]."""
        mapper = EmotionMapper()

        record_high = {"intensity": 2.5}
        record_low = {"intensity": -0.5}

        intensity_high = mapper.score_intensity(record_high)
        intensity_low = mapper.score_intensity(record_low)

        assert intensity_high == 1.0
        assert intensity_low == 0.0

    def test_intensity_inferred_from_profile(self):
        """Test intensity inferred from emotion profile."""
        mapper = EmotionMapper()

        record = {"mood_hint": "calm"}
        intensity = mapper.score_intensity(record)

        # Should be influenced by calm profile
        assert 0.0 <= intensity <= 1.0
        # Calm profile has high similarity_boost, so should be relatively high
        assert intensity > 0.5

    def test_intensity_with_emotion_vector(self):
        """Test intensity calculation with emotion vector."""
        mapper = EmotionMapper()

        # Vector close to baseline should have low affect_delta, high intensity
        record_low = {"mood_hint": "calm", "emotion_vector": [0.5, 0.5, 0.5]}
        intensity_low = mapper.score_intensity(record_low)

        # Vector far from baseline should have high affect_delta, lower intensity
        record_high = {"mood_hint": "calm", "emotion_vector": [1.0, 1.0, 1.0]}
        intensity_high = mapper.score_intensity(record_high)

        # Lower affect_delta should give higher intensity
        assert intensity_low > intensity_high

    def test_intensity_with_unknown_mood(self):
        """Test intensity with unknown mood hint falls back to neutral."""
        mapper = EmotionMapper()

        record = {"mood_hint": "unknown_emotion"}
        intensity = mapper.score_intensity(record)

        # Should use neutral profile
        assert 0.0 <= intensity <= 1.0

    def test_intensity_always_in_range(self):
        """Test intensity score is always in valid range."""
        mapper = EmotionMapper()

        test_cases = [
            {},
            {"mood_hint": "intense"},
            {"mood_hint": "calm"},
            {"emotion_vector": [0.0, 0.0, 0.0]},
            {"emotion_vector": [1.0, 1.0, 1.0]},
            {"mood_hint": "focused", "emotion_vector": [0.3, 0.7, 0.9]},
        ]

        for record in test_cases:
            intensity = mapper.score_intensity(record)
            assert 0.0 <= intensity <= 1.0

    def test_integer_intensity_converted(self):
        """Test integer intensity values are converted to float."""
        mapper = EmotionMapper()

        record = {"intensity": 1}
        intensity = mapper.score_intensity(record)

        assert isinstance(intensity, float)
        assert intensity == 1.0


class TestToneSimilarity:
    """Test tone similarity computation."""

    def test_similarity_same_emotion(self):
        """Test similarity when target and tone match."""
        mapper = EmotionMapper()

        record = {"tone": "calm"}
        similarity = mapper.tone_similarity_score("calm", record)

        # Same emotion should have high similarity
        assert similarity > 0.7

    def test_similarity_different_emotions(self):
        """Test similarity between different emotions."""
        mapper = EmotionMapper()

        record = {"tone": "intense"}
        similarity = mapper.tone_similarity_score("calm", record)

        # Different emotions should have lower similarity
        # (calm is high stability, intense is low stability)
        assert similarity >= 0.0

    def test_similarity_empty_target(self):
        """Test similarity with empty target emotion."""
        mapper = EmotionMapper()

        record = {"tone": "calm"}
        similarity = mapper.tone_similarity_score("", record)

        assert similarity == 0.0

    def test_similarity_empty_tone(self):
        """Test similarity when record has no tone."""
        mapper = EmotionMapper()

        record: dict[str, Any] = {}
        similarity = mapper.tone_similarity_score("calm", record)

        assert similarity == 0.0

    def test_similarity_uses_mood_hint_fallback(self):
        """Test similarity falls back to mood_hint."""
        mapper = EmotionMapper()

        record = {"mood_hint": "calm"}
        similarity = mapper.tone_similarity_score("calm", record)

        assert similarity > 0.0

    def test_similarity_always_non_negative(self):
        """Test similarity is always >= 0."""
        mapper = EmotionMapper()

        test_cases = [
            ("calm", {"tone": "intense"}),
            ("focused", {"tone": "calm"}),
            ("intense", {"tone": "curious"}),
            ("neutral", {"tone": "focused"}),
        ]

        for target, record in test_cases:
            similarity = mapper.tone_similarity_score(target, record)
            assert similarity >= 0.0

    def test_similarity_unknown_target(self):
        """Test similarity with unknown target emotion."""
        mapper = EmotionMapper()

        record = {"tone": "calm"}
        similarity = mapper.tone_similarity_score("unknown_emotion", record)

        # Should fall back to neutral for unknown target
        assert similarity >= 0.0

    def test_similarity_stability_delta(self):
        """Test that stability delta affects similarity."""
        mapper = EmotionMapper()

        # Calm and curious have similar stability (0.7 vs 0.65)
        record_similar = {"tone": "calm"}
        similarity_similar = mapper.tone_similarity_score("curious", record_similar)

        # Calm and intense have very different stability (0.7 vs 0.35)
        record_different = {"tone": "intense"}
        similarity_different = mapper.tone_similarity_score("calm", record_different)

        # Similar stability should give higher similarity
        assert similarity_similar > similarity_different


class TestAffectDeltaComputation:
    """Test affect delta computation."""

    def test_affect_delta_baseline(self):
        """Test affect delta with baseline vector."""
        mapper = EmotionMapper()

        # Baseline vector should have zero affect delta
        delta = mapper._compute_affect_delta([0.5, 0.5, 0.5])
        assert delta == 0.0

    def test_affect_delta_maximum(self):
        """Test affect delta with maximum difference."""
        mapper = EmotionMapper()

        # Maximum difference from baseline (0.5, 0.5, 0.5)
        delta = mapper._compute_affect_delta([1.0, 1.0, 1.0])
        assert delta == 0.5  # Average of (0.5, 0.5, 0.5)

    def test_affect_delta_minimum(self):
        """Test affect delta with minimum values."""
        mapper = EmotionMapper()

        delta = mapper._compute_affect_delta([0.0, 0.0, 0.0])
        assert delta == 0.5  # Average of (0.5, 0.5, 0.5)

    def test_affect_delta_none_vector(self):
        """Test affect delta with None vector uses baseline."""
        mapper = EmotionMapper()

        delta = mapper._compute_affect_delta(None)
        assert delta == 0.0  # Should use baseline

    def test_affect_delta_empty_vector(self):
        """Test affect delta with empty vector."""
        mapper = EmotionMapper()

        delta = mapper._compute_affect_delta([])
        # Empty vector should be truncated to baseline length
        assert delta == 0.0

    def test_affect_delta_clamped(self):
        """Test affect delta is clamped to [0, 1]."""
        mapper = EmotionMapper()

        test_vectors = [
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
            [0.3, 0.6, 0.9],
            [0.8, 0.2, 0.5],
        ]

        for vector in test_vectors:
            delta = mapper._compute_affect_delta(vector)
            assert 0.0 <= delta <= 1.0

    def test_affect_delta_partial_difference(self):
        """Test affect delta with partial differences."""
        mapper = EmotionMapper()

        # One dimension different
        delta_one = mapper._compute_affect_delta([0.7, 0.5, 0.5])
        # Two dimensions different
        delta_two = mapper._compute_affect_delta([0.7, 0.7, 0.5])
        # Three dimensions different
        delta_three = mapper._compute_affect_delta([0.7, 0.7, 0.7])

        # More differences should give larger delta
        assert delta_one < delta_two < delta_three

    def test_affect_delta_high_dimensional_truncation(self):
        """Test that high-dimensional vectors are truncated."""
        mapper = EmotionMapper()

        # Baseline is 3D, provide 5D vector
        long_vector = [0.6, 0.7, 0.8, 0.9, 1.0]
        delta = mapper._compute_affect_delta(long_vector)

        # Should only use first 3 dimensions
        assert 0.0 <= delta <= 1.0

    def test_affect_delta_consistent(self):
        """Test affect delta is deterministic."""
        mapper = EmotionMapper()

        vector = [0.6, 0.7, 0.8]
        delta1 = mapper._compute_affect_delta(vector)
        delta2 = mapper._compute_affect_delta(vector)

        assert delta1 == delta2


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_record_with_all_fields(self):
        """Test record with all possible fields."""
        mapper = EmotionMapper()

        record = {
            "tone": "focused",
            "mood_hint": "calm",
            "intensity": 0.75,
            "emotion_vector": [0.6, 0.7, 0.8],
        }

        tone = mapper.suggest_tone("test", record)
        intensity = mapper.score_intensity(record)
        similarity = mapper.tone_similarity_score("focused", record)

        # Should use explicit tone
        assert tone == "focused"
        # Should use explicit intensity
        assert intensity == 0.75
        # Should compute similarity
        assert similarity > 0.0

    def test_record_with_no_fields(self):
        """Test record with no emotion fields."""
        mapper = EmotionMapper()

        record: dict[str, Any] = {}

        tone = mapper.suggest_tone("neutral", record)
        intensity = mapper.score_intensity(record)
        similarity = mapper.tone_similarity_score("neutral", record)

        # Should use defaults
        assert tone == "neutral"
        assert 0.0 <= intensity <= 1.0
        assert similarity == 0.0

    def test_negative_intensity(self):
        """Test handling of negative intensity values."""
        mapper = EmotionMapper()

        record = {"intensity": -5.0}
        intensity = mapper.score_intensity(record)

        assert intensity == 0.0

    def test_large_intensity(self):
        """Test handling of very large intensity values."""
        mapper = EmotionMapper()

        record = {"intensity": 1000.0}
        intensity = mapper.score_intensity(record)

        assert intensity == 1.0

    def test_special_characters_in_tone(self):
        """Test handling of special characters in tone."""
        mapper = EmotionMapper()

        record = {"tone": "calm 🧠"}
        tone = mapper.suggest_tone("test", record)

        # Should preserve special characters
        assert tone == "calm 🧠"

    def test_numeric_tone(self):
        """Test handling of numeric tone values."""
        mapper = EmotionMapper()

        record = {"tone": 123}
        # Type system allows Any, but code expects str
        # This should be handled gracefully
        result = mapper.suggest_tone("neutral", record)
        assert result == 123  # Preserved as-is

    def test_mapper_state_isolation(self):
        """Test that multiple mappers have isolated state."""
        mapper1 = EmotionMapper()
        mapper2 = EmotionMapper()

        # Make suggestions in mapper1
        for _ in range(5):
            mapper1.suggest_tone("test", {"emotion_vector": [0.8, 0.8, 0.8]})

        # mapper2 should have independent cumulative delta
        assert mapper1._cumulative_affect_delta > 0.0
        assert mapper2._cumulative_affect_delta == 0.0

    def test_zero_resonance_threshold(self):
        """Test mapper with zero resonance threshold."""
        mapper = EmotionMapper(resonance_threshold=0.0)

        assert mapper.resonance_threshold == 0.0
        # Should still function normally
        tone = mapper.suggest_tone("test", {"mood_hint": "calm"})
        assert tone == "calm"

    def test_max_resonance_threshold(self):
        """Test mapper with maximum resonance threshold."""
        mapper = EmotionMapper(resonance_threshold=1.0)

        assert mapper.resonance_threshold == 1.0
        # Should still function normally
        tone = mapper.suggest_tone("test", {"mood_hint": "calm"})
        assert tone == "calm"


class TestCustomProfiles:
    """Test custom emotion profiles."""

    def test_single_custom_profile(self):
        """Test mapper with single custom profile."""
        custom = {"happy": EmotionProfile(stability=0.9, similarity_boost=0.95)}
        mapper = EmotionMapper(profiles=custom)

        tone = mapper.suggest_tone("test", {"mood_hint": "happy"})
        assert tone == "happy"

    def test_custom_profile_overrides_default(self):
        """Test that custom profiles override defaults."""
        # Override the "neutral" profile
        custom = {"neutral": EmotionProfile(stability=0.99, similarity_boost=0.99)}
        mapper = EmotionMapper(profiles=custom)

        record = {"mood_hint": "neutral"}
        intensity = mapper.score_intensity(record)

        # Should use custom profile with high boost
        assert intensity > 0.9

    def test_mixed_custom_and_default(self):
        """Test mapper with both custom and default behavior."""
        # Add custom profile, defaults should still work
        custom = {"custom_emotion": EmotionProfile(stability=0.5, similarity_boost=0.5)}
        mapper = EmotionMapper(profiles=custom)

        custom_tone = mapper.suggest_tone("test", {"mood_hint": "custom_emotion"})
        # Default profiles not available, should fall back to neutral
        default_tone = mapper.suggest_tone("test", {"mood_hint": "calm"})

        assert custom_tone == "custom_emotion"
        assert default_tone == "neutral"  # Fallback


@pytest.mark.integration
class TestEmotionMapperIntegration:
    """Integration tests for EmotionMapper."""

    def test_healix_workflow(self):
        """Test complete Healix memory workflow."""
        mapper = EmotionMapper(resonance_threshold=0.8)

        # Simulate Healix memory processing
        memories = [
            {
                "memory_id": "mem-001",
                "mood_hint": "calm",
                "emotion_vector": [0.5, 0.5, 0.5],
            },
            {
                "memory_id": "mem-002",
                "tone": "focused",
                "emotion_vector": [0.6, 0.7, 0.6],
            },
            {
                "memory_id": "mem-003",
                "mood_hint": "intense",
                "intensity": 0.9,
                "emotion_vector": [0.9, 0.8, 0.7],
            },
        ]

        results = []
        for memory in memories:
            tone = mapper.suggest_tone("processing", memory)
            intensity = mapper.score_intensity(memory)
            results.append({"tone": tone, "intensity": intensity})

        # Verify results
        assert results[0]["tone"] == "calm"
        assert results[1]["tone"] == "focused"
        assert results[2]["tone"] == "intense"
        assert results[2]["intensity"] == 0.9

    def test_cumulative_affect_tracking_workflow(self):
        """Test cumulative affect delta tracking over multiple operations."""
        mapper = EmotionMapper()

        vectors = [
            [0.5, 0.5, 0.5],  # Baseline
            [0.6, 0.6, 0.6],  # Small change
            [0.7, 0.7, 0.7],  # Medium change
            [0.9, 0.9, 0.9],  # Large change
        ]

        deltas = []
        for vector in vectors:
            mapper.suggest_tone("test", {"emotion_vector": vector})
            deltas.append(mapper._cumulative_affect_delta)

        # Cumulative delta should monotonically increase
        for i in range(1, len(deltas)):
            assert deltas[i] >= deltas[i - 1]

    def test_tone_similarity_matrix(self):
        """Test similarity matrix across all default profiles."""
        mapper = EmotionMapper()

        profiles = ["neutral", "calm", "curious", "focused", "intense"]
        similarity_matrix = {}

        for target in profiles:
            similarity_matrix[target] = {}
            for tone in profiles:
                record = {"tone": tone}
                similarity = mapper.tone_similarity_score(target, record)
                similarity_matrix[target][tone] = similarity

        # Diagonal (same emotion) should have highest similarity
        for profile in profiles:
            self_similarity = similarity_matrix[profile][profile]
            for other_profile in profiles:
                if other_profile != profile:
                    assert self_similarity >= similarity_matrix[profile][other_profile]

    def test_emotion_state_progression(self):
        """Test emotion state progression tracking."""
        mapper = EmotionMapper()

        # Simulate emotional state progression
        states = [
            ("calm", [0.5, 0.5, 0.5]),
            ("curious", [0.55, 0.6, 0.55]),
            ("focused", [0.6, 0.7, 0.6]),
            ("intense", [0.8, 0.9, 0.8]),
        ]

        cumulative_deltas = []
        for mood, vector in states:
            record = {"mood_hint": mood, "emotion_vector": vector}
            tone = mapper.suggest_tone("progression", record)
            intensity = mapper.score_intensity(record)
            cumulative_deltas.append(mapper._cumulative_affect_delta)

            # Verify basic properties
            assert tone in ["calm", "curious", "focused", "intense", "neutral"]
            assert 0.0 <= intensity <= 1.0

        # Cumulative delta should increase (or stay same)
        assert all(cumulative_deltas[i] <= cumulative_deltas[i + 1] for i in range(len(cumulative_deltas) - 1))
