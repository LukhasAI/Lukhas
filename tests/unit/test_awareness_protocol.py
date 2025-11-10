import pytest
from consciousness.awareness.awareness_protocol import map_local_tier_to_global
from tiers import GlobalTier, TierMappingError


def test_map_local_tier_to_global_valid_tiers():
    """
    Tests that valid local tier names are correctly mapped to global tiers.
    """
    assert map_local_tier_to_global("restricted") == GlobalTier.PUBLIC
    assert map_local_tier_to_global("basic") == GlobalTier.AUTHENTICATED
    assert map_local_tier_to_global("standard") == GlobalTier.ELEVATED
    assert map_local_tier_to_global("elevated") == GlobalTier.PRIVILEGED
    assert map_local_tier_to_global("advanced") == GlobalTier.ADMIN

def test_map_local_tier_to_global_case_insensitivity():
    """
    Tests that the mapping is case-insensitive.
    """
    assert map_local_tier_to_global("Restricted") == GlobalTier.PUBLIC
    assert map_local_tier_to_global("BASIC") == GlobalTier.AUTHENTICATED

def test_map_local_tier_to_global_unknown_tier():
    """
    Tests that an unknown local tier name raises a TierMappingError.
    """
    with pytest.raises(TierMappingError) as excinfo:
        map_local_tier_to_global("unknown_tier")
    assert "Unknown local tier name: 'unknown_tier'" in str(excinfo.value)

def test_map_local_tier_to_global_empty_string():
    """
    Tests that an empty string raises a TierMappingError.
    """
    with pytest.raises(TierMappingError):
        map_local_tier_to_global("")
