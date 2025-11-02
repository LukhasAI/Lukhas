"""Authentication helpers for the OpenAI-compatible façade."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Mapping, MutableMapping, Optional, Sequence

from fastapi import Header, HTTPException, status

try:
    from core.interfaces.api.v1.v1.common.api_key_cache import (  # type: ignore
        ApiKeyMetadata,
        api_key_cache,
    )
except ModuleNotFoundError:  # pragma: no cover - offline fallback
    ApiKeyMetadata = None  # type: ignore[assignment]
    api_key_cache = None  # type: ignore[assignment]

try:
    from core.policy_guard import PolicyGuard  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - offline fallback

    class _StubDecision:
        def __init__(self, allow: bool = True, reason: str = "policy guard stub allow") -> None:
            self.allow = allow
            self.reason = reason

    class PolicyGuard:  # type: ignore
        """Minimal PolicyGuard stub for docs-only environments."""

        def __init__(self, lane: str | None = None) -> None:
            self.lane = (lane or os.getenv("LUKHAS_LANE", "experimental")).lower()
            self.config = type("Config", (), {"allowed_kinds": set()})()

        def check_replay(self, event_kind: str, **_: object) -> _StubDecision:
            self.config.allowed_kinds.add(event_kind)
            return _StubDecision()


INVALID_API_KEY_ERROR: Mapping[str, Mapping[str, str]] = {
    "error": {
        "type": "invalid_api_key",
        "message": "Missing or invalid API key",
        "code": "invalid_api_key",
    }
}


def _insufficient_permissions_error(missing: Sequence[str]) -> Mapping[str, object]:
    scopes = sorted(set(missing))
    scope_list = ", ".join(scopes)
    return {
        "error": {
            "type": "insufficient_permissions",
            "message": f"Missing required scope(s): {scope_list}",
            "code": "insufficient_permissions",
            "missing_scopes": scopes,
        }
    }


def _policy_denied_error(reason: str) -> Mapping[str, str]:
    return {
        "error": {
            "type": "policy_denied",
            "message": reason,
            "code": "policy_denied",
        }
    }


@dataclass(frozen=True)
class TokenClaims:
    """Lightweight view over derived token claims."""

    token_type: str
    owner: str
    org_id: str
    scopes: tuple[str, ...]
    lane: str
    token_hash: str = field(repr=False)
    project_id: Optional[str] = None
    subject: Optional[str] = None

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes

    def require_scopes(self, required_scopes: Iterable[str]) -> tuple[str, ...]:
        missing = tuple(sorted({scope for scope in required_scopes if scope not in self.scopes}))
        return missing


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _metadata_for_token(token: str) -> "ApiKeyMetadata":
    if api_key_cache is None or ApiKeyMetadata is None:  # pragma: no cover - fallback safety
        raise RuntimeError("API key cache unavailable; cannot verify tokens")

    metadata = api_key_cache.lookup(token)
    if metadata is None:
        raise ValueError("unknown token")

    if not metadata.is_active():
        if getattr(metadata, "revoked", False):
            raise PermissionError("token revoked")
        expires_at = getattr(metadata, "expires_at", None)
        if expires_at:
            if isinstance(expires_at, datetime):
                expires_at = expires_at.astimezone(timezone.utc)
            raise PermissionError(f"token expired at {expires_at}")
        raise PermissionError("token inactive")

    return metadata


def _string_attr(metadata: "ApiKeyMetadata", *keys: str) -> Optional[str]:
    attributes = getattr(metadata, "attributes", {}) or {}
    for key in keys:
        value = attributes.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
        else:
            return str(value)
    return None


def _classify_token(token: str) -> tuple[str, str]:
    lowered = token.lower()
    if lowered.startswith("sk-lukhas-"):
        parts = token.split("-")
        owner = parts[2] if len(parts) >= 3 else "default"
        return "pat", owner.lower()
    if lowered.startswith(("st-lukhas-", "sv-lukhas-", "svc-lukhas-", "service-lukhas-")):
        parts = token.split("-")
        owner = parts[2] if len(parts) >= 3 else "service"
        return "service", owner.lower()
    return "unknown", "default"


def _derive_org(owner: str, token_type: str) -> str:
    if token_type == "service":
        return f"service:{owner}"
    if owner.startswith("org") or owner.startswith("tenant"):
        return owner
    return os.getenv("LUKHAS_DEFAULT_ORG", "lukhas")


def _scopes_for(token_type: str, owner: str) -> tuple[str, ...]:
    base_scopes = {"api.read", "api.models"}
    if token_type == "service":
        service_scopes = base_scopes | {"api.responses", "api.embeddings", "api.service"}
        if owner not in {"router", "relay"}:
            service_scopes.add("api.jobs")
        return tuple(sorted(service_scopes))
    tier_scopes = base_scopes | {"api.responses", "api.embeddings"}
    if owner in {"premium", "enterprise"}:
        tier_scopes |= {"api.write", "api.admin"}
    else:
        tier_scopes.add("api.write")
    return tuple(sorted(tier_scopes))


def _lane_for(owner: str, token_type: str) -> str:
    if token_type == "service":
        return "prod"
    mapping: MutableMapping[str, str] = {
        "basic": "experimental",
        "standard": "candidate",
        "premium": "prod",
        "enterprise": "prod",
    }
    if owner.startswith("org") or owner.startswith("tenant"):
        return "candidate"
    return mapping.get(owner, os.getenv("LUKHAS_LANE", "candidate").lower())


def _risk_for(token_type: str, owner: str) -> float:
    if token_type == "service":
        return 0.15
    if owner == "basic":
        return 0.05
    if owner in {"standard", "org1", "org2", "tenant1", "tenant2"}:
        return 0.1
    if owner in {"premium", "enterprise"}:
        return 0.2
    return 0.15


def _resolve_token_type(token: str, metadata: "ApiKeyMetadata") -> str:
    hint = _string_attr(metadata, "token_type", "kind", "type", "category")
    if hint:
        return hint.lower()
    token_type, _ = _classify_token(token)
    return token_type if token_type != "unknown" else "pat"


def _resolve_owner(token: str, metadata: "ApiKeyMetadata") -> str:
    hint = _string_attr(metadata, "owner", "token_owner", "user", "user_id")
    if hint:
        return hint.lower()
    _, owner = _classify_token(token)
    if owner != "default":
        return owner
    fallback = getattr(metadata, "user_id", None)
    if fallback:
        return str(fallback).lower()
    return "default"


def _scopes_from_metadata(token_type: str, owner: str, metadata: "ApiKeyMetadata") -> tuple[str, ...]:
    scopes = tuple(sorted(getattr(metadata, "scopes", ()) or ()))
    if scopes:
        return scopes

    attr = getattr(metadata, "attributes", {}).get("scopes")
    if isinstance(attr, (list, tuple, set)):
        raw_scopes = {str(scope).strip() for scope in attr if str(scope).strip()}
        if raw_scopes:
            return tuple(sorted(raw_scopes))

    return _scopes_for(token_type, owner)


def _lane_from_metadata(token_type: str, owner: str, metadata: "ApiKeyMetadata") -> str:
    lane_hint = _string_attr(metadata, "lane", "deployment_lane", "lane_hint")
    if lane_hint:
        return lane_hint.lower()

    tier = getattr(metadata, "tier", None)
    if tier is not None:
        try:
            tier_value = int(tier)
        except (TypeError, ValueError):
            tier_value = None
        else:
            if tier_value >= 3:
                return "prod"
            if tier_value == 2:
                return "candidate"
            if tier_value <= 1:
                return "experimental"

    return _lane_for(owner, token_type)


def _org_from_metadata(owner: str, token_type: str, metadata: "ApiKeyMetadata") -> str:
    org_hint = _string_attr(metadata, "org_id", "organization", "tenant", "org")
    if org_hint:
        return org_hint
    return _derive_org(owner, token_type)


def _risk_from_metadata(token_type: str, owner: str, metadata: "ApiKeyMetadata") -> float:
    risk_hint = _string_attr(metadata, "risk", "risk_level", "risk_score")
    if risk_hint:
        try:
            return float(risk_hint)
        except ValueError:
            pass
    numeric_risk = getattr(metadata, "attributes", {}).get("risk_level")
    if isinstance(numeric_risk, (int, float)):
        return float(numeric_risk)
    return _risk_for(token_type, owner)


def _project_from_metadata(project_id: str | None, metadata: "ApiKeyMetadata") -> str | None:
    if project_id:
        return project_id
    return _string_attr(metadata, "project_id", "default_project_id", "project")


def verify_token_with_policy(
    token: str,
    *,
    required_scopes: Sequence[str] | None = None,
    project_id: str | None = None,
) -> TokenClaims:
    """Validate a token and derive its claims using PolicyGuard for gating."""
    token = (token or "").strip()
    if len(token) < 8:
        raise ValueError("token too short")

    metadata = _metadata_for_token(token)
    token_type = _resolve_token_type(token, metadata)
    owner = _resolve_owner(token, metadata)
    if token_type == "unknown":
        raise ValueError("unsupported token format")

    scopes = _scopes_from_metadata(token_type, owner, metadata)
    lane = _lane_from_metadata(token_type, owner, metadata)
    org_id = _org_from_metadata(owner, token_type, metadata)
    resolved_project_id = _project_from_metadata(project_id, metadata)
    guard = PolicyGuard(lane=lane)
    guard.config.allowed_kinds.add("token_auth")

    decision = guard.check_replay(
        event_kind="token_auth",
        payload={
            "token_owner": owner,
            "token_type": token_type,
            "scopes": scopes,
            "project_id": resolved_project_id,
            "token_subject": getattr(metadata, "user_id", None),
            "token_source": getattr(metadata, "attributes", {}).get("source"),
        },
        risk_level=_risk_from_metadata(token_type, owner, metadata),
        source_lane=lane if token_type == "service" else None,
    )
    if not decision.allow:
        raise PermissionError(decision.reason)

    claims = TokenClaims(
        token_type=token_type,
        owner=owner,
        org_id=org_id,
        scopes=scopes,
        lane=lane,
        token_hash=_hash_token(token),
        project_id=resolved_project_id,
        subject=getattr(metadata, "user_id", None),
    )

    if required_scopes:
        missing = claims.require_scopes(required_scopes)
        if missing:
            raise PermissionError(f"missing scopes: {', '.join(missing)}")

    return claims


def require_bearer(
    authorization: str | None = Header(default=None),
    *,
    required_scopes: Sequence[str] | None = None,
    project_id: str | None = Header(default=None, alias="X-Lukhas-Project"),
) -> TokenClaims:
    """FastAPI dependency that validates Bearer tokens."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_API_KEY_ERROR)

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_API_KEY_ERROR)

    try:
        return verify_token_with_policy(token, required_scopes=required_scopes, project_id=project_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_API_KEY_ERROR) from None
    except PermissionError as exc:
        message = str(exc)
        if message.startswith("missing scopes") and required_scopes:
            missing = [scope.strip() for scope in message.split(":", 1)[-1].split(",")]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=_insufficient_permissions_error([scope for scope in missing if scope]),
            ) from None
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_policy_denied_error(message or "Token denied by policy"),
        ) from None


__all__ = ["TokenClaims", "require_bearer", "verify_token_with_policy"]
