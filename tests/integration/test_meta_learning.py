#!/usr/bin/env python3
"""
Integration tests for Meta Learning
"""
import pytest


def test_meta_learning_import():
    """Test that meta_learning can be imported"""
    import matriz.consciousness.reflection.meta_learning

    assert matriz.consciousness.reflection.meta_learning is not None
