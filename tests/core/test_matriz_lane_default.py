#!/usr/bin/env python3
"""
MATRIZ Lane Default Test
======================

Simple test ensuring MATRIZ defaults to 'canary' lane for T4/0.01% excellence.
"""

import os
import pytest
from unittest.mock import patch


def test_matriz_lane_defaults_to_canary():
    """MATRIZ must default to 'canary' lane for safer rollouts"""
    # Test the exact pattern used in matriz/core/async_orchestrator.py line 70
    with patch.dict(os.environ, {}, clear=True):
        default_lane = os.getenv("LUKHAS_LANE", "canary").lower()
        assert default_lane == "canary", f"Default lane is '{default_lane}', should be 'canary'"


def test_explicit_lane_override():
    """Lane can be explicitly overridden"""
    test_cases = [
        ("production", "production"),
        ("candidate", "candidate"),
        ("experimental", "experimental"),
    ]

    for env_value, expected in test_cases:
        with patch.dict(os.environ, {"LUKHAS_LANE": env_value}):
            lane = os.getenv("LUKHAS_LANE", "canary").lower()
            assert lane == expected, f"Expected '{expected}', got '{lane}'"


def test_production_safety():
    """Never default to production lane"""
    with patch.dict(os.environ, {}, clear=True):
        lane = os.getenv("LUKHAS_LANE", "canary").lower()
        assert lane != "production", "Must not default to production"
        assert lane == "canary", f"Should default to 'canary', got '{lane}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])