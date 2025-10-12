"""
LUKHAS Production Monitoring & Telemetry
Enterprise-grade observability for Cognitive AI systems
"""
import asyncio
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional


class MetricType(Enum):
    """Types of metrics"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """System metric"""

    name: str
    type: MetricType
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Alert:
    """System alert"""

    id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class AGITelemetrySystem:
    """
    Production-grade telemetry for LUKHAS Cognitive AI
    Tracks performance, health, and emergent behaviors
    """

    def __init__(self):
        # Metrics storage
        self.metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.histograms: dict[str, list[float]] = defaultdict(list)

        # Alert management
        self.alerts: list[Alert] = []
        self.alert_handlers: dict[AlertSeverity, list[Callable]] = defaultdict(list)

        # System health
        self.health_checks: dict[str, Callable] = {}
        self.health_status: dict[str, bool] = {}

        # Performance tracking
        self.performance_baselines: dict[str, float] = {}
        self.anomaly_detectors: dict[str, Callable] = {}

        # Cognitive AI-specific metrics
        self.consciousness_metrics = ConsciousnessMetrics()
        self.learning_metrics = LearningMetrics()
        self.emergence_detector = EmergenceDetector()

        self._running = False

    async def initialize(self):
        """Initialize telemetry system"""
        self._running = True

        # Start monitoring tasks
        asyncio.create_task(self._metrics_aggregator())
        asyncio.create_task(self._health_monitor())
        asyncio.create_task(self._anomaly_detector())
        asyncio.create_task(self._emergence_monitor())

        # Initialize exporters
        await self._initialize_exporters()

    # Core metrics API

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[dict[str, str]] = None,
    ):
        """Record a metric value"""
        metric = Metric(
            name=name,
            type=metric_type,
            value=value,
            labels=labels or {},
            timestamp=datetime.now(timezone.utc),
        )

        self.metrics[name].append(metric)

        # Check for anomalies
        if name in self.anomaly_detectors:
            asyncio.create_task(self._check_anomaly(name, value))

    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[dict[str, str]] = None):
        """Increment a counter metric"""
        self.record_metric(name, value, MetricType.COUNTER, labels)

    def set_gauge(self, name: str, value: float, labels: Optional[dict[str, str]] = None):
        """Set a gauge metric"""
        self.record_metric(name, value, MetricType.GAUGE, labels)

    def record_histogram(self, name: str, value: float, labels: Optional[dict[str, str]] = None):
        """Record histogram observation"""
        self.histograms[name].append(value)
        self.record_metric(name, value, MetricType.HISTOGRAM, labels)

    # Health checks

    def register_health_check(self, name: str, check_func: Callable):
        """Register a health check function"""
        self.health_checks[name] = check_func

    async def check_health(self) -> dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True

        for name, check_func in self.health_checks.items():
            try:
                is_healthy = await check_func()
                results[name] = {
                    "healthy": is_healthy,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                self.health_status[name] = is_healthy

                if not is_healthy:
                    overall_healthy = False

            except Exception as e:
                results[name] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                overall_healthy = False

        results["overall"] = overall_healthy
        return results

    # Alert management

    def create_alert(
        self,
        title: str,
        description: str,
        severity: AlertSeverity,
        source: str,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """Create a new alert"""
        alert = Alert(
            id=self._generate_alert_id(),
            title=title,
            description=description,
            severity=severity,
            source=source,
            metadata=metadata or {},
        )

        self.alerts.append(alert)

        # Trigger handlers
        asyncio.create_task(self._handle_alert(alert))

        return alert.id

    def register_alert_handler(self, severity: AlertSeverity, handler: Callable):
        """Register an alert handler for specific severity"""
        self.alert_handlers[severity].append(handler)

    # Cognitive AI-specific monitoring
    async def record_consciousness_state(self, state: dict[str, Any]):
        """Record consciousness state metrics"""
        # Extract key metrics
        self.set_gauge("consciousness.coherence", state.get("coherence", 0))
        self.set_gauge("consciousness.awareness_level", state.get("awareness", 0))
        self.set_gauge("consciousness.processing_depth", state.get("depth", 0))

        # Record to specialized metrics
        await self.consciousness_metrics.record(state)

    async def record_learning_event(self, event: dict[str, Any]):
        """Record learning event"""
        self.increment_counter("learning.events_total")
        self.set_gauge("learning.rate", event.get("learning_rate", 0))

        # Record to specialized metrics
        await self.learning_metrics.record(event)

    async def check_emergence(self, behavior_data: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Check for emergent behaviors"""
        emergence = await self.emergence_detector.analyze(behavior_data)

        if emergence:
            self.create_alert(
                "Emergent Behavior Detected",
                f"New emergent pattern: {emergence['pattern']}",
                AlertSeverity.INFO,
                "emergence_detector",
                emergence,
            )

        return emergence

    # Performance profiling

    def start_trace(self, operation: str) -> "TraceContext":
        """Start performance trace"""
        return TraceContext(self, operation)

    def set_baseline(self, metric: str, value: float):
        """Set performance baseline"""
        self.performance_baselines[metric] = value

    def register_anomaly_detector(self, metric: str, detector: Callable):
        """Register anomaly detection for metric"""
        self.anomaly_detectors[metric] = detector

    # Internal monitoring tasks
    async def _metrics_aggregator(self):
        """Aggregate metrics periodically"""
        while self._running:
            await asyncio.sleep(60)  # Every minute

            # Calculate aggregates
            for metric_name, values in self.metrics.items():
                if values:
                    recent_values = [m.value for m in list(values)[-100:]]

                    self.set_gauge(
                        f"{metric_name}.avg",
                        sum(recent_values) / len(recent_values),
                    )
                    self.set_gauge(f"{metric_name}.min", min(recent_values))
                    self.set_gauge(f"{metric_name}.max", max(recent_values))

    async def _health_monitor(self):
        """Monitor system health"""
        while self._running:
            await asyncio.sleep(30)  # Every 30 seconds

            health_results = await self.check_health()

            # Record health metrics
            for check_name, result in health_results.items():
                if check_name != "overall":
                    self.set_gauge(
                        f"health.{check_name}",
                        1.0 if result["healthy"] else 0.0,
                    )

            # Alert on health issues
            if not health_results["overall"]:
                unhealthy = [k for k, v in health_results.items() if k != "overall" and not v.get("healthy", True)]

                self.create_alert(
                    "System Health Degraded",
                    f"Unhealthy components: {', '.join(unhealthy)}",
                    AlertSeverity.WARNING,
                    "health_monitor",
                    health_results,
                )

    async def _anomaly_detector(self):
        """Detect metric anomalies"""
        while self._running:
            await asyncio.sleep(60)  # Every minute

            for metric_name, detector in self.anomaly_detectors.items():
                if self.metrics.get(metric_name):
                    recent_values = [m.value for m in list(self.metrics[metric_name])[-100:]]

                    if recent_values:
                        is_anomaly = await detector(recent_values)

                        if is_anomaly:
                            self.create_alert(
                                f"Anomaly Detected: {metric_name}",
                                f"Unusual pattern in {metric_name}",
                                AlertSeverity.WARNING,
                                "anomaly_detector",
                                {
                                    "metric": metric_name,
                                    "values": recent_values[-10:],
                                },
                            )

    async def _emergence_monitor(self):
        """Monitor for emergent behaviors"""
        while self._running:
            await asyncio.sleep(300)  # Every 5 minutes

            # Collect behavior data
            behavior_data = await self._collect_behavior_data()

            # Check for emergence
            await self.check_emergence(behavior_data)

    async def _handle_alert(self, alert: Alert):
        """Handle alert with registered handlers"""
        # Call severity-specific handlers
        for handler in self.alert_handlers[alert.severity]:
            try:
                await handler(alert)
            except Exception as e:
                print(f"Alert handler error: {e}")

        # Call general handlers
        for handler in self.alert_handlers.get(None, []):
            try:
                await handler(alert)
            except Exception as e:
                print(f"Alert handler error: {e}")

    async def _check_anomaly(self, metric: str, value: float):
        """Check single value for anomaly"""
        if metric in self.performance_baselines:
            baseline = self.performance_baselines[metric]
            deviation = abs(value - baseline) / baseline

            if deviation > 0.5:  # 50% deviation
                self.create_alert(
                    f"Performance Anomaly: {metric}",
                    f"Value {value} deviates {deviation  * 100:.1f}% from baseline {baseline}",
                    AlertSeverity.WARNING,
                    "performance_monitor",
                )

    async def _collect_behavior_data(self) -> dict[str, Any]:
        """Collect data for emergence detection"""
        return {
            "metrics_snapshot": {name: [m.value for m in list(values)[-100:]] for name, values in self.metrics.items()},
            "health_status": self.health_status.copy(),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _initialize_exporters(self):
        """Initialize metric exporters"""
        # In production, would export to Prometheus, CloudWatch, etc.

    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        import uuid

        return f"alert_{uuid.uuid4().hex[:8]}"


class TraceContext:
    """Performance trace context manager"""

    def __init__(self, telemetry: AGITelemetrySystem, operation: str):
        self.telemetry = telemetry
        self.operation = operation
        self.start_time = None
        self.metadata = {}

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        # Record duration
        self.telemetry.record_histogram(f"operation.duration.{self.operation}", duration, self.metadata)

        # Record success/failure
        if exc_type is None:
            self.telemetry.increment_counter(f"operation.success.{self.operation}")
        else:
            self.telemetry.increment_counter(f"operation.failure.{self.operation}")

    def add_metadata(self, key: str, value: str):
        """Add metadata to trace"""
        self.metadata[key] = value


class ConsciousnessMetrics:
    """Specialized metrics for consciousness monitoring"""

    def __init__(self):
        self.coherence_history = deque(maxlen=1000)
        self.state_transitions = defaultdict(int)

    async def record(self, state: dict[str, Any]):
        """Record consciousness metrics"""
        self.coherence_history.append(state.get("coherence", 0))

        # Track state transitions
        if "previous_state" in state and "current_state" in state:
            transition = f"{state['previous_state']}->{state['current_state']}"
            self.state_transitions[transition] += 1


class LearningMetrics:
    """Specialized metrics for learning monitoring"""

    def __init__(self):
        self.learning_events = deque(maxlen=10000)
        self.improvement_rates = defaultdict(list)

    async def record(self, event: dict[str, Any]):
        """Record learning metrics"""
        self.learning_events.append(event)

        if "domain" in event and "improvement" in event:
            self.improvement_rates[event["domain"]].append(event["improvement"])


class EmergenceDetector:
    """Detect emergent behaviors in Cognitive AI"""

    def __init__(self):
        self.pattern_history = deque(maxlen=1000)
        self.known_patterns = set()

    async def analyze(self, behavior_data: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Analyze for emergent patterns"""
        # Convert behavior to pattern signature
        pattern_sig = self._create_pattern_signature(behavior_data)

        if pattern_sig and pattern_sig not in self.known_patterns:
            # New pattern detected
            self.known_patterns.add(pattern_sig)

            return {
                "pattern": pattern_sig,
                "first_observed": datetime.now(timezone.utc).isoformat(),
                "data": behavior_data,
            }

        return None

    def _create_pattern_signature(self, data: dict[str, Any]) -> Optional[str]:
        """Create signature from behavior data"""
        # Simplified - in production would use more sophisticated analysis
        try:
            sig_data = json.dumps(data, sort_keys=True)
            return str(hash(sig_data))
        except BaseException:
            return None
