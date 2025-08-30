# path: qi/feedback/ingest_api.py
from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime
from typing import Any

from fastapi import BackgroundTasks, Body, FastAPI, HTTPException, Query
from pydantic import ValidationError

from qi.crypto.pqc_signer import sign_dilithium
from qi.feedback.proposals import ProposalMapper
from qi.feedback.schema import FeedbackCard
from qi.feedback.store import get_store
from qi.feedback.triage import get_triage

app = FastAPI(title="LUKHAS Feedback Ingestion API", version="0.1.0")

# ------------- Ingest Endpoints -------------


@app.post("/feedback/ingest")
async def ingest_feedback(
    user_id: str = Body(..., description="User identifier (will be HMACed)"),
    session_id: str = Body(..., description="Session identifier (will be HMACed)"),
    task: str = Body(..., description="Task type"),
    jurisdiction: str = Body("global", description="Jurisdiction"),
    satisfaction: float = Body(..., ge=0.0, le=1.0, description="Satisfaction score"),
    issues: list[str] = Body(default=[], description="Issue types"),
    note: str | None = Body(None, description="User note (will be HMACed)"),
    style: str | None = Body(None, description="Proposed style"),
    threshold_delta: float | None = Body(None, description="Proposed threshold adjustment"),
) -> dict[str, Any]:
    """Ingest a feedback card with HMAC redaction and validation."""
    try:
        store = get_store()

        # Build feedback card
        fc_data = {
            "fc_id": str(uuid.uuid4()),
            "ts": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,  # Will be HMACed by store
            "session_id": session_id,  # Will be HMACed by store
            "context": {
                "task": task,
                "jurisdiction": jurisdiction,
                "policy_pack": os.environ.get("POLICY_PACK", "global@2025-08-01"),
                "model_version": os.environ.get("MODEL_VERSION", "lukhas-qiv2.1"),
            },
            "feedback": {
                "satisfaction": satisfaction,
                "issues": issues,
                "note": note,  # Will be HMACed by store
            },
        }

        # Add proposed tuning if provided
        if style or threshold_delta is not None:
            fc_data["proposed_tuning"] = {}
            if style:
                fc_data["proposed_tuning"]["style"] = style
            if threshold_delta is not None:
                fc_data["proposed_tuning"]["threshold_delta"] = threshold_delta

        # Add constraints
        fc_data["constraints"] = {"ethics_bound": True, "compliance_bound": True}

        # Validate with schema
        try:
            # This will trigger validation but we'll use the dict for storage
            FeedbackCard(**fc_data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f"Invalid feedback data: {e!s}")

        # Sign the feedback
        canonical = json.dumps(fc_data, sort_keys=True, separators=(",", ":"))
        signature = sign_dilithium(canonical.encode())
        fc_data["attestation"] = signature

        # Append to JSONL (applies HMAC redaction)
        fc_id = store.append_feedback(fc_data)

        return {"fc_id": fc_id, "status": "ingested", "timestamp": time.time()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e!s}")


@app.get("/feedback/list")
async def list_feedback(
    task: str | None = Query(None, description="Filter by task"),
    jurisdiction: str | None = Query(None, description="Filter by jurisdiction"),
    limit: int = Query(100, le=1000, description="Maximum results"),
) -> dict[str, Any]:
    """List recent feedback cards with optional filters."""
    try:
        store = get_store()
        feedback = store.read_feedback(
            limit=limit, task_filter=task, jurisdiction_filter=jurisdiction
        )

        # Compute summary statistics
        if feedback:
            satisfactions = [fc.get("feedback", {}).get("satisfaction", 0.5) for fc in feedback]
            avg_satisfaction = sum(satisfactions) / len(satisfactions)

            issue_counts = {}
            for fc in feedback:
                for issue in fc.get("feedback", {}).get("issues", []):
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
        else:
            avg_satisfaction = None
            issue_counts = {}

        return {
            "feedback": feedback,
            "count": len(feedback),
            "filters": {"task": task, "jurisdiction": jurisdiction},
            "summary": {"avg_satisfaction": avg_satisfaction, "issue_distribution": issue_counts},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List failed: {e!s}")


# ------------- Clustering Endpoints -------------


@app.post("/feedback/cluster")
async def run_clustering(
    background_tasks: BackgroundTasks, limit: int = Query(1000, description="Feedback to process")
) -> dict[str, Any]:
    """Run clustering job (can be triggered as offline job)."""
    try:
        # Run triage immediately for API call
        triage = get_triage()
        stats = triage.run_triage(limit=limit)

        # Also schedule weekly digest generation in background
        background_tasks.add_task(generate_weekly_digest)

        return {"status": "completed", "stats": stats, "timestamp": time.time()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering failed: {e!s}")


@app.get("/feedback/clusters")
async def get_clusters(
    task: str | None = Query(None, description="Filter by task"),
) -> dict[str, Any]:
    """Get computed clusters."""
    try:
        store = get_store()
        clusters = store.read_clusters()

        if task:
            clusters = [c for c in clusters if c.get("task") == task]

        return {"clusters": clusters, "count": len(clusters), "filter": {"task": task}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cluster retrieval failed: {e!s}")


# ------------- Promotion Endpoints -------------


@app.post("/feedback/promote")
async def promote_to_proposal(
    fc_id: str | None = Query(None, description="Feedback card ID"),
    cluster_id: str | None = Query(None, description="Cluster ID"),
    target_file: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
) -> dict[str, Any]:
    """Promote a feedback card or cluster to a change proposal."""
    try:
        if not fc_id and not cluster_id:
            raise HTTPException(status_code=400, detail="Either fc_id or cluster_id required")

        mapper = ProposalMapper()

        if cluster_id:
            proposal_id = mapper.promote_cluster(cluster_id, target_file)
        else:
            proposal_id = mapper.promote_feedback_card(fc_id, target_file)

        if not proposal_id:
            raise HTTPException(status_code=400, detail="Could not create proposal from feedback")

        return {
            "proposal_id": proposal_id,
            "status": "queued",
            "source": "cluster" if cluster_id else "feedback_card",
            "timestamp": time.time(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Promotion failed: {e!s}")


# ------------- Digest Endpoints -------------


@app.post("/feedback/digest")
async def generate_digest() -> dict[str, Any]:
    """Generate weekly Merkle digest with signature."""
    try:
        store = get_store()
        digest = store.generate_weekly_digest()

        return {"digest": digest, "status": "generated", "timestamp": time.time()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Digest generation failed: {e!s}")


# ------------- Helper Functions -------------


def generate_weekly_digest():
    """Background task to generate weekly digest."""
    store = get_store()
    store.generate_weekly_digest()


# ------------- Health Check -------------


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "feedback_ingest",
        "version": "0.1.0",
        "timestamp": time.time(),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("FEEDBACK_PORT", "8099"))
    uvicorn.run(app, host="127.0.0.1", port=port)
