"""Test consciousness bridge exports and contract."""
import pytest


def test_dream_bridge_exports():
    """Verify consciousness.dream bridge exists."""
    from consciousness.dream import dream

    # Should be a module
    assert hasattr(dream, '__file__')


def test_awareness_bridge_exports():
    """Verify consciousness.awareness bridge exists."""
    from consciousness.awareness import awareness

    # Should be a module
    assert hasattr(awareness, '__file__')


def test_reflection_bridge_exports():
    """Verify consciousness.reflection bridge exports expected symbols."""
    from consciousness.reflection import (
        AlignmentScore,
        AlignmentStatus,
        EmotionalDrift,
        EmotionalTone,
        LambdaMirror,
        ReflectionEntry,
        ReflectionType,
    )

    # Verify classes/types exist
    assert AlignmentScore is not None
    assert LambdaMirror is not None
    assert ReflectionType is not None


def test_reflection_single_source_of_truth():
    """Verify reflection exports come from candidate.consciousness.reflection."""
    from candidate.consciousness.reflection import LambdaMirror as canonical_mirror
    from consciousness.reflection import LambdaMirror as bridge_mirror

    # Should be same class
    assert bridge_mirror is canonical_mirror


def test_reflection_all_defined():
    """Verify __all__ is properly defined."""
    from consciousness import reflection

    assert hasattr(reflection, "__all__")
    assert isinstance(reflection.__all__, list)
    assert len(reflection.__all__) == 7
    assert "LambdaMirror" in reflection.__all__
