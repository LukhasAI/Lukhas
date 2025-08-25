#!/usr/bin/env python3
"""
LUKHAS Meta Dashboard
=====================
Real-time monitoring dashboard for symbolic systems, drift analysis,
and persona coherence tracking.

Components:
- FastAPI server with WebSocket streaming
- Drift analysis and trending
- Trinity coherence monitoring
- Symbolic collapse visualization
- Persona distribution analytics
"""

__version__ = "1.0.0"
__author__ = "LUKHAS AGI"

from .dashboard_server import app, start_dashboard
from .utils import (
    calculate_drift_trends,
    entropy_color_code,
    load_meta_metrics,
    parse_jsonl_snapshots,
)

__all__ = [
    "app",
    "start_dashboard",
    "load_meta_metrics",
    "parse_jsonl_snapshots",
    "calculate_drift_trends",
    "entropy_color_code",
]
