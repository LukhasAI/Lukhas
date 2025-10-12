"""Test branding bridge exports and contract."""
import pytest


def test_branding_exports():
    """Verify branding bridge exports expected symbols."""
    from branding import (
        APPROVED_TERMS,
        COLORS,
        CONSCIOUSNESS_SYMBOL,
        CONSTELLATION_FRAMEWORK,
        GUARDIAN_SYMBOL,
        IDENTITY_SYMBOL,
        SYSTEM_NAME,
        SYSTEM_VERSION,
        get_constellation_description,
        get_system_signature,
        normalize_chunk,
        normalize_output,
        validate_branding_compliance,
    )

    # Verify core symbols exist
    assert isinstance(APPROVED_TERMS, dict)
    assert isinstance(COLORS, dict)
    assert isinstance(SYSTEM_NAME, str)
    assert "LUKHAS" in SYSTEM_NAME
    assert callable(get_system_signature)


def test_branding_single_source_of_truth():
    """Verify branding data comes from candidate.branding."""
    import branding
    from candidate.branding import APPROVED_TERMS as canonical_terms

    # Should be same object (not a copy)
    assert branding.APPROVED_TERMS is canonical_terms


def test_branding_all_defined():
    """Verify __all__ is properly defined."""
    import branding

    assert hasattr(branding, "__all__")
    assert isinstance(branding.__all__, list)
    assert len(branding.__all__) == 13
    assert "APPROVED_TERMS" in branding.__all__
