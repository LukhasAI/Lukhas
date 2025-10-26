#!/usr/bin/env python3
"""
Integration tests for Parallel Reality Simulator
"""
import pytest


def test_parallel_reality_simulator_import():
    """Test that parallel_reality_simulator can be imported"""
    import matriz.consciousness.dream.parallel_reality_simulator

    assert matriz.consciousness.dream.parallel_reality_simulator is not None
