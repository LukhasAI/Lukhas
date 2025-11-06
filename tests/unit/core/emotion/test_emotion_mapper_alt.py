"""Unit tests for the EmotionMapper class."""
from __future__ import annotations

import pytest
from core.emotion.emotion_mapper_alt import EmotionMapper, EmotionProfile


def test_initialization_default():
    """Test that the EmotionMapper initializes with default profiles."""
    mapper = EmotionMapper()
    assert mapper.resonance_threshold == 0.75
    assert "neutral" in mapper._profiles

def test_initialization_custom():
    """Test that the EmotionMapper initializes with custom profiles."""
    custom_profiles = {
        "happy": EmotionProfile(stability=0.8, similarity_boost=0.9),
        "sad": EmotionProfile(stability=0.4, similarity_boost=0.5),
    }
    mapper = EmotionMapper(profiles=custom_profiles, resonance_threshold=0.8)
    assert mapper.resonance_threshold == 0.8
    assert "happy" in mapper._profiles
    assert "sad" in mapper._profiles
    assert "neutral" not in mapper._profiles

def test_suggest_tone_explicit():
    """Test that suggest_tone returns the explicit tone if present."""
    mapper = EmotionMapper()
    record = {"tone": "angry"}
    assert mapper.suggest_tone("test_context", record) == "angry"

def test_suggest_tone_mood_hint():
    """Test that suggest_tone uses the mood_hint if present."""
    mapper = EmotionMapper()
    record = {"mood_hint": "calm"}
    assert mapper.suggest_tone("test_context", record) == "calm"

def test_suggest_tone_mood_hint_not_in_profiles():
    """Test that suggest_tone falls back to neutral if mood_hint is not a valid profile."""
    mapper = EmotionMapper()
    record = {"mood_hint": "unknown"}
    assert mapper.suggest_tone("test_context", record) == "neutral"

def test_suggest_tone_no_hint():
    """Test that suggest_tone falls back to the context if no hint is provided."""
    mapper = EmotionMapper()
    record = {}
    assert mapper.suggest_tone("curious", record) == "curious"

def test_suggest_tone_no_hint_no_context_in_profiles():
    """Test that suggest_tone falls back to neutral if context is not a valid profile."""
    mapper = EmotionMapper()
    record = {}
    assert mapper.suggest_tone("unknown", record) == "neutral"

@pytest.mark.xfail(reason="Known bug: suggest_tone does not correctly fall back to the first profile.")
def test_suggest_tone_fallback_to_first_profile():
    """Test that suggest_tone falls back to the first available profile if neutral is missing."""
    custom_profiles = {
        "happy": EmotionProfile(stability=0.8, similarity_boost=0.9),
        "sad": EmotionProfile(stability=0.4, similarity_boost=0.5),
    }
    mapper = EmotionMapper(profiles=custom_profiles)
    record = {"mood_hint": "unknown"}
    assert mapper.suggest_tone("test_context", record) == "happy"

def test_score_intensity_explicit():
    """Test that score_intensity returns the explicit intensity if present."""
    mapper = EmotionMapper()
    record = {"intensity": 0.7}
    assert mapper.score_intensity(record) == 0.7

def test_score_intensity_explicit_clamped():
    """Test that score_intensity clamps explicit intensity to the range [0, 1]."""
    mapper = EmotionMapper()
    assert mapper.score_intensity({"intensity": 1.5}) == 1.0
    assert mapper.score_intensity({"intensity": -0.5}) == 0.0

def test_score_intensity_inferred():
    """Test that score_intensity infers intensity when not explicit."""
    mapper = EmotionMapper()
    record = {"emotion_vector": (0.6, 0.6, 0.6)}
    # This should be close to the similarity_boost of the neutral profile (0.8)
    assert mapper.score_intensity(record) == pytest.approx(0.72)

def test_score_intensity_fallback_profile():
    """Test intensity scoring falls back to the first profile if neutral is missing."""
    custom_profiles = {
        "happy": EmotionProfile(stability=0.8, similarity_boost=0.9),
    }
    mapper = EmotionMapper(profiles=custom_profiles)
    record = {"emotion_vector": (0.5, 0.5, 0.5)}
    assert mapper.score_intensity(record) == pytest.approx(0.9)


def test_tone_similarity_score():
    """Test the tone_similarity_score method."""
    mapper = EmotionMapper()
    record = {"tone": "calm"}
    assert mapper.tone_similarity_score("neutral", record) > 0

def test_tone_similarity_score_no_target():
    """Test tone_similarity_score returns 0 if no target emotion is provided."""
    mapper = EmotionMapper()
    record = {"tone": "calm"}
    assert mapper.tone_similarity_score("", record) == 0.0

def test_tone_similarity_score_no_tone_in_record():
    """Test tone_similarity_score returns 0 if no tone is found in the record."""
    mapper = EmotionMapper()
    record = {}
    assert mapper.tone_similarity_score("neutral", record) == 0.0

def test_tone_similarity_score_unknown_tone():
    """Test tone_similarity_score returns 0 for tones not in profiles."""
    mapper = EmotionMapper()
    record = {"tone": "unknown"}
    assert mapper.tone_similarity_score("neutral", record) == 0.0

def test_compute_affect_delta():
    """Test the _compute_affect_delta method."""
    mapper = EmotionMapper()
    # No deviation from baseline
    assert mapper._compute_affect_delta(None) == 0.0
    assert mapper._compute_affect_delta((0.5, 0.5, 0.5)) == 0.0
    # Max deviation
    assert mapper._compute_affect_delta((1.0, 1.0, 1.0)) == 0.5
    assert mapper._compute_affect_delta((0.0, 0.0, 0.0)) == 0.5
    # Partial deviation
    assert mapper._compute_affect_delta((0.6, 0.5, 0.4)) == pytest.approx(0.0666666, abs=1e-6)

def test_compute_affect_delta_different_vector_length():
    """Test _compute_affect_delta handles vectors of different lengths."""
    mapper = EmotionMapper()
    assert mapper._compute_affect_delta((0.6, 0.6, 0.6, 1.0)) == pytest.approx(0.1)
