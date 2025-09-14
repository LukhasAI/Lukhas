#!/usr/bin/env python3
"""
LUKHAS AI Trace Module
=====================
Drift monitoring and harmonization components for Trinity Framework compliance.

Trinity Framework: ⚛️🧠🛡️
- ⚛️ Identity: Symbolic integrity preservation
- 🧠 Consciousness: Pattern learning and adaptation
- 🛡️ Guardian: Ethical drift detection and correction
"""

from .drift_harmonizer import (
    DriftAnalysis,
    DriftHarmonizer,
    DriftSeverity,
    RealignmentStrategy,
)
from .drift_metrics import DriftTracker

__version__ = "1.0.0"
__author__ = "LUKHAS AI Guardian System"
__triad_compliance__ = True

# Export main classes
__all__ = [
    "DriftAnalysis",
    "DriftHarmonizer",
    "DriftSeverity",
    "DriftTracker",
    "RealignmentStrategy",
]
