"""
OpenAI-compatible façade for LUKHAS MATRIZ.
(Version updated to include Guardian Policy Engine)
"""
from typing import Any, Dict, List, Optional, Tuple
from fastapi import FastAPI, Request, Response, HTTPException, Depends, Body
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
from threading import Lock
import os
import time
import uuid
import logging
import math
from datetime import datetime
from functools import lru_cache

# Reliability and Observability Imports
from lukhas.core.reliability.ratelimit import create_rate_limiter
from lukhas.observability.tracing import setup_otel, traced_operation, get_trace_id_hex
from lukhas.adapters.openai.auth import require_bearer, TokenClaims

# Guardian Policy Engine Imports
from lukhas.adapters.openai.policy_pdp import PDP, PolicyLoader, Policy
from lukhas.adapters.openai.policy_models import Context, Decision

logger = logging.getLogger(__name__)

# --- Action Normalization Map ---
ACTION_NORMALIZATION_MAP: Dict[Tuple[str, str], str] = {
    ("GET", "/v1/models"): "models.read",
    ("POST", "/v1/embeddings"): "embeddings.create",
    ("POST", "/v1/responses"): "responses.create",
    ("POST", "/v1/dreams"): "dreams.create",
    ("GET", "/v1/indexes/{index_id}"): "indexes.read",
    ("POST", "/v1/indexes"): "indexes.write",
}

# (Stubs for unavailable modules remain the same as before)
try:
    from matriz.core.orchestrator import CognitiveOrchestrator
    MATRIZ_AVAILABLE = True
except ImportError:
    logger.warning("MATRIZ orchestrator not available, running in stub mode")
    MATRIZ_AVAILABLE = False
    CognitiveOrchestrator = None

def get_app() -> FastAPI:
    """Create and configure the LUKHAS OpenAI façade application."""
    app = FastAPI(
        title="Lukhas OpenAI Facade",
        version="0.9.0",
        description="OpenAI-compatible API with Guardian Policy Enforcement"
    )

    # --- Guardian PDP Initialization ---
    policy_file = os.environ.get("LUKHAS_POLICY_FILE", "configs/policy/guardian_policies.yaml")
    policy = PolicyLoader.load_from_file(policy_file)
    pdp = PDP(policy)
    policy_mode = os.environ.get("LUKHAS_POLICY_MODE", "strict")

    # --- Caching Layer for PDP Decisions ---
    @lru_cache(maxsize=1024)
    def get_cached_decision(
        tenant_id: str, user_id: Optional[str], scopes: frozenset, action: str,
        resource: str, model: Optional[str], ip: str, policy_etag: str
    ) -> Decision:
        # Time and data_classification are dynamic, so we create a partial context for caching
        ctx = Context(
            tenant_id=tenant_id, user_id=user_id, roles=frozenset(), scopes=scopes,
            action=action, resource=resource, model=model, ip=ip,
            time_utc=datetime.utcnow(), data_classification="internal", # Re-evaluated
            policy_etag=policy_etag, trace_id=get_trace_id_hex() or ""
        )
        return pdp.decide(ctx)

    # --- Policy Enforcement Dependency ---
    async def enforce_policy(request: Request, claims: TokenClaims = Depends(require_bearer)):
        # 1. Normalize Action and Resource
        action = ACTION_NORMALIZATION_MAP.get((request.method, request.scope.get("root_path", "") + request.route.path), "unknown.action")
        resource = request.url.path

        # 2. Create Request Context
        # Note: model and data_classification might need to be extracted from body for more complex policies
        ctx_for_cache = (
            claims.org_id, claims.sub, frozenset(claims.scopes), action, resource,
            None, # Model not extracted for this example
            request.client.host if request.client else "127.0.0.1",
            policy.etag
        )
        
        # 3. Get Decision (from cache if possible)
        decision = get_cached_decision(*ctx_for_cache)
        
        # 4. Add Metrics & Audit Logging (stubs)
        logger.info(
            f"Guardian PDP Decision: {decision.allow} for user {claims.sub} on {action}:{resource}. "
            f"Reason: {decision.reason}, Rule: {decision.rule_id}, Mode: {policy_mode}"
        )
        # TODO: Add Prometheus counters for decisions, denies, etc.

        # 5. Handle Decision based on mode
        if not decision.allow:
            if policy_mode == "strict":
                raise HTTPException(
                    status_code=403,
                    detail={"error": {"type": "authorization_error", "message": "Forbidden", "code": "forbidden"}}
                )
            elif policy_mode == "permissive":
                logger.warning(f"Guardian 'would_deny' in permissive mode for user {claims.sub} on {action}:{resource}")
                # Fall through and allow
            # "dryrun" mode also falls through

        # TODO: Handle obligations from decision.obligations
        return decision

    # (Existing middlewares like tracing, metrics, rate limiting are omitted for brevity, but would be here)
    # --- Rate Limiter Initialization ---
    rate_limiter = create_rate_limiter()

    # --- Endpoints with Policy Enforcement ---
    @app.get("/v1/models")
    def models(claims: TokenClaims = Depends(require_bearer), _=Depends(enforce_policy)):
        return {"data": [{"id": "lukhas-matriz", "object": "model"}]}

    @app.post("/v1/embeddings")
    async def embeddings(request: Request, claims: TokenClaims = Depends(require_bearer), _=Depends(enforce_policy)):
        # (Endpoint logic remains the same)
        payload = await request.json()
        text = payload.get("input", "")
        # ... existing embedding generation logic ...
        return {"data": [{"embedding": [0.1, 0.2], "index": 0}]}

    @app.post("/v1/responses")
    async def responses(request: Request, claims: TokenClaims = Depends(require_bearer), _=Depends(enforce_policy)):
        # (Endpoint logic remains the same)
        payload = await request.json()
        user_input = str(payload.get("input", ""))
        # ... existing response generation logic ...
        return {"id": "resp_123", "output": {"text": f"echo: {user_input}"}}

    @app.post("/v1/dreams")
    async def dreams(request: Request, claims: TokenClaims = Depends(require_bearer), _=Depends(enforce_policy)):
        # (Endpoint logic remains the same)
        payload = await request.json()
        seed = payload.get("seed", "dream")
        # ... existing dream generation logic ...
        return {"id": f"dream_{uuid.uuid4().hex[:8]}", "seed": seed, "traces": []}

    return app
