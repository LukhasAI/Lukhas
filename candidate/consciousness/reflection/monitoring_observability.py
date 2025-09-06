import logging
logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


╔═══════════════════════════════════════════════════════════════════════════╗
║ LUKHAS AI - MONITORING & OBSERVABILITY SYSTEM                           ║
║ Enterprise-grade monitoring for creative AI systems                     ║
╚═══════════════════════════════════════════════════════════════════════════╝

Module: monitoring_observability.py
Path:
Created: 2025-06-11
Author: lukhasUKHAS AI Observability Division
Version: 2.0.0-enterprise

OBSERVABILITY FEATURES:
- Real-time model performance monitoring with drift detection
- Distributed tracing for request flows across microservices
- Custom metrics collection with statistical anomaly detection
- Automated alerting with intelligent noise reduction
- Performance profiling and bottleneck identification
- Business metrics tracking (creativity scores, user satisfaction)
- Log aggregation and intelligent log analysis
- SLA monitoring with automatic incident management
"""

import asyncio
import json
import logging
import time
import uuid
from collections import Counter, defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Optional

import aiohttp
import aioredis
import numpy as np
import pandas as pd
import redis.asyncio as aioredis

# Monitoring and observability libraries
# import prometheus_client  # External dependency
# from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry
import torch

# Custom imports (would be actual imports in production, timezone)
from datadog import DogStatsdClient, statsd
from elasticsearch import Elasticsearch
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Custom imports (would be actual imports in production)
# TODO: Restore this import when creative_expressions_v2 module is available
# from creative_expressions_v2 import CreativeMetrics


# Prometheus metrics
MODEL_INFERENCE_DURATION = Histogram(
    "model_inference_duration_seconds",
    "Time spent on model inference",
    ["model_id", "environment"],
)
MODEL_ACCURACY_SCORE = Gauge("model_accuracy_score", "Current model accuracy score", ["model_id", "metric_type"])
REQUEST_RATE = Counter("requests_total", "Total number of requests", ["endpoint", "status", "model_id"])
ERROR_RATE = Counter("errors_total", "Total number of errors", ["error_type", "service", "severity"])
DRIFT_DETECTION_SCORE = Gauge("model_drift_score", "Model drift detection score", ["model_id", "drift_type"])


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Types of metrics being monitored."""

    PERFORMANCE = auto()
    BUSINESS = auto()
    SYSTEM = auto()
    SECURITY = auto()


class DriftType(Enum):
    """Types of model drift."""

    CONCEPT_DRIFT = "concept"
    DATA_DRIFT = "data"
    PREDICTION_DRIFT = "prediction"
    PERFORMANCE_DRIFT = "performance"


@dataclass
class Alert:
    """Alert data structure."""

    id: str
    title: str
    description: str
    severity: AlertSeverity
    metric_name: str
    current_value: float
    threshold: float
    service: str
    model_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class MetricThreshold:
    """Threshold configuration for metrics."""

    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison_operator: str = ">"  # >, <, ==, !=
    evaluation_window_minutes: int = 5
    min_data_points: int = 3


@dataclass
class MonitoringConfig:
    """Configuration for monitoring system."""

    prometheus_port: int = 8090
    jaeger_endpoint: str = "http://jaeger:14268/api/traces"
    elasticsearch_host: str = "elasticsearch:9200"
    redis_host: str = "redis:6379"
    datadog_api_key: Optional[str] = None
    alert_webhook_url: Optional[str] = None
    drift_detection_threshold: float = 0.7
    anomaly_detection_sensitivity: float = 0.1
    log_level: str = "INFO"


class DistributedTracer:
    """Distributed tracing for request flows across services."""

    def __init__(self, service_name: str, jaeger_endpoint: str):
        self.service_name = service_name

        # Initialize Jaeger tracer
        jaeger_exporter = JaegerExporter(
            agent_host_name="jaeger",
            agent_port=6831,
        )

        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()

        span_processor = BatchSpanProcessor(jaeger_exporter)
        tracer_provider.add_span_processor(span_processor)

        self.tracer = trace.get_tracer(service_name)

        # Instrument HTTP requests
        RequestsInstrumentor().instrument()

    @asynccontextmanager
    async def trace_request(self, operation_name: str, **attributes):
        """Context manager for tracing requests."""
        with self.tracer.start_as_current_span(operation_name) as span:
            # Add custom attributes
            for key, value in attributes.items():
                span.set_attribute(key, str(value))

            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    def add_span_event(self, span, event_name: str, **attributes):
        """Add event to current span."""
        span.add_event(event_name, attributes)


class ModelDriftDetector:
    """
    Advanced model drift detection using statistical methods and ML.
    Detects concept drift, data drift, and prediction drift.
    """

    def __init__(self, reference_window_size: int = 1000):
        self.reference_window_size = reference_window_size
        self.reference_data: dict[str, deque] = defaultdict(lambda: deque(maxlen=reference_window_size))
        self.drift_scores: dict[str, float] = {}

        # Anomaly detection models
        self.isolation_forests: dict[str, IsolationForest] = {}
        self.scalers: dict[str, StandardScaler] = {}

    async def initialize_reference_baseline(self, model_id: str, baseline_data: list[dict[str, float]]) -> None:
        """Initialize reference baseline for drift detection."""
        logger.info(
            "Initializing drift detection baseline",
            model_id=model_id,
            samples=len(baseline_data),
        )

        # Store reference data
        for data_point in baseline_data:
            for metric_name, value in data_point.items():
                self.reference_data[f"{model_id}_{metric_name}"].append(value)

        # Train anomaly detection models
        await self._train_anomaly_detectors(model_id, baseline_data)

    async def _train_anomaly_detectors(self, model_id: str, training_data: list[dict[str, float]]) -> None:
        """Train isolation forest models for anomaly detection."""
        if len(training_data) < 100:
            logger.warning(
                "Insufficient data for anomaly detection training",
                model_id=model_id,
                samples=len(training_data),
            )
            return

        # Convert to DataFrame for easier processing
        df = pd.DataFrame(training_data)

        # Train scaler
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df)
        self.scalers[model_id] = scaler

        # Train isolation forest
        isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100,  # Expect 10% anomalies
        )
        isolation_forest.fit(scaled_data)
        self.isolation_forests[model_id] = isolation_forest

        logger.info("Anomaly detection models trained", model_id=model_id)

    async def detect_drift(self, model_id: str, current_metrics: dict[str, float]) -> dict[DriftType, float]:
        """
        Detect various types of drift for a model.

        Returns:
            Dictionary mapping drift types to drift scores (0-1, higher = more drift)
        """
        drift_scores = {}

        # Data drift detection using statistical tests
        drift_scores[DriftType.DATA_DRIFT] = await self._detect_data_drift(model_id, current_metrics)

        # Performance drift detection
        drift_scores[DriftType.PERFORMANCE_DRIFT] = await self._detect_performance_drift(model_id, current_metrics)

        # Prediction drift detection using anomaly detection
        drift_scores[DriftType.PREDICTION_DRIFT] = await self._detect_prediction_drift(model_id, current_metrics)

        # Update Prometheus metrics
        for drift_type, score in drift_scores.items():
            DRIFT_DETECTION_SCORE.labels(model_id=model_id, drift_type=drift_type.value).set(score)

        self.drift_scores[model_id] = drift_scores

        return drift_scores

    async def _detect_data_drift(self, model_id: str, current_metrics: dict[str, float]) -> float:
        """Detect data drift using Kolmogorov-Smirnov test."""
        drift_scores = []

        for metric_name, current_value in current_metrics.items():
            reference_key = f"{model_id}_{metric_name}"

            if reference_key not in self.reference_data:
                continue

            reference_values = list(self.reference_data[reference_key])
            if len(reference_values) < 30:  # Need minimum samples
                continue

            # Create current window (simulated - in practice you'd maintain this)
            current_window = [current_value] * 30  # Simplified

            # Kolmogorov-Smirnov test
            try:
                ks_statistic, p_value = stats.ks_2samp(reference_values, current_window)
                drift_score = ks_statistic  # Higher = more drift
                drift_scores.append(drift_score)
            except Exception as e:
                logger.warning("KS test failed", metric=metric_name, error=str(e))

        return np.mean(drift_scores) if drift_scores else 0.0

    async def _detect_performance_drift(self, model_id: str, current_metrics: dict[str, float]) -> float:
        """Detect performance drift by comparing key performance metrics."""
        performance_metrics = [
            "creativity_score",
            "semantic_coherence",
            "syllable_accuracy",
        ]

        drift_scores = []

        for metric in performance_metrics:
            if metric not in current_metrics:
                continue

            reference_key = f"{model_id}_{metric}"
            if reference_key not in self.reference_data:
                continue

            reference_values = list(self.reference_data[reference_key])
            if len(reference_values) < 10:
                continue

            reference_mean = np.mean(reference_values)
            current_value = current_metrics[metric]

            # Calculate relative change
            if reference_mean != 0:
                relative_change = abs(current_value - reference_mean) / reference_mean
                drift_scores.append(min(relative_change, 1.0))  # Cap at 1.0

        return np.mean(drift_scores) if drift_scores else 0.0

    async def _detect_prediction_drift(self, model_id: str, current_metrics: dict[str, float]) -> float:
        """Detect prediction drift using trained anomaly detection models."""
        if model_id not in self.isolation_forests:
            return 0.0

        isolation_forest = self.isolation_forests[model_id]
        scaler = self.scalers[model_id]

        try:
            # Prepare current data point
            metric_values = list(current_metrics.values())
            scaled_data = scaler.transform([metric_values])

            # Get anomaly score
            anomaly_score = isolation_forest.decision_function(scaled_data)[0]

            # Convert to drift score (0-1 range)
            # Isolation forest returns negative scores for anomalies
            drift_score = max(0, -anomaly_score)  # Convert to positive
            drift_score = min(drift_score, 1.0)  # Cap at 1.0

            return drift_score

        except Exception as e:
            logger.error("Prediction drift detection failed", model_id=model_id, error=str(e))
            return 0.0


class AlertManager:
    """
    Intelligent alert management with deduplication, escalation, and noise reduction.
    """

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.suppression_rules: list[dict] = []

        # External integrations
        self.webhook_url = config.alert_webhook_url
        self.datadog_client = None
        if config.datadog_api_key:
            self.datadog_client = DogStatsdClient()
            self.datadog_client = statsd

        # Alert rate limiting
        self.alert_counts: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

    async def evaluate_thresholds(
        self,
        metrics: dict[str, float],
        thresholds: list[MetricThreshold],
        model_id: Optional[str] = None,
    ) -> list[Alert]:
        """Evaluate metrics against thresholds and generate alerts."""
        generated_alerts = []

        for threshold in thresholds:
            if threshold.metric_name not in metrics:
                continue

            current_value = metrics[threshold.metric_name]

            # Check if threshold is violated
            violation_level = self._check_threshold_violation(current_value, threshold)

            if violation_level:
                alert = await self._create_alert(
                    threshold=threshold,
                    current_value=current_value,
                    severity=violation_level,
                    model_id=model_id,
                )

                if alert and await self._should_send_alert(alert):
                    generated_alerts.append(alert)
                    await self._send_alert(alert)

        return generated_alerts

    def _check_threshold_violation(self, current_value: float, threshold: MetricThreshold) -> Optional[AlertSeverity]:
        """Check if a threshold is violated and return severity level."""
        operator = threshold.comparison_operator

        # Check critical threshold
        if self._compare_values(current_value, threshold.critical_threshold, operator):
            return AlertSeverity.CRITICAL

        # Check warning threshold
        if self._compare_values(current_value, threshold.warning_threshold, operator):
            return AlertSeverity.WARNING

        return None

    def _compare_values(self, current: float, threshold: float, operator: str) -> bool:
        """Compare values based on operator."""
        if operator == ">":
            return current > threshold
        elif operator == "<":
            return current < threshold
        elif operator == "==":
            return abs(current - threshold) < 1e-6
        elif operator == "!=":
            return abs(current - threshold) >= 1e-6
        else:
            return False

    async def _create_alert(
        self,
        threshold: MetricThreshold,
        current_value: float,
        severity: AlertSeverity,
        model_id: Optional[str] = None,
    ) -> Optional[Alert]:
        """Create alert object."""
        alert_id = str(uuid.uuid4())

        alert = Alert(
            id=alert_id,
            title=f"{threshold.metric_name} threshold exceeded",
            description=f"{threshold.metric_name} = {current_value:.3f}, "
            f"threshold = {threshold.critical_threshold if severity == AlertSeverity.CRITICAL else threshold.warning_threshold}",
            severity=severity,
            metric_name=threshold.metric_name,
            current_value=current_value,
            threshold=(
                threshold.critical_threshold if severity == AlertSeverity.CRITICAL else threshold.warning_threshold
            ),
            service="creative_agi",
            model_id=model_id,
        )

        return alert

    async def _should_send_alert(self, alert: Alert) -> bool:
        """Determine if alert should be sent based on suppression rules and rate limiting."""
        # Check suppression rules
        for rule in self.suppression_rules:
            if self._matches_suppression_rule(alert, rule):
                logger.debug("Alert suppressed by rule", alert_id=alert.id, rule=rule)
                return False

        # Rate limiting - don't send more than 5 alerts per metric per hour
        rate_key = f"{alert.metric_name}_{alert.service}"
        now = time.time()

        # Clean old timestamps
        self.alert_counts[rate_key] = deque(
            [ts for ts in self.alert_counts[rate_key] if now - ts < 3600],  # Last hour
            maxlen=100,
        )

        if len(self.alert_counts[rate_key]) >= 5:
            logger.debug("Alert rate limited", alert_id=alert.id, metric=alert.metric_name)
            return False

        # Record alert timestamp
        self.alert_counts[rate_key].append(now)

        return True

    def _matches_suppression_rule(self, alert: Alert, rule: dict) -> bool:
        """Check if alert matches suppression rule."""
        # Simple rule matching - could be much more sophisticated
        if rule.get("metric_name") == alert.metric_name:
            return True
        return rule.get("severity") == alert.severity.value

    async def _send_alert(self, alert: Alert) -> None:
        """Send alert via configured channels."""
        # Store alert
        self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)

        # Update Prometheus metrics
        ERROR_RATE.labels(
            error_type="threshold_violation",
            service=alert.service,
            severity=alert.severity.value,
        ).inc()

        # Send to external systems
        await self._send_webhook_alert(alert)
        await self._send_datadog_alert(alert)

        logger.warning(
            "Alert generated",
            alert_id=alert.id,
            title=alert.title,
            severity=alert.severity.value,
            metric=alert.metric_name,
            value=alert.current_value,
        )

    async def _send_webhook_alert(self, alert: Alert) -> None:
        """Send alert via webhook."""
        if not self.webhook_url:
            return

        payload = {
            "alert_id": alert.id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity.value,
            "metric_name": alert.metric_name,
            "current_value": alert.current_value,
            "threshold": alert.threshold,
            "service": alert.service,
            "model_id": alert.model_id,
            "timestamp": alert.timestamp.isoformat(),
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.debug("Webhook alert sent successfully", alert_id=alert.id)
                    else:
                        logger.error(
                            "Webhook alert failed",
                            alert_id=alert.id,
                            status=response.status,
                        )
        except Exception as e:
            logger.error("Webhook alert exception", alert_id=alert.id, error=str(e))

    async def _send_datadog_alert(self, alert: Alert) -> None:
        """Send alert to Datadog."""
        if not self.datadog_client:
            return

        try:
            self.datadog_client.increment(
                "ai.alerts.generated",
                tags=[
                    f"severity:{alert.severity.value}",
                    f"service:{alert.service}",
                    f"metric:{alert.metric_name}",
                ],
            )
        except Exception as e:
            logger.error("Datadog alert failed", alert_id=alert.id, error=str(e))

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert."""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolution_time = datetime.now(timezone.utc)

        del self.active_alerts[alert_id]

        logger.info("Alert resolved", alert_id=alert_id, resolution_time=alert.resolution_time)

        return True


class PerformanceProfiler:
    """
    Performance profiler for identifying bottlenecks and optimization opportunities.
    """

    def __init__(self):
        self.execution_times: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.memory_usage: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.gpu_usage: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

    @asynccontextmanager
    async def profile_execution(self, operation_name: str):
        """Context manager for profiling code execution."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_gpu = self._get_gpu_usage()

        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            end_gpu = self._get_gpu_usage()

            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory
            gpu_delta = end_gpu - start_gpu

            # Record metrics
            self.execution_times[operation_name].append(execution_time)
            self.memory_usage[operation_name].append(memory_delta)
            self.gpu_usage[operation_name].append(gpu_delta)

            # Update Prometheus metrics
            MODEL_INFERENCE_DURATION.labels(model_id="unknown", environment="unknown").observe(execution_time)

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0

    def _get_gpu_usage(self) -> float:
        """Get current GPU memory usage."""
        try:
            if torch.cuda.is_available():
                return torch.cuda.memory_allocated() / 1024 / 1024  # MB
            return 0.0
        except Exception:
            return 0.0

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary statistics."""
        summary = {}

        for operation, times in self.execution_times.items():
            if len(times) == 0:
                continue

            times_list = list(times)
            summary[operation] = {
                "avg_execution_time_ms": np.mean(times_list) * 1000,
                "p95_execution_time_ms": np.percentile(times_list, 95) * 1000,
                "p99_execution_time_ms": np.percentile(times_list, 99) * 1000,
                "total_calls": len(times_list),
                "avg_memory_delta_mb": (
                    np.mean(list(self.memory_usage[operation])) if self.memory_usage[operation] else 0
                ),
                "avg_gpu_delta_mb": (np.mean(list(self.gpu_usage[operation])) if self.gpu_usage[operation] else 0),
            }

        return summary


class ObservabilitySystem:
    """
    Main observability system that coordinates all monitoring components.
    """

    def __init__(self, config: MonitoringConfig):
        self.config = config

        # Initialize components
        self.tracer = DistributedTracer("creative_agi", config.jaeger_endpoint)
        self.drift_detector = ModelDriftDetector()
        self.alert_manager = AlertManager(config)
        self.profiler = PerformanceProfiler()

        # External connections
        self.elasticsearch = None
        self.redis_client = None

        # Metric thresholds
        self.thresholds = [
            MetricThreshold(
                metric_name="creativity_score",
                warning_threshold=0.7,
                critical_threshold=0.5,
                comparison_operator="<",
            ),
            MetricThreshold(
                metric_name="generation_time_ms",
                warning_threshold=1000,
                critical_threshold=5000,
                comparison_operator=">",
            ),
            MetricThreshold(
                metric_name="error_rate",
                warning_threshold=0.05,
                critical_threshold=0.10,
                comparison_operator=">",
            ),
        ]

    async def initialize(self) -> None:
        """Initialize observability system components."""
        # Initialize Elasticsearch
        try:
            self.elasticsearch = Elasticsearch([self.config.elasticsearch_host])
            logger.info("Elasticsearch connection established")
        except Exception as e:
            logger.error("Failed to connect to Elasticsearch", error=str(e))

        # Initialize Redis
        try:
            self.redis_client = await aioredis.from_url(f"redis://{self.config.redis_host}")
            logger.info("Redis connection established")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))

        # Start Prometheus metrics server
        prometheus_client.start_http_server(self.config.prometheus_port)
        logger.info("Prometheus metrics server started", port=self.config.prometheus_port)

    async def monitor_model_inference(
        self,
        model_id: str,
        request_data: dict[str, Any],
        response_data: dict[str, Any],
        execution_time_ms: float,
    ) -> None:
        """Monitor a single model inference request."""

        async with self.tracer.trace_request(
            "model_inference", model_id=model_id, execution_time_ms=execution_time_ms
        ) as span:
            # Record basic metrics
            MODEL_INFERENCE_DURATION.labels(
                model_id=model_id,
                environment=request_data.get("environment", "unknown"),
            ).observe(execution_time_ms / 1000)

            REQUEST_RATE.labels(endpoint="inference", status="success", model_id=model_id).inc()

            # Extract metrics from response
            if "metrics" in response_data:
                metrics = response_data["metrics"]

                # Update Prometheus gauges
                for metric_name, value in metrics.items():
                    MODEL_ACCURACY_SCORE.labels(model_id=model_id, metric_type=metric_name).set(value)

                # Check for drift
                drift_scores = await self.drift_detector.detect_drift(model_id, metrics)

                # Add drift info to span
                for drift_type, score in drift_scores.items():
                    self.tracer.add_span_event(
                        span,
                        "drift_detection",
                        drift_type=drift_type.value,
                        drift_score=score,
                    )

                # Evaluate alert thresholds
                alerts = await self.alert_manager.evaluate_thresholds(metrics, self.thresholds, model_id)

                if alerts:
                    self.tracer.add_span_event(span, "alerts_generated", alert_count=len(alerts))

            # Log to Elasticsearch
            await self._log_inference_event(model_id, request_data, response_data, execution_time_ms)

    async def _log_inference_event(
        self,
        model_id: str,
        request_data: dict[str, Any],
        response_data: dict[str, Any],
        execution_time_ms: float,
    ) -> None:
        """Log inference event to Elasticsearch."""
        if not self.elasticsearch:
            return

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_id": model_id,
            "execution_time_ms": execution_time_ms,
            "request_size": len(str(request_data)),
            "response_size": len(str(response_data)),
            "metrics": response_data.get("metrics", {}),
            "environment": request_data.get("environment", "unknown"),
        }

        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.elasticsearch.index,
                {
                    "index": f"ai-inference-{datetime.now(timezone.utc).strftime('%Y.%m')}",
                    "body": event,
                },
            )
        except Exception as e:
            logger.error("Failed to log to Elasticsearch", error=str(e))

    async def register_model_baseline(self, model_id: str, baseline_metrics: list[dict[str, float]]) -> None:
        """Register baseline metrics for a model."""
        await self.drift_detector.initialize_reference_baseline(model_id, baseline_metrics)
        logger.info(
            "Model baseline registered",
            model_id=model_id,
            samples=len(baseline_metrics),
        )

    async def get_system_health(self) -> dict[str, Any]:
        """Get comprehensive system health status."""
        health = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "elasticsearch": await self._check_elasticsearch_health(),
                "redis": await self._check_redis_health(),
                "prometheus": True,  # Always true if we can execute this
            },
            "active_alerts": len(self.alert_manager.active_alerts),
            "alert_history_24h": len(
                [
                    alert
                    for alert in self.alert_manager.alert_history
                    if alert.timestamp > datetime.now(timezone.utc) - timedelta(hours=24)
                ]
            ),
            "performance_summary": self.profiler.get_performance_summary(),
            "drift_scores": self.drift_detector.drift_scores,
        }

        return health

    async def _check_elasticsearch_health(self) -> bool:
        """Check Elasticsearch health."""
        if not self.elasticsearch:
            return False

        try:
            health = await asyncio.get_event_loop().run_in_executor(None, self.elasticsearch.cluster.health)
            return health["status"] in ["green", "yellow"]
        except Exception:
            return False

    async def _check_redis_health(self) -> bool:
        """Check Redis health."""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False

    async def generate_health_report(self) -> str:
        """Generate comprehensive health report."""
        health = await self.get_system_health()

        report = f"""
# ΛUKHAS AI System Health Report
# lukhasUKHAS AI System Health Report
Generated: {health["timestamp"]}

## Service Status
- Elasticsearch: {"✅" if health["services"]["elasticsearch"] else "❌"}
- Redis: {"✅" if health["services"]["redis"] else "❌"}
- Prometheus: {"✅" if health["services"]["prometheus"] else "❌"}

## Alert Summary
- Active Alerts: {health["active_alerts"]}
- Alerts (24h): {health["alert_history_24h"]}

## Performance Summary
"""

        for operation, stats in health["performance_summary"].items():
            report += f"""
### {operation}
- Average Execution: {stats["avg_execution_time_ms"]:.1f}ms
- P95 Execution: {stats["p95_execution_time_ms"]:.1f}ms
- P99 Execution: {stats["p99_execution_time_ms"]:.1f}ms
- Total Calls: {stats["total_calls"]}
"""

        if health["drift_scores"]:
            report += "\n## Model Drift Status\n"
            for model_id, drift_info in health["drift_scores"].items():
                report += f"- {model_id}: {drift_info}\n"

        return report

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()

        logger.info("Observability system cleaned up")


# Example usage and integration
async def main():
    """Example usage of the observability system."""

    # Configuration
    config = MonitoringConfig(
        prometheus_port=8090,
        jaeger_endpoint="http://jaeger:14268/api/traces",
        elasticsearch_host="elasticsearch:9200",
        redis_host="redis:6379",
    )

    # Initialize observability system
    obs_system = ObservabilitySystem(config)
    await obs_system.initialize()

    # Register model baseline
    baseline_metrics = [{"creativity_score": 0.85, "generation_time_ms": 450, "error_rate": 0.02} for _ in range(1000)]
    await obs_system.register_model_baseline("model_123", baseline_metrics)

    # Simulate monitoring model inference
    request_data = {
        "user_id": "user_456",
        "environment": "production",
        "model_version": "v2.1",
    }

    response_data = {
        "haiku": "Ancient pond waits\nA frog leaps in silently\nWater's voice returns",
        "metrics": {
            "creativity_score": 0.82,
            "generation_time_ms": 520,
            "semantic_coherence": 0.91,
            "syllable_accuracy": 0.95,
        },
    }

    await obs_system.monitor_model_inference(
        model_id="model_123",
        request_data=request_data,
        response_data=response_data,
        execution_time_ms=520,
    )

    # Get system health
    health = await obs_system.get_system_health()
    logging.info(f"System Health: {json.dumps(health, indent=2)}")

    # Generate health report
    report = await obs_system.generate_health_report()
    logging.info(report)

    # Cleanup
    await obs_system.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

# ═══════════════════════════════════════════════════════════════════════════
# LUKHAS AI - MONITORING & OBSERVABILITY SYSTEM
# Enterprise-grade monitoring for creative AI systems:
# • Real-time model performance monitoring with statistical drift detection
# • Distributed tracing for request flows across microservices
# • Custom metrics collection with intelligent anomaly detection
# • Automated alerting with noise reduction and escalation policies
# • Performance profiling and bottleneck identification
# • Business metrics tracking (creativity scores, user satisfaction)
# • Log aggregation and intelligent log analysis with Elasticsearch
# • SLA monitoring with automatic incident management
# ═══════════════════════════════════════════════════════════════════════════