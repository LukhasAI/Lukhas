"""JWKS (JSON Web Key Set) endpoint for Lukhas Identity.

Provides public key discovery for JWT verification per RFC 7517.

Clients can fetch this endpoint to get public keys for verifying
ID tokens issued by Lukhas Identity system.
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from core.identity.keys import KeyManager

logger = logging.getLogger(__name__)

# Router for well-known endpoints
router = APIRouter(prefix="/.well-known", tags=["discovery"])


# Global key manager instance (initialized by app startup)
_key_manager: KeyManager = None


def init_jwks_endpoint(key_manager: KeyManager):
    """Initialize JWKS endpoint with key manager.

    Call this from FastAPI app startup:
        ```python
        @app.on_event("startup")
        async def startup():
            km = KeyManager(algorithm="RS256", key_dir="/secrets/keys")
            init_jwks_endpoint(km)
        ```

    Args:
        key_manager: KeyManager instance
    """
    global _key_manager
    _key_manager = key_manager
    logger.info("JWKS endpoint initialized")


@router.get("/jwks.json", response_class=JSONResponse)
async def get_jwks() -> Dict[str, List[Dict]]:
    """Get JSON Web Key Set (JWKS) for JWT verification.

    This endpoint returns public keys in JWK format per RFC 7517.
    Clients use these keys to verify signatures on ID tokens.

    Returns:
        JWKS dictionary:
        ```json
        {
          "keys": [
            {
              "kty": "RSA",
              "use": "sig",
              "kid": "lukhas-rs256-20251114120000",
              "alg": "RS256",
              "n": "...",  // RSA modulus (base64url)
              "e": "AQAB"   // RSA exponent
            }
          ]
        }
        ```

    Example usage:
        ```bash
        # Fetch JWKS
        curl https://ai/.well-known/jwks.json

        # Verify JWT with JWKS
        jwt verify <token> --jwks-uri https://ai/.well-known/jwks.json
        ```

    Caching:
        - Clients SHOULD cache this response for at least 1 hour
        - Clients MUST refresh if they encounter an unknown `kid`
        - Max-age header set to 3600 seconds (1 hour)
    """
    if _key_manager is None:
        logger.error("JWKS endpoint not initialized - call init_jwks_endpoint() first")
        raise HTTPException(
            status_code=500, detail="JWKS endpoint not properly configured"
        )

    try:
        jwks = _key_manager.export_jwks()

        # Add caching headers
        headers = {
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "Access-Control-Allow-Origin": "*",  # Allow CORS (public endpoint)
        }

        return JSONResponse(content=jwks, headers=headers)

    except Exception as e:
        logger.error(f"Error generating JWKS: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/openid-configuration", response_class=JSONResponse)
async def get_openid_configuration() -> Dict:
    """Get OpenID Connect Discovery document (RFC 8414).

    This endpoint provides metadata about the Lukhas Identity provider,
    including supported endpoints, algorithms, and capabilities.

    Returns:
        OpenID Connect Discovery document

    Note:
        This is a placeholder. Full implementation in Task 51.
    """
    # Placeholder for Task 51 - OIDC Discovery
    return {
        "issuer": "https://ai",
        "jwks_uri": "https://ai/.well-known/jwks.json",
        "authorization_endpoint": "https://ai/oauth2/authorize",
        "token_endpoint": "https://ai/oauth2/token",
        "userinfo_endpoint": "https://ai/oauth2/userinfo",
        "introspection_endpoint": "https://ai/oauth2/introspect",
        "revocation_endpoint": "https://ai/oauth2/revoke",
        "response_types_supported": ["code", "token", "id_token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": [
            _key_manager.algorithm if _key_manager else "RS256"
        ],
        "scopes_supported": ["openid", "profile", "email"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "none"],
        "claims_supported": ["sub", "iss", "aud", "exp", "iat", "lid_type", "trinity"],
    }


# Health check for JWKS system
@router.get("/jwks/health")
async def jwks_health() -> Dict:
    """Health check for JWKS/key management system.

    Returns:
        Health status with key statistics
    """
    if _key_manager is None:
        return {"status": "unhealthy", "error": "Key manager not initialized"}

    return _key_manager.health_check()
