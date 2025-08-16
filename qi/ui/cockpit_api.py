# path: qi/ui/cockpit_api.py
from __future__ import annotations
import os, io, json, glob, hashlib, time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Component imports
from qi.docs.model_safety_card import generate_card, to_markdown
from qi.ops.auto_safety_report import generate_report, _mk_markdown, _recent_receipts, _latest_eval
from qi.learning.adaptive_engine import AdaptiveLearningEngine
from qi.learning.human_adapt_engine import HumanAdaptEngine
from qi.autonomy.self_healer import list_proposals, approve, apply
from qi.provenance.receipts_api import receipt_neighbors, receipt_sample

# Auth
def _check_auth(token: Optional[str] = Header(None, alias="X-Auth-Token")):
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
    overlays: Optional[str] = Query("qi/risk"),
    jurisdictions: str = Query("global,eu,us"),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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

@app.get("/cockpit/nightly-report")
def get_nightly_report(
    policy_root: str = Query("qi/safety/policy_packs"),
    overlays: Optional[str] = Query("qi/risk"),
    window: int = Query(500),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    overlays: Optional[str] = Query("qi/risk"),
    window: int = Query(500),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    token: Optional[str] = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = AdaptiveLearningEngine()
        patterns = engine.analyze_performance_patterns(window=window)
        return {"analysis": patterns, "window": window}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Adaptive analysis failed: {str(e)}")

@app.post("/cockpit/adaptive/evolve-params")
def evolve_adaptive_parameters(
    target_file: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
    tasks_focus: Optional[str] = Query(None),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    tasks_focus: Optional[str] = Query(None),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    token: Optional[str] = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        engine = HumanAdaptEngine()
        patterns = engine.analyze_satisfaction_patterns(window=window)
        return {"analysis": patterns, "window": window}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Human satisfaction analysis failed: {str(e)}")

@app.post("/cockpit/human-adapt/propose-tone")
def propose_tone_adaptations(
    target_file: str = Query("qi/safety/policy_packs/global/mappings.yaml"),
    user_focus: Optional[str] = Query(None),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    status_filter: Optional[str] = Query(None),
    author_filter: Optional[str] = Query(None),
    limit: int = Query(50),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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

@app.post("/cockpit/approvals/{proposal_id}/approve")
def approve_proposal_unified(
    proposal_id: str,
    reviewer: str = Query(...),
    reason: str = Query("Approved via unified cockpit"),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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
    task_filter: Optional[str] = Query(None),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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

@app.get("/cockpit/receipts/{receipt_id}/neighbors")
def get_receipt_neighbors_unified(
    receipt_id: str,
    task_filter: Optional[str] = Query(None),
    limit: int = Query(10),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        neighbors = receipt_neighbors(receipt_id, task_filter, limit)
        return {"receipt_id": receipt_id, "neighbors": neighbors, "task_filter": task_filter, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neighbor retrieval failed: {str(e)}")

@app.get("/cockpit/receipts/sample")
def get_receipt_sample_unified(
    task_filter: Optional[str] = Query(None),
    limit: int = Query(20),
    token: Optional[str] = Header(None, alias="X-Auth-Token")
):
    _check_auth(token)
    try:
        sample = receipt_sample(task_filter, limit)
        return {"sample": sample, "task_filter": task_filter, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample retrieval failed: {str(e)}")

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
            "receipts": "available"
        }
    }

@app.get("/cockpit/dashboard")
def get_dashboard_summary(
    token: Optional[str] = Header(None, alias="X-Auth-Token")
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

# Root redirect
@app.get("/")
def root():
    return {"message": "LUKHAS Unified Ops Cockpit API", "version": "1.0.0", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("COCKPIT_PORT", "8099"))
    uvicorn.run(app, host="127.0.0.1", port=port)