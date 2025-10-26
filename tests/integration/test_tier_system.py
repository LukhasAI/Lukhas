#!/usr/bin/env python3
"""
Integration tests for Tier System
"""
import pytest


def test_tier_system_import():
    """Test that tier_system can be imported"""
    from core.memory.tier_system import TierLevel, AccessType

    assert TierLevel.PUBLIC is not None
    assert AccessType is not None


def test_tier_levels():
    """Test tier levels are available"""
    from core.memory.tier_system import TierLevel

    assert hasattr(TierLevel, 'PUBLIC')
    assert hasattr(TierLevel, 'AUTHENTICATED')
    assert hasattr(TierLevel, 'ELEVATED')
