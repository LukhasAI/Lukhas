#!/usr/bin/env python3
"""
Integration tests for QI Mesh Integrator
"""
import pytest


def test_qi_mesh_integrator_import():
    """Test that qi_mesh_integrator can be imported"""
    import core.consciousness.qi_mesh_integrator

    assert core.consciousness.qi_mesh_integrator is not None
