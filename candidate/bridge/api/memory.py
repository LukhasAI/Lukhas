#!/usr/bin/env python3
"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony

══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ```PLAINTEXT
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: memory.py
║ Path: api/memory.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │                            LUKHAS MEMORY API - A CONFLUENCE OF THOUGHT       │
║ ├──────────────────────────────────────────────────────────────────────────────┤
║ │ Description: A symphonic orchestration of memory systems, evoking the         │
║ │ essence of recall and the art of forgetting.                                  │
║ ├──────────────────────────────────────────────────────────────────────────────┤
║ │ Poetic Essence:                                                                │
║ │ In the vast expanse of the digital cosmos, where ephemeral thoughts mingle with│
║ │ the eternal echoes of data, lies a sanctuary—the Memory API. Here, memories   │
║ │ are not mere fragments of the past but vibrant tapestries woven from the      │
║ │ threads of experience, each fold a testament to the fleeting nature of time.  │
║ │ With every invocation, we summon forth these treasures, crafting a narrative   │
║ │ that speaks of context and clarity, allowing the mind's eye to wander freely   │
║ │ through the labyrinthine corridors of knowledge.                               │
║ │                                                                               │
║ │ Like a skilled artisan shaping clay, this module enables the creation of       │
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛSTANDARD, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

try:
    from lukhas.consciousness.reflection.unified_memory_manager import MemoryFoldSystem
except ImportError:
    MemoryFoldSystem = None

try:
    from dream.dashboard.dream_metrics_view import metrics_view
except ImportError:
    metrics_view = None

logger = logging.getLogger("api.memory", timezone)


def convert_numpy_to_serializable(obj: Any) -> Any:
    """
    Convert numpy arrays and other non-serializable objects to JSON-serializable format.
    Recursively processes dictionaries, lists, and numpy arrays.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_to_serializable(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        # Handle custom objects by converting their attributes
        return {
            key: convert_numpy_to_serializable(value)
            for key, value in obj.__dict__.items()
        }
    else:
        return obj


router = APIRouter(prefix="/memory", tags=["memory"])

# Pydantic Models


class MemoryCreateRequest(BaseModel):
    emotion: str = Field(
        ...,
        description="Primary emotion for the memory",
        example="enlightenment",
    )
    context_snippet: str = Field(
        ..., description="Memory content/context", min_length=10
    )
    user_id: str = Field(..., description="User identifier", example="lukhas_admin")
    metadata: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class MemoryRecallRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    filter_emotion: Optional[str] = Field(
        None, description="Filter by specific emotion"
    )
    user_tier: int = Field(5, description="User access tier (0-5)", ge=0, le=5)
    limit: int = Field(
        50, description="Maximum number of memories to return", ge=1, le=1000
    )


class EnhancedRecallRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    target_emotion: str = Field(..., description="Target emotion for enhanced recall")
    user_tier: int = Field(5, description="User access tier (0-5)", ge=0, le=5)
    emotion_threshold: float = Field(
        0.3, description="Emotion similarity threshold", ge=0.0, le=1.0
    )
    context_query: Optional[str] = Field(
        None, description="Context query for semantic search"
    )
    max_results: int = Field(20, description="Maximum results to return", ge=1, le=100)


class APIResponse(BaseModel):
    status: str = Field(..., description="Response status")
    data: Any = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Optional message")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str = Field(..., description="Error message")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Initialize memory system
memory_system = None
if MemoryFoldSystem:
    try:
        memory_system = MemoryFoldSystem()
        logger.info("✅ MemoryFoldSystem initialized for API")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MemoryFoldSystem: {e}")


@router.post("/create", response_model=APIResponse)
async def create_memory(request: MemoryCreateRequest):
    """Create a new memory fold in the system"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Memory system not available")

    try:
        result = memory_system.create_memory_fold(
            emotion=request.emotion,
            context_snippet=request.context_snippet,
            user_id=request.user_id,
            metadata=request.metadata,
        )

        # Convert numpy arrays to serializable format
        serializable_result = convert_numpy_to_serializable(result)

        return APIResponse(
            status="success",
            data=serializable_result,
            message=f"Memory fold created with ID: {serializable_result.get('fold_id', 'unknown')}",
        )

    except Exception as e:
        logger.error(f"Memory creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recall", response_model=APIResponse)
async def recall_memories(request: MemoryRecallRequest):
    """Recall memories with optional filtering"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Memory system not available")

    try:
        memories = memory_system.recall_memory_folds(
            user_id=request.user_id,
            filter_emotion=request.filter_emotion,
            user_tier=request.user_tier,
            limit=request.limit,
        )

        # Convert numpy arrays to serializable format
        serializable_memories = convert_numpy_to_serializable(memories)

        return APIResponse(
            status="success",
            data={
                "memories": serializable_memories,
                "count": len(memories),
                "user_tier": request.user_tier,
                "filter_emotion": request.filter_emotion,
            },
            message=f"Retrieved {len(memories)} memories",
        )

    except Exception as e:
        logger.error(f"Memory recall failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhanced-recall", response_model=APIResponse)
async def enhanced_recall(request: EnhancedRecallRequest):
    """Enhanced contextual memory recall with semantic search"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Memory system not available")

    try:
        memories = memory_system.enhanced_recall_memory_folds(
            user_id=request.user_id,
            target_emotion=request.target_emotion,
            user_tier=request.user_tier,
            emotion_threshold=request.emotion_threshold,
            context_query=request.context_query,
            max_results=request.max_results,
        )

        # Convert numpy arrays to serializable format
        serializable_memories = convert_numpy_to_serializable(memories)

        return APIResponse(
            status="success",
            data={
                "memories": serializable_memories,
                "count": len(memories),
                "target_emotion": request.target_emotion,
                "threshold": request.emotion_threshold,
                "context_query": request.context_query,
            },
            message=f"Enhanced recall found {len(memories)} relevant memories",
        )

    except Exception as e:
        logger.error(f"Enhanced recall failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=APIResponse)
async def memory_history(user_id: str, limit: int = 20):
    """Retrieve recent memory folds for the user"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Memory system not available")

    try:
        folds = memory_system.database.get_folds(user_id=user_id, limit=limit)
        if metrics_view:
            metrics_view.update_memory_metrics(
                hits=len(folds), misses=0 if folds else 1
            )
        return APIResponse(
            status="success",
            data={"memories": folds, "count": len(folds)},
            message=f"Retrieved {len(folds)} memories",
        )

    except Exception as e:
        logger.error(f"History retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=APIResponse)
async def get_statistics(
    include_users: bool = Query(True, description="Include user statistics"),
    include_emotions: bool = Query(True, description="Include emotion statistics"),
    include_vectors: bool = Query(
        False, description="Include emotion vector statistics"
    ),
):
    """Get comprehensive memory system statistics"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Memory system not available")

    try:
        stats = memory_system.get_system_statistics()

        # Filter statistics based on request parameters
        filtered_stats = {
            "total_folds": stats.get("total_folds", 0),
            "unique_emotions": stats.get("unique_emotions", 0),
            "active_users": stats.get("active_users", 0),
            "recent_folds_24h": stats.get("recent_folds_24h", 0),
        }

        if include_users and "users" in stats:
            filtered_stats["users"] = stats["users"]

        if include_emotions and "emotions" in stats:
            filtered_stats["emotions"] = stats["emotions"]

        if include_vectors and "emotion_vectors" in stats:
            filtered_stats["emotion_vectors"] = stats["emotion_vectors"]

        return APIResponse(
            status="success",
            data=filtered_stats,
            message="System statistics retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=APIResponse)
async def memory_health_check():
    """Check memory system health and availability"""
    if not memory_system:
        return APIResponse(
            status="error",
            data={
                "available": False,
                "error": "Memory system not initialized",
            },
            message="Memory system unavailable",
        )

    try:
        # Test basic functionality
        stats = memory_system.get_system_statistics()

        return APIResponse(
            status="success",
            data={
                "available": True,
                "total_memories": stats.get("total_folds", 0),
                "system_ready": True,
            },
            message="Memory system is healthy and operational",
        )

    except Exception as e:
        logger.error(f"Memory health check failed: {e}")
        return APIResponse(
            status="error",
            data={"available": False, "error": str(e)},
            message="Memory system health check failed",
        )
