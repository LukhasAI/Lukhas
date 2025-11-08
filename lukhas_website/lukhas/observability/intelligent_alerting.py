#!/usr/bin/env python3
"""
LUKHAS Intelligent Alerting Framework
Advanced alerting system with intelligent escalation, noise reduction, and correlation.

Features:
- Intelligent alert correlation and deduplication
- Multi-tier escalation with customizable rules
- Alert fatigue prevention and noise reduction
- Integration with external alerting systems
- Evidence-based alerting with audit trails
- Dynamic threshold adjustment based on patterns
- Alert storm detection and mitigation
"""

import asyncio
import json
import smtplib
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from .advanced_metrics import MetricSeverity, get_advanced_metrics
from .evidence_collection import EvidenceType, collect_evidence


class AlertState(Enum):
    """Alert state lifecycle"""
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"


class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"
    DASHBOARD = "dashboard"


class EscalationLevel(Enum):
    """Alert escalation levels"""
    L1_MONITORING = "l1_monitoring"
    L2_ENGINEERING = "l2_engineering"
    L3_SENIOR_ENGINEERING = "l3_senior_engineering"
    L4_MANAGEMENT = "l4_management"
    L5_EXECUTIVE = "l5_executive"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    condition: str  # Metric condition expression
    severity: MetricSeverity
    notification_channels: list[NotificationChannel]
    escalation_rules: dict[EscalationLevel, timedelta]
    suppression_window: timedelta = timedelta(minutes=15)
    max_alerts_per_hour: int = 10
    correlation_tags: list[str] = field(default_factory=list)
    runbook_url: Optional[str] = None
    enabled: bool = True


@dataclass
class Alert:
    """Active alert instance"""
    alert_id: str
    rule_id: str
    title: str
    description: str
    severity: MetricSeverity
    state: AlertState
    source_component: str
    metric_name: str
    current_value: float
    threshold_value: float
    labels: dict[str, str]
    annotations: dict[str, str]
    created_at: datetime
    updated_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    escalation_level: EscalationLevel = EscalationLevel.L1_MONITORING
    correlation_id: Optional[str] = None
    evidence_ids: list[str] = field(default_factory=list)
    notification_history: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class NotificationTemplate:
    """Notification message template"""
    channel: NotificationChannel
    subject_template: str
    body_template: str
    format_type: str = "text"  # text, html, markdown


@dataclass
class EscalationPolicy:
    """Escalation policy configuration"""
    policy_id: str
    name: str
    escalation_rules: dict[EscalationLevel, dict[str, Any]]
    enabled: bool = True


class IntelligentAlertingSystem:
    """
    Intelligent alerting system with noise reduction and smart escalation.
    Provides comprehensive alerting capabilities for LUKHAS operations.
    """

    def __init__(
        self,
        config_path: str = "./config/alerting.json",
        smtp_config: Optional[dict[str, str]] = None,
        webhook_timeout: int = 30,
        enable_storm_detection: bool = True,
        alert_history_days: int = 30,
    ):
        """
        Initialize intelligent alerting system.

        Args:
            config_path: Path to alerting configuration file
            smtp_config: SMTP configuration for email notifications
            webhook_timeout: Timeout for webhook notifications
            enable_storm_detection: Enable alert storm detection
            alert_history_days: Days to retain alert history
        """
        self.config_path = Path(config_path)
        self.smtp_config = smtp_config
        self.webhook_timeout = webhook_timeout
        self.enable_storm_detection = enable_storm_detection
        self.alert_history_days = alert_history_days

        # Core state
        self.alert_rules: dict[str, AlertRule] = {}
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: list[Alert] = []
        self.escalation_policies: dict[str, EscalationPolicy] = {}
        self.notification_templates: dict[NotificationChannel, NotificationTemplate] = {}

        # Alert correlation and deduplication
        self.correlation_groups: dict[str, set[str]] = defaultdict(set)
        self.alert_fingerprints: dict[str, datetime] = {}

        # Storm detection
        self.alert_rate_tracker: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.suppressed_alerts: set[str] = set()

        # Background tasks
        self._escalation_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

        # Integration with advanced metrics
        self.advanced_metrics = get_advanced_metrics()

        # Initialize system
        self._load_configuration()
        self._initialize_templates()
        self._start_background_tasks()

    def _load_configuration(self):
        """Load alerting configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = json.load(f)

                # Load alert rules
                for rule_data in config.get("alert_rules", []):
                    rule = AlertRule(
                        rule_id=rule_data["rule_id"],
                        name=rule_data["name"],
                        condition=rule_data["condition"],
                        severity=MetricSeverity(rule_data["severity"]),
                        notification_channels=[NotificationChannel(c) for c in rule_data["channels"]],
                        escalation_rules={
                            EscalationLevel(level): timedelta(seconds=seconds)
                            for level, seconds in rule_data["escalation_rules"].items()
                        },
                        suppression_window=timedelta(seconds=rule_data.get("suppression_window", 900)),
                        max_alerts_per_hour=rule_data.get("max_alerts_per_hour", 10),
                        correlation_tags=rule_data.get("correlation_tags", []),
                        runbook_url=rule_data.get("runbook_url"),
                        enabled=rule_data.get("enabled", True),
                    )
                    self.alert_rules[rule.rule_id] = rule

                # Load escalation policies
                for policy_data in config.get("escalation_policies", []):
                    policy = EscalationPolicy(
                        policy_id=policy_data["policy_id"],
                        name=policy_data["name"],
                        escalation_rules=policy_data["escalation_rules"],
                        enabled=policy_data.get("enabled", True),
                    )
                    self.escalation_policies[policy.policy_id] = policy

            except Exception as e:
                print(f"Warning: Failed to load alerting configuration: {e}")

        # Create default rules if none exist
        if not self.alert_rules:
            self._create_default_rules()

    def _create_default_rules(self):
        """Create default alerting rules for LUKHAS"""
        default_rules = [
            AlertRule(
                rule_id="high_response_time",
                name="High Response Time",
                condition="lukhas_response_time_seconds > 0.25",
                severity=MetricSeverity.CRITICAL,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                escalation_rules={
                    EscalationLevel.L1_MONITORING: timedelta(minutes=5),
                    EscalationLevel.L2_ENGINEERING: timedelta(minutes=15),
                    EscalationLevel.L3_SENIOR_ENGINEERING: timedelta(minutes=30),
                },
                correlation_tags=["performance", "user_experience"],
                runbook_url="https://docs.ai/runbooks/high-response-time",
            ),
            AlertRule(
                rule_id="evidence_collection_failure",
                name="Evidence Collection Failure",
                condition="lukhas_evidence_collection_errors > 5",
                severity=MetricSeverity.CRITICAL,
                notification_channels=[NotificationChannel.EMAIL],
                escalation_rules={
                    EscalationLevel.L2_ENGINEERING: timedelta(minutes=10),
                    EscalationLevel.L3_SENIOR_ENGINEERING: timedelta(minutes=20),
                    EscalationLevel.L4_MANAGEMENT: timedelta(minutes=60),
                },
                correlation_tags=["compliance", "evidence", "audit"],
                runbook_url="https://docs.ai/runbooks/evidence-collection-failure",
            ),
            AlertRule(
                rule_id="anomaly_detection_critical",
                name="Critical System Anomaly Detected",
                condition="lukhas_anomaly_critical > 0",
                severity=MetricSeverity.EMERGENCY,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.WEBHOOK],
                escalation_rules={
                    EscalationLevel.L2_ENGINEERING: timedelta(minutes=2),
                    EscalationLevel.L3_SENIOR_ENGINEERING: timedelta(minutes=5),
                    EscalationLevel.L4_MANAGEMENT: timedelta(minutes=15),
                },
                correlation_tags=["anomaly", "system_health"],
                max_alerts_per_hour=5,  # Lower for critical anomalies
            ),
        ]

        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule

    def _initialize_templates(self):
        """Initialize notification templates"""
        self.notification_templates[NotificationChannel.EMAIL] = NotificationTemplate(
            channel=NotificationChannel.EMAIL,
            subject_template="[LUKHAS {severity}] {title}",
            body_template="""
LUKHAS Alert: {title}

Description: {description}
Severity: {severity}
Component: {source_component}
Metric: {metric_name} = {current_value} (threshold: {threshold_value})

Timestamp: {created_at}
Alert ID: {alert_id}

Labels:
{labels}

Runbook: {runbook_url}

---
This is an automated alert from LUKHAS AI System.
            """.strip(),
            format_type="text",
        )

        self.notification_templates[NotificationChannel.SLACK] = NotificationTemplate(
            channel=NotificationChannel.SLACK,
            subject_template="{title}",
            body_template="""
🚨 *LUKHAS Alert: {title}*

*Description:* {description}
*Severity:* {severity}
*Component:* {source_component}
*Metric:* {metric_name} = {current_value} (threshold: {threshold_value})

*Alert ID:* {alert_id}
*Timestamp:* {created_at}

{runbook_url}
            """.strip(),
            format_type="markdown",
        )

    async def trigger_alert(
        self,
        rule_id: str,
        source_component: str,
        metric_name: str,
        current_value: float,
        threshold_value: float,
        labels: Optional[dict[str, str]] = None,
        annotations: Optional[dict[str, str]] = None,
        correlation_id: Optional[str] = None,
    ) -> str:
        """
        Trigger an alert based on metric conditions.

        Args:
            rule_id: ID of the alert rule
            source_component: Component that triggered the alert
            metric_name: Name of the triggering metric
            current_value: Current metric value
            threshold_value: Threshold that was breached
            labels: Additional labels for the alert
            annotations: Additional annotations
            correlation_id: Correlation ID for tracking

        Returns:
            Alert ID
        """
        if rule_id not in self.alert_rules:
            raise ValueError(f"Unknown alert rule: {rule_id}")

        rule = self.alert_rules[rule_id]
        if not rule.enabled:
            return ""

        # Check for alert storm
        if self.enable_storm_detection and self._is_alert_storm(rule_id):
            return ""

        # Generate alert fingerprint for deduplication
        fingerprint = self._generate_alert_fingerprint(
            rule_id, source_component, metric_name, labels or {}
        )

        # Check if alert is suppressed
        if fingerprint in self.alert_fingerprints:
            last_alert_time = self.alert_fingerprints[fingerprint]
            if datetime.now(timezone.utc) - last_alert_time < rule.suppression_window:
                return ""

        # Create new alert
        alert_id = str(uuid4())
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule_id,
            title=rule.name,
            description=f"{rule.name} triggered for {source_component}",
            severity=rule.severity,
            state=AlertState.FIRING,
            source_component=source_component,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            labels=labels or {},
            annotations=annotations or {},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            correlation_id=correlation_id,
        )

        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_fingerprints[fingerprint] = alert.created_at

        # Track alert rate
        self.alert_rate_tracker[rule_id].append(alert.created_at)

        # Correlate with existing alerts
        await self._correlate_alert(alert)

        # Send initial notifications
        await self._send_notifications(alert)

        # Collect evidence
        evidence_id = await collect_evidence(
            evidence_type=EvidenceType.SYSTEM_EVENT,
            source_component="intelligent_alerting",
            operation="alert_triggered",
            payload={
                "alert_id": alert_id,
                "rule_id": rule_id,
                "title": alert.title,
                "severity": rule.severity.value,
                "metric_name": metric_name,
                "current_value": current_value,
                "threshold_value": threshold_value,
                "labels": labels,
                "correlation_id": correlation_id,
            },
            correlation_id=correlation_id,
        )
        alert.evidence_ids.append(evidence_id)

        return alert_id

    def _generate_alert_fingerprint(
        self,
        rule_id: str,
        source_component: str,
        metric_name: str,
        labels: dict[str, str],
    ) -> str:
        """Generate unique fingerprint for alert deduplication"""
        fingerprint_data = {
            "rule_id": rule_id,
            "source_component": source_component,
            "metric_name": metric_name,
            "labels": sorted(labels.items()),
        }
        import hashlib
        return hashlib.md5(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()

    def _is_alert_storm(self, rule_id: str) -> bool:
        """Check if we're experiencing an alert storm for this rule"""
        if rule_id not in self.alert_rules:
            return False

        rule = self.alert_rules[rule_id]
        recent_alerts = [
            timestamp for timestamp in self.alert_rate_tracker[rule_id]
            if (datetime.now(timezone.utc) - timestamp).total_seconds() < 3600  # Last hour
        ]

        if len(recent_alerts) > rule.max_alerts_per_hour:
            if rule_id not in self.suppressed_alerts:
                self.suppressed_alerts.add(rule_id)
                print(f"Alert storm detected for rule {rule_id}, suppressing further alerts")
            return True

        # Remove from suppressed if rate has decreased
        if rule_id in self.suppressed_alerts and len(recent_alerts) < rule.max_alerts_per_hour * 0.5:
            self.suppressed_alerts.remove(rule_id)
            print(f"Alert storm resolved for rule {rule_id}, resuming alerts")

        return False

    async def _correlate_alert(self, alert: Alert):
        """Correlate alert with existing alerts"""
        rule = self.alert_rules[alert.rule_id]

        # Group alerts by correlation tags
        for tag in rule.correlation_tags:
            self.correlation_groups[tag].add(alert.alert_id)

        # Find related alerts
        related_alerts = set()
        for tag in rule.correlation_tags:
            related_alerts.update(self.correlation_groups[tag])

        if len(related_alerts) > 1:
            # Create correlation ID if not exists
            if not alert.correlation_id:
                alert.correlation_id = f"correlation_{uuid4()}"

            # Apply correlation ID to related alerts
            for related_alert_id in related_alerts:
                if related_alert_id in self.active_alerts:
                    self.active_alerts[related_alert_id].correlation_id = alert.correlation_id

    async def _send_notifications(self, alert: Alert):
        """Send notifications for an alert"""
        rule = self.alert_rules[alert.rule_id]

        for channel in rule.notification_channels:
            try:
                success = await self._send_notification(alert, channel)

                # Record notification attempt
                alert.notification_history.append({
                    "channel": channel.value,
                    "success": success,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

            except Exception as e:
                print(f"Failed to send notification via {channel.value}: {e}")

    async def _send_notification(self, alert: Alert, channel: NotificationChannel) -> bool:
        """Send notification via specific channel"""
        template = self.notification_templates.get(channel)
        if not template:
            return False

        try:
            # Format message
            context = {
                "title": alert.title,
                "description": alert.description,
                "severity": alert.severity.value.upper(),
                "source_component": alert.source_component,
                "metric_name": alert.metric_name,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "alert_id": alert.alert_id,
                "created_at": alert.created_at.isoformat(),
                "labels": "\n".join([f"  {k}: {v}" for k, v in alert.labels.items()]),
                "runbook_url": self.alert_rules[alert.rule_id].runbook_url or "N/A",
            }

            subject = template.subject_template.format(**context)
            body = template.body_template.format(**context)

            if channel == NotificationChannel.EMAIL:
                return await self._send_email_notification(subject, body, alert)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook_notification(subject, body, alert)
            elif channel == NotificationChannel.DASHBOARD:
                return await self._send_dashboard_notification(alert)
            # Add other channels as needed

            return True

        except Exception as e:
            print(f"Notification formatting error for {channel.value}: {e}")
            return False

    async def _send_email_notification(self, subject: str, body: str, alert: Alert) -> bool:
        """Send email notification"""
        if not self.smtp_config:
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = self.smtp_config['to_email']
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                if self.smtp_config.get('use_tls'):
                    server.starttls()
                if self.smtp_config.get('username'):
                    server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Email notification error: {e}")
            return False

    async def _send_webhook_notification(self, subject: str, body: str, alert: Alert) -> bool:
        """Send webhook notification"""
        if not AIOHTTP_AVAILABLE:
            return False

        webhook_url = self.smtp_config.get('webhook_url') if self.smtp_config else None
        if not webhook_url:
            return False

        try:
            payload = {
                "alert_id": alert.alert_id,
                "title": subject,
                "body": body,
                "severity": alert.severity.value,
                "timestamp": alert.created_at.isoformat(),
                "labels": alert.labels,
                "annotations": alert.annotations,
            }

            async with aiohttp.ClientSession() as session, session.post(
                webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.webhook_timeout)
            ) as response:
                return response.status < 400

        except Exception as e:
            print(f"Webhook notification error: {e}")
            return False

    async def _send_dashboard_notification(self, alert: Alert) -> bool:
        """Send dashboard notification (store in memory/cache)"""
        # This would integrate with the dashboard system
        # For now, just return True to indicate successful "notification"
        return True

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an active alert"""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        if alert.state != AlertState.FIRING:
            return False

        alert.state = AlertState.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledged_by = acknowledged_by
        alert.updated_at = datetime.now(timezone.utc)

        # Collect evidence
        await collect_evidence(
            evidence_type=EvidenceType.USER_INTERACTION,
            source_component="intelligent_alerting",
            operation="alert_acknowledged",
            payload={
                "alert_id": alert_id,
                "acknowledged_by": acknowledged_by,
                "acknowledgment_time": alert.acknowledged_at.isoformat(),
            },
            user_id=acknowledged_by,
            correlation_id=alert.correlation_id,
        )

        return True

    async def resolve_alert(self, alert_id: str, resolved_by: Optional[str] = None) -> bool:
        """Resolve an active alert"""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.state = AlertState.RESOLVED
        alert.resolved_at = datetime.now(timezone.utc)
        alert.updated_at = datetime.now(timezone.utc)

        # Move to history
        self.alert_history.append(alert)
        del self.active_alerts[alert_id]

        # Collect evidence
        await collect_evidence(
            evidence_type=EvidenceType.SYSTEM_EVENT,
            source_component="intelligent_alerting",
            operation="alert_resolved",
            payload={
                "alert_id": alert_id,
                "resolved_by": resolved_by,
                "resolution_time": alert.resolved_at.isoformat(),
                "duration_seconds": (alert.resolved_at - alert.created_at).total_seconds(),
            },
            user_id=resolved_by,
            correlation_id=alert.correlation_id,
        )

        return True

    def get_active_alerts(
        self,
        severity_filter: Optional[MetricSeverity] = None,
        component_filter: Optional[str] = None,
    ) -> list[Alert]:
        """Get list of active alerts with optional filtering"""
        alerts = list(self.active_alerts.values())

        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]

        if component_filter:
            alerts = [a for a in alerts if a.source_component == component_filter]

        return sorted(alerts, key=lambda x: x.created_at, reverse=True)

    def get_alert_statistics(self, hours_back: int = 24) -> dict[str, Any]:
        """Get alert statistics for dashboard"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)

        # Recent alerts (active + recently resolved)
        recent_alerts = list(self.active_alerts.values())
        recent_alerts.extend([
            a for a in self.alert_history
            if a.created_at >= cutoff_time
        ])

        # Statistics
        stats = {
            "total_active": len(self.active_alerts),
            "total_recent": len(recent_alerts),
            "by_severity": defaultdict(int),
            "by_component": defaultdict(int),
            "average_resolution_time_minutes": 0,
            "acknowledged_percentage": 0,
            "suppressed_rules": len(self.suppressed_alerts),
        }

        if recent_alerts:
            for alert in recent_alerts:
                stats["by_severity"][alert.severity.value] += 1
                stats["by_component"][alert.source_component] += 1

            # Resolution time for resolved alerts
            resolved_alerts = [a for a in recent_alerts if a.resolved_at]
            if resolved_alerts:
                resolution_times = [
                    (a.resolved_at - a.created_at).total_seconds() / 60
                    for a in resolved_alerts
                ]
                stats["average_resolution_time_minutes"] = sum(resolution_times) / len(resolution_times)

            # Acknowledgment rate
            acknowledged_count = len([a for a in recent_alerts if a.acknowledged_at])
            stats["acknowledged_percentage"] = (acknowledged_count / len(recent_alerts)) * 100

        return dict(stats)

    def _start_background_tasks(self):
        """Start background tasks for alert management"""
        async def escalation_worker():
            while True:
                try:
                    await self._process_escalations()
                    await asyncio.sleep(60)  # Check every minute
                except Exception as e:
                    print(f"Escalation worker error: {e}")
                    await asyncio.sleep(60)

        async def cleanup_worker():
            while True:
                try:
                    await self._cleanup_old_alerts()
                    await asyncio.sleep(3600)  # Check hourly
                except Exception as e:
                    print(f"Cleanup worker error: {e}")
                    await asyncio.sleep(3600)

        # Start background tasks if event loop is available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._escalation_task = loop.create_task(escalation_worker())
                self._cleanup_task = loop.create_task(cleanup_worker())
        except RuntimeError:
            # No event loop running
            pass

    async def _process_escalations(self):
        """Process alert escalations"""
        current_time = datetime.now(timezone.utc)

        for alert in self.active_alerts.values():
            if alert.state not in [AlertState.FIRING, AlertState.ACKNOWLEDGED]:
                continue

            rule = self.alert_rules[alert.rule_id]

            # Check if alert needs escalation
            for level, delay in rule.escalation_rules.items():
                escalation_time = alert.created_at + delay

                if (current_time >= escalation_time and
                    alert.escalation_level.value < level.value and
                    alert.state != AlertState.ACKNOWLEDGED):

                    await self._escalate_alert(alert, level)

    async def _escalate_alert(self, alert: Alert, new_level: EscalationLevel):
        """Escalate an alert to a higher level"""
        old_level = alert.escalation_level
        alert.escalation_level = new_level
        alert.state = AlertState.ESCALATED
        alert.updated_at = datetime.now(timezone.utc)

        # Send escalation notifications
        await self._send_notifications(alert)

        # Collect evidence
        await collect_evidence(
            evidence_type=EvidenceType.SYSTEM_EVENT,
            source_component="intelligent_alerting",
            operation="alert_escalated",
            payload={
                "alert_id": alert.alert_id,
                "old_level": old_level.value,
                "new_level": new_level.value,
                "escalation_time": alert.updated_at.isoformat(),
            },
            correlation_id=alert.correlation_id,
        )

    async def _cleanup_old_alerts(self):
        """Clean up old alert data"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.alert_history_days)

        # Clean alert history
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.created_at >= cutoff_time
        ]

        # Clean alert fingerprints
        self.alert_fingerprints = {
            fingerprint: timestamp
            for fingerprint, timestamp in self.alert_fingerprints.items()
            if timestamp >= cutoff_time
        }

        # Clean alert rate trackers
        for rule_id in self.alert_rate_tracker:
            self.alert_rate_tracker[rule_id] = deque([
                timestamp for timestamp in self.alert_rate_tracker[rule_id]
                if timestamp >= cutoff_time
            ], maxlen=100)

    async def shutdown(self):
        """Shutdown alerting system"""
        if self._escalation_task:
            self._escalation_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()


# Global instance
_alerting_system: Optional[IntelligentAlertingSystem] = None


def initialize_alerting(
    config_path: str = "./config/alerting.json",
    **kwargs
) -> IntelligentAlertingSystem:
    """Initialize global alerting system"""
    global _alerting_system
    _alerting_system = IntelligentAlertingSystem(config_path=config_path, **kwargs)
    return _alerting_system


def get_alerting_system() -> IntelligentAlertingSystem:
    """Get or create global alerting system"""
    global _alerting_system
    if _alerting_system is None:
        _alerting_system = initialize_alerting()
    return _alerting_system


async def trigger_alert(rule_id: str, source_component: str, **kwargs) -> str:
    """Convenience function for triggering alerts"""
    system = get_alerting_system()
    return await system.trigger_alert(rule_id, source_component, **kwargs)


async def shutdown_alerting():
    """Shutdown global alerting system"""
    global _alerting_system
    if _alerting_system:
        await _alerting_system.shutdown()
        _alerting_system = None
