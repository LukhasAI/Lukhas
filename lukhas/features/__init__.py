"""
Feature flags module for LUKHAS AI.

This module provides a privacy-first feature flags system for controlled rollouts,
A/B testing, and safe experimentation without third-party dependencies.
"""

from lukhas.features.flags_service import FeatureFlagsService, FlagType

__all__ = ["FeatureFlagsService", "FlagType"]
