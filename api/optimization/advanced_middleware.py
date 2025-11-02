#!/usr/bin/env python3
"""
LUKHAS Advanced API Middleware System

Intelligent middleware stack with request optimization, security integration,
analytics, and adaptive performance tuning.

# ΛTAG: api_middleware, request_processing, security_integration, performance_tuning
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
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
        OptimizationConfig,
        OptimizationStrategy,
        RequestContext,
        RequestPriority,
    )

    OPTIMIZER_AVAILABLE = True
except ImportError:
    OPTIMIZER_AVAILABLE = False

# FastAPI integration
try:
    from fastapi import HTTPException, Request, Response
    from fastapi.middleware.base import BaseHTTPMiddleware
    from starlette.middleware.base import RequestResponseEndpoint

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Security integration
try:
    from security.security_framework import LUKHASSecurityFramework

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False


class MiddlewareType(Enum):
    """Types of middleware in the processing pipeline."""

    SECURITY = "security"
    RATE_LIMITING = "rate_limiting"
    OPTIMIZATION = "optimization"
    ANALYTICS = "analytics"
    COMPRESSION = "compression"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    LOGGING = "logging"


class ProcessingPhase(Enum):
    """Request processing phases."""

    PRE_PROCESSING = "pre_processing"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMITING = "rate_limiting"
    OPTIMIZATION = "optimization"
    PROCESSING = "processing"
    POST_PROCESSING = "post_processing"
    RESPONSE_TRANSFORMATION = "response_transformation"
    LOGGING = "logging"


@dataclass
class MiddlewareConfig:
    """Configuration for middleware pipeline."""

    enable_security: bool = True
    enable_rate_limiting: bool = True
    enable_optimization: bool = True
    enable_analytics: bool = True
    enable_compression: bool = True
    enable_request_validation: bool = True
    enable_response_transformation: bool = True
    enable_detailed_logging: bool = True
    max_request_size_mb: float = 100.0
    request_timeout_seconds: float = 30.0
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    enable_metrics: bool = True


@dataclass
class RequestMetadata:
    """Enhanced request metadata for middleware processing."""

    request_id: str
    start_time: float
    client_ip: str
    user_agent: str
    endpoint: str
    method: str
    content_type: Optional[str] = None
    content_length: int = 0
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    tier: APITier = APITier.FREE
    priority: RequestPriority = RequestPriority.NORMAL
    security_context: Dict[str, Any] = field(default_factory=dict)
    optimization_context: Dict[str, Any] = field(default_factory=dict)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    processing_phases: List[str] = field(default_factory=list)
    middleware_data: Dict[str, Any] = field(default_factory=dict)


class BaseMiddleware(ABC):
    """Base class for all middleware components."""

    def __init__(self, name: str, middleware_type: MiddlewareType, config: Dict[str, Any] = None):
        self.name = name
        self.middleware_type = middleware_type
        self.config = config or {}
        self.enabled = True
        self.metrics = {"requests_processed": 0, "requests_blocked": 0, "processing_time_ms": 0, "errors": 0}

    @abstractmethod
    async def process_request(
        self, metadata: RequestMetadata, request_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process incoming request. Returns (continue, data)."""
        pass

    @abstractmethod
    async def process_response(self, metadata: RequestMetadata, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process outgoing response."""
        pass

    async def on_error(self, metadata: RequestMetadata, error: Exception) -> Dict[str, Any]:
        """Handle errors during processing."""
        self.metrics["errors"] += 1
        return {"error": f"Middleware {self.name} error: {str(error)}", "type": type(error).__name__}

    def get_metrics(self) -> Dict[str, Any]:
        """Get middleware metrics."""
        return {
            "name": self.name,
            "type": self.middleware_type.value,
            "enabled": self.enabled,
            "metrics": dict(self.metrics),
        }


class SecurityMiddleware(BaseMiddleware):
    """Security validation and authentication middleware."""

    def __init__(self, security_framework: Optional["LUKHASSecurityFramework"] = None):
        super().__init__("security", MiddlewareType.SECURITY)
        self.security_framework = security_framework

    async def process_request(
        self, metadata: RequestMetadata, request_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Validate security and authenticate request."""
        start_time = time.time()

        try:
            # Extract authentication token
            auth_header = metadata.custom_headers.get("authorization", "")
            api_key = metadata.custom_headers.get("x-api-key", "")

            if self.security_framework:
                # Validate JWT token
                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    user = await self.security_framework.jwt_service.validate_token(token)
                    if user:
                        metadata.user_id = user.user_id
                        metadata.tier = self._determine_user_tier(user)
                        metadata.security_context["user"] = user
                    else:
                        self.metrics["requests_blocked"] += 1
                        return False, {"error": "Invalid authentication token", "status": 401}

                # Validate API key
                elif api_key:
                    # In a real implementation, validate API key against database
                    metadata.api_key = api_key
                    metadata.tier = self._determine_api_key_tier(api_key)

                # Check for threats
                threat_detected = await self._check_for_threats(metadata, request_data)
                if threat_detected:
                    self.metrics["requests_blocked"] += 1
                    return False, {"error": "Security threat detected", "status": 403}

            # Rate limiting and security headers
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            }

            metadata.security_context["headers"] = security_headers
            metadata.processing_phases.append("security_validated")

            self.metrics["requests_processed"] += 1
            self.metrics["processing_time_ms"] += (time.time() - start_time) * 1000

            return True, {"security_context": metadata.security_context}

        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return await self.on_error(metadata, e), {}

    async def process_response(self, metadata: RequestMetadata, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add security headers to response."""
        if "headers" not in response_data:
            response_data["headers"] = {}

        security_headers = metadata.security_context.get("headers", {})
        response_data["headers"].update(security_headers)

        return response_data

    def _determine_user_tier(self, user) -> APITier:
        """Determine user tier from user object."""
        # This would typically check user subscription, permissions, etc.
        if hasattr(user, "roles"):
            if "enterprise" in user.roles:
                return APITier.ENTERPRISE
            elif "premium" in user.roles:
                return APITier.PREMIUM
            elif "basic" in user.roles:
                return APITier.BASIC
        return APITier.FREE

    def _determine_api_key_tier(self, api_key: str) -> APITier:
        """Determine tier from API key."""
        # This would typically look up the API key in a database
        if api_key.startswith("ent_"):
            return APITier.ENTERPRISE
        elif api_key.startswith("pre_"):
            return APITier.PREMIUM
        elif api_key.startswith("bas_"):
            return APITier.BASIC
        return APITier.FREE

    async def _check_for_threats(self, metadata: RequestMetadata, request_data: Dict[str, Any]) -> bool:
        """Check for security threats."""
        if not self.security_framework:
            return False

        # Check for common attack patterns
        threat_patterns = [
            metadata.endpoint,
            str(request_data),
            metadata.user_agent,
            json.dumps(metadata.custom_headers),
        ]

        for pattern in threat_patterns:
            if await self.security_framework.threat_detector.detect_threat("general", pattern):
                return True

        return False


class OptimizationMiddleware(BaseMiddleware):
    """API optimization and caching middleware."""

    def __init__(self, optimizer: Optional["LUKHASAPIOptimizer"] = None):
        super().__init__("optimization", MiddlewareType.OPTIMIZATION)
        self.optimizer = optimizer

    async def process_request(
        self, metadata: RequestMetadata, request_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Apply optimization strategies to request."""
        start_time = time.time()

        try:
            if not self.optimizer:
                return True, {}

            # Create request context for optimizer
            context = RequestContext(
                request_id=metadata.request_id,
                endpoint=metadata.endpoint,
                method=metadata.method,
                user_id=metadata.user_id,
                api_key=metadata.api_key,
                tier=metadata.tier,
                priority=metadata.priority,
                size_bytes=metadata.content_length,
                headers=dict(metadata.custom_headers),
            )

            # Check rate limits and cache
            allowed, optimization_info = await self.optimizer.process_request(context)

            if not allowed:
                self.metrics["requests_blocked"] += 1
                return False, {
                    "error": "Request blocked by optimization layer",
                    "status": 429,
                    "details": optimization_info,
                }

            # Check for cached response
            if optimization_info.get("cached"):
                metadata.optimization_context["cached_response"] = optimization_info["data"]
                metadata.optimization_context["cache_hit"] = True
            else:
                metadata.optimization_context["cache_hit"] = False

            metadata.optimization_context["context"] = context
            metadata.optimization_context["optimization_info"] = optimization_info
            metadata.processing_phases.append("optimization_applied")

            self.metrics["requests_processed"] += 1
            self.metrics["processing_time_ms"] += (time.time() - start_time) * 1000

            return True, {"optimization_context": metadata.optimization_context}

        except Exception as e:
            logger.error(f"Optimization middleware error: {e}")
            return await self.on_error(metadata, e), {}

    async def process_response(self, metadata: RequestMetadata, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete optimization processing."""
        try:
            if self.optimizer and "context" in metadata.optimization_context:
                context = metadata.optimization_context["context"]
                status_code = response_data.get("status_code", 200)

                # Complete request processing for analytics
                await self.optimizer.complete_request(context, response_data, status_code)

                # Add optimization headers
                if "headers" not in response_data:
                    response_data["headers"] = {}

                response_data["headers"]["X-Cache-Status"] = (
                    "HIT" if metadata.optimization_context.get("cache_hit") else "MISS"
                )
                response_data["headers"]["X-Request-ID"] = metadata.request_id

            return response_data

        except Exception as e:
            logger.error(f"Optimization response processing error: {e}")
            return response_data


class ValidationMiddleware(BaseMiddleware):
    """Request validation and sanitization middleware."""

    def __init__(self, max_request_size_mb: float = 100.0):
        super().__init__("validation", MiddlewareType.VALIDATION)
        self.max_request_size_bytes = max_request_size_mb * 1024 * 1024

    async def process_request(
        self, metadata: RequestMetadata, request_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Validate request structure and content."""
        start_time = time.time()

        try:
            # Check request size
            if metadata.content_length > self.max_request_size_bytes:
                self.metrics["requests_blocked"] += 1
                return False, {
                    "error": f"Request too large: {metadata.content_length} bytes",
                    "status": 413,
                    "max_size": self.max_request_size_bytes,
                }

            # Validate content type for POST/PUT requests
            if metadata.method in ["POST", "PUT", "PATCH"]:
                if not metadata.content_type:
                    self.metrics["requests_blocked"] += 1
                    return False, {"error": "Content-Type header required", "status": 400}

                if metadata.content_type not in [
                    "application/json",
                    "application/x-www-form-urlencoded",
                    "multipart/form-data",
                    "text/plain",
                ]:
                    self.metrics["requests_blocked"] += 1
                    return False, {"error": f"Unsupported content type: {metadata.content_type}", "status": 415}

            # Basic JSON validation for JSON requests
            if metadata.content_type == "application/json" and request_data:
                try:
                    if isinstance(request_data, str):
                        json.loads(request_data)
                except json.JSONDecodeError as e:
                    self.metrics["requests_blocked"] += 1
                    return False, {"error": f"Invalid JSON: {str(e)}", "status": 400}

            # Sanitize request data
            sanitized_data = await self._sanitize_request_data(request_data)

            metadata.processing_phases.append("validation_passed")
            self.metrics["requests_processed"] += 1
            self.metrics["processing_time_ms"] += (time.time() - start_time) * 1000

            return True, {"sanitized_data": sanitized_data}

        except Exception as e:
            logger.error(f"Validation middleware error: {e}")
            return await self.on_error(metadata, e), {}

    async def process_response(self, metadata: RequestMetadata, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize response."""
        # Add validation headers
        if "headers" not in response_data:
            response_data["headers"] = {}

        response_data["headers"]["X-Validation-Status"] = "passed"

        return response_data

    async def _sanitize_request_data(self, data: Any) -> Any:
        """Sanitize request data to prevent common attacks."""
        if isinstance(data, dict):
            return {k: await self._sanitize_request_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [await self._sanitize_request_data(item) for item in data]
        elif isinstance(data, str):
            # Basic string sanitization
            return data.strip()
        else:
            return data


class AnalyticsMiddleware(BaseMiddleware):
    """Analytics and monitoring middleware."""

    def __init__(self):
        super().__init__("analytics", MiddlewareType.ANALYTICS)
        self.request_logs = []

    async def process_request(
        self, metadata: RequestMetadata, request_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Log request for analytics."""
        # Store request start time for duration calculation
        metadata.middleware_data["analytics_start"] = time.time()

        self.metrics["requests_processed"] += 1
        return True, {}

    async def process_response(self, metadata: RequestMetadata, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log response and calculate metrics."""
        end_time = time.time()
        start_time = metadata.middleware_data.get("analytics_start", metadata.start_time)
        duration_ms = (end_time - start_time) * 1000

        # Create analytics log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": metadata.request_id,
            "method": metadata.method,
            "endpoint": metadata.endpoint,
            "status_code": response_data.get("status_code", 200),
            "duration_ms": duration_ms,
            "user_id": metadata.user_id,
            "client_ip": metadata.client_ip,
            "user_agent": metadata.user_agent,
            "tier": metadata.tier.value,
            "content_length": metadata.content_length,
            "processing_phases": metadata.processing_phases,
        }

        # Store log entry (in production, this would go to a proper logging system)
        self.request_logs.append(log_entry)

        # Keep only last 1000 entries in memory
        if len(self.request_logs) > 1000:
            self.request_logs = self.request_logs[-1000:]

        # Add analytics headers
        if "headers" not in response_data:
            response_data["headers"] = {}

        response_data["headers"]["X-Processing-Time"] = f"{duration_ms:.2f}ms"
        response_data["headers"]["X-Analytics-ID"] = metadata.request_id

        return response_data

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        if not self.request_logs:
            return {"message": "No analytics data available"}

        recent_logs = self.request_logs[-100:]  # Last 100 requests

        avg_duration = sum(log["duration_ms"] for log in recent_logs) / len(recent_logs)
        status_codes = [log["status_code"] for log in recent_logs]
        error_rate = len([s for s in status_codes if s >= 400]) / len(status_codes) * 100

        return {
            "total_requests": len(self.request_logs),
            "recent_requests": len(recent_logs),
            "avg_duration_ms": avg_duration,
            "error_rate_percent": error_rate,
            "status_distribution": self._count_distribution(status_codes),
            "top_endpoints": self._get_top_endpoints(recent_logs),
        }

    def _count_distribution(self, data: List[Any]) -> Dict[Any, int]:
        """Get count distribution."""
        counts = {}
        for item in data:
            counts[item] = counts.get(item, 0) + 1
        return counts

    def _get_top_endpoints(self, logs: List[Dict]) -> List[Dict]:
        """Get top endpoints by request count."""
        endpoint_counts = {}
        for log in logs:
            endpoint = f"{log['method']} {log['endpoint']}"
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1

        return [
            {"endpoint": endpoint, "count": count}
            for endpoint, count in sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]


class LUKHASMiddlewarePipeline:
    """Main middleware pipeline coordinator."""

    def __init__(self, config: MiddlewareConfig):
        self.config = config
        self.middleware_stack: List[BaseMiddleware] = []
        self.processing_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "blocked_requests": 0,
            "error_requests": 0,
            "avg_processing_time_ms": 0,
        }

    def add_middleware(self, middleware: BaseMiddleware):
        """Add middleware to the processing pipeline."""
        self.middleware_stack.append(middleware)
        logger.info(f"Added middleware: {middleware.name} ({middleware.middleware_type.value})")

    def remove_middleware(self, name: str):
        """Remove middleware from pipeline."""
        self.middleware_stack = [m for m in self.middleware_stack if m.name != name]
        logger.info(f"Removed middleware: {name}")

    async def process_request(
        self, metadata: RequestMetadata, request_data: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Process request through middleware pipeline."""
        start_time = time.time()
        self.processing_stats["total_requests"] += 1

        try:
            processed_data = dict(request_data)

            # Process through each middleware
            for middleware in self.middleware_stack:
                if not middleware.enabled:
                    continue

                try:
                    continue_processing, middleware_data = await middleware.process_request(metadata, processed_data)

                    if not continue_processing:
                        self.processing_stats["blocked_requests"] += 1
                        return False, middleware_data

                    # Merge middleware data
                    processed_data.update(middleware_data)

                except Exception as e:
                    logger.error(f"Middleware {middleware.name} failed: {e}")
                    error_data = await middleware.on_error(metadata, e)
                    self.processing_stats["error_requests"] += 1
                    return False, error_data

            self.processing_stats["successful_requests"] += 1

            # Update average processing time
            processing_time = (time.time() - start_time) * 1000
            total_requests = self.processing_stats["total_requests"]
            current_avg = self.processing_stats["avg_processing_time_ms"]
            self.processing_stats["avg_processing_time_ms"] = (
                current_avg * (total_requests - 1) + processing_time
            ) / total_requests

            return True, processed_data

        except Exception as e:
            logger.error(f"Pipeline processing error: {e}")
            self.processing_stats["error_requests"] += 1
            return False, {"error": f"Pipeline error: {str(e)}", "status": 500}

    async def process_response(self, metadata: RequestMetadata, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process response through middleware pipeline (reverse order)."""
        try:
            processed_response = dict(response_data)

            # Process through middleware in reverse order
            for middleware in reversed(self.middleware_stack):
                if not middleware.enabled:
                    continue

                try:
                    processed_response = await middleware.process_response(metadata, processed_response)
                except Exception as e:
                    logger.error(f"Middleware {middleware.name} response processing failed: {e}")
                    # Continue processing other middleware

            return processed_response

        except Exception as e:
            logger.error(f"Pipeline response processing error: {e}")
            return response_data

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics."""
        middleware_stats = [m.get_metrics() for m in self.middleware_stack]

        return {
            "pipeline": dict(self.processing_stats),
            "middleware": middleware_stats,
            "config": {
                "total_middleware": len(self.middleware_stack),
                "enabled_middleware": len([m for m in self.middleware_stack if m.enabled]),
                "security_enabled": self.config.enable_security,
                "optimization_enabled": self.config.enable_optimization,
                "analytics_enabled": self.config.enable_analytics,
            },
        }


# FastAPI integration
if FASTAPI_AVAILABLE:

    class LUKHASFastAPIMiddleware(BaseHTTPMiddleware):
        """FastAPI middleware integration for LUKHAS."""

        def __init__(self, app, pipeline: LUKHASMiddlewarePipeline):
            super().__init__(app)
            self.pipeline = pipeline

        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
            """Process FastAPI request through LUKHAS middleware pipeline."""

            # Create request metadata
            metadata = RequestMetadata(
                request_id=f"req_{int(time.time() * 1000)}_{id(request)}",
                start_time=time.time(),
                client_ip=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", ""),
                endpoint=str(request.url.path),
                method=request.method,
                content_type=request.headers.get("content-type"),
                content_length=int(request.headers.get("content-length", 0)),
                custom_headers=dict(request.headers),
            )

            # Extract request data
            request_data = {}
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    if metadata.content_type == "application/json":
                        request_data = await request.json()
                    else:
                        request_data = {"body": await request.body()}
                except Exception as e:
                    logger.warning(f"Failed to parse request data: {e}")

            # Process through pipeline
            allowed, processed_data = await self.pipeline.process_request(metadata, request_data)

            if not allowed:
                # Return error response
                status_code = processed_data.get("status", 400)
                return Response(
                    content=json.dumps(processed_data), status_code=status_code, media_type="application/json"
                )

            # Check for cached response
            if metadata.optimization_context.get("cached_response"):
                cached_response = metadata.optimization_context["cached_response"]
                response_data = await self.pipeline.process_response(metadata, cached_response)
                return Response(
                    content=json.dumps(response_data),
                    status_code=200,
                    media_type="application/json",
                    headers=response_data.get("headers", {}),
                )

            # Continue with normal processing
            response = await call_next(request)

            # Process response
            response_data = {"status_code": response.status_code, "headers": dict(response.headers)}

            # Read response body if needed
            if response.status_code == 200:
                try:
                    body = b""
                    async for chunk in response.body_iterator:
                        body += chunk

                    if body:
                        response_data["body"] = body.decode()
                        if response.headers.get("content-type", "").startswith("application/json"):
                            response_data["json"] = json.loads(body.decode())
                except Exception as e:
                    logger.warning(f"Failed to read response body: {e}")

            # Process response through pipeline
            processed_response = await self.pipeline.process_response(metadata, response_data)

            # Update response headers
            for key, value in processed_response.get("headers", {}).items():
                response.headers[key] = value

            return response


# Factory function for creating configured pipeline
async def create_middleware_pipeline(
    config: MiddlewareConfig,
    security_framework: Optional["LUKHASSecurityFramework"] = None,
    optimizer: Optional["LUKHASAPIOptimizer"] = None,
) -> LUKHASMiddlewarePipeline:
    """Create a fully configured middleware pipeline."""

    pipeline = LUKHASMiddlewarePipeline(config)

    # Add middleware in processing order
    if config.enable_security and SECURITY_AVAILABLE:
        pipeline.add_middleware(SecurityMiddleware(security_framework))

    if config.enable_request_validation:
        pipeline.add_middleware(ValidationMiddleware(config.max_request_size_mb))

    if config.enable_optimization and OPTIMIZER_AVAILABLE:
        pipeline.add_middleware(OptimizationMiddleware(optimizer))

    if config.enable_analytics:
        pipeline.add_middleware(AnalyticsMiddleware())

    logger.info(f"Created middleware pipeline with {len(pipeline.middleware_stack)} middleware components")

    return pipeline


if __name__ == "__main__":

    async def test_middleware_pipeline():
        """Test the middleware pipeline."""

        # Create configuration
        config = MiddlewareConfig(
            enable_security=True, enable_optimization=True, enable_analytics=True, enable_request_validation=True
        )

        # Create pipeline
        pipeline = await create_middleware_pipeline(config)

        # Create test request
        metadata = RequestMetadata(
            request_id="test_123",
            start_time=time.time(),
            client_ip="192.168.1.100",
            user_agent="Test Agent",
            endpoint="/api/v1/test",
            method="GET",
            custom_headers={"authorization": "Bearer test_token"},
        )

        request_data = {"test": "data"}

        # Process request
        allowed, processed_data = await pipeline.process_request(metadata, request_data)

        if allowed:
            print("✅ Request processed successfully")

            # Simulate response
            response_data = {"result": "success", "status_code": 200}
            processed_response = await pipeline.process_response(metadata, response_data)

            print(f"📊 Response: {processed_response}")

            # Get stats
            stats = pipeline.get_pipeline_stats()
            print(f"📈 Stats: {stats}")
        else:
            print(f"❌ Request blocked: {processed_data}")

    asyncio.run(test_middleware_pipeline())
