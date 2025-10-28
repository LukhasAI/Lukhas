"""Authentication helpers for the OpenAI-compatible façade."""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Iterable, Mapping, MutableMapping, Optional, Sequence

from fastapi import Header, HTTPException, status

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

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes

    def require_scopes(self, required_scopes: Iterable[str]) -> tuple[str, ...]:
        missing = tuple(sorted({scope for scope in required_scopes if scope not in self.scopes}))
        return missing


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


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

    token_type, owner = _classify_token(token)
    if token_type == "unknown":
        raise ValueError("unsupported token format")

    scopes = _scopes_for(token_type, owner)
    lane = _lane_for(owner, token_type)
    guard = PolicyGuard(lane=lane)
    guard.config.allowed_kinds.add("token_auth")

    decision = guard.check_replay(
        event_kind="token_auth",
        payload={
            "token_owner": owner,
            "token_type": token_type,
            "scopes": scopes,
            "project_id": project_id,
        },
        risk_level=_risk_for(token_type, owner),
        source_lane=lane if token_type == "service" else None,
    )
    if not decision.allow:
        raise PermissionError(decision.reason)

    claims = TokenClaims(
        token_type=token_type,
        owner=owner,
        org_id=_derive_org(owner, token_type),
        scopes=scopes,
        lane=lane,
        token_hash=_hash_token(token),
        project_id=project_id,
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
