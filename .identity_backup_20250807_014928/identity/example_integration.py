"""
LUKHΛS Identity Integration Example
===================================

Example showing how to integrate the identity system with a FastAPI application.
Demonstrates protected routes and tier-based access control.
"""

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

# Import identity system components
from identity import (
    AuthContext,
    get_current_user,
    identity_router,
    require_t3_or_above,
    require_t5,
)

# Create FastAPI app
app = FastAPI(
    title="LUKHΛS Protected Application",
    description="Example application with identity integration",
    version="1.0.0",
)

# Include the identity router
app.include_router(identity_router)


# Public endpoint - no authentication required
@app.get("/")
async def root():
    """Public endpoint accessible to everyone."""
    return {
        "message": "Welcome to LUKHΛS",
        "endpoints": {
            "public": "/",
            "identity_info": "/identity",
            "register": "/identity/register",
            "login": "/identity/login",
            "protected": "/protected (requires auth)",
            "dashboard": "/dashboard (requires T2+)",
            "admin": "/admin (requires T5)",
        },
    }


# Protected endpoint - requires any authenticated user
@app.get("/protected")
async def protected_route(user: AuthContext = Depends(get_current_user)):
    """Protected endpoint requiring authentication."""
    return {
        "message": f"Hello {user.email}!",
        "tier": user.tier,
        "lambda_id": user.lambda_id,
        "glyphs": user.glyphs,
        "trinity_score": user.trinity_score,
    }


# Dashboard endpoint - requires T2 or higher
@app.get("/dashboard")
async def dashboard(user: AuthContext = Depends(require_t3_or_above)):
    """Dashboard endpoint requiring T3+ tier."""
    return {
        "message": "Welcome to the LUKHΛS Dashboard",
        "user": user.email,
        "tier": user.tier,
        "features_available": [
            "Consciousness Module",
            "Emotion Processing",
            "Dream Engine",
        ],
    }


# Admin endpoint - requires T5 (Guardian)
@app.get("/admin")
async def admin_panel(user: AuthContext = Depends(require_t5)):
    """Admin panel requiring T5 Guardian tier."""
    return {
        "message": "Guardian Control Panel",
        "user": user.email,
        "full_trinity_access": True,
        "admin_features": [
            "User Management",
            "System Configuration",
            "Guardian Oversight",
            "Drift Monitoring",
        ],
    }


# Example API endpoint with tier-based functionality
@app.post("/api/process")
async def process_data(data: dict, user: AuthContext = Depends(get_current_user)):
    """
    Process data with tier-based features.
    Higher tiers get more processing capabilities.
    """
    result = {"user": user.email, "tier": user.tier, "input": data}

    # Basic processing for all tiers
    result["basic_analysis"] = len(str(data))

    # Enhanced processing for T2+
    if user.is_tier_or_above("T2"):
        result["enhanced_analysis"] = {
            "keys": list(data.keys()),
            "complexity": len(data.keys()),
        }

    # Consciousness processing for T3+
    if user.is_tier_or_above("T3"):
        result["consciousness_score"] = user.trinity_score
        result["emotional_context"] = "analyzed"

    # Quantum processing for T4+
    if user.is_tier_or_above("T4"):
        result["quantum_analysis"] = "quantum_enhanced"

    # Guardian insights for T5
    if user.tier == "T5":
        result["guardian_insights"] = {
            "drift_detected": False,
            "ethical_score": 1.0,
            "recommendation": "approved",
        }

    return result


# Error handler for authentication failures
@app.exception_handler(401)
async def unauthorized_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={
            "error": "Unauthorized",
            "message": str(exc.detail),
            "login_endpoint": "/identity/login",
        },
    )


@app.exception_handler(403)
async def forbidden_handler(request, exc):
    return JSONResponse(
        status_code=403,
        content={
            "error": "Forbidden",
            "message": str(exc.detail),
            "required_tier": "Check endpoint documentation",
        },
    )


if __name__ == "__main__":
    print("🧠 LUKHΛS Identity Integration Example")
    print("=" * 50)
    print("\nDemo credentials:")
    print("  Email: reviewer@openai.com")
    print("  Password: demo_password")
    print("  Tier: T5 (Full Guardian access)")
    print("\nStarting server on http://localhost:8000")
    print("API documentation available at http://localhost:8000/docs")
    print("\n" + "=" * 50)

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
