#!/usr/bin/env python3
"""
LUKHAS API Analytics Dashboard & Intelligence System

Real-time API analytics, performance monitoring, and intelligent insights
for API optimization and business intelligence.

# ΛTAG: api_analytics, dashboard, intelligence, monitoring, business_insights
"""

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Optional dependencies for advanced features
try:
    import numpy as np
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class MetricType(Enum):
    """Types of metrics collected."""
    PERFORMANCE = "performance"
    USAGE = "usage"
    ERROR = "error"
    BUSINESS = "business"
    SECURITY = "security"
    RESOURCE = "resource"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TimeWindow(Enum):
    """Time windows for analytics."""
    REAL_TIME = "real_time"
    LAST_MINUTE = "last_minute"
    LAST_HOUR = "last_hour"
    LAST_DAY = "last_day"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"


@dataclass
class MetricPoint:
    """Individual metric data point."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """System alert."""
    id: str
    severity: AlertSeverity
    title: str
    description: str
    metric_type: MetricType
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BusinessInsight:
    """Business intelligence insight."""
    id: str
    title: str
    description: str
    insight_type: str
    confidence: float  # 0-1
    impact: str  # "high", "medium", "low"
    recommendation: str
    supporting_data: Dict[str, Any]
    timestamp: datetime


@dataclass
class APIEndpointMetrics:
    """Comprehensive metrics for API endpoint."""
    endpoint: str
    method: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0
    unique_users: int = 0
    data_transferred_mb: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """Collects and stores metrics data."""

    def __init__(self, max_points: int = 100000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.endpoint_metrics: Dict[str, APIEndpointMetrics] = {}
        self.user_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.system_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

    async def record_metric(self, metric_name: str, value: float,
                          labels: Dict[str, str] = None,
                          metadata: Dict[str, Any] = None):
        """Record a metric point."""
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            labels=labels or {},
            metadata=metadata or {}
        )

        self.metrics[metric_name].append(point)

    async def record_api_request(self, endpoint: str, method: str,
                                response_time: float, status_code: int,
                                user_id: Optional[str] = None,
                                request_size: int = 0, response_size: int = 0,
                                cache_hit: bool = False):
        """Record API request metrics."""
        endpoint_key = f"{method}:{endpoint}"

        # Update or create endpoint metrics
        if endpoint_key not in self.endpoint_metrics:
            self.endpoint_metrics[endpoint_key] = APIEndpointMetrics(
                endpoint=endpoint,
                method=method
            )

        metrics = self.endpoint_metrics[endpoint_key]
        metrics.total_requests += 1

        if status_code < 400:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1

        # Update response time statistics
        metrics.min_response_time = min(metrics.min_response_time, response_time)
        metrics.max_response_time = max(metrics.max_response_time, response_time)

        # Update average response time
        total_requests = metrics.total_requests
        if total_requests == 1:
            metrics.avg_response_time = response_time
        else:
            metrics.avg_response_time = (
                (metrics.avg_response_time * (total_requests - 1) + response_time) / total_requests
            )

        # Update error rate
        metrics.error_rate = (metrics.failed_requests / metrics.total_requests) * 100

        # Update data transfer
        metrics.data_transferred_mb += (request_size + response_size) / (1024 * 1024)

        # Update cache metrics
        if cache_hit:
            # Recalculate cache hit rate
            cache_hits = getattr(metrics, '_cache_hits', 0) + 1
            setattr(metrics, '_cache_hits', cache_hits)
            metrics.cache_hit_rate = (cache_hits / metrics.total_requests) * 100

        metrics.last_updated = datetime.now()

        # Record detailed metrics
        await self.record_metric(f"api.{endpoint_key}.response_time", response_time)
        await self.record_metric(f"api.{endpoint_key}.status", status_code)

        # Update user metrics
        if user_id:
            if user_id not in self.user_metrics:
                self.user_metrics[user_id] = {
                    "total_requests": 0,
                    "endpoints": set(),
                    "total_response_time": 0,
                    "first_seen": datetime.now(),
                    "last_seen": datetime.now()
                }

            user_data = self.user_metrics[user_id]
            user_data["total_requests"] += 1
            user_data["endpoints"].add(endpoint_key)
            user_data["total_response_time"] += response_time
            user_data["last_seen"] = datetime.now()

    async def get_metrics(self, metric_name: str,
                         time_window: TimeWindow = TimeWindow.LAST_HOUR) -> List[MetricPoint]:
        """Get metrics for specified time window."""
        if metric_name not in self.metrics:
            return []

        cutoff_time = self._get_cutoff_time(time_window)
        return [point for point in self.metrics[metric_name]
                if point.timestamp >= cutoff_time]

    async def get_endpoint_metrics(self, endpoint: str = None,
                                 method: str = None) -> Dict[str, APIEndpointMetrics]:
        """Get endpoint metrics."""
        if endpoint and method:
            endpoint_key = f"{method}:{endpoint}"
            return {endpoint_key: self.endpoint_metrics.get(endpoint_key)}
        elif endpoint:
            return {k: v for k, v in self.endpoint_metrics.items()
                    if v.endpoint == endpoint}
        else:
            return dict(self.endpoint_metrics)

    def _get_cutoff_time(self, time_window: TimeWindow) -> float:
        """Get cutoff timestamp for time window."""
        now = time.time()

        if time_window == TimeWindow.REAL_TIME:
            return now - 60  # Last minute
        elif time_window == TimeWindow.LAST_MINUTE:
            return now - 60
        elif time_window == TimeWindow.LAST_HOUR:
            return now - 3600
        elif time_window == TimeWindow.LAST_DAY:
            return now - 86400
        elif time_window == TimeWindow.LAST_WEEK:
            return now - 604800
        elif time_window == TimeWindow.LAST_MONTH:
            return now - 2592000
        else:
            return now - 3600


class AlertManager:
    """Manages alerts and notifications."""

    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.alert_history: deque = deque(maxlen=1000)

    def add_alert_rule(self, metric_name: str, threshold: float,
                      severity: AlertSeverity, comparison: str = "greater",
                      description: str = ""):
        """Add alert rule."""
        rule = {
            "metric_name": metric_name,
            "threshold": threshold,
            "severity": severity,
            "comparison": comparison,
            "description": description
        }
        self.alert_rules.append(rule)

    async def check_alerts(self, metrics_collector: MetricsCollector):
        """Check all alert rules against current metrics."""
        for rule in self.alert_rules:
            await self._check_rule(rule, metrics_collector)

    async def _check_rule(self, rule: Dict[str, Any], metrics_collector: MetricsCollector):
        """Check individual alert rule."""
        metric_name = rule["metric_name"]
        threshold = rule["threshold"]
        severity = rule["severity"]
        comparison = rule["comparison"]

        # Get recent metrics
        recent_metrics = await metrics_collector.get_metrics(
            metric_name, TimeWindow.LAST_MINUTE
        )

        if not recent_metrics:
            return

        # Calculate current value
        current_value = statistics.mean([point.value for point in recent_metrics])

        # Check threshold
        alert_triggered = False
        if comparison == "greater" and current_value > threshold:
            alert_triggered = True
        elif comparison == "less" and current_value < threshold:
            alert_triggered = True
        elif comparison == "equal" and abs(current_value - threshold) < 0.01:
            alert_triggered = True

        alert_id = f"{metric_name}_{threshold}_{comparison}"

        if alert_triggered:
            if alert_id not in self.alerts:
                # Create new alert
                alert = Alert(
                    id=alert_id,
                    severity=severity,
                    title=f"Alert: {metric_name}",
                    description=rule.get("description", f"{metric_name} {comparison} {threshold}"),
                    metric_type=MetricType.PERFORMANCE,
                    threshold=threshold,
                    current_value=current_value,
                    timestamp=datetime.now()
                )

                self.alerts[alert_id] = alert
                self.alert_history.append(alert)

                logger.warning(f"Alert triggered: {alert.title} - {current_value}")
        else:
            # Resolve alert if it exists
            if alert_id in self.alerts:
                alert = self.alerts[alert_id]
                alert.resolved = True
                alert.resolution_time = datetime.now()
                del self.alerts[alert_id]

                logger.info(f"Alert resolved: {alert.title}")

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.alerts.values())

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history."""
        return list(self.alert_history)[-limit:]


class IntelligenceEngine:
    """Provides intelligent insights and recommendations."""

    def __init__(self):
        self.insights_cache: Dict[str, BusinessInsight] = {}
        self.pattern_history: deque = deque(maxlen=10000)

    async def generate_insights(self, metrics_collector: MetricsCollector) -> List[BusinessInsight]:
        """Generate business insights from metrics data."""
        insights = []

        # Performance insights
        performance_insights = await self._analyze_performance(metrics_collector)
        insights.extend(performance_insights)

        # Usage pattern insights
        usage_insights = await self._analyze_usage_patterns(metrics_collector)
        insights.extend(usage_insights)

        # Error pattern insights
        error_insights = await self._analyze_error_patterns(metrics_collector)
        insights.extend(error_insights)

        # Business impact insights
        business_insights = await self._analyze_business_impact(metrics_collector)
        insights.extend(business_insights)

        return insights

    async def _analyze_performance(self, metrics_collector: MetricsCollector) -> List[BusinessInsight]:
        """Analyze performance patterns."""
        insights = []

        # Get endpoint metrics
        endpoint_metrics = await metrics_collector.get_endpoint_metrics()

        # Find slow endpoints
        slow_endpoints = [
            (key, metrics) for key, metrics in endpoint_metrics.items()
            if metrics.avg_response_time > 1000  # > 1 second
        ]

        if slow_endpoints:
            slow_endpoints.sort(key=lambda x: x[1].avg_response_time, reverse=True)
            endpoint_key, metrics = slow_endpoints[0]

            insight = BusinessInsight(
                id=f"slow_endpoint_{endpoint_key}",
                title="Slow API Endpoint Detected",
                description=f"Endpoint {metrics.endpoint} has high average response time",
                insight_type="performance",
                confidence=0.9,
                impact="high",
                recommendation=f"Consider optimizing {metrics.endpoint} - current avg: {metrics.avg_response_time:.0f}ms",
                supporting_data={
                    "endpoint": metrics.endpoint,
                    "avg_response_time": metrics.avg_response_time,
                    "total_requests": metrics.total_requests,
                    "p95_response_time": metrics.p95_response_time
                },
                timestamp=datetime.now()
            )
            insights.append(insight)

        # Find high error rate endpoints
        error_endpoints = [
            (key, metrics) for key, metrics in endpoint_metrics.items()
            if metrics.error_rate > 5  # > 5% error rate
        ]

        if error_endpoints:
            error_endpoints.sort(key=lambda x: x[1].error_rate, reverse=True)
            endpoint_key, metrics = error_endpoints[0]

            insight = BusinessInsight(
                id=f"high_error_rate_{endpoint_key}",
                title="High Error Rate Detected",
                description=f"Endpoint {metrics.endpoint} has high error rate",
                insight_type="reliability",
                confidence=0.95,
                impact="high",
                recommendation=f"Investigate and fix errors in {metrics.endpoint} - current error rate: {metrics.error_rate:.1f}%",
                supporting_data={
                    "endpoint": metrics.endpoint,
                    "error_rate": metrics.error_rate,
                    "failed_requests": metrics.failed_requests,
                    "total_requests": metrics.total_requests
                },
                timestamp=datetime.now()
            )
            insights.append(insight)

        return insights

    async def _analyze_usage_patterns(self, metrics_collector: MetricsCollector) -> List[BusinessInsight]:
        """Analyze usage patterns."""
        insights = []

        # Analyze user behavior
        user_metrics = metrics_collector.user_metrics

        if len(user_metrics) >= 10:  # Need sufficient data
            # Find power users
            power_users = sorted(
                user_metrics.items(),
                key=lambda x: x[1]["total_requests"],
                reverse=True
            )[:5]

            if power_users and power_users[0][1]["total_requests"] > 100:
                user_id, data = power_users[0]

                insight = BusinessInsight(
                    id=f"power_user_{user_id}",
                    title="Power User Identified",
                    description=f"User {user_id} is a heavy API consumer",
                    insight_type="usage",
                    confidence=0.8,
                    impact="medium",
                    recommendation="Consider reaching out to this user for feedback or upgrade opportunities",
                    supporting_data={
                        "user_id": user_id,
                        "total_requests": data["total_requests"],
                        "unique_endpoints": len(data["endpoints"]),
                        "avg_response_time": data["total_response_time"] / data["total_requests"]
                    },
                    timestamp=datetime.now()
                )
                insights.append(insight)

        # Analyze endpoint popularity
        endpoint_metrics = await metrics_collector.get_endpoint_metrics()

        if endpoint_metrics:
            popular_endpoints = sorted(
                endpoint_metrics.items(),
                key=lambda x: x[1].total_requests,
                reverse=True
            )[:3]

            most_popular = popular_endpoints[0][1]

            insight = BusinessInsight(
                id=f"popular_endpoint_{most_popular.endpoint}",
                title="Most Popular API Endpoint",
                description=f"Endpoint {most_popular.endpoint} receives the most traffic",
                insight_type="usage",
                confidence=0.9,
                impact="medium",
                recommendation="Ensure this endpoint is well-optimized and monitored",
                supporting_data={
                    "endpoint": most_popular.endpoint,
                    "total_requests": most_popular.total_requests,
                    "percentage_of_traffic": (most_popular.total_requests /
                                            sum(m.total_requests for m in endpoint_metrics.values())) * 100
                },
                timestamp=datetime.now()
            )
            insights.append(insight)

        return insights

    async def _analyze_error_patterns(self, metrics_collector: MetricsCollector) -> List[BusinessInsight]:
        """Analyze error patterns."""
        insights = []

        # Check for sudden error spikes
        error_metrics = await metrics_collector.get_metrics("api.errors", TimeWindow.LAST_HOUR)

        if len(error_metrics) > 10:
            recent_errors = [point.value for point in error_metrics[-10:]]
            older_errors = [point.value for point in error_metrics[-20:-10]] if len(error_metrics) >= 20 else []

            if older_errors:
                recent_avg = statistics.mean(recent_errors)
                older_avg = statistics.mean(older_errors)

                if recent_avg > older_avg * 2:  # 100% increase
                    insight = BusinessInsight(
                        id="error_spike_detected",
                        title="Error Spike Detected",
                        description="Recent error rate is significantly higher than usual",
                        insight_type="reliability",
                        confidence=0.85,
                        impact="high",
                        recommendation="Investigate recent changes and monitor system health",
                        supporting_data={
                            "recent_avg_errors": recent_avg,
                            "older_avg_errors": older_avg,
                            "increase_percentage": ((recent_avg - older_avg) / older_avg) * 100
                        },
                        timestamp=datetime.now()
                    )
                    insights.append(insight)

        return insights

    async def _analyze_business_impact(self, metrics_collector: MetricsCollector) -> List[BusinessInsight]:
        """Analyze business impact."""
        insights = []

        # Calculate API adoption trends
        endpoint_metrics = await metrics_collector.get_endpoint_metrics()

        if endpoint_metrics:
            total_requests = sum(m.total_requests for m in endpoint_metrics.values())
            total_data_transfer = sum(m.data_transferred_mb for m in endpoint_metrics.values())
            unique_users = len(metrics_collector.user_metrics)

            if total_requests > 1000:  # Significant usage
                insight = BusinessInsight(
                    id="api_adoption_summary",
                    title="API Adoption Summary",
                    description="API showing healthy adoption metrics",
                    insight_type="business",
                    confidence=0.9,
                    impact="medium",
                    recommendation="Continue monitoring growth trends and consider capacity planning",
                    supporting_data={
                        "total_requests": total_requests,
                        "total_data_transfer_mb": total_data_transfer,
                        "unique_users": unique_users,
                        "avg_requests_per_user": total_requests / unique_users if unique_users > 0 else 0
                    },
                    timestamp=datetime.now()
                )
                insights.append(insight)

        return insights


class AnalyticsDashboard:
    """Main analytics dashboard coordinator."""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.intelligence_engine = IntelligenceEngine()

        # Setup default alert rules
        self._setup_default_alerts()

    def _setup_default_alerts(self):
        """Setup default alert rules."""
        self.alert_manager.add_alert_rule(
            "api.response_time.avg",
            2000,  # 2 seconds
            AlertSeverity.WARNING,
            "greater",
            "Average API response time is high"
        )

        self.alert_manager.add_alert_rule(
            "api.error_rate",
            10,  # 10%
            AlertSeverity.ERROR,
            "greater",
            "API error rate is too high"
        )

        self.alert_manager.add_alert_rule(
            "api.requests_per_second",
            1000,  # 1000 RPS
            AlertSeverity.WARNING,
            "greater",
            "High API request rate detected"
        )

    async def record_api_request(self, endpoint: str, method: str,
                               response_time: float, status_code: int,
                               user_id: Optional[str] = None,
                               request_size: int = 0, response_size: int = 0,
                               cache_hit: bool = False):
        """Record API request metrics."""
        await self.metrics_collector.record_api_request(
            endpoint, method, response_time, status_code,
            user_id, request_size, response_size, cache_hit
        )

        # Record additional system metrics
        await self.metrics_collector.record_metric("api.requests_total", 1)
        await self.metrics_collector.record_metric("api.response_time.avg", response_time)

        if status_code >= 400:
            await self.metrics_collector.record_metric("api.errors", 1)
            await self.metrics_collector.record_metric("api.error_rate",
                                                     (status_code >= 400) * 100)

    async def get_dashboard_data(self, time_window: TimeWindow = TimeWindow.LAST_HOUR) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""

        # Get endpoint metrics
        endpoint_metrics = await self.metrics_collector.get_endpoint_metrics()

        # Get active alerts
        active_alerts = self.alert_manager.get_active_alerts()

        # Get insights
        insights = await self.intelligence_engine.generate_insights(self.metrics_collector)

        # Calculate summary statistics
        total_requests = sum(m.total_requests for m in endpoint_metrics.values())
        avg_response_time = statistics.mean([m.avg_response_time for m in endpoint_metrics.values()]) if endpoint_metrics else 0
        overall_error_rate = (sum(m.failed_requests for m in endpoint_metrics.values()) / total_requests * 100) if total_requests > 0 else 0
        unique_users = len(self.metrics_collector.user_metrics)

        # Get top endpoints
        top_endpoints = sorted(
            endpoint_metrics.items(),
            key=lambda x: x[1].total_requests,
            reverse=True
        )[:10]

        # Get recent metrics
        response_time_metrics = await self.metrics_collector.get_metrics(
            "api.response_time.avg", time_window
        )

        return {
            "summary": {
                "total_requests": total_requests,
                "avg_response_time_ms": avg_response_time,
                "error_rate_percent": overall_error_rate,
                "unique_users": unique_users,
                "active_alerts": len(active_alerts),
                "total_endpoints": len(endpoint_metrics)
            },
            "top_endpoints": [
                {
                    "endpoint": metrics.endpoint,
                    "method": metrics.method,
                    "requests": metrics.total_requests,
                    "avg_response_time": metrics.avg_response_time,
                    "error_rate": metrics.error_rate
                }
                for key, metrics in top_endpoints
            ],
            "alerts": [
                {
                    "id": alert.id,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "description": alert.description,
                    "current_value": alert.current_value,
                    "threshold": alert.threshold,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in active_alerts
            ],
            "insights": [
                {
                    "id": insight.id,
                    "title": insight.title,
                    "description": insight.description,
                    "type": insight.insight_type,
                    "confidence": insight.confidence,
                    "impact": insight.impact,
                    "recommendation": insight.recommendation,
                    "timestamp": insight.timestamp.isoformat()
                }
                for insight in insights[:10]  # Top 10 insights
            ],
            "performance_trend": [
                {
                    "timestamp": point.timestamp,
                    "response_time": point.value
                }
                for point in response_time_metrics[-50:]  # Last 50 points
            ],
            "time_window": time_window.value
        }

    async def get_endpoint_details(self, endpoint: str, method: str) -> Dict[str, Any]:
        """Get detailed metrics for specific endpoint."""
        endpoint_key = f"{method}:{endpoint}"
        endpoint_metrics = await self.metrics_collector.get_endpoint_metrics(endpoint, method)

        if endpoint_key not in endpoint_metrics:
            return {"error": "Endpoint not found"}

        metrics = endpoint_metrics[endpoint_key]

        # Get detailed metrics
        response_time_metrics = await self.metrics_collector.get_metrics(
            f"api.{endpoint_key}.response_time", TimeWindow.LAST_DAY
        )

        # Calculate percentiles
        if response_time_metrics:
            response_times = [point.value for point in response_time_metrics]
            response_times.sort()
            n = len(response_times)

            p50 = response_times[int(n * 0.5)] if n > 0 else 0
            p95 = response_times[int(n * 0.95)] if n > 0 else 0
            p99 = response_times[int(n * 0.99)] if n > 0 else 0
        else:
            p50 = p95 = p99 = 0

        return {
            "endpoint": endpoint,
            "method": method,
            "metrics": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "avg_response_time": metrics.avg_response_time,
                "min_response_time": metrics.min_response_time,
                "max_response_time": metrics.max_response_time,
                "p50_response_time": p50,
                "p95_response_time": p95,
                "p99_response_time": p99,
                "error_rate": metrics.error_rate,
                "cache_hit_rate": metrics.cache_hit_rate,
                "data_transferred_mb": metrics.data_transferred_mb
            },
            "performance_trend": [
                {
                    "timestamp": point.timestamp,
                    "response_time": point.value
                }
                for point in response_time_metrics[-100:]  # Last 100 points
            ]
        }

    async def run_analytics_loop(self, interval_seconds: int = 60):
        """Run continuous analytics processing."""
        while True:
            try:
                # Check alerts
                await self.alert_manager.check_alerts(self.metrics_collector)

                # Generate insights (less frequently)
                if int(time.time()) % (interval_seconds * 5) == 0:  # Every 5 intervals
                    await self.intelligence_engine.generate_insights(self.metrics_collector)

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"Analytics loop error: {e}")
                await asyncio.sleep(interval_seconds)


# Factory function
async def create_analytics_dashboard() -> AnalyticsDashboard:
    """Create analytics dashboard."""
    dashboard = AnalyticsDashboard()
    logger.info("Analytics dashboard created")
    return dashboard


if __name__ == "__main__":
    async def test_analytics_dashboard():
        """Test the analytics dashboard."""
        dashboard = await create_analytics_dashboard()

        # Simulate some API requests
        for i in range(100):
            await dashboard.record_api_request(
                endpoint=f"/api/v1/endpoint{i % 5}",
                method="GET",
                response_time=50 + (i % 10) * 20,  # Varying response times
                status_code=200 if i % 20 != 0 else 404,  # 5% error rate
                user_id=f"user_{i % 10}",
                request_size=1024,
                response_size=2048,
                cache_hit=(i % 3 == 0)  # 33% cache hit rate
            )

        # Get dashboard data
        dashboard_data = await dashboard.get_dashboard_data()

        print("📊 Dashboard Summary:")
        print(f"  Total Requests: {dashboard_data['summary']['total_requests']}")
        print(f"  Avg Response Time: {dashboard_data['summary']['avg_response_time_ms']:.1f}ms")
        print(f"  Error Rate: {dashboard_data['summary']['error_rate_percent']:.1f}%")
        print(f"  Unique Users: {dashboard_data['summary']['unique_users']}")
        print(f"  Active Alerts: {dashboard_data['summary']['active_alerts']}")

        print("\n🔝 Top Endpoints:")
        for endpoint in dashboard_data['top_endpoints'][:3]:
            print(f"  {endpoint['method']} {endpoint['endpoint']}: {endpoint['requests']} requests")

        print("\n💡 Insights:")
        for insight in dashboard_data['insights'][:3]:
            print(f"  {insight['title']}: {insight['description']}")

        if dashboard_data['alerts']:
            print("\n🚨 Active Alerts:")
            for alert in dashboard_data['alerts']:
                print(f"  {alert['severity'].upper()}: {alert['title']}")

    asyncio.run(test_analytics_dashboard())
