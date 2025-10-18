#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Core Monitoring Module

Copyright (c) 2025 LUKHAS Cognitive AI Development Team
All rights reserved.

This file is part of the LUKHAS Cognitive system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

Core monitoring module providing unified drift detection and system health
monitoring capabilities. Exports the UnifiedDriftMonitor system and related
components for comprehensive Cognitive system monitoring.

For more information, visit: https://ai
"""
import streamlit as st

# ΛTRACE: Core monitoring module initialization
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 12 - Drift Detection Integration

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@ai"
__status__ = "Production"

from .drift_monitor import (
    DriftAlert,
    DriftType,
    InterventionType,
    UnifiedDriftMonitor,
    UnifiedDriftScore,
    create_drift_monitor,
)

__all__ = [
    "DriftAlert",
    "DriftType",
    "InterventionType",
    "UnifiedDriftMonitor",
    "UnifiedDriftScore",
    "create_drift_monitor",
]
