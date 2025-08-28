#!/usr/bin/env python3
"""
LUKHAS AI - Comprehensive API Bridge Main Module
===============================================

Main FastAPI application that integrates all API bridge components
including orchestration, onboarding, validation, security, and documentation.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Performance Target: <100ms API response latency
Supports: Multi-model orchestration, healthcare compliance, enterprise security

Features:
- Complete API bridge implementation
- Multi-model AI orchestration with consensus
- Healthcare-compliant endpoints with HIPAA support
- Comprehensive validation and security
- User onboarding with intelligent tier assignment
- Real-time streaming and WebSocket support
- Interactive API documentation
- Comprehensive monitoring and metrics
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

try:
    from fastapi import FastAPI, HTTPException, Request, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from fastapi.responses import JSONResponse, RedirectResponse
    from fastapi.staticfiles import StaticFiles
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# LUKHAS imports
try:
    from candidate.bridge.api.documentation import (
        export_openapi_spec,
        generate_api_documentation,
    )
    from candidate.bridge.api.onboarding import router as onboarding_router
    from candidate.bridge.api.orchestration_endpoints import app as orchestration_app
    from candidate.bridge.api.security import get_security_manager
    from candidate.bridge.api.validation import get_validator, run_validation_tests
    BRIDGE_MODULES_AVAILABLE = True
except ImportError as e:
    logging.error(f"Bridge module import error: {e}")
    BRIDGE_MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("🚀 LUKHAS AI API Bridge starting up...")

    try:
        # Initialize components
        if BRIDGE_MODULES_AVAILABLE:
            # Initialize validator
            get_validator()
            logger.info("✅ API validator initialized")

            # Initialize security manager
            get_security_manager()
            logger.info("✅ Security manager initialized")

            # Run startup validation tests
            logger.info("🔍 Running startup validation tests...")
            test_results = await run_validation_tests()

            if test_results["overall_success"]:
                logger.info("✅ All validation tests passed")
            else:
                logger.warning("⚠️ Some validation tests failed - check logs")

            # API documentation can be generated manually
            logger.info("✅ Skipping API documentation generation at startup")

        logger.info("🎉 LUKHAS AI API Bridge startup complete!")

    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 LUKHAS AI API Bridge shutting down...")
    logger.info("✅ Shutdown complete")

# Create FastAPI application
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="LUKHAS AI Multi-Model Orchestration API",
        description="Advanced multi-model AI orchestration with enterprise security and healthcare compliance",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        # Custom OpenAPI generation
        openapi_tags=[
            {
                "name": "orchestration",
                "description": "Multi-model AI orchestration endpoints with advanced consensus algorithms"
            },
            {
                "name": "healthcare",
                "description": "HIPAA-compliant healthcare AI endpoints with audit trails"
            },
            {
                "name": "streaming",
                "description": "Real-time streaming endpoints with SSE and WebSocket support"
            },
            {
                "name": "onboarding",
                "description": "User onboarding with intelligent tier assignment and consent management"
            },
            {
                "name": "monitoring",
                "description": "API health monitoring, metrics, and performance analytics"
            },
            {
                "name": "security",
                "description": "Security management, API keys, and audit trails"
            }
        ]
    )

    # Middleware configuration
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware for request tracking and performance monitoring
    @app.middleware("http")
    async def performance_middleware(request: Request, call_next):
        """Track request performance and add custom headers"""
        start_time = time.perf_counter()

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error", "request_id": str(time.time())}
            )

        # Calculate processing time
        process_time = time.perf_counter() - start_time

        # Add custom headers
        response.headers["X-Process-Time"] = str(f"{process_time:.4f}")
        response.headers["X-LUKHAS-API-Version"] = "2.0.0"
        response.headers["X-Timestamp"] = datetime.now(timezone.utc).isoformat()

        # Log performance metrics
        if process_time > 1.0:  # Log slow requests
            logger.warning(f"Slow request: {request.method} {request.url} - {process_time:.4f}s")

        return response

    # Exception handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        """Custom 404 handler with helpful information"""
        return JSONResponse(
            status_code=404,
            content={
                "error": "Endpoint not found",
                "message": "The requested endpoint does not exist",
                "available_endpoints": [
                    "/docs - Interactive API documentation",
                    "/health - API health check",
                    "/api/v1/orchestrate - Multi-model orchestration",
                    "/api/v1/stream - Real-time streaming",
                    "/api/v2/onboarding - User onboarding"
                ],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception):
        """Custom 500 handler with error tracking"""
        error_id = str(time.time())
        logger.error(f"Internal error {error_id}: {exc}")

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_id": error_id,
                "message": "An unexpected error occurred. Please try again later.",
                "support": "Contact support@lukhas.ai with error ID for assistance",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

    # Root endpoint
    @app.get("/")
    async def root():
        """API root with welcome message and basic information"""
        return {
            "message": "Welcome to LUKHAS AI Multi-Model Orchestration API",
            "version": "2.0.0",
            "status": "active",
            "documentation": "/docs",
            "health_check": "/health",
            "features": [
                "Multi-model AI orchestration",
                "Advanced consensus algorithms",
                "Real-time streaming",
                "Healthcare compliance (HIPAA)",
                "Enterprise security",
                "Comprehensive validation",
                "User onboarding system"
            ],
            "trinity_framework": {
                "identity": "⚛️ Secure authentication and user management",
                "consciousness": "🧠 Intelligent orchestration and decision-making",
                "guardian": "🛡️ Security, validation, and compliance protection"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # Redirect /api to documentation
    @app.get("/api")
    async def api_redirect():
        """Redirect /api to documentation"""
        return RedirectResponse(url="/docs")

    # Comprehensive health check
    @app.get("/health", tags=["monitoring"])
    async def health_check():
        """Comprehensive health check with component status"""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "uptime": time.time(),  # Simplified uptime
            "components": {
                "api_bridge": True,
                "validation_system": BRIDGE_MODULES_AVAILABLE,
                "security_manager": BRIDGE_MODULES_AVAILABLE,
                "orchestration": BRIDGE_MODULES_AVAILABLE,
                "onboarding": BRIDGE_MODULES_AVAILABLE
            }
        }

        if BRIDGE_MODULES_AVAILABLE:
            try:
                # Check component health
                validator = get_validator()
                security = get_security_manager()

                # Get system metrics
                validation_metrics = validator.get_validation_metrics() if validator else {}
                security_metrics = security.get_security_metrics() if security else {}

                health_data.update({
                    "validation_metrics": {
                        "total_validations": validation_metrics.get("total_validations", 0),
                        "success_rate": validation_metrics.get("success_rate", 0.0),
                        "average_latency_ms": validation_metrics.get("average_latency_ms", 0.0)
                    },
                    "security_metrics": {
                        "total_api_keys": security_metrics.get("total_api_keys", 0),
                        "security_events_24h": security_metrics.get("security_events_24h", 0),
                        "blocked_ips": security_metrics.get("blocked_ips", 0)
                    },
                    "performance": {
                        "target_latency_ms": 100,
                        "validation_latency_target_ms": 10,
                        "security_latency_target_ms": 5
                    }
                })

            except Exception as e:
                logger.error(f"Health check component error: {e}")
                health_data["components"]["error"] = str(e)

        # Determine overall health
        component_health = all(health_data["components"].values())
        if not component_health:
            health_data["status"] = "degraded"

        return health_data

    # Metrics endpoint
    @app.get("/metrics", tags=["monitoring"])
    async def get_metrics():
        """Get comprehensive API metrics and performance data"""
        if not BRIDGE_MODULES_AVAILABLE:
            return {"error": "Metrics not available - bridge modules not loaded"}

        try:
            validator = get_validator()
            security = get_security_manager()

            metrics = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "api_version": "2.0.0",
                "validation_metrics": validator.get_validation_metrics() if validator else {},
                "security_metrics": security.get_security_metrics() if security else {},
                "system_info": {
                    "python_version": os.sys.version,
                    "platform": os.name,
                    "process_id": os.getpid()
                }
            }

            return metrics

        except Exception as e:
            logger.error(f"Metrics error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve metrics: {str(e)}"
            )

    # Status endpoint for monitoring systems
    @app.get("/status", tags=["monitoring"])
    async def get_status():
        """Simple status endpoint for monitoring systems"""
        return {
            "status": "ok",
            "service": "lukhas-api-bridge",
            "version": "2.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # Include sub-applications and routers
    if BRIDGE_MODULES_AVAILABLE:
        # Include orchestration endpoints
        if orchestration_app:
            app.mount("/api/v1", orchestration_app)
            logger.info("✅ Orchestration endpoints mounted at /api/v1")

        # Include onboarding router
        if onboarding_router:
            app.include_router(onboarding_router)
            logger.info("✅ Onboarding endpoints included")

    logger.info("🌟 LUKHAS AI API Bridge configured successfully")

else:
    logger.error("❌ FastAPI not available - API bridge cannot start")
    app = None

# Development server runner
if __name__ == "__main__":
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
        exit(1)

    if not BRIDGE_MODULES_AVAILABLE:
        print("⚠️ Some bridge modules not available. Some features may be limited.")

    try:
        import uvicorn

        # Development configuration
        config = {
            "host": "127.0.0.1",
            "port": 8080,
            "reload": True,
            "reload_dirs": ["candidate/bridge/api"],
            "log_level": "info",
            "access_log": True
        }

        print("🚀 Starting LUKHAS AI API Bridge development server...")
        print(f"   URL: http://{config['host']}:{config['port']}")
        print(f"   Documentation: http://{config['host']}:{config['port']}/docs")
        print(f"   Health Check: http://{config['host']}:{config['port']}/health")

        uvicorn.run("main_app:app", **config)

    except ImportError:
        print("❌ Uvicorn not available. Install with: pip install uvicorn")
        print("   Or run with: uvicorn candidate.bridge.api.main_app:app --reload --port 8080")
    except KeyboardInterrupt:
        print("\n👋 LUKHAS AI API Bridge stopped")

# Export main components
__all__ = ["app"]
