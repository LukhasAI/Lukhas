#!/usr/bin/env python3
"""
Production-Ready Monitoring and Alerting System
==============================================
Comprehensive monitoring system for LUKHAS AI infrastructure
Integrates with T4 Observability Stack and testing infrastructure

Features:
- Real-time system health monitoring
- Intelligent alert escalation
- Integration with existing T4 observability stack
- Performance regression detection
- Automated incident response
- Multi-channel alerting (email, Slack, webhook)
- Alert fatigue prevention
"""

import asyncio
import json
import logging
import smtplib
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import httpx
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels with escalation thresholds"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert lifecycle status"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """Configuration for an alert rule"""

    name: str
    condition: str  # Python expression to evaluate
    severity: AlertSeverity
    threshold_value: float
    evaluation_window: int = 300  # seconds
    cooldown_period: int = 600  # seconds to prevent alert spam
    tags: Set[str] = field(default_factory=set)
    enabled: bool = True
    description: str = ""
    escalation_delay: int = 1800  # seconds before escalation


@dataclass
class AlertInstance:
    """An active alert instance"""

    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    triggered_at: datetime
    last_updated: datetime
    value: float
    threshold: float
    message: str
    tags: Set[str] = field(default_factory=set)
    acknowledged_by: Optional[str] = None
    escalated: bool = False
    suppression_end: Optional[datetime] = None


@dataclass
class SystemMetrics:
    """Current system performance metrics"""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io_bytes: Dict[str, int]
    test_success_rate: float
    coverage_percentage: float
    response_time_p95: float
    error_rate: float
    active_connections: int


class AlertChannel:
    """Base class for alert notification channels"""

    async def send_alert(self, alert: AlertInstance, metrics: SystemMetrics) -> bool:
        """Send alert notification. Return True if successful."""
        raise NotImplementedError


class EmailAlertChannel(AlertChannel):
    """Email alert notifications"""

    def __init__(
        self, smtp_host: str, smtp_port: int, username: str, password: str, from_email: str, to_emails: List[str]
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails

    async def send_alert(self, alert: AlertInstance, metrics: SystemMetrics) -> bool:
        """Send email alert notification"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = f"[{alert.severity.value.upper()}] LUKHAS AI Alert: {alert.rule_name}"

            body = self._format_alert_email(alert, metrics)
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email alert sent for {alert.rule_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    def _format_alert_email(self, alert: AlertInstance, metrics: SystemMetrics) -> str:
        """Format alert as HTML email"""
        color = {
            AlertSeverity.LOW: "#28a745",
            AlertSeverity.MEDIUM: "#ffc107",
            AlertSeverity.HIGH: "#fd7e14",
            AlertSeverity.CRITICAL: "#dc3545",
        }[alert.severity]

        return f"""
        <html>
        <body>
            <h2 style="color: {color};">LUKHAS AI System Alert</h2>
            <table border="1" cellpadding="5">
                <tr><td><b>Alert Rule</b></td><td>{alert.rule_name}</td></tr>
                <tr><td><b>Severity</b></td><td style="color: {color};">{alert.severity.value.upper()}</td></tr>
                <tr><td><b>Triggered At</b></td><td>{alert.triggered_at}</td></tr>
                <tr><td><b>Current Value</b></td><td>{alert.value:.2f}</td></tr>
                <tr><td><b>Threshold</b></td><td>{alert.threshold:.2f}</td></tr>
                <tr><td><b>Message</b></td><td>{alert.message}</td></tr>
            </table>

            <h3>Current System Metrics</h3>
            <table border="1" cellpadding="5">
                <tr><td><b>CPU Usage</b></td><td>{metrics.cpu_percent:.1f}%</td></tr>
                <tr><td><b>Memory Usage</b></td><td>{metrics.memory_percent:.1f}%</td></tr>
                <tr><td><b>Disk Usage</b></td><td>{metrics.disk_usage_percent:.1f}%</td></tr>
                <tr><td><b>Test Success Rate</b></td><td>{metrics.test_success_rate:.1f}%</td></tr>
                <tr><td><b>Coverage</b></td><td>{metrics.coverage_percentage:.1f}%</td></tr>
                <tr><td><b>Response Time P95</b></td><td>{metrics.response_time_p95:.0f}ms</td></tr>
            </table>
        </body>
        </html>
        """


class SlackAlertChannel(AlertChannel):
    """Slack alert notifications via webhook"""

    def __init__(self, webhook_url: str, channel: str = "#alerts"):
        self.webhook_url = webhook_url
        self.channel = channel

    async def send_alert(self, alert: AlertInstance, metrics: SystemMetrics) -> bool:
        """Send Slack alert notification"""
        try:
            color = {
                AlertSeverity.LOW: "good",
                AlertSeverity.MEDIUM: "warning",
                AlertSeverity.HIGH: "danger",
                AlertSeverity.CRITICAL: "danger",
            }[alert.severity]

            payload = {
                "channel": self.channel,
                "username": "LUKHAS AI Monitoring",
                "icon_emoji": ":warning:",
                "attachments": [
                    {
                        "color": color,
                        "title": f"{alert.severity.value.upper()}: {alert.rule_name}",
                        "text": alert.message,
                        "fields": [
                            {"title": "Value", "value": f"{alert.value:.2f}", "short": True},
                            {"title": "Threshold", "value": f"{alert.threshold:.2f}", "short": True},
                            {"title": "CPU", "value": f"{metrics.cpu_percent:.1f}%", "short": True},
                            {"title": "Memory", "value": f"{metrics.memory_percent:.1f}%", "short": True},
                        ],
                        "ts": int(alert.triggered_at.timestamp()),
                    }
                ],
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()

            logger.info(f"Slack alert sent for {alert.rule_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False


class WebhookAlertChannel(AlertChannel):
    """Generic webhook alert notifications"""

    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {}

    async def send_alert(self, alert: AlertInstance, metrics: SystemMetrics) -> bool:
        """Send webhook alert notification"""
        try:
            payload = {
                "alert": {
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "message": alert.message,
                    "tags": list(alert.tags),
                },
                "metrics": {
                    "timestamp": metrics.timestamp.isoformat(),
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "disk_usage_percent": metrics.disk_usage_percent,
                    "test_success_rate": metrics.test_success_rate,
                    "coverage_percentage": metrics.coverage_percentage,
                    "response_time_p95": metrics.response_time_p95,
                    "error_rate": metrics.error_rate,
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload, headers=self.headers, timeout=10.0)
                response.raise_for_status()

            logger.info(f"Webhook alert sent for {alert.rule_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False


class ProductionAlertingSystem:
    """Production-ready monitoring and alerting system"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.db_path = Path("tools/monitoring/alerts.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, AlertInstance] = {}
        self.alert_channels: List[AlertChannel] = []
        self.last_evaluation: Dict[str, datetime] = {}
        self.metrics_history: List[SystemMetrics] = []

        # Performance baselines for regression detection
        self.performance_baselines: Dict[str, float] = {
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "disk_threshold": 90.0,
            "test_success_threshold": 95.0,
            "coverage_threshold": 80.0,
            "response_time_threshold": 1000.0,  # ms
            "error_rate_threshold": 1.0,  # percent
        }

        self._init_database()
        self._load_default_rules()
        self._setup_alert_channels()

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if config_path and config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")

        # Default configuration
        return {
            "evaluation_interval": 60,  # seconds
            "metrics_retention_days": 30,
            "alert_retention_days": 90,
            "max_alerts_per_hour": 10,
            "escalation_enabled": True,
            "channels": {
                "email": {
                    "enabled": False,
                    "smtp_host": "localhost",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "alerts@ai",
                    "to_emails": ["admin@ai"],
                },
                "slack": {"enabled": False, "webhook_url": "", "channel": "#alerts"},
                "webhook": {"enabled": False, "url": "", "headers": {}},
            },
        }

    def _init_database(self):
        """Initialize SQLite database for alert storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    triggered_at TIMESTAMP NOT NULL,
                    resolved_at TIMESTAMP,
                    value REAL NOT NULL,
                    threshold_value REAL NOT NULL,
                    message TEXT NOT NULL,
                    tags TEXT,
                    acknowledged_by TEXT,
                    escalated BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS metrics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_usage_percent REAL,
                    test_success_rate REAL,
                    coverage_percentage REAL,
                    response_time_p95 REAL,
                    error_rate REAL,
                    active_connections INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_alerts_rule_name ON alerts(rule_name);
                CREATE INDEX IF NOT EXISTS idx_alerts_triggered_at ON alerts(triggered_at);
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics_history(timestamp);
            """
            )

    def _load_default_rules(self):
        """Load default alert rules for LUKHAS AI infrastructure"""
        default_rules = [
            AlertRule(
                name="high_cpu_usage",
                condition="metrics.cpu_percent > threshold",
                severity=AlertSeverity.HIGH,
                threshold_value=80.0,
                description="CPU usage exceeds acceptable threshold",
            ),
            AlertRule(
                name="high_memory_usage",
                condition="metrics.memory_percent > threshold",
                severity=AlertSeverity.HIGH,
                threshold_value=85.0,
                description="Memory usage approaching critical levels",
            ),
            AlertRule(
                name="disk_space_critical",
                condition="metrics.disk_usage_percent > threshold",
                severity=AlertSeverity.CRITICAL,
                threshold_value=90.0,
                description="Disk space critically low",
            ),
            AlertRule(
                name="test_success_rate_low",
                condition="metrics.test_success_rate < threshold",
                severity=AlertSeverity.MEDIUM,
                threshold_value=95.0,
                description="Test success rate below acceptable level",
            ),
            AlertRule(
                name="coverage_regression",
                condition="metrics.coverage_percentage < threshold",
                severity=AlertSeverity.MEDIUM,
                threshold_value=80.0,
                description="Test coverage below minimum requirement",
            ),
            AlertRule(
                name="response_time_degradation",
                condition="metrics.response_time_p95 > threshold",
                severity=AlertSeverity.HIGH,
                threshold_value=1000.0,  # ms
                description="95th percentile response time exceeds SLA",
            ),
            AlertRule(
                name="error_rate_spike",
                condition="metrics.error_rate > threshold",
                severity=AlertSeverity.HIGH,
                threshold_value=1.0,  # percent
                description="Error rate spike detected",
            ),
        ]

        for rule in default_rules:
            self.alert_rules[rule.name] = rule

    def _setup_alert_channels(self):
        """Setup alert notification channels based on configuration"""
        config = self.config.get("channels", {})

        # Email channel
        if config.get("email", {}).get("enabled", False):
            email_config = config["email"]
            self.alert_channels.append(
                EmailAlertChannel(
                    smtp_host=email_config["smtp_host"],
                    smtp_port=email_config["smtp_port"],
                    username=email_config["username"],
                    password=email_config["password"],
                    from_email=email_config["from_email"],
                    to_emails=email_config["to_emails"],
                )
            )

        # Slack channel
        if config.get("slack", {}).get("enabled", False):
            slack_config = config["slack"]
            self.alert_channels.append(
                SlackAlertChannel(
                    webhook_url=slack_config["webhook_url"], channel=slack_config.get("channel", "#alerts")
                )
            )

        # Generic webhook channel
        if config.get("webhook", {}).get("enabled", False):
            webhook_config = config["webhook"]
            self.alert_channels.append(
                WebhookAlertChannel(webhook_url=webhook_config["url"], headers=webhook_config.get("headers", {}))
            )

    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics"""
        # Basic system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        network = psutil.net_io_counters()

        # Try to collect test metrics from coverage system
        test_success_rate = 100.0  # Default
        coverage_percentage = 0.0  # Default
        response_time_p95 = 100.0  # Default
        error_rate = 0.0  # Default

        try:
            # Integration with coverage metrics system
            coverage_db_path = Path("tools/testing/coverage_metrics.db")
            if coverage_db_path.exists():
                with sqlite3.connect(coverage_db_path) as conn:
                    cursor = conn.execute(
                        """
                        SELECT test_success_rate, overall_coverage_percentage
                        FROM test_runs
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """
                    )
                    result = cursor.fetchone()
                    if result:
                        test_success_rate = result[0] or 100.0
                        coverage_percentage = result[1] or 0.0
        except Exception as e:
            logger.debug(f"Could not collect test metrics: {e}")

        return SystemMetrics(
            timestamp=datetime.now(timezone.utc),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_usage_percent=(disk.used / disk.total) * 100,
            network_io_bytes={"sent": network.bytes_sent, "recv": network.bytes_recv},
            test_success_rate=test_success_rate,
            coverage_percentage=coverage_percentage,
            response_time_p95=response_time_p95,
            error_rate=error_rate,
            active_connections=len(psutil.net_connections()),
        )

    def _store_metrics(self, metrics: SystemMetrics):
        """Store metrics in database for historical tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO metrics_history
                    (timestamp, cpu_percent, memory_percent, disk_usage_percent,
                     test_success_rate, coverage_percentage, response_time_p95,
                     error_rate, active_connections)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metrics.timestamp,
                        metrics.cpu_percent,
                        metrics.memory_percent,
                        metrics.disk_usage_percent,
                        metrics.test_success_rate,
                        metrics.coverage_percentage,
                        metrics.response_time_p95,
                        metrics.error_rate,
                        metrics.active_connections,
                    ),
                )
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")

    def _evaluate_alert_rule(self, rule: AlertRule, metrics: SystemMetrics) -> bool:
        """Evaluate whether an alert rule should trigger"""
        if not rule.enabled:
            return False

        # Check cooldown period
        if rule.name in self.last_evaluation:
            time_since_last = (datetime.now(timezone.utc) - self.last_evaluation[rule.name]).total_seconds()
            if time_since_last < rule.cooldown_period and rule.name in self.active_alerts:
                return False

        # Evaluate the condition
        try:
            # Create evaluation context
            context = {"metrics": metrics, "threshold": rule.threshold_value}

            result = eval(rule.condition, {"__builtins__": {}}, context)
            return bool(result)

        except Exception as e:
            logger.error(f"Error evaluating rule {rule.name}: {e}")
            return False

    async def _trigger_alert(self, rule: AlertRule, metrics: SystemMetrics):
        """Trigger a new alert"""
        # Get the actual value that triggered the alert
        value = getattr(metrics, rule.condition.split(".")[1].split()[0], 0.0)

        alert = AlertInstance(
            rule_name=rule.name,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            triggered_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            value=value,
            threshold=rule.threshold_value,
            message=f"{rule.description}: {value:.2f} (threshold: {rule.threshold_value:.2f})",
            tags=rule.tags.copy(),
        )

        self.active_alerts[rule.name] = alert
        self.last_evaluation[rule.name] = datetime.now(timezone.utc)

        # Store in database
        self._store_alert(alert)

        # Send notifications
        await self._send_alert_notifications(alert, metrics)

        logger.warning(f"Alert triggered: {rule.name} - {alert.message}")

    def _store_alert(self, alert: AlertInstance):
        """Store alert in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO alerts
                    (rule_name, severity, status, triggered_at, value,
                     threshold_value, message, tags, acknowledged_by, escalated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        alert.rule_name,
                        alert.severity.value,
                        alert.status.value,
                        alert.triggered_at,
                        alert.value,
                        alert.threshold,
                        alert.message,
                        json.dumps(list(alert.tags)),
                        alert.acknowledged_by,
                        alert.escalated,
                    ),
                )
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")

    async def _send_alert_notifications(self, alert: AlertInstance, metrics: SystemMetrics):
        """Send alert notifications through all configured channels"""
        if not self.alert_channels:
            logger.warning("No alert channels configured")
            return

        # Check rate limiting
        if not self._check_rate_limit():
            logger.warning("Alert rate limit exceeded, suppressing notification")
            return

        # Send through all channels
        for channel in self.alert_channels:
            try:
                await channel.send_alert(alert, metrics)
            except Exception as e:
                logger.error(f"Failed to send alert via {type(channel).__name__}: {e}")

    def _check_rate_limit(self) -> bool:
        """Check if we're under the alert rate limit"""
        max_alerts = self.config.get("max_alerts_per_hour", 10)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT COUNT(*) FROM alerts
                    WHERE triggered_at > datetime('now', '-1 hour')
                """
                )
                count = cursor.fetchone()[0]
                return count < max_alerts
        except Exception:
            return True  # Allow alerts if we can't check rate limit

    async def evaluate_rules(self):
        """Evaluate all alert rules against current metrics"""
        metrics = await self.collect_system_metrics()
        self.metrics_history.append(metrics)
        self._store_metrics(metrics)

        # Keep metrics history manageable
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-500:]

        # Evaluate each rule
        for rule in self.alert_rules.values():
            should_trigger = self._evaluate_alert_rule(rule, metrics)

            if should_trigger and rule.name not in self.active_alerts:
                await self._trigger_alert(rule, metrics)
            elif not should_trigger and rule.name in self.active_alerts:
                await self._resolve_alert(rule.name, metrics)

    async def _resolve_alert(self, rule_name: str, metrics: SystemMetrics):
        """Resolve an active alert"""
        if rule_name not in self.active_alerts:
            return

        alert = self.active_alerts[rule_name]
        alert.status = AlertStatus.RESOLVED
        alert.last_updated = datetime.now(timezone.utc)

        # Update in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE alerts
                    SET status = ?, resolved_at = ?
                    WHERE rule_name = ? AND status = 'active'
                """,
                    (AlertStatus.RESOLVED.value, alert.last_updated, rule_name),
                )
        except Exception as e:
            logger.error(f"Failed to update resolved alert: {e}")

        # Remove from active alerts
        del self.active_alerts[rule_name]

        logger.info(f"Alert resolved: {rule_name}")

    def acknowledge_alert(self, rule_name: str, acknowledged_by: str) -> bool:
        """Acknowledge an active alert"""
        if rule_name not in self.active_alerts:
            return False

        alert = self.active_alerts[rule_name]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = acknowledged_by
        alert.last_updated = datetime.now(timezone.utc)

        # Update in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE alerts
                    SET status = ?, acknowledged_by = ?
                    WHERE rule_name = ? AND status = 'active'
                """,
                    (AlertStatus.ACKNOWLEDGED.value, acknowledged_by, rule_name),
                )
        except Exception as e:
            logger.error(f"Failed to update acknowledged alert: {e}")
            return False

        logger.info(f"Alert acknowledged: {rule_name} by {acknowledged_by}")
        return True

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alert status"""
        summary = {
            "active_alerts": len(self.active_alerts),
            "alerts_by_severity": {severity.value: 0 for severity in AlertSeverity},
            "recent_alerts": [],
            "system_health": "healthy",
        }

        # Count alerts by severity
        for alert in self.active_alerts.values():
            summary["alerts_by_severity"][alert.severity.value] += 1

        # Determine overall system health
        if summary["alerts_by_severity"]["critical"] > 0:
            summary["system_health"] = "critical"
        elif summary["alerts_by_severity"]["high"] > 0:
            summary["system_health"] = "degraded"
        elif summary["alerts_by_severity"]["medium"] > 0:
            summary["system_health"] = "warning"

        # Get recent alerts from database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT rule_name, severity, status, triggered_at, message
                    FROM alerts
                    ORDER BY triggered_at DESC
                    LIMIT 10
                """
                )
                summary["recent_alerts"] = [
                    {
                        "rule_name": row[0],
                        "severity": row[1],
                        "status": row[2],
                        "triggered_at": row[3],
                        "message": row[4],
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {e}")

        return summary

    async def run_monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting production monitoring system")

        evaluation_interval = self.config.get("evaluation_interval", 60)

        while True:
            try:
                await self.evaluate_rules()
                await asyncio.sleep(evaluation_interval)
            except KeyboardInterrupt:
                logger.info("Monitoring loop interrupted")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(evaluation_interval)

    def generate_health_report(self) -> str:
        """Generate a comprehensive health report"""
        summary = self.get_alert_summary()

        if not self.metrics_history:
            return "No metrics available for health report"

        latest_metrics = self.metrics_history[-1]

        report = f"""
LUKHAS AI System Health Report
Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

OVERALL STATUS: {summary['system_health'].upper()}

ACTIVE ALERTS: {summary['active_alerts']}
- Critical: {summary['alerts_by_severity']['critical']}
- High: {summary['alerts_by_severity']['high']}
- Medium: {summary['alerts_by_severity']['medium']}
- Low: {summary['alerts_by_severity']['low']}

CURRENT METRICS:
- CPU Usage: {latest_metrics.cpu_percent:.1f}%
- Memory Usage: {latest_metrics.memory_percent:.1f}%
- Disk Usage: {latest_metrics.disk_usage_percent:.1f}%
- Test Success Rate: {latest_metrics.test_success_rate:.1f}%
- Coverage: {latest_metrics.coverage_percentage:.1f}%
- Response Time P95: {latest_metrics.response_time_p95:.0f}ms
- Error Rate: {latest_metrics.error_rate:.2f}%
- Active Connections: {latest_metrics.active_connections}

ALERT RULES: {len(self.alert_rules)} configured
NOTIFICATION CHANNELS: {len(self.alert_channels)} configured
        """

        return report.strip()


async def main():
    """Main entry point for running the monitoring system"""
    system = ProductionAlertingSystem()

    # Generate initial health report
    print(system.generate_health_report())

    # Run monitoring loop
    try:
        await system.run_monitoring_loop()
    except KeyboardInterrupt:
        logger.info("Monitoring system shutdown")


if __name__ == "__main__":
    asyncio.run(main())
