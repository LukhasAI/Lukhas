"""Tests for the REST API authentication middleware."""

from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi import HTTPException, status

ROOT = Path(__file__).resolve().parents[7]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def auth_components():
    """Load middleware and cache classes lazily to avoid import-time failures."""

    import types

    interfaces_pkg = sys.modules.setdefault("interfaces", types.ModuleType("interfaces"))
    interfaces_pkg.__path__ = []  # pragma: no cover - stub path for namespace

    interfaces_api_pkg = sys.modules.setdefault("interfaces.api", types.ModuleType("interfaces.api"))
    interfaces_api_pkg.API_PREFIX = "/api/v1"
    interfaces_api_pkg.__path__ = []

    sys.modules.setdefault("interfaces.api.v1", types.ModuleType("interfaces.api.v1"))
    sys.modules.setdefault("interfaces.api.v1.rest", types.ModuleType("interfaces.api.v1.rest"))

    routers_module = types.ModuleType("interfaces.api.v1.rest.routers")
    routers_module.health_router = object()
    routers_module.metrics_router = object()
    routers_module.process_router = object()
    routers_module.tasks_router = object()
    sys.modules.setdefault("interfaces.api.v1.rest.routers", routers_module)

    import labs  # ensure base package is registered

    import core
    import core.interfaces
    import core.interfaces.api
    import core.interfaces.api.v1

    core_common_stub = sys.modules.setdefault("labs.core.common", types.ModuleType("labs.core.common"))

    def _tier_noop(level=None, fallback=None):
        def decorator(func):
            return func

        return decorator

    if not hasattr(core_common_stub, "lukhas_tier_required"):
        core_common_stub.lukhas_tier_required = _tier_noop

    common_pkg = sys.modules.setdefault(
        "labs.core.interfaces.api.v1.common",
        types.ModuleType("labs.core.interfaces.api.v1.common"),
    )
    common_pkg.__path__ = [str(ROOT / "labs" / "core" / "interfaces" / "api" / "v1" / "common")]

    api_key_cache_path = ROOT / "labs" / "core" / "interfaces" / "api" / "v1" / "common" / "api_key_cache.py"
    api_spec = importlib.util.spec_from_file_location(
        "labs.core.interfaces.api.v1.common.api_key_cache", api_key_cache_path
    )
    assert api_spec and api_spec.loader
    api_module = importlib.util.module_from_spec(api_spec)
    sys.modules[api_spec.name] = api_module
    api_spec.loader.exec_module(api_module)

    common_pkg.ApiKeyCache = api_module.ApiKeyCache
    common_pkg.ApiKeyMetadata = api_module.ApiKeyMetadata
    common_pkg.api_key_cache = api_module.api_key_cache
    common_pkg.__all__ = ["ApiKeyCache", "ApiKeyMetadata", "api_key_cache"]

    rest_pkg = sys.modules.setdefault(
        "labs.core.interfaces.api.v1.rest",
        types.ModuleType("labs.core.interfaces.api.v1.rest"),
    )
    rest_pkg.__path__ = [str(ROOT / "labs" / "core" / "interfaces" / "api" / "v1" / "rest")]

    middleware_path = ROOT / "labs" / "core" / "interfaces" / "api" / "v1" / "rest" / "middleware.py"
    spec = importlib.util.spec_from_file_location("labs.core.interfaces.api.v1.rest.middleware", middleware_path)
    assert spec and spec.loader  # pragma: no cover - sanity check
    middleware_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = middleware_module
    spec.loader.exec_module(middleware_module)

    common_package = importlib.import_module("labs.core.interfaces.api.v1.common")
    return middleware_module.AuthMiddleware, common_package.ApiKeyCache


@pytest.fixture(autouse=True)
def clear_api_key_env(monkeypatch):
    """Ensure registry-related environment variables are isolated per test."""

    for env in [
        "LUKHAS_API_KEY_REGISTRY_PATH",
        "LUKHAS_API_KEY_REGISTRY",
        "LUKHAS_API_KEY_HASHES",
    ]:
        monkeypatch.delenv(env, raising=False)


@pytest.fixture
def registry_path(tmp_path):
    """Helper to create an API key registry file."""

    def _create(entries):
        data = {"api_keys": entries}
        path = tmp_path / "api_keys.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return str(path)

    return _create


@pytest.mark.asyncio
async def test_validate_api_key_from_registry_success(registry_path, auth_components):
    """API keys defined in the registry should resolve with metadata."""

    valid_key = "luk_prod_1234567890abcdef1234567890abcdefabcd"
    path = registry_path(
        [
            {
                "key": valid_key,
                "user_id": "lukhas_developer",
                "tier": 3,
                "scopes": ["dream:read", "dream:write"],
            }
        ]
    )

    AuthMiddleware, ApiKeyCacheCls = auth_components
    cache = ApiKeyCacheCls(registry_path=path, refresh_interval=0)
    middleware = AuthMiddleware(key_cache=cache)

    result = await middleware.validate_api_key(valid_key)

    assert result["user_id"] == "lukhas_developer"
    assert result["tier_level"] == 3
    assert tuple(result["scopes"]) == ("dream:read", "dream:write")


@pytest.mark.asyncio
async def test_validate_api_key_revoked_raises(registry_path, auth_components):
    """Revoked keys should be rejected with a 403 status."""

    revoked_key = "luk_prod_abcdefabcdefabcdefabcdefabcdefabcd"
    path = registry_path(
        [
            {
                "key": revoked_key,
                "user_id": "revoked_user",
                "tier": 2,
                "revoked": True,
            }
        ]
    )

    AuthMiddleware, ApiKeyCacheCls = auth_components
    cache = ApiKeyCacheCls(registry_path=path, refresh_interval=0)
    middleware = AuthMiddleware(key_cache=cache)

    with pytest.raises(HTTPException) as exc:
        await middleware.validate_api_key(revoked_key)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "API key revoked"


@pytest.mark.asyncio
async def test_validate_api_key_expired_raises(registry_path, auth_components):
    """Expired keys should fail even when present in the registry."""

    expired_key = "luk_prod_feedfacefeedfacefeedfacefeedface"
    expiry = datetime.now(timezone.utc) - timedelta(minutes=5)
    path = registry_path(
        [
            {
                "key": expired_key,
                "user_id": "expired_user",
                "tier": 2,
                "expires_at": expiry.isoformat(),
            }
        ]
    )

    AuthMiddleware, ApiKeyCacheCls = auth_components
    cache = ApiKeyCacheCls(registry_path=path, refresh_interval=0)
    middleware = AuthMiddleware(key_cache=cache)

    with pytest.raises(HTTPException) as exc:
        await middleware.validate_api_key(expired_key)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "API key expired"


@pytest.mark.asyncio
async def test_validate_api_key_not_recognized_when_registry_active(registry_path, auth_components):
    """When the registry is configured an unknown key should be rejected."""

    valid_key = "luk_prod_facefeedfacefeedfacefeedfacefeed"
    path = registry_path(
        [
            {
                "key": valid_key,
                "user_id": "lukhas_developer",
                "tier": 3,
            }
        ]
    )

    AuthMiddleware, ApiKeyCacheCls = auth_components
    cache = ApiKeyCacheCls(registry_path=path, refresh_interval=0)
    middleware = AuthMiddleware(key_cache=cache)

    with pytest.raises(HTTPException) as exc:
        await middleware.validate_api_key("luk_prod_unknown000000000000000000000000")

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "API key not recognized"


@pytest.mark.asyncio
async def test_validate_api_key_prefix_fallback_when_not_configured(auth_components):
    """Without a registry the legacy prefix mapping should remain available."""

    fallback_key = "sk_live_admin_1234567890abcdef1234567890abcdef"

    AuthMiddleware, ApiKeyCacheCls = auth_components
    cache = ApiKeyCacheCls(refresh_interval=0)
    middleware = AuthMiddleware(key_cache=cache)

    result = await middleware.validate_api_key(fallback_key)

    assert result["tier_level"] == 4
    assert result["auth_method"] == "api_key"
    assert result["user_id"].endswith(fallback_key[-8:])
    assert result["scopes"] == ()
