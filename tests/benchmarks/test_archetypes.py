"""
Tests for archetypal taxonomy system.
Validates archetypal classification and analysis.
"""
import pytest
from benchmarks.dream.archetypes import (
    ARCHETYPES,
    CANONICAL_EMOTIONS,
    analyze_snapshot_archetypes,
    calculate_archetype_score,
    classify_archetype,
    create_archetypal_test_case,
    suggest_archetypal_balance,
)


class TestArchetypalClassification:
    """Test archetypal classification functionality."""

    def test_hero_archetype_detection(self):
        """Test detection of hero archetype."""
        # Strong hero profile: high confidence, joy, curiosity
        hero_emotion = {
            "confidence": 0.9,
            "joy": 0.8,
            "curiosity": 0.9,
            "trust": 0.7,
            "fear": 0.1,
            "sadness": 0.1,
            "anger": 0.0,
            "surprise": 0.4
        }

        classifications = classify_archetype(hero_emotion, threshold=0.6)

        # Should classify as hero
        archetype_names = [name for name, score in classifications]
        assert "hero" in archetype_names

        # Hero should have high score
        hero_score = next(score for name, score in classifications if name == "hero")
        assert hero_score > 0.6

    def test_shadow_archetype_detection(self):
        """Test detection of shadow archetype."""
        # Strong shadow profile: high fear, anger, sadness
        shadow_emotion = {
            "confidence": 0.1,
            "joy": 0.1,
            "curiosity": 0.2,
            "trust": 0.2,
            "fear": 0.9,
            "sadness": 0.8,
            "anger": 0.9,
            "surprise": 0.7
        }

        classifications = classify_archetype(shadow_emotion)

        archetype_names = [name for name, score in classifications]
        assert "shadow" in archetype_names

    def test_trickster_archetype_detection(self):
        """Test detection of trickster archetype."""
        # Strong trickster profile: high surprise, curiosity
        trickster_emotion = {
            "confidence": 0.5,
            "joy": 0.6,
            "curiosity": 0.9,
            "trust": 0.4,
            "fear": 0.2,
            "sadness": 0.1,
            "anger": 0.1,
            "surprise": 0.9
        }

        classifications = classify_archetype(trickster_emotion)

        archetype_names = [name for name, score in classifications]
        assert "trickster" in archetype_names

    def test_threshold_filtering(self):
        """Test that threshold properly filters results."""
        # Weak archetypal signal
        weak_emotion = {emotion: 0.5 for emotion in CANONICAL_EMOTIONS}

        # High threshold should filter out weak matches
        classifications_high = classify_archetype(weak_emotion, threshold=0.8)
        classifications_low = classify_archetype(weak_emotion, threshold=0.3)

        assert len(classifications_high) <= len(classifications_low)

    def test_score_calculation(self):
        """Test archetypal score calculation."""
        emotion = {
            "confidence": 0.8,
            "joy": 0.7,
            "curiosity": 0.9,
            "fear": 0.1,
            "sadness": 0.1,
            "anger": 0.0,
            "surprise": 0.4,
            "trust": 0.6
        }

        hero_data = ARCHETYPES["hero"]
        score = calculate_archetype_score(emotion, hero_data)

        # Should be positive score for good match
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be reasonably high for hero match

    def test_opposition_penalty(self):
        """Test that opposed emotions reduce archetype scores."""
        # Hero with high fear (opposed emotion)
        conflicted_hero = {
            "confidence": 0.9,
            "joy": 0.8,
            "curiosity": 0.9,
            "fear": 0.9,  # High opposed emotion
            "sadness": 0.1,
            "anger": 0.0,
            "surprise": 0.4,
            "trust": 0.6
        }

        # Pure hero
        pure_hero = conflicted_hero.copy()
        pure_hero["fear"] = 0.1

        hero_data = ARCHETYPES["hero"]

        conflicted_score = calculate_archetype_score(conflicted_hero, hero_data)
        pure_score = calculate_archetype_score(pure_hero, hero_data)

        # Pure hero should score higher than conflicted
        assert pure_score > conflicted_score

    def test_missing_emotions(self):
        """Test handling of missing emotion keys."""
        # Partial emotion vector
        partial_emotion = {"confidence": 0.8, "joy": 0.7}

        classifications = classify_archetype(partial_emotion)

        # Should handle gracefully (missing emotions treated as 0)
        assert isinstance(classifications, list)

    def test_all_archetypes_represented(self):
        """Test that all defined archetypes can be detected."""
        # Create test cases for each archetype
        for archetype_name in ARCHETYPES:
            test_case = create_archetypal_test_case(archetype_name, intensity=0.9)
            emotion_vector = test_case["emotional_context"]

            classifications = classify_archetype(emotion_vector, threshold=0.4)
            archetype_names = [name for name, score in classifications]

            assert archetype_name in archetype_names, f"Failed to detect {archetype_name} archetype"

class TestSnapshotAnalysis:
    """Test snapshot archetypal analysis."""

    def test_snapshot_analysis(self):
        """Test archetypal analysis of snapshot collection."""
        snapshots = [
            {
                "name": "hero_snap",
                "emotional_context": {
                    "confidence": 0.9, "joy": 0.8, "curiosity": 0.7,
                    "fear": 0.1, "sadness": 0.1, "anger": 0.0,
                    "surprise": 0.4, "trust": 0.6
                }
            },
            {
                "name": "shadow_snap",
                "emotional_context": {
                    "confidence": 0.1, "joy": 0.1, "curiosity": 0.2,
                    "fear": 0.9, "sadness": 0.8, "anger": 0.7,
                    "surprise": 0.6, "trust": 0.2
                }
            }
        ]

        analysis = analyze_snapshot_archetypes(snapshots)

        assert analysis["total_snapshots"] == 2
        assert len(analysis["snapshot_archetypes"]) == 2
        assert "archetype_statistics" in analysis
        assert "dominant_archetypes" in analysis

        # Should detect both hero and shadow
        stats = analysis["archetype_statistics"]
        assert stats["hero"]["frequency"] >= 1
        assert stats["shadow"]["frequency"] >= 1

    def test_diversity_calculation(self):
        """Test archetypal diversity calculation."""
        # Diverse snapshots
        diverse_snapshots = []
        for archetype_name in ["hero", "shadow", "trickster", "sage"]:
            test_case = create_archetypal_test_case(archetype_name)
            diverse_snapshots.append(test_case)

        diverse_analysis = analyze_snapshot_archetypes(diverse_snapshots)

        # Uniform snapshots
        uniform_snapshots = []
        for _ in range(4):
            test_case = create_archetypal_test_case("hero")
            uniform_snapshots.append(test_case)

        uniform_analysis = analyze_snapshot_archetypes(uniform_snapshots)

        # Diverse should have higher diversity index
        assert diverse_analysis["diversity_index"] > uniform_analysis["diversity_index"]

    def test_invalid_snapshots(self):
        """Test handling of invalid snapshots."""
        invalid_snapshots = [
            {"name": "no_emotion"},  # Missing emotional_context
            {"name": "invalid_emotion", "emotional_context": "not_a_dict"},
            {
                "name": "valid_snap",
                "emotional_context": {"confidence": 0.7, "joy": 0.6}
            }
        ]

        analysis = analyze_snapshot_archetypes(invalid_snapshots)

        # Should only process valid snapshot
        assert analysis["total_snapshots"] == 1

class TestArchetypalBalance:
    """Test archetypal balance suggestions."""

    def test_balance_suggestions(self):
        """Test archetypal balance analysis."""
        # Create imbalanced collection (all hero)
        hero_snapshots = []
        for _ in range(5):
            test_case = create_archetypal_test_case("hero")
            hero_snapshots.append(test_case)

        current_stats = analyze_snapshot_archetypes(hero_snapshots)
        suggestions = suggest_archetypal_balance(current_stats, target_balance="balanced")

        assert "recommendations" in suggestions
        assert len(suggestions["recommendations"]) > 0

        # Should suggest reducing hero and increasing others
        actions = [rec["action"] for rec in suggestions["recommendations"]]
        assert "decrease" in actions  # Should suggest reducing hero
        assert "increase" in actions  # Should suggest increasing others

    def test_different_target_balances(self):
        """Test different target balance types."""
        snapshots = [create_archetypal_test_case("hero")]
        current_stats = analyze_snapshot_archetypes(snapshots)

        balances = ["balanced", "heroic", "exploratory", "nurturing", "transformative"]

        for balance_type in balances:
            suggestions = suggest_archetypal_balance(current_stats, target_balance=balance_type)

            assert suggestions["target_balance"] == balance_type
            assert "overall_balance_score" in suggestions
            assert 0.0 <= suggestions["overall_balance_score"] <= 1.0

    def test_balance_score_calculation(self):
        """Test balance score calculation."""
        # Perfect balance case
        balanced_snapshots = []
        archetype_names = list(ARCHETYPES.keys())[:4]  # First 4 archetypes

        for archetype_name in archetype_names:
            test_case = create_archetypal_test_case(archetype_name)
            balanced_snapshots.append(test_case)

        balanced_stats = analyze_snapshot_archetypes(balanced_snapshots)
        balanced_suggestions = suggest_archetypal_balance(balanced_stats, "balanced")

        # Imbalanced case
        imbalanced_snapshots = [create_archetypal_test_case("hero")] * 4
        imbalanced_stats = analyze_snapshot_archetypes(imbalanced_snapshots)
        imbalanced_suggestions = suggest_archetypal_balance(imbalanced_stats, "balanced")

        # Balanced should score higher
        assert balanced_suggestions["overall_balance_score"] > imbalanced_suggestions["overall_balance_score"]

class TestArchetypalTestCases:
    """Test archetypal test case generation."""

    def test_test_case_generation(self):
        """Test generation of archetypal test cases."""
        for archetype_name in ARCHETYPES:
            test_case = create_archetypal_test_case(archetype_name, intensity=0.8)

            assert test_case["name"] == f"{archetype_name}_test_case"
            assert "emotional_context" in test_case
            assert test_case["metadata"]["archetype"] == archetype_name

            # Should classify as intended archetype
            emotion_vector = test_case["emotional_context"]
            classifications = classify_archetype(emotion_vector, threshold=0.5)

            if classifications:  # Should have at least one classification
                top_archetype = classifications[0][0]
                assert top_archetype == archetype_name, f"Test case for {archetype_name} classified as {top_archetype}"

    def test_intensity_scaling(self):
        """Test intensity scaling in test case generation."""
        low_intensity = create_archetypal_test_case("hero", intensity=0.3)
        high_intensity = create_archetypal_test_case("hero", intensity=0.9)

        low_emotion = low_intensity["emotional_context"]
        high_emotion = high_intensity["emotional_context"]

        # High intensity should have stronger archetypal signal
        hero_data = ARCHETYPES["hero"]

        low_score = calculate_archetype_score(low_emotion, hero_data)
        high_score = calculate_archetype_score(high_emotion, hero_data)

        assert high_score > low_score

    def test_invalid_archetype(self):
        """Test handling of invalid archetype names."""
        with pytest.raises(ValueError):
            create_archetypal_test_case("nonexistent_archetype")

    def test_emotion_value_validity(self):
        """Test that generated test cases have valid emotion values."""
        for archetype_name in ARCHETYPES:
            test_case = create_archetypal_test_case(archetype_name)
            emotion_vector = test_case["emotional_context"]

            for emotion_key, emotion_value in emotion_vector.items():
                assert 0.0 <= emotion_value <= 1.0, f"Invalid emotion value: {emotion_key}={emotion_value}"

class TestArchetypalSystem:
    """Test overall archetypal system functionality."""

    def test_canonical_emotions_coverage(self):
        """Test that all canonical emotions are covered in archetypes."""
        all_archetypal_emotions = set()

        for archetype_data in ARCHETYPES.values():
            all_archetypal_emotions.update(archetype_data["primary_emotions"])
            all_archetypal_emotions.update(archetype_data["secondary_emotions"])
            all_archetypal_emotions.update(archetype_data["opposed_emotions"])

        # Should cover most or all canonical emotions
        coverage = len(all_archetypal_emotions & set(CANONICAL_EMOTIONS)) / len(CANONICAL_EMOTIONS)
        assert coverage > 0.7, f"Archetype coverage {coverage:.1%} too low"

    def test_archetype_distinctiveness(self):
        """Test that archetypes are sufficiently distinct."""
        archetype_signatures = {}

        for archetype_name in ARCHETYPES:
            test_case = create_archetypal_test_case(archetype_name, intensity=0.9)
            emotion_vector = test_case["emotional_context"]

            # Create signature from top emotions
            top_emotions = sorted(emotion_vector.items(), key=lambda x: x[1], reverse=True)[:3]
            signature = tuple(sorted([emotion for emotion, value in top_emotions]))

            archetype_signatures[archetype_name] = signature

        # Signatures should be mostly distinct
        unique_signatures = len(set(archetype_signatures.values()))
        total_archetypes = len(archetype_signatures)

        distinctiveness = unique_signatures / total_archetypes
        assert distinctiveness > 0.6, f"Archetype distinctiveness {distinctiveness:.1%} too low"

    def test_system_consistency(self):
        """Test overall system consistency."""
        # All archetypes should have required fields
        for archetype_name, archetype_data in ARCHETYPES.items():
            required_fields = ["primary_emotions", "secondary_emotions", "opposed_emotions", "description"]

            for field in required_fields:
                assert field in archetype_data, f"Archetype {archetype_name} missing field {field}"

            # Should have non-empty description
            assert len(archetype_data["description"]) > 10, f"Archetype {archetype_name} description too short"
