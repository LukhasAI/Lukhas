"""
Self-Healing Automation Dashboard
=================================
Unified interface for monitoring and controlling all automated fix systems in LUKHAS.

Components:
- SelfHealingDashboard: Main dashboard interface
- SystemHealthMetrics: Health monitoring data structures
- DashboardState: Configuration and state management

Trinity Framework Integration: ⚛️🧠🛡️
"""

from .self_healing_dashboard import (
    SelfHealingDashboard,
    SystemHealthMetrics,
    DashboardState
)

__all__ = [
    "SelfHealingDashboard",
    "SystemHealthMetrics", 
    "DashboardState"
]