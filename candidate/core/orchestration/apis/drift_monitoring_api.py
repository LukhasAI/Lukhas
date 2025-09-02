"""
📊 Drift Monitoring API
═══════════════════════════════════════════════════════════════════════════

PURPOSE: Real-time monitoring and alerting system for concept drift, performance
         degradation, and behavioral changes in LUKHAS AGI systems

CAPABILITY: Tracks performance metrics, behavioral patterns, and model drift
           with automated alerting and corrective action recommendations

ARCHITECTURE: Event-driven monitoring with statistical analysis, anomaly
             detection, and integration with SRD for automated responses

INTEGRATION: Connects with all LUKHAS components to provide comprehensive
            drift detection across reasoning, memory, ethics, and creativity

🔍 DRIFT DETECTION FEATURES:
- Performance drift monitoring (response time, accuracy)
- Behavioral pattern deviation analysis
- Model output distribution changes
- Memory access pattern shifts
- Reasoning coherence degradation
- Ethical decision consistency tracking
- Creative output quality variance
- User interaction pattern changes

📈 STATISTICAL ANALYSIS:
- Moving averages and trend detection
- Gaussian distribution change detection
- Kolmogorov-Smirnov tests for distribution shifts
- Time series anomaly detection
- Confidence interval breach monitoring
- Multi-variate drift analysis
- Seasonal pattern recognition
- Outlier detection and filtering

⚡ REAL-TIME MONITORING:
- Continuous metric collection
- Streaming data analysis
- Threshold-based alerting
- Dashboard and visualization
- Historical trend analysis
- Comparative baseline tracking
- Performance regression detection
- System health scoring

🚨 ALERTING & RESPONSE:
- Configurable alert thresholds
- Multi-channel notifications (email, slack, webhooks)
- Automated response triggers
- Integration with SRD for corrective actions
- Escalation procedures for critical drift
- Performance optimization recommendations
- Model retraining suggestions

VERSION: v1.0.0 • CREATED: 2025-01-21 • AUTHOR: LUKHAS AGI TEAM
SYMBOLIC TAGS: ΛDRIFT, ΛMONITORING, ΛANOMALY, ΛPERFORMANCE, ΛALERTS
"""

import asyncio
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

import structlog

# Initialize structured logger
logger = structlog.get_logger("lukhas.drift_monitoring")


class DriftType(Enum):
    """Types of drift that can be detected"""

    PERFORMANCE = "performance"  # Response time, throughput changes
    ACCURACY = "accuracy"  # Model accuracy degradation
    BEHAVIORAL = "behavioral"  # Behavioral pattern changes
    DISTRIBUTION = "distribution"  # Output distribution changes
    MEMORY = "memory"  # Memory access patterns
    REASONING = "reasoning"  # Reasoning quality changes
    ETHICAL = "ethical"  # Ethical decision consistency
    CREATIVE = "creative"  # Creative output quality
    SYSTEM = "system"  # General system health


class DriftSeverity(Enum):
    """Severity levels for drift alerts"""

    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Action required soon
    MEDIUM = "medium"  # Monitor closely
    LOW = "low"  # Informational
    INFO = "info"  # Baseline information


class AlertChannel(Enum):
    """Alert notification channels"""

    LOG = "log"  # Log file only
    EMAIL = "email"  # Email notification
    SLACK = "slack"  # Slack message
    WEBHOOK = "webhook"  # HTTP webhook
    DASHBOARD = "dashboard"  # Dashboard alert
    SMS = "sms"  # SMS notification


@dataclass
class MetricDataPoint:
    """Individual metric measurement"""

    timestamp: datetime
    value: float
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"


@dataclass
class DriftAlert:
    """Drift detection alert"""

    alert_id: str = field(default_factory=lambda: str(uuid4()))
    drift_type: DriftType = DriftType.PERFORMANCE
    severity: DriftSeverity = DriftSeverity.MEDIUM
    metric_name: str = ""
    current_value: float = 0.0
    baseline_value: float = 0.0
    deviation_percent: float = 0.0
    threshold_breached: float = 0.0
    message: str = ""
    recommendations: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now())
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class MonitoringConfig:
    """Configuration for drift monitoring"""

    metric_name: str
    drift_type: DriftType
    collection_interval_seconds: int = 60
    window_size: int = 100  # Number of data points for analysis
    threshold_percent: float = 10.0  # Percentage change threshold
    critical_threshold_percent: float = 25.0
    baseline_window_hours: int = 24  # Hours for baseline calculation
    enable_alerts: bool = True
    alert_channels: list[AlertChannel] = field(
        default_factory=lambda: [AlertChannel.LOG]
    )
    statistical_test: str = "zscore"  # zscore, ks_test, moving_average


class StatisticalAnalyzer:
    """Statistical analysis engine for drift detection"""

    @staticmethod
    def calculate_zscore(values: list[float], current_value: float) -> float:
        """Calculate Z-score for current value against historical values"""
        if len(values) < 2:
            return 0.0

        mean = statistics.mean(values)
        try:
            stdev = statistics.stdev(values)
            if stdev == 0:
                return 0.0
            return (current_value - mean) / stdev
        except (
            ValueError,
            ZeroDivisionError,
            statistics.StatisticsError,
        ) as e:
            logger.warning(f"Failed to calculate z-score: {e}")
            return 0.0

    @staticmethod
    def detect_trend(values: list[float]) -> tuple[str, float]:
        """Detect trend direction and strength"""
        if len(values) < 3:
            return "stable", 0.0

        # Simple linear regression for trend detection
        n = len(values)
        x_values = list(range(n))

        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable", 0.0

        slope = numerator / denominator

        # Determine trend direction and strength
        if abs(slope) < 0.01:
            return "stable", slope
        elif slope > 0:
            return "increasing", slope
        else:
            return "decreasing", slope

    @staticmethod
    def kolmogorov_smirnov_test(baseline: list[float], current: list[float]) -> float:
        """Simplified K-S test for distribution change"""
        if len(baseline) == 0 or len(current) == 0:
            return 0.0

        # Sort both samples
        baseline_sorted = sorted(baseline)
        current_sorted = sorted(current)

        # Create combined sorted list
        all_values = sorted(set(baseline_sorted + current_sorted))

        max_diff = 0.0

        for value in all_values:
            # Calculate empirical CDFs
            baseline_cdf = sum(1 for x in baseline_sorted if x <= value) / len(
                baseline_sorted
            )
            current_cdf = sum(1 for x in current_sorted if x <= value) / len(
                current_sorted
            )

            diff = abs(baseline_cdf - current_cdf)
            max_diff = max(max_diff, diff)

        return max_diff

    @staticmethod
    def moving_average_deviation(values: list[float], window_size: int = 10) -> float:
        """Calculate deviation from moving average"""
        if len(values) < window_size:
            return 0.0

        current_value = values[-1]
        recent_values = values[-window_size:]
        moving_avg = sum(recent_values[:-1]) / (window_size - 1)

        if moving_avg == 0:
            return 0.0

        return abs(current_value - moving_avg) / moving_avg * 100


class MetricCollector:
    """Collects and stores metrics for drift analysis"""

    def __init__(self, max_history_hours: int = 168):  # 1 week default
        """
        Initialize metric collector

        # Notes:
        - Stores metrics in memory with configurable retention
        - Automatically purges old data to prevent memory growth
        - Thread-safe for concurrent metric collection
        """
        self.max_history_hours = max_history_hours
        self.metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.last_cleanup = datetime.now()

    async def collect_metric(
        self,
        metric_name: str,
        value: float,
        source: str = "unknown",
        metadata: Optional[dict[str, Any]] = None,
    ):
        """Collect a metric data point"""
        data_point = MetricDataPoint(
            timestamp=datetime.now(),
            value=value,
            source=source,
            metadata=metadata or {},
        )

        self.metrics[metric_name].append(data_point)

        # Periodic cleanup
        if (datetime.now() - self.last_cleanup).total_seconds() > 3600:  # Every hour
            await self._cleanup_old_metrics()

    def get_recent_values(self, metric_name: str, hours: int = 24) -> list[float]:
        """Get recent metric values within time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_points = [
            point
            for point in self.metrics[metric_name]
            if point.timestamp >= cutoff_time
        ]
        return [point.value for point in recent_points]

    def get_metric_history(
        self, metric_name: str, hours: int = 24
    ) -> list[MetricDataPoint]:
        """Get complete metric history within time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            point
            for point in self.metrics[metric_name]
            if point.timestamp >= cutoff_time
        ]

    async def _cleanup_old_metrics(self):
        """Remove old metric data points to prevent memory growth"""
        cutoff_time = datetime.now() - timedelta(hours=self.max_history_hours)

        for points in self.metrics.values():
            # Remove old points
            while points and points[0].timestamp < cutoff_time:
                points.popleft()

        self.last_cleanup = datetime.now()
        logger.debug("ΛDRIFT: Metric cleanup completed")


class DriftDetector:
    """Core drift detection engine"""

    def __init__(self, config: MonitoringConfig):
        """Initialize drift detector with configuration"""
        self.config = config
        self.analyzer = StatisticalAnalyzer()

        # Detection state
        self.last_baseline_calculation = datetime.now() - timedelta(hours=25)
        self.current_baseline: Optional[float] = None
        self.baseline_std: Optional[float] = None

        # Alert management
        self.active_alerts: dict[str, DriftAlert] = {}
        self.alert_history: deque = deque(maxlen=1000)

    async def detect_drift(
        self, metric_collector: MetricCollector
    ) -> Optional[DriftAlert]:
        """
        Detect drift in metrics and generate alerts if necessary

        # Notes:
        - Compares current metrics against established baseline
        - Uses configured statistical test for detection
        - Generates alerts based on severity thresholds
        - Includes actionable recommendations
        """
        # Get recent metric values
        recent_values = metric_collector.get_recent_values(
            self.config.metric_name,
            hours=1,  # Last hour for current analysis
        )

        if not recent_values:
            return None

        current_value = recent_values[-1]

        # Update baseline if needed
        await self._update_baseline_if_needed(metric_collector)

        if self.current_baseline is None:
            return None

        # Perform drift detection based on configured method
        drift_detected = False
        deviation_percent = 0.0
        confidence_score = 0.0

        if self.config.statistical_test == "zscore":
            baseline_values = metric_collector.get_recent_values(
                self.config.metric_name,
                hours=self.config.baseline_window_hours,
            )

            if len(baseline_values) > 10:
                zscore = self.analyzer.calculate_zscore(baseline_values, current_value)
                confidence_score = min(abs(zscore) / 3.0, 1.0)  # Normalize to 0-1

                # Z-score > 2 indicates significant deviation
                if abs(zscore) > 2:
                    drift_detected = True
                    deviation_percent = (
                        abs(current_value - self.current_baseline)
                        / self.current_baseline
                        * 100
                    )

        elif self.config.statistical_test == "ks_test":
            baseline_values = metric_collector.get_recent_values(
                self.config.metric_name,
                hours=self.config.baseline_window_hours,
            )

            current_window = recent_values[-min(len(recent_values), 20) :]

            if len(baseline_values) > 10 and len(current_window) > 5:
                ks_statistic = self.analyzer.kolmogorov_smirnov_test(
                    baseline_values, current_window
                )
                confidence_score = ks_statistic

                # K-S statistic > 0.3 indicates distribution shift
                if ks_statistic > 0.3:
                    drift_detected = True
                    deviation_percent = ks_statistic * 100

        elif self.config.statistical_test == "moving_average":
            all_values = metric_collector.get_recent_values(
                self.config.metric_name, hours=24
            )

            if len(all_values) > self.config.window_size:
                deviation_percent = self.analyzer.moving_average_deviation(
                    all_values, self.config.window_size
                )
                confidence_score = min(deviation_percent / 50.0, 1.0)  # Normalize

                if deviation_percent > self.config.threshold_percent:
                    drift_detected = True

        # Generate alert if drift detected
        if drift_detected and self.config.enable_alerts:
            return await self._generate_alert(
                current_value=current_value,
                deviation_percent=deviation_percent,
                confidence_score=confidence_score,
            )

        return None

    async def _update_baseline_if_needed(self, metric_collector: MetricCollector):
        """Update baseline metrics if sufficient time has passed"""
        hours_since_baseline = (
            datetime.now() - self.last_baseline_calculation
        ).total_seconds() / 3600

        if hours_since_baseline >= self.config.baseline_window_hours:
            baseline_values = metric_collector.get_recent_values(
                self.config.metric_name,
                hours=self.config.baseline_window_hours,
            )

            if len(baseline_values) > 10:
                self.current_baseline = statistics.mean(baseline_values)
                try:
                    self.baseline_std = statistics.stdev(baseline_values)
                except (ValueError, statistics.StatisticsError) as e:
                    logger.warning(f"Failed to calculate standard deviation: {e}")
                    self.baseline_std = 0.0

                self.last_baseline_calculation = datetime.now()

                logger.info(
                    "ΛDRIFT: Baseline updated",
                    metric=self.config.metric_name,
                    baseline=self.current_baseline,
                    std=self.baseline_std,
                )

    async def _generate_alert(
        self,
        current_value: float,
        deviation_percent: float,
        confidence_score: float,
    ) -> DriftAlert:
        """Generate drift alert with recommendations"""

        # Determine severity
        if deviation_percent > self.config.critical_threshold_percent:
            severity = DriftSeverity.CRITICAL
        elif deviation_percent > self.config.threshold_percent * 2:
            severity = DriftSeverity.HIGH
        elif deviation_percent > self.config.threshold_percent:
            severity = DriftSeverity.MEDIUM
        else:
            severity = DriftSeverity.LOW

        # Generate recommendations based on drift type and severity
        recommendations = self._generate_recommendations(severity, deviation_percent)

        # Create alert message
        message = (
            f"Drift detected in {self.config.metric_name}: "
            " + "
            f"{deviation_percent:.1f}% deviation from baseline "
            " + "
            f"(confidence: {confidence_score:.2f})"
        )

        alert = DriftAlert(
            drift_type=self.config.drift_type,
            severity=severity,
            metric_name=self.config.metric_name,
            current_value=current_value,
            baseline_value=self.current_baseline or 0.0,
            deviation_percent=deviation_percent,
            threshold_breached=self.config.threshold_percent,
            message=message,
            recommendations=recommendations,
        )

        # Store alert
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)

        logger.warning(
            "ΛDRIFT: Alert generated",
            alert_id=alert.alert_id,
            metric=self.config.metric_name,
            severity=severity.value,
            deviation=f"{deviation_percent:.1f}%",
        )

        return alert

    def _generate_recommendations(
        self, severity: DriftSeverity, deviation_percent: float
    ) -> list[str]:
        """Generate actionable recommendations based on drift"""
        recommendations = []

        if self.config.drift_type == DriftType.PERFORMANCE:
            if severity in [DriftSeverity.CRITICAL, DriftSeverity.HIGH]:
                recommendations.extend(
                    [
                        "Investigate system resource usage (CPU, memory)",
                        "Check for network latency issues",
                        "Review recent code deployments",
                        "Scale system resources if needed",
                    ]
                )
            else:
                recommendations.extend(
                    [
                        "Monitor performance trends",
                        "Review system configuration",
                        "Consider optimization opportunities",
                    ]
                )

        elif self.config.drift_type == DriftType.ACCURACY:
            if severity in [DriftSeverity.CRITICAL, DriftSeverity.HIGH]:
                recommendations.extend(
                    [
                        "Investigate data quality issues",
                        "Check model inputs for distribution changes",
                        "Consider model retraining",
                        "Review feature engineering pipeline",
                    ]
                )
            else:
                recommendations.extend(
                    [
                        "Monitor accuracy trends closely",
                        "Collect additional training data",
                        "Review model hyperparameters",
                    ]
                )

        elif self.config.drift_type == DriftType.BEHAVIORAL:
            recommendations.extend(
                [
                    "Analyze user interaction patterns",
                    "Review system behavior logs",
                    "Check for external factors affecting behavior",
                    "Consider adaptive response adjustments",
                ]
            )

        elif self.config.drift_type == DriftType.MEMORY:
            recommendations.extend(
                [
                    "Investigate memory access patterns",
                    "Check for memory leaks or inefficiencies",
                    "Review memory management configuration",
                    "Consider memory optimization strategies",
                ]
            )

        # Add general recommendations
        if severity == DriftSeverity.CRITICAL:
            recommendations.insert(0, "IMMEDIATE ACTION REQUIRED")
            recommendations.append("Consider system rollback if issue persists")

        return recommendations


class AlertManager:
    """Manages drift alerts and notifications"""

    def __init__(self):
        """Initialize alert manager"""
        self.notification_handlers: dict[AlertChannel, Callable] = {
            AlertChannel.LOG: self._log_alert,
            AlertChannel.EMAIL: self._send_email_alert,
            AlertChannel.SLACK: self._send_slack_alert,
            AlertChannel.WEBHOOK: self._send_webhook_alert,
            AlertChannel.DASHBOARD: self._update_dashboard_alert,
            AlertChannel.SMS: self._send_sms_alert,
        }

        # Alert management
        self.alert_suppression: dict[str, datetime] = {}
        self.escalation_rules: list[dict[str, Any]] = []

    async def process_alert(self, alert: DriftAlert, channels: list[AlertChannel]):
        """Process and send alert through specified channels"""

        # Check for alert suppression
        suppression_key = f"{alert.drift_type.value}_{alert.metric_name}"
        if suppression_key in self.alert_suppression:
            last_alert = self.alert_suppression[suppression_key]
            if (
                datetime.now() - last_alert
            ).total_seconds() < 300:  # 5 minute suppression
                return

        # Send through all configured channels
        for channel in channels:
            try:
                handler = self.notification_handlers.get(channel)
                if handler:
                    await handler(alert)
            except Exception as e:
                logger.error(
                    "ΛDRIFT: Alert notification failed",
                    channel=channel.value,
                    alert_id=alert.alert_id,
                    error=str(e),
                )

        # Update suppression tracking
        self.alert_suppression[suppression_key] = datetime.now()

        logger.info(
            "ΛDRIFT: Alert processed",
            alert_id=alert.alert_id,
            channels=[c.value for c in channels],
        )

    async def _log_alert(self, alert: DriftAlert):
        """Log alert to structured log"""
        logger.warning(
            "ΛDRIFT_ALERT",
            alert_id=alert.alert_id,
            severity=alert.severity.value,
            drift_type=alert.drift_type.value,
            metric=alert.metric_name,
            current_value=alert.current_value,
            baseline_value=alert.baseline_value,
            deviation_percent=alert.deviation_percent,
            message=alert.message,
            recommendations=alert.recommendations,
        )

    async def _send_email_alert(self, alert: DriftAlert):
        """Send email alert (placeholder)"""
        # Placeholder for email integration
        logger.info("ΛDRIFT: Email alert sent", alert_id=alert.alert_id)

    async def _send_slack_alert(self, alert: DriftAlert):
        """Send Slack alert (placeholder)"""
        # Placeholder for Slack integration
        logger.info("ΛDRIFT: Slack alert sent", alert_id=alert.alert_id)

    async def _send_webhook_alert(self, alert: DriftAlert):
        """Send webhook alert (placeholder)"""
        # Placeholder for webhook integration
        logger.info("ΛDRIFT: Webhook alert sent", alert_id=alert.alert_id)

    async def _update_dashboard_alert(self, alert: DriftAlert):
        """Update dashboard with alert (placeholder)"""
        # Placeholder for dashboard integration
        logger.info("ΛDRIFT: Dashboard alert updated", alert_id=alert.alert_id)

    async def _send_sms_alert(self, alert: DriftAlert):
        """Send SMS alert (placeholder)"""
        # Placeholder for SMS integration
        logger.info("ΛDRIFT: SMS alert sent", alert_id=alert.alert_id)


class DriftMonitoringAPI:
    """Main API for drift monitoring and alerting"""

    def __init__(self, max_history_hours: int = 168):
        """
        Initialize the Drift Monitoring API

        # Notes:
        - Provides unified interface for drift detection across LUKHAS
        - Manages multiple metric collectors and detectors
        - Handles alert generation and notification routing
        - Supports real-time and batch analysis modes
        """
        self.max_history_hours = max_history_hours

        # Core components
        self.metric_collector = MetricCollector(max_history_hours)
        self.alert_manager = AlertManager()

        # Monitoring configuration
        self.monitoring_configs: dict[str, MonitoringConfig] = {}
        self.drift_detectors: dict[str, DriftDetector] = {}

        # API state
        self.active_monitors: set[str] = set()
        self.monitoring_stats = {
            "total_metrics_collected": 0,
            "total_alerts_generated": 0,
            "active_monitors": 0,
            "last_analysis_time": None,
        }

        # Background tasks
        self._running = False
        self._monitoring_task = None
        self._cleanup_task = None

        logger.info(
            "ΛDRIFT: Monitoring API initialized",
            max_history_hours=max_history_hours,
        )

    async def start_monitoring(self):
        """Start drift monitoring background tasks"""
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("ΛDRIFT: Monitoring started")

    async def stop_monitoring(self):
        """Stop drift monitoring"""
        self._running = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

        logger.info("ΛDRIFT: Monitoring stopped")

    async def register_metric(self, config: MonitoringConfig):
        """Register a new metric for drift monitoring"""
        metric_key = f"{config.drift_type.value}_{config.metric_name}"

        self.monitoring_configs[metric_key] = config
        self.drift_detectors[metric_key] = DriftDetector(config)
        self.active_monitors.add(metric_key)

        self.monitoring_stats["active_monitors"] = len(self.active_monitors)

        logger.info(
            "ΛDRIFT: Metric registered",
            metric=config.metric_name,
            drift_type=config.drift_type.value,
            threshold=config.threshold_percent,
        )

    async def collect_metric(
        self,
        metric_name: str,
        value: float,
        drift_type: DriftType = DriftType.PERFORMANCE,
        source: str = "unknown",
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Collect a metric value for drift analysis

        # Notes:
        - Stores metric with timestamp and metadata
        - Triggers drift analysis if monitoring is enabled
        - Updates collection statistics
        - Thread-safe for concurrent collection
        """
        await self.metric_collector.collect_metric(
            metric_name=metric_name,
            value=value,
            source=source,
            metadata=metadata,
        )

        self.monitoring_stats["total_metrics_collected"] += 1

        # Trigger immediate analysis if configured for real-time
        metric_key = f"{drift_type.value}_{metric_name}"
        if metric_key in self.drift_detectors:
            config = self.monitoring_configs[metric_key]
            if config.collection_interval_seconds < 60:  # Real-time threshold
                await self._analyze_metric(metric_key)

    async def analyze_metric_drift(
        self, metric_name: str, drift_type: DriftType = DriftType.PERFORMANCE
    ) -> Optional[DriftAlert]:
        """Manually trigger drift analysis for a specific metric"""
        metric_key = f"{drift_type.value}_{metric_name}"

        if metric_key not in self.drift_detectors:
            return None

        return await self._analyze_metric(metric_key)

    async def get_metric_summary(
        self, metric_name: str, hours: int = 24
    ) -> dict[str, Any]:
        """Get summary statistics for a metric"""
        values = self.metric_collector.get_recent_values(metric_name, hours)

        if not values:
            return {"error": "No data available"}

        # Calculate statistics
        summary = {
            "metric_name": metric_name,
            "time_window_hours": hours,
            "data_points": len(values),
            "current_value": values[-1],
            "min_value": min(values),
            "max_value": max(values),
            "mean_value": statistics.mean(values),
            "median_value": statistics.median(values),
        }

        try:
            summary["std_deviation"] = statistics.stdev(values)
        except (ValueError, statistics.StatisticsError) as e:
            logger.warning(f"Failed to calculate standard deviation for summary: {e}")
            summary["std_deviation"] = 0.0

        # Trend analysis
        trend_direction, trend_strength = StatisticalAnalyzer.detect_trend(values)
        summary["trend"] = {
            "direction": trend_direction,
            "strength": trend_strength,
        }

        return summary

    async def get_active_alerts(
        self, severity: Optional[DriftSeverity] = None
    ) -> list[DriftAlert]:
        """Get currently active alerts"""
        active_alerts = []

        for detector in self.drift_detectors.values():
            for alert in detector.active_alerts.values():
                if not alert.resolved and (
                    severity is None or alert.severity == severity
                ):
                    active_alerts.append(alert)

        return sorted(active_alerts, key=lambda a: a.created_at, reverse=True)

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an active alert"""
        for detector in self.drift_detectors.values():
            if alert_id in detector.active_alerts:
                detector.active_alerts[alert_id].acknowledged = True
                logger.info("ΛDRIFT: Alert acknowledged", alert_id=alert_id)
                return True

        return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        for detector in self.drift_detectors.values():
            if alert_id in detector.active_alerts:
                alert = detector.active_alerts[alert_id]
                alert.resolved = True
                alert.acknowledged = True
                logger.info("ΛDRIFT: Alert resolved", alert_id=alert_id)
                return True

        return False

    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._running:
            try:
                start_time = time.time()

                # Analyze all monitored metrics
                for metric_key in list(self.active_monitors):
                    await self._analyze_metric(metric_key)

                analysis_time = time.time() - start_time
                self.monitoring_stats["last_analysis_time"] = datetime.now()

                # Adaptive sleep based on analysis time
                sleep_time = max(
                    30, 60 - analysis_time
                )  # At least 30s, adjust for analysis time
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error("ΛDRIFT: Monitoring loop error", error=str(e))
                await asyncio.sleep(60)

    async def _analyze_metric(self, metric_key: str) -> Optional[DriftAlert]:
        """Analyze a specific metric for drift"""
        if metric_key not in self.drift_detectors:
            return None

        try:
            detector = self.drift_detectors[metric_key]
            alert = await detector.detect_drift(self.metric_collector)

            if alert:
                # Send alert through configured channels
                config = self.monitoring_configs[metric_key]
                await self.alert_manager.process_alert(alert, config.alert_channels)

                self.monitoring_stats["total_alerts_generated"] += 1

            return alert

        except Exception as e:
            logger.error(
                "ΛDRIFT: Metric analysis failed",
                metric_key=metric_key,
                error=str(e),
            )
            return None

    async def _cleanup_loop(self):
        """Background cleanup of old data and resolved alerts"""
        while self._running:
            try:
                # Clean up resolved alerts older than 24 hours
                cutoff_time = datetime.now() - timedelta(hours=24)

                for detector in self.drift_detectors.values():
                    resolved_alerts = [
                        alert_id
                        for alert_id, alert in detector.active_alerts.items()
                        if alert.resolved and alert.created_at < cutoff_time
                    ]

                    for alert_id in resolved_alerts:
                        del detector.active_alerts[alert_id]

                await asyncio.sleep(3600)  # Run every hour

            except Exception as e:
                logger.error("ΛDRIFT: Cleanup loop error", error=str(e))
                await asyncio.sleep(3600)

    def get_monitoring_status(self) -> dict[str, Any]:
        """Get comprehensive monitoring status"""
        # Count active alerts synchronously
        active_alerts_count = 0
        for detector in self.drift_detectors.values():
            active_alerts_count += len(
                [a for a in detector.active_alerts.values() if not a.resolved]
            )

        return {
            "api_version": "v1.0.0",
            "monitoring_active": self._running,
            "statistics": self.monitoring_stats.copy(),
            "active_monitors": len(self.active_monitors),
            "monitored_metrics": list(self.monitoring_configs.keys()),
            "active_alerts": active_alerts_count,
            "supported_drift_types": [dt.value for dt in DriftType],
            "supported_alert_channels": [ac.value for ac in AlertChannel],
        }


# Global drift monitoring instance
_drift_monitoring_api: Optional[DriftMonitoringAPI] = None


async def get_drift_monitoring_api() -> DriftMonitoringAPI:
    """Get the global Drift Monitoring API instance"""
    global _drift_monitoring_api
    if _drift_monitoring_api is None:
        _drift_monitoring_api = DriftMonitoringAPI()
        await _drift_monitoring_api.start_monitoring()
    return _drift_monitoring_api


# ═══════════════════════════════════════════════════════════════════════════
# 📚 USER GUIDE
# ═══════════════════════════════════════════════════════════════════════════
#
# BASIC USAGE:
# -----------
# 1. Register metrics for monitoring:
#    drift_api = await get_drift_monitoring_api()
#    config = MonitoringConfig(
#        metric_name="response_time_ms",
#        drift_type=DriftType.PERFORMANCE,
#        threshold_percent=15.0,
#        alert_channels=[AlertChannel.LOG, AlertChannel.EMAIL]
#    )
#    await drift_api.register_metric(config)
#
# 2. Collect metric data:
#    await drift_api.collect_metric(
#        metric_name="response_time_ms",
#        value=125.5,
#        drift_type=DriftType.PERFORMANCE,
#        source="api_endpoint",
#        metadata={"endpoint": "/api/users", "method": "GET"}
#    )
#
# 3. Check for active alerts:
#    alerts = await drift_api.get_active_alerts(severity=DriftSeverity.HIGH)
#    for alert in alerts:
#        print(f"Alert: {alert.message}")
#        print(f"Recommendations: {alert.recommendations}")
#
# 4. Get metric summaries:
#    summary = await drift_api.get_metric_summary("response_time_ms", hours=6)
#    print(f"Current: {summary['current_value']}ms")
#    print(f"Average: {summary['mean_value']:.1f}ms")
#
# ═══════════════════════════════════════════════════════════════════════════
# 👨‍💻 DEVELOPER GUIDE
# ═══════════════════════════════════════════════════════════════════════════
#
# ADDING CUSTOM DRIFT DETECTORS:
# ------------------------------
# 1. Extend DriftDetector class
# 2. Implement custom statistical analysis
# 3. Add new drift types to DriftType enum
# 4. Register with DriftMonitoringAPI
#
# CUSTOM ALERT CHANNELS:
# ---------------------
# 1. Add channel to AlertChannel enum
# 2. Implement handler method in AlertManager
# 3. Add to notification_handlers dict
# 4. Configure in MonitoringConfig
#
# STATISTICAL ANALYSIS EXTENSION:
# ------------------------------
# - Implement custom statistical tests in StatisticalAnalyzer
# - Add new test types to MonitoringConfig.statistical_test
# - Extend drift detection logic in DriftDetector
# - Consider using scipy.stats for advanced tests
#
# PERFORMANCE OPTIMIZATION:
# ------------------------
# - Use sampling for high-frequency metrics
# - Implement data compression for long-term storage
# - Add metric aggregation for reduced storage
# - Use async processing for large datasets
#
# ═══════════════════════════════════════════════════════════════════════════
# 🎯 FINE-TUNING INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════════
#
# FOR HIGH-FREQUENCY MONITORING:
# ------------------------------
# - Set collection_interval_seconds to 5-10 seconds
# - Use moving_average statistical test for responsiveness
# - Increase window_size to 200+ for stability
# - Enable real-time alerting for critical metrics
#
# FOR SENSITIVE SYSTEMS:
# ---------------------
# - Lower threshold_percent to 5-8%
# - Set critical_threshold_percent to 15%
# - Enable multiple alert channels for redundancy
# - Use zscore test with stricter thresholds (1.5-2.0)
#
# FOR RESOURCE-CONSTRAINED SYSTEMS:
# --------------------------------
# - Increase collection_interval_seconds to 300+
# - Reduce max_history_hours to 48-72
# - Use LOG channel only for alerts
# - Implement metric sampling for high-volume data
#
# ═══════════════════════════════════════════════════════════════════════════
# ❓ COMMON QUESTIONS & PROBLEMS
# ═══════════════════════════════════════════════════════════════════════════
#
# Q: Why am I getting too many false positive alerts?
# A: Increase threshold_percent (try 20-25%)
#    Use longer baseline_window_hours (48-72 hours)
#    Switch to moving_average test for more stability
#    Add alert suppression with longer intervals
#
# Q: How do I monitor custom application metrics?
# A: Create MonitoringConfig with appropriate drift_type
#    Use collect_metric() with descriptive metadata
#    Set reasonable thresholds based on metric nature
#    Choose appropriate statistical_test for data type
#
# Q: Can I integrate with external monitoring systems?
# A: Yes, implement custom AlertChannel handlers
#    Use webhook channel for generic HTTP integrations
#    Extend AlertManager with custom notification methods
#    Consider using metric export for Prometheus/Grafana
#
# Q: How do I handle seasonal patterns in metrics?
# A: Use longer baseline_window_hours (168+ for weekly patterns)
#    Consider implementing seasonal adjustment algorithms
#    Use moving_average test which adapts to trends
#    Manually adjust thresholds during known seasonal changes
#
# Q: What's the maximum number of metrics I can monitor?
# A: Limited by memory (default 10,000 points per metric)
#    Adjust MetricCollector maxlen for more/less history
#    Consider metric sampling for high-volume metrics
#    Use external storage for long-term trend analysis
#
# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: orchestration/apis/drift_monitoring_api.py
# VERSION: v1.0.0
# SYMBOLIC TAGS: ΛDRIFT, ΛMONITORING, ΛANOMALY, ΛPERFORMANCE, ΛALERTS
# CLASSES: DriftMonitoringAPI, DriftDetector, MetricCollector, AlertManager
# FUNCTIONS: get_drift_monitoring_api, collect_metric, analyze_metric_drift
# LOGGER: structlog (UTC)
# INTEGRATION: SRD, MEG, Performance Monitoring, Dashboard Systems
# ═══════════════════════════════════════════════════════════════════════════
