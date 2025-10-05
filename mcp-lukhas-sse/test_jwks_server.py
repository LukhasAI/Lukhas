#!/usr/bin/env python3
"""Local test JWKS server for development."""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Test JWKS Server")

# Test JWKS (matches the key used in generate_test_jwt.py)
TEST_JWKS = {
    "keys": [
        {
            "kty": "oct",
            "use": "sig",
            "kid": "test-key-1",
            "k": "dGVzdC1zZWNyZXQta2V5LWZvci1sb2NhbC1kZXZlbG9wbWVudC1vbmx5LWRvLW5vdC11c2UtaW4tcHJvZHVjdGlvbg"
        }
    ]
}

@app.get("/.well-known/jwks.json")
async def get_jwks():
    """Return test JWKS."""
    return JSONResponse(content=TEST_JWKS)

@app.get("/.well-known/openid-configuration")
async def get_openid_config():
    """Return OpenID configuration."""
    return JSONResponse(content={
        "issuer": "https://test-issuer.local",
        "jwks_uri": "http://localhost:8081/.well-known/jwks.json",
        "authorization_endpoint": "http://localhost:8081/auth",
        "token_endpoint": "http://localhost:8081/token",
        "userinfo_endpoint": "http://localhost:8081/userinfo",
        "response_types_supported": ["code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email"]
    })

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Test JWKS Server for Local Development", "jwks_url": "/.well-known/jwks.json"}

if __name__ == "__main__":
    print("🧪 Starting Test JWKS Server on port 8081")
    print("📍 JWKS URL: http://localhost:8081/.well-known/jwks.json")
    print("📍 OpenID Config: http://localhost:8081/.well-known/openid-configuration")

    uvicorn.run(app, host="0.0.0.0", port=8081)
