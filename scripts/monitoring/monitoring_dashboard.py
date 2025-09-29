#!/usr/bin/env python3
"""
Monitoring Dashboard alias for test compatibility
"""

# Import the actual dashboard implementation
from lukhas.core.observability.unified_monitoring_dashboard import UnifiedMonitoringDashboard as MonitoringDashboard

# Export for backward compatibility
__all__ = ["MonitoringDashboard"]
