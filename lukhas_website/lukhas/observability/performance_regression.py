#!/usr/bin/env python3
"""
LUKHAS Performance Regression Detection
ML-based anomaly detection for performance regression identification and alerting.

Features:
- Statistical and ML-based performance anomaly detection
- Automated performance regression identification
- Real-time performance monitoring with alerting
- Historical performance baseline establishment
- Predictive performance modeling
- Performance impact assessment
- Automated regression root cause analysis
"""

import asyncio
import math
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

try:
    import numpy as np
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    np = None
    stats = None

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .advanced_metrics import MetricSeverity, get_advanced_metrics
from .evidence_collection import EvidenceType, collect_evidence
from .intelligent_alerting import get_alerting_system


class RegressionSeverity(Enum):
    """Performance regression severity levels"""
    MINOR = "minor"          # 5-15% degradation
    MODERATE = "moderate"    # 15-30% degradation
    MAJOR = "major"          # 30-50% degradation
    CRITICAL = "critical"    # >50% degradation


class DetectionMethod(Enum):
    """Methods used for regression detection"""
    STATISTICAL_THRESHOLD = "statistical_threshold"
    Z_SCORE = "z_score"
    TREND_ANALYSIS = "trend_analysis"
    ISOLATION_FOREST = "isolation_forest"
    CHANGE_POINT_DETECTION = "change_point_detection"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"


@dataclass
class PerformanceBaseline:
    """Performance baseline for a metric"""
    metric_name: str
    component: str
    baseline_value: float
    std_deviation: float
    percentiles: Dict[str, float]  # p50, p95, p99
    sample_count: int
    baseline_period_start: datetime
    baseline_period_end: datetime
    confidence_interval: Tuple[float, float]
    seasonal_patterns: Optional[Dict[str, float]] = None


@dataclass
class PerformanceRegression:
    """Detected performance regression"""
    regression_id: str
    metric_name: str
    component: str
    detection_method: DetectionMethod
    severity: RegressionSeverity
    baseline_value: float
    current_value: float
    degradation_percentage: float
    detection_timestamp: datetime
    confidence_score: float
    statistical_significance: float
    affected_operations: List[str]
    root_cause_candidates: List[str] = field(default_factory=list)
    correlation_evidence: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    false_positive: bool = False


@dataclass
class PerformanceAlert:
    """Performance regression alert"""
    alert_id: str
    regression: PerformanceRegression
    alert_level: MetricSeverity
    notification_sent: bool = False
    escalated: bool = False
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None


class PerformanceRegressionDetector:
    """
    Advanced performance regression detection system with ML-based anomaly detection.
    Provides comprehensive performance monitoring and automated regression identification.
    """

    def __init__(
        self,
        baseline_window_days: int = 7,
        detection_sensitivity: float = 0.8,
        min_samples_for_baseline: int = 100,
        enable_ml_detection: bool = True,
        enable_seasonal_analysis: bool = True,
        false_positive_learning: bool = True,
    ):
        """
        Initialize performance regression detector.

        Args:
            baseline_window_days: Days of data for baseline establishment
            detection_sensitivity: Detection sensitivity (0.0-1.0)
            min_samples_for_baseline: Minimum samples needed for baseline
            enable_ml_detection: Enable ML-based detection methods
            enable_seasonal_analysis: Enable seasonal pattern analysis
            false_positive_learning: Enable false positive learning
        """
        self.baseline_window_days = baseline_window_days
        self.detection_sensitivity = detection_sensitivity
        self.min_samples_for_baseline = min_samples_for_baseline
        self.enable_ml_detection = enable_ml_detection and SKLEARN_AVAILABLE
        self.enable_seasonal_analysis = enable_seasonal_analysis
        self.false_positive_learning = false_positive_learning

        # Core state
        self.performance_baselines: Dict[str, PerformanceBaseline] = {}
        self.detected_regressions: Dict[str, PerformanceRegression] = {}
        self.performance_alerts: Dict[str, PerformanceAlert] = {}

        # Historical data storage
        self.metric_timeseries: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.metric_timestamps: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))

        # ML models
        self.anomaly_models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}

        # Detection statistics
        self.detection_stats = {
            "total_detections": 0,
            "false_positives": 0,
            "true_positives": 0,
            "detection_accuracy": 0.0,
        }

        # Integration
        self.advanced_metrics = get_advanced_metrics()
        self.alerting_system = get_alerting_system()

        # Background tasks
        self._baseline_update_task: Optional[asyncio.Task] = None
        self._detection_task: Optional[asyncio.Task] = None

        self._start_background_tasks()

    async def record_performance_metric(
        self,
        metric_name: str,
        component: str,
        value: float,
        operation: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Record performance metric for regression detection.

        Args:
            metric_name: Name of the performance metric
            component: Component generating the metric
            value: Metric value
            operation: Specific operation if applicable
            timestamp: Metric timestamp (defaults to now)
            context: Additional context for the metric
        """
        timestamp = timestamp or datetime.now(timezone.utc)
        metric_key = f"{component}_{metric_name}"

        # Store metric data
        self.metric_timeseries[metric_key].append(value)
        self.metric_timestamps[metric_key].append(timestamp)

        # Clean old data
        cutoff_time = timestamp - timedelta(days=self.baseline_window_days * 2)
        while (self.metric_timestamps[metric_key] and
               self.metric_timestamps[metric_key][0] < cutoff_time):
            self.metric_timestamps[metric_key].popleft()
            self.metric_timeseries[metric_key].popleft()

        # Check for immediate regression if baseline exists
        if metric_key in self.performance_baselines:
            await self._check_for_regression(metric_key, value, timestamp, operation, context)

    async def establish_baseline(
        self,
        metric_name: str,
        component: str,
        force_update: bool = False,
    ) -> Optional[PerformanceBaseline]:
        """
        Establish performance baseline for a metric.

        Args:
            metric_name: Name of the metric
            component: Component name
            force_update: Force baseline update even if exists

        Returns:
            Established baseline or None if insufficient data
        """
        metric_key = f"{component}_{metric_name}"

        if not force_update and metric_key in self.performance_baselines:
            return self.performance_baselines[metric_key]

        # Check if we have enough data
        if len(self.metric_timeseries[metric_key]) < self.min_samples_for_baseline:
            return None

        values = list(self.metric_timeseries[metric_key])
        timestamps = list(self.metric_timestamps[metric_key])

        # Use data from the baseline window
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.baseline_window_days)
        baseline_data = [
            (v, t) for v, t in zip(values, timestamps) if t >= cutoff_time
        ]

        if len(baseline_data) < self.min_samples_for_baseline:
            return None

        baseline_values = [v for v, t in baseline_data]

        # Calculate statistical baseline
        mean_val = statistics.mean(baseline_values)
        std_val = statistics.stdev(baseline_values) if len(baseline_values) > 1 else 0
        sorted_values = sorted(baseline_values)
        n = len(sorted_values)

        percentiles = {
            "p50": sorted_values[int(n * 0.5)],
            "p95": sorted_values[int(n * 0.95)],
            "p99": sorted_values[int(n * 0.99)],
        }

        # Calculate confidence interval (95%)
        if std_val > 0 and SCIPY_AVAILABLE:
            confidence_interval = stats.t.interval(
                0.95, len(baseline_values) - 1,
                loc=mean_val, scale=std_val / math.sqrt(len(baseline_values))
            )
        else:
            confidence_interval = (mean_val - std_val, mean_val + std_val)

        # Seasonal pattern analysis
        seasonal_patterns = None
        if self.enable_seasonal_analysis and len(baseline_values) >= 50:
            seasonal_patterns = await self._analyze_seasonal_patterns(baseline_values, timestamps)

        baseline = PerformanceBaseline(
            metric_name=metric_name,
            component=component,
            baseline_value=mean_val,
            std_deviation=std_val,
            percentiles=percentiles,
            sample_count=len(baseline_values),
            baseline_period_start=baseline_data[0][1],
            baseline_period_end=baseline_data[-1][1],
            confidence_interval=confidence_interval,
            seasonal_patterns=seasonal_patterns,
        )

        self.performance_baselines[metric_key] = baseline

        # Train ML model for this metric
        if self.enable_ml_detection:
            await self._train_anomaly_model(metric_key, baseline_values)

        return baseline

    async def _analyze_seasonal_patterns(
        self,
        values: List[float],
        timestamps: List[datetime],
    ) -> Dict[str, float]:
        """Analyze seasonal patterns in the data"""
        if not SCIPY_AVAILABLE:
            return {}

        try:
            # Group by hour of day
            hourly_patterns = defaultdict(list)
            for value, timestamp in zip(values, timestamps):
                hour = timestamp.hour
                hourly_patterns[hour].append(value)

            # Calculate average for each hour
            hourly_averages = {}
            for hour, hour_values in hourly_patterns.items():
                if len(hour_values) >= 3:  # Minimum samples per hour
                    hourly_averages[f"hour_{hour}"] = statistics.mean(hour_values)

            return hourly_averages

        except Exception as e:
            print(f"Seasonal pattern analysis error: {e}")
            return {}

    async def _train_anomaly_model(self, metric_key: str, values: List[float]):
        """Train ML anomaly detection model for a metric"""
        if not self.enable_ml_detection or not SKLEARN_AVAILABLE:
            return

        try:
            # Prepare data for training
            X = np.array(values).reshape(-1, 1)

            # Scale the data
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Train Isolation Forest model
            model = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100,
            )
            model.fit(X_scaled)

            # Store model and scaler
            self.anomaly_models[metric_key] = model
            self.scalers[metric_key] = scaler

        except Exception as e:
            print(f"ML model training error for {metric_key}: {e}")

    async def _check_for_regression(
        self,
        metric_key: str,
        value: float,
        timestamp: datetime,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Check for performance regression using multiple detection methods"""
        baseline = self.performance_baselines[metric_key]

        # Statistical threshold detection
        regression = await self._detect_statistical_regression(
            metric_key, baseline, value, timestamp
        )

        # ML-based detection
        if not regression and self.enable_ml_detection:
            regression = await self._detect_ml_regression(
                metric_key, baseline, value, timestamp
            )

        # Trend analysis
        if not regression:
            regression = await self._detect_trend_regression(
                metric_key, baseline, value, timestamp
            )

        if regression:
            # Add operation and context information
            if operation:
                regression.affected_operations.append(operation)

            if context:
                regression.correlation_evidence.update(context)

            # Perform root cause analysis
            await self._analyze_root_cause(regression)

            # Store regression
            self.detected_regressions[regression.regression_id] = regression

            # Create alert
            await self._create_performance_alert(regression)

            # Collect evidence
            await self._collect_regression_evidence(regression)

    async def _detect_statistical_regression(
        self,
        metric_key: str,
        baseline: PerformanceBaseline,
        value: float,
        timestamp: datetime,
    ) -> Optional[PerformanceRegression]:
        """Detect regression using statistical methods"""
        # Z-score detection
        if baseline.std_deviation > 0:
            z_score = abs(value - baseline.baseline_value) / baseline.std_deviation

            # Adjust threshold based on sensitivity
            threshold = 3.0 - (self.detection_sensitivity * 1.5)

            if z_score > threshold and value > baseline.baseline_value:
                degradation_pct = ((value - baseline.baseline_value) / baseline.baseline_value) * 100

                # Determine severity
                severity = self._classify_regression_severity(degradation_pct)

                return PerformanceRegression(
                    regression_id=str(uuid4()),
                    metric_name=baseline.metric_name,
                    component=baseline.component,
                    detection_method=DetectionMethod.Z_SCORE,
                    severity=severity,
                    baseline_value=baseline.baseline_value,
                    current_value=value,
                    degradation_percentage=degradation_pct,
                    detection_timestamp=timestamp,
                    confidence_score=min(0.95, z_score / 5.0),
                    statistical_significance=1.0 - (1.0 / (1.0 + z_score)),
                    affected_operations=[],
                )

        # Percentile-based detection
        if value > baseline.percentiles["p99"]:
            degradation_pct = ((value - baseline.percentiles["p95"]) / baseline.percentiles["p95"]) * 100

            if degradation_pct > 10:  # 10% threshold above p95
                severity = self._classify_regression_severity(degradation_pct)

                return PerformanceRegression(
                    regression_id=str(uuid4()),
                    metric_name=baseline.metric_name,
                    component=baseline.component,
                    detection_method=DetectionMethod.STATISTICAL_THRESHOLD,
                    severity=severity,
                    baseline_value=baseline.percentiles["p95"],
                    current_value=value,
                    degradation_percentage=degradation_pct,
                    detection_timestamp=timestamp,
                    confidence_score=0.8,
                    statistical_significance=0.85,
                    affected_operations=[],
                )

        return None

    async def _detect_ml_regression(
        self,
        metric_key: str,
        baseline: PerformanceBaseline,
        value: float,
        timestamp: datetime,
    ) -> Optional[PerformanceRegression]:
        """Detect regression using ML models"""
        if metric_key not in self.anomaly_models:
            return None

        try:
            model = self.anomaly_models[metric_key]
            scaler = self.scalers[metric_key]

            # Scale the value
            X = np.array([[value]])
            X_scaled = scaler.transform(X)

            # Predict anomaly
            anomaly_score = model.decision_function(X_scaled)[0]
            is_anomaly = model.predict(X_scaled)[0] == -1

            if is_anomaly and value > baseline.baseline_value:
                degradation_pct = ((value - baseline.baseline_value) / baseline.baseline_value) * 100

                # Only consider significant degradations
                if degradation_pct > 5:
                    severity = self._classify_regression_severity(degradation_pct)

                    return PerformanceRegression(
                        regression_id=str(uuid4()),
                        metric_name=baseline.metric_name,
                        component=baseline.component,
                        detection_method=DetectionMethod.ISOLATION_FOREST,
                        severity=severity,
                        baseline_value=baseline.baseline_value,
                        current_value=value,
                        degradation_percentage=degradation_pct,
                        detection_timestamp=timestamp,
                        confidence_score=min(0.9, abs(anomaly_score) / 0.5),
                        statistical_significance=0.8,
                        affected_operations=[],
                    )

        except Exception as e:
            print(f"ML regression detection error: {e}")

        return None

    async def _detect_trend_regression(
        self,
        metric_key: str,
        baseline: PerformanceBaseline,
        value: float,
        timestamp: datetime,
    ) -> Optional[PerformanceRegression]:
        """Detect regression using trend analysis"""
        if not SCIPY_AVAILABLE or len(self.metric_timeseries[metric_key]) < 20:
            return None

        try:
            # Get recent data for trend analysis
            recent_values = list(self.metric_timeseries[metric_key])[-20:]
            recent_timestamps = list(self.metric_timestamps[metric_key])[-20:]

            # Convert timestamps to numeric for regression
            start_time = recent_timestamps[0].timestamp()
            x_values = [(t.timestamp() - start_time) / 3600 for t in recent_timestamps]  # Hours

            # Linear regression
            slope, intercept, r_value, p_value, _std_err = stats.linregress(x_values, recent_values)

            # Check if trend is significantly upward (performance degradation)
            if slope > 0 and p_value < 0.05 and abs(r_value) > 0.7:
                # Predict where the trend is heading
                predicted_value = slope * x_values[-1] + intercept
                degradation_pct = ((predicted_value - baseline.baseline_value) / baseline.baseline_value) * 100

                if degradation_pct > 10:
                    severity = self._classify_regression_severity(degradation_pct)

                    return PerformanceRegression(
                        regression_id=str(uuid4()),
                        metric_name=baseline.metric_name,
                        component=baseline.component,
                        detection_method=DetectionMethod.TREND_ANALYSIS,
                        severity=severity,
                        baseline_value=baseline.baseline_value,
                        current_value=value,
                        degradation_percentage=degradation_pct,
                        detection_timestamp=timestamp,
                        confidence_score=abs(r_value),
                        statistical_significance=1.0 - p_value,
                        affected_operations=[],
                        correlation_evidence={
                            "trend_slope": slope,
                            "r_squared": r_value**2,
                            "p_value": p_value,
                        }
                    )

        except Exception as e:
            print(f"Trend regression detection error: {e}")

        return None

    def _classify_regression_severity(self, degradation_percentage: float) -> RegressionSeverity:
        """Classify regression severity based on degradation percentage"""
        if degradation_percentage >= 50:
            return RegressionSeverity.CRITICAL
        elif degradation_percentage >= 30:
            return RegressionSeverity.MAJOR
        elif degradation_percentage >= 15:
            return RegressionSeverity.MODERATE
        else:
            return RegressionSeverity.MINOR

    async def _analyze_root_cause(self, regression: PerformanceRegression):
        """Perform automated root cause analysis for regression"""
        root_causes = []

        # Check for correlated metrics
        metric_key = f"{regression.component}_{regression.metric_name}"
        current_time = regression.detection_timestamp

        # Look for other metrics that regressed around the same time
        for other_key, other_timestamps in self.metric_timestamps.items():
            if other_key == metric_key:
                continue

            # Check if any values around the same time
            for i, timestamp in enumerate(other_timestamps):
                if abs((timestamp - current_time).total_seconds()) < 300 and i < len(self.metric_timeseries[other_key]):  # Within 5 minutes
                    other_value = self.metric_timeseries[other_key][i]
                    if other_key in self.performance_baselines:
                        other_baseline = self.performance_baselines[other_key]
                        if other_value > other_baseline.baseline_value * 1.2:  # 20% increase
                            root_causes.append(f"Correlated regression in {other_key}")

        # Check for error rate increases
        error_patterns = [
            "error_rate_increase",
            "connection_failures",
            "timeout_events",
            "memory_pressure",
            "cpu_saturation",
        ]

        for pattern in error_patterns:
            # This would check against actual error metrics
            # For now, add as potential cause
            if regression.severity in [RegressionSeverity.MAJOR, RegressionSeverity.CRITICAL]:
                root_causes.append(f"Potential {pattern}")

        regression.root_cause_candidates = root_causes[:5]  # Limit to top 5

    async def _create_performance_alert(self, regression: PerformanceRegression):
        """Create performance alert for regression"""
        # Map regression severity to alert severity
        alert_severity_map = {
            RegressionSeverity.MINOR: MetricSeverity.INFO,
            RegressionSeverity.MODERATE: MetricSeverity.WARNING,
            RegressionSeverity.MAJOR: MetricSeverity.CRITICAL,
            RegressionSeverity.CRITICAL: MetricSeverity.CRITICAL,
        }

        alert = PerformanceAlert(
            alert_id=str(uuid4()),
            regression=regression,
            alert_level=alert_severity_map[regression.severity],
        )

        self.performance_alerts[alert.alert_id] = alert

        # Send alert through alerting system
        try:
            await self.alerting_system.trigger_alert(
                rule_id="performance_regression_detected",
                source_component=regression.component,
                metric_name=regression.metric_name,
                current_value=regression.current_value,
                threshold_value=regression.baseline_value,
                labels={
                    "severity": regression.severity.value,
                    "degradation_pct": str(regression.degradation_percentage),
                    "detection_method": regression.detection_method.value,
                },
                annotations={
                    "description": f"Performance regression detected in {regression.component}",
                    "root_causes": ", ".join(regression.root_cause_candidates),
                },
                correlation_id=regression.regression_id,
            )
            alert.notification_sent = True

        except Exception as e:
            print(f"Failed to send performance alert: {e}")

    async def _collect_regression_evidence(self, regression: PerformanceRegression):
        """Collect evidence for regression detection"""
        await collect_evidence(
            evidence_type=EvidenceType.PERFORMANCE_METRIC,
            source_component="performance_regression_detector",
            operation="regression_detected",
            payload={
                "regression_id": regression.regression_id,
                "metric_name": regression.metric_name,
                "component": regression.component,
                "detection_method": regression.detection_method.value,
                "severity": regression.severity.value,
                "baseline_value": regression.baseline_value,
                "current_value": regression.current_value,
                "degradation_percentage": regression.degradation_percentage,
                "confidence_score": regression.confidence_score,
                "statistical_significance": regression.statistical_significance,
                "root_cause_candidates": regression.root_cause_candidates,
                "correlation_evidence": regression.correlation_evidence,
            },
            correlation_id=regression.regression_id,
        )

    async def mark_regression_resolved(
        self,
        regression_id: str,
        resolved_by: Optional[str] = None,
    ) -> bool:
        """Mark a regression as resolved"""
        if regression_id not in self.detected_regressions:
            return False

        regression = self.detected_regressions[regression_id]
        regression.resolved = True
        regression.resolution_timestamp = datetime.now(timezone.utc)

        # Collect evidence
        await collect_evidence(
            evidence_type=EvidenceType.SYSTEM_EVENT,
            source_component="performance_regression_detector",
            operation="regression_resolved",
            payload={
                "regression_id": regression_id,
                "resolved_by": resolved_by,
                "resolution_duration_seconds": (
                    regression.resolution_timestamp - regression.detection_timestamp
                ).total_seconds(),
            },
            user_id=resolved_by,
            correlation_id=regression_id,
        )

        return True

    async def mark_false_positive(
        self,
        regression_id: str,
        marked_by: Optional[str] = None,
    ) -> bool:
        """Mark a regression as false positive for learning"""
        if regression_id not in self.detected_regressions:
            return False

        regression = self.detected_regressions[regression_id]
        regression.false_positive = True

        # Update detection statistics
        self.detection_stats["false_positives"] += 1
        self._update_detection_accuracy()

        # If false positive learning is enabled, adjust models
        if self.false_positive_learning:
            await self._learn_from_false_positive(regression)

        # Collect evidence
        await collect_evidence(
            evidence_type=EvidenceType.USER_INTERACTION,
            source_component="performance_regression_detector",
            operation="false_positive_marked",
            payload={
                "regression_id": regression_id,
                "marked_by": marked_by,
                "detection_method": regression.detection_method.value,
                "degradation_percentage": regression.degradation_percentage,
            },
            user_id=marked_by,
            correlation_id=regression_id,
        )

        return True

    async def _learn_from_false_positive(self, regression: PerformanceRegression):
        """Learn from false positive to improve detection accuracy"""
        # This is a simplified implementation
        # In practice, would adjust model parameters, thresholds, etc.

        metric_key = f"{regression.component}_{regression.metric_name}"

        # Adjust statistical thresholds for this metric
        if metric_key in self.performance_baselines:
            self.performance_baselines[metric_key]

            # Slightly increase tolerance for this type of detection
            if regression.detection_method == DetectionMethod.Z_SCORE:
                # This would adjust internal thresholds
                pass

    def _update_detection_accuracy(self):
        """Update detection accuracy statistics"""
        total = self.detection_stats["false_positives"] + self.detection_stats["true_positives"]
        if total > 0:
            self.detection_stats["detection_accuracy"] = (
                self.detection_stats["true_positives"] / total
            )

    def get_active_regressions(
        self,
        component_filter: Optional[str] = None,
        severity_filter: Optional[RegressionSeverity] = None,
    ) -> List[PerformanceRegression]:
        """Get list of active (unresolved) regressions"""
        regressions = [
            r for r in self.detected_regressions.values()
            if not r.resolved and not r.false_positive
        ]

        if component_filter:
            regressions = [r for r in regressions if r.component == component_filter]

        if severity_filter:
            regressions = [r for r in regressions if r.severity == severity_filter]

        return sorted(regressions, key=lambda x: x.detection_timestamp, reverse=True)

    def get_regression_statistics(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get regression detection statistics"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)

        recent_regressions = [
            r for r in self.detected_regressions.values()
            if r.detection_timestamp >= cutoff_time
        ]

        stats = {
            "total_regressions": len(recent_regressions),
            "by_severity": defaultdict(int),
            "by_component": defaultdict(int),
            "by_detection_method": defaultdict(int),
            "resolved_count": len([r for r in recent_regressions if r.resolved]),
            "false_positive_count": len([r for r in recent_regressions if r.false_positive]),
            "average_degradation": 0,
            "detection_accuracy": self.detection_stats["detection_accuracy"],
        }

        if recent_regressions:
            for regression in recent_regressions:
                stats["by_severity"][regression.severity.value] += 1
                stats["by_component"][regression.component] += 1
                stats["by_detection_method"][regression.detection_method.value] += 1

            stats["average_degradation"] = statistics.mean([
                r.degradation_percentage for r in recent_regressions
            ])

        return dict(stats)

    def _start_background_tasks(self):
        """Start background tasks for baseline updates and detection"""
        async def baseline_worker():
            while True:
                try:
                    await self._update_baselines()
                    await asyncio.sleep(1800)  # Every 30 minutes
                except Exception as e:
                    print(f"Baseline update error: {e}")
                    await asyncio.sleep(1800)

        async def detection_worker():
            while True:
                try:
                    await self._periodic_detection_tasks()
                    await asyncio.sleep(300)  # Every 5 minutes
                except Exception as e:
                    print(f"Detection task error: {e}")
                    await asyncio.sleep(300)

        # Start background tasks if event loop is available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._baseline_update_task = loop.create_task(baseline_worker())
                self._detection_task = loop.create_task(detection_worker())
        except RuntimeError:
            # No event loop running
            pass

    async def _update_baselines(self):
        """Periodically update performance baselines"""
        for metric_key in list(self.metric_timeseries.keys()):
            if len(self.metric_timeseries[metric_key]) >= self.min_samples_for_baseline:
                parts = metric_key.split('_', 1)
                if len(parts) == 2:
                    component, metric_name = parts
                    await self.establish_baseline(metric_name, component, force_update=True)

    async def _periodic_detection_tasks(self):
        """Perform periodic detection and cleanup tasks"""
        # Clean old resolved regressions
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=30)
        old_regressions = [
            rid for rid, regression in self.detected_regressions.items()
            if regression.resolved and regression.resolution_timestamp and
            regression.resolution_timestamp < cutoff_time
        ]

        for rid in old_regressions:
            del self.detected_regressions[rid]

        # Clean old alerts
        old_alerts = [
            aid for aid, alert in self.performance_alerts.items()
            if alert.regression.resolved
        ]

        for aid in old_alerts:
            del self.performance_alerts[aid]

    async def shutdown(self):
        """Shutdown performance regression detector"""
        if self._baseline_update_task:
            self._baseline_update_task.cancel()
        if self._detection_task:
            self._detection_task.cancel()


# Global instance
_regression_detector: Optional[PerformanceRegressionDetector] = None


def initialize_regression_detector(**kwargs) -> PerformanceRegressionDetector:
    """Initialize global performance regression detector"""
    global _regression_detector
    _regression_detector = PerformanceRegressionDetector(**kwargs)
    return _regression_detector


def get_regression_detector() -> PerformanceRegressionDetector:
    """Get or create global regression detector"""
    global _regression_detector
    if _regression_detector is None:
        _regression_detector = initialize_regression_detector()
    return _regression_detector


async def record_performance_data(metric_name: str, component: str, value: float, **kwargs):
    """Convenience function for recording performance data"""
    detector = get_regression_detector()
    await detector.record_performance_metric(metric_name, component, value, **kwargs)


async def shutdown_regression_detector():
    """Shutdown global regression detector"""
    global _regression_detector
    if _regression_detector:
        await _regression_detector.shutdown()
        _regression_detector = None
