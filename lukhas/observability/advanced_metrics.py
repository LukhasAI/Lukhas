#!/usr/bin/env python3
"""
LUKHAS Advanced Metrics System
Enhanced metrics collection beyond basic Prometheus for LUKHAS-specific operations.

Features:
- LUKHAS-specific custom metrics with rich labels
- Real-time performance regression detection
- Evidence collection integration metrics
- Compliance and regulatory metrics
- High-cardinality metrics with intelligent aggregation
- ML-based anomaly detection for metrics
- Advanced alerting threshold calculations
"""

import asyncio
import json
import os
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from .prometheus_metrics import LUKHASMetrics, get_lukhas_metrics
from .evidence_collection import EvidenceType, collect_evidence


class MetricSeverity(Enum):
    """Metric alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AnomalyType(Enum):
    """Types of anomalies detected in metrics"""
    PERFORMANCE_REGRESSION = "performance_regression"
    ERROR_SPIKE = "error_spike"
    UNUSUAL_PATTERN = "unusual_pattern"
    THRESHOLD_BREACH = "threshold_breach"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    COMPLIANCE_VIOLATION = "compliance_violation"


@dataclass
class MetricAnomaly:
    """Detected metric anomaly"""
    anomaly_id: str
    metric_name: str
    anomaly_type: AnomalyType
    severity: MetricSeverity
    value: float
    expected_range: Tuple[float, float]
    confidence: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None


@dataclass
class MetricThreshold:
    """Dynamic metric threshold configuration"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    emergency_threshold: float
    evaluation_window_seconds: int = 300
    min_samples: int = 10
    adaptive: bool = True
    last_updated: Optional[datetime] = None


@dataclass
class ComplianceMetric:
    """Compliance-specific metric tracking"""
    regulation: str
    metric_name: str
    current_value: float
    compliance_threshold: float
    is_compliant: bool
    violation_count: int = 0
    last_violation: Optional[datetime] = None
    remediation_actions: List[str] = field(default_factory=list)


class AdvancedMetricsSystem:
    """
    Advanced metrics system with ML-based anomaly detection and intelligent alerting.
    Provides enhanced observability for LUKHAS-specific operations.
    """

    def __init__(
        self,
        enable_anomaly_detection: bool = True,
        enable_ml_features: bool = True,
        metric_retention_hours: int = 168,  # 7 days
        anomaly_sensitivity: float = 0.8,
        compliance_checks_enabled: bool = True,
    ):
        """
        Initialize advanced metrics system.

        Args:
            enable_anomaly_detection: Enable anomaly detection
            enable_ml_features: Enable ML-based features (requires numpy)
            metric_retention_hours: Hours to retain detailed metrics
            anomaly_sensitivity: Sensitivity for anomaly detection (0.0-1.0)
            compliance_checks_enabled: Enable compliance monitoring
        """
        self.enable_anomaly_detection = enable_anomaly_detection
        self.enable_ml_features = enable_ml_features and NUMPY_AVAILABLE
        self.metric_retention_hours = metric_retention_hours
        self.anomaly_sensitivity = anomaly_sensitivity
        self.compliance_checks_enabled = compliance_checks_enabled

        # Core metrics system integration
        self.prometheus_metrics = get_lukhas_metrics()

        # Advanced metrics storage
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.metric_timestamps: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))

        # Anomaly detection state
        self.detected_anomalies: List[MetricAnomaly] = []
        self.metric_baselines: Dict[str, Dict[str, float]] = {}
        self.metric_thresholds: Dict[str, MetricThreshold] = {}

        # Performance tracking
        self.operation_timings: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.error_patterns: Dict[str, List[datetime]] = defaultdict(list)

        # Compliance metrics
        self.compliance_metrics: Dict[str, ComplianceMetric] = {}

        # Evidence integration
        self.evidence_metrics_enabled = True

        # Background processing
        self._processing_task: Optional[asyncio.Task] = None
        self._start_background_processing()

        # Initialize default thresholds
        self._initialize_default_thresholds()

    def _initialize_default_thresholds(self):
        """Initialize default metric thresholds for LUKHAS operations"""
        default_thresholds = {
            "lukhas_response_time_seconds": MetricThreshold(
                metric_name="lukhas_response_time_seconds",
                warning_threshold=0.1,    # 100ms
                critical_threshold=0.25,  # 250ms (T4 requirement)
                emergency_threshold=1.0,  # 1s
                evaluation_window_seconds=60,
            ),
            "lukhas_memory_recall_latency_seconds": MetricThreshold(
                metric_name="lukhas_memory_recall_latency_seconds",
                warning_threshold=0.05,   # 50ms
                critical_threshold=0.1,   # 100ms
                emergency_threshold=0.5,  # 500ms
            ),
            "lukhas_errors_total": MetricThreshold(
                metric_name="lukhas_errors_total",
                warning_threshold=10,     # 10 errors/window
                critical_threshold=50,    # 50 errors/window
                emergency_threshold=100,  # 100 errors/window
                evaluation_window_seconds=300,
            ),
            "lukhas_evidence_collection_time_ms": MetricThreshold(
                metric_name="lukhas_evidence_collection_time_ms",
                warning_threshold=5,      # 5ms
                critical_threshold=10,    # 10ms (requirement)
                emergency_threshold=50,   # 50ms
            ),
        }

        for name, threshold in default_thresholds.items():
            self.metric_thresholds[name] = threshold

        # Initialize compliance metrics
        if self.compliance_checks_enabled:
            self._initialize_compliance_metrics()

    def _initialize_compliance_metrics(self):
        """Initialize compliance-specific metrics"""
        compliance_configs = {
            "gdpr_data_retention": ComplianceMetric(
                regulation="GDPR",
                metric_name="data_retention_days",
                current_value=0,
                compliance_threshold=2555,  # 7 years max
                is_compliant=True,
            ),
            "evidence_integrity_rate": ComplianceMetric(
                regulation="SOX",
                metric_name="evidence_integrity_verification_rate",
                current_value=100.0,
                compliance_threshold=99.99,
                is_compliant=True,
            ),
            "audit_trail_completeness": ComplianceMetric(
                regulation="SOX",
                metric_name="audit_trail_completeness_percent",
                current_value=100.0,
                compliance_threshold=100.0,
                is_compliant=True,
            ),
        }

        for name, metric in compliance_configs.items():
            self.compliance_metrics[name] = metric

    async def record_advanced_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None,
    ):
        """
        Record advanced metric with anomaly detection.

        Args:
            metric_name: Name of the metric
            value: Metric value
            labels: Optional metric labels
            timestamp: Optional timestamp (defaults to now)
        """
        timestamp = timestamp or datetime.now(timezone.utc)

        # Store metric history
        self.metric_history[metric_name].append(value)
        self.metric_timestamps[metric_name].append(timestamp)

        # Clean old metrics
        cutoff_time = timestamp - timedelta(hours=self.metric_retention_hours)
        while (self.metric_timestamps[metric_name] and
               self.metric_timestamps[metric_name][0] < cutoff_time):
            self.metric_timestamps[metric_name].popleft()
            self.metric_history[metric_name].popleft()

        # Anomaly detection
        if self.enable_anomaly_detection:
            await self._check_for_anomalies(metric_name, value, timestamp)

        # Evidence collection for critical metrics
        if (self.evidence_metrics_enabled and
            metric_name in self.metric_thresholds and
            value > self.metric_thresholds[metric_name].warning_threshold):

            await collect_evidence(
                evidence_type=EvidenceType.PERFORMANCE_METRIC,
                source_component="advanced_metrics",
                operation="threshold_breach",
                payload={
                    "metric_name": metric_name,
                    "value": value,
                    "threshold": self.metric_thresholds[metric_name].warning_threshold,
                    "labels": labels,
                }
            )

    async def _check_for_anomalies(
        self,
        metric_name: str,
        value: float,
        timestamp: datetime,
    ):
        """Check metric for anomalies using statistical and ML methods"""
        history = list(self.metric_history[metric_name])

        if len(history) < 10:  # Need minimum data points
            return

        # Statistical anomaly detection
        mean_val = statistics.mean(history[:-1])  # Exclude current value
        std_val = statistics.stdev(history[:-1]) if len(history) > 1 else 0

        # Z-score based detection
        if std_val > 0:
            z_score = abs(value - mean_val) / std_val
            if z_score > (3.0 - self.anomaly_sensitivity):  # Adaptive threshold
                await self._record_anomaly(
                    metric_name=metric_name,
                    anomaly_type=AnomalyType.UNUSUAL_PATTERN,
                    value=value,
                    expected_range=(mean_val - 2*std_val, mean_val + 2*std_val),
                    confidence=min(0.95, z_score / 3.0),
                    timestamp=timestamp,
                    context={"z_score": z_score, "mean": mean_val, "std": std_val}
                )

        # ML-based anomaly detection
        if self.enable_ml_features and len(history) >= 50:
            await self._ml_anomaly_detection(metric_name, value, timestamp, history)

        # Threshold-based detection
        if metric_name in self.metric_thresholds:
            await self._threshold_based_detection(metric_name, value, timestamp)

    async def _ml_anomaly_detection(
        self,
        metric_name: str,
        value: float,
        timestamp: datetime,
        history: List[float],
    ):
        """ML-based anomaly detection using statistical methods"""
        if not NUMPY_AVAILABLE:
            return

        try:
            # Convert to numpy array for analysis
            data = np.array(history)

            # Simple trend analysis
            if len(data) >= 20:
                recent_trend = np.polyfit(range(len(data[-20:])), data[-20:], 1)[0]
                overall_trend = np.polyfit(range(len(data)), data, 1)[0]

                # Detect sudden trend changes
                if abs(recent_trend - overall_trend) > np.std(data) * 0.5:
                    await self._record_anomaly(
                        metric_name=metric_name,
                        anomaly_type=AnomalyType.PERFORMANCE_REGRESSION,
                        value=value,
                        expected_range=(np.min(data), np.max(data)),
                        confidence=0.8,
                        timestamp=timestamp,
                        context={
                            "recent_trend": recent_trend,
                            "overall_trend": overall_trend,
                            "trend_change": recent_trend - overall_trend,
                        }
                    )

            # Seasonal pattern detection (simplified)
            if len(data) >= 100:
                # Look for unusual deviations from recent patterns
                recent_data = data[-50:]
                baseline_data = data[-100:-50]

                recent_mean = np.mean(recent_data)
                baseline_mean = np.mean(baseline_data)
                baseline_std = np.std(baseline_data)

                if baseline_std > 0 and abs(recent_mean - baseline_mean) > 2 * baseline_std:
                    await self._record_anomaly(
                        metric_name=metric_name,
                        anomaly_type=AnomalyType.UNUSUAL_PATTERN,
                        value=value,
                        expected_range=(baseline_mean - 2*baseline_std, baseline_mean + 2*baseline_std),
                        confidence=0.85,
                        timestamp=timestamp,
                        context={
                            "recent_mean": recent_mean,
                            "baseline_mean": baseline_mean,
                            "deviation": abs(recent_mean - baseline_mean),
                        }
                    )

        except Exception as e:
            # Log error but don't fail the metric recording
            print(f"ML anomaly detection error for {metric_name}: {e}")

    async def _threshold_based_detection(
        self,
        metric_name: str,
        value: float,
        timestamp: datetime,
    ):
        """Check for threshold-based anomalies"""
        threshold = self.metric_thresholds[metric_name]

        severity = None
        if value >= threshold.emergency_threshold:
            severity = MetricSeverity.EMERGENCY
        elif value >= threshold.critical_threshold:
            severity = MetricSeverity.CRITICAL
        elif value >= threshold.warning_threshold:
            severity = MetricSeverity.WARNING

        if severity:
            await self._record_anomaly(
                metric_name=metric_name,
                anomaly_type=AnomalyType.THRESHOLD_BREACH,
                value=value,
                expected_range=(0, threshold.warning_threshold),
                confidence=1.0,
                timestamp=timestamp,
                severity=severity,
                context={
                    "threshold_type": severity.value,
                    "threshold_value": getattr(threshold, f"{severity.value}_threshold"),
                }
            )

    async def _record_anomaly(
        self,
        metric_name: str,
        anomaly_type: AnomalyType,
        value: float,
        expected_range: Tuple[float, float],
        confidence: float,
        timestamp: datetime,
        severity: Optional[MetricSeverity] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Record detected anomaly"""
        if not severity:
            # Auto-assign severity based on confidence and deviation
            if confidence >= 0.95:
                severity = MetricSeverity.CRITICAL
            elif confidence >= 0.8:
                severity = MetricSeverity.WARNING
            else:
                severity = MetricSeverity.INFO

        anomaly = MetricAnomaly(
            anomaly_id=str(uuid4()),
            metric_name=metric_name,
            anomaly_type=anomaly_type,
            severity=severity,
            value=value,
            expected_range=expected_range,
            confidence=confidence,
            timestamp=timestamp,
            context=context or {},
        )

        self.detected_anomalies.append(anomaly)

        # Collect evidence for critical anomalies
        if severity in [MetricSeverity.CRITICAL, MetricSeverity.EMERGENCY]:
            await collect_evidence(
                evidence_type=EvidenceType.SYSTEM_EVENT,
                source_component="advanced_metrics",
                operation="anomaly_detection",
                payload={
                    "anomaly_id": anomaly.anomaly_id,
                    "metric_name": metric_name,
                    "anomaly_type": anomaly_type.value,
                    "severity": severity.value,
                    "value": value,
                    "expected_range": expected_range,
                    "confidence": confidence,
                    "context": context,
                }
            )

        # Update Prometheus metrics
        if hasattr(self.prometheus_metrics, 'errors_total'):
            self.prometheus_metrics.errors_total.labels(
                component="anomaly_detection",
                error_type=f"{anomaly_type.value}_{severity.value}",
                lane=self.prometheus_metrics.lane,
            ).inc()

    def record_operation_timing(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Record operation timing for performance analysis"""
        self.operation_timings[operation].append({
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.now(timezone.utc),
            "context": context or {},
        })

        # Async record to advanced metrics
        asyncio.create_task(self.record_advanced_metric(
            metric_name=f"lukhas_operation_{operation}_duration_ms",
            value=duration_ms,
            labels={"success": str(success)},
        ))

    def update_compliance_metric(
        self,
        regulation: str,
        metric_name: str,
        current_value: float,
    ):
        """Update compliance metric and check for violations"""
        compliance_key = f"{regulation.lower()}_{metric_name}"

        if compliance_key in self.compliance_metrics:
            metric = self.compliance_metrics[compliance_key]
            metric.current_value = current_value

            # Check compliance
            if regulation.upper() == "GDPR":
                # For GDPR, lower is better (retention period)
                metric.is_compliant = current_value <= metric.compliance_threshold
            else:
                # For most regulations, higher is better
                metric.is_compliant = current_value >= metric.compliance_threshold

            if not metric.is_compliant:
                metric.violation_count += 1
                metric.last_violation = datetime.now(timezone.utc)

                # Record compliance violation evidence
                asyncio.create_task(collect_evidence(
                    evidence_type=EvidenceType.REGULATORY_EVENT,
                    source_component="advanced_metrics",
                    operation="compliance_violation",
                    payload={
                        "regulation": regulation,
                        "metric_name": metric_name,
                        "current_value": current_value,
                        "threshold": metric.compliance_threshold,
                        "violation_count": metric.violation_count,
                    },
                    compliance_regimes=[regulation.upper()],
                ))

    def get_metric_statistics(self, metric_name: str) -> Dict[str, Any]:
        """Get statistical analysis of a metric"""
        if metric_name not in self.metric_history:
            return {}

        history = list(self.metric_history[metric_name])
        if not history:
            return {}

        stats = {
            "count": len(history),
            "min": min(history),
            "max": max(history),
            "mean": statistics.mean(history),
            "median": statistics.median(history),
        }

        if len(history) > 1:
            stats["std"] = statistics.stdev(history)

            # Percentiles
            sorted_history = sorted(history)
            n = len(sorted_history)
            stats["p95"] = sorted_history[int(n * 0.95)]
            stats["p99"] = sorted_history[int(n * 0.99)]

        return stats

    def get_anomaly_summary(
        self,
        hours_back: int = 24,
        severity_filter: Optional[MetricSeverity] = None,
    ) -> List[MetricAnomaly]:
        """Get summary of detected anomalies"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)

        filtered_anomalies = [
            anomaly for anomaly in self.detected_anomalies
            if anomaly.timestamp >= cutoff_time and not anomaly.resolved
        ]

        if severity_filter:
            filtered_anomalies = [
                anomaly for anomaly in filtered_anomalies
                if anomaly.severity == severity_filter
            ]

        return filtered_anomalies

    def get_performance_dashboard_data(self) -> Dict[str, Any]:
        """Get data for performance dashboard"""
        current_time = datetime.now(timezone.utc)

        # Calculate performance metrics
        operation_stats = {}
        for operation, timings in self.operation_timings.items():
            recent_timings = [
                t for t in timings
                if (current_time - t["timestamp"]).total_seconds() < 3600  # Last hour
            ]

            if recent_timings:
                durations = [t["duration_ms"] for t in recent_timings]
                success_rate = sum(1 for t in recent_timings if t["success"]) / len(recent_timings)

                operation_stats[operation] = {
                    "count": len(recent_timings),
                    "avg_duration_ms": statistics.mean(durations),
                    "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)],
                    "success_rate": success_rate,
                }

        # Recent anomalies
        recent_anomalies = self.get_anomaly_summary(hours_back=1)
        anomaly_counts = defaultdict(int)
        for anomaly in recent_anomalies:
            anomaly_counts[anomaly.severity] += 1

        # Compliance status
        compliance_summary = {}
        for key, metric in self.compliance_metrics.items():
            compliance_summary[key] = {
                "regulation": metric.regulation,
                "is_compliant": metric.is_compliant,
                "current_value": metric.current_value,
                "threshold": metric.compliance_threshold,
                "violation_count": metric.violation_count,
            }

        return {
            "timestamp": current_time.isoformat(),
            "operation_statistics": operation_stats,
            "anomaly_counts": dict(anomaly_counts),
            "compliance_status": compliance_summary,
            "total_metrics_tracked": len(self.metric_history),
            "evidence_collection_enabled": self.evidence_metrics_enabled,
        }

    def _start_background_processing(self):
        """Start background processing tasks"""
        async def process_metrics():
            while True:
                try:
                    await self._update_metric_baselines()
                    await self._cleanup_old_data()
                    await asyncio.sleep(300)  # Every 5 minutes
                except Exception as e:
                    print(f"Background metrics processing error: {e}")
                    await asyncio.sleep(60)

        # Start background task if event loop is available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._processing_task = loop.create_task(process_metrics())
        except RuntimeError:
            # No event loop running
            pass

    async def _update_metric_baselines(self):
        """Update metric baselines for improved anomaly detection"""
        for metric_name, history in self.metric_history.items():
            if len(history) >= 100:  # Need sufficient data
                recent_data = list(history)[-100:]  # Last 100 points

                self.metric_baselines[metric_name] = {
                    "mean": statistics.mean(recent_data),
                    "std": statistics.stdev(recent_data) if len(recent_data) > 1 else 0,
                    "min": min(recent_data),
                    "max": max(recent_data),
                    "updated_at": datetime.now(timezone.utc),
                }

    async def _cleanup_old_data(self):
        """Clean up old metric data and resolved anomalies"""
        # Clean old anomalies
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
        self.detected_anomalies = [
            anomaly for anomaly in self.detected_anomalies
            if anomaly.timestamp >= cutoff_time or not anomaly.resolved
        ]

        # Clean old error patterns
        for error_type in self.error_patterns:
            self.error_patterns[error_type] = [
                timestamp for timestamp in self.error_patterns[error_type]
                if timestamp >= cutoff_time
            ]

    async def shutdown(self):
        """Shutdown advanced metrics system"""
        if self._processing_task:
            self._processing_task.cancel()


# Global instance
_advanced_metrics: Optional[AdvancedMetricsSystem] = None


def initialize_advanced_metrics(
    enable_anomaly_detection: bool = True,
    enable_ml_features: bool = True,
    **kwargs
) -> AdvancedMetricsSystem:
    """Initialize global advanced metrics system"""
    global _advanced_metrics
    _advanced_metrics = AdvancedMetricsSystem(
        enable_anomaly_detection=enable_anomaly_detection,
        enable_ml_features=enable_ml_features,
        **kwargs
    )
    return _advanced_metrics


def get_advanced_metrics() -> AdvancedMetricsSystem:
    """Get or create global advanced metrics system"""
    global _advanced_metrics
    if _advanced_metrics is None:
        _advanced_metrics = initialize_advanced_metrics()
    return _advanced_metrics


async def record_metric(metric_name: str, value: Union[int, float], **kwargs) -> None:
    """Convenience function for recording advanced metrics"""
    system = get_advanced_metrics()
    await system.record_advanced_metric(metric_name, value, **kwargs)


def record_operation_performance(operation: str, duration_ms: float, success: bool = True) -> None:
    """Convenience function for recording operation performance"""
    system = get_advanced_metrics()
    system.record_operation_timing(operation, duration_ms, success)


async def shutdown_advanced_metrics():
    """Shutdown global advanced metrics"""
    global _advanced_metrics
    if _advanced_metrics:
        await _advanced_metrics.shutdown()
        _advanced_metrics = None