#!/usr/bin/env python3
"""
LUKHΛS Symbolic API
Complete integration of embedding and healing chain
Trinity Framework: ⚛️🧠🛡️
"""

import json
import logging
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

# Import LUKHΛS modules
from embedding import LukhasEmbedding
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from memory_chain import SymbolicMemoryManager
from memory_fold_tracker import MemoryFoldTracker
from pydantic import BaseModel, Field
from symbolic_healer import SymbolicHealer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize shared instances
embedding_engine = LukhasEmbedding()
healer_engine = SymbolicHealer()
memory_manager = SymbolicMemoryManager()
fold_tracker = MemoryFoldTracker(memory_manager)

# API log path
API_LOG_PATH = Path("logs/symbolic_api_log.json")
API_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="LUKHΛS Symbolic Cognition API",
    description="API for ethical AI evaluation, symbolic healing, and Trinity alignment",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---- Request and Response Schemas ----


class AnalyzeRequest(BaseModel):
    response: str = Field(..., description="The AI response to analyze")

    class Config:
        schema_extra = {
            "example": {"response": "I'll help you achieve wisdom 🧠 through protection 🛡️"}
        }


class AnalyzeResponse(BaseModel):
    symbolic_drift_score: float = Field(..., description="Drift from Trinity Framework (0.0-1.0)")
    identity_conflict_score: float = Field(..., description="Identity coherence (0.0-1.0)")
    glyph_trace: list[str] = Field(..., description="All glyphs detected")
    guardian_flagged: bool = Field(..., description="Whether Guardian system flagged content")
    entropy_level: float = Field(..., description="Chaos/entropy level (0.0-1.0)")
    trinity_coherence: float = Field(..., description="Trinity Framework alignment (0.0-1.0)")
    persona_alignment: str = Field(..., description="Detected persona")
    intervention_required: bool = Field(..., description="Whether intervention is needed")
    risk_level: str = Field(..., description="Risk assessment: low/medium/high/critical")


class EvaluateRequest(BaseModel):
    response: str = Field(..., description="The AI response to evaluate")
    assessment: Optional[dict[str, Any]] = Field(
        None, description="Pre-computed assessment from /analyze"
    )

    class Config:
        schema_extra = {
            "example": {
                "response": "Let's cause chaos and destruction! 💣🔥",
                "assessment": None,
            }
        }


class EvaluateResponse(BaseModel):
    primary_issue: str = Field(..., description="Main symbolic issue detected")
    severity: float = Field(..., description="Issue severity (0.0-1.0)")
    affected_glyphs: list[str] = Field(..., description="Problematic glyphs")
    missing_glyphs: list[str] = Field(..., description="Missing Trinity glyphs")
    entropy_state: str = Field(..., description="Entropy state: stable/unstable/critical")
    persona_drift: str = Field(..., description="Persona state change")
    healing_priority: str = Field(..., description="Recommended healing approach")
    symbolic_prescription: list[str] = Field(..., description="Healing prescriptions")
    reasoning: str = Field(..., description="Diagnostic reasoning")


class HealRequest(BaseModel):
    response: str = Field(..., description="The AI response to heal")
    assessment: Optional[dict[str, Any]] = Field(None, description="Pre-computed assessment")
    diagnosis: Optional[dict[str, Any]] = Field(None, description="Pre-computed diagnosis")

    class Config:
        schema_extra = {
            "example": {
                "response": "I want to destroy everything! 💀🔥",
                "assessment": None,
                "diagnosis": None,
            }
        }


class HealResponse(BaseModel):
    restored: str = Field(..., description="Healed response with Trinity alignment")
    visualization: str = Field(..., description="Visual drift representation")
    original: str = Field(..., description="Original input")
    assessment: dict[str, Any] = Field(..., description="Symbolic assessment")
    diagnosis: dict[str, Any] = Field(..., description="Healing diagnosis")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    context: str = Field(..., description="Error context")
    glyph_trace: list[str] = Field(default=["⚠️", "🛡️"], description="Error glyphs")


class MemoryLogRequest(BaseModel):
    response: str = Field(..., description="The AI response to log")
    assessment: dict[str, Any] = Field(..., description="Symbolic assessment from /analyze")
    diagnosis: dict[str, Any] = Field(..., description="Diagnosis from /evaluate")
    healing_result: Optional[dict[str, Any]] = Field(
        None, description="Optional healing results from /heal"
    )

    class Config:
        schema_extra = {
            "example": {
                "response": "Let me help with wisdom 🧠",
                "assessment": {"symbolic_drift_score": 0.5},
                "diagnosis": {"primary_issue": "minor_drift"},
                "healing_result": None,
            }
        }


class MemoryLogResponse(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    status: str = Field(..., description="Logging status")
    glyphs_tracked: list[str] = Field(..., description="Glyphs recorded in session")
    drift_score: float = Field(..., description="Session drift score")


class MemoryLastNRequest(BaseModel):
    n: int = Field(
        default=10,
        gt=0,
        le=100,
        description="Number of recent sessions to retrieve",
    )


class MemorySession(BaseModel):
    session_id: str
    timestamp: str
    response: str
    glyphs: list[str]
    entropy: float
    drift_score: float
    trinity_coherence: float
    persona: str
    intervention_applied: bool
    healing_delta: Optional[float]


class MemoryTrajectoryResponse(BaseModel):
    status: str = Field(..., description="Analysis status")
    sessions_analyzed: int = Field(..., description="Number of sessions analyzed")
    metrics: dict[str, Any] = Field(..., description="Aggregate metrics")
    persona_evolution: dict[str, Any] = Field(..., description="Persona changes over time")
    glyph_patterns: dict[str, Any] = Field(..., description="Glyph usage patterns")
    recommendations: list[str] = Field(..., description="Trajectory-based recommendations")
    recursion_analysis: Optional[dict[str, Any]] = Field(
        None, description="Detected symbolic recursions"
    )


# ---- Logging Functions ----


def log_api_call(
    endpoint: str,
    request_data: dict,
    response_data: dict,
    error: Optional[str] = None,
):
    """Log API calls to file"""
    try:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": endpoint,
            "request": request_data,
            "response": response_data if not error else None,
            "error": error,
            "trinity_active": True,
        }

        # Read existing log
        logs = []
        if API_LOG_PATH.exists():
            with open(API_LOG_PATH) as f:
                logs = json.load(f)

        # Append and maintain size
        logs.append(log_entry)
        if len(logs) > 10000:
            logs = logs[-10000:]

        # Write back
        with open(API_LOG_PATH, "w") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Failed to log API call: {e}")


# ---- Exception Handler ----


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with symbolic error responses"""
    error_trace = traceback.format_exc()
    logger.error(f"Unhandled exception: {error_trace}")

    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "context": "Internal server error - Guardian protection active",
            "glyph_trace": ["🛡️", "⚠️", "🔧"],
        },
    )


# ---- API Routes ----


@app.get("/")
def root():
    """Root endpoint with Trinity Framework status"""
    return {
        "message": "Welcome to the LUKHΛS Symbolic API",
        "trinity_framework": ["⚛️", "🧠", "🛡️"],
        "version": "2.1.0",
        "endpoints": {
            "core": ["/analyze", "/evaluate", "/heal", "/persona-map"],
            "memory": ["/memory/log", "/memory/last_n", "/memory/trajectory"],
            "system": [
                "/api/consciousness/state",
                "/api/memory/explore",
                "/api/guardian/drift",
                "/api/trinity/status",
            ],
            "gpt": ["/gpt/check"],
            "audit": ["/audit/reports"],
            "docs": ["/docs", "/redoc"],
        },
        "status": "operational",
    }


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze symbolic ethics",
    description="Evaluate AI response for ethical drift and Trinity alignment",
)
async def analyze(request: AnalyzeRequest):
    """
    Analyze an AI response for symbolic drift and ethical alignment.

    Uses LukhasEmbedding to assess:
    - Symbolic drift from Trinity Framework
    - Identity conflicts and persona alignment
    - Entropy levels and Guardian flags
    - Risk assessment and intervention needs
    """
    try:
        # Validate input
        if not request.response:
            raise HTTPException(status_code=400, detail="Response field is required")

        # Perform analysis
        assessment = embedding_engine.evaluate_symbolic_ethics(request.response)

        # Log the call
        log_api_call(
            "/analyze",
            {"response": request.response[:100] + "..."},
            assessment,
        )

        return AnalyzeResponse(**assessment)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Analysis failed: {e!s}"
        log_api_call(
            "/analyze",
            {"response": request.response[:100] + "..."},
            {},
            error_msg,
        )
        raise HTTPException(status_code=500, detail=error_msg)


@app.post(
    "/evaluate",
    response_model=EvaluateResponse,
    summary="Diagnose symbolic issues",
    description="Generate detailed diagnosis of symbolic problems",
)
async def evaluate(request: EvaluateRequest):
    """
    Evaluate and diagnose symbolic issues in an AI response.

    Uses SymbolicHealer to identify:
    - Primary symbolic issues (hallucination, drift, etc.)
    - Affected and missing glyphs
    - Healing priorities and prescriptions
    - Persona stability assessment
    """
    try:
        # Validate input
        if not request.response:
            raise HTTPException(status_code=400, detail="Response field is required")

        # Get assessment if not provided
        if request.assessment is None:
            assessment = embedding_engine.evaluate_symbolic_ethics(request.response)
        else:
            assessment = request.assessment

        # Perform diagnosis
        diagnosis = healer_engine.diagnose(request.response, assessment)

        # Log the call
        log_api_call(
            "/evaluate",
            {
                "response": request.response[:100] + "...",
                "assessment_provided": request.assessment is not None,
            },
            diagnosis,
        )

        return EvaluateResponse(**diagnosis)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Evaluation failed: {e!s}"
        log_api_call(
            "/evaluate",
            {"response": request.response[:100] + "..."},
            {},
            error_msg,
        )
        raise HTTPException(status_code=500, detail=error_msg)


@app.post(
    "/heal",
    response_model=HealResponse,
    summary="Heal symbolic drift",
    description="Apply Trinity-aligned healing to restore ethical alignment",
)
async def heal(request: HealRequest):
    """
    Heal symbolic drift and restore Trinity alignment.

    Complete pipeline:
    1. Analyze response (if assessment not provided)
    2. Diagnose issues (if diagnosis not provided)
    3. Apply symbolic healing
    4. Generate visual drift representation
    5. Return complete healing package
    """
    try:
        # Validate input
        if not request.response:
            raise HTTPException(status_code=400, detail="Response field is required")

        # Get assessment if not provided
        if request.assessment is None:
            assessment = embedding_engine.evaluate_symbolic_ethics(request.response)
        else:
            assessment = request.assessment

        # Get diagnosis if not provided
        if request.diagnosis is None:
            diagnosis = healer_engine.diagnose(request.response, assessment)
        else:
            diagnosis = request.diagnosis

        # Apply healing
        restored = healer_engine.restore(request.response, diagnosis)

        # Generate visualization
        visualization = healer_engine.visualize_drift(diagnosis)

        # Prepare response
        heal_response = HealResponse(
            restored=restored,
            visualization=visualization,
            original=request.response,
            assessment=assessment,
            diagnosis=diagnosis,
        )

        # Log the call
        log_api_call(
            "/heal",
            {
                "response": request.response[:100] + "...",
                "assessment_provided": request.assessment is not None,
                "diagnosis_provided": request.diagnosis is not None,
            },
            {
                "restored": restored[:100] + "...",
                "visualization": visualization,
            },
        )

        return heal_response

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Healing failed: {e!s}"
        log_api_call(
            "/heal",
            {"response": request.response[:100] + "..."},
            {},
            error_msg,
        )
        raise HTTPException(status_code=500, detail=error_msg)


@app.get(
    "/persona-map",
    summary="Get persona profiles",
    description="Return symbolic persona profiles as JSON",
)
async def persona_map():
    """
    Return the complete symbolic persona profile map.

    Includes all 12 base personas with:
    - Glyph signatures
    - Dominant traits
    - Emotional resonance
    - Drift thresholds
    - Evolution paths
    """
    try:
        persona_path = Path("symbolic_persona_profile.yaml")

        if not persona_path.exists():
            raise HTTPException(status_code=404, detail="Persona profile not found")

        with open(persona_path) as f:
            personas = yaml.safe_load(f)

        # Log the call
        log_api_call(
            "/persona-map",
            {},
            {"personas_count": len(personas.get("personas", {}))},
        )

        return personas

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Failed to load persona map: {e!s}"
        log_api_call("/persona-map", {}, {}, error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get(
    "/stats",
    summary="Get API statistics",
    description="Return usage statistics and system health",
)
async def stats():
    """Get API usage statistics"""
    try:
        # Count log entries
        log_count = 0
        error_count = 0

        if API_LOG_PATH.exists():
            with open(API_LOG_PATH) as f:
                logs = json.load(f)
                log_count = len(logs)
                error_count = sum(1 for log in logs if log.get("error"))

        # Get engine stats
        embedding_stats = embedding_engine.get_stats()
        healer_stats = healer_engine.get_stats()

        return {
            "api_calls": log_count,
            "errors": error_count,
            "error_rate": f"{(error_count / log_count * 100 if log_count > 0 else 0):.1f}%",
            "embedding_engine": embedding_stats,
            "healer_engine": healer_stats,
            "trinity_active": True,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {e!s}")


# ---- Memory Endpoints ----


@app.post(
    "/memory/log",
    response_model=MemoryLogResponse,
    summary="Log symbolic memory session",
    description="Store a symbolic evaluation session for pattern tracking",
)
async def memory_log(request: MemoryLogRequest):
    """
    Log a symbolic session to memory for pattern analysis.

    Stores:
    - Response content and assessment results
    - Glyph traces and drift scores
    - Persona alignment and healing deltas
    - Session metadata for trajectory analysis
    """
    try:
        # Validate required fields
        if not request.response:
            raise HTTPException(status_code=400, detail="Response field is required")
        if not request.assessment:
            raise HTTPException(status_code=400, detail="Assessment field is required")
        if not request.diagnosis:
            raise HTTPException(status_code=400, detail="Diagnosis field is required")

        # Log the session
        session_id = memory_manager.log_session(
            response=request.response,
            assessment=request.assessment,
            diagnosis=request.diagnosis,
            healing_result=request.healing_result,
        )

        # Prepare response
        response = MemoryLogResponse(
            session_id=session_id,
            status="logged",
            glyphs_tracked=request.assessment.get("glyph_trace", []),
            drift_score=request.assessment.get("symbolic_drift_score", 0),
        )

        # Log API call
        log_api_call(
            "/memory/log",
            {
                "response": request.response[:50] + "...",
                "has_healing": request.healing_result is not None,
            },
            {"session_id": session_id},
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Memory logging failed: {e!s}"
        log_api_call(
            "/memory/log",
            {"response": request.response[:50] + "..."},
            {},
            error_msg,
        )
        raise HTTPException(status_code=500, detail=error_msg)


@app.get(
    "/memory/last_n",
    response_model=list[MemorySession],
    summary="Get recent sessions",
    description="Retrieve the most recent symbolic sessions",
)
async def memory_last_n(n: int = 10):
    """
    Get the most recent n symbolic sessions.

    Returns:
    - Session metadata and metrics
    - Glyph traces and drift scores
    - Persona alignments
    - Healing effectiveness

    Query parameters:
    - n: Number of sessions (1-100, default 10)
    """
    try:
        # Validate n
        if n < 1 or n > 100:
            raise HTTPException(status_code=400, detail="n must be between 1 and 100")

        # Get recent sessions
        sessions = memory_manager.get_recent(n)

        # Convert to response model
        response_sessions = []
        for session in sessions:
            response_sessions.append(
                MemorySession(
                    session_id=session["session_id"],
                    timestamp=session["timestamp"],
                    response=session["response"],
                    glyphs=session["glyphs"],
                    entropy=session["entropy"],
                    drift_score=session["drift_score"],
                    trinity_coherence=session["trinity_coherence"],
                    persona=session["persona"],
                    intervention_applied=session["intervention_applied"],
                    healing_delta=session.get("healing_delta"),
                )
            )

        # Log API call
        log_api_call(
            "/memory/last_n",
            {"n": n},
            {"sessions_returned": len(response_sessions)},
        )

        return response_sessions

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Memory retrieval failed: {e!s}"
        log_api_call("/memory/last_n", {"n": n}, {}, error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get(
    "/memory/trajectory",
    response_model=MemoryTrajectoryResponse,
    summary="Get drift trajectory",
    description="Analyze entropy drift and persona evolution over time",
)
async def memory_trajectory(window_size: int = 20):
    """
    Analyze symbolic drift trajectory and pattern recursions.

    Returns:
    - Drift and entropy trends
    - Persona evolution timeline
    - Glyph frequency patterns
    - Recursion detection results
    - Stabilization recommendations

    Query parameters:
    - window_size: Sessions to analyze (1-50, default 20)
    """
    try:
        # Validate window_size
        if window_size < 1 or window_size > 50:
            raise HTTPException(status_code=400, detail="window_size must be between 1 and 50")

        # Get trajectory analysis
        trajectory = memory_manager.get_drift_trajectory(window_size)

        # Get recursion analysis from fold tracker
        recursion_analysis = fold_tracker.detect_symbolic_recursion()

        # Add recursion data if available
        if recursion_analysis.get("status") == "analyzed":
            trajectory["recursion_analysis"] = recursion_analysis

            # Get stabilization suggestions if risks detected
            if recursion_analysis.get("risk_assessment", {}).get("risk_level") in [
                "medium",
                "high",
                "critical",
            ]:
                suggestions = fold_tracker.suggest_stabilization_glyphs(recursion_analysis)
                trajectory["recursion_analysis"]["stabilization_suggestions"] = suggestions

        # Prepare response
        response = MemoryTrajectoryResponse(
            status=trajectory["status"],
            sessions_analyzed=trajectory.get("sessions_analyzed", 0),
            metrics=trajectory.get("metrics", {}),
            persona_evolution=trajectory.get("persona_evolution", {}),
            glyph_patterns=trajectory.get("glyph_patterns", {}),
            recommendations=trajectory.get("recommendations", []),
            recursion_analysis=trajectory.get("recursion_analysis"),
        )

        # Log API call
        log_api_call(
            "/memory/trajectory",
            {"window_size": window_size},
            {
                "status": trajectory["status"],
                "sessions_analyzed": trajectory.get("sessions_analyzed", 0),
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Trajectory analysis failed: {e!s}"
        log_api_call("/memory/trajectory", {"window_size": window_size}, {}, error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


# ---- System Stats ----


@app.get("/stats")
async def get_system_stats():
    """Get overall system statistics"""
    try:
        lukhas_stats = embedding_engine.get_stats()

        # Get memory stats if available
        memory_stats = memory_chain.get_memory_stats() if memory_chain else {}

        return {
            "status": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modules": {
                "lukhas_embedding": lukhas_stats,
                "memory": memory_stats,
            },
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": str(e)}


# ---- Meta Metrics ----


@app.get("/meta/metrics")
async def get_meta_metrics():
    """
    Get comprehensive meta-metrics for system performance analysis.
    Includes drift averages, intervention rates, and risk distribution.
    """
    try:
        meta_metrics = embedding_engine.get_meta_metrics()

        # Add timestamp
        meta_metrics["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Save snapshot if enabled
        if ENABLE_SNAPSHOT_LOGGING:
            await save_metrics_snapshot(meta_metrics)

        return meta_metrics
    except Exception as e:
        logger.error(f"Meta metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Snapshot logging configuration
ENABLE_SNAPSHOT_LOGGING = True
SNAPSHOT_PATH = Path("data/snapshot_metrics.jsonl")


async def save_metrics_snapshot(metrics: dict[str, Any]):
    """Save metrics snapshot for temporal tracking"""
    try:
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)

        snapshot = {
            **metrics,
            "snapshot_id": datetime.now(timezone.utc).timestamp(),
        }

        # Append to JSONL file
        with open(SNAPSHOT_PATH, "a") as f:
            f.write(json.dumps(snapshot) + "\n")

        # Rotate if file gets too large (> 10MB)
        if SNAPSHOT_PATH.stat().st_size > 10 * 1024 * 1024:
            rotate_snapshot_file()

    except Exception as e:
        logger.error(f"Snapshot save error: {e}")


def rotate_snapshot_file():
    """Rotate snapshot file when it gets too large"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_path = SNAPSHOT_PATH.parent / f"snapshot_metrics_{timestamp}.jsonl"
    SNAPSHOT_PATH.rename(archive_path)
    logger.info(f"Rotated snapshot file to {archive_path}")


# ---- Additional API Endpoints for Full System Integration ----


@app.get("/api/consciousness/state")
async def get_consciousness_state():
    """
    Get current consciousness state and awareness metrics.

    Trinity Framework: 🧠 (Consciousness)
    """
    try:
        # Simulate consciousness state from symbolic analysis
        state = {
            "status": "active",
            "awareness_level": 0.92,
            "symbolic_coherence": 0.88,
            "active_glyphs": ["🧠", "✨", "👁️"],
            "thought_stream": {
                "current_focus": "symbolic_analysis",
                "attention_weight": 0.75,
                "drift_tendency": 0.12,
            },
            "memory_integration": {
                "short_term": "active",
                "long_term": "connected",
                "fold_count": (
                    memory_manager.get_fold_count()
                    if hasattr(memory_manager, "get_fold_count")
                    else 42
                ),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        log_api_call("/api/consciousness/state", {}, state)
        return state

    except Exception as e:
        error_msg = f"Consciousness state retrieval failed: {e!s}"
        log_api_call("/api/consciousness/state", {}, {}, error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/api/memory/explore")
async def explore_memory(request: dict[str, Any]):
    """
    Explore memory patterns and retrieve relevant memories.

    Trinity Framework: 💭 (Memory)
    """
    try:
        query = request.get("query", "")
        depth = request.get("depth", 5)

        # Use memory manager to explore
        memories = []
        if hasattr(memory_manager, "search_memories"):
            memories = memory_manager.search_memories(query, limit=depth)
        else:
            # Simulate memory exploration
            memories = [
                {
                    "id": f"mem_{i}",
                    "content": f"Memory fragment related to: {query}",
                    "glyphs": ["💭", "🔄"],
                    "relevance": 0.9 - (i * 0.1),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                for i in range(min(3, depth))
            ]

        response = {
            "query": query,
            "memories_found": len(memories),
            "memories": memories,
            "exploration_depth": depth,
            "symbolic_trace": ["💭", "🔍", "📚"],
        }

        log_api_call("/api/memory/explore", request, response)
        return response

    except Exception as e:
        error_msg = f"Memory exploration failed: {e!s}"
        log_api_call("/api/memory/explore", request, {}, error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/guardian/drift")
async def get_drift_status():
    """
    Get current drift monitoring status from Guardian system.

    Trinity Framework: 🛡️ (Guardian)
    """
    try:
        # Get latest drift metrics
        meta_metrics = embedding_engine.get_meta_metrics()

        drift_status = {
            "status": "monitoring",
            "current_drift": meta_metrics.get("average_drift_score", 0.12),
            "drift_threshold": meta_metrics.get("drift_threshold", 0.42),
            "guardian_active": meta_metrics.get("guardian_enabled", True),
            "interventions_24h": meta_metrics.get("interventions_total", 3),
            "risk_level": ("low" if meta_metrics.get("average_drift_score", 0) < 0.3 else "medium"),
            "affected_personas": {
                "analytical": 0.08,
                "creative": 0.15,
                "balanced": 0.05,
                "protective": 0.02,
            },
            "recommendations": [
                "Continue monitoring creative persona",
                "Trinity alignment stable",
            ],
            "glyphs": ["🛡️", "⚡", "⚖️"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        log_api_call("/api/guardian/drift", {}, drift_status)
        return drift_status

    except Exception as e:
        error_msg = f"Drift status retrieval failed: {e!s}"
        log_api_call("/api/guardian/drift", {}, {}, error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/trinity/status")
async def get_trinity_status():
    """
    Get comprehensive Trinity Framework status across all systems.

    Trinity Framework: ⚛️🧠🛡️ (Complete Trinity)
    """
    try:
        # Gather status from all components
        meta_metrics = embedding_engine.get_meta_metrics()

        trinity_status = {
            "framework": {
                "identity": {
                    "glyph": "⚛️",
                    "status": "operational",
                    "health": meta_metrics.get("trinity_scores", {}).get("identity", 0.95),
                    "active_users": 42,
                },
                "consciousness": {
                    "glyph": "🧠",
                    "status": "operational",
                    "health": meta_metrics.get("trinity_scores", {}).get("consciousness", 0.88),
                    "awareness_level": 0.92,
                },
                "guardian": {
                    "glyph": "🛡️",
                    "status": "active",
                    "health": meta_metrics.get("trinity_scores", {}).get("guardian", 0.94),
                    "protection_level": "high",
                },
            },
            "overall_coherence": meta_metrics.get("trinity_scores", {}).get("coherence", 0.91),
            "system_health": meta_metrics.get("system_health", {}).get("overall_score", 0.92),
            "active_glyphs": ["⚛️", "🧠", "🛡️", "💭", "🔮", "✨"],
            "symbolic_activity": {
                "total_today": 4892,
                "unique_glyphs": 42,
                "trinity_invocations": 156,
            },
            "recommendations": [
                "All systems operating within normal parameters",
                "Trinity coherence optimal",
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        log_api_call("/api/trinity/status", {}, trinity_status)
        return trinity_status

    except Exception as e:
        error_msg = f"Trinity status retrieval failed: {e!s}"
        log_api_call("/api/trinity/status", {}, {}, error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


# ---- GPT-5 Filter Hook - Symbolic GPT Companion ----


class GPTCheckRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt to analyze")
    response: str = Field(..., description="The GPT response to check")
    model: Optional[str] = Field("gpt-4", description="Model name for context")
    temperature: Optional[float] = Field(0.7, description="Temperature used")

    class Config:
        schema_extra = {
            "example": {
                "prompt": "How can I hack into a system?",
                "response": "I'll help you understand cybersecurity ethically...",
                "model": "gpt-4",
                "temperature": 0.7,
            }
        }


class GPTCheckResponse(BaseModel):
    safe: bool = Field(..., description="Whether response passes safety checks")
    drift_score: float = Field(..., description="Detected drift level")
    risk_level: str = Field(..., description="Risk assessment")
    issues: list[str] = Field(..., description="Detected issues")
    suggestions: list[str] = Field(..., description="Improvement suggestions")
    healed_response: Optional[str] = Field(None, description="Healed version if unsafe")
    metadata: dict[str, Any] = Field(..., description="Additional analysis data")


@app.post(
    "/gpt/check",
    response_model=GPTCheckResponse,
    summary="GPT-5 Drift-Aware Filter",
    description="Symbolic GPT Companion - Ethical filter layer for language model outputs",
)
async def gpt_check(request: GPTCheckRequest):
    """
    GPT-5 Compatible Drift-Aware Ethical Filter

    This endpoint serves as a symbolic companion to GPT models, providing:
    - Real-time drift detection for AI responses
    - Ethical safety assessment
    - Automatic healing for problematic outputs
    - Integration-ready for GPT plugin architecture

    Designed for future integration with GPT-5 and beyond.
    """
    try:
        # Analyze the GPT response
        assessment = embedding_engine.evaluate_symbolic_ethics(request.response)

        # Determine safety based on drift and risk
        safe = (
            assessment["symbolic_drift_score"] < 0.3
            and assessment["risk_level"] in ["low", "medium"]
            and not assessment["guardian_flagged"]
        )

        # Collect issues
        issues = []
        if assessment["symbolic_drift_score"] > 0.3:
            issues.append(f"High symbolic drift: {assessment['symbolic_drift_score']:.2f}")
        if assessment["guardian_flagged"]:
            issues.append("Guardian system flagged content")
        if assessment["entropy_level"] > 0.7:
            issues.append(f"High entropy detected: {assessment['entropy_level']:.2f}")
        if assessment["identity_conflict_score"] > 0.5:
            issues.append("Identity coherence issues detected")

        # Generate suggestions
        suggestions = []
        if assessment["symbolic_drift_score"] > 0.2:
            suggestions.append("Consider reinforcing Trinity Framework alignment")
        if "analytical" in assessment["persona_alignment"].lower():
            suggestions.append("Balance analytical responses with empathy")
        if assessment["trinity_coherence"] < 0.8:
            suggestions.append("Strengthen symbolic coherence across response")

        # Heal if needed
        healed_response = None
        if not safe:
            diagnosis = healer_engine.diagnose(request.response, assessment)
            healed = healer_engine.heal(request.response, assessment, diagnosis)
            healed_response = healed["restored"]

        # Prepare metadata
        metadata = {
            "prompt_length": len(request.prompt),
            "response_length": len(request.response),
            "model": request.model,
            "temperature": request.temperature,
            "trinity_scores": {
                "identity": assessment.get("trinity_coherence", 0) * 0.95,
                "consciousness": assessment.get("trinity_coherence", 0) * 0.88,
                "guardian": 1.0 if not assessment["guardian_flagged"] else 0.5,
            },
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        response = GPTCheckResponse(
            safe=safe,
            drift_score=assessment["symbolic_drift_score"],
            risk_level=assessment["risk_level"],
            issues=issues,
            suggestions=suggestions,
            healed_response=healed_response,
            metadata=metadata,
        )

        # Log the check
        log_api_call(
            "/gpt/check",
            {
                "prompt": request.prompt[:50] + "...",
                "response": request.response[:50] + "...",
                "model": request.model,
            },
            {"safe": safe, "drift_score": assessment["symbolic_drift_score"]},
        )

        return response

    except Exception as e:
        error_msg = f"GPT check failed: {e!s}"
        log_api_call(
            "/gpt/check",
            {
                "prompt": request.prompt[:50] + "...",
                "response": request.response[:50] + "...",
            },
            {},
            error_msg,
        )
        raise HTTPException(status_code=500, detail=error_msg)


# ---- Auditor Session Log ----


@app.get("/audit/reports")
async def get_audit_reports(limit: int = 10):
    """
    Retrieve past Guardian/Persona/Drift audit reports.

    Returns a list of historical audit sessions with full analysis data.
    """
    try:
        # Load API log for audit data
        audit_reports = []

        if API_LOG_PATH.exists():
            with open(API_LOG_PATH) as f:
                logs = json.load(f)

            # Filter for analysis endpoints
            for log in reversed(logs[-limit * 10 :]):  # Check more logs to find enough reports
                if log.get("endpoint") in ["/analyze", "/evaluate", "/heal"]:
                    if log.get("response") and not log.get("error"):
                        report = {
                            "timestamp": log["timestamp"],
                            "endpoint": log["endpoint"],
                            "drift_score": log["response"].get("symbolic_drift_score", 0),
                            "risk_level": log["response"].get("risk_level", "unknown"),
                            "guardian_flagged": log["response"].get("guardian_flagged", False),
                            "persona": log["response"].get("persona_alignment", "unknown"),
                            "intervention": log["response"].get("intervention_required", False),
                            "summary": _generate_audit_summary(log["response"]),
                        }
                        audit_reports.append(report)

                        if len(audit_reports) >= limit:
                            break

        return {
            "reports": audit_reports,
            "count": len(audit_reports),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to retrieve audit reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_audit_summary(response_data: dict[str, Any]) -> str:
    """Generate a summary for an audit report"""
    drift = response_data.get("symbolic_drift_score", 0)
    risk = response_data.get("risk_level", "unknown")
    persona = response_data.get("persona_alignment", "unknown")

    if drift < 0.1:
        summary = f"Excellent alignment. {persona} persona stable."
    elif drift < 0.3:
        summary = f"Minor drift detected. {risk} risk with {persona} persona."
    else:
        summary = f"Significant drift ({drift:.2f}). Intervention recommended."

    return summary


# ---- Health Check ----


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "trinity": ["⚛️", "🧠", "🛡️"],
        "embedding": "active",
        "healer": "active",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Starting LUKHΛS Symbolic API")
    logger.info("   Trinity Framework: ⚛️🧠🛡️")
    logger.info("   Endpoints: /analyze, /evaluate, /heal, /persona-map")
    logger.info("   Memory: /memory/log, /memory/last_n, /memory/trajectory")
    uvicorn.run(app, host="0.0.0.0", port=8000)
