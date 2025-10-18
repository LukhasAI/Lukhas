"""Tests for tier resolution in the core integrator."""

import pytest

from consciousness.reflection.core_integrator import AccessTier, resolve_access_tier
from tiers import GlobalTier, TierMappingError


def test_resolve_access_tier_supports_legacy_names() -> None:
    """Legacy tier names should map to canonical global tiers."""

    tier = resolve_access_tier("restricted")

    assert tier is AccessTier.PUBLIC
    assert tier.global_tier is GlobalTier.PUBLIC


def test_resolve_access_tier_transcendent_alias() -> None:
    """Transcendent aliases should align with the system tier."""

    tier = resolve_access_tier("Free-Transcendent")

    assert tier is AccessTier.SYSTEM
    assert tier.global_tier is GlobalTier.SYSTEM


def test_resolve_access_tier_invalid_name_raises() -> None:
    """Unknown tier names should raise a mapping error."""

    with pytest.raises(TierMappingError):
        resolve_access_tier("unknown-tier")
