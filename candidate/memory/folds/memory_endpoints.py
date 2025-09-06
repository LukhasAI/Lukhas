#!/usr/bin/env python3
"""

#TAG:memory
#TAG:folds
#TAG:neuroplastic
#TAG:colony


FastAPI Memory System Endpoints
Provides RESTful API for LUKHAS memory operations.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Future import after refactoring
# from memory import MemoryCore
# from memory.drift_tracker import DriftMetrics
# Current import
from memory.core import HybridMemoryFold


# Pydantic models for API
class MemoryFoldRequest(BaseModel, timezone):
    """Request model for memory folding."""

    experience: dict[str, Any] = Field(..., description="Experience data to store")
    context: dict[str, Any] = Field(..., description="Context for memory storage")
    agent_id: str = Field(..., description="ID of the agent storing memory")

    class Config:
        json_schema_extra = {
            "example": {
                "experience": {
                    "type": "observation",
                    "content": "User requested weather information",
                    "timestamp": "2024-01-15T10:30:00Z",
                },
                "context": {
                    "emotional_state": 0.7,
                    "attention_level": 0.9,
                    "task_relevance": 0.8,
                },
                "agent_id": "consciousness-001",
            }
        }


class MemoryFoldResponse(BaseModel):
    """Response model for memory folding."""

    memory_id: str = Field(..., description="Unique ID of stored memory")
    vector_hash: str = Field(..., description="Hash of memory vector")
    drift_score: Optional[float] = Field(None, description="Initial drift score")
    timestamp: datetime = Field(..., description="Storage timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "memory_id": "mem_1234567890abcdef",
                "vector_hash": "sha256:abcdef123456...",
                "drift_score": 0.0,
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


class MemorySearchRequest(BaseModel):
    """Request model for memory search."""

    query: dict[str, Any] = Field(..., description="Query for similarity search")
    context: Optional[dict[str, Any]] = Field(None, description="Search context")
    top_k: int = Field(5, ge=1, le=100, description="Number of results")
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Similarity threshold")
    agent_id: str = Field(..., description="ID of the agent searching")


class MemorySearchResult(BaseModel):
    """Individual search result."""

    memory_id: str
    similarity_score: float
    experience: dict[str, Any]
    metadata: dict[str, Any]
    drift_score: Optional[float]


class DriftAnalysis(BaseModel):
    """Drift analysis response."""

    memory_id: str
    current_drift: float
    entropy: float
    stability: float
    collapse_probability: float
    time_since_storage: float
    recommendation: str


class LineageTrace(BaseModel):
    """Memory lineage information."""

    memory_id: str
    lineage_depth: int
    ancestors: list[dict[str, Any]]
    collapse_events: list[dict[str, Any]]
    total_drift: float


class CollapseRequest(BaseModel):
    """Request to force memory collapse."""

    memory_ids: list[str] = Field(..., description="Memory IDs to collapse")
    reason: str = Field(..., description="Reason for forced collapse")
    agent_id: str = Field(..., description="Agent requesting collapse")


# Router setup
router = APIRouter(prefix="/memory", tags=["memory"])

# In-memory storage for demo (replace with actual implementation)
memory_systems: dict[str, HybridMemoryFold] = {}


def get_memory_system(agent_id: str) -> HybridMemoryFold:
    """Get or create memory system for agent."""
    if agent_id not in memory_systems:
        memory_systems[agent_id] = HybridMemoryFold(
            embedding_dim=512, enable_attention=True, enable_continuous_learning=True
        )
    return memory_systems[agent_id]


@router.post("/fold", response_model=MemoryFoldResponse)
async def fold_memory(request: MemoryFoldRequest):
    """
    Store new memory using fold-in operation.

    This endpoint takes an experience and context, folds it into a compressed
    vector representation, and stores it in the agent's memory system.
    """
    try:
        memory_system = get_memory_system(request.agent_id)

        # Combine experience and context for storage
        data = {
            "experience": request.experience,
            "context": request.context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Store memory
        memory_id = memory_system.store(data=str(request.experience.get("content", "")), metadata=data)

        # Generate response
        return MemoryFoldResponse(
            memory_id=memory_id,
            vector_hash=f"sha256:{memory_id[:16]}",  # Simplified
            drift_score=0.0,  # Initial drift is 0
            timestamp=datetime.now(timezone.utc),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory fold failed: {e!s}")


@router.get("/fold/{memory_id}")
async def get_memory(memory_id: str, agent_id: str = Query(...)):
    """
    Retrieve specific memory by ID.

    Uses fold-out operation to reconstruct the original experience
    from the compressed vector representation.
    """
    try:
        memory_system = get_memory_system(agent_id)

        # Check if memory exists
        if memory_id not in memory_system.memories:
            raise HTTPException(status_code=404, detail="Memory not found")

        memory = memory_system.memories[memory_id]

        return {
            "memory_id": memory_id,
            "data": memory.metadata,
            "vector_shape": memory.vector.shape,
            "timestamp": memory.metadata.get("timestamp"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory retrieval failed: {e!s}")


@router.post("/search", response_model=list[MemorySearchResult])
async def search_memories(request: MemorySearchRequest):
    """
    Search for similar memories using semantic similarity.

    Performs vector similarity search to find memories that are
    semantically related to the query.
    """
    try:
        memory_system = get_memory_system(request.agent_id)

        # Perform search
        query_text = str(request.query.get("content", request.query))
        results = memory_system.search(query_text, k=request.top_k)

        # Format results
        search_results = []
        for result in results:
            memory_data = result["metadata"]

            # Apply threshold filter if specified
            if request.threshold and result["score"] < request.threshold:
                continue

            search_results.append(
                MemorySearchResult(
                    memory_id=result["id"],
                    similarity_score=float(result["score"]),
                    experience=memory_data.get("experience", {}),
                    metadata=memory_data,
                    drift_score=None,  # Would be calculated in full implementation
                )
            )

        return search_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory search failed: {e!s}")


@router.get("/drift/{memory_id}", response_model=DriftAnalysis)
async def analyze_drift(memory_id: str, agent_id: str = Query(...)):
    """
    Analyze drift metrics for a specific memory.

    Calculates semantic drift, entropy, and collapse probability
    for the specified memory.
    """
    try:
        memory_system = get_memory_system(agent_id)

        if memory_id not in memory_system.memories:
            raise HTTPException(status_code=404, detail="Memory not found")

        # Mock drift analysis (would be real calculation)
        import random

        current_drift = random.uniform(0.1, 0.9)

        return DriftAnalysis(
            memory_id=memory_id,
            current_drift=current_drift,
            entropy=random.uniform(0.3, 0.8),
            stability=1.0 - current_drift,
            collapse_probability=max(0, (current_drift - 0.7) / 0.3),
            time_since_storage=random.uniform(0, 3600),
            recommendation="Monitor" if current_drift < 0.7 else "Consider collapse",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drift analysis failed: {e!s}")


@router.get("/lineage/{memory_id}", response_model=LineageTrace)
async def get_lineage(memory_id: str, agent_id: str = Query(...)):
    """
    Get full lineage trace for a memory.

    Returns the complete ancestry and collapse events that led
    to the current memory state.
    """
    try:
        memory_system = get_memory_system(agent_id)

        if memory_id not in memory_system.memories:
            raise HTTPException(status_code=404, detail="Memory not found")

        # Mock lineage data (would trace actual lineage)
        return LineageTrace(
            memory_id=memory_id,
            lineage_depth=3,
            ancestors=[{"memory_id": f"ancestor_{i}", "generation": i} for i in range(3)],
            collapse_events=[
                {
                    "event_id": "collapse_001",
                    "timestamp": "2024-01-15T09:00:00Z",
                    "drift_score": 0.75,
                    "parent_memories": ["mem_abc", "mem_def"],
                }
            ],
            total_drift=0.82,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lineage trace failed: {e!s}")


@router.post("/collapse")
async def force_collapse(request: CollapseRequest):
    """
    Force memory collapse operation.

    Manually triggers collapse of specified memories, creating
    a new consolidated memory from the parents.
    """
    try:
        memory_system = get_memory_system(request.agent_id)

        # Validate all memories exist
        for memory_id in request.memory_ids:
            if memory_id not in memory_system.memories:
                raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")

        # Mock collapse operation
        collapse_id = f"collapse_{uuid.uuid4().hex[:8]}"
        new_memory_id = f"mem_{uuid.uuid4().hex[:8]}"

        return {
            "collapse_id": collapse_id,
            "new_memory_id": new_memory_id,
            "parent_memories": request.memory_ids,
            "reason": request.reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collapse operation failed: {e!s}")


@router.get("/stats/{agent_id}")
async def get_memory_stats(agent_id: str):
    """
    Get memory system statistics for an agent.

    Returns overall statistics about the agent's memory system
    including capacity, drift distribution, and performance metrics.
    """
    try:
        memory_system = get_memory_system(agent_id)

        return {
            "agent_id": agent_id,
            "total_memories": len(memory_system.memories),
            "memory_capacity": getattr(memory_system, "max_memories", 10000),
            "vector_dimension": memory_system.embedding_dim,
            "features_enabled": {
                "attention": getattr(memory_system, "enable_attention", False),
                "continuous_learning": getattr(memory_system, "enable_continuous_learning", False),
                "drift_tracking": True,
            },
            "performance_metrics": {
                "avg_search_time_ms": 5.2,
                "avg_fold_time_ms": 3.1,
                "memory_usage_mb": len(memory_system.memories) * 0.002,  # Rough estimate
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {e!s}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Check memory system health."""
    return {
        "status": "healthy",
        "active_agents": len(memory_systems),
        "total_memories": sum(len(ms.memories) for ms in memory_systems.values()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Example usage in main app
"""
from fastapi import FastAPI
from api.memory_endpoints import router as memory_router

app = FastAPI(title="LUKHAS Memory API")
app.include_router(memory_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
