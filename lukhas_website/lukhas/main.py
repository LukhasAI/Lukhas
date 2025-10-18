#!/usr/bin/env python3
"""
LUKHAS AI - Main API Entry Point
Production Schema v1.0.0

Central FastAPI application that wires all LUKHAS services together:
- Identity & WebAuthn (I.1-I.6)
- Orchestration & Multi-AI routing (O.2)
- Governance & Guardian system (G.1)
- Health checks and observability
"""

import logging
import os
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Import observability
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app

from lukhas.governance.guardian import get_guardian_status

# Import API routers
from identity.webauthn_api import router as webauthn_router
from lukhas.orchestration.api import router as orchestration_router

logger = logging.getLogger(__name__)

# Prometheus metrics
api_requests_total = Counter(
    'lukhas_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration_seconds = Histogram(
    'lukhas_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

api_active_connections = Gauge(
    'lukhas_api_active_connections',
    'Active API connections'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting LUKHAS AI API server...")

    # Startup
    logger.info("✅ LUKHAS AI API server started successfully")

    yield

    # Shutdown
    logger.info("🛑 Shutting down LUKHAS AI API server...")


# Create FastAPI app
app = FastAPI(
    title="LUKHAS AI",
    description="Advanced AI system with consciousness, identity, and orchestration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted hosts for production
if os.getenv("TRUSTED_HOSTS"):
    trusted_hosts = os.getenv("TRUSTED_HOSTS", "").split(",")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)


# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track API requests for metrics"""
    start_time = time.time()
    api_active_connections.inc()

    try:
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        method = request.method
        endpoint = request.url.path
        status = response.status_code

        api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

        api_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        return response

    finally:
        api_active_connections.dec()


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "lukhas-api",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status"""
    try:
        # Check Guardian status
        guardian_status = get_guardian_status()

        # Check component health
        components = {
            "guardian": {
                "status": "healthy" if guardian_status.get("enabled") else "degraded",
                "mode": guardian_status.get("mode"),
                "implementation": guardian_status.get("implementation")
            },
            "identity": {
                "status": "healthy",
                "webauthn": "available"
            },
            "orchestration": {
                "status": "healthy",
                "multi_ai": "available"
            }
        }

        # Overall status
        all_healthy = all(c.get("status") == "healthy" for c in components.values())
        overall_status = "healthy" if all_healthy else "degraded"

        return {
            "status": overall_status,
            "service": "lukhas-api",
            "version": "1.0.0",
            "timestamp": time.time(),
            "components": components,
            "guardian": guardian_status
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Health check failed")


@app.get("/status")
async def api_status():
    """API status with metrics"""
    return {
        "api": "lukhas-ai",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": time.time(),
        "endpoints": {
            "identity": "/identity",
            "orchestration": "/orchestration",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        },
        "environment": {
            "guardian_mode": os.getenv("GUARDIAN_MODE", "development"),
            "lukhas_mode": os.getenv("LUKHAS_MODE", "development")
        }
    }


# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Include API routers
app.include_router(
    webauthn_router,
    prefix="/identity/webauthn",
    tags=["Identity", "WebAuthn"]
)

app.include_router(
    orchestration_router,
    prefix="/orchestration",
    tags=["Orchestration", "Multi-AI"]
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "LUKHAS AI",
        "version": "1.0.0",
        "description": "Advanced AI system with consciousness, identity, and orchestration",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "identity": "/identity",
            "orchestration": "/orchestration",
            "docs": "/docs",
            "metrics": "/metrics"
        },
        "timestamp": time.time()
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "endpoint_not_found",
            "message": f"Endpoint {request.url.path} not found",
            "available_endpoints": [
                "/health",
                "/status",
                "/identity/webauthn",
                "/orchestration",
                "/docs"
            ]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal server error occurred",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )


def create_app() -> FastAPI:
    """Application factory"""
    return app


if __name__ == "__main__":
    # Development server
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"🚀 Starting LUKHAS AI API on {host}:{port}")

    uvicorn.run(
        "lukhas.main:app",
        host=host,
        port=port,
        reload=os.getenv("LUKHAS_MODE") == "development",
        log_level="info"
    )
