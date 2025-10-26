#!/usr/bin/env python3
"""
Integration tests for Agent Coordination
"""
import pytest


def test_agent_coordination_import():
    """Test that agent_coordination can be imported"""
    import matriz.consciousness.reflection.agent_coordination

    assert matriz.consciousness.reflection.agent_coordination is not None
