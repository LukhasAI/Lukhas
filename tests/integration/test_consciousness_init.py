#!/usr/bin/env python3
"""
Integration tests for Consciousness Init Module
"""
import pytest


def test_consciousness_init_import():
    """Test that consciousness init can be imported"""
    import core.consciousness

    assert core.consciousness is not None
