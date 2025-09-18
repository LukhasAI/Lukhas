"""
Tests for conflict scenario corpus.
Ensures strategies handle direct emotional clashes properly.
"""
import pytest

from benchmarks.dream.conflict import (
    get_conflict_corpus, get_conflict_case, validate_conflict_case,
    run_conflict_validation
)

class TestConflictCorpus:
    """Test conflict scenario corpus functionality."""

    def test_corpus_structure(self):
        """Test that conflict corpus has proper structure."""
        corpus = get_conflict_corpus()

        assert len(corpus) > 0
        assert isinstance(corpus, list)

        # Check first case structure
        first_case = corpus[0]
        required_fields = ["id", "description", "query_emotion", "snapshots", "expected_selection", "rationale"]

        for field in required_fields:
            assert field in first_case, f"Missing required field: {field}"

    def test_conflict_case_retrieval(self):
        """Test retrieving specific conflict cases."""
        # Test valid case
        case = get_conflict_case("confidence_vs_fear")
        assert case["id"] == "confidence_vs_fear"
        assert "snapshots" in case

        # Test invalid case
        with pytest.raises(ValueError):
            get_conflict_case("nonexistent_case")

    def test_case_validation(self):
        """Test conflict case validation logic."""
        # Valid case
        valid_case = {
            "id": "test_case",
            "description": "Test case",
            "query_emotion": {"confidence": 0.8},
            "snapshots": [
                {
                    "name": "snap1",
                    "emotional_context": {"confidence": 0.9},
                    "timestamp": 100.0,
                    "content": "Test snapshot 1"
                },
                {
                    "name": "snap2",
                    "emotional_context": {"confidence": 0.1},
                    "timestamp": 100.0,
                    "content": "Test snapshot 2"
                }
            ],
            "expected_selection": "snap1",
            "rationale": "Test rationale"
        }

        errors = validate_conflict_case(valid_case)
        assert len(errors) == 0

        # Invalid case - missing field
        invalid_case = valid_case.copy()
        del invalid_case["expected_selection"]

        errors = validate_conflict_case(invalid_case)
        assert len(errors) > 0
        assert any("expected_selection" in error for error in errors)

        # Invalid case - expected selection not in snapshots
        invalid_case2 = valid_case.copy()
        invalid_case2["expected_selection"] = "nonexistent_snap"

        errors = validate_conflict_case(invalid_case2)
        assert len(errors) > 0
        assert any("not found in snapshot names" in error for error in errors)

    def test_corpus_validation(self):
        """Test validation of entire conflict corpus."""
        validation = run_conflict_validation()

        assert "total_cases" in validation
        assert "valid_cases" in validation
        assert "overall_valid" in validation

        assert validation["total_cases"] > 0
        assert validation["valid_cases"] <= validation["total_cases"]

        # Should be valid if no errors
        if not validation["validation_errors"]:
            assert validation["overall_valid"] is True

    def test_emotional_oppositions(self):
        """Test that conflict cases actually contain emotional oppositions."""
        corpus = get_conflict_corpus()

        for case in corpus:
            snapshots = case["snapshots"]
            assert len(snapshots) >= 2, f"Case {case['id']} needs at least 2 snapshots"

            # Check that snapshots have different emotional profiles
            emotions_set = []
            for snapshot in snapshots:
                emotion_context = snapshot["emotional_context"]
                emotions_set.append(tuple(sorted(emotion_context.items())))

            # Should have different emotional signatures
            assert len(set(emotions_set)) > 1, f"Case {case['id']} snapshots too similar"

    def test_confidence_vs_fear_case(self):
        """Test specific confidence vs fear conflict case."""
        case = get_conflict_case("confidence_vs_fear")

        # Should have high confidence option and high fear option
        high_conf_found = False
        high_fear_found = False

        for snapshot in case["snapshots"]:
            emotion = snapshot["emotional_context"]

            if emotion.get("confidence", 0) > 0.8:
                high_conf_found = True

            if emotion.get("fear", 0) > 0.8:
                high_fear_found = True

        assert high_conf_found, "Should have high confidence snapshot"
        assert high_fear_found, "Should have high fear snapshot"

        # Expected selection should be the confident one
        assert case["expected_selection"] == "high_conf"

    def test_extreme_opposition_case(self):
        """Test extreme opposition case."""
        case = get_conflict_case("extreme_opposition")

        positive_found = False
        negative_found = False

        for snapshot in case["snapshots"]:
            emotion = snapshot["emotional_context"]

            # Check for positive extreme
            if (emotion.get("confidence", 0) == 1.0 and
                emotion.get("joy", 0) == 1.0 and
                emotion.get("trust", 0) == 1.0):
                positive_found = True

            # Check for negative extreme
            if (emotion.get("fear", 0) == 1.0 and
                emotion.get("anger", 0) == 1.0 and
                emotion.get("sadness", 0) == 1.0):
                negative_found = True

        assert positive_found, "Should have positive extreme"
        assert negative_found, "Should have negative extreme"

    def test_subtle_preference_case(self):
        """Test subtle preference discrimination case."""
        case = get_conflict_case("subtle_preference")

        # Should have snapshots with small differences
        snapshots = case["snapshots"]
        assert len(snapshots) == 2

        snap1_emotion = snapshots[0]["emotional_context"]
        snap2_emotion = snapshots[1]["emotional_context"]

        # Calculate differences
        differences = []
        common_keys = set(snap1_emotion.keys()) & set(snap2_emotion.keys())

        for key in common_keys:
            diff = abs(snap1_emotion[key] - snap2_emotion[key])
            differences.append(diff)

        # Should have small but measurable differences
        avg_diff = sum(differences) / len(differences)
        assert 0.01 < avg_diff < 0.2, "Differences should be subtle but measurable"

    def test_all_cases_have_expected_selections(self):
        """Test that all conflict cases have valid expected selections."""
        corpus = get_conflict_corpus()

        for case in corpus:
            snapshot_names = [s["name"] for s in case["snapshots"]]
            expected = case["expected_selection"]

            assert expected in snapshot_names, f"Case {case['id']}: expected '{expected}' not in {snapshot_names}"

    def test_emotional_context_validity(self):
        """Test that all emotional contexts have valid values."""
        corpus = get_conflict_corpus()

        for case in corpus:
            case_id = case["id"]

            # Check query emotion
            for key, value in case["query_emotion"].items():
                assert 0.0 <= value <= 1.0, f"Case {case_id}: query emotion {key}={value} out of range"

            # Check snapshot emotions
            for snapshot in case["snapshots"]:
                for key, value in snapshot["emotional_context"].items():
                    assert 0.0 <= value <= 1.0, f"Case {case_id}: snapshot {snapshot['name']} emotion {key}={value} out of range"

    def test_case_diversity(self):
        """Test that conflict cases cover diverse scenarios."""
        corpus = get_conflict_corpus()

        # Should have multiple types of conflicts
        case_descriptions = [case["description"].lower() for case in corpus]

        # Check for different conflict types
        conflict_types = [
            "confidence",
            "joy",
            "curiosity",
            "trust",
            "extreme",
            "subtle"
        ]

        for conflict_type in conflict_types:
            assert any(conflict_type in desc for desc in case_descriptions), f"Missing {conflict_type} conflict type"

    def test_rationale_quality(self):
        """Test that all cases have meaningful rationales."""
        corpus = get_conflict_corpus()

        for case in corpus:
            rationale = case["rationale"]

            assert len(rationale) > 10, f"Case {case['id']} rationale too short"
            assert "should" in rationale.lower(), f"Case {case['id']} rationale lacks clear expectation"