#!/usr/bin/env python3
"""
Module: monitoring_dashboard.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Monitoring Dashboard alias for test compatibility
"""

# Import the actual dashboard implementation
from core.observability.unified_monitoring_dashboard import UnifiedMonitoringDashboard as MonitoringDashboard

# Export for backward compatibility
__all__ = ["MonitoringDashboard"]
