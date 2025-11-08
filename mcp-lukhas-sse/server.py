#!/usr/bin/env python3

import logging
import os
from pathlib import Path
from typing import Any, Optional

import httpx
import uvicorn
from fastmcp import FastMCP
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
allowed_roots = os.getenv("LUKHAS_MCP_ROOTS", "").split(":") if os.getenv("LUKHAS_MCP_ROOTS") else []
write_enabled = os.getenv("WRITE_ENABLED", "false").lower() == "true"
oauth_issuer = os.getenv("OAUTH_ISSUER", "")
oauth_audience = os.getenv("OAUTH_AUDIENCE", "")
public_base_url = os.getenv("PUBLIC_BASE_URL", "")

# Validate OAuth configuration
if not oauth_issuer or not oauth_audience or not public_base_url:
    logger.error("Missing required OAuth configuration: OAUTH_ISSUER, OAUTH_AUDIENCE, and PUBLIC_BASE_URL must be set")
    raise ValueError("OAuth configuration incomplete")

# Global JWKS cache
jwks_cache = {"keys": [], "expires_at": 0}


class JWKSResponse(BaseModel):
    keys: list[dict[str, Any]]


class OIDCConfiguration(BaseModel):
    issuer: str
    jwks_uri: str
    authorization_endpoint: Optional[str] = None
    token_endpoint: Optional[str] = None


async def fetch_oidc_configuration() -> OIDCConfiguration:
    """Fetch OIDC configuration from the issuer's well-known endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(oauth_issuer)
        response.raise_for_status()
        config = response.json()
        return OIDCConfiguration(**config)


async def fetch_jwks(jwks_uri: str) -> JWKSResponse:
    """Fetch JWKS from the issuer's JWKS endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_uri)
        response.raise_for_status()
        return JWKSResponse(**response.json())


async def get_jwks_keys() -> list[dict[str, Any]]:
    """Get JWKS keys with caching."""
    import time

    current_time = time.time()

    # Check if cache is still valid (5 minutes)
    if jwks_cache["expires_at"] > current_time:
        return jwks_cache["keys"]

    try:
        # Fetch fresh OIDC configuration and JWKS
        oidc_config = await fetch_oidc_configuration()
        jwks_response = await fetch_jwks(oidc_config.jwks_uri)

        # Update cache
        jwks_cache["keys"] = jwks_response.keys
        jwks_cache["expires_at"] = current_time + 300  # 5 minutes

        return jwks_cache["keys"]
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        # Return cached keys if available
        return jwks_cache["keys"]


async def verify_jwt_token(token: str) -> Optional[dict[str, Any]]:
    """Verify JWT token and return payload if valid."""
    try:
        # Get JWKS keys
        keys = await get_jwks_keys()

        if not keys:
            logger.error("No JWKS keys available")
            return None

        # Try to verify with each key
        for key in keys:
            try:
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=["RS256"],
                    audience=oauth_audience,
                    issuer=oauth_issuer.removesuffix('/.well-known/openid-configuration')
                )
                return payload
            except JWTError:
                continue

        logger.warning("Token verification failed with all available keys")
        return None

    except Exception as e:
        logger.error(f"JWT verification error: {e}")
        return None


def is_path_allowed(path: Path) -> bool:
    """Check if path is within allowed roots and safe."""
    try:
        resolved = path.resolve()

        # Check against allowed roots
        for root in allowed_roots:
            root_path = Path(root).resolve()
            try:
                resolved.relative_to(root_path)
                return True
            except ValueError:
                continue

        return False
    except (OSError, ValueError):
        return False


class OAuth2Middleware:
    """OAuth 2.1 JWT validation middleware."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Skip auth for health check and PRM endpoint
            if request.url.path in ["/healthz", "/.well-known/oauth-protected-resource"]:
                await self.app(scope, receive, send)
                return

            # For SSE endpoint, check authorization
            if request.url.path.startswith("/sse"):
                auth_header = request.headers.get("Authorization", "")

                if not auth_header.startswith("Bearer "):
                    response = JSONResponse(
                        content={"error": "Missing or invalid Authorization header"},
                        status_code=401,
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                    await response(scope, receive, send)
                    return

                token = auth_header[7:]  # Remove "Bearer " prefix

                # Verify token
                payload = await verify_jwt_token(token)
                if not payload:
                    response = JSONResponse(
                        content={"error": "Invalid or expired token"},
                        status_code=401,
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                    await response(scope, receive, send)
                    return

        await self.app(scope, receive, send)


# Initialize FastMCP
mcp = FastMCP("LUKHAS MCP Server")


@mcp.tool()
def list_dir(path: str) -> list[str]:
    """List contents of a directory."""
    target_path = Path(path)

    if not is_path_allowed(target_path):
        raise ValueError(f"Access denied: {path}")

    if not target_path.exists():
        raise FileNotFoundError(f"Directory not found: {path}")

    if not target_path.is_dir():
        raise ValueError(f"Not a directory: {path}")

    try:
        contents = []
        for item in target_path.iterdir():
            if item.is_dir():
                contents.append(f"{item.name}/")
            else:
                contents.append(item.name)
        return sorted(contents)
    except PermissionError:
        raise PermissionError(f"Permission denied: {path}")


@mcp.tool()
def read_text(path: str) -> str:
    """Read text content from a file."""
    target_path = Path(path)

    if not is_path_allowed(target_path):
        raise ValueError(f"Access denied: {path}")

    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not target_path.is_file():
        raise ValueError(f"Not a file: {path}")

    try:
        return target_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        raise ValueError(f"File is not valid UTF-8: {path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {path}")


@mcp.tool()
def search_glob(pattern: str, root_path: str = "") -> list[str]:
    """Search for files using glob patterns."""
    if root_path:
        search_root = Path(root_path)
    else:
        # Use first allowed root as default
        if not allowed_roots:
            raise ValueError("No allowed roots configured")
        search_root = Path(allowed_roots[0])

    if not is_path_allowed(search_root):
        raise ValueError(f"Access denied: {search_root}")

    if not search_root.exists() or not search_root.is_dir():
        raise ValueError(f"Invalid search root: {search_root}")

    try:
        matches = []
        for match in search_root.glob(pattern):
            if is_path_allowed(match):
                matches.append(str(match))
        return sorted(matches)
    except Exception as e:
        raise ValueError(f"Search failed: {e}")


@mcp.tool()
def write_text(path: str, content: str) -> str:
    """Write text content to a file (if write operations are enabled)."""
    if not write_enabled:
        raise PermissionError("Write operations are disabled")

    target_path = Path(path)

    if not is_path_allowed(target_path):
        raise ValueError(f"Access denied: {path}")

    try:
        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding='utf-8')
        return f"Successfully wrote {len(content)} characters to {path}"
    except PermissionError:
        raise PermissionError(f"Permission denied: {path}")
    except Exception as e:
        raise ValueError(f"Write failed: {e}")


async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint."""
    return PlainTextResponse("OK")


async def protected_resource_metadata(request: Request) -> JSONResponse:
    """OAuth Protected Resource Metadata endpoint."""
    prm = {
        "resource": public_base_url,
        "authorization_servers": [oauth_issuer.removesuffix('/.well-known/openid-configuration')]
    }
    return JSONResponse(prm)


# Create main Starlette app
routes = [
    Route("/healthz", health_check, methods=["GET"]),
    Route("/.well-known/oauth-protected-resource", protected_resource_metadata, methods=["GET"]),
]

app = Starlette(routes=routes)

# Create OAuth-protected SSE app
sse_app = mcp.sse_app(path="/")

# Apply OAuth middleware and mount SSE app
app.add_middleware(OAuth2Middleware)
app.mount("/sse", sse_app)


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=True
    )
