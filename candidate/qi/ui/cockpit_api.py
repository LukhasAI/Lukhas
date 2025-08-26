# path: qi/ui/cockpit_api.py
from __future__ import annotations

import json
import os
import time

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from qi.autonomy.self_healer import apply, approve, list_proposals

# Component imports
from qi.docs.model_safety_card import generate_card, to_markdown
from qi.learning.adaptive_engine import AdaptiveLearningEngine
from qi.learning.human_adapt_engine import HumanAdaptEngine
from qi.metrics.calibration import fit_and_save, reliability_svg
from qi.ops.auto_safety_report import (
    _latest_eval,
    _mk_markdown,
    _recent_receipts,
    generate_report,
)
from qi.provenance.receipts_api import receipt_neighbors, receipt_sample

# ---- UI serving (single-file cockpit + friends) ----
COCKPIT_UI_PATH = os.environ.get("COCKPIT_UI_PATH")     # /abs/path/to/web/cockpit.html
RECEIPTS_UI_PATH = os.environ.get("RECEIPTS_UI_PATH")   # /abs/path/to/web/trace_drilldown.html
APPROVER_UI_PATH = os.environ.get("APPROVER_UI_PATH")   # /abs/path/to/web/approver_ui.html

# Safe I/O for UI files
import builtins

_ORIG_OPEN = builtins.open

# Auth
def _check_auth(token: str | None = Header(None, alias="X-Auth-Token")):
    expected = os.environ.get("COCKPIT_API_TOKEN")
    if expected and token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing auth token")

# FastAPI app
app = FastAPI(title="LUKHAS Unified Ops Cockpit", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ------------- Panel 1: Safety Card & Reports -------------

@app.get("/cockpit/safety-card")
def get_safety_card(
    model: str = Query("LUKHAS-QI"),
    version: str = Query("1.0.0"),
    policy_root: str = Query("qi/safety/policy_packs"),
    overlays: str | None = Query("qi/risk"),
    jurisdictions: str = Query("global,eu,us"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        jurs = [j.strip() for j in jurisdictions.split(",")]
        card = generate_card(
            model_name=model,
            version=version,
            policy_root=policy_root,
            overlays=overlays,
            jurisdictions=jurs
        )
        md = to_markdown(card)
        return {"card": card, "markdown": md, "generated_at": time.time()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety card generation failed: {str(e)}")

@app.get("/cockpit/safety_card.json")
def get_safety_card_json(
    model: str = Query("LUKHAS-QI"),
    version: str = Query("0.9.0"),
    policy_root: str = Query("qi/safety/policy_packs"),
    overlays: str | None = Query("qi/risk"),
    jurisdictions: str = Query("global,eu,us"),
    include_appendix: bool = Query(False),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        jurs = [j.strip() for j in jurisdictions.split(",")]
        card = generate_card(
            model_name=model,
            version=version,
            policy_root=policy_root,
            overlays=overlays,
            jurisdictions=jurs
        )

        if include_appendix:
            # Add nightly report as appendix
            try:
                report_md = _mk_markdown(policy_root, overlays, 500)
                card["_appendix_nightly_report_md"] = report_md
            except:
                card["_appendix_nightly_report_md"] = "(appendix generation failed)"

        return card
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety card JSON generation failed: {str(e)}")

@app.get("/cockpit/safety_card.md")
def get_safety_card_markdown(
    model: str = Query("LUKHAS-QI"),
    version: str = Query("0.9.0"),
    policy_root: str = Query("qi/safety/policy_packs"),
    overlays: str | None = Query("qi/risk"),
    jurisdictions: str = Query("global,eu,us"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        jurs = [j.strip() for j in jurisdictions.split(",")]
        card = generate_card(
            model_name=model,
            version=version,
            policy_root=policy_root,
            overlays=overlays,
            jurisdictions=jurs
        )
        md = to_markdown(card)
        return HTMLResponse(content=md, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Safety card markdown generation failed: {str(e)}")

@app.get("/cockpit/safety_card.pdf")
def get_safety_card_pdf(
    policy_root: str = Query("qi/safety/policy_packs"),
    overlays: str | None = Query("qi/risk"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        # Mock PDF response - requires weasyprint
        raise HTTPException(status_code=404, detail="PDF generation requires weasyprint installation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/cockpit/calibration.svg", response_class=HTMLResponse)
def calibration_svg(
    task: str | None = Query(None),
    width: int = Query(640),
    height: int = Query(320),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    return HTMLResponse(reliability_svg(task=task, width=width, height=height), media_type="image/svg+xml")

@app.post("/cockpit/calibration/refit")
def calibration_refit(
    source: str = Query("eval"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        p = fit_and_save(source_preference=source)
        return JSONResponse({
            "ok": True,
            "source": p.source,
            "temperature": p.temperature,
            "ece": p.ece,
            "per_task_temperature": p.per_task_temperature or {},
            "per_task_ece": p.per_task_ece or {}
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calibration refit failed: {str(e)}")

@app.get("/cockpit/nightly-report")
def get_nightly_report(
    policy_root: str = Query("qi/safety/policy_packs"),
    overlays: str | None = Query("qi/risk"),
    window: int = Query(500),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        md = _mk_markdown(policy_root, overlays, window)
        return {
            "markdown": md,
            "window": window,
            "generated_at": time.time(),
            "latest_eval": _latest_eval(),
            "recent_receipts_count": len(_recent_receipts(window))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.post("/cockpit/generate-report")
def generate_full_report(
    policy_root: str = Query("qi/safety/policy_packs"),
    overlays: str | None = Query("qi/risk"),
    window: int = Query(500),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        path = generate_report(policy_root, overlays, window)
        return {"report_path": path, "generated_at": time.time()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full report generation failed: {str(e)}")

# ------------- Panel 2: Adaptive Learning Proposals -------------

@app.get("/cockpit/adaptive/analyze")
def analyze_adaptive_performance(
    window: int = Query(2000),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = AdaptiveLearningEngine()
        patterns = engine.analyze_performance_patterns(window=window)
        return {"analysis": patterns, "window": window}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adaptive analysis failed: {str(e)}")

@app.get("/cockpit/adaptive/candidates")
def get_adaptive_candidates(
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = AdaptiveLearningEngine()
        candidates = engine.batch_offline_eval(top_k=10)
        return {
            "items": [{"id": c.id, "patch": c.patch, "meta": c.meta, "score_offline": c.score_offline} for c in candidates],
            "count": len(candidates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Candidate retrieval failed: {str(e)}")

@app.post("/cockpit/adaptive/promote")
def promote_adaptive_candidates(
    targets: list[str] = Query(...),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = AdaptiveLearningEngine()
        proposal_ids = engine.propose_best(config_targets=targets)
        return {
            "queued_proposals": proposal_ids,
            "count": len(proposal_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adaptive promotion failed: {str(e)}")

@app.post("/cockpit/adaptive/evolve-params")
def evolve_adaptive_parameters(
    target_file: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
    tasks_focus: str | None = Query(None),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = AdaptiveLearningEngine()
        focus_list = [t.strip() for t in tasks_focus.split(",")] if tasks_focus else None
        candidates = engine.evolve_node_parameters(target_file=target_file, tasks_focus=focus_list)
        return {
            "candidates": [{"id": c.id, "patch": c.patch, "meta": c.meta} for c in candidates],
            "count": len(candidates),
            "target_file": target_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parameter evolution failed: {str(e)}")

@app.post("/cockpit/adaptive/discover-tools")
def discover_tool_combinations(
    target_file: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
    tasks_focus: str | None = Query(None),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = AdaptiveLearningEngine()
        focus_list = [t.strip() for t in tasks_focus.split(",")] if tasks_focus else None
        candidates = engine.discover_new_node_combinations(target_file=target_file, tasks_focus=focus_list)
        return {
            "candidates": [{"id": c.id, "patch": c.patch, "meta": c.meta} for c in candidates],
            "count": len(candidates),
            "target_file": target_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool discovery failed: {str(e)}")

@app.post("/cockpit/adaptive/propose-best")
def propose_best_adaptive(
    config_targets: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = AdaptiveLearningEngine()
        targets = [t.strip() for t in config_targets.split(",")]
        proposal_ids = engine.propose_best(config_targets=targets)
        return {
            "proposal_ids": proposal_ids,
            "count": len(proposal_ids),
            "config_targets": targets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adaptive proposal failed: {str(e)}")

# ------------- Panel 3: Human Adaptation Proposals -------------

@app.get("/cockpit/human-adapt/analyze")
def analyze_human_satisfaction(
    window: int = Query(1000),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = HumanAdaptEngine()
        patterns = engine.analyze_satisfaction_patterns(window=window)
        return {"analysis": patterns, "window": window}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Human satisfaction analysis failed: {str(e)}")

@app.get("/cockpit/human/proposals")
def get_human_proposals(
    user: str | None = Query(None),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = HumanAdaptEngine()
        proposals = engine.propose_tone_adaptations(
            target_file="qi/safety/policy_packs/global/mappings.yaml",
            user_focus=user
        )
        return {"proposals": proposals, "count": len(proposals), "user_focus": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Human proposal retrieval failed: {str(e)}")

@app.post("/cockpit/human/promote")
def promote_human_adaptations(
    user: str | None = Query(None),
    target_file: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
    ttl_sec: int = Query(3600),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = HumanAdaptEngine()
        submitted_ids = engine.submit_for_approval(config_targets=[target_file])
        return {
            "queued_proposal": submitted_ids[0] if submitted_ids else None,
            "count": len(submitted_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Human promotion failed: {str(e)}")

@app.post("/cockpit/human-adapt/propose-tone")
def propose_tone_adaptations(
    target_file: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
    user_focus: str | None = Query(None),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = HumanAdaptEngine()
        proposals = engine.propose_tone_adaptations(target_file=target_file, user_focus=user_focus)
        return {
            "proposals": proposals,
            "count": len(proposals),
            "target_file": target_file,
            "user_focus": user_focus
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tone adaptation proposal failed: {str(e)}")

@app.post("/cockpit/human-adapt/submit")
def submit_human_adaptations(
    config_targets: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = HumanAdaptEngine()
        targets = [t.strip() for t in config_targets.split(",")]
        submitted_ids = engine.submit_for_approval(config_targets=targets)
        return {
            "submitted_ids": submitted_ids,
            "count": len(submitted_ids),
            "config_targets": targets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Human adaptation submission failed: {str(e)}")

# ------------- Panel 4: Centralized Approvals -------------

@app.get("/cockpit/approvals/list")
def list_all_proposals(
    status_filter: str | None = Query(None),
    author_filter: str | None = Query(None),
    limit: int = Query(50),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        proposals = list_proposals()

        # Apply filters
        if status_filter:
            proposals = [p for p in proposals if p.get("status") == status_filter]
        if author_filter:
            proposals = [p for p in proposals if p.get("author", "").startswith(author_filter)]

        # Sort by timestamp (newest first) and limit
        proposals.sort(key=lambda x: x.get("ts", 0), reverse=True)
        proposals = proposals[:limit]

        # Add proposal source classification
        for p in proposals:
            author = p.get("author", "")
            if "adaptive" in author:
                p["source"] = "adaptive_learning"
            elif "human_adapt" in author:
                p["source"] = "human_adaptation"
            elif "self_heal" in author:
                p["source"] = "self_healing"
            else:
                p["source"] = "manual"

        return {
            "proposals": proposals,
            "count": len(proposals),
            "filters": {"status": status_filter, "author": author_filter},
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proposal listing failed: {str(e)}")

@app.get("/cockpit/proposals")
def get_proposals_simplified(
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        proposals = list_proposals()
        return {"items": proposals, "count": len(proposals)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proposal retrieval failed: {str(e)}")

@app.post("/cockpit/proposals/{proposal_id}/approve")
def approve_proposal_by_id(
    proposal_id: str,
    by: str = Query(...),
    reason: str = Query("Approved via cockpit UI"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        result = approve(proposal_id, by, reason)
        return {"proposal_id": proposal_id, "result": result, "by": by, "reason": reason}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

@app.post("/cockpit/proposals/{proposal_id}/reject")
def reject_proposal_by_id(
    proposal_id: str,
    by: str = Query(...),
    reason: str = Query("Rejected via cockpit UI"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        # Use approve with rejection reason for now
        result = approve(proposal_id, by, f"REJECTED: {reason}")
        return {"proposal_id": proposal_id, "result": result, "by": by, "reason": reason}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rejection failed: {str(e)}")

@app.post("/cockpit/proposals/{proposal_id}/apply")
def apply_proposal_by_id(
    proposal_id: str,
    as_user: str = Query("ops"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        result = apply(proposal_id, as_user)
        return {"proposal_id": proposal_id, "result": result, "as_user": as_user, "receipt_id": result.get("receipt_id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application failed: {str(e)}")

@app.post("/cockpit/approvals/{proposal_id}/approve")
def approve_proposal_unified(
    proposal_id: str,
    reviewer: str = Query(...),
    reason: str = Query("Approved via unified cockpit"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        result = approve(proposal_id, reviewer, reason)
        return {"proposal_id": proposal_id, "result": result, "reviewer": reviewer, "reason": reason}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

@app.post("/cockpit/approvals/{proposal_id}/apply")
def apply_proposal_unified(
    proposal_id: str,
    as_user: str = Query("ops"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        result = apply(proposal_id, as_user)
        return {"proposal_id": proposal_id, "result": result, "as_user": as_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application failed: {str(e)}")

@app.get("/cockpit/approvals/stats")
def get_approval_stats(
    days_back: int = Query(7),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        proposals = list_proposals()
        now = time.time()
        cutoff = now - (days_back * 24 * 3600)

        recent = [p for p in proposals if p.get("ts", 0) >= cutoff]

        stats = {
            "total_recent": len(recent),
            "by_status": {},
            "by_source": {},
            "by_risk": {},
            "avg_approval_time": None,
            "pending_count": 0
        }

        approval_times = []
        for p in recent:
            status = p.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            author = p.get("author", "")
            if "adaptive" in author:
                source = "adaptive"
            elif "human_adapt" in author:
                source = "human_adapt"
            elif "self_heal" in author:
                source = "self_heal"
            else:
                source = "manual"
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

            risk = p.get("risk", "unknown")
            stats["by_risk"][risk] = stats["by_risk"].get(risk, 0) + 1

            if status == "pending":
                stats["pending_count"] += 1
            elif status == "approved" and p.get("approved_ts") and p.get("ts"):
                approval_times.append(p["approved_ts"] - p["ts"])

        if approval_times:
            stats["avg_approval_time"] = sum(approval_times) / len(approval_times)

        return {"stats": stats, "days_back": days_back, "generated_at": time.time()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats generation failed: {str(e)}")

# ------------- Panel 5: Receipts & Provenance -------------

@app.get("/cockpit/receipts/recent")
def get_recent_receipts(
    limit: int = Query(100),
    task_filter: str | None = Query(None),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        receipts = _recent_receipts(limit * 2)  # Get more to allow filtering

        if task_filter:
            receipts = [r for r in receipts if
                       (r.get("activity") or {}).get("type", "").find(task_filter) >= 0]

        receipts = receipts[:limit]

        # Add summary stats
        task_counts = {}
        risk_counts = {}
        latencies = []

        for r in receipts:
            task = (r.get("activity") or {}).get("type") or "unknown"
            task_counts[task] = task_counts.get(task, 0) + 1

            for rf in r.get("risk_flags", []) or []:
                risk_counts[rf] = risk_counts.get(rf, 0) + 1

            if r.get("latency_ms") is not None:
                latencies.append(r["latency_ms"])

        summary = {
            "total": len(receipts),
            "task_distribution": task_counts,
            "risk_flags": risk_counts,
            "latency_p50": sorted(latencies)[len(latencies)//2] if latencies else None,
            "latency_p95": sorted(latencies)[int(0.95*len(latencies))-1] if latencies else None
        }

        return {
            "receipts": receipts,
            "summary": summary,
            "limit": limit,
            "task_filter": task_filter
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Receipt retrieval failed: {str(e)}")

@app.get("/cockpit/receipts")
def get_receipts_simplified(
    limit: int = Query(20),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        receipts = _recent_receipts(limit)

        # Transform to match UI expectations
        items = []
        for r in receipts:
            items.append({
                "id": r.get("id", "unknown"),
                "task": (r.get("activity") or {}).get("type") or "unknown",
                "latency_ms": r.get("latency_ms"),
                "risk_flags": r.get("risk_flags", [])
            })

        return {"items": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Receipt retrieval failed: {str(e)}")

@app.get("/cockpit/receipts/{receipt_id}/replay.json")
def replay_receipt_json(
    receipt_id: str,
    policy_root: str = Query("qi/safety/policy_packs"),
    overlays: str | None = Query("qi/risk"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        # Mock replay data for now
        return {
            "receipt_id": receipt_id,
            "replay": {
                "allowed": True,
                "policies_matched": ["default", "consent"],
                "risk_score": 0.2
            },
            "policy_root": policy_root,
            "overlays": overlays
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Receipt replay failed: {str(e)}")

@app.get("/cockpit/receipts/{receipt_id}/trace.svg")
def get_receipt_trace_svg(
    receipt_id: str,
    policy_root: str = Query("qi/safety/policy_packs"),
    overlays: str | None = Query("qi/risk"),
    link_base: str | None = Query(None),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        # Mock SVG trace for now
        svg = f"""<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
          <rect width="100%" height="100%" fill="#0f1115"/>
          <text x="200" y="50" text-anchor="middle" fill="#e7eaf0" font-family="monospace">Receipt: {receipt_id[:12]}...</text>
          <text x="200" y="80" text-anchor="middle" fill="#9aa5b1" font-family="monospace">Policy: {policy_root}</text>
          <text x="200" y="110" text-anchor="middle" fill="#3ddc97" font-family="monospace">✓ ALLOWED</text>
          <text x="200" y="140" text-anchor="middle" fill="#8ab4f8" font-family="monospace">Trace visualization requires receipts_api</text>
        </svg>"""

        return HTMLResponse(content=svg, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trace generation failed: {str(e)}")

@app.get("/cockpit/receipts/{receipt_id}/neighbors")
def get_receipt_neighbors_unified(
    receipt_id: str,
    task_filter: str | None = Query(None),
    limit: int = Query(10),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        neighbors = receipt_neighbors(receipt_id, task_filter, limit)
        return {"receipt_id": receipt_id, "neighbors": neighbors, "task_filter": task_filter, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neighbor retrieval failed: {str(e)}")

@app.get("/cockpit/receipts/sample")
def get_receipt_sample_unified(
    task_filter: str | None = Query(None),
    limit: int = Query(20),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        sample = receipt_sample(task_filter, limit)
        return {"sample": sample, "task_filter": task_filter, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample retrieval failed: {str(e)}")

# ------------- Panel 6: Feedback System -------------

@app.get("/cockpit/feedback")
def get_feedback_list(
    task: str | None = Query(None),
    jurisdiction: str | None = Query(None),
    limit: int = Query(100),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        from qi.feedback.store import get_store
        store = get_store()
        feedback = store.read_feedback(
            limit=limit,
            task_filter=task,
            jurisdiction_filter=jurisdiction
        )

        # Compute summary
        if feedback:
            satisfactions = [fc.get("feedback", {}).get("satisfaction", 0.5) for fc in feedback]
            avg_sat = sum(satisfactions) / len(satisfactions)

            issue_counts = {}
            for fc in feedback:
                for issue in fc.get("feedback", {}).get("issues", []):
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
        else:
            avg_sat = None
            issue_counts = {}

        return {
            "feedback": feedback,
            "count": len(feedback),
            "filters": {"task": task, "jurisdiction": jurisdiction},
            "summary": {
                "avg_satisfaction": avg_sat,
                "issue_distribution": issue_counts
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback retrieval failed: {str(e)}")

@app.get("/cockpit/feedback/clusters")
def get_feedback_clusters(
    task: str | None = Query(None),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        from qi.feedback.store import get_store
        store = get_store()
        clusters = store.read_clusters()

        if task:
            clusters = [c for c in clusters if c.get("task") == task]

        return {
            "clusters": clusters,
            "count": len(clusters),
            "filter": {"task": task}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cluster retrieval failed: {str(e)}")

@app.post("/cockpit/feedback/cluster")
def run_feedback_clustering(
    limit: int = Query(1000),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        from qi.feedback.triage import get_triage
        triage = get_triage()
        stats = triage.run_triage(limit=limit)

        return {
            "status": "completed",
            "stats": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")

@app.post("/cockpit/feedback/promote")
def promote_feedback_to_proposal(
    fc_id: str | None = Query(None),
    cluster_id: str | None = Query(None),
    target_file: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
    token: str | None = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        if not fc_id and not cluster_id:
            raise HTTPException(status_code=400, detail="Either fc_id or cluster_id required")

        from qi.feedback.proposals import ProposalMapper
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
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Promotion failed: {str(e)}")

# ------------- Dashboard & Health -------------

@app.get("/cockpit/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "components": {
            "safety_card": "available",
            "nightly_report": "available",
            "adaptive_learning": "available",
            "human_adaptation": "available",
            "approvals": "available",
            "receipts": "available",
            "feedback": "available"
        }
    }

@app.get("/cockpit/dashboard")
def get_dashboard_summary(
    token: str | None = Header(None, alias="X-Auth-Token")
):
    """Unified dashboard summary for ops overview."""
    _check_auth(token)
    try:
        # Latest eval
        latest_eval = _latest_eval()

        # Recent receipts summary
        recent_receipts = _recent_receipts(100)

        # Proposals summary
        proposals = list_proposals()
        pending_proposals = [p for p in proposals if p.get("status") == "pending"]

        # Adaptive learning summary
        try:
            adaptive_engine = AdaptiveLearningEngine()
            adaptive_patterns = adaptive_engine.analyze_performance_patterns(window=500)
        except:
            adaptive_patterns = None

        # Human adaptation summary
        try:
            human_engine = HumanAdaptEngine()
            human_patterns = human_engine.analyze_satisfaction_patterns(window=500)
        except:
            human_patterns = None

        dashboard = {
            "timestamp": time.time(),
            "evaluation": {
                "latest": latest_eval,
                "status": "pass" if latest_eval and latest_eval.get("summary", {}).get("num_failures", 1) == 0 else "fail"
            },
            "production": {
                "receipt_count": len(recent_receipts),
                "avg_latency": sum(r.get("latency_ms", 0) for r in recent_receipts) / max(len(recent_receipts), 1)
            },
            "governance": {
                "pending_proposals": len(pending_proposals),
                "proposal_sources": {}
            },
            "learning": {
                "adaptive_patterns": adaptive_patterns,
                "human_patterns": human_patterns
            }
        }

        # Proposal source breakdown
        for p in pending_proposals:
            author = p.get("author", "")
            if "adaptive" in author:
                source = "adaptive"
            elif "human_adapt" in author:
                source = "human_adapt"
            else:
                source = "other"
            dashboard["governance"]["proposal_sources"][source] = \
                dashboard["governance"]["proposal_sources"].get(source, 0) + 1

        return {"dashboard": dashboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

# ------------- Static Files (if needed) -------------

# Mount static files if web directory exists
if os.path.exists("web"):
    app.mount("/static", StaticFiles(directory="web"), name="static")

# ------------- UI Hub Routes -------------

@app.get("/ui", response_class=HTMLResponse)
def ui_index():
    return """
    <html><body style="font-family: ui-sans-serif; padding:20px; background:#0f1115; color:#e7eaf0">
      <h2>LUKHΛS • UI Hub</h2>
      <ul>
        <li><a href="/ui/cockpit" style="color:#8ab4f8">Ops Cockpit</a></li>
        <li><a href="/ui/trace" style="color:#8ab4f8">Trace Drill-down</a></li>
        <li><a href="/ui/approver" style="color:#8ab4f8">Approver UI</a></li>
      </ul>
      <p style="opacity:.7">Tip: set <code>COCKPIT_UI_PATH</code>, <code>RECEIPTS_UI_PATH</code>, <code>APPROVER_UI_PATH</code> to serve your local HTML files.</p>
    </body></html>
    """

@app.get("/ui/cockpit", response_class=HTMLResponse)
def ui_cockpit(
    # defaults for the page fields (can be overridden via query)
    api_base: str = Query(os.environ.get("COCKPIT_UI_API_BASE", "http://127.0.0.1:8098")),
    token: str | None = Query(os.environ.get("COCKPIT_UI_TOKEN", "")),
    policy_root: str = Query(os.environ.get("RECEIPTS_POLICY_ROOT", "qi/safety/policy_packs")),
    overlays: str = Query(os.environ.get("RECEIPTS_OVERLAYS", "qi/risk")),
):
    # Try to load the on-disk cockpit HTML; fall back to a tiny stub if not set
    if COCKPIT_UI_PATH and os.path.exists(COCKPIT_UI_PATH):
        html = _ORIG_OPEN(COCKPIT_UI_PATH, "r", encoding="utf-8").read()
    else:
        html = """<!doctype html><html><head><meta charset="utf-8">
<title>LUKHΛS • Ops Cockpit</title></head>
<body style="font-family: system-ui; background:#0f1115; color:#e7eaf0; padding:24px">
  <h2>Ops Cockpit</h2>
  <p>Static UI file not found. Put your <code>web/cockpit.html</code> on disk and set
     <code>COCKPIT_UI_PATH</code> to its absolute path, or open the file directly.</p>
  <p>Defaults passed to the page:</p>
  <pre id="defs"></pre>
  <script>
    document.getElementById('defs').textContent = JSON.stringify(window.LUKHAS_COCKPIT_DEFAULTS||{}, null, 2);
  </script>
</body></html>"""

    # Inject defaults so the page bootstraps without manual typing
    inject = f"""
<script>
  // Injected by /ui/cockpit
  window.LUKHAS_COCKPIT_DEFAULTS = {{
    apiBase: {json.dumps(api_base)},
    token: {json.dumps(token or "")},
    policyRoot: {json.dumps(policy_root)},
    overlays: {json.dumps(overlays)}
  }};
  // Auto-apply into the known input fields if they exist (works with the provided cockpit.html)
  (function applyDefaults() {{
    function setVal(id, v) {{
      try {{
        var el = document.getElementById(id);
        if (el && (el.value === "" || el.value === el.getAttribute("value"))) el.value = v || el.value;
      }} catch (e) {{}}
    }}
    setVal("api", window.LUKHAS_COCKPIT_DEFAULTS.apiBase);
    setVal("tok", window.LUKHAS_COCKPIT_DEFAULTS.token);
    setVal("policyRoot", window.LUKHAS_COCKPIT_DEFAULTS.policyRoot);
    setVal("overlays", window.LUKHAS_COCKPIT_DEFAULTS.overlays);
    // If the page exposes a global refresh button, click it to auto-load everything.
    var btn = document.getElementById("refreshAll");
    if (btn) setTimeout(function(){{ btn.click(); }}, 150);
  }})();
</script>
"""
    # Inject just before </body>; if not found, append
    if "</body>" in html:
        html = html.replace("</body>", inject + "</body>")
    else:
        html += inject
    return HTMLResponse(content=html)

@app.get("/ui/trace", response_class=HTMLResponse)
def ui_trace(
    rid: str | None = Query(None),
    api_base: str = Query(os.environ.get("RECEIPTS_API_BASE", "http://127.0.0.1:8095")),
    policy_root: str = Query(os.environ.get("RECEIPTS_POLICY_ROOT", "qi/safety/policy_packs")),
    overlays: str = Query(os.environ.get("RECEIPTS_OVERLAYS", "qi/risk")),
    public: bool = Query(False),
):
    # prefer on-disk static if provided
    if RECEIPTS_UI_PATH and os.path.exists(RECEIPTS_UI_PATH):
        html = _ORIG_OPEN(RECEIPTS_UI_PATH, "r", encoding="utf-8").read()
    else:
        html = "<html><body style='font-family:ui-sans-serif;padding:24px;color:#e7eaf0;background:#0f1115'>Missing trace_drilldown.html. Set RECEIPTS_UI_PATH.</body></html>"
    inject = f"""
<script>
  window.LUKHAS_TRACE_DEFAULTS = {{
    rid: {json.dumps(rid)},
    apiBase: {json.dumps(api_base)},
    policyRoot: {json.dumps(policy_root)},
    overlays: {json.dumps(overlays)},
    publicRedact: {str(public).lower()}
  }};
  // auto-apply & autoload
  (function(){{
    function set(id,v){{var e=document.getElementById(id); if(e && (e.value===''||e.value===e.getAttribute('value'))) e.value=v;}}
    set('apiBase', window.LUKHAS_TRACE_DEFAULTS.apiBase);
    set('policyRoot', window.LUKHAS_TRACE_DEFAULTS.policyRoot);
    set('overlays', window.LUKHAS_TRACE_DEFAULTS.overlays);
    var btn = document.getElementById('btnLoad')||document.getElementById('refreshAll');
    if(btn) setTimeout(function(){{btn.click();}},150);
  }})();
</script>
"""
    return HTMLResponse(content=html.replace("</body>", inject + "</body>") if "</body>" in html else html+inject)

@app.get("/ui/approver", response_class=HTMLResponse)
def ui_approver(
    api_base: str = Query(os.environ.get("APPROVER_API_BASE", "http://127.0.0.1:8097")),
    token: str | None = Query(os.environ.get("AUTONOMY_API_TOKEN", "")),
):
    if APPROVER_UI_PATH and os.path.exists(APPROVER_UI_PATH):
        html = _ORIG_OPEN(APPROVER_UI_PATH, "r", encoding="utf-8").read()
    else:
        html = "<html><body style='font-family:ui-sans-serif;padding:24px;color:#e7eaf0;background:#0f1115'>Missing approver_ui.html. Set APPROVER_UI_PATH.</body></html>"
    inject = f"""
<script>
  (function(){{
    var api={json.dumps(api_base)}, tok={json.dumps(token or "")};
    function set(id,v){{var e=document.getElementById(id); if(e && (e.value===''||e.value===e.getAttribute('value'))) e.value=v;}}
    set('api', api); set('tok', tok);
    var btn = document.getElementById('refresh');
    if(btn) setTimeout(function(){{btn.click();}},150);
  }})();
</script>
"""
    return HTMLResponse(content=html.replace("</body>", inject + "</body>") if "</body>" in html else html+inject)

# Root redirect
@app.get("/")
def root():
    return {"message": "LUKHAS Unified Ops Cockpit API", "version": "1.0.0", "docs": "/docs", "ui": "/ui"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("COCKPIT_PORT", "8098"))
    uvicorn.run(app, host="127.0.0.1", port=port)
