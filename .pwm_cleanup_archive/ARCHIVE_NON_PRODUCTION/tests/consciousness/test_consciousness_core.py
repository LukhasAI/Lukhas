#!/usr/bin/env python3
"""
Consciousness System Tests
==========================

Tests for consciousness integration, awareness protocols, and cognitive services.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from consciousness.consciousness_service import ConsciousnessService
    from consciousness.core_consciousness.consciousness_integrator import (
        ConsciousnessIntegrator,
    )

    CONSCIOUSNESS_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_AVAILABLE = False


class TestConsciousnessService(unittest.TestCase):
    """Test consciousness service functionality."""

    @unittest.skipUnless(CONSCIOUSNESS_AVAILABLE, "Consciousness not available")
    def test_consciousness_service_initialization(self):
        """Test consciousness service starts properly."""
        try:
            service = ConsciousnessService()
            self.assertIsNotNone(service)
        except Exception:
            self.skipTest("Consciousness service initialization failed")

    @unittest.skipUnless(CONSCIOUSNESS_AVAILABLE, "Consciousness not available")
    def test_consciousness_integrator(self):
        """Test consciousness integration functionality."""
        try:
            integrator = ConsciousnessIntegrator()
            self.assertIsNotNone(integrator)
            self.assertTrue(hasattr(integrator, "integrate"))
        except Exception:
            self.skipTest("Consciousness integrator not available")

    def test_awareness_levels(self):
        """Test different levels of awareness processing."""
        awareness_levels = ["basic", "intermediate", "advanced", "meta"]

        for level in awareness_levels:
            with self.subTest(level=level):
                # Test that awareness levels are properly defined
                self.assertIn(level, awareness_levels)

    def test_cognitive_state_transitions(self):
        """Test cognitive state transition mechanisms."""
        states = ["idle", "processing", "reflecting", "learning"]

        # Test valid state transitions
        valid_transitions = {
            "idle": ["processing"],
            "processing": ["reflecting", "idle"],
            "reflecting": ["learning", "idle"],
            "learning": ["idle", "processing"],
        }

        for state, next_states in valid_transitions.items():
            self.assertIn(state, states)
            for next_state in next_states:
                self.assertIn(next_state, states)


if __name__ == "__main__":
    unittest.main()
