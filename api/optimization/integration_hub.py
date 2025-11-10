#!/usr/bin/env python3
"""
LUKHAS API Optimization Integration Hub

Unified integration system that coordinates all API optimization components:
- Advanced API Optimizer
- Middleware Pipeline
- Analytics Dashboard
- Performance Monitoring
- Intelligent Insights

# ΛTAG: api_integration, optimization_hub, unified_coordination, intelligent_api
"""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Import our optimization components
try:
    from .advanced_api_optimizer import (
        APITier,
        LUKHASAPIOptimizer,
        OptimizationStrategy,
        RequestContext,
        RequestPriority,
        create_api_optimizer,
    )
    from .advanced_middleware import (
        LUKHASMiddlewarePipeline,
        MiddlewareConfig,
        RequestMetadata,
        create_middleware_pipeline,
    )
    from .analytics_dashboard import AnalyticsDashboard, create_analytics_dashboard
    OPTIMIZATION_COMPONENTS_AVAILABLE = True
except ImportError:
    OPTIMIZATION_COMPONENTS_AVAILABLE = False

# Security framework integration
try:
    from security.security_framework import LUKHASSecurityFramework
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Cache system integration
try:
    from caching.cache_system import HierarchicalCacheManager
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False


class IntegrationMode(Enum):
    """API optimization integration modes."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    HIGH_PERFORMANCE = "high_performance"
    RESOURCE_CONSERVATIVE = "resource_conservative"


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNAVAILABLE = "unavailable"


@dataclass
class IntegrationConfig:
    """Configuration for API optimization integration."""
    mode: IntegrationMode = IntegrationMode.PRODUCTION
    enable_optimizer: bool = True
    enable_middleware: bool = True
    enable_analytics: bool = True
    enable_security_integration: bool = True
    enable_cache_integration: bool = True
    enable_auto_scaling: bool = True
    enable_intelligent_routing: bool = True
    enable_predictive_caching: bool = True
    enable_adaptive_rate_limiting: bool = True
    health_check_interval_seconds: int = 60
    metrics_retention_hours: int = 24
    auto_optimization_enabled: bool = True
    redis_url: Optional[str] = None
    monitoring_dashboard_url: Optional[str] = None


@dataclass
class APIPerformanceMetrics:
    """Comprehensive API performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    error_rate_percent: float = 0.0
    cache_hit_rate_percent: float = 0.0
    throughput_rps: float = 0.0
    active_connections: int = 0
    rate_limit_violations: int = 0
    security_threats_blocked: int = 0
    optimization_effectiveness: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: HealthStatus
    score: float  # 0-100
    components: Dict[str, HealthStatus] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    last_check: datetime = field(default_factory=datetime.now)


class IntelligentRoutingEngine:
    """Intelligent request routing based on performance patterns."""

    def __init__(self):
        self.endpoint_performance = {}
        self.routing_rules = []
        self.adaptive_rules = {}

    async def route_request(self, context: RequestContext) -> Dict[str, Any]:
        """Intelligently route request based on patterns."""
        endpoint_key = f"{context.method}:{context.endpoint}"

        # Get endpoint performance history
        performance = self.endpoint_performance.get(endpoint_key, {})

        routing_decision = {
            "route": "default",
            "priority": context.priority,
            "optimizations": [],
            "estimated_response_time": performance.get("avg_response_time", 100)
        }

        # Apply intelligent routing rules
        if performance.get("avg_response_time", 0) > 1000:  # Slow endpoint
            routing_decision["optimizations"].append("aggressive_cache")
            routing_decision["priority"] = RequestPriority.HIGH

        if performance.get("error_rate", 0) > 10:  # High error rate
            routing_decision["optimizations"].append("retry_logic")
            routing_decision["optimizations"].append("circuit_breaker")

        # User tier-based routing
        if context.tier in [APITier.ENTERPRISE, APITier.PREMIUM]:
            routing_decision["route"] = "priority_queue"
            routing_decision["optimizations"].append("dedicated_resources")

        return routing_decision

    async def update_performance_data(self, endpoint: str, method: str,
                                    response_time: float, error_rate: float):
        """Update endpoint performance data for routing decisions."""
        endpoint_key = f"{method}:{endpoint}"

        if endpoint_key not in self.endpoint_performance:
            self.endpoint_performance[endpoint_key] = {
                "avg_response_time": response_time,
                "error_rate": error_rate,
                "request_count": 1
            }
        else:
            perf = self.endpoint_performance[endpoint_key]
            count = perf["request_count"]

            # Update rolling average
            perf["avg_response_time"] = (
                (perf["avg_response_time"] * count + response_time) / (count + 1)
            )
            perf["error_rate"] = (
                (perf["error_rate"] * count + error_rate) / (count + 1)
            )
            perf["request_count"] = count + 1


class PredictiveCacheManager:
    """Predictive caching based on usage patterns and ML."""

    def __init__(self):
        self.access_patterns = {}
        self.cache_predictions = {}
        self.effectiveness_scores = {}

    async def predict_cache_needs(self, context: RequestContext) -> Dict[str, Any]:
        """Predict if request should be cached and for how long."""
        endpoint_key = f"{context.method}:{context.endpoint}"

        # Analyze access patterns
        patterns = self.access_patterns.get(endpoint_key, {})

        prediction = {
            "should_cache": False,
            "ttl_seconds": 300,
            "cache_priority": "normal",
            "prefetch_related": []
        }

        # Pattern-based predictions
        if patterns.get("access_frequency", 0) > 10:  # Frequently accessed
            prediction["should_cache"] = True
            prediction["cache_priority"] = "high"

        if patterns.get("temporal_pattern") == "predictable":
            prediction["ttl_seconds"] = 3600  # Longer TTL for predictable patterns
            prediction["prefetch_related"] = self._get_related_endpoints(endpoint_key)

        # User-specific caching
        if context.user_id and patterns.get("user_specific", False):
            prediction["should_cache"] = True
            prediction["ttl_seconds"] = 1800  # 30 minutes for user-specific data

        return prediction

    async def update_access_pattern(self, endpoint: str, method: str,
                                  user_id: Optional[str] = None):
        """Update access patterns for predictive caching."""
        endpoint_key = f"{method}:{endpoint}"
        timestamp = time.time()

        if endpoint_key not in self.access_patterns:
            self.access_patterns[endpoint_key] = {
                "access_frequency": 0,
                "last_access": timestamp,
                "access_times": [],
                "user_specific": False
            }

        pattern = self.access_patterns[endpoint_key]
        pattern["access_frequency"] += 1
        pattern["last_access"] = timestamp
        pattern["access_times"].append(timestamp)

        # Keep only recent access times (last hour)
        recent_threshold = timestamp - 3600
        pattern["access_times"] = [
            t for t in pattern["access_times"] if t > recent_threshold
        ]

        # Detect if endpoint is user-specific
        if user_id:
            pattern["user_specific"] = True

        # Analyze temporal patterns
        if len(pattern["access_times"]) > 5:
            intervals = [
                pattern["access_times"][i] - pattern["access_times"][i-1]
                for i in range(1, len(pattern["access_times"]))
            ]
            avg_interval = sum(intervals) / len(intervals)

            if avg_interval < 300:  # Less than 5 minutes
                pattern["temporal_pattern"] = "frequent"
            elif avg_interval < 3600:  # Less than 1 hour
                pattern["temporal_pattern"] = "regular"
            else:
                pattern["temporal_pattern"] = "sporadic"

    def _get_related_endpoints(self, endpoint_key: str) -> List[str]:
        """Get related endpoints for prefetching."""
        # Simple related endpoint detection
        # In production, this would use more sophisticated ML
        related = []

        if "/users/" in endpoint_key:
            related.extend(["/users/profile", "/users/settings"])
        elif "/products/" in endpoint_key:
            related.extend(["/products/categories", "/products/recommendations"])
        elif "/orders/" in endpoint_key:
            related.extend(["/orders/history", "/payments/status"])

        return related


class AutoScalingManager:
    """Automatic scaling based on performance metrics."""

    def __init__(self):
        self.scaling_history = []
        self.current_capacity = 1.0
        self.scaling_rules = {
            "scale_up_threshold": 0.8,    # Scale up at 80% capacity
            "scale_down_threshold": 0.3,  # Scale down at 30% capacity
            "max_capacity": 10.0,         # Maximum 10x scaling
            "min_capacity": 0.5,          # Minimum 0.5x scaling
            "cooldown_minutes": 5         # 5 minute cooldown
        }

    async def evaluate_scaling(self, metrics: APIPerformanceMetrics) -> Dict[str, Any]:
        """Evaluate if scaling is needed."""
        current_load = self._calculate_load_factor(metrics)

        decision = {
            "action": "none",
            "current_capacity": self.current_capacity,
            "recommended_capacity": self.current_capacity,
            "reason": "No scaling needed",
            "load_factor": current_load
        }

        # Check if cooldown period has passed
        if self._in_cooldown():
            decision["reason"] = "In cooldown period"
            return decision

        # Scale up decision
        if current_load > self.scaling_rules["scale_up_threshold"]:
            new_capacity = min(
                self.current_capacity * 1.5,
                self.scaling_rules["max_capacity"]
            )
            if new_capacity > self.current_capacity:
                decision.update({
                    "action": "scale_up",
                    "recommended_capacity": new_capacity,
                    "reason": f"High load detected: {current_load:.2f}"
                })

        # Scale down decision
        elif current_load < self.scaling_rules["scale_down_threshold"]:
            new_capacity = max(
                self.current_capacity * 0.7,
                self.scaling_rules["min_capacity"]
            )
            if new_capacity < self.current_capacity:
                decision.update({
                    "action": "scale_down",
                    "recommended_capacity": new_capacity,
                    "reason": f"Low load detected: {current_load:.2f}"
                })

        return decision

    async def apply_scaling(self, new_capacity: float) -> bool:
        """Apply scaling decision."""
        try:
            # Record scaling event
            self.scaling_history.append({
                "timestamp": time.time(),
                "old_capacity": self.current_capacity,
                "new_capacity": new_capacity,
                "action": "scale_up" if new_capacity > self.current_capacity else "scale_down"
            })

            self.current_capacity = new_capacity

            logger.info(f"Scaled API capacity to {new_capacity:.2f}x")
            return True

        except Exception as e:
            logger.error(f"Failed to apply scaling: {e}")
            return False

    def _calculate_load_factor(self, metrics: APIPerformanceMetrics) -> float:
        """Calculate current load factor (0-1)."""
        # Combine multiple metrics to calculate load
        response_time_factor = min(metrics.avg_response_time_ms / 1000, 1.0)  # Normalize to 1s
        error_rate_factor = metrics.error_rate_percent / 100
        throughput_factor = min(metrics.throughput_rps / 1000, 1.0)  # Normalize to 1000 RPS

        # Weighted average
        load_factor = (
            response_time_factor * 0.4 +
            error_rate_factor * 0.3 +
            throughput_factor * 0.3
        )

        return min(load_factor, 1.0)

    def _in_cooldown(self) -> bool:
        """Check if we're in cooldown period."""
        if not self.scaling_history:
            return False

        last_scaling = self.scaling_history[-1]
        cooldown_seconds = self.scaling_rules["cooldown_minutes"] * 60

        return time.time() - last_scaling["timestamp"] < cooldown_seconds


class LUKHASAPIOptimizationHub:
    """Main integration hub for all API optimization components."""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.optimizer: Optional[LUKHASAPIOptimizer] = None
        self.middleware_pipeline: Optional[LUKHASMiddlewarePipeline] = None
        self.analytics_dashboard: Optional[AnalyticsDashboard] = None
        self.security_framework: Optional[LUKHASSecurityFramework] = None
        self.cache_manager: Optional[HierarchicalCacheManager] = None

        # Advanced components
        self.routing_engine = IntelligentRoutingEngine()
        self.predictive_cache = PredictiveCacheManager()
        self.auto_scaler = AutoScalingManager()

        # State tracking
        self.system_health = SystemHealth(status=HealthStatus.UNAVAILABLE, score=0)
        self.performance_metrics = APIPerformanceMetrics()
        self.is_initialized = False
        self.health_check_task: Optional[asyncio.Task] = None

    async def initialize(self):
        """Initialize all optimization components."""
        logger.info("Initializing LUKHAS API Optimization Hub...")

        try:
            # Initialize core components based on config
            if self.config.enable_optimizer and OPTIMIZATION_COMPONENTS_AVAILABLE:
                await self._initialize_optimizer()

            if self.config.enable_middleware and OPTIMIZATION_COMPONENTS_AVAILABLE:
                await self._initialize_middleware()

            if self.config.enable_analytics and OPTIMIZATION_COMPONENTS_AVAILABLE:
                await self._initialize_analytics()

            if self.config.enable_security_integration and SECURITY_AVAILABLE:
                await self._initialize_security()

            if self.config.enable_cache_integration and CACHE_AVAILABLE:
                await self._initialize_cache()

            # Start health monitoring
            if self.config.health_check_interval_seconds > 0:
                self.health_check_task = asyncio.create_task(self._health_check_loop())

            self.is_initialized = True
            self.system_health.status = HealthStatus.HEALTHY
            self.system_health.score = 100.0

            logger.info("✅ API Optimization Hub initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize API Optimization Hub: {e}")
            self.system_health.status = HealthStatus.CRITICAL
            self.system_health.issues.append(f"Initialization failed: {e}")
            raise

    async def _initialize_optimizer(self):
        """Initialize API optimizer."""
        optimization_strategy = {
            IntegrationMode.DEVELOPMENT: OptimizationStrategy.BALANCED,
            IntegrationMode.TESTING: OptimizationStrategy.BALANCED,
            IntegrationMode.PRODUCTION: OptimizationStrategy.LOW_LATENCY,
            IntegrationMode.HIGH_PERFORMANCE: OptimizationStrategy.AGGRESSIVE_CACHE,
            IntegrationMode.RESOURCE_CONSERVATIVE: OptimizationStrategy.RESOURCE_CONSERVATION
        }.get(self.config.mode, OptimizationStrategy.BALANCED)

        self.optimizer = await create_api_optimizer(
            strategy=optimization_strategy,
            redis_url=self.config.redis_url
        )

        logger.info(f"API optimizer initialized with {optimization_strategy.value} strategy")

    async def _initialize_middleware(self):
        """Initialize middleware pipeline."""
        middleware_config = MiddlewareConfig(
            enable_security=self.config.enable_security_integration,
            enable_optimization=self.config.enable_optimizer,
            enable_analytics=self.config.enable_analytics,
            enable_request_validation=True,
            enable_compression=True,
            max_request_size_mb=100.0 if self.config.mode == IntegrationMode.PRODUCTION else 10.0
        )

        self.middleware_pipeline = await create_middleware_pipeline(
            config=middleware_config,
            security_framework=self.security_framework,
            optimizer=self.optimizer
        )

        logger.info("Middleware pipeline initialized")

    async def _initialize_analytics(self):
        """Initialize analytics dashboard."""
        self.analytics_dashboard = await create_analytics_dashboard()
        logger.info("Analytics dashboard initialized")

    async def _initialize_security(self):
        """Initialize security framework."""
        # This would be implemented based on security framework availability
        logger.info("Security framework integration initialized")

    async def _initialize_cache(self):
        """Initialize cache manager."""
        # This would be implemented based on cache system availability
        logger.info("Cache manager integration initialized")

    async def process_api_request(self, endpoint: str, method: str,
                                headers: Optional[Dict[str, str]] = None,
                                params: Optional[Dict[str, Any]] = None,
                                user_id: Optional[str] = None,
                                api_key: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Process API request through optimization pipeline."""
        if not self.is_initialized:
            return False, {"error": "Optimization hub not initialized", "status": 503}

        start_time = time.time()
        request_id = f"req_{int(time.time() * 1000)}_{id(params)}"

        try:
            # Create request context
            context = RequestContext(
                request_id=request_id,
                endpoint=endpoint,
                method=method,
                user_id=user_id,
                api_key=api_key,
                tier=self._determine_user_tier(user_id, api_key),
                priority=RequestPriority.NORMAL,
                headers=headers or {},
                params=params or {}
            )

            # Create request metadata
            metadata = RequestMetadata(
                request_id=request_id,
                start_time=start_time,
                client_ip="unknown",  # Would be extracted from actual request
                user_agent=headers.get("user-agent", "") if headers else "",
                endpoint=endpoint,
                method=method,
                custom_headers=headers or {}
            )

            # Intelligent routing
            if self.config.enable_intelligent_routing:
                routing_decision = await self.routing_engine.route_request(context)
                context.priority = routing_decision["priority"]
                metadata.middleware_data["routing"] = routing_decision

            # Predictive caching
            if self.config.enable_predictive_caching:
                cache_prediction = await self.predictive_cache.predict_cache_needs(context)
                metadata.middleware_data["cache_prediction"] = cache_prediction

            # Process through optimizer
            optimizer_result = {"allowed": True, "info": {}}
            if self.optimizer:
                optimizer_allowed, optimizer_info = await self.optimizer.process_request(context)
                optimizer_result = {"allowed": optimizer_allowed, "info": optimizer_info}

                if not optimizer_allowed:
                    await self._record_request_metrics(context, 0, 429, False)
                    return False, {
                        "error": "Request blocked by optimizer",
                        "details": optimizer_info,
                        "status": 429
                    }

            # Process through middleware pipeline
            middleware_result = {"allowed": True, "data": {}}
            if self.middleware_pipeline:
                middleware_allowed, middleware_data = await self.middleware_pipeline.process_request(
                    metadata, params or {}
                )
                middleware_result = {"allowed": middleware_allowed, "data": middleware_data}

                if not middleware_allowed:
                    await self._record_request_metrics(context, 0, 400, False)
                    return False, middleware_data

            # Check for cached response
            if optimizer_result["info"].get("cached"):
                cached_response = optimizer_result["info"]["data"]
                processing_time = (time.time() - start_time) * 1000

                await self._record_request_metrics(context, processing_time, 200, True)

                return True, {
                    "cached": True,
                    "data": cached_response,
                    "processing_time_ms": processing_time,
                    "optimizations_applied": self._get_applied_optimizations(
                        optimizer_result, middleware_result
                    )
                }

            # Request is allowed to proceed
            processing_time = (time.time() - start_time) * 1000
            await self._record_request_metrics(context, processing_time, 200, False)

            return True, {
                "request_id": request_id,
                "processing_time_ms": processing_time,
                "optimizer_info": optimizer_result["info"],
                "middleware_data": middleware_result["data"],
                "optimizations_applied": self._get_applied_optimizations(
                    optimizer_result, middleware_result
                )
            }

        except Exception as e:
            logger.error(f"Error processing API request: {e}")
            error_time = (time.time() - start_time) * 1000

            # Record error metrics
            if hasattr(self, '_record_request_metrics'):
                await self._record_request_metrics(
                    RequestContext(request_id=request_id, endpoint=endpoint, method=method),
                    error_time, 500, False
                )

            return False, {
                "error": "Internal optimization error",
                "status": 500,
                "processing_time_ms": error_time
            }

    async def complete_api_request(self, request_id: str, response_data: Dict[str, Any],
                                 status_code: int):
        """Complete API request processing."""
        try:
            # Update optimizer
            if self.optimizer and hasattr(self.optimizer, 'active_requests'):
                for context in self.optimizer.active_requests.values():
                    if context.request_id == request_id:
                        await self.optimizer.complete_request(context, response_data, status_code)
                        break

            # Update analytics
            if self.analytics_dashboard:
                await self.analytics_dashboard.record_api_request(
                    endpoint="unknown",  # Would be stored in request tracking
                    method="GET",        # Would be stored in request tracking
                    response_time=0,     # Would be calculated from stored start time
                    status_code=status_code,
                    user_id=None,        # Would be extracted from request context
                    response_size=len(json.dumps(response_data))
                )

        except Exception as e:
            logger.error(f"Error completing API request {request_id}: {e}")

    async def get_optimization_status(self) -> Dict[str, Any]:
        """Get comprehensive optimization status."""
        status = {
            "hub": {
                "initialized": self.is_initialized,
                "mode": self.config.mode.value,
                "health": {
                    "status": self.system_health.status.value,
                    "score": self.system_health.score,
                    "issues": self.system_health.issues,
                    "recommendations": self.system_health.recommendations
                }
            },
            "components": {},
            "performance": self._get_performance_summary(),
            "intelligent_features": {
                "routing_enabled": self.config.enable_intelligent_routing,
                "predictive_caching_enabled": self.config.enable_predictive_caching,
                "auto_scaling_enabled": self.config.enable_auto_scaling,
                "adaptive_rate_limiting_enabled": self.config.enable_adaptive_rate_limiting
            }
        }

        # Get component statuses
        if self.optimizer:
            status["components"]["optimizer"] = await self.optimizer.get_optimization_stats()

        if self.middleware_pipeline:
            status["components"]["middleware"] = self.middleware_pipeline.get_pipeline_stats()

        if self.analytics_dashboard:
            status["components"]["analytics"] = await self.analytics_dashboard.get_dashboard_data()

        # Auto-scaling status
        if self.config.enable_auto_scaling:
            scaling_decision = await self.auto_scaler.evaluate_scaling(self.performance_metrics)
            status["auto_scaling"] = {
                "current_capacity": self.auto_scaler.current_capacity,
                "scaling_decision": scaling_decision,
                "scaling_history": self.auto_scaler.scaling_history[-5:]  # Last 5 events
            }

        return status

    async def _record_request_metrics(self, context: RequestContext,
                                    response_time_ms: float, status_code: int,
                                    cache_hit: bool):
        """Record request metrics across all systems."""

        # Update performance metrics
        self.performance_metrics.total_requests += 1

        if status_code < 400:
            self.performance_metrics.successful_requests += 1
        else:
            self.performance_metrics.failed_requests += 1

        # Update response time
        if self.performance_metrics.total_requests == 1:
            self.performance_metrics.avg_response_time_ms = response_time_ms
        else:
            total = self.performance_metrics.total_requests
            current_avg = self.performance_metrics.avg_response_time_ms
            self.performance_metrics.avg_response_time_ms = (
                (current_avg * (total - 1) + response_time_ms) / total
            )

        # Update error rate
        self.performance_metrics.error_rate_percent = (
            self.performance_metrics.failed_requests /
            self.performance_metrics.total_requests * 100
        )

        # Update cache hit rate
        if cache_hit:
            cache_hits = getattr(self.performance_metrics, '_cache_hits', 0) + 1
            self.performance_metrics._cache_hits = cache_hits
            self.performance_metrics.cache_hit_rate_percent = (
                cache_hits / self.performance_metrics.total_requests * 100
            )

        # Update routing engine
        if self.config.enable_intelligent_routing:
            await self.routing_engine.update_performance_data(
                context.endpoint, context.method, response_time_ms,
                100 if status_code >= 400 else 0
            )

        # Update predictive cache
        if self.config.enable_predictive_caching:
            await self.predictive_cache.update_access_pattern(
                context.endpoint, context.method, context.user_id
            )

    async def _health_check_loop(self):
        """Continuous health monitoring loop."""
        while True:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config.health_check_interval_seconds)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(self.config.health_check_interval_seconds)

    async def _perform_health_check(self):
        """Perform comprehensive health check."""
        health_score = 100.0
        issues = []
        recommendations = []
        component_health = {}

        # Check optimizer health
        if self.optimizer:
            optimizer_healthy = True  # Would implement actual health check
            component_health["optimizer"] = HealthStatus.HEALTHY if optimizer_healthy else HealthStatus.DEGRADED
            if not optimizer_healthy:
                health_score -= 20
                issues.append("API optimizer degraded")

        # Check middleware health
        if self.middleware_pipeline:
            middleware_stats = self.middleware_pipeline.get_pipeline_stats()
            error_rate = (
                middleware_stats["pipeline"].get("error_requests", 0) /
                max(middleware_stats["pipeline"].get("total_requests", 1), 1) * 100
            )

            if error_rate > 10:
                component_health["middleware"] = HealthStatus.DEGRADED
                health_score -= 15
                issues.append(f"High middleware error rate: {error_rate:.1f}%")
            else:
                component_health["middleware"] = HealthStatus.HEALTHY

        # Check performance metrics
        if self.performance_metrics.avg_response_time_ms > 2000:
            health_score -= 20
            issues.append("High average response time")
            recommendations.append("Consider scaling up or optimizing slow endpoints")

        if self.performance_metrics.error_rate_percent > 5:
            health_score -= 25
            issues.append("High error rate")
            recommendations.append("Investigate error patterns and fix underlying issues")

        # Auto-scaling evaluation
        if self.config.enable_auto_scaling:
            scaling_decision = await self.auto_scaler.evaluate_scaling(self.performance_metrics)
            if scaling_decision["action"] != "none":
                recommendations.append(f"Auto-scaling recommendation: {scaling_decision['action']}")

                # Apply auto-scaling if enabled
                if self.config.auto_optimization_enabled:
                    success = await self.auto_scaler.apply_scaling(
                        scaling_decision["recommended_capacity"]
                    )
                    if success:
                        recommendations.append("Auto-scaling applied successfully")

        # Update system health
        if health_score >= 90:
            status = HealthStatus.HEALTHY
        elif health_score >= 70:
            status = HealthStatus.WARNING
        elif health_score >= 40:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.CRITICAL

        self.system_health = SystemHealth(
            status=status,
            score=health_score,
            components=component_health,
            issues=issues,
            recommendations=recommendations,
            last_check=datetime.now()
        )

    def _determine_user_tier(self, user_id: Optional[str], api_key: Optional[str]) -> APITier:
        """Determine user tier from credentials."""
        if api_key:
            if api_key.startswith("ent_"):
                return APITier.ENTERPRISE
            elif api_key.startswith("pre_"):
                return APITier.PREMIUM
            elif api_key.startswith("bas_"):
                return APITier.BASIC

        return APITier.FREE

    def _get_applied_optimizations(self, optimizer_result: Dict,
                                 middleware_result: Dict) -> List[str]:
        """Get list of applied optimizations."""
        optimizations = []

        if optimizer_result.get("info", {}).get("cached"):
            optimizations.append("response_cached")

        if "rate_limit_info" in optimizer_result.get("info", {}):
            optimizations.append("rate_limiting")

        if middleware_result.get("data", {}).get("security_context"):
            optimizations.append("security_validation")

        if middleware_result.get("data", {}).get("sanitized_data"):
            optimizations.append("input_sanitization")

        return optimizations

    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        return {
            "total_requests": self.performance_metrics.total_requests,
            "avg_response_time_ms": self.performance_metrics.avg_response_time_ms,
            "error_rate_percent": self.performance_metrics.error_rate_percent,
            "cache_hit_rate_percent": self.performance_metrics.cache_hit_rate_percent,
            "throughput_rps": self.performance_metrics.throughput_rps,
            "optimization_effectiveness": self.performance_metrics.optimization_effectiveness,
            "last_updated": self.performance_metrics.last_updated.isoformat()
        }

    async def shutdown(self):
        """Gracefully shutdown optimization hub."""
        logger.info("Shutting down API Optimization Hub...")

        # Cancel health check task
        if self.health_check_task:
            self.health_check_task.cancel()
            with suppress(asyncio.CancelledError):
                await self.health_check_task

        # Shutdown components
        if self.optimizer and hasattr(self.optimizer, 'cleanup'):
            await self.optimizer.cleanup()

        if self.middleware_pipeline and hasattr(self.middleware_pipeline, 'shutdown'):
            await self.middleware_pipeline.shutdown()

        self.is_initialized = False
        logger.info("✅ API Optimization Hub shutdown complete")


# Factory function
async def create_optimization_hub(config: IntegrationConfig = None) -> LUKHASAPIOptimizationHub:
    """Create and initialize API optimization hub."""
    if config is None:
        config = IntegrationConfig()

    hub = LUKHASAPIOptimizationHub(config)
    await hub.initialize()

    return hub


# Context manager for request processing
@asynccontextmanager
async def optimized_api_processing(hub: LUKHASAPIOptimizationHub,
                                 endpoint: str, method: str,
                                 **kwargs):
    """Context manager for optimized API request processing."""

    # Pre-processing
    allowed, info = await hub.process_api_request(endpoint, method, **kwargs)

    if not allowed:
        yield False, info
        return

    info.get("request_id")

    try:
        yield True, info
    finally:
        # Post-processing would be handled by complete_api_request
        pass


if __name__ == "__main__":
    async def test_optimization_hub():
        """Test the optimization hub."""

        # Create configuration
        config = IntegrationConfig(
            mode=IntegrationMode.DEVELOPMENT,
            enable_intelligent_routing=True,
            enable_predictive_caching=True,
            enable_auto_scaling=True
        )

        # Create and initialize hub
        hub = await create_optimization_hub(config)

        try:
            # Test API request processing
            async with optimized_api_processing(
                hub, "/api/v1/test", "GET",
                headers={"Authorization": "Bearer test_token"},
                params={"page": 1, "limit": 10},
                user_id="test_user"
            ) as (allowed, result):

                if allowed:
                    print("✅ Request processed successfully")
                    print(f"📊 Processing time: {result.get('processing_time_ms', 0):.1f}ms")
                    print(f"🎯 Optimizations: {result.get('optimizations_applied', [])}")

                    # Simulate API response
                    await hub.complete_api_request(
                        result["request_id"],
                        {"data": "test response", "success": True},
                        200
                    )
                else:
                    print(f"❌ Request blocked: {result}")

            # Get optimization status
            status = await hub.get_optimization_status()
            print(f"\n📈 System Status: {status['hub']['health']['status']}")
            print(f"🎯 Health Score: {status['hub']['health']['score']:.1f}")

            if status['hub']['health']['recommendations']:
                print("💡 Recommendations:")
                for rec in status['hub']['health']['recommendations']:
                    print(f"  - {rec}")

        finally:
            await hub.shutdown()

    asyncio.run(test_optimization_hub())
