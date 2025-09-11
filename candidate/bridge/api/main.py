

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: main.py
# MODULE: oneiric_core
# DESCRIPTION: Main FastAPI application for Oneiric Core - A symbolic dream
#              analysis system with ΛiD (LUKHAS Identity) integration. Provides
#              RESTful API endpoints for dream generation, analysis, and user
#              management with multi-tier authentication.
# DEPENDENCIES: fastapi, uvicorn, pydantic, asyncpg, .db.db, .identity.auth_middleware,
#               .analysis.drift_score, .settings
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .analysis.drift_score import update_user_drift_profile
from .db.db import init_db
from .identity.auth_middleware import AuthUser, get_current_user
from .settings import get_settings

# Initialize FastAPI app

# TAG:bridge
# TAG:api
# TAG:neuroplastic
# TAG:colony

app = FastAPI(
    title="Oneiric Core API",
    description="Symbolic Dream Analysis System with ΛiD Identity",
    version="2.9.0",
)

# Initialize database
init_db(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://oneiric-core.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for basic API info


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Oneiric Core API",
        "version": "2.9.0",
        "description": "Symbolic Dream Analysis System with ΛiD Identity",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "api": {
                "dreams": "/api/dreams",
                "symbols": "/api/symbols",
                "settings": "/api/settings",
            },
        },
    }


# Health check endpoint


@app.get("/healthz")
async def health_check(user: AuthUser = Depends(get_current_user)):
    """Health check with user authentication"""
    return {
        "status": "ok",
        "user_id": user.id,
        "tier": user.tier,
        "identity_legacy": (user.lukhas_id[:16] + "..." if user.lukhas_id else None),
        "timestamp": "2025-07-10T12:00:00Z",
    }


# Public health check (no auth required)


@app.get("/health")
async def public_health():
    """Public health check"""
    return {"status": "ok", "service": "oneiric-core"}


# Dream generation endpoint


@app.post("/api/generate-dream")
async def generate_dream(request: Request, user: AuthUser = Depends(get_current_user)):
    """Generate a dream scene with symbolic analysis"""
    try:
        # Get request data
        data = await request.json()
        prompt = data.get("prompt", "")
        data.get("recursive", False)

        # Mock dream generation response
        dream_response = {
            "sceneId": f"dream_{user.id}_{hash(prompt) % 10000}",
            "narrativeText": f"In the depths of symbolic space, {prompt} unfolds into a cascade of meaning...",
            "renderedImageUrl": "https://via.placeholder.com/512x512?text=Dream+Scene",
            "narrativeAudioUrl": None,
            "symbolicStructure": {
                "visualAnchor": "cascading_symbols",
                "directive_used": "symbolic_exploration",
                "driftAnalysis": {
                    "driftScore": 0.15,
                    "symbolic_entropy": 0.65,
                    "emotional_charge": 0.3,
                    "narrative_coherence": 0.85,
                },
            },
        }

        # Update user drift profile
        dream_metrics = {
            "symbolic_entropy": 0.65,
            "emotional_charge": 0.3,
            "narrative_coherence": 0.85,
            "timestamp": "2025-07-10T12:00:00Z",
        }

        updated_profile = await update_user_drift_profile(user.id, dream_metrics)

        # Add profile info to response
        dream_response["userProfile"] = {
            "total_dreams": updated_profile.get("total_dreams", 0),
            "avg_drift": updated_profile.get("drift_history", [{}])[-1].get("drift_score", 0.0),
        }

        return dream_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dreams list endpoint


@app.get("/api/dreams")
async def list_dreams(user: AuthUser = Depends(get_current_user)):
    """List user's dreams"""
    # Mock dreams data
    dreams = [
        {
            "sceneId": f"dream_{user.id}_001",
            "narrativeText": "A symbolic journey through cascading memories...",
            "renderedImageUrl": "https://via.placeholder.com/512x512?text=Dream+1",
            "symbolicStructure": {
                "visualAnchor": "memory_cascade",
                "directive_used": "memory_exploration",
                "driftAnalysis": {"driftScore": 0.12},
            },
        },
        {
            "sceneId": f"dream_{user.id}_002",
            "narrativeText": "Fragments of consciousness weaving together...",
            "renderedImageUrl": "https://via.placeholder.com/512x512?text=Dream+2",
            "symbolicStructure": {
                "visualAnchor": "consciousness_weave",
                "directive_used": "consciousness_exploration",
                "driftAnalysis": {"driftScore": 0.08},
            },
        },
    ]

    return {"dreams": dreams}


# Dream rating endpoint


@app.post("/api/dreams/{dream_id}/rate")
async def rate_dream(dream_id: str, request: Request, user: AuthUser = Depends(get_current_user)):
    """Rate a dream"""
    data = await request.json()
    rating = data.get("rating", 0)  # -1, 0, 1

    # Mock rating storage
    return {
        "success": True,
        "dream_id": dream_id,
        "rating": rating,
        "message": "Rating recorded",
    }


# Symbols endpoint


@app.get("/api/symbols")
async def list_symbols(user: AuthUser = Depends(get_current_user)):
    """List user's symbolic patterns"""
    # Mock symbols data
    symbols = [
        {
            "symbol": "water",
            "frequency": 12,
            "emotional_charge": 0.3,
            "recent_dreams": ["dream_001", "dream_005"],
        },
        {
            "symbol": "flight",
            "frequency": 8,
            "emotional_charge": 0.7,
            "recent_dreams": ["dream_002", "dream_003"],
        },
    ]

    return {"symbols": symbols}


# Settings endpoint


@app.get("/api/settings")
async def get_user_settings(user: AuthUser = Depends(get_current_user)):
    """Get user settings"""
    return {
        "recursive_dreams": True,
        "drift_logging": True,
        "audio_enabled": True,
        "theme": "default",
    }


@app.post("/api/settings")
async def update_user_settings(request: Request, user: AuthUser = Depends(get_current_user)):
    """Update user settings"""
    data = await request.json()

    # Mock settings update
    return {"success": True, "settings": data, "message": "Settings updated"}


# Error handlers


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": "http_error"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"},
    )


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug)

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: main.py
# VERSION: 2.9.0
# TIER SYSTEM: Tier 1-5 (Multi-tier authentication and authorization)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: RESTful API server for dream analysis, user management, ΛiD
#               identity integration, symbolic interpretation, and multi-tier
#               authentication system.
# FUNCTIONS: health_check, public_health, generate_dream, analyze_dream,
#           get_user_symbols, save_dream, get_dream_history, get_user_profile,
#           update_user_profile, http_exception_handler, general_exception_handler
# CLASSES: None directly defined (uses imported classes)
# DECORATORS: @app.get, @app.post, @app.put, @app.exception_handler
# DEPENDENCIES: FastAPI, uvicorn, CORS middleware, database layer, auth middleware,
#               drift analysis, settings management
# INTERFACES: REST API endpoints, JSON request/response formats, ΛiD protocol
# ERROR HANDLING: HTTP exception handling, general exception handling, validation
# LOGGING: ΛTRACE_ENABLED for request/response tracking and user actions
# AUTHENTICATION: ΛiD-based authentication with Clerk.dev integration
# HOW TO USE:
#   python -m oneiric_core.main
#   or via Docker: docker run -p 8000:8000 oneiric-core
#   API docs available at: http://localhost:8000/docs
# INTEGRATION NOTES: Central API gateway for all Oneiric Core services. Integrates
#   with PostgreSQL database, Clerk.dev authentication, and ΛiD identity system.
#   Supports multi-tier user classification and drift analysis.
# MAINTENANCE: Update API versions, endpoint documentation, and tier permissions
#   as requirements evolve. Monitor performance and error rates.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
