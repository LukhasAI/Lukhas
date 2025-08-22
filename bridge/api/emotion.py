"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony

LUKHAS Emotion API
=================

FastAPI endpoints for emotional processing operations including:
- Emotional landscape mapping
- Emotion cluster analysis
- Emotional neighborhood discovery
- Content emotion analysis

Based on successful Tier 5 testing with 4 emotion clusters and 23-dimensional space.
"""

from datetime import datetime
from typing import Any
from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel
from pydantic import Field

try:
    from lukhas.consciousness.reflection.unified_memory_manager import MemoryFoldSystem
except ImportError:
    MemoryFoldSystem = None

logger = logging.getLogger("api.emotion")

router = APIRouter(prefix="/emotion", tags=["emotion"])

# Pydantic Models


class EmotionAnalysisRequest(BaseModel):
    content: str = Field(
        ...,
        description="Content to analyze for emotional content",
        min_length=5,
    )
    analysis_depth: str = Field(
        "standard", description="Analysis depth (basic, standard, deep)"
    )
    return_vectors: bool = Field(False, description="Return emotion vectors")


class EmotionClusterRequest(BaseModel):
    tier_level: int = Field(5, description="User tier level for access", ge=0, le=5)
    cluster_method: str = Field(
        "automatic",
        description="Clustering method (automatic, hierarchical, kmeans)",
    )
    min_cluster_size: int = Field(2, description="Minimum cluster size", ge=1, le=10)


class EmotionNeighborhoodRequest(BaseModel):
    target_emotion: str = Field(
        ...,
        description="Target emotion for neighborhood analysis",
        example="enlightenment",
    )
    threshold: float = Field(0.6, description="Similarity threshold", ge=0.0, le=1.0)
    max_neighbors: int = Field(
        10, description="Maximum neighbors to return", ge=1, le=50
    )


class APIResponse(BaseModel):
    status: str = Field(..., description="Response status")
    data: Any = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Optional message")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# Initialize memory system for emotion operations
memory_system = None
if MemoryFoldSystem:
    try:
        memory_system = MemoryFoldSystem()
        logger.info("✅ MemoryFoldSystem initialized for Emotion API")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MemoryFoldSystem for emotions: {e}")


@router.get("/landscape", response_model=APIResponse)
async def get_emotional_landscape(
    user_id: str = Query("lukhas_admin", description="User identifier"),
    include_vectors: bool = Query(
        False, description="Include emotion vectors in response"
    ),
    include_statistics: bool = Query(True, description="Include emotion statistics"),
):
    """Get comprehensive emotional landscape mapping"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Emotion system not available")

    try:
        # Get system statistics for emotional data
        stats = memory_system.get_system_statistics()

        # Get emotion clusters
        clusters = memory_system.create_emotion_clusters(tier_level=5)

        # Build emotional landscape
        landscape = {
            "cluster_count": len(clusters),
            "clusters": clusters,
            "total_unique_emotions": stats.get("unique_emotions", 0),
        }

        if include_statistics and "emotions" in stats:
            landscape["emotion_statistics"] = stats["emotions"]

        if include_vectors:
            landscape["emotion_vectors"] = {
                "total_dimensions": len(memory_system.emotion_vectors),
                "vector_space": "3D emotional coordinate system",
                "available_emotions": list(memory_system.emotion_vectors.keys()),
            }

        return APIResponse(
            status="success",
            data=landscape,
            message=f"Emotional landscape mapped: {len(clusters)} clusters,"
            {landscape['total_unique_emotions']} unique emotions",
        )

    except Exception as e:
        logger.error(f"Emotional landscape mapping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=APIResponse)
async def analyze_emotion(request: EmotionAnalysisRequest):
    """Analyze emotional content of text"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Emotion system not available")

    try:
        # Simple emotion analysis based on keywords (in production, use ML models)
        content_lower = request.content.lower()

        # Emotion keyword mapping
        emotion_keywords = {
            "enlightenment": [
                "enlightenment",
                "insight",
                "discovery",
                "understanding",
                "clarity",
            ],
            "transcendence": [
                "transcendence",
                "beyond",
                "higher",
                "elevated",
                "spiritual",
            ],
            "unity": ["unity", "harmony", "connection", "oneness", "together"],
            "joy": ["joy", "happiness", "delight", "pleasure", "bliss"],
            "lucid": ["lucid", "clear", "conscious", "aware", "mindful"],
            "wonder": ["wonder", "amazement", "awe", "marvel", "astonishment"],
            "curiosity": [
                "curious",
                "wonder",
                "explore",
                "investigate",
                "question",
            ],
            "fear": ["fear", "afraid", "scared", "terrified", "anxious"],
            "anger": ["anger", "angry", "rage", "furious", "mad"],
            "sadness": ["sad", "grief", "sorrow", "melancholy", "depression"],
        }

        detected_emotions = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                detected_emotions[emotion] = score / len(keywords)

        # Get dominant emotion
        dominant_emotion = None
        if detected_emotions:
            dominant_emotion = max(detected_emotions.items(), key=lambda x: x[1])

        analysis_result = {
            "detected_emotions": detected_emotions,
            "dominant_emotion": (dominant_emotion[0] if dominant_emotion else None),
            "confidence": dominant_emotion[1] if dominant_emotion else 0.0,
            "analysis_depth": request.analysis_depth,
            "content_length": len(request.content),
        }

        if request.return_vectors and dominant_emotion:
            emotion_name = dominant_emotion[0]
            if emotion_name in memory_system.emotion_vectors:
                analysis_result["emotion_vector"] = memory_system.emotion_vectors[
                    emotion_name
                ]

        return APIResponse(
            status="success",
            data=analysis_result,
            message=f"Emotion analysis complete: {dominant_emotion[0] if dominant_emotion else 'No clear emotion'} detected",
        )

    except Exception as e:
        logger.error(f"Emotion analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clusters", response_model=APIResponse)
async def create_emotion_clusters(request: EmotionClusterRequest):
    """Create and analyze emotion clusters"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Emotion system not available")

    try:
        clusters = memory_system.create_emotion_clusters(tier_level=request.tier_level)

        # Analyze cluster characteristics
        cluster_analysis = {}
        for cluster_name, emotions in clusters.items():
            cluster_analysis[cluster_name] = {
                "emotion_count": len(emotions),
                "emotions": emotions,
                "cluster_strength": len(emotions)
                / sum(len(e) for e in clusters.values()),
                "representative_emotion": emotions[0] if emotions else None,
            }

        return APIResponse(
            status="success",
            data={
                "clusters": clusters,
                "cluster_analysis": cluster_analysis,
                "total_clusters": len(clusters),
                "clustering_method": request.cluster_method,
            },
            message=f"Created {len(clusters)} emotion clusters with {request.cluster_method} method",
        )

    except Exception as e:
        logger.error(f"Emotion clustering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/neighborhood/{emotion}", response_model=APIResponse)
async def get_emotion_neighborhood(
    emotion: str,
    threshold: float = Query(0.6, description="Similarity threshold", ge=0.0, le=1.0),
    max_neighbors: int = Query(10, description="Maximum neighbors", ge=1, le=50),
):
    """Get emotional neighborhood for a specific emotion"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Emotion system not available")

    try:
        neighborhood = memory_system.get_emotional_neighborhood(
            target_emotion=emotion, threshold=threshold
        )

        # Limit results if requested
        if len(neighborhood) > max_neighbors:
            neighborhood = neighborhood[:max_neighbors]

        # Calculate neighborhood metrics
        metrics = {
            "target_emotion": emotion,
            "neighbor_count": len(neighborhood),
            "threshold_used": threshold,
            "neighborhood_density": (
                len(neighborhood) / len(memory_system.emotion_vectors)
                if memory_system.emotion_vectors:
                else 0:
            ),
        }

        return APIResponse(
            status="success",
            data={
                "neighborhood": neighborhood,
                "metrics": metrics,
                "target_emotion": emotion,
            },
            message=f"Found {len(neighborhood)} emotional neighbors for '{emotion}'",
        )

    except Exception as e:
        logger.error(f"Emotional neighborhood analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vectors", response_model=APIResponse)
async def get_emotion_vectors(
    include_coordinates: bool = Query(False, description="Include vector coordinates"),
    emotion_filter: Optional[str] = Query(
        None, description="Filter by specific emotion"
    ),
):
    """Get emotion vector space information"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="Emotion system not available")

    try:
        vectors = memory_system.emotion_vectors

        # Filter if requested
        if emotion_filter:
            vectors = {
                k: v for k, v in vectors.items() if emotion_filter.lower() in k.lower()
            }

        vector_info = {
            "total_emotions": len(vectors),
            "available_emotions": list(vectors.keys()),
            "vector_dimensions": 3,  # Based on the 3D coordinate system
            "vector_space_type": "3D emotional coordinate system",
        }

        if include_coordinates:
            vector_info["coordinates"] = vectors

        return APIResponse(
            status="success",
            data=vector_info,
            message=f"Retrieved {len(vectors)} emotion vectors",
        )

    except Exception as e:
        logger.error(f"Emotion vector retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=APIResponse)
async def emotion_health_check():
    """Check emotion system health and capabilities"""
    if not memory_system:
        return APIResponse(
            status="error",
            data={
                "available": False,
                "error": "Emotion system not initialized",
            },
            message="Emotion system unavailable",
        )

    try:
        # Test emotion functionality
        stats = memory_system.get_system_statistics()
        clusters = memory_system.create_emotion_clusters(tier_level=5)

        return APIResponse(
            status="success",
            data={
                "available": True,
                "emotion_processing": "operational",
                "cluster_analysis": "available",
                "neighborhood_mapping": "ready",
                "total_emotions": stats.get("unique_emotions", 0),
                "cluster_count": len(clusters),
                "vector_dimensions": len(memory_system.emotion_vectors),
            },
            message="Emotion system is healthy and operational",
        )

    except Exception as e:
        logger.error(f"Emotion health check failed: {e}")
        return APIResponse(
            status="error",
            data={"available": False, "error": str(e)},
            message="Emotion system health check failed",
        )