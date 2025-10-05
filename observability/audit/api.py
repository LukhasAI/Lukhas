"""
FastAPI endpoints for audit trail submission and retrieval.
Includes signed permalink generation and consent-aware redaction.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request

from .links import mint_signed_query, verify_signed_query
from .models import DecisionTrace, EvidenceLink, GovernanceEvent, TraceSpan
from .redaction import mask_pii, viewer_allows_scope
from .storage import fetch_decision_trace, fetch_jsons_by_trace, write_json

REQUIRE_SIGNED = os.getenv("AUDIT_REQUIRE_SIGNED", "false").lower() in {"1", "true", "yes"}
DEFAULT_SCOPE = os.getenv("AUDIT_DEFAULT_SCOPE", "default")

router = APIRouter(prefix="/audit", tags=["audit"])


@router.post("/trace", status_code=202)
async def submit_trace(trace: DecisionTrace) -> Dict[str, Any]:
    """
    Submit a decision trace for audit storage.

    Args:
        trace: Decision trace object

    Returns:
        Confirmation with trace_id
    """
    await write_json("decision_trace", {"id": trace.trace_id, **trace.model_dump()})
    return {"ok": True, "trace_id": trace.trace_id}


@router.post("/span", status_code=202)
async def submit_span(span: TraceSpan) -> Dict[str, Any]:
    """
    Submit a trace span for audit storage.

    Args:
        span: Trace span object

    Returns:
        Confirmation with span_id
    """
    await write_json("trace_span", {"id": span.span_id, **span.model_dump()})
    return {"ok": True, "span_id": span.span_id}


@router.post("/evidence", status_code=202)
async def submit_evidence(e: EvidenceLink) -> Dict[str, Any]:
    """
    Submit evidence link for audit storage.

    Args:
        e: Evidence link object

    Returns:
        Confirmation
    """
    await write_json("evidence_link", {"id": f"{e.span_id}:{e.uri_or_key}", **e.model_dump()})
    return {"ok": True}


@router.post("/governance", status_code=202)
async def submit_governance(event: GovernanceEvent) -> Dict[str, Any]:
    """
    Submit governance event for audit storage.

    Args:
        event: Governance event object

    Returns:
        Confirmation with event_id
    """
    await write_json("governance_event", {"id": event.event_id, **event.model_dump()})
    return {"ok": True, "event_id": event.event_id}


@router.post("/link")
async def mint_link(body: Dict[str, Any], request: Request) -> Dict[str, Any]:
    """
    Generate a short-lived signed permalink for viewing a trace.

    Args:
        body: { trace_id: str, ttl_seconds?: int }
        request: FastAPI request (for viewer identity)

    Returns:
        { url: str } - Signed URL for audit trail viewer

    Example:
        POST /audit/link
        { "trace_id": "abc123", "ttl_seconds": 300 }
        → { "url": "/audit/trace/abc123?trace=...&viewer=...&exp=...&sig=..." }
    """
    trace_id = body.get("trace_id")
    if not trace_id:
        raise HTTPException(400, "trace_id required")

    ttl = int(body.get("ttl_seconds") or 300)
    viewer = getattr(request.state, "viewer_id", None) or request.client.host or "anon"
    query = mint_signed_query(trace_id, viewer, ttl)

    return {"url": f"/audit/trace/{trace_id}?{query}"}


@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str, request: Request) -> Dict[str, Any]:
    """
    Retrieve complete audit trail for a trace with consent-aware redaction.

    Args:
        trace_id: Trace identifier
        request: FastAPI request (for signature verification and scopes)

    Returns:
        Complete audit trail with spans, evidence, governance, and feedback

    Security:
        - Verifies HMAC signature when AUDIT_REQUIRE_SIGNED=true
        - Applies consent-aware redaction based on viewer scopes
        - Masks PII in evidence excerpts when scope is insufficient
    """
    # Verify signed query when required
    if REQUIRE_SIGNED:
        params = dict(request.query_params)
        ok, why = verify_signed_query(trace_id, params)
        if not ok:
            raise HTTPException(403, f"invalid link: {why}")
        viewer_id = params.get("viewer")
    else:
        viewer_id = getattr(request.state, "viewer_id", None) or request.client.host or "anon"

    # Extract viewer scopes from header or query
    raw_scopes = request.headers.get("X-Viewer-Scopes", DEFAULT_SCOPE)
    viewer_scopes: List[str] = [s.strip() for s in raw_scopes.split(",") if s.strip()]

    # Fetch trace data
    trace = await fetch_decision_trace(trace_id)
    if not trace:
        raise HTTPException(404, "trace not found")

    spans = await fetch_jsons_by_trace("trace_span", trace_id, order_by="ts_start")
    evidence = await fetch_jsons_by_trace("evidence_link", trace_id)
    governance = await fetch_jsons_by_trace("governance_event", trace_id)
    feedback = await fetch_jsons_by_trace("feedback_event", trace_id)

    # Apply consent-aware redaction to evidence
    redacted_evidence = []
    for e in evidence:
        e = dict(e)
        scope = e.get("consent_scope") or DEFAULT_SCOPE

        if not viewer_allows_scope(viewer_scopes, scope):
            # Viewer doesn't have required scope - redact
            if e.get("excerpt"):
                e["excerpt"] = mask_pii(e["excerpt"])
            e["redacted"] = True
            # Hide direct URI; force signed proxy if needed
            e["uri_or_key"] = f"/audit/proxy/{trace_id}/evidence?span_id={e.get('span_id')}&key={e.get('sha256')}"

        redacted_evidence.append(e)

    # Group evidence by span for UI convenience
    evidence_by_span: Dict[str, list] = {}
    for ev in redacted_evidence:
        evidence_by_span.setdefault(ev.get("span_id", "?"), []).append(ev)

    return {
        "trace": trace,
        "viewer": {"id": viewer_id, "scopes": viewer_scopes},
        "spans": spans,
        "evidence_by_span": evidence_by_span,
        "governance_events": governance,
        "feedback_events": feedback,
    }
