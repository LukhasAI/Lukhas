"""
LUKHAS AI Observability and Monitoring System

This module provides comprehensive observability and monitoring capabilities
for the LUKHAS AI system, integrating Guardian System monitoring, consciousness
awareness tracking, system health observability, and Constellation Framework
monitoring into a unified platform.

Key Components:
- Guardian System Monitoring Dashboard
- Consciousness Awareness Monitoring System
- System Health Monitor
- Comprehensive Alerting System
- Constellation Framework Monitor
- Unified Monitoring Dashboard

Features:
- Real-time monitoring with drift detection (0.15 threshold)
- Consciousness awareness state tracking and analysis
- System health observability with performance metrics
- Comprehensive alerting with compliance audit trails
- Constellation Framework monitoring (⚛️🧠🛡️)
- Authentication and API performance tracking
- Multi-channel notifications and escalation
- Compliance monitoring (GDPR/CCPA/HIPAA/SOC2)
- Predictive analytics and optimization recommendations

Usage:
    from candidate.core.observability import (
        UnifiedMonitoringDashboard,
        GuardianMonitoringDashboard,
        AwarenessMonitoringSystem,
        SystemHealthMonitor,
        ComprehensiveAlertingSystem,
        ConstellationFrameworkMonitor
    )

    # Initialize unified monitoring
    dashboard = UnifiedMonitoringDashboard()

    # Get real-time system status
    status = await dashboard.get_dashboard_data(session_id)

    # Access individual monitoring systems
    guardian = dashboard.guardian_monitor
    consciousness = dashboard.consciousness_monitor
    health = dashboard.health_monitor

#TAG:observability
#TAG:monitoring
#TAG:dashboard
#TAG:constellation
#TAG:guardian
"""
import logging
import time
from typing import Any, Dict, Optional

import streamlit as st

logger = logging.getLogger(__name__)

# Import legacy collector
try:
    from .collector import Collector

    logger.debug("Imported Collector from .collector")
except ImportError as e:
    logger.warning(f"Could not import Collector: {e}")
    Collector = None

# Import monitoring systems
try:
    from .unified_monitoring_dashboard import (
        AlertPriority,
        DashboardConfig,
        DashboardData,
        DashboardMode,
        DashboardSession,
        UnifiedAlert,
        UnifiedMonitoringDashboard,
        ViewType,
    )

    UNIFIED_DASHBOARD_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Unified dashboard not available: {e}")
    UNIFIED_DASHBOARD_AVAILABLE = False

try:
    from candidate.governance.guardian.monitoring_dashboard import (
        AlertSeverity as GuardianAlertSeverity,
    )
    from candidate.governance.guardian.monitoring_dashboard import (
        ComplianceViolation,
        GuardianMonitoringDashboard,
        MonitoringMetric,
        MonitoringReport,
        MonitoringScope,
        ThreatDetection,
        ThreatLevel,
    )
    from candidate.governance.guardian.monitoring_dashboard import (
        SystemHealthStatus as GuardianHealthStatus,
    )

    GUARDIAN_MONITORING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Guardian monitoring not available: {e}")
    GUARDIAN_MONITORING_AVAILABLE = False

try:
    from candidate.consciousness.awareness.awareness_monitoring_system import (
        AttentionMode,
        AttentionPattern,
        AwarenessLevel,
        AwarenessMonitoringSystem,
        AwarenessReport,
        AwarenessSnapshot,
        CognitiveLoadLevel,
        ConsciousnessInsight,
        ConsciousnessState,
    )

    CONSCIOUSNESS_MONITORING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Consciousness monitoring not available: {e}")
    CONSCIOUSNESS_MONITORING_AVAILABLE = False

try:
    from .system_health_monitor import (
        ComponentHealth,
        ComponentType,
        HealthMetric,
        HealthReport,
        HealthStatus,
        MetricType,
        SystemHealthMonitor,
        SystemHealthSnapshot,
    )

    HEALTH_MONITORING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Health monitoring not available: {e}")
    HEALTH_MONITORING_AVAILABLE = False

try:
    from .alerting_system import (
        Alert,
        AlertCategory,
        AlertingMetrics,
        AlertRule,
        AlertSeverity,
        AlertStatus,
        ComplianceAuditEntry,
        ComplianceRegulation,
        ComprehensiveAlertingSystem,
        NotificationChannel,
        NotificationConfig,
    )

    ALERTING_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Alerting system not available: {e}")
    ALERTING_SYSTEM_AVAILABLE = False

try:
    from .constellation_framework_monitor import (
        APIPerformanceMetric,
        AuthenticationEvent,
        InteractionType,
        PerformanceMetric,
        ConstellationComponent,
        ConstellationFrameworkMonitor,
        ConstellationHealthStatus,
        ConstellationInteraction,
        ConstellationReport,
    )

    TRINITY_MONITORING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Constellation monitoring not available: {e}")
    TRINITY_MONITORING_AVAILABLE = False


class ObservabilityManager:
    """
    Centralized observability manager for LUKHAS AI

    Provides a single point of access to all monitoring systems
    with coordinated initialization, configuration, and lifecycle management.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Monitoring systems
        self.unified_dashboard: Optional[UnifiedMonitoringDashboard] = None
        self.guardian_monitor: Optional[GuardianMonitoringDashboard] = None
        self.consciousness_monitor: Optional[AwarenessMonitoringSystem] = None
        self.health_monitor: Optional[SystemHealthMonitor] = None
        self.alerting_system: Optional[ComprehensiveAlertingSystem] = None
        self.constellation_monitor: Optional[ConstellationFrameworkMonitor] = None

        # System state
        self.initialized = False
        self.monitoring_active = False

        logger.info("🔍 Observability Manager initialized")

    async def initialize_all_systems(self) -> dict[str, bool]:
        """Initialize all available monitoring systems"""

        initialization_results = {}

        try:
            # Initialize Constellation Framework monitoring first (foundation)
            if TRINITY_MONITORING_AVAILABLE:
                self.constellation_monitor = ConstellationFrameworkMonitor(self.config.get("constellation_monitoring", {}))
                initialization_results["constellation_monitoring"] = True
                logger.info("✅ Constellation Framework monitoring initialized")
            else:
                initialization_results["constellation_monitoring"] = False
                logger.warning("⚠️ Constellation Framework monitoring not available")

            # Initialize Guardian monitoring
            if GUARDIAN_MONITORING_AVAILABLE:
                self.guardian_monitor = GuardianMonitoringDashboard(self.config.get("guardian_monitoring", {}))
                initialization_results["guardian_monitoring"] = True
                logger.info("✅ Guardian monitoring initialized")
            else:
                initialization_results["guardian_monitoring"] = False
                logger.warning("⚠️ Guardian monitoring not available")

            # Initialize consciousness monitoring
            if CONSCIOUSNESS_MONITORING_AVAILABLE:
                self.consciousness_monitor = AwarenessMonitoringSystem(self.config.get("consciousness_monitoring", {}))
                initialization_results["consciousness_monitoring"] = True
                logger.info("✅ Consciousness monitoring initialized")
            else:
                initialization_results["consciousness_monitoring"] = False
                logger.warning("⚠️ Consciousness monitoring not available")

            # Initialize system health monitoring
            if HEALTH_MONITORING_AVAILABLE:
                self.health_monitor = SystemHealthMonitor(self.config.get("health_monitoring", {}))
                initialization_results["health_monitoring"] = True
                logger.info("✅ System health monitoring initialized")
            else:
                initialization_results["health_monitoring"] = False
                logger.warning("⚠️ System health monitoring not available")

            # Initialize alerting system
            if ALERTING_SYSTEM_AVAILABLE:
                self.alerting_system = ComprehensiveAlertingSystem(self.config.get("alerting", {}))
                initialization_results["alerting_system"] = True
                logger.info("✅ Alerting system initialized")
            else:
                initialization_results["alerting_system"] = False
                logger.warning("⚠️ Alerting system not available")

            # Initialize unified dashboard last (integrates all others)
            if UNIFIED_DASHBOARD_AVAILABLE:
                dashboard_config = DashboardConfig(**self.config.get("unified_dashboard", {}))
                self.unified_dashboard = UnifiedMonitoringDashboard(dashboard_config)
                initialization_results["unified_dashboard"] = True
                logger.info("✅ Unified dashboard initialized")
            else:
                initialization_results["unified_dashboard"] = False
                logger.warning("⚠️ Unified dashboard not available")

            self.initialized = True
            self.monitoring_active = True

            # Log initialization summary
            successful_systems = sum(1 for success in initialization_results.values() if success)
            total_systems = len(initialization_results)

            logger.info(
                f"🔍 Observability initialization complete: {successful_systems}/{total_systems} systems active"
            )

            return initialization_results

        except Exception as e:
            logger.error(f"❌ Observability initialization failed: {e}")
            self.initialized = False
            return initialization_results

    def get_system_status(self) -> dict[str, Any]:
        """Get current observability system status"""

        return {
            "initialized": self.initialized,
            "monitoring_active": self.monitoring_active,
            "systems_status": {
                "unified_dashboard": ("active" if self.unified_dashboard else "not_available"),
                "guardian_monitor": ("active" if self.guardian_monitor else "not_available"),
                "consciousness_monitor": ("active" if self.consciousness_monitor else "not_available"),
                "health_monitor": "active" if self.health_monitor else "not_available",
                "alerting_system": ("active" if self.alerting_system else "not_available"),
                "constellation_monitor": ("active" if self.constellation_monitor else "not_available"),
            },
            "availability": {
                "unified_dashboard": UNIFIED_DASHBOARD_AVAILABLE,
                "guardian_monitoring": GUARDIAN_MONITORING_AVAILABLE,
                "consciousness_monitoring": CONSCIOUSNESS_MONITORING_AVAILABLE,
                "health_monitoring": HEALTH_MONITORING_AVAILABLE,
                "alerting_system": ALERTING_SYSTEM_AVAILABLE,
                "constellation_monitoring": TRINITY_MONITORING_AVAILABLE,
            },
        }


# Create default observability manager instance
default_observability_manager = ObservabilityManager()

# Export all components
__all__ = [
    "ALERTING_SYSTEM_AVAILABLE",
    "CONSCIOUSNESS_MONITORING_AVAILABLE",
    "GUARDIAN_MONITORING_AVAILABLE",
    "HEALTH_MONITORING_AVAILABLE",
    "TRINITY_MONITORING_AVAILABLE",
    # Availability flags
    "UNIFIED_DASHBOARD_AVAILABLE",
    # Legacy collector
    "Collector",
    # Manager
    "ObservabilityManager",
    "default_observability_manager",
]

# Conditionally export available components
if UNIFIED_DASHBOARD_AVAILABLE:
    __all__.extend(
        [
            "AlertPriority",
            "DashboardConfig",
            "DashboardData",
            "DashboardMode",
            "DashboardSession",
            "UnifiedAlert",
            "UnifiedMonitoringDashboard",
            "ViewType",
        ]
    )

if GUARDIAN_MONITORING_AVAILABLE:
    __all__.extend(
        [
            "ComplianceViolation",
            "GuardianAlertSeverity",
            "GuardianHealthStatus",
            "GuardianMonitoringDashboard",
            "MonitoringMetric",
            "MonitoringReport",
            "MonitoringScope",
            "ThreatDetection",
            "ThreatLevel",
        ]
    )

if CONSCIOUSNESS_MONITORING_AVAILABLE:
    __all__.extend(
        [
            "AttentionMode",
            "AttentionPattern",
            "AwarenessLevel",
            "AwarenessMonitoringSystem",
            "AwarenessReport",
            "AwarenessSnapshot",
            "CognitiveLoadLevel",
            "ConsciousnessInsight",
            "ConsciousnessState",
        ]
    )

if HEALTH_MONITORING_AVAILABLE:
    __all__.extend(
        [
            "ComponentHealth",
            "ComponentType",
            "HealthMetric",
            "HealthReport",
            "HealthStatus",
            "MetricType",
            "SystemHealthMonitor",
            "SystemHealthSnapshot",
        ]
    )

if ALERTING_SYSTEM_AVAILABLE:
    __all__.extend(
        [
            "Alert",
            "AlertCategory",
            "AlertRule",
            "AlertSeverity",
            "AlertStatus",
            "AlertingMetrics",
            "ComplianceAuditEntry",
            "ComplianceRegulation",
            "ComprehensiveAlertingSystem",
            "NotificationChannel",
            "NotificationConfig",
        ]
    )

if TRINITY_MONITORING_AVAILABLE:
    __all__.extend(
        [
            "APIPerformanceMetric",
            "AuthenticationEvent",
            "InteractionType",
            "PerformanceMetric",
            "ConstellationComponent",
            "ConstellationFrameworkMonitor",
            "ConstellationHealthStatus",
            "ConstellationInteraction",
            "ConstellationReport",
        ]
    )

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(
    f"🔍 LUKHAS AI Observability module loaded - {len([x for x in [UNIFIED_DASHBOARD_AVAILABLE, GUARDIAN_MONITORING_AVAILABLE, CONSCIOUSNESS_MONITORING_AVAILABLE, HEALTH_MONITORING_AVAILABLE, ALERTING_SYSTEM_AVAILABLE, TRINITY_MONITORING_AVAILABLE] if x])}/6 systems available"
)
