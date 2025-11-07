"""
Service-Specific Metrics Collection
===================================

P0-3 OBS-BURN: Comprehensive service metrics for missing components
with T4/0.01% excellence monitoring and burn-rate SLO tracking.

Features:
- Service-specific metric collectors
- T4/0.01% excellence compliance tracking
- Burn rate calculation for SLOs
- Integration with memory, registry, and identity services
- Prometheus metrics export
- Real-time alerting integration
"""

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of services monitored"""
    MEMORY = "memory"
    REGISTRY = "registry"
    IDENTITY = "identity"
    CONSCIOUSNESS = "consciousness"
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
    LEDGER = "ledger"


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    SUMMARY = "summary"


@dataclass
class ServiceMetric:
    """Individual service metric"""
    name: str
    service: ServiceType
    metric_type: MetricType
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    help_text: str = ""


@dataclass
class SLOBurnRate:
    """SLO burn rate calculation"""
    service: str
    slo_target: float  # Target SLO (e.g., 0.999 for 99.9%)
    time_window: str   # Time window (e.g., "1h", "6h", "24h")
    error_rate: float  # Current error rate
    burn_rate: float   # Rate at which error budget is consumed
    budget_remaining: float  # Remaining error budget (0.0-1.0)
    alert_threshold: float  # Alert when burn rate exceeds this
    critical_threshold: float  # Critical alert threshold


@dataclass
class T4ComplianceMetrics:
    """T4/0.01% excellence compliance tracking"""
    service: str
    operation: str
    p95_latency_ms: float
    p99_latency_ms: float
    p999_latency_ms: float
    slo_target_ms: float
    compliance_rate: float  # 0.0-1.0
    total_operations: int
    failed_operations: int
    sample_window: int = 1000


class ServiceMetricsCollector:
    """
    Comprehensive service metrics collector with T4/0.01% excellence tracking
    and burn-rate SLO monitoring.
    """

    def __init__(self):
        self.metrics: dict[str, ServiceMetric] = {}
        self.metric_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.slo_burn_rates: dict[str, SLOBurnRate] = {}
        self.t4_compliance: dict[str, T4ComplianceMetrics] = {}

        # Service configurations
        self.service_configs = self._initialize_service_configs()

        # Thread safety
        self._lock = threading.RLock()

        # Prometheus metrics (mock for now)
        self.prometheus_metrics = {}

        logger.info("ServiceMetricsCollector initialized")

    def _initialize_service_configs(self) -> dict[ServiceType, dict[str, Any]]:
        """Initialize service-specific configurations"""
        return {
            ServiceType.MEMORY: {
                "slo_target": 0.999,  # 99.9% availability
                "latency_targets": {
                    "search": 50.0,    # p95 <50ms
                    "upsert": 100.0,   # p95 <100ms
                    "batch": 200.0     # p95 <200ms
                },
                "burn_rate_windows": ["1h", "6h", "24h"],
                "alert_thresholds": {
                    "warning": 2.0,
                    "critical": 10.0
                }
            },
            ServiceType.REGISTRY: {
                "slo_target": 0.9995,  # 99.95% availability
                "latency_targets": {
                    "discovery": 10.0,   # p95 <10ms
                    "resolve": 5.0,      # p95 <5ms
                    "register": 20.0     # p95 <20ms
                },
                "burn_rate_windows": ["1h", "6h"],
                "alert_thresholds": {
                    "warning": 1.5,
                    "critical": 5.0
                }
            },
            ServiceType.IDENTITY: {
                "slo_target": 0.9999,  # 99.99% availability
                "latency_targets": {
                    "authenticate": 100.0,  # p95 <100ms
                    "authorize": 50.0,      # p95 <50ms
                    "webauthn": 200.0       # p95 <200ms
                },
                "burn_rate_windows": ["1h", "6h", "24h"],
                "alert_thresholds": {
                    "warning": 2.0,
                    "critical": 8.0
                }
            },
            ServiceType.CONSCIOUSNESS: {
                "slo_target": 0.995,  # 99.5% availability
                "latency_targets": {
                    "process": 500.0,      # p95 <500ms
                    "dream": 1000.0,       # p95 <1000ms
                    "awareness": 100.0     # p95 <100ms
                },
                "burn_rate_windows": ["6h", "24h"],
                "alert_thresholds": {
                    "warning": 3.0,
                    "critical": 12.0
                }
            },
            ServiceType.GOVERNANCE: {
                "slo_target": 0.9999,  # 99.99% availability
                "latency_targets": {
                    "policy_check": 50.0,   # p95 <50ms
                    "consent": 100.0,       # p95 <100ms
                    "audit": 200.0          # p95 <200ms
                },
                "burn_rate_windows": ["1h", "6h", "24h"],
                "alert_thresholds": {
                    "warning": 1.0,
                    "critical": 4.0
                }
            }
        }

    def create_standard_labels(self,
                              lane: Optional[str] = None,
                              component: Optional[str] = None,
                              operation: Optional[str] = None,
                              provider: Optional[str] = None,
                              **custom_labels) -> dict[str, str]:
        """Create standardized Prometheus labels for T4/0.01% compliance"""
        labels = {}

        # Standard T4 labels (avoid high-cardinality IDs)
        if lane:
            labels["lane"] = lane
        if component:
            labels["component"] = component
        if operation:
            labels["operation"] = operation
        if provider:
            labels["provider"] = provider

        # Add any custom labels
        labels.update(custom_labels)

        return labels

    def record_metric(self,
                     name: str,
                     value: float,
                     service: ServiceType,
                     metric_type: MetricType = MetricType.GAUGE,
                     labels: Optional[dict[str, str]] = None,
                     help_text: str = "",
                     lane: Optional[str] = None,
                     component: Optional[str] = None,
                     operation: Optional[str] = None,
                     provider: Optional[str] = None):
        """Record a service metric with standardized labels"""
        with self._lock:
            metric_key = f"{service.value}_{name}"

            # Create standardized labels
            standard_labels = self.create_standard_labels(
                lane=lane,
                component=component,
                operation=operation,
                provider=provider,
                **(labels or {})
            )

            metric = ServiceMetric(
                name=name,
                service=service,
                metric_type=metric_type,
                value=value,
                labels=standard_labels,
                help_text=help_text
            )

            self.metrics[metric_key] = metric
            self.metric_history[metric_key].append(metric)

            # Update Prometheus metrics (mock)
            self._update_prometheus_metric(metric)

    def record_operation_latency(self,
                               service: ServiceType,
                               operation: str,
                               latency_ms: float,
                               success: bool = True):
        """Record operation latency for T4/0.01% excellence tracking"""
        with self._lock:
            # Record basic latency metric
            self.record_metric(
                f"{operation}_latency_ms",
                latency_ms,
                service,
                MetricType.HISTOGRAM,
                {"operation": operation, "success": str(success)}
            )

            # Update T4 compliance metrics
            compliance_key = f"{service.value}_{operation}"

            if compliance_key not in self.t4_compliance:
                config = self.service_configs.get(service, {})
                target_latency = config.get("latency_targets", {}).get(operation, 100.0)

                self.t4_compliance[compliance_key] = T4ComplianceMetrics(
                    service=service.value,
                    operation=operation,
                    p95_latency_ms=0.0,
                    p99_latency_ms=0.0,
                    p999_latency_ms=0.0,
                    slo_target_ms=target_latency,
                    compliance_rate=0.0,
                    total_operations=0,
                    failed_operations=0
                )

            compliance = self.t4_compliance[compliance_key]
            compliance.total_operations += 1

            if not success:
                compliance.failed_operations += 1

            # Update latency percentiles from history
            history_key = f"{service.value}_{operation}_latency_ms"
            if history_key in self.metric_history:
                recent_latencies = [m.value for m in list(self.metric_history[history_key])[-1000:]]
                if len(recent_latencies) >= 20:
                    sorted_latencies = sorted(recent_latencies)
                    n = len(sorted_latencies)

                    compliance.p95_latency_ms = sorted_latencies[int(n * 0.95)]
                    compliance.p99_latency_ms = sorted_latencies[int(n * 0.99)]
                    compliance.p999_latency_ms = sorted_latencies[int(n * 0.999)]

                    # Calculate compliance rate
                    compliant_ops = sum(1 for lat in recent_latencies if lat <= compliance.slo_target_ms)
                    compliance.compliance_rate = compliant_ops / len(recent_latencies)

    def calculate_burn_rate(self,
                          service: ServiceType,
                          time_window: str = "1h") -> Optional[SLOBurnRate]:
        """Calculate SLO burn rate for a service"""
        with self._lock:
            config = self.service_configs.get(service)
            if not config:
                return None

            slo_target = config["slo_target"]
            error_budget = 1.0 - slo_target

            # Calculate current error rate from recent metrics
            error_rate = self._calculate_error_rate(service, time_window)

            # Calculate burn rate
            # Burn rate = (error rate) / (error budget)
            burn_rate = error_rate / error_budget if error_budget > 0 else 0.0

            # Calculate remaining budget
            # Simplified - in production would track over longer periods
            budget_remaining = max(0.0, 1.0 - (error_rate / error_budget))

            # Get alert thresholds
            alert_threshold = config.get("alert_thresholds", {}).get("warning", 2.0)
            critical_threshold = config.get("alert_thresholds", {}).get("critical", 10.0)

            burn_rate_metric = SLOBurnRate(
                service=service.value,
                slo_target=slo_target,
                time_window=time_window,
                error_rate=error_rate,
                burn_rate=burn_rate,
                budget_remaining=budget_remaining,
                alert_threshold=alert_threshold,
                critical_threshold=critical_threshold
            )

            # Store for tracking
            burn_rate_key = f"{service.value}_{time_window}"
            self.slo_burn_rates[burn_rate_key] = burn_rate_metric

            # Record as metric
            self.record_metric(
                f"slo_burn_rate_{time_window}",
                burn_rate,
                service,
                MetricType.GAUGE,
                {"time_window": time_window}
            )

            return burn_rate_metric

    def _calculate_error_rate(self, service: ServiceType, time_window: str) -> float:
        """Calculate error rate for a service in given time window"""
        # Parse time window
        if time_window.endswith('h'):
            hours = int(time_window[:-1])
            window_seconds = hours * 3600
        elif time_window.endswith('m'):
            minutes = int(time_window[:-1])
            window_seconds = minutes * 60
        else:
            window_seconds = 3600  # Default 1 hour

        cutoff_time = time.time() - window_seconds

        # Count success vs error operations
        total_ops = 0
        error_ops = 0

        for metric_key, history in self.metric_history.items():
            if not metric_key.startswith(service.value):
                continue

            for metric in history:
                if metric.timestamp < cutoff_time:
                    continue

                # Count operations with success/failure labels
                if 'success' in metric.labels:
                    total_ops += 1
                    if metric.labels['success'] == 'False':
                        error_ops += 1

        return error_ops / total_ops if total_ops > 0 else 0.0

    def _update_prometheus_metric(self, metric: ServiceMetric):
        """Update Prometheus metrics (mock implementation)"""
        # In a real implementation, this would update actual Prometheus metrics
        metric_name = f"lukhas_{metric.service.value}_{metric.name}"

        if metric.metric_type == MetricType.COUNTER:
            # Would increment a Prometheus Counter
            pass
        elif metric.metric_type == MetricType.HISTOGRAM:
            # Would observe a Prometheus Histogram
            pass
        elif metric.metric_type == MetricType.GAUGE:
            # Would set a Prometheus Gauge
            pass

        self.prometheus_metrics[metric_name] = {
            'value': metric.value,
            'labels': metric.labels,
            'timestamp': metric.timestamp
        }

    def get_service_metrics(self, service: ServiceType) -> dict[str, ServiceMetric]:
        """Get all metrics for a specific service"""
        with self._lock:
            return {
                key: metric for key, metric in self.metrics.items()
                if metric.service == service
            }

    def get_t4_compliance_report(self) -> dict[str, dict[str, Any]]:
        """Get T4/0.01% excellence compliance report"""
        with self._lock:
            report = {}

            for key, compliance in self.t4_compliance.items():
                is_compliant = compliance.p95_latency_ms <= compliance.slo_target_ms

                report[key] = {
                    'service': compliance.service,
                    'operation': compliance.operation,
                    'p95_latency_ms': compliance.p95_latency_ms,
                    'p99_latency_ms': compliance.p99_latency_ms,
                    'slo_target_ms': compliance.slo_target_ms,
                    'compliance_rate': compliance.compliance_rate,
                    't4_compliant': is_compliant,
                    'total_operations': compliance.total_operations,
                    'error_rate': compliance.failed_operations / max(compliance.total_operations, 1)
                }

            return report

    def get_burn_rate_status(self) -> dict[str, dict[str, Any]]:
        """Get current burn rate status for all services"""
        with self._lock:
            status = {}

            for key, burn_rate in self.slo_burn_rates.items():
                alert_level = "ok"
                if burn_rate.burn_rate >= burn_rate.critical_threshold:
                    alert_level = "critical"
                elif burn_rate.burn_rate >= burn_rate.alert_threshold:
                    alert_level = "warning"

                status[key] = {
                    'service': burn_rate.service,
                    'time_window': burn_rate.time_window,
                    'slo_target': burn_rate.slo_target,
                    'error_rate': burn_rate.error_rate,
                    'burn_rate': burn_rate.burn_rate,
                    'budget_remaining': burn_rate.budget_remaining,
                    'alert_level': alert_level,
                    'budget_exhaustion_time': self._calculate_exhaustion_time(burn_rate)
                }

            return status

    def _calculate_exhaustion_time(self, burn_rate: SLOBurnRate) -> Optional[str]:
        """Calculate when error budget will be exhausted at current burn rate"""
        if burn_rate.burn_rate <= 0 or burn_rate.budget_remaining <= 0:
            return None

        # Time to exhaustion = remaining budget / burn rate
        hours_to_exhaustion = burn_rate.budget_remaining / burn_rate.burn_rate

        if hours_to_exhaustion < 1:
            return f"{int(hours_to_exhaustion * 60)}m"
        elif hours_to_exhaustion < 24:
            return f"{hours_to_exhaustion:.1f}h"
        else:
            days = hours_to_exhaustion / 24
            return f"{days:.1f}d"

    def get_alerts(self) -> list[dict[str, Any]]:
        """Get current alerts based on burn rates and T4 compliance"""
        alerts = []

        # Check burn rate alerts
        for _key, status in self.get_burn_rate_status().items():
            if status['alert_level'] != 'ok':
                severity = 'critical' if status['alert_level'] == 'critical' else 'warning'

                alerts.append({
                    'type': 'burn_rate',
                    'severity': severity,
                    'service': status['service'],
                    'message': f"High burn rate: {status['burn_rate']:.2f}x normal",
                    'details': {
                        'burn_rate': status['burn_rate'],
                        'budget_remaining': status['budget_remaining'],
                        'exhaustion_time': status['budget_exhaustion_time']
                    }
                })

        # Check T4 compliance alerts
        for _key, compliance in self.get_t4_compliance_report().items():
            if not compliance['t4_compliant']:
                alerts.append({
                    'type': 't4_compliance',
                    'severity': 'warning',
                    'service': compliance['service'],
                    'message': f"T4 SLO violation: p95={compliance['p95_latency_ms']:.1f}ms > {compliance['slo_target_ms']:.1f}ms",
                    'details': {
                        'p95_latency_ms': compliance['p95_latency_ms'],
                        'slo_target_ms': compliance['slo_target_ms'],
                        'compliance_rate': compliance['compliance_rate']
                    }
                })

        return alerts

    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []

        for metric_name, metric_data in self.prometheus_metrics.items():
            # Add help text
            lines.append(f"# HELP {metric_name} Service metric")
            lines.append(f"# TYPE {metric_name} gauge")

            # Add labels
            label_str = ""
            if metric_data['labels']:
                label_pairs = [f'{k}="{v}"' for k, v in metric_data['labels'].items()]
                label_str = "{" + ",".join(label_pairs) + "}"

            lines.append(f"{metric_name}{label_str} {metric_data['value']}")

        return "\n".join(lines)

    def get_service_health_summary(self) -> dict[str, dict[str, Any]]:
        """Get overall health summary for all services"""
        summary = {}

        for service_type in ServiceType:
            service_metrics = self.get_service_metrics(service_type)
            compliance_data = {k: v for k, v in self.get_t4_compliance_report().items()
                             if v['service'] == service_type.value}
            burn_rates = {k: v for k, v in self.get_burn_rate_status().items()
                         if v['service'] == service_type.value}

            # Calculate overall health score
            health_score = 1.0
            issues = []

            # Check T4 compliance
            for _comp_key, comp_data in compliance_data.items():
                if not comp_data['t4_compliant']:
                    health_score *= 0.8
                    issues.append(f"T4 SLO violation: {comp_data['operation']}")

            # Check burn rates
            for _burn_key, burn_data in burn_rates.items():
                if burn_data['alert_level'] == 'critical':
                    health_score *= 0.5
                    issues.append(f"Critical burn rate: {burn_data['time_window']}")
                elif burn_data['alert_level'] == 'warning':
                    health_score *= 0.7
                    issues.append(f"High burn rate: {burn_data['time_window']}")

            summary[service_type.value] = {
                'health_score': health_score,
                'status': 'healthy' if health_score > 0.8 else 'degraded' if health_score > 0.5 else 'unhealthy',
                'metric_count': len(service_metrics),
                'compliance_checks': len(compliance_data),
                'burn_rate_monitors': len(burn_rates),
                'issues': issues,
                'last_updated': time.time()
            }

        return summary


# Global instance
_global_metrics_collector: Optional[ServiceMetricsCollector] = None


def get_metrics_collector() -> ServiceMetricsCollector:
    """Get global metrics collector instance"""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = ServiceMetricsCollector()
    return _global_metrics_collector


def record_service_operation(service: ServiceType,
                           operation: str,
                           latency_ms: float,
                           success: bool = True,
                           **labels):
    """Convenience function to record service operations"""
    collector = get_metrics_collector()
    collector.record_operation_latency(service, operation, latency_ms, success)

    # Record additional metrics
    if labels:
        collector.record_metric(
            f"{operation}_total",
            1,
            service,
            MetricType.COUNTER,
            {**labels, 'success': str(success)}
        )


def get_service_health() -> dict[str, Any]:
    """Get overall service health status"""
    collector = get_metrics_collector()
    return {
        'services': collector.get_service_health_summary(),
        't4_compliance': collector.get_t4_compliance_report(),
        'burn_rates': collector.get_burn_rate_status(),
        'active_alerts': collector.get_alerts()
    }
