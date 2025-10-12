"""
Advanced Guardian System Monitoring Dashboard for LUKHAS AI

This module provides a comprehensive real-time monitoring dashboard for the
Guardian System with drift detection, threat monitoring, and compliance
oversight. Maintains the critical 0.15 threshold for system stability while
providing extensive observability and alerting capabilities.

Features:
- Real-time Guardian System monitoring
- Drift detection dashboard (threshold: 0.15)
- Threat detection and analysis
- Constitutional compliance monitoring
- Constellation Framework integration (⚛️🧠🛡️)
- Performance metrics and health monitoring
- Alert management and notification system
- Audit trail visualization
- Security event correlation
- Compliance reporting dashboard

#TAG:governance
#TAG:guardian
#TAG:monitoring
#TAG:dashboard
#TAG:observability
#TAG:constellation
"""
import asyncio
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MonitoringScope(Enum):
    """Monitoring scope levels"""

    SYSTEM_WIDE = "system_wide"
    GUARDIAN_FOCUSED = "guardian_focused"
    DRIFT_SPECIFIC = "drift_specific"
    THREAT_ANALYSIS = "threat_analysis"
    COMPLIANCE_AUDIT = "compliance_audit"
    PERFORMANCE_HEALTH = "performance_health"


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ThreatLevel(Enum):
    """Threat classification levels"""

    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class MonitoringMetric:
    """Individual monitoring metric"""

    metric_id: str
    name: str
    value: float
    unit: str
    timestamp: datetime
    source: str

    # Classification
    category: str
    scope: MonitoringScope

    # Status information
    is_healthy: bool = True
    threshold_breached: bool = False
    severity: AlertSeverity = AlertSeverity.INFO

    # Context
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Constellation Framework tracking
    identity_impact: Optional[float] = None  # ⚛️
    consciousness_impact: Optional[float] = None  # 🧠
    guardian_priority: str = "normal"  # 🛡️


@dataclass
class ThreatDetection:
    """Security threat detection record"""

    threat_id: str
    threat_type: str
    description: str
    detected_at: datetime

    # Classification
    threat_level: ThreatLevel
    confidence: float
    false_positive_probability: float

    # Source information
    source_system: str
    detection_method: str
    triggering_events: list[dict[str, Any]] = field(default_factory=list)

    # Analysis
    indicators: list[str] = field(default_factory=list)
    attack_vectors: list[str] = field(default_factory=list)
    potential_impact: dict[str, float] = field(default_factory=dict)

    # Response
    mitigation_actions: list[str] = field(default_factory=list)
    containment_status: str = "pending"
    response_time: Optional[timedelta] = None


@dataclass
class ComplianceViolation:
    """Compliance violation record"""

    violation_id: str
    regulation: str
    violation_type: str
    description: str
    detected_at: datetime

    # Severity assessment
    severity: AlertSeverity
    legal_risk: float
    business_impact: float

    # Evidence
    evidence: list[dict[str, Any]] = field(default_factory=list)
    audit_trail: list[str] = field(default_factory=list)

    # Remediation
    remediation_required: bool = True
    remediation_actions: list[str] = field(default_factory=list)
    compliance_deadline: Optional[datetime] = None


@dataclass
class SystemHealthStatus:
    """Overall system health status"""

    status_id: str
    timestamp: datetime
    overall_health: float  # 0.0 to 1.0

    # Component health
    guardian_health: float
    consciousness_health: float
    identity_health: float
    memory_health: float
    api_health: float

    # Key metrics
    drift_score: float
    threat_level: ThreatLevel
    compliance_score: float
    performance_score: float

    # System state
    active_alerts: int
    unresolved_issues: int
    maintenance_required: bool = False
    emergency_mode: bool = False


@dataclass
class MonitoringReport:
    """Comprehensive monitoring report"""

    report_id: str
    generated_at: datetime
    time_period: tuple[datetime, datetime]
    scope: MonitoringScope

    # Summary statistics
    total_metrics: int

    # System health
    health_status: SystemHealthStatus

    # Fields with defaults
    metrics_by_category: dict[str, int] = field(default_factory=dict)
    alert_summary: dict[AlertSeverity, int] = field(default_factory=dict)

    # Security analysis
    threats_detected: list[ThreatDetection] = field(default_factory=list)
    security_incidents: int = 0

    # Compliance status
    compliance_violations: list[ComplianceViolation] = field(default_factory=list)
    compliance_score: float = 1.0

    # Performance insights
    performance_trends: dict[str, list[float]] = field(default_factory=dict)
    anomalies_detected: list[str] = field(default_factory=list)

    # Recommendations
    immediate_actions: list[str] = field(default_factory=list)
    preventive_measures: list[str] = field(default_factory=list)
    optimization_suggestions: list[str] = field(default_factory=list)


class GuardianMonitoringDashboard:
    """
    Advanced monitoring dashboard for Guardian System

    Provides comprehensive real-time monitoring with threat detection,
    compliance oversight, performance tracking, and integrated alerting
    system for the LUKHAS AI Guardian System.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Core configuration
        self.drift_threshold = 0.15
        self.monitoring_interval = 1.0  # seconds
        self.metrics_retention_hours = 72
        self.alert_retention_days = 30

        # Data storage
        self.metrics_history: deque = deque(maxlen=50000)
        self.alerts_history: deque = deque(maxlen=10000)
        self.threats_detected: deque = deque(maxlen=1000)
        self.compliance_violations: deque = deque(maxlen=500)

        # Real-time tracking
        self.current_metrics: dict[str, MonitoringMetric] = {}
        self.active_alerts: dict[str, dict[str, Any]] = {}
        self.system_health: Optional[SystemHealthStatus] = None

        # Monitoring state
        self.monitoring_active = True
        self.dashboard_sessions: dict[str, dict[str, Any]] = {}

        # Performance tracking
        self.performance_metrics = {
            "dashboard_requests": 0,
            "metrics_processed": 0,
            "alerts_generated": 0,
            "threats_detected": 0,
            "compliance_checks": 0,
            "average_response_time": 0.0,
            "uptime_seconds": 0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        # Threshold configurations
        self.thresholds = {
            "drift_score": 0.15,
            "response_time": 1000.0,  # milliseconds
            "cpu_usage": 80.0,  # percentage
            "memory_usage": 85.0,  # percentage
            "error_rate": 5.0,  # percentage
            "threat_confidence": 0.7,  # 0.0 to 1.0
            "compliance_score": 0.95,  # 0.0 to 1.0
        }

        # Initialize dashboard
        asyncio.create_task(self._initialize_dashboard())

        logger.info("🖥️ Guardian Monitoring Dashboard initialized")

    async def _initialize_dashboard(self):
        """Initialize the monitoring dashboard"""

        try:
            # Initialize system health
            await self._initialize_system_health()

            # Start monitoring loops
            asyncio.create_task(self._metrics_collection_loop())
            asyncio.create_task(self._threat_detection_loop())
            asyncio.create_task(self._compliance_monitoring_loop())
            asyncio.create_task(self._health_check_loop())
            asyncio.create_task(self._alert_management_loop())
            asyncio.create_task(self._cleanup_loop())

            logger.info("✅ Dashboard monitoring loops started")

        except Exception as e:
            logger.error(f"❌ Dashboard initialization failed: {e}")

    async def _initialize_system_health(self):
        """Initialize system health monitoring"""

        self.system_health = SystemHealthStatus(
            status_id=f"health_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc),
            overall_health=1.0,
            guardian_health=1.0,
            consciousness_health=1.0,
            identity_health=1.0,
            memory_health=1.0,
            api_health=1.0,
            drift_score=0.0,
            threat_level=ThreatLevel.BENIGN,
            compliance_score=1.0,
            performance_score=1.0,
            active_alerts=0,
            unresolved_issues=0,
        )

    async def _metrics_collection_loop(self):
        """Background loop for metrics collection"""

        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"❌ Metrics collection error: {e}")
                await asyncio.sleep(5)

    async def _threat_detection_loop(self):
        """Background loop for threat detection"""

        while self.monitoring_active:
            try:
                await self._analyze_security_threats()
                await asyncio.sleep(10)  # Threat analysis every 10 seconds

            except Exception as e:
                logger.error(f"❌ Threat detection error: {e}")
                await asyncio.sleep(30)

    async def _compliance_monitoring_loop(self):
        """Background loop for compliance monitoring"""

        while self.monitoring_active:
            try:
                await self._check_compliance_status()
                await asyncio.sleep(60)  # Compliance check every minute

            except Exception as e:
                logger.error(f"❌ Compliance monitoring error: {e}")
                await asyncio.sleep(120)

    async def _health_check_loop(self):
        """Background loop for system health checks"""

        while self.monitoring_active:
            try:
                await self._update_system_health()
                await asyncio.sleep(30)  # Health check every 30 seconds

            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(60)

    async def _alert_management_loop(self):
        """Background loop for alert management"""

        while self.monitoring_active:
            try:
                await self._process_alerts()
                await asyncio.sleep(5)  # Alert processing every 5 seconds

            except Exception as e:
                logger.error(f"❌ Alert management error: {e}")
                await asyncio.sleep(15)

    async def _cleanup_loop(self):
        """Background loop for data cleanup"""

        while self.monitoring_active:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Cleanup every hour

            except Exception as e:
                logger.error(f"❌ Cleanup loop error: {e}")
                await asyncio.sleep(1800)

    async def record_metric(
        self,
        name: str,
        value: float,
        unit: str,
        source: str,
        category: str = "general",
        scope: MonitoringScope = MonitoringScope.SYSTEM_WIDE,
        tags: Optional[dict[str, str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> MonitoringMetric:
        """Record a monitoring metric"""

        metric_id = f"metric_{uuid.uuid4().hex[:8]}"
        tags = tags or {}
        metadata = metadata or {}

        # Create metric
        metric = MonitoringMetric(
            metric_id=metric_id,
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(timezone.utc),
            source=source,
            category=category,
            scope=scope,
            tags=tags,
            metadata=metadata,
        )

        # Check thresholds
        threshold_key = name.lower()
        if threshold_key in self.thresholds:
            threshold = self.thresholds[threshold_key]
            metric.threshold_breached = value > threshold

            if metric.threshold_breached:
                metric.is_healthy = False
                metric.severity = self._determine_alert_severity(name, value, threshold)

        # Constellation Framework analysis
        metric.identity_impact = await self._analyze_identity_impact(metric)
        metric.consciousness_impact = await self._analyze_consciousness_impact(metric)
        metric.guardian_priority = await self._determine_guardian_priority(metric)

        # Store metric
        self.metrics_history.append(metric)
        self.current_metrics[name] = metric

        # Generate alert if necessary
        if metric.threshold_breached:
            await self._generate_alert(metric)

        # Update performance metrics
        self.performance_metrics["metrics_processed"] += 1

        logger.debug(f"📊 Metric recorded: {name} = {value} {unit}")

        return metric

    async def detect_threat(
        self,
        threat_type: str,
        description: str,
        source_system: str,
        detection_method: str,
        confidence: float,
        indicators: Optional[list[str]] = None,
        attack_vectors: Optional[list[str]] = None,
    ) -> ThreatDetection:
        """Record a security threat detection"""

        threat_id = f"threat_{uuid.uuid4().hex[:8]}"
        indicators = indicators or []
        attack_vectors = attack_vectors or []

        # Determine threat level
        threat_level = self._determine_threat_level(confidence, threat_type)

        # Create threat record
        threat = ThreatDetection(
            threat_id=threat_id,
            threat_type=threat_type,
            description=description,
            detected_at=datetime.now(timezone.utc),
            threat_level=threat_level,
            confidence=confidence,
            false_positive_probability=1.0 - confidence,
            source_system=source_system,
            detection_method=detection_method,
            indicators=indicators,
            attack_vectors=attack_vectors,
        )

        # Analyze potential impact
        threat.potential_impact = await self._analyze_threat_impact(threat)

        # Generate mitigation actions
        threat.mitigation_actions = await self._generate_mitigation_actions(threat)

        # Store threat
        self.threats_detected.append(threat)

        # Generate critical alert for high-level threats
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.SEVERE, ThreatLevel.CRITICAL]:
            await self._generate_threat_alert(threat)

        # Update performance metrics
        self.performance_metrics["threats_detected"] += 1

        logger.warning(f"🚨 Threat detected: {threat_type} (confidence: {confidence:.2f})")

        return threat

    async def record_compliance_violation(
        self,
        regulation: str,
        violation_type: str,
        description: str,
        severity: AlertSeverity,
        legal_risk: float,
        business_impact: float,
        evidence: Optional[list[dict[str, Any]]] = None,
    ) -> ComplianceViolation:
        """Record a compliance violation"""

        violation_id = f"violation_{uuid.uuid4().hex[:8]}"
        evidence = evidence or []

        # Create violation record
        violation = ComplianceViolation(
            violation_id=violation_id,
            regulation=regulation,
            violation_type=violation_type,
            description=description,
            detected_at=datetime.now(timezone.utc),
            severity=severity,
            legal_risk=legal_risk,
            business_impact=business_impact,
            evidence=evidence,
        )

        # Generate audit trail
        violation.audit_trail = [
            f"Violation detected at {violation.detected_at.isoformat()}",
            f"Regulation: {regulation}",
            f"Type: {violation_type}",
            f"Severity: {severity.value}",
            f"Legal risk: {legal_risk:.2f}",
            f"Business impact: {business_impact:.2f}",
        ]

        # Generate remediation actions
        violation.remediation_actions = await self._generate_remediation_actions(violation)

        # Set compliance deadline
        violation.compliance_deadline = self._calculate_compliance_deadline(severity, regulation)

        # Store violation
        self.compliance_violations.append(violation)

        # Generate compliance alert
        await self._generate_compliance_alert(violation)

        # Update performance metrics
        self.performance_metrics["compliance_checks"] += 1

        logger.error(f"⚖️ Compliance violation: {regulation} - {violation_type}")

        return violation

    async def get_dashboard_data(
        self,
        scope: MonitoringScope = MonitoringScope.SYSTEM_WIDE,
        time_range_hours: int = 24,
    ) -> dict[str, Any]:
        """Get comprehensive dashboard data"""

        try:
            # Update performance metrics
            self.performance_metrics["dashboard_requests"] += 1

            # Calculate time range
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=time_range_hours)

            # Filter data by time range and scope
            relevant_metrics = [
                m
                for m in self.metrics_history
                if start_time <= m.timestamp <= end_time and (scope == MonitoringScope.SYSTEM_WIDE or m.scope == scope)
            ]

            relevant_alerts = [
                alert
                for alert in self.active_alerts.values()
                if start_time <= datetime.fromisoformat(alert["created_at"]) <= end_time
            ]

            recent_threats = [t for t in self.threats_detected if start_time <= t.detected_at <= end_time]

            recent_violations = [v for v in self.compliance_violations if start_time <= v.detected_at <= end_time]

            # Aggregate metrics by category
            metrics_by_category = defaultdict(list)
            for metric in relevant_metrics:
                metrics_by_category[metric.category].append(metric.value)

            # Calculate trend data
            trend_data = {}
            for category, values in metrics_by_category.items():
                if len(values) > 1:
                    trend_data[category] = {
                        "current": values[-1],
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "trend": ("increasing" if values[-1] > sum(values[:-1]) / len(values[:-1]) else "decreasing"),
                    }

            # Dashboard data structure
            dashboard_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "scope": scope.value,
                "time_range_hours": time_range_hours,
                # System health
                "system_health": {
                    "overall_health": (self.system_health.overall_health if self.system_health else 0.0),
                    "guardian_health": (self.system_health.guardian_health if self.system_health else 0.0),
                    "consciousness_health": (self.system_health.consciousness_health if self.system_health else 0.0),
                    "identity_health": (self.system_health.identity_health if self.system_health else 0.0),
                    "drift_score": (self.system_health.drift_score if self.system_health else 0.0),
                    "threat_level": (self.system_health.threat_level.value if self.system_health else "benign"),
                    "compliance_score": (self.system_health.compliance_score if self.system_health else 1.0),
                    "emergency_mode": (self.system_health.emergency_mode if self.system_health else False),
                },
                # Current metrics
                "current_metrics": {
                    name: {
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp.isoformat(),
                        "is_healthy": metric.is_healthy,
                        "threshold_breached": metric.threshold_breached,
                        "severity": metric.severity.value,
                    }
                    for name, metric in self.current_metrics.items()
                },
                # Trend analysis
                "trends": trend_data,
                # Alert summary
                "alerts": {
                    "active_count": len(self.active_alerts),
                    "by_severity": self._count_alerts_by_severity(relevant_alerts),
                    "recent": [
                        {
                            "id": alert["id"],
                            "type": alert["type"],
                            "severity": alert["severity"],
                            "message": alert["message"],
                            "created_at": alert["created_at"],
                        }
                        for alert in list(relevant_alerts)[:10]
                    ],
                },
                # Security status
                "security": {
                    "threat_level": (self.system_health.threat_level.value if self.system_health else "benign"),
                    "threats_detected": len(recent_threats),
                    "high_risk_threats": len(
                        [
                            t
                            for t in recent_threats
                            if t.threat_level
                            in [
                                ThreatLevel.HIGH,
                                ThreatLevel.SEVERE,
                                ThreatLevel.CRITICAL,
                            ]
                        ]
                    ),
                    "recent_threats": [
                        {
                            "id": threat.threat_id,
                            "type": threat.threat_type,
                            "level": threat.threat_level.value,
                            "confidence": threat.confidence,
                            "detected_at": threat.detected_at.isoformat(),
                        }
                        for threat in recent_threats[:5]
                    ],
                },
                # Compliance status
                "compliance": {
                    "score": (self.system_health.compliance_score if self.system_health else 1.0),
                    "violations_count": len(recent_violations),
                    "critical_violations": len([v for v in recent_violations if v.severity == AlertSeverity.CRITICAL]),
                    "recent_violations": [
                        {
                            "id": violation.violation_id,
                            "regulation": violation.regulation,
                            "type": violation.violation_type,
                            "severity": violation.severity.value,
                            "detected_at": violation.detected_at.isoformat(),
                        }
                        for violation in recent_violations[:5]
                    ],
                },
                # Performance data
                "performance": self.performance_metrics.copy(),
                # Guardian-specific data
                "guardian": {
                    "drift_threshold": self.drift_threshold,
                    "current_drift_score": (self.system_health.drift_score if self.system_health else 0.0),
                    "threshold_breached": (self.system_health.drift_score if self.system_health else 0.0)
                    > self.drift_threshold,
                    "monitoring_active": self.monitoring_active,
                    "active_protections": self._get_active_protections(),
                },
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"❌ Dashboard data generation failed: {e}")
            return {"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}

    def _determine_alert_severity(self, metric_name: str, value: float, threshold: float) -> AlertSeverity:
        """Determine alert severity based on metric value and threshold"""

        if value >= threshold * 2.0:
            return AlertSeverity.CRITICAL
        elif value >= threshold * 1.5:
            return AlertSeverity.HIGH
        elif value >= threshold * 1.2:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW

    def _determine_threat_level(self, confidence: float, threat_type: str) -> ThreatLevel:
        """Determine threat level based on confidence and type"""

        # Base level from confidence
        if confidence >= 0.9:
            base_level = ThreatLevel.CRITICAL
        elif confidence >= 0.8:
            base_level = ThreatLevel.SEVERE
        elif confidence >= 0.7:
            base_level = ThreatLevel.HIGH
        elif confidence >= 0.5:
            base_level = ThreatLevel.MODERATE
        elif confidence >= 0.3:
            base_level = ThreatLevel.SUSPICIOUS
        else:
            base_level = ThreatLevel.BENIGN

        # Adjust based on threat type
        high_risk_types = ["data_breach", "system_compromise", "privilege_escalation"]
        if threat_type.lower() in high_risk_types and base_level != ThreatLevel.CRITICAL:
            # Elevate by one level
            level_order = [
                ThreatLevel.BENIGN,
                ThreatLevel.SUSPICIOUS,
                ThreatLevel.MODERATE,
                ThreatLevel.HIGH,
                ThreatLevel.SEVERE,
                ThreatLevel.CRITICAL,
            ]
            current_index = level_order.index(base_level)
            if current_index < len(level_order) - 1:
                base_level = level_order[current_index + 1]

        return base_level

    async def _collect_system_metrics(self):
        """Collect system-wide metrics"""

        # Simulate system metrics collection
        # In production, would integrate with actual system monitoring

        try:
            # Record basic system metrics
            await self.record_metric("drift_score", 0.08, "score", "guardian_system", "guardian")
            await self.record_metric("response_time", 250.0, "ms", "api_gateway", "performance")
            await self.record_metric("cpu_usage", 45.0, "%", "system_monitor", "performance")
            await self.record_metric("memory_usage", 62.0, "%", "system_monitor", "performance")
            await self.record_metric("error_rate", 1.2, "%", "api_gateway", "reliability")
            await self.record_metric("active_sessions", 127.0, "count", "auth_system", "usage")

        except Exception as e:
            logger.error(f"❌ System metrics collection failed: {e}")

    async def _analyze_security_threats(self):
        """Analyze and detect security threats"""

        # Simulate threat analysis
        # In production, would integrate with security monitoring systems
        pass

    async def _check_compliance_status(self):
        """Check compliance status across regulations"""

        # Simulate compliance checking
        # In production, would integrate with compliance monitoring systems
        pass

    async def _update_system_health(self):
        """Update overall system health status"""

        if not self.system_health:
            return

        try:
            # Calculate component health scores
            guardian_metrics = [m for m in self.current_metrics.values() if m.category == "guardian"]
            consciousness_metrics = [m for m in self.current_metrics.values() if m.category == "consciousness"]
            identity_metrics = [m for m in self.current_metrics.values() if m.category == "identity"]
            performance_metrics = [m for m in self.current_metrics.values() if m.category == "performance"]

            # Update component health (simplified calculation)
            self.system_health.guardian_health = self._calculate_component_health(guardian_metrics)
            self.system_health.consciousness_health = self._calculate_component_health(consciousness_metrics)
            self.system_health.identity_health = self._calculate_component_health(identity_metrics)
            self.system_health.api_health = self._calculate_component_health(performance_metrics)

            # Update overall health
            component_healths = [
                self.system_health.guardian_health,
                self.system_health.consciousness_health,
                self.system_health.identity_health,
                self.system_health.api_health,
            ]

            self.system_health.overall_health = sum(component_healths) / len(component_healths)

            # Update drift score from current metrics
            if "drift_score" in self.current_metrics:
                self.system_health.drift_score = self.current_metrics["drift_score"].value

            # Update alert counts
            self.system_health.active_alerts = len(self.active_alerts)

            # Update timestamp
            self.system_health.timestamp = datetime.now(timezone.utc)

        except Exception as e:
            logger.error(f"❌ System health update failed: {e}")

    def _calculate_component_health(self, metrics: list[MonitoringMetric]) -> float:
        """Calculate health score for component metrics"""

        if not metrics:
            return 1.0

        healthy_count = sum(1 for m in metrics if m.is_healthy)
        return healthy_count / len(metrics)

    async def _process_alerts(self):
        """Process and manage active alerts"""

        # Remove expired alerts
        current_time = datetime.now(timezone.utc)
        expired_alerts = []

        for alert_id, alert in self.active_alerts.items():
            created_at = datetime.fromisoformat(alert["created_at"])
            if (current_time - created_at).total_seconds() > 3600:  # 1 hour expiry
                expired_alerts.append(alert_id)

        for alert_id in expired_alerts:
            del self.active_alerts[alert_id]

    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.metrics_retention_hours)

        # Clean metrics history
        while self.metrics_history and self.metrics_history[0].timestamp < cutoff_time:
            self.metrics_history.popleft()

        # Clean threats
        while self.threats_detected and self.threats_detected[0].detected_at < cutoff_time:
            self.threats_detected.popleft()

        # Clean compliance violations
        while self.compliance_violations and self.compliance_violations[0].detected_at < cutoff_time:
            self.compliance_violations.popleft()

    async def _generate_alert(self, metric: MonitoringMetric):
        """Generate alert for threshold breach"""

        alert_id = f"alert_{uuid.uuid4().hex[:8]}"

        alert = {
            "id": alert_id,
            "type": "metric_threshold",
            "severity": metric.severity.value,
            "message": f"Metric '{metric.name}' exceeded threshold: {metric.value} {metric.unit}",
            "source": metric.source,
            "metric_id": metric.metric_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "acknowledged": False,
            "resolved": False,
        }

        self.active_alerts[alert_id] = alert
        self.performance_metrics["alerts_generated"] += 1

        logger.warning(f"🚨 Alert generated: {alert['message']}")

    async def _generate_threat_alert(self, threat: ThreatDetection):
        """Generate alert for security threat"""

        alert_id = f"alert_{uuid.uuid4().hex[:8]}"

        severity_mapping = {
            ThreatLevel.HIGH: AlertSeverity.HIGH,
            ThreatLevel.SEVERE: AlertSeverity.CRITICAL,
            ThreatLevel.CRITICAL: AlertSeverity.EMERGENCY,
        }

        severity = severity_mapping.get(threat.threat_level, AlertSeverity.MEDIUM)

        alert = {
            "id": alert_id,
            "type": "security_threat",
            "severity": severity.value,
            "message": f"Security threat detected: {threat.threat_type} (confidence: {threat.confidence:.2f})",
            "source": threat.source_system,
            "threat_id": threat.threat_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "acknowledged": False,
            "resolved": False,
        }

        self.active_alerts[alert_id] = alert
        self.performance_metrics["alerts_generated"] += 1

        logger.error(f"🚨 Security alert: {alert['message']}")

    async def _generate_compliance_alert(self, violation: ComplianceViolation):
        """Generate alert for compliance violation"""

        alert_id = f"alert_{uuid.uuid4().hex[:8]}"

        alert = {
            "id": alert_id,
            "type": "compliance_violation",
            "severity": violation.severity.value,
            "message": f"Compliance violation: {violation.regulation} - {violation.violation_type}",
            "source": "compliance_monitor",
            "violation_id": violation.violation_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "acknowledged": False,
            "resolved": False,
        }

        self.active_alerts[alert_id] = alert
        self.performance_metrics["alerts_generated"] += 1

        logger.error(f"⚖️ Compliance alert: {alert['message']}")

    def _count_alerts_by_severity(self, alerts: list[dict[str, Any]]) -> dict[str, int]:
        """Count alerts by severity level"""

        counts = defaultdict(int)
        for alert in alerts:
            counts[alert.get("severity", "info")] += 1
        return dict(counts)

    def _get_active_protections(self) -> list[str]:
        """Get list of currently active Guardian protections"""

        return [
            "drift_monitoring",
            "threat_detection",
            "compliance_checking",
            "constitutional_oversight",
            "constellation_framework_protection",
        ]

    async def _analyze_identity_impact(self, metric: MonitoringMetric) -> Optional[float]:
        """Analyze metric impact on identity systems (⚛️)"""

        identity_keywords = [
            "auth",
            "identity",
            "user",
            "login",
            "access",
            "permission",
        ]

        if any(keyword in metric.name.lower() for keyword in identity_keywords):
            return min(1.0, metric.value / 100.0) if metric.threshold_breached else None

        return None

    async def _analyze_consciousness_impact(self, metric: MonitoringMetric) -> Optional[float]:
        """Analyze metric impact on consciousness systems (🧠)"""

        consciousness_keywords = [
            "consciousness",
            "awareness",
            "decision",
            "learning",
            "lukhas.memory",
        ]

        if any(keyword in metric.name.lower() for keyword in consciousness_keywords):
            return min(1.0, metric.value / 100.0) if metric.threshold_breached else None

        return None

    async def _determine_guardian_priority(self, metric: MonitoringMetric) -> str:
        """Determine Guardian system priority (🛡️)"""

        if metric.threshold_breached:
            if metric.severity == AlertSeverity.CRITICAL:
                return "critical"
            elif metric.severity == AlertSeverity.HIGH:
                return "high"
            else:
                return "elevated"

        return "normal"

    async def _analyze_threat_impact(self, threat: ThreatDetection) -> dict[str, float]:
        """Analyze potential threat impact"""

        return {
            "data_confidentiality": (0.7 if "data" in threat.threat_type.lower() else 0.3),
            "system_availability": 0.8 if "dos" in threat.threat_type.lower() else 0.2,
            "service_integrity": (0.6 if "injection" in threat.threat_type.lower() else 0.1),
            "user_privacy": 0.9 if "privacy" in threat.threat_type.lower() else 0.2,
        }

    async def _generate_mitigation_actions(self, threat: ThreatDetection) -> list[str]:
        """Generate mitigation actions for threat"""

        actions = ["Monitor threat indicators", "Review access logs"]

        if threat.threat_level in [
            ThreatLevel.HIGH,
            ThreatLevel.SEVERE,
            ThreatLevel.CRITICAL,
        ]:
            actions.extend(
                [
                    "Activate enhanced monitoring",
                    "Notify security team",
                    "Consider system isolation",
                ]
            )

        return actions

    async def _generate_remediation_actions(self, violation: ComplianceViolation) -> list[str]:
        """Generate remediation actions for compliance violation"""

        actions = [
            f"Review {violation.regulation} requirements",
            "Document violation in compliance log",
            "Assess legal implications",
        ]

        if violation.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            actions.extend(
                [
                    "Immediate remediation required",
                    "Notify compliance officer",
                    "Prepare regulatory response",
                ]
            )

        return actions

    def _calculate_compliance_deadline(self, severity: AlertSeverity, regulation: str) -> Optional[datetime]:
        """Calculate compliance remediation deadline"""

        deadline_days = {
            AlertSeverity.CRITICAL: 1,
            AlertSeverity.HIGH: 7,
            AlertSeverity.MEDIUM: 30,
            AlertSeverity.LOW: 90,
        }

        days = deadline_days.get(severity, 30)
        return datetime.now(timezone.utc) + timedelta(days=days)

    async def get_monitoring_report(
        self,
        scope: MonitoringScope = MonitoringScope.SYSTEM_WIDE,
        time_period: Optional[tuple[datetime, datetime]] = None,
    ) -> MonitoringReport:
        """Generate comprehensive monitoring report"""

        if not time_period:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=24)
            time_period = (start_time, end_time)

        report_id = f"report_{uuid.uuid4().hex[:8]}"

        # Filter data for time period
        period_metrics = [m for m in self.metrics_history if time_period[0] <= m.timestamp <= time_period[1]]

        period_threats = [t for t in self.threats_detected if time_period[0] <= t.detected_at <= time_period[1]]

        period_violations = [v for v in self.compliance_violations if time_period[0] <= v.detected_at <= time_period[1]]

        # Generate report
        report = MonitoringReport(
            report_id=report_id,
            generated_at=datetime.now(timezone.utc),
            time_period=time_period,
            scope=scope,
            total_metrics=len(period_metrics),
            health_status=self.system_health,
            threats_detected=period_threats,
            security_incidents=len(
                [
                    t
                    for t in period_threats
                    if t.threat_level in [ThreatLevel.HIGH, ThreatLevel.SEVERE, ThreatLevel.CRITICAL]
                ]
            ),
            compliance_violations=period_violations,
            compliance_score=1.0 - (len(period_violations) * 0.1),  # Simplified calculation
        )

        # Add recommendations based on findings
        if report.security_incidents > 0:
            report.immediate_actions.append("Review security incidents")
            report.preventive_measures.append("Enhance threat detection")

        if len(period_violations) > 0:
            report.immediate_actions.append("Address compliance violations")
            report.preventive_measures.append("Strengthen compliance monitoring")

        return report

    async def shutdown(self):
        """Shutdown monitoring dashboard"""

        self.monitoring_active = False
        logger.info("🛑 Guardian Monitoring Dashboard shutdown initiated")


# Export main classes
__all__ = [
    "AlertSeverity",
    "ComplianceViolation",
    "GuardianMonitoringDashboard",
    "MonitoringMetric",
    "MonitoringReport",
    "MonitoringScope",
    "SystemHealthStatus",
    "ThreatDetection",
    "ThreatLevel",
]
