"""
Unified Monitoring Dashboard for LUKHAS AI

This module provides a comprehensive unified monitoring dashboard that
integrates Guardian System monitoring, consciousness awareness tracking,
system health observability, and real-time debug interfaces into a
single cohesive monitoring platform for the LUKHAS AI system.

Features:
- Unified monitoring dashboard interface
- Real-time system status visualization
- Guardian System integration with drift monitoring
- Consciousness awareness state tracking
- System health and performance monitoring
- Interactive debug interfaces
- Trinity Framework monitoring (⚛️🧠🛡️)
- Compliance and audit trail visualization
- Alert management and notification center
- Predictive analytics dashboard
- Performance optimization recommendations
- Administrative monitoring tools

#TAG:observability
#TAG:dashboard
#TAG:monitoring
#TAG:unified
#TAG:trinity
"""

import asyncio
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# Import monitoring systems
try:
    from .system_health_monitor import ComponentType, HealthStatus, SystemHealthMonitor
except ImportError:
    SystemHealthMonitor = None
    ComponentType = None
    HealthStatus = None

try:
    from candidate.governance.guardian.monitoring_dashboard import (
        AlertSeverity,
        GuardianMonitoringDashboard,
        MonitoringScope,
    )
except ImportError:
    GuardianMonitoringDashboard = None
    MonitoringScope = None
    AlertSeverity = None

try:
    from candidate.consciousness.awareness.awareness_monitoring_system import (
        AwarenessLevel,
        AwarenessMonitoringSystem,
    )
except ImportError:
    AwarenessMonitoringSystem = None
    AwarenessLevel = None

logger = logging.getLogger(__name__)


class DashboardMode(Enum):
    """Dashboard display modes"""

    OVERVIEW = "overview"
    DETAILED = "detailed"
    GUARDIAN_FOCUS = "guardian_focus"
    CONSCIOUSNESS_FOCUS = "consciousness_focus"
    HEALTH_FOCUS = "health_focus"
    DEBUG = "debug"
    ADMIN = "admin"


class ViewType(Enum):
    """Dashboard view types"""

    REAL_TIME = "real_time"
    HISTORICAL = "historical"
    PREDICTIVE = "predictive"
    COMPARATIVE = "comparative"
    DIAGNOSTIC = "diagnostic"


class AlertPriority(Enum):
    """Alert priority levels"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class DashboardConfig:
    """Dashboard configuration settings"""

    # Display settings
    refresh_interval: float = 2.0  # seconds
    max_data_points: int = 1000
    auto_refresh: bool = True

    # Monitoring settings
    enable_guardian_monitoring: bool = True
    enable_consciousness_monitoring: bool = True
    enable_health_monitoring: bool = True
    enable_predictive_analytics: bool = True

    # Alert settings
    enable_alert_notifications: bool = True
    alert_sound_enabled: bool = False
    email_notifications: bool = False

    # Performance settings
    enable_real_time_updates: bool = True
    data_compression: bool = True
    cache_enabled: bool = True

    # Security settings
    require_authentication: bool = True
    audit_dashboard_access: bool = True
    session_timeout: int = 3600  # seconds


@dataclass
class DashboardSession:
    """Dashboard user session"""

    session_id: str
    user_id: Optional[str]
    created_at: datetime
    last_active: datetime

    # Session preferences
    current_mode: DashboardMode = DashboardMode.OVERVIEW
    current_view: ViewType = ViewType.REAL_TIME
    selected_components: set[str] = field(default_factory=set)

    # Customization
    custom_filters: dict[str, Any] = field(default_factory=dict)
    favorite_views: list[str] = field(default_factory=list)
    alert_preferences: dict[str, Any] = field(default_factory=dict)

    # Security
    ip_address: Optional[str] = None
    permissions: set[str] = field(default_factory=set)


@dataclass
class UnifiedAlert:
    """Unified alert from any monitoring system"""

    alert_id: str
    source_system: str
    alert_type: str
    title: str
    message: str

    # Classification
    priority: AlertPriority
    category: str
    component: Optional[str] = None

    # Timing
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Status
    acknowledged: bool = False
    resolved: bool = False
    suppressed: bool = False

    # Context
    source_data: dict[str, Any] = field(default_factory=dict)
    affected_systems: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)

    # Trinity Framework context
    trinity_impact: dict[str, float] = field(default_factory=dict)  # ⚛️🧠🛡️


@dataclass
class DashboardData:
    """Unified dashboard data structure"""

    timestamp: datetime
    mode: DashboardMode
    view: ViewType

    # System overview
    overall_status: str
    overall_health: float
    system_uptime: float

    # Guardian System data
    guardian_data: dict[str, Any] = field(default_factory=dict)
    drift_score: float = 0.0
    threat_level: str = "benign"
    compliance_score: float = 1.0

    # Consciousness data
    consciousness_data: dict[str, Any] = field(default_factory=dict)
    awareness_level: str = "standard"
    cognitive_load: float = 0.5
    consciousness_health: float = 1.0

    # System health data
    health_data: dict[str, Any] = field(default_factory=dict)
    component_health: dict[str, float] = field(default_factory=dict)
    resource_utilization: dict[str, float] = field(default_factory=dict)

    # Performance metrics
    performance_data: dict[str, Any] = field(default_factory=dict)
    response_times: list[float] = field(default_factory=list)
    throughput: float = 0.0
    error_rate: float = 0.0

    # Alert summary
    active_alerts: list[UnifiedAlert] = field(default_factory=list)
    alert_counts_by_priority: dict[str, int] = field(default_factory=dict)

    # Trinity Framework status
    trinity_status: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Predictive insights
    predictions: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class UnifiedMonitoringDashboard:
    """
    Unified monitoring dashboard for LUKHAS AI

    Provides comprehensive real-time monitoring with integrated views
    of Guardian System, consciousness awareness, system health, and
    performance metrics with interactive debug interfaces and
    administrative monitoring tools.
    """

    def __init__(self, config: Optional[DashboardConfig] = None):
        self.config = config or DashboardConfig()

        # Core monitoring systems
        self.guardian_monitor: Optional[GuardianMonitoringDashboard] = None
        self.consciousness_monitor: Optional[AwarenessMonitoringSystem] = None
        self.health_monitor: Optional[SystemHealthMonitor] = None

        # Dashboard state
        self.dashboard_active = True
        self.sessions: dict[str, DashboardSession] = {}
        self.unified_alerts: deque = deque(maxlen=1000)

        # Data cache
        self.cached_data: dict[str, DashboardData] = {}
        self.cache_timestamps: dict[str, datetime] = {}

        # Performance metrics
        self.dashboard_metrics = {
            "dashboard_requests": 0,
            "active_sessions": 0,
            "alerts_processed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
            "uptime_seconds": 0,
            "last_updated": datetime.now().isoformat(),
        }

        # Initialize dashboard
        asyncio.create_task(self._initialize_dashboard())

        logger.info("🖥️ Unified Monitoring Dashboard initialized")

    async def _initialize_dashboard(self):
        """Initialize the unified monitoring dashboard"""

        try:
            # Initialize monitoring systems
            await self._initialize_monitoring_systems()

            # Start dashboard loops
            asyncio.create_task(self._dashboard_update_loop())
            asyncio.create_task(self._alert_processing_loop())
            asyncio.create_task(self._session_management_loop())
            asyncio.create_task(self._cache_cleanup_loop())

            logger.info("✅ Unified dashboard loops started")

        except Exception as e:
            logger.error(f"❌ Dashboard initialization failed: {e}")

    async def _initialize_monitoring_systems(self):
        """Initialize all monitoring systems"""

        try:
            # Initialize Guardian monitoring
            if self.config.enable_guardian_monitoring and GuardianMonitoringDashboard:
                self.guardian_monitor = GuardianMonitoringDashboard()
                logger.info("✅ Guardian monitoring initialized")

            # Initialize consciousness monitoring
            if self.config.enable_consciousness_monitoring and AwarenessMonitoringSystem:
                self.consciousness_monitor = AwarenessMonitoringSystem()
                logger.info("✅ Consciousness monitoring initialized")

            # Initialize health monitoring
            if self.config.enable_health_monitoring and SystemHealthMonitor:
                self.health_monitor = SystemHealthMonitor()
                logger.info("✅ Health monitoring initialized")

        except Exception as e:
            logger.error(f"❌ Monitoring systems initialization failed: {e}")

    async def _dashboard_update_loop(self):
        """Main dashboard update loop"""

        while self.dashboard_active:
            try:
                # Update cached data for all active sessions
                await self._update_dashboard_cache()

                # Update performance metrics
                await self._update_dashboard_metrics()

                await asyncio.sleep(self.config.refresh_interval)

            except Exception as e:
                logger.error(f"❌ Dashboard update error: {e}")
                await asyncio.sleep(5)

    async def _alert_processing_loop(self):
        """Background loop for processing alerts from all systems"""

        while self.dashboard_active:
            try:
                await self._collect_and_process_alerts()
                await asyncio.sleep(1.0)  # High frequency for alerts

            except Exception as e:
                logger.error(f"❌ Alert processing error: {e}")
                await asyncio.sleep(5)

    async def _session_management_loop(self):
        """Background loop for managing dashboard sessions"""

        while self.dashboard_active:
            try:
                await self._cleanup_expired_sessions()
                await self._update_session_metrics()
                await asyncio.sleep(60)  # Every minute

            except Exception as e:
                logger.error(f"❌ Session management error: {e}")
                await asyncio.sleep(120)

    async def _cache_cleanup_loop(self):
        """Background loop for cache cleanup"""

        while self.dashboard_active:
            try:
                await self._cleanup_old_cache_data()
                await asyncio.sleep(300)  # Every 5 minutes

            except Exception as e:
                logger.error(f"❌ Cache cleanup error: {e}")
                await asyncio.sleep(600)

    async def create_session(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        permissions: Optional[set[str]] = None,
    ) -> DashboardSession:
        """Create new dashboard session"""

        session_id = f"session_{uuid.uuid4().hex[:12]}"
        permissions = permissions or {"read"}

        session = DashboardSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            ip_address=ip_address,
            permissions=permissions,
        )

        self.sessions[session_id] = session

        logger.info(f"📱 Dashboard session created: {session_id}")

        return session

    async def get_dashboard_data(
        self,
        session_id: str,
        mode: DashboardMode = DashboardMode.OVERVIEW,
        view: ViewType = ViewType.REAL_TIME,
        time_range_hours: int = 24,
    ) -> DashboardData:
        """Get comprehensive dashboard data for session"""

        # Update session activity
        if session_id in self.sessions:
            self.sessions[session_id].last_active = datetime.now()
            self.sessions[session_id].current_mode = mode
            self.sessions[session_id].current_view = view

        # Check cache first
        cache_key = f"{session_id}_{mode.value}_{view.value}"

        if self.config.cache_enabled and cache_key in self.cached_data:
            cache_time = self.cache_timestamps.get(cache_key, datetime.min)
            if (datetime.now() - cache_time).total_seconds() < self.config.refresh_interval:
                self.dashboard_metrics["cache_hits"] += 1
                return self.cached_data[cache_key]

        # Generate fresh data
        self.dashboard_metrics["cache_misses"] += 1
        dashboard_data = await self._generate_dashboard_data(mode, view, time_range_hours)

        # Cache the data
        if self.config.cache_enabled:
            self.cached_data[cache_key] = dashboard_data
            self.cache_timestamps[cache_key] = datetime.now()

        # Update metrics
        self.dashboard_metrics["dashboard_requests"] += 1

        return dashboard_data

    async def _generate_dashboard_data(
        self, mode: DashboardMode, view: ViewType, time_range_hours: int
    ) -> DashboardData:
        """Generate fresh dashboard data"""

        timestamp = datetime.now()

        # Initialize dashboard data
        dashboard_data = DashboardData(
            timestamp=timestamp,
            mode=mode,
            view=view,
            overall_status="healthy",
            overall_health=1.0,
            system_uptime=1.0,
        )

        try:
            # Collect Guardian System data
            if self.guardian_monitor:
                guardian_data = await self.guardian_monitor.get_dashboard_data(
                    scope=MonitoringScope.SYSTEM_WIDE if MonitoringScope else None,
                    time_range_hours=time_range_hours,
                )
                dashboard_data.guardian_data = guardian_data

                # Extract key metrics
                if "guardian" in guardian_data:
                    dashboard_data.drift_score = guardian_data["guardian"].get("current_drift_score", 0.0)

                if "security" in guardian_data:
                    dashboard_data.threat_level = guardian_data["security"].get("threat_level", "benign")

                if "compliance" in guardian_data:
                    dashboard_data.compliance_score = guardian_data["compliance"].get("score", 1.0)

            # Collect consciousness data
            if self.consciousness_monitor:
                consciousness_status = await self.consciousness_monitor.get_current_awareness_status()
                dashboard_data.consciousness_data = consciousness_status

                if consciousness_status:
                    dashboard_data.awareness_level = consciousness_status.get("awareness_level", "standard")
                    dashboard_data.cognitive_load = consciousness_status.get("cognitive_load_score", 0.5)
                    dashboard_data.consciousness_health = consciousness_status.get("performance_metrics", {}).get(
                        "overall_performance", 1.0
                    )

            # Collect system health data
            if self.health_monitor:
                health_status = await self.health_monitor.get_current_health_status()
                dashboard_data.health_data = health_status

                if health_status:
                    dashboard_data.overall_health = health_status.get("overall_health", 1.0)
                    dashboard_data.overall_status = health_status.get("system_status", "healthy")
                    dashboard_data.system_uptime = health_status.get("system_metrics", {}).get("uptime", 1.0)

                    # Extract component health
                    components = health_status.get("components", {})
                    dashboard_data.component_health = {
                        component: data.get("health", 1.0) for component, data in components.items()
                    }

                    # Extract resource utilization
                    system_metrics = health_status.get("system_metrics", {})
                    dashboard_data.resource_utilization = {
                        "cpu": system_metrics.get("cpu_usage", 0.0),
                        "memory": system_metrics.get("memory_usage", 0.0),
                        "disk": system_metrics.get("disk_usage", 0.0),
                    }

                    # Extract performance metrics
                    dashboard_data.performance_data = {
                        "response_time": system_metrics.get("avg_response_time", 0.0),
                        "error_rate": system_metrics.get("error_rate", 0.0),
                    }

                    dashboard_data.response_times = [system_metrics.get("avg_response_time", 0.0)]
                    dashboard_data.error_rate = system_metrics.get("error_rate", 0.0)

            # Collect active alerts
            dashboard_data.active_alerts = list(self.unified_alerts)[-50:]  # Last 50 alerts

            # Count alerts by priority
            alert_counts = defaultdict(int)
            for alert in dashboard_data.active_alerts:
                if not alert.resolved:
                    alert_counts[alert.priority.value] += 1
            dashboard_data.alert_counts_by_priority = dict(alert_counts)

            # Trinity Framework status
            dashboard_data.trinity_status = {
                "identity": {  # ⚛️
                    "health": dashboard_data.component_health.get("identity", 1.0),
                    "status": "operational",
                },
                "consciousness": {  # 🧠
                    "health": dashboard_data.consciousness_health,
                    "awareness_level": dashboard_data.awareness_level,
                    "cognitive_load": dashboard_data.cognitive_load,
                },
                "guardian": {  # 🛡️
                    "health": dashboard_data.component_health.get("guardian", 1.0),
                    "drift_score": dashboard_data.drift_score,
                    "threat_level": dashboard_data.threat_level,
                    "compliance_score": dashboard_data.compliance_score,
                },
            }

            # Generate predictions and recommendations based on mode
            if mode in [DashboardMode.DETAILED, DashboardMode.DEBUG] and self.config.enable_predictive_analytics:
                dashboard_data.predictions = await self._generate_predictions(dashboard_data)
                dashboard_data.recommendations = await self._generate_recommendations(dashboard_data)

        except Exception as e:
            logger.error(f"❌ Dashboard data generation failed: {e}")
            dashboard_data.overall_status = "error"
            dashboard_data.overall_health = 0.0

        return dashboard_data

    async def _collect_and_process_alerts(self):
        """Collect alerts from all monitoring systems"""

        try:
            new_alerts = []

            # Collect Guardian alerts
            if self.guardian_monitor:
                guardian_data = await self.guardian_monitor.get_dashboard_data()

                if "alerts" in guardian_data and "recent" in guardian_data["alerts"]:
                    for alert_data in guardian_data["alerts"]["recent"]:
                        unified_alert = UnifiedAlert(
                            alert_id=f"guardian_{alert_data.get('id', uuid.uuid4().hex[:8])}",
                            source_system="guardian",
                            alert_type=alert_data.get("type", "unknown"),
                            title=f"Guardian Alert: {alert_data.get('type', 'Unknown')}",
                            message=alert_data.get("message", "No message"),
                            priority=self._convert_to_alert_priority(alert_data.get("severity", "info")),
                            category="guardian",
                            created_at=datetime.fromisoformat(alert_data.get("created_at", datetime.now().isoformat())),
                            source_data=alert_data,
                            trinity_impact={"guardian": 1.0},  # 🛡️
                        )
                        new_alerts.append(unified_alert)

            # Collect health monitoring alerts
            if self.health_monitor:
                health_status = await self.health_monitor.get_current_health_status()

                alerts_data = health_status.get("alerts", {})
                if alerts_data.get("critical", 0) > 0:
                    unified_alert = UnifiedAlert(
                        alert_id=f"health_{uuid.uuid4().hex[:8]}",
                        source_system="health_monitor",
                        alert_type="critical_health",
                        title="Critical Health Issues Detected",
                        message=f"{alerts_data['critical']} critical health issues detected",
                        priority=AlertPriority.CRITICAL,
                        category="health",
                        created_at=datetime.now(),
                        source_data=alerts_data,
                        trinity_impact={"identity": 0.3, "consciousness": 0.3, "guardian": 0.3},
                    )
                    new_alerts.append(unified_alert)

            # Collect consciousness alerts
            if self.consciousness_monitor:
                consciousness_status = await self.consciousness_monitor.get_current_awareness_status()

                stress_indicators = consciousness_status.get("stress_indicators", [])
                if stress_indicators:
                    unified_alert = UnifiedAlert(
                        alert_id=f"consciousness_{uuid.uuid4().hex[:8]}",
                        source_system="consciousness_monitor",
                        alert_type="consciousness_stress",
                        title="Consciousness Stress Detected",
                        message=f"Stress indicators: {', '.join(stress_indicators)}",
                        priority=AlertPriority.MEDIUM,
                        category="consciousness",
                        created_at=datetime.now(),
                        source_data=consciousness_status,
                        trinity_impact={"consciousness": 1.0},  # 🧠
                    )
                    new_alerts.append(unified_alert)

            # Add new alerts to unified queue
            for alert in new_alerts:
                self.unified_alerts.append(alert)
                self.dashboard_metrics["alerts_processed"] += 1

        except Exception as e:
            logger.error(f"❌ Alert collection failed: {e}")

    def _convert_to_alert_priority(self, severity: str) -> AlertPriority:
        """Convert severity string to AlertPriority"""

        severity_map = {
            "info": AlertPriority.INFO,
            "low": AlertPriority.LOW,
            "medium": AlertPriority.MEDIUM,
            "high": AlertPriority.HIGH,
            "critical": AlertPriority.CRITICAL,
            "emergency": AlertPriority.EMERGENCY,
        }

        return severity_map.get(severity.lower(), AlertPriority.INFO)

    async def _generate_predictions(self, dashboard_data: DashboardData) -> list[dict[str, Any]]:
        """Generate predictive insights"""

        predictions = []

        # Predict based on drift score trend
        if dashboard_data.drift_score > 0.1:
            predictions.append(
                {
                    "type": "drift_trend",
                    "prediction": "Drift score may exceed threshold",
                    "confidence": 0.7,
                    "time_frame": "next_2_hours",
                    "impact": "medium",
                }
            )

        # Predict based on cognitive load
        if dashboard_data.cognitive_load > 0.8:
            predictions.append(
                {
                    "type": "cognitive_overload",
                    "prediction": "Cognitive overload risk",
                    "confidence": 0.8,
                    "time_frame": "next_30_minutes",
                    "impact": "high",
                }
            )

        # Predict based on system health
        if dashboard_data.overall_health < 0.7:
            predictions.append(
                {
                    "type": "system_degradation",
                    "prediction": "System performance degradation",
                    "confidence": 0.75,
                    "time_frame": "next_1_hour",
                    "impact": "high",
                }
            )

        return predictions

    async def _generate_recommendations(self, dashboard_data: DashboardData) -> list[str]:
        """Generate optimization recommendations"""

        recommendations = []

        # Guardian recommendations
        if dashboard_data.drift_score > 0.12:
            recommendations.append("Consider drift mitigation measures")

        if dashboard_data.compliance_score < 0.95:
            recommendations.append("Review compliance procedures")

        # Consciousness recommendations
        if dashboard_data.cognitive_load > 0.75:
            recommendations.append("Implement load balancing strategies")

        if dashboard_data.awareness_level == "minimal":
            recommendations.append("Activate awareness enhancement protocols")

        # System health recommendations
        cpu_usage = dashboard_data.resource_utilization.get("cpu", 0)
        if cpu_usage > 80:
            recommendations.append("Optimize CPU usage - consider task distribution")

        memory_usage = dashboard_data.resource_utilization.get("memory", 0)
        if memory_usage > 85:
            recommendations.append("Memory usage high - consider cleanup procedures")

        # Trinity Framework recommendations
        trinity_health_avg = sum(component["health"] for component in dashboard_data.trinity_status.values()) / 3

        if trinity_health_avg < 0.8:
            recommendations.append("Trinity Framework health below optimal - review all components")

        return recommendations

    async def _update_dashboard_cache(self):
        """Update cached dashboard data"""

        # Update cache for commonly used views
        common_modes = [DashboardMode.OVERVIEW, DashboardMode.DETAILED]
        common_views = [ViewType.REAL_TIME, ViewType.HISTORICAL]

        for mode in common_modes:
            for view in common_views:
                cache_key = f"preload_{mode.value}_{view.value}"

                # Only update if cache is stale
                cache_time = self.cache_timestamps.get(cache_key, datetime.min)
                if (datetime.now() - cache_time).total_seconds() >= self.config.refresh_interval:
                    dashboard_data = await self._generate_dashboard_data(mode, view, 24)

                    if self.config.cache_enabled:
                        self.cached_data[cache_key] = dashboard_data
                        self.cache_timestamps[cache_key] = datetime.now()

    async def _update_dashboard_metrics(self):
        """Update dashboard performance metrics"""

        self.dashboard_metrics["active_sessions"] = len(
            [
                s
                for s in self.sessions.values()
                if (datetime.now() - s.last_active).total_seconds() < self.config.session_timeout
            ]
        )

        self.dashboard_metrics["uptime_seconds"] = (
            datetime.now() - datetime.fromisoformat(self.dashboard_metrics["last_updated"])
        ).total_seconds()

        self.dashboard_metrics["last_updated"] = datetime.now().isoformat()

    async def _cleanup_expired_sessions(self):
        """Clean up expired dashboard sessions"""

        current_time = datetime.now()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if (current_time - session.last_active).total_seconds() > self.config.session_timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"🗑️ Expired dashboard session cleaned up: {session_id}")

    async def _update_session_metrics(self):
        """Update session-related metrics"""

        active_count = len(
            [
                s
                for s in self.sessions.values()
                if (datetime.now() - s.last_active).total_seconds() < 300  # Active in last 5 minutes
            ]
        )

        self.dashboard_metrics["active_sessions"] = active_count

    async def _cleanup_old_cache_data(self):
        """Clean up old cached data"""

        current_time = datetime.now()
        expired_keys = []

        for cache_key, cache_time in self.cache_timestamps.items():
            if (current_time - cache_time).total_seconds() > 3600:  # 1 hour
                expired_keys.append(cache_key)

        for key in expired_keys:
            if key in self.cached_data:
                del self.cached_data[key]
            del self.cache_timestamps[key]

    async def acknowledge_alert(self, alert_id: str, session_id: str) -> bool:
        """Acknowledge an alert"""

        for alert in self.unified_alerts:
            if alert.alert_id == alert_id and not alert.acknowledged:
                alert.acknowledged = True
                alert.updated_at = datetime.now()

                logger.info(f"✅ Alert acknowledged: {alert_id} by session {session_id}")
                return True

        return False

    async def resolve_alert(self, alert_id: str, session_id: str) -> bool:
        """Resolve an alert"""

        for alert in self.unified_alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()

                logger.info(f"✅ Alert resolved: {alert_id} by session {session_id}")
                return True

        return False

    async def get_debug_interface_data(self, session_id: str) -> dict[str, Any]:
        """Get debug interface data"""

        session = self.sessions.get(session_id)
        if not session or "debug" not in session.permissions:
            return {"error": "Insufficient permissions"}

        debug_data = {
            "timestamp": datetime.now().isoformat(),
            "dashboard_metrics": self.dashboard_metrics.copy(),
            "active_sessions": len(self.sessions),
            "cached_data_count": len(self.cached_data),
            "alert_queue_size": len(self.unified_alerts),
            "monitoring_systems_status": {
                "guardian_monitor": self.guardian_monitor is not None,
                "consciousness_monitor": self.consciousness_monitor is not None,
                "health_monitor": self.health_monitor is not None,
            },
            "cache_statistics": {
                "cache_enabled": self.config.cache_enabled,
                "cache_hits": self.dashboard_metrics["cache_hits"],
                "cache_misses": self.dashboard_metrics["cache_misses"],
                "hit_rate": self.dashboard_metrics["cache_hits"]
                / max(1, self.dashboard_metrics["cache_hits"] + self.dashboard_metrics["cache_misses"])
                * 100,
            },
            "system_configuration": {
                "refresh_interval": self.config.refresh_interval,
                "auto_refresh": self.config.auto_refresh,
                "max_data_points": self.config.max_data_points,
                "session_timeout": self.config.session_timeout,
            },
        }

        return debug_data

    async def get_admin_interface_data(self, session_id: str) -> dict[str, Any]:
        """Get administrative interface data"""

        session = self.sessions.get(session_id)
        if not session or "admin" not in session.permissions:
            return {"error": "Insufficient permissions"}

        admin_data = {
            "timestamp": datetime.now().isoformat(),
            "system_overview": {
                "dashboard_active": self.dashboard_active,
                "total_sessions": len(self.sessions),
                "total_alerts_processed": self.dashboard_metrics["alerts_processed"],
                "uptime_hours": self.dashboard_metrics["uptime_seconds"] / 3600,
            },
            "session_details": [
                {
                    "session_id": s.session_id,
                    "user_id": s.user_id,
                    "created_at": s.created_at.isoformat(),
                    "last_active": s.last_active.isoformat(),
                    "current_mode": s.current_mode.value,
                    "ip_address": s.ip_address,
                    "permissions": list(s.permissions),
                }
                for s in self.sessions.values()
            ],
            "alert_management": {
                "total_alerts": len(self.unified_alerts),
                "unresolved_alerts": len([a for a in self.unified_alerts if not a.resolved]),
                "critical_alerts": len([a for a in self.unified_alerts if a.priority == AlertPriority.CRITICAL]),
                "alerts_by_system": {
                    system: len([a for a in self.unified_alerts if a.source_system == system])
                    for system in set(a.source_system for a in self.unified_alerts)
                },
            },
            "performance_metrics": self.dashboard_metrics.copy(),
            "configuration": {
                "monitoring_enabled": {
                    "guardian": self.config.enable_guardian_monitoring,
                    "consciousness": self.config.enable_consciousness_monitoring,
                    "health": self.config.enable_health_monitoring,
                    "predictive": self.config.enable_predictive_analytics,
                },
                "features_enabled": {
                    "real_time_updates": self.config.enable_real_time_updates,
                    "cache": self.config.cache_enabled,
                    "notifications": self.config.enable_alert_notifications,
                },
            },
        }

        return admin_data

    async def get_dashboard_metrics(self) -> dict[str, Any]:
        """Get dashboard performance metrics"""

        return self.dashboard_metrics.copy()

    async def shutdown(self):
        """Shutdown unified monitoring dashboard"""

        self.dashboard_active = False

        # Shutdown monitoring systems
        if self.guardian_monitor:
            await self.guardian_monitor.shutdown()

        if self.consciousness_monitor:
            await self.consciousness_monitor.shutdown()

        if self.health_monitor:
            await self.health_monitor.shutdown()

        logger.info("🛑 Unified Monitoring Dashboard shutdown completed")


# Export main classes
__all__ = [
    "AlertPriority",
    "DashboardConfig",
    "DashboardData",
    "DashboardMode",
    "DashboardSession",
    "UnifiedAlert",
    "UnifiedMonitoringDashboard",
    "ViewType",
]
