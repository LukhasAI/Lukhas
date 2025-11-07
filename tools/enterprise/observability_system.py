#!/usr/bin/env python3
"""
LUKHAS Enterprise Observability System
Real-time monitoring, anomaly detection, and intelligent alerting
Based on ΛBot ObservaTrix with enterprise enhancements
"""

import asyncio
import os
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional

import aiohttp
import numpy as np
import pandas as pd
import structlog
from prometheus_api_client import PrometheusConnect
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Configure structured logging
logger = structlog.get_logger()


class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MetricAnomaly:
    """Detected metric anomaly with root cause analysis"""

    metric_name: str
    timestamp: datetime
    actual_value: float
    expected_value: float
    deviation_score: float
    severity: SeverityLevel
    context: dict[str, Any]
    root_cause_analysis: Optional[str] = None
    correlated_metrics: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)


@dataclass
class AlertRule:
    """Enhanced alert rule with ML-based thresholds"""

    name: str
    metric_query: str
    threshold: float
    comparison: str  # '>', '<', '>=', '<=', '==', 'anomaly'
    duration: str  # e.g., '5m', '10m'
    severity: SeverityLevel
    enabled: bool = True
    auto_resolve: bool = True
    ml_enabled: bool = True
    notification_channels: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricBaseline:
    """Baseline for a metric"""

    metric_name: str
    hourly_patterns: dict[int, tuple[float, float]]  # hour -> (mean, std)
    weekly_patterns: dict[int, tuple[float, float]]  # day_of_week -> (mean, std)
    seasonal_adjustments: dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class AnomalyDetector:
    """Advanced statistical anomaly detection with ML"""

    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.models = {}
        self.scalers = {}
        self.baselines = {}
        self.feature_buffers = defaultdict(lambda: deque(maxlen=1000))

    def train_model(self, metric_name: str, historical_data: pd.DataFrame):
        """Train anomaly detection model with time-series features"""
        try:
            # Extract time-series features
            features = self._extract_features(historical_data)

            # Scale features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features)

            # Train Isolation Forest
            model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100,
                max_samples="auto",
                n_jobs=-1,
            )
            model.fit(scaled_features)

            # Store model and scaler
            self.models[metric_name] = model
            self.scalers[metric_name] = scaler

            # Calculate baselines
            self._calculate_baselines(metric_name, historical_data)

            logger.info(
                "anomaly_model_trained",
                metric=metric_name,
                samples=len(historical_data),
            )

        except Exception as e:
            logger.error("model_training_failed", metric=metric_name, error=str(e))

    def _extract_features(self, data: pd.DataFrame) -> np.ndarray:
        """Extract time-series features for anomaly detection"""
        features = []

        # Basic statistics
        features.append(data["value"].values.reshape(-1, 1))

        # Rolling statistics
        for window in [5, 15, 60]:  # 5min, 15min, 1hour
            rolling = data["value"].rolling(window=window, min_periods=1)
            features.append(rolling.mean().values.reshape(-1, 1))
            features.append(rolling.std().values.reshape(-1, 1))

        # Rate of change
        features.append(data["value"].diff().fillna(0).values.reshape(-1, 1))

        # Time-based features
        if "timestamp" in data.columns:
            timestamps = pd.to_datetime(data["timestamp"])
            features.append(timestamps.dt.hour.values.reshape(-1, 1))
            features.append(timestamps.dt.dayofweek.values.reshape(-1, 1))

        return np.hstack(features)

    def _calculate_baselines(self, metric_name: str, data: pd.DataFrame):
        """Calculate hourly and weekly baselines"""
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        data["hour"] = data["timestamp"].dt.hour
        data["dayofweek"] = data["timestamp"].dt.dayofweek

        # Hourly patterns
        hourly = data.groupby("hour")["value"].agg(["mean", "std"]).to_dict()

        # Weekly patterns
        weekly = data.groupby("dayofweek")["value"].agg(["mean", "std"]).to_dict()

        self.baselines[metric_name] = MetricBaseline(
            metric_name=metric_name,
            hourly_patterns={h: (hourly["mean"][h], hourly["std"][h]) for h in range(24) if h in hourly["mean"]},
            weekly_patterns={d: (weekly["mean"][d], weekly["std"][d]) for d in range(7) if d in weekly["mean"]},
        )

    def detect_anomaly(
        self,
        metric_name: str,
        value: float,
        timestamp: datetime,
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, float, Optional[str]]:
        """Detect if a value is anomalous with explanation"""
        if metric_name not in self.models:
            return False, 0.0, None

        try:
            # Add to feature buffer
            self.feature_buffers[metric_name].append({"value": value, "timestamp": timestamp})

            # Need enough data for features
            if len(self.feature_buffers[metric_name]) < 5:
                return False, 0.0, None

            # Create DataFrame from buffer
            df = pd.DataFrame(list(self.feature_buffers[metric_name]))

            # Extract features
            features = self._extract_features(df)
            latest_features = features[-1:, :]

            # Scale
            scaled_features = self.scalers[metric_name].transform(latest_features)

            # Predict
            anomaly_score = self.models[metric_name].score_samples(scaled_features)[0]
            is_anomaly = self.models[metric_name].predict(scaled_features)[0] == -1

            # Generate explanation if anomaly
            explanation = None
            if is_anomaly:
                explanation = self._generate_explanation(metric_name, value, timestamp, anomaly_score)

            return is_anomaly, abs(anomaly_score), explanation

        except Exception as e:
            logger.error("anomaly_detection_failed", metric=metric_name, error=str(e))
            return False, 0.0, None

    def _generate_explanation(self, metric_name: str, value: float, timestamp: datetime, anomaly_score: float) -> str:
        """Generate human-readable explanation for anomaly"""
        explanations = []

        # Check against baselines
        if metric_name in self.baselines:
            baseline = self.baselines[metric_name]
            hour = timestamp.hour
            dow = timestamp.weekday()

            # Check hourly pattern
            if hour in baseline.hourly_patterns:
                mean, std = baseline.hourly_patterns[hour]
                z_score = (value - mean) / (std + 1e-6)
                if abs(z_score) > 3:
                    explanations.append(f"Value deviates {abs(z_score):.1f} standard deviations from hourly average")

            # Check weekly pattern
            if dow in baseline.weekly_patterns:
                mean, std = baseline.weekly_patterns[dow]
                z_score = (value - mean) / (std + 1e-6)
                if abs(z_score) > 3:
                    explanations.append(f"Value deviates {abs(z_score):.1f} standard deviations from weekly average")

        # Check recent trend
        if len(self.feature_buffers[metric_name]) > 10:
            recent_values = [x["value"] for x in list(self.feature_buffers[metric_name])[-10:]]
            recent_mean = np.mean(recent_values)
            if value > recent_mean * 2:
                explanations.append(f"Value is {value/recent_mean:.1f}x recent average")
            elif value < recent_mean * 0.5:
                explanations.append(f"Value is {value/recent_mean:.1%} of recent average")

        if not explanations:
            explanations.append(f"Statistical anomaly detected (score: {abs(anomaly_score):.2f})")

        return " | ".join(explanations)


class ObservabilitySystem:
    """
    Enterprise observability system with:
    - Real-time metric collection
    - ML-based anomaly detection
    - Intelligent alerting
    - Root cause analysis
    - Correlation detection
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.anomaly_detector = AnomalyDetector(contamination=config.get("anomaly_contamination", 0.1))

        # Alert rules
        self.alert_rules: dict[str, AlertRule] = {}
        self.active_alerts: dict[str, MetricAnomaly] = {}

        # Metric storage
        self.metric_buffer = defaultdict(lambda: deque(maxlen=10000))

        # Prometheus connection
        self.prom_client = None
        if "prometheus_url" in config:
            self.prom_client = PrometheusConnect(url=config["prometheus_url"], disable_ssl=True)

        # Notification handlers
        self.notification_handlers: dict[str, Callable] = {}

        # Correlation detection
        self.correlation_window = timedelta(minutes=5)
        self.correlation_threshold = 0.7

    async def initialize(self):
        """Initialize the observability system"""
        logger.info("observability_system_initializing")

        # Load alert rules
        await self._load_alert_rules()

        # Train anomaly detection models
        await self._train_anomaly_models()

        # Start monitoring loops
        asyncio.create_task(self._metric_collection_loop())
        asyncio.create_task(self._anomaly_detection_loop())
        asyncio.create_task(self._alert_evaluation_loop())

        logger.info("observability_system_initialized")

    async def _load_alert_rules(self):
        """Load alert rules from configuration"""
        rules_config = self.config.get("alert_rules", [])

        for rule_config in rules_config:
            rule = AlertRule(**rule_config)
            self.alert_rules[rule.name] = rule

        # Add default LUKHAS-specific rules
        self._add_lukhas_alert_rules()

        logger.info("alert_rules_loaded", count=len(self.alert_rules))

    def _add_lukhas_alert_rules(self):
        """Add LUKHAS-specific alert rules"""
        lukhas_rules = [
            AlertRule(
                name="memory_fold_latency",
                metric_query="lukhas_memory_fold_duration_seconds",
                threshold=5.0,
                comparison=">",
                duration="5m",
                severity=SeverityLevel.WARNING,
                ml_enabled=True,
                metadata={"component": "memory"},
            ),
            AlertRule(
                name="consciousness_drift",
                metric_query="lukhas_consciousness_drift_score",
                threshold=0.7,
                comparison=">",
                duration="10m",
                severity=SeverityLevel.CRITICAL,
                ml_enabled=True,
                metadata={"component": "consciousness"},
            ),
            AlertRule(
                name="tier_access_violations",
                metric_query="lukhas_tier_access_denied_total",
                threshold=10,
                comparison=">",
                duration="5m",
                severity=SeverityLevel.WARNING,
                metadata={"component": "security"},
            ),
        ]

        for rule in lukhas_rules:
            self.alert_rules[rule.name] = rule

    async def _train_anomaly_models(self):
        """Train anomaly detection models on historical data"""
        if not self.prom_client:
            logger.warning("prometheus_not_configured")
            return

        for rule_name, rule in self.alert_rules.items():
            if not rule.ml_enabled:
                continue

            try:
                # Fetch historical data (last 7 days)
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(days=7)

                data = self.prom_client.custom_query_range(
                    query=rule.metric_query,
                    start_time=start_time,
                    end_time=end_time,
                    step="5m",
                )

                if data:
                    # Convert to DataFrame
                    df = self._prometheus_to_dataframe(data)

                    # Train model
                    self.anomaly_detector.train_model(rule.metric_query, df)

            except Exception as e:
                logger.error("model_training_failed", rule=rule_name, error=str(e))

    def _prometheus_to_dataframe(self, prom_data: list[dict]) -> pd.DataFrame:
        """Convert Prometheus data to DataFrame"""
        records = []

        for series in prom_data:
            metric_name = series["metric"].get("__name__", "unknown")

            for timestamp, value in series["values"]:
                records.append(
                    {
                        "timestamp": datetime.fromtimestamp(timestamp, tz=timezone.utc),
                        "value": float(value),
                        "metric": metric_name,
                    }
                )

        return pd.DataFrame(records)

    async def _metric_collection_loop(self):
        """Continuously collect metrics"""
        while True:
            try:
                await self._collect_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                logger.error("metric_collection_error", error=str(e))
                await asyncio.sleep(60)

    async def _collect_metrics(self):
        """Collect current metrics from Prometheus"""
        if not self.prom_client:
            return

        for rule_name, rule in self.alert_rules.items():
            try:
                # Query current value
                result = self.prom_client.custom_query(rule.metric_query)

                if result:
                    for series in result:
                        value = float(series["value"][1])
                        timestamp = datetime.fromtimestamp(series["value"][0], tz=timezone.utc)

                        # Store in buffer
                        self.metric_buffer[rule.metric_query].append(
                            {
                                "timestamp": timestamp,
                                "value": value,
                                "labels": series["metric"],
                            }
                        )

            except Exception as e:
                logger.error("metric_query_failed", rule=rule_name, error=str(e))

    async def _anomaly_detection_loop(self):
        """Continuously check for anomalies"""
        while True:
            try:
                await self._detect_anomalies()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error("anomaly_detection_error", error=str(e))
                await asyncio.sleep(120)

    async def _detect_anomalies(self):
        """Detect anomalies in current metrics"""
        anomalies = []

        for metric_name, buffer in self.metric_buffer.items():
            if not buffer:
                continue

            # Get latest value
            latest = buffer[-1]

            # Check for anomaly
            is_anomaly, score, explanation = self.anomaly_detector.detect_anomaly(
                metric_name,
                latest["value"],
                latest["timestamp"],
                latest.get("labels", {}),
            )

            if is_anomaly:
                # Determine severity based on score
                if score > 0.9:
                    severity = SeverityLevel.CRITICAL
                elif score > 0.7:
                    severity = SeverityLevel.WARNING
                else:
                    severity = SeverityLevel.INFO

                # Calculate expected value from baseline
                expected_value = 0.0
                if metric_name in self.anomaly_detector.baselines:
                    baseline = self.anomaly_detector.baselines[metric_name]
                    hour = latest["timestamp"].hour
                    dow = latest["timestamp"].weekday()

                    # Use hourly pattern if available, otherwise weekly pattern
                    if hour in baseline.hourly_patterns:
                        expected_value = baseline.hourly_patterns[hour][0]  # mean value
                    elif dow in baseline.weekly_patterns:
                        expected_value = baseline.weekly_patterns[dow][0]  # mean value

                anomaly = MetricAnomaly(
                    metric_name=metric_name,
                    timestamp=latest["timestamp"],
                    actual_value=latest["value"],
                    expected_value=expected_value,
                    deviation_score=score,
                    severity=severity,
                    context=latest.get("labels", {}),
                    root_cause_analysis=explanation,
                )

                # Detect correlations
                anomaly.correlated_metrics = await self._find_correlated_anomalies(anomaly)

                # Suggest actions
                anomaly.suggested_actions = self._suggest_actions(anomaly)

                anomalies.append(anomaly)

        # Process detected anomalies
        for anomaly in anomalies:
            await self._process_anomaly(anomaly)

    async def _find_correlated_anomalies(self, anomaly: MetricAnomaly) -> list[str]:
        """Find metrics that are anomalous at the same time"""
        correlated = []

        anomaly_time = anomaly.timestamp
        time_window_start = anomaly_time - self.correlation_window
        time_window_end = anomaly_time + self.correlation_window

        for metric_name, buffer in self.metric_buffer.items():
            if metric_name == anomaly.metric_name:
                continue

            # Check for anomalies in time window
            for entry in buffer:
                if time_window_start <= entry["timestamp"] <= time_window_end:
                    is_anomaly, score, _ = self.anomaly_detector.detect_anomaly(
                        metric_name, entry["value"], entry["timestamp"]
                    )

                    if is_anomaly and score > self.correlation_threshold:
                        correlated.append(metric_name)
                        break

        return correlated

    def _suggest_actions(self, anomaly: MetricAnomaly) -> list[str]:
        """Suggest actions based on anomaly type"""
        actions = []

        # LUKHAS-specific suggestions
        if "memory_fold" in anomaly.metric_name:
            actions.append("Check memory system load and available resources")
            actions.append("Review recent memory fold operations for errors")
            if anomaly.deviation_score > 0.8:
                actions.append("Consider scaling memory fold workers")

        elif "consciousness_drift" in anomaly.metric_name:
            actions.append("Review recent consciousness state changes")
            actions.append("Check for ethical boundary violations")
            actions.append("Consider manual consciousness calibration")

        elif "tier_access" in anomaly.metric_name:
            actions.append("Review access logs for unauthorized attempts")
            actions.append("Check tier configuration for misconfigurations")

        # Generic suggestions based on patterns
        if anomaly.actual_value > 0 and len(anomaly.correlated_metrics) > 3:
            actions.append("Multiple correlated anomalies detected - check for system-wide issues")

        if anomaly.severity == SeverityLevel.CRITICAL:
            actions.append("IMMEDIATE ACTION REQUIRED - Engage incident response team")

        return actions

    async def _process_anomaly(self, anomaly: MetricAnomaly):
        """Process detected anomaly"""
        # Log anomaly
        logger.warning(
            "anomaly_detected",
            metric=anomaly.metric_name,
            severity=anomaly.severity.value,
            score=anomaly.deviation_score,
            value=anomaly.actual_value,
            explanation=anomaly.root_cause_analysis,
        )

        # Check if we should create an alert
        rule = self._find_matching_rule(anomaly.metric_name)
        if rule and rule.enabled:
            alert_key = f"{anomaly.metric_name}_{anomaly.severity.value}"

            # Check if alert already active
            if alert_key not in self.active_alerts:
                self.active_alerts[alert_key] = anomaly
                await self._send_notifications(anomaly, rule)

    def _find_matching_rule(self, metric_name: str) -> Optional[AlertRule]:
        """Find alert rule matching the metric"""
        for rule in self.alert_rules.values():
            if rule.metric_query == metric_name:
                return rule
        return None

    async def _alert_evaluation_loop(self):
        """Evaluate alert rules continuously"""
        while True:
            try:
                await self._evaluate_alert_rules()
                await asyncio.sleep(60)  # Evaluate every minute
            except Exception as e:
                logger.error("alert_evaluation_error", error=str(e))
                await asyncio.sleep(120)

    async def _evaluate_alert_rules(self):
        """Evaluate all alert rules"""
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue

            try:
                # Get metric values for duration
                values = self._get_metric_values_for_duration(rule.metric_query, rule.duration)

                if not values:
                    continue

                # Evaluate rule
                triggered = self._evaluate_rule(rule, values)

                if triggered:
                    await self._trigger_alert(rule, values)
                elif rule.auto_resolve:
                    await self._resolve_alert(rule)

            except Exception as e:
                logger.error("rule_evaluation_failed", rule=rule_name, error=str(e))

    def _get_metric_values_for_duration(self, metric_query: str, duration: str) -> list[float]:
        """Get metric values for specified duration"""
        # Parse duration (e.g., "5m" -> 5 minutes)
        if duration.endswith("m"):
            minutes = int(duration[:-1])
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        else:
            return []

        values = []
        if metric_query in self.metric_buffer:
            for entry in self.metric_buffer[metric_query]:
                if entry["timestamp"] >= cutoff:
                    values.append(entry["value"])

        return values

    def _evaluate_rule(self, rule: AlertRule, values: list[float]) -> bool:
        """Evaluate if alert rule is triggered"""
        if not values:
            return False

        if rule.comparison == "anomaly":
            # Use ML-based detection
            latest_value = values[-1]
            is_anomaly, _score, _ = self.anomaly_detector.detect_anomaly(
                rule.metric_query, latest_value, datetime.now(timezone.utc)
            )
            return is_anomaly
        else:
            # Traditional threshold-based
            avg_value = np.mean(values)

            if rule.comparison == ">":
                return avg_value > rule.threshold
            elif rule.comparison == "<":
                return avg_value < rule.threshold
            elif rule.comparison == ">=":
                return avg_value >= rule.threshold
            elif rule.comparison == "<=":
                return avg_value <= rule.threshold
            elif rule.comparison == "==":
                return avg_value == rule.threshold

        return False

    async def _trigger_alert(self, rule: AlertRule, values: list[float]):
        """Trigger an alert"""
        alert_key = f"{rule.name}_alert"

        if alert_key not in self.active_alerts:
            anomaly = MetricAnomaly(
                metric_name=rule.metric_query,
                timestamp=datetime.now(timezone.utc),
                actual_value=values[-1] if values else 0,
                expected_value=rule.threshold,
                deviation_score=(abs(values[-1] - rule.threshold) / rule.threshold if values else 0),
                severity=rule.severity,
                context={"rule": rule.name},
            )

            self.active_alerts[alert_key] = anomaly
            await self._send_notifications(anomaly, rule)

    async def _resolve_alert(self, rule: AlertRule):
        """Resolve an alert if conditions no longer met"""
        alert_key = f"{rule.name}_alert"

        if alert_key in self.active_alerts:
            del self.active_alerts[alert_key]
            logger.info("alert_resolved", rule=rule.name)

    async def _send_notifications(self, anomaly: MetricAnomaly, rule: AlertRule):
        """Send notifications for anomaly"""
        for channel in rule.notification_channels:
            if channel in self.notification_handlers:
                try:
                    await self.notification_handlers[channel](anomaly, rule)
                except Exception as e:
                    logger.error("notification_failed", channel=channel, error=str(e))

    def register_notification_handler(self, channel: str, handler: Callable):
        """Register a notification handler"""
        self.notification_handlers[channel] = handler

    async def get_active_alerts(self) -> list[MetricAnomaly]:
        """Get all active alerts"""
        return list(self.active_alerts.values())

    async def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of current metrics"""
        summary = {
            "total_metrics": len(self.metric_buffer),
            "active_alerts": len(self.active_alerts),
            "alert_rules": len(self.alert_rules),
            "metrics": {},
        }

        for metric_name, buffer in self.metric_buffer.items():
            if buffer:
                recent_values = [e["value"] for e in list(buffer)[-100:]]
                summary["metrics"][metric_name] = {
                    "current": buffer[-1]["value"],
                    "avg_1h": np.mean(recent_values),
                    "min_1h": np.min(recent_values),
                    "max_1h": np.max(recent_values),
                    "samples": len(buffer),
                }

        return summary


# Notification handlers


async def slack_notification_handler(anomaly: MetricAnomaly, rule: AlertRule):
    """Send notification to Slack"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return

    message = {
        "text": f"🚨 Alert: {rule.name}",
        "attachments": [
            {
                "color": ("danger" if anomaly.severity == SeverityLevel.CRITICAL else "warning"),
                "fields": [
                    {"title": "Metric", "value": anomaly.metric_name, "short": True},
                    {
                        "title": "Severity",
                        "value": anomaly.severity.value,
                        "short": True,
                    },
                    {
                        "title": "Value",
                        "value": f"{anomaly.actual_value:.2f}",
                        "short": True,
                    },
                    {
                        "title": "Score",
                        "value": f"{anomaly.deviation_score:.2f}",
                        "short": True,
                    },
                    {
                        "title": "Analysis",
                        "value": anomaly.root_cause_analysis or "N/A",
                        "short": False,
                    },
                ],
                "footer": "LUKHAS Observability",
                "ts": int(anomaly.timestamp.timestamp()),
            }
        ],
    }

    if anomaly.suggested_actions:
        message["attachments"][0]["fields"].append(
            {
                "title": "Suggested Actions",
                "value": "\n".join(f"• {action}" for action in anomaly.suggested_actions),
                "short": False,
            }
        )

    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json=message)


async def main():
    """Example usage"""
    config = {
        "prometheus_url": "http://localhost:9090",
        "anomaly_contamination": 0.1,
        "alert_rules": [
            {
                "name": "high_cpu",
                "metric_query": "node_cpu_usage",
                "threshold": 80,
                "comparison": ">",
                "duration": "5m",
                "severity": "warning",
                "notification_channels": ["slack"],
            }
        ],
    }

    # Initialize observability system
    obs_system = ObservabilitySystem(config)

    # Register notification handlers
    obs_system.register_notification_handler("slack", slack_notification_handler)

    # Initialize
    await obs_system.initialize()

    # Let it run for a bit
    await asyncio.sleep(300)

    # Get summary
    summary = await obs_system.get_metrics_summary()
    print("\n📊 Metrics Summary:")
    print(f"   Total Metrics: {summary['total_metrics']}")
    print(f"   Active Alerts: {summary['active_alerts']}")

    # Get active alerts
    alerts = await obs_system.get_active_alerts()
    if alerts:
        print("\n🚨 Active Alerts:")
        for alert in alerts:
            print(f"   - {alert.metric_name}: {alert.severity.value}")
            print(f"     Value: {alert.actual_value:.2f}")
            print(f"     Analysis: {alert.root_cause_analysis}")


if __name__ == "__main__":
    asyncio.run(main())
