"""

#TAG:governance
#TAG:oversight
#TAG:neuroplastic
#TAG:colony


Monitoring and Observability for LUKHAS Orchestrators
Provides comprehensive monitoring, health checks, and alerting capabilities
"""

import structlog

# Initialize logger for ΛTRACE using structlog
from core.common import get_logger
logger.info("ΛTRACE: Initializing orchestration.monitoring package.")

# Import existing modules
from . import reflection_layer

# Import guardian system
try:
    from .remediator_agent import RemediatorAgent, RemediationType, SubAgentStatus
    from .sub_agents import EthicsGuardian, MemoryCleaner
    GUARDIAN_SYSTEM_AVAILABLE = True
except ImportError:
    logger.warning("Guardian system modules not available")
    GUARDIAN_SYSTEM_AVAILABLE = False

# Import new production monitoring modules (with fallbacks)
try:
    from .health_checks import (
        HealthChecker,
        HealthStatus,
        ComponentHealth,
        get_health_checker
    )
    HEALTH_CHECKS_AVAILABLE = True
except ImportError:
    logger.warning("Health checks module not available")
    HEALTH_CHECKS_AVAILABLE = False

try:
    from .metrics_collector import (
        MetricsCollector,
        OrchestrationMetric,
        MetricType,
        get_metrics_collector
    )
    METRICS_AVAILABLE = True
except ImportError:
    logger.warning("Metrics collector module not available")
    METRICS_AVAILABLE = False

try:
    from .dashboard_server import (
        DashboardServer,
        start_monitoring_dashboard,
        stop_monitoring_dashboard
    )
    DASHBOARD_AVAILABLE = True
except ImportError:
    logger.warning("Dashboard server module not available")
    DASHBOARD_AVAILABLE = False

try:
    from .alerts import (
        AlertManager,
        Alert,
        AlertSeverity,
        AlertRule,
        get_alert_manager
    )
    ALERTS_AVAILABLE = True
except ImportError:
    logger.warning("Alerts module not available")
    ALERTS_AVAILABLE = False

# Define what is explicitly exported by this package
__all__ = [
    # Legacy guardian system exports
    "reflection_layer",
]

# Add guardian system exports if available
if GUARDIAN_SYSTEM_AVAILABLE:
    __all__.extend([
        'RemediatorAgent',
        'RemediationType',
        'SubAgentStatus',
        'EthicsGuardian',
        'MemoryCleaner'
    ])

# Add new exports if available
if HEALTH_CHECKS_AVAILABLE:
    __all__.extend([
        'HealthChecker',
        'HealthStatus', 
        'ComponentHealth',
        'get_health_checker'
    ])

if METRICS_AVAILABLE:
    __all__.extend([
        'MetricsCollector',
        'OrchestrationMetric',
        'MetricType',
        'get_metrics_collector'
    ])

if DASHBOARD_AVAILABLE:
    __all__.extend([
        'DashboardServer',
        'start_monitoring_dashboard',
        'stop_monitoring_dashboard'
    ])

if ALERTS_AVAILABLE:
    __all__.extend([
        'AlertManager',
        'Alert',
        'AlertSeverity',
        'AlertRule',
        'get_alert_manager'
    ])

logger.info("ΛTRACE: orchestration.monitoring package initialized successfully.")
