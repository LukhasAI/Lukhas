#!/usr/bin/env python3
"""
Integration tests for Decision Making Bridge
"""
import pytest


def test_bridge_import():
    """Test that bridge can be imported"""
    import core.consciousness.bridge

    assert core.consciousness.bridge is not None
