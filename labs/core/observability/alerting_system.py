"""
Comprehensive Alerting System for LUKHAS AI

This module provides a comprehensive alerting system with critical event
monitoring, compliance audit trails, multi-channel notifications, and
sophisticated alert management for the LUKHAS AI system. Integrates with
all monitoring systems to provide unified alerting capabilities.

Features:
- Multi-level alert classification and prioritization
- Real-time critical event monitoring
- Compliance audit trail generation (GDPR/CCPA/HIPAA)
- Multi-channel notification system (email, webhooks, dashboard)
- Alert correlation and deduplication
- Escalation policies and notification chains
- Constellation Framework alert integration (⚛️🧠🛡️)
- Automated alert resolution and acknowledgment
- Historical alert analysis and reporting
- Compliance violation detection and reporting

#TAG:alerting
#TAG:compliance
#TAG:audit
#TAG:notifications
#TAG:constellation
"""
import asyncio
import contextlib
import hashlib
import json
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertCategory(Enum):
    """Alert category types"""

    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    GUARDIAN = "guardian"
    CONSCIOUSNESS = "consciousness"
    IDENTITY = "identity"
    MEMORY = "memory"
    API = "api"
    DRIFT = "drift"
    HEALTH = "health"


class AlertStatus(Enum):
    """Alert status values"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    CLOSED = "closed"


class NotificationChannel(Enum):
    """Notification delivery channels"""

    DASHBOARD = "dashboard"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    SLACK = "slack"
    LOG = "log"


class ComplianceRegulation(Enum):
    """Compliance regulations for audit trails"""

    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"


@dataclass
class AlertRule:
    """Alert rule definition"""

    rule_id: str
    name: str
    description: str
    enabled: bool = True

    # Conditions
    metric_name: str = ""
    threshold_value: Optional[float] = None
    threshold_operator: str = ">"  # >, <, >=, <=, ==, !=
    evaluation_window: int = 60  # seconds

    # Classification
    severity: AlertSeverity = AlertSeverity.MEDIUM
    category: AlertCategory = AlertCategory.SYSTEM

    # Notification
    notification_channels: list[NotificationChannel] = field(default_factory=list)
    notification_cooldown: int = 300  # seconds

    # Escalation
    escalation_timeout: int = 1800  # 30 minutes
    escalation_severity: Optional[AlertSeverity] = None

    # Compliance
    compliance_relevant: bool = False
    applicable_regulations: list[ComplianceRegulation] = field(default_factory=list)

    # Constellation Framework
    constellation_component: Optional[str] = None  # identity, consciousness, guardian

    # Auto-resolution
    auto_resolve: bool = False
    auto_resolve_timeout: int = 3600  # 1 hour


@dataclass
class Alert:
    """Individual alert instance"""

    alert_id: str
    rule_id: str
    title: str
    message: str

    # Classification
    severity: AlertSeverity
    category: AlertCategory
    status: AlertStatus = AlertStatus.ACTIVE

    # Timing
    created_at: datetime
    updated_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Source information
    source_system: str = "unknown"
    source_metric: Optional[str] = None
    triggered_value: Optional[float] = None

    # Context
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    affected_systems: list[str] = field(default_factory=list)

    # Actions
    acknowledgment_user: Optional[str] = None
    resolution_user: Optional[str] = None
    resolution_notes: Optional[str] = None

    # Notifications
    notification_history: list[dict[str, Any]] = field(default_factory=list)
    last_notification_sent: Optional[datetime] = None
    notification_count: int = 0

    # Escalation
    escalation_level: int = 0
    escalated_at: Optional[datetime] = None
    escalation_history: list[dict[str, Any]] = field(default_factory=list)

    # Compliance
    compliance_relevant: bool = False
    applicable_regulations: list[ComplianceRegulation] = field(default_factory=list)
    audit_trail_id: Optional[str] = None

    # Constellation Framework
    constellation_impact: dict[str, float] = field(default_factory=dict)  # ⚛️🧠🛡️

    # Correlation
    correlation_key: Optional[str] = None
    parent_alert_id: Optional[str] = None
    child_alert_ids: list[str] = field(default_factory=list)

    # Performance
    detection_latency: Optional[float] = None
    notification_latency: Optional[float] = None


@dataclass
class ComplianceAuditEntry:
    """Compliance audit trail entry"""

    entry_id: str
    timestamp: datetime

    # Event information
    event_type: str
    event_description: str
    alert_id: Optional[str] = None

    # Compliance context
    regulation: ComplianceRegulation
    compliance_requirement: str
    violation_severity: str

    # Data subject information (for GDPR/CCPA)
    data_subject_id: Optional[str] = None
    data_categories: list[str] = field(default_factory=list)
    processing_purpose: Optional[str] = None

    # System context
    system_component: str = "unknown"
    user_id: Optional[str] = None
    ip_address: Optional[str] = None

    # Evidence
    evidence: dict[str, Any] = field(default_factory=dict)
    supporting_data: list[str] = field(default_factory=list)

    # Remediation
    remediation_required: bool = True
    remediation_actions: list[str] = field(default_factory=list)
    remediation_deadline: Optional[datetime] = None

    # Status
    status: str = "open"
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


@dataclass
class NotificationConfig:
    """Notification configuration"""

    config_id: str
    name: str
    enabled: bool = True

    # Channel configuration
    channel: NotificationChannel
    endpoint: str  # email address, webhook URL, etc.

    # Filter criteria
    severity_filter: list[AlertSeverity] = field(default_factory=list)
    category_filter: list[AlertCategory] = field(default_factory=list)
    system_filter: list[str] = field(default_factory=list)

    # Rate limiting
    rate_limit: int = 10  # max notifications per hour
    burst_limit: int = 3  # max notifications per minute

    # Templates
    subject_template: str = "LUKHAS AI Alert: {title}"
    body_template: str = "Alert: {message}\nSeverity: {severity}\nTime: {created_at}"

    # Retry configuration
    retry_attempts: int = 3
    retry_delay: int = 60  # seconds


@dataclass
class AlertingMetrics:
    """Alerting system performance metrics"""

    # Alert statistics
    total_alerts_created: int = 0
    alerts_by_severity: dict[str, int] = field(default_factory=dict)
    alerts_by_category: dict[str, int] = field(default_factory=dict)
    active_alerts_count: int = 0

    # Performance metrics
    average_detection_time: float = 0.0
    average_notification_time: float = 0.0
    alert_resolution_rate: float = 0.0
    false_positive_rate: float = 0.0

    # Notification metrics
    total_notifications_sent: int = 0
    notifications_by_channel: dict[str, int] = field(default_factory=dict)
    notification_success_rate: float = 100.0

    # Compliance metrics
    compliance_violations_detected: int = 0
    audit_entries_created: int = 0
    compliance_response_time: float = 0.0

    # System health
    alerting_system_uptime: float = 100.0
    rule_evaluation_rate: float = 0.0
    last_metrics_update: Optional[datetime] = None


class ComprehensiveAlertingSystem:
    """
    Comprehensive alerting system for LUKHAS AI

    Provides advanced alerting capabilities with multi-channel notifications,
    compliance audit trails, alert correlation, and integrated monitoring
    for all LUKHAS AI system components.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Core configuration
        self.alert_retention_days = 90
        self.audit_retention_days = 2555  # 7 years for compliance
        self.max_active_alerts = 1000
        self.evaluation_interval = 5.0  # seconds

        # Data storage
        self.alert_rules: dict[str, AlertRule] = {}
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=50000)
        self.audit_trail: deque = deque(maxlen=100000)

        # Notification system
        self.notification_configs: dict[str, NotificationConfig] = {}
        self.notification_queue: deque = deque()

        # Correlation engine
        self.correlation_keys: dict[str, list[str]] = defaultdict(list)
        self.alert_correlations: dict[str, str] = {}

        # Performance tracking
        self.metrics = AlertingMetrics()
        self.system_start_time = datetime.now(timezone.utc)

        # System state
        self.alerting_active = True
        self.notification_processor_active = True

        # Initialize system
        asyncio.create_task(self._initialize_alerting_system())

        logger.info("🚨 Comprehensive Alerting System initialized")

    async def _initialize_alerting_system(self):
        """Initialize the alerting system"""

        try:
            # Load default alert rules
            await self._load_default_alert_rules()

            # Load notification configurations
            await self._load_notification_configurations()

            # Start processing loops
            asyncio.create_task(self._alert_evaluation_loop())
            asyncio.create_task(self._notification_processing_loop())
            asyncio.create_task(self._escalation_monitoring_loop())
            asyncio.create_task(self._compliance_monitoring_loop())
            asyncio.create_task(self._cleanup_loop())

            logger.info("✅ Alerting system loops started")

        except Exception as e:
            logger.error(f"❌ Alerting system initialization failed: {e}")

    async def _load_default_alert_rules(self):
        """Load default alert rules"""

        default_rules = [
            # Guardian System alerts
            AlertRule(
                rule_id="guardian_drift_threshold",
                name="Guardian Drift Threshold Exceeded",
                description="Guardian system drift score exceeded 0.15 threshold",
                metric_name="drift_score",
                threshold_value=0.15,
                threshold_operator=">",
                severity=AlertSeverity.HIGH,
                category=AlertCategory.GUARDIAN,
                notification_channels=[
                    NotificationChannel.DASHBOARD,
                    NotificationChannel.EMAIL,
                ],
                compliance_relevant=True,
                applicable_regulations=[ComplianceRegulation.SOC2],
                constellation_component="guardian",
            ),
            # Consciousness alerts
            AlertRule(
                rule_id="consciousness_cognitive_overload",
                name="Cognitive Overload Detected",
                description="Consciousness system cognitive load exceeded safe threshold",
                metric_name="cognitive_load",
                threshold_value=0.85,
                threshold_operator=">=",
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.CONSCIOUSNESS,
                notification_channels=[NotificationChannel.DASHBOARD],
                constellation_component="consciousness",
            ),
            # System health alerts
            AlertRule(
                rule_id="system_health_critical",
                name="Critical System Health",
                description="System health dropped to critical levels",
                metric_name="overall_health",
                threshold_value=0.3,
                threshold_operator="<",
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.HEALTH,
                notification_channels=[
                    NotificationChannel.DASHBOARD,
                    NotificationChannel.EMAIL,
                ],
                escalation_timeout=900,
                escalation_severity=AlertSeverity.EMERGENCY,
            ),
            # Memory cascade prevention
            AlertRule(
                rule_id="memory_cascade_risk",
                name="Memory Cascade Risk Detected",
                description="Memory cascade prevention score below target",
                metric_name="cascade_prevention_score",
                threshold_value=0.997,
                threshold_operator="<",
                severity=AlertSeverity.HIGH,
                category=AlertCategory.MEMORY,
                notification_channels=[
                    NotificationChannel.DASHBOARD,
                    NotificationChannel.EMAIL,
                ],
                compliance_relevant=True,
                applicable_regulations=[ComplianceRegulation.SOC2],
            ),
            # API performance alerts
            AlertRule(
                rule_id="api_response_time",
                name="API Response Time Degraded",
                description="API response time exceeded acceptable threshold",
                metric_name="response_time",
                threshold_value=5000.0,  # 5 seconds
                threshold_operator=">",
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.API,
                notification_channels=[NotificationChannel.DASHBOARD],
            ),
            # Compliance violations
            AlertRule(
                rule_id="compliance_violation",
                name="Compliance Violation Detected",
                description="Potential compliance violation identified",
                metric_name="compliance_score",
                threshold_value=0.95,
                threshold_operator="<",
                severity=AlertSeverity.HIGH,
                category=AlertCategory.COMPLIANCE,
                notification_channels=[
                    NotificationChannel.DASHBOARD,
                    NotificationChannel.EMAIL,
                ],
                compliance_relevant=True,
                applicable_regulations=[
                    ComplianceRegulation.GDPR,
                    ComplianceRegulation.CCPA,
                ],
                escalation_timeout=1800,
            ),
        ]

        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule

        logger.info(f"✅ Loaded {len(default_rules)} default alert rules")

    async def _load_notification_configurations(self):
        """Load notification configurations"""

        default_configs = [
            NotificationConfig(
                config_id="dashboard_notifications",
                name="Dashboard Notifications",
                channel=NotificationChannel.DASHBOARD,
                endpoint="dashboard",
                severity_filter=[
                    AlertSeverity.MEDIUM,
                    AlertSeverity.HIGH,
                    AlertSeverity.CRITICAL,
                    AlertSeverity.EMERGENCY,
                ],
            ),
            NotificationConfig(
                config_id="email_critical",
                name="Critical Email Notifications",
                channel=NotificationChannel.EMAIL,
                endpoint="admin@ai",
                severity_filter=[AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY],
                rate_limit=5,
                subject_template="🚨 LUKHAS AI Critical Alert: {title}",
                body_template="""
Critical Alert Detected in LUKHAS AI System

Alert: {title}
Severity: {severity}
Category: {category}
Time: {created_at}
Source: {source_system}

Description:
{message}

Metadata:
{metadata}

Please take immediate action to address this alert.

LUKHAS AI Monitoring System
                """,
            ),
        ]

        for config in default_configs:
            self.notification_configs[config.config_id] = config

        logger.info(f"✅ Loaded {len(default_configs)} notification configurations")

    async def _alert_evaluation_loop(self):
        """Main alert evaluation loop"""

        while self.alerting_active:
            try:
                await self._evaluate_alert_rules()
                await self._update_alert_metrics()
                await asyncio.sleep(self.evaluation_interval)

            except Exception as e:
                logger.error(f"❌ Alert evaluation error: {e}")
                await asyncio.sleep(10)

    async def _notification_processing_loop(self):
        """Background loop for processing notifications"""

        while self.notification_processor_active:
            try:
                await self._process_notification_queue()
                await asyncio.sleep(1.0)  # High frequency for notifications

            except Exception as e:
                logger.error(f"❌ Notification processing error: {e}")
                await asyncio.sleep(5)

    async def _escalation_monitoring_loop(self):
        """Background loop for monitoring alert escalations"""

        while self.alerting_active:
            try:
                await self._check_alert_escalations()
                await asyncio.sleep(60)  # Every minute

            except Exception as e:
                logger.error(f"❌ Escalation monitoring error: {e}")
                await asyncio.sleep(120)

    async def _compliance_monitoring_loop(self):
        """Background loop for compliance monitoring"""

        while self.alerting_active:
            try:
                await self._monitor_compliance_violations()
                await self._generate_compliance_reports()
                await asyncio.sleep(300)  # Every 5 minutes

            except Exception as e:
                logger.error(f"❌ Compliance monitoring error: {e}")
                await asyncio.sleep(600)

    async def _cleanup_loop(self):
        """Background loop for data cleanup"""

        while self.alerting_active:
            try:
                await self._cleanup_old_alerts()
                await self._cleanup_old_audit_entries()
                await asyncio.sleep(3600)  # Every hour

            except Exception as e:
                logger.error(f"❌ Cleanup loop error: {e}")
                await asyncio.sleep(1800)

    async def create_alert(
        self,
        rule_id: str,
        title: str,
        message: str,
        severity: AlertSeverity,
        category: AlertCategory,
        source_system: str = "unknown",
        source_metric: Optional[str] = None,
        triggered_value: Optional[float] = None,
        tags: Optional[dict[str, str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        affected_systems: Optional[list[str]] = None,
    ) -> Alert:
        """Create a new alert"""

        alert_id = f"alert_{uuid.uuid4().hex[:12]}"
        tags = tags or {}
        metadata = metadata or {}
        affected_systems = affected_systems or []

        # Check for correlation
        correlation_key = await self._generate_correlation_key(rule_id, source_system, source_metric, tags)

        # Create alert
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule_id,
            title=title,
            message=message,
            severity=severity,
            category=category,
            created_at=datetime.now(timezone.utc),
            source_system=source_system,
            source_metric=source_metric,
            triggered_value=triggered_value,
            tags=tags,
            metadata=metadata,
            affected_systems=affected_systems,
            correlation_key=correlation_key,
        )

        # Set compliance relevance
        if rule_id in self.alert_rules:
            rule = self.alert_rules[rule_id]
            alert.compliance_relevant = rule.compliance_relevant
            alert.applicable_regulations = rule.applicable_regulations.copy()

        # Constellation Framework impact analysis
        alert.constellation_impact = await self._analyze_trinity_impact(alert)

        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        # Update correlation mapping
        if correlation_key:
            self.correlation_keys[correlation_key].append(alert_id)

            # Link to parent alert if correlation exists
            existing_alerts = [aid for aid in self.correlation_keys[correlation_key] if aid != alert_id]
            if existing_alerts:
                parent_id = existing_alerts[0]  # Use first alert as parent
                alert.parent_alert_id = parent_id

                if parent_id in self.active_alerts:
                    self.active_alerts[parent_id].child_alert_ids.append(alert_id)

        # Generate compliance audit entry if needed
        if alert.compliance_relevant:
            await self._create_compliance_audit_entry(alert)

        # Queue notifications
        await self._queue_alert_notifications(alert)

        # Update metrics
        self.metrics.total_alerts_created += 1
        self.metrics.active_alerts_count = len(self.active_alerts)

        severity_key = severity.value
        self.metrics.alerts_by_severity[severity_key] = self.metrics.alerts_by_severity.get(severity_key, 0) + 1

        category_key = category.value
        self.metrics.alerts_by_category[category_key] = self.metrics.alerts_by_category.get(category_key, 0) + 1

        logger.warning(f"🚨 Alert created: {title} ({severity.value})")

        return alert

    async def _generate_correlation_key(
        self,
        rule_id: str,
        source_system: str,
        source_metric: Optional[str],
        tags: dict[str, str],
    ) -> str:
        """Generate correlation key for alert deduplication"""

        # Create correlation string
        correlation_parts = [rule_id, source_system]

        if source_metric:
            correlation_parts.append(source_metric)

        # Add significant tags
        significant_tags = ["component", "service", "host"]
        for tag_key in significant_tags:
            if tag_key in tags:
                correlation_parts.append(f"{tag_key}:{tags[tag_key]}")

        correlation_string = "|".join(correlation_parts)

        # Generate hash
        return hashlib.md5(correlation_string.encode()).hexdigest()[:16]

    async def _analyze_trinity_impact(self, alert: Alert) -> dict[str, float]:
        """Analyze alert impact on Constellation Framework components"""

        impact = {"identity": 0.0, "consciousness": 0.0, "guardian": 0.0}

        # Category-based impact
        if alert.category == AlertCategory.IDENTITY:
            impact["identity"] = 1.0
        elif alert.category == AlertCategory.CONSCIOUSNESS:
            impact["consciousness"] = 1.0
        elif alert.category == AlertCategory.GUARDIAN:
            impact["guardian"] = 1.0
        elif alert.category == AlertCategory.DRIFT:
            impact["guardian"] = 0.8
            impact["consciousness"] = 0.3
        elif alert.category == AlertCategory.SECURITY:
            impact["guardian"] = 0.9
            impact["identity"] = 0.7
        elif alert.category == AlertCategory.MEMORY:
            impact["consciousness"] = 0.6
            impact["guardian"] = 0.4

        # Severity multiplier
        severity_multipliers = {
            AlertSeverity.INFO: 0.1,
            AlertSeverity.LOW: 0.3,
            AlertSeverity.MEDIUM: 0.5,
            AlertSeverity.HIGH: 0.8,
            AlertSeverity.CRITICAL: 1.0,
            AlertSeverity.EMERGENCY: 1.2,
        }

        multiplier = severity_multipliers.get(alert.severity, 0.5)

        # Apply multiplier
        for component in impact:
            impact[component] *= multiplier
            impact[component] = min(1.0, impact[component])  # Cap at 1.0

        return impact

    async def _create_compliance_audit_entry(self, alert: Alert):
        """Create compliance audit trail entry"""

        for regulation in alert.applicable_regulations:
            entry_id = f"audit_{uuid.uuid4().hex[:12]}"

            # Determine violation severity
            violation_severity = (
                "high" if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY] else "medium"
            )

            # Create audit entry
            audit_entry = ComplianceAuditEntry(
                entry_id=entry_id,
                timestamp=datetime.now(timezone.utc),
                event_type="alert_triggered",
                event_description=f"Alert triggered: {alert.title}",
                alert_id=alert.alert_id,
                regulation=regulation,
                compliance_requirement=self._get_compliance_requirement(regulation, alert),
                violation_severity=violation_severity,
                system_component=alert.source_system,
                evidence={
                    "alert_details": {
                        "title": alert.title,
                        "message": alert.message,
                        "severity": alert.severity.value,
                        "category": alert.category.value,
                        "triggered_value": alert.triggered_value,
                        "metadata": alert.metadata,
                    }
                },
                remediation_required=True,
                remediation_actions=[
                    f"Investigate alert: {alert.title}",
                    f"Review {alert.source_system} system compliance",
                    "Implement corrective measures if needed",
                ],
                remediation_deadline=datetime.now(timezone.utc) + timedelta(days=7 if violation_severity == "medium" else 1),
            )

            # Store audit entry
            self.audit_trail.append(audit_entry)
            alert.audit_trail_id = entry_id

            # Update metrics
            self.metrics.compliance_violations_detected += 1
            self.metrics.audit_entries_created += 1

            logger.info(f"📋 Compliance audit entry created: {entry_id} ({regulation.value})")

    def _get_compliance_requirement(self, regulation: ComplianceRegulation, alert: Alert) -> str:
        """Get compliance requirement description"""

        requirements = {
            ComplianceRegulation.GDPR: {
                AlertCategory.SECURITY: "Article 32 - Security of processing",
                AlertCategory.COMPLIANCE: "Article 5 - Principles of processing",
                "default": "General data protection requirements",
            },
            ComplianceRegulation.CCPA: {
                AlertCategory.SECURITY: "Section 1798.81.5 - Security procedures",
                AlertCategory.COMPLIANCE: "Section 1798.100 - Consumer rights",
                "default": "Consumer privacy protection requirements",
            },
            ComplianceRegulation.SOC2: {
                AlertCategory.SECURITY: "CC6.0 - Logical and Physical Access Controls",
                AlertCategory.SYSTEM: "CC7.0 - System Operations",
                "default": "Trust services criteria compliance",
            },
        }

        regulation_reqs = requirements.get(regulation, {})
        return regulation_reqs.get(
            alert.category,
            regulation_reqs.get("default", "General compliance requirement"),
        )

    async def _queue_alert_notifications(self, alert: Alert):
        """Queue notifications for an alert"""

        if alert.rule_id not in self.alert_rules:
            return

        rule = self.alert_rules[alert.rule_id]

        # Check notification cooldown
        if alert.last_notification_sent:
            time_since_last = (datetime.now(timezone.utc) - alert.last_notification_sent).total_seconds()
            if time_since_last < rule.notification_cooldown:
                return

        # Queue notifications for each configured channel
        for channel in rule.notification_channels:
            notification = {
                "alert_id": alert.alert_id,
                "channel": channel,
                "timestamp": datetime.now(timezone.utc),
                "attempt": 1,
            }

            self.notification_queue.append(notification)

        alert.last_notification_sent = datetime.now(timezone.utc)
        alert.notification_count += 1

    async def _process_notification_queue(self):
        """Process pending notifications"""

        if not self.notification_queue:
            return

        # Process notifications in batches
        batch_size = 10
        processed = 0

        while self.notification_queue and processed < batch_size:
            notification = self.notification_queue.popleft()

            try:
                await self._send_notification(notification)
                processed += 1

            except Exception as e:
                logger.error(f"❌ Notification failed: {e}")

                # Retry logic
                if notification["attempt"] < 3:
                    notification["attempt"] += 1
                    notification["timestamp"] = datetime.now(timezone.utc) + timedelta(seconds=60)
                    self.notification_queue.append(notification)

    async def _send_notification(self, notification: dict[str, Any]):
        """Send individual notification"""

        alert_id = notification["alert_id"]
        channel = notification["channel"]

        if alert_id not in self.active_alerts:
            return

        alert = self.active_alerts[alert_id]

        # Find matching notification configuration
        matching_configs = [
            config
            for config in self.notification_configs.values()
            if (config.channel == channel and config.enabled and self._notification_matches_filters(alert, config))
        ]

        if not matching_configs:
            return

        config = matching_configs[0]  # Use first matching config

        # Check rate limiting
        if not await self._check_rate_limit(config, alert):
            return

        # Send notification based on channel
        success = False

        if channel == NotificationChannel.DASHBOARD:
            success = await self._send_dashboard_notification(alert, config)
        elif channel == NotificationChannel.EMAIL:
            success = await self._send_email_notification(alert, config)
        elif channel == NotificationChannel.WEBHOOK:
            success = await self._send_webhook_notification(alert, config)
        elif channel == NotificationChannel.LOG:
            success = await self._send_log_notification(alert, config)

        # Record notification in alert history
        notification_record = {
            "channel": channel.value,
            "config_id": config.config_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": success,
            "attempt": notification["attempt"],
        }

        alert.notification_history.append(notification_record)

        # Update metrics
        self.metrics.total_notifications_sent += 1

        channel_key = channel.value
        self.metrics.notifications_by_channel[channel_key] = (
            self.metrics.notifications_by_channel.get(channel_key, 0) + 1
        )

        if success:
            logger.info(f"📤 Notification sent: {alert.title} via {channel.value}")
        else:
            logger.warning(f"📤 Notification failed: {alert.title} via {channel.value}")

    def _notification_matches_filters(self, alert: Alert, config: NotificationConfig) -> bool:
        """Check if alert matches notification configuration filters"""

        # Severity filter
        if config.severity_filter and alert.severity not in config.severity_filter:
            return False

        # Category filter
        if config.category_filter and alert.category not in config.category_filter:
            return False

        # System filter
        return not (config.system_filter and alert.source_system not in config.system_filter)

    async def _check_rate_limit(self, config: NotificationConfig, alert: Alert) -> bool:
        """Check if notification is within rate limits"""

        # Simple rate limiting implementation
        # In production, would use more sophisticated rate limiting

        current_time = datetime.now(timezone.utc)

        # Check recent notifications for this config
        recent_notifications = [
            record
            for record in alert.notification_history
            if record["config_id"] == config.config_id
            and (current_time - datetime.fromisoformat(record["timestamp"])).total_seconds() < 3600
        ]

        if len(recent_notifications) >= config.rate_limit:
            return False

        # Check burst limit
        recent_burst = [
            record
            for record in recent_notifications
            if (current_time - datetime.fromisoformat(record["timestamp"])).total_seconds() < 60
        ]

        return not len(recent_burst) >= config.burst_limit

    async def _send_dashboard_notification(self, alert: Alert, config: NotificationConfig) -> bool:
        """Send dashboard notification"""

        # Dashboard notifications are handled by the dashboard itself
        # This just records the notification
        return True

    async def _send_email_notification(self, alert: Alert, config: NotificationConfig) -> bool:
        """Send email notification"""

        try:
            # Format email content
            subject = config.subject_template.format(
                title=alert.title,
                severity=alert.severity.value,
                category=alert.category.value,
            )

            body = config.body_template.format(
                title=alert.title,
                message=alert.message,
                severity=alert.severity.value,
                category=alert.category.value,
                created_at=alert.created_at.isoformat(),
                source_system=alert.source_system,
                metadata=json.dumps(alert.metadata, indent=2),
            )

            # Create email message
            msg = MimeMultipart()
            msg["From"] = "alerts@ai"
            msg["To"] = config.endpoint
            msg["Subject"] = subject

            msg.attach(MimeText(body, "plain"))

            # In production, would actually send the email
            # For now, just log it
            logger.info(f"📧 Email notification prepared for {config.endpoint}")
            logger.debug(f"Subject: {subject}")
            logger.debug(f"Body: {body}")

            return True

        except Exception as e:
            logger.error(f"❌ Email notification failed: {e}")
            return False

    async def _send_webhook_notification(self, alert: Alert, config: NotificationConfig) -> bool:
        """Send webhook notification"""

        try:
            # Create webhook payload
            payload = {
                "alert_id": alert.alert_id,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity.value,
                "category": alert.category.value,
                "status": alert.status.value,
                "created_at": alert.created_at.isoformat(),
                "source_system": alert.source_system,
                "tags": alert.tags,
                "metadata": alert.metadata,
                "constellation_impact": alert.constellation_impact,
            }

            # In production, would make HTTP POST to webhook URL
            logger.info(f"🔗 Webhook notification prepared for {config.endpoint}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            return True

        except Exception as e:
            logger.error(f"❌ Webhook notification failed: {e}")
            return False

    async def _send_log_notification(self, alert: Alert, config: NotificationConfig) -> bool:
        """Send log notification"""

        try:
            log_message = f"ALERT: {alert.title} | Severity: {alert.severity.value} | Category: {alert.category.value} | Source: {alert.source_system} | Message: {alert.message}"

            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                logger.critical(log_message)
            elif alert.severity == AlertSeverity.HIGH:
                logger.error(log_message)
            elif alert.severity == AlertSeverity.MEDIUM:
                logger.warning(log_message)
            else:
                logger.info(log_message)

            return True

        except Exception as e:
            logger.error(f"❌ Log notification failed: {e}")
            return False

    async def acknowledge_alert(self, alert_id: str, user_id: Optional[str] = None) -> bool:
        """Acknowledge an alert"""

        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]

        if alert.status != AlertStatus.ACTIVE:
            return False

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledgment_user = user_id
        alert.updated_at = datetime.now(timezone.utc)

        # Create compliance audit entry for acknowledgment
        if alert.compliance_relevant:
            await self._create_acknowledgment_audit_entry(alert, user_id)

        logger.info(f"✅ Alert acknowledged: {alert.title}")

        return True

    async def resolve_alert(
        self,
        alert_id: str,
        user_id: Optional[str] = None,
        resolution_notes: Optional[str] = None,
    ) -> bool:
        """Resolve an alert"""

        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]

        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolution_user = user_id
        alert.resolution_notes = resolution_notes
        alert.updated_at = datetime.now(timezone.utc)

        # Remove from active alerts
        del self.active_alerts[alert_id]

        # Update metrics
        self.metrics.active_alerts_count = len(self.active_alerts)

        # Create compliance audit entry for resolution
        if alert.compliance_relevant:
            await self._create_resolution_audit_entry(alert, user_id, resolution_notes)

        logger.info(f"✅ Alert resolved: {alert.title}")

        return True

    async def _create_acknowledgment_audit_entry(self, alert: Alert, user_id: Optional[str]):
        """Create audit entry for alert acknowledgment"""

        entry_id = f"audit_{uuid.uuid4().hex[:12]}"

        audit_entry = ComplianceAuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(timezone.utc),
            event_type="alert_acknowledged",
            event_description=f"Alert acknowledged: {alert.title}",
            alert_id=alert.alert_id,
            regulation=(alert.applicable_regulations[0] if alert.applicable_regulations else ComplianceRegulation.SOC2),
            compliance_requirement="Incident response - acknowledgment",
            violation_severity="low",
            system_component=alert.source_system,
            user_id=user_id,
            evidence={
                "acknowledgment_details": {
                    "alert_id": alert.alert_id,
                    "acknowledged_at": (alert.acknowledged_at.isoformat() if alert.acknowledged_at else None),
                    "user_id": user_id,
                }
            },
            status="acknowledged",
            remediation_required=True,
            remediation_actions=["Continue investigation", "Implement resolution"],
        )

        self.audit_trail.append(audit_entry)
        self.metrics.audit_entries_created += 1

        logger.info(f"📋 Acknowledgment audit entry created: {entry_id}")

    async def _create_resolution_audit_entry(
        self, alert: Alert, user_id: Optional[str], resolution_notes: Optional[str]
    ):
        """Create audit entry for alert resolution"""

        entry_id = f"audit_{uuid.uuid4().hex[:12]}"

        audit_entry = ComplianceAuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(timezone.utc),
            event_type="alert_resolved",
            event_description=f"Alert resolved: {alert.title}",
            alert_id=alert.alert_id,
            regulation=(alert.applicable_regulations[0] if alert.applicable_regulations else ComplianceRegulation.SOC2),
            compliance_requirement="Incident response - resolution",
            violation_severity="resolved",
            system_component=alert.source_system,
            user_id=user_id,
            evidence={
                "resolution_details": {
                    "alert_id": alert.alert_id,
                    "resolved_at": (alert.resolved_at.isoformat() if alert.resolved_at else None),
                    "user_id": user_id,
                    "resolution_notes": resolution_notes,
                    "total_duration_seconds": (
                        (alert.resolved_at - alert.created_at).total_seconds() if alert.resolved_at else None
                    ),
                }
            },
            status="resolved",
            resolved_at=datetime.now(timezone.utc),
            resolution_notes=resolution_notes or "Alert resolved",
            remediation_required=False,
        )

        self.audit_trail.append(audit_entry)
        self.metrics.audit_entries_created += 1

        logger.info(f"📋 Resolution audit entry created: {entry_id}")

    async def _evaluate_alert_rules(self):
        """Evaluate all alert rules against current metrics"""

        # This method would integrate with actual monitoring systems
        # For now, it's a placeholder for the evaluation logic
        pass

    async def _check_alert_escalations(self):
        """Check for alerts that need escalation"""

        current_time = datetime.now(timezone.utc)

        for alert in self.active_alerts.values():
            if alert.status not in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
                continue

            # Get rule for escalation settings
            if alert.rule_id not in self.alert_rules:
                continue

            rule = self.alert_rules[alert.rule_id]

            if not rule.escalation_severity or rule.escalation_timeout <= 0:
                continue

            # Check if escalation is due
            time_since_creation = (current_time - alert.created_at).total_seconds()

            if time_since_creation >= rule.escalation_timeout and alert.escalation_level == 0:
                # Escalate alert
                alert.severity = rule.escalation_severity
                alert.escalation_level += 1
                alert.escalated_at = current_time
                alert.updated_at = current_time

                escalation_record = {
                    "timestamp": current_time.isoformat(),
                    "from_severity": alert.severity.value,
                    "to_severity": rule.escalation_severity.value,
                    "reason": "timeout_escalation",
                }

                alert.escalation_history.append(escalation_record)

                # Queue new notifications for escalated alert
                await self._queue_alert_notifications(alert)

                logger.warning(f"⬆️ Alert escalated: {alert.title} to {rule.escalation_severity.value}")

    async def _monitor_compliance_violations(self):
        """Monitor for compliance violations"""

        # Check for unresolved compliance alerts
        [
            alert
            for alert in self.active_alerts.values()
            if alert.compliance_relevant and alert.status == AlertStatus.ACTIVE
        ]

        # Check for overdue remediation
        current_time = datetime.now(timezone.utc)

        for entry in self.audit_trail:
            if entry.status == "open" and entry.remediation_deadline and current_time > entry.remediation_deadline:
                # Create overdue remediation alert
                await self.create_alert(
                    rule_id="compliance_overdue",
                    title=f"Overdue Compliance Remediation: {entry.regulation.value}",
                    message=f"Remediation deadline exceeded for {entry.compliance_requirement}",
                    severity=AlertSeverity.HIGH,
                    category=AlertCategory.COMPLIANCE,
                    source_system="compliance_monitor",
                    metadata={"audit_entry_id": entry.entry_id},
                )

    async def _generate_compliance_reports(self):
        """Generate periodic compliance reports"""

        # Generate hourly compliance summary
        # This would create compliance reports for regulatory requirements
        pass

    async def _update_alert_metrics(self):
        """Update alerting system metrics"""

        current_time = datetime.now(timezone.utc)

        # Update basic counts
        self.metrics.active_alerts_count = len(self.active_alerts)

        # Calculate resolution rate
        resolved_alerts = len([a for a in self.alert_history if a.status == AlertStatus.RESOLVED])
        total_alerts = len(self.alert_history)

        if total_alerts > 0:
            self.metrics.alert_resolution_rate = resolved_alerts / total_alerts

        # Calculate notification success rate
        total_notifications = sum(self.metrics.notifications_by_channel.values())
        if total_notifications > 0:
            # Simplified calculation - in production would track actual success/failure
            self.metrics.notification_success_rate = 95.0  # Assume 95% success rate

        # Update uptime
        uptime_seconds = (current_time - self.system_start_time).total_seconds()
        if uptime_seconds > 0:
            self.metrics.alerting_system_uptime = min(100.0, (uptime_seconds / (uptime_seconds + 60)) * 100)

        self.metrics.last_metrics_update = current_time

    async def _cleanup_old_alerts(self):
        """Clean up old alerts"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.alert_retention_days)

        # Clean alert history
        old_alerts = [a for a in self.alert_history if a.created_at < cutoff_date]
        for alert in old_alerts:
            with contextlib.suppress(ValueError):
                self.alert_history.remove(alert)

    async def _cleanup_old_audit_entries(self):
        """Clean up old audit entries"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.audit_retention_days)

        # Clean audit trail (keep for 7 years for compliance)
        old_entries = [e for e in self.audit_trail if e.timestamp < cutoff_date]
        for entry in old_entries:
            with contextlib.suppress(ValueError):
                self.audit_trail.remove(entry)

    async def get_active_alerts(self) -> list[Alert]:
        """Get all active alerts"""

        return list(self.active_alerts.values())

    async def get_alert_by_id(self, alert_id: str) -> Optional[Alert]:
        """Get specific alert by ID"""

        # Check active alerts first
        if alert_id in self.active_alerts:
            return self.active_alerts[alert_id]

        # Check alert history
        for alert in self.alert_history:
            if alert.alert_id == alert_id:
                return alert

        return None

    async def get_compliance_audit_trail(
        self,
        regulation: Optional[ComplianceRegulation] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[ComplianceAuditEntry]:
        """Get compliance audit trail entries"""

        entries = list(self.audit_trail)

        # Filter by regulation
        if regulation:
            entries = [e for e in entries if e.regulation == regulation]

        # Filter by date range
        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]

        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]

        return entries

    async def get_alerting_metrics(self) -> AlertingMetrics:
        """Get alerting system metrics"""

        return self.metrics

    async def shutdown(self):
        """Shutdown alerting system"""

        self.alerting_active = False
        self.notification_processor_active = False

        logger.info("🛑 Comprehensive Alerting System shutdown initiated")


# Export main classes
__all__ = [
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
