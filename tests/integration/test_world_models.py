#!/usr/bin/env python3
"""
Integration tests for World Models
"""
import pytest


def test_world_models_import():
    """Test that world_models can be imported"""
    import core.consciousness.world_models

    assert core.consciousness.world_models is not None
