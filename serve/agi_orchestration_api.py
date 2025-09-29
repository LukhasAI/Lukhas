"""
AGI-Enhanced Orchestration API for LUKHAS

Enhanced orchestration endpoints that integrate AGI multi-model routing,
consensus building, and intelligent model selection with existing LUKHAS systems.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# AGI Core imports
try:
    from cognitive_core.orchestration.capability_matrix import CapabilityDimension, CapabilityMatrix
    from cognitive_core.orchestration.consensus_engine import ConsensusEngine, ConsensusMethod
    from cognitive_core.orchestration.cost_optimizer import CostConstraints, CostOptimizer, OptimizationStrategy
    from cognitive_core.orchestration.model_router import ModelRouter, RoutingRequest, TaskType

    AGI_ORCHESTRATION_AVAILABLE = True
except ImportError:
    AGI_ORCHESTRATION_AVAILABLE = False
    logging.warning("AGI Orchestration components not available")

# Existing LUKHAS orchestration (graceful fallback)
try:
    from lukhas.bridge.orchestration.multi_ai_orchestrator import MultiAIOrchestrator

    LUKHAS_ORCHESTRATION_AVAILABLE = True
except ImportError:
    LUKHAS_ORCHESTRATION_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic models
class OrchestrationRequest(BaseModel):
    content: str
    task_type: Optional[str] = "general"
    models: Optional[list[str]] = None  # Specific models to use
    use_consensus: bool = False
    consensus_method: Optional[str] = "majority_vote"
    max_cost_per_request: Optional[float] = None
    constellation_context: Optional[dict[str, float]] = None
    priority: float = 1.0


class OrchestrationResponse(BaseModel):
    response: str
    model_used: str
    reasoning: Optional[str] = None
    confidence: float
    latency_ms: int
    cost: Optional[float] = None
    quality_score: float
    metadata: dict[str, Any]


class ConsensusRequest(BaseModel):
    question: str
    models: list[str]
    method: str = "majority_vote"
    consensus_threshold: float = 0.7
    max_attempts: int = 3
    constellation_context: Optional[dict[str, float]] = None


class ConsensusResponse(BaseModel):
    consensus_reached: bool
    final_answer: str
    agreement_level: float
    confidence_score: float
    individual_responses: list[dict[str, Any]]
    disagreements: list[str]
    processing_time_ms: int


class ModelCapabilitiesRequest(BaseModel):
    task_requirements: dict[str, float]
    constellation_filter: Optional[dict[str, float]] = None
    cost_constraints: Optional[dict[str, Any]] = None


class ModelCapabilitiesResponse(BaseModel):
    ranked_models: list[dict[str, Any]]
    recommendations: list[str]
    cost_analysis: dict[str, Any]


# Global orchestration components
agi_model_router: Optional[ModelRouter] = None
agi_consensus_engine: Optional[ConsensusEngine] = None
agi_capability_matrix: Optional[CapabilityMatrix] = None
agi_cost_optimizer: Optional[CostOptimizer] = None


async def initialize_orchestration_components():
    """Initialize AGI orchestration components."""

    if not AGI_ORCHESTRATION_AVAILABLE:
        return

    try:
        # Initialize components and assign into module globals to avoid `global` statement
        g = globals()
        g["agi_capability_matrix"] = CapabilityMatrix()
        g["agi_cost_optimizer"] = CostOptimizer()
        g["agi_model_router"] = ModelRouter()
        g["agi_consensus_engine"] = ConsensusEngine()

        logger.info("AGI orchestration components initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize AGI orchestration components: {e}")


@router.on_event("startup")
async def startup_event():
    """Initialize orchestration components on router startup."""
    await initialize_orchestration_components()


@router.post("/api/v2/orchestration/route", response_model=OrchestrationResponse)
async def intelligent_model_routing(request: OrchestrationRequest):
    """
    Intelligent model routing with AGI capability matching and cost optimization.
    Routes requests to the most suitable model based on task requirements,
    capabilities, cost constraints, and constellation context.
    """
    start_time = datetime.now(timezone.utc)

    try:
        # Fallback to existing LUKHAS orchestration if AGI not available
        if not AGI_ORCHESTRATION_AVAILABLE or not agi_model_router:
            if LUKHAS_ORCHESTRATION_AVAILABLE:
                # Use existing orchestration
                orchestrator = MultiAIOrchestrator()
                result = await orchestrator.execute_consensus(request.content)

                return OrchestrationResponse(
                    response=result.get("response", "No response"),
                    model_used=result.get("providers", ["unknown"])[0] if result.get("providers") else "unknown",
                    confidence=result.get("confidence", 0.5),
                    latency_ms=result.get("latency_ms", 0),
                    quality_score=0.7,
                    metadata={"source": "lukhas_orchestration"},
                )
            else:
                # Basic fallback
                await asyncio.sleep(0.1)
                return OrchestrationResponse(
                    response=f"Processed: {request.content}",
                    model_used="fallback",
                    confidence=0.5,
                    latency_ms=100,
                    quality_score=0.5,
                    metadata={"source": "fallback"},
                )

        # Map task type string to enum
        task_type_mapping = {
            "reasoning": TaskType.REASONING,
            "creative": TaskType.CREATIVE,
            "technical": TaskType.TECHNICAL,
            "analytical": TaskType.ANALYTICAL,
            "conversational": TaskType.CONVERSATIONAL,
            "code_generation": TaskType.CODE_GENERATION,
            "mathematical": TaskType.MATH,
            "scientific": TaskType.SCIENTIFIC,
            "synthesis": TaskType.SYNTHESIS,
            "classification": TaskType.CLASSIFICATION,
        }

        task_type = task_type_mapping.get(request.task_type, TaskType.REASONING)

        # Create AGI routing request
        routing_request = RoutingRequest(
            content=request.content,
            task_type=task_type,
            priority=request.priority,
            max_cost_per_request=request.max_cost_per_request,
            constellation_context=request.constellation_context,
        )

        # Route request through Cognitive system
        decision, response = await agi_model_router.route_request(routing_request)

        # Calculate processing time
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        return OrchestrationResponse(
            response=response.content,
            model_used=response.model_used,
            reasoning=decision.reasoning,
            confidence=response.quality_score,
            latency_ms=int(processing_time),
            cost=response.cost,
            quality_score=response.quality_score,
            metadata={
                "decision_factors": decision.decision_factors,
                "alternative_models": decision.alternative_models,
                "constellation_alignment": request.constellation_context or {},
            },
        )

    except Exception as e:
        logger.error(f"Error in intelligent model routing: {e}")
        raise HTTPException(status_code=500, detail=f"Routing error: {e!s}") from e


@router.post("/api/v2/orchestration/consensus", response_model=ConsensusResponse)
async def multi_model_consensus(request: ConsensusRequest):
    """
    Multi-model consensus building with AGI orchestration.
    Gathers responses from multiple models and builds consensus
    using various consensus methods and agreement analysis.
    """
    start_time = datetime.now(timezone.utc)

    try:
        # Fallback if AGI not available
        if not AGI_ORCHESTRATION_AVAILABLE or not agi_consensus_engine:
            await asyncio.sleep(0.2)
            return ConsensusResponse(
                consensus_reached=True,
                final_answer="Consensus building not available - using fallback",
                agreement_level=0.5,
                confidence_score=0.5,
                individual_responses=[],
                disagreements=[],
                processing_time_ms=200,
            )

        # Map consensus method string to enum
        method_mapping = {
            "majority_vote": ConsensusMethod.MAJORITY_VOTE,
            "weighted_quality": ConsensusMethod.WEIGHTED_QUALITY,
            "confidence_threshold": ConsensusMethod.CONFIDENCE_THRESHOLD,
            "iterative_refinement": ConsensusMethod.ITERATIVE_REFINEMENT,
            "dream_synthesis": ConsensusMethod.DREAM_SYNTHESIS,
        }

        consensus_method = method_mapping.get(request.method, ConsensusMethod.MAJORITY_VOTE)

        # Build consensus
        consensus_result = await agi_consensus_engine.reach_consensus(
            question=request.question,
            models=request.models,
            method=consensus_method,
            consensus_threshold=request.consensus_threshold,
            max_attempts=request.max_attempts,
            constellation_context=request.constellation_context,
        )

        # Calculate processing time
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        return ConsensusResponse(
            consensus_reached=consensus_result.consensus_reached,
            final_answer=consensus_result.final_answer,
            agreement_level=consensus_result.agreement_level,
            confidence_score=consensus_result.confidence_score,
            individual_responses=[
                {
                    "model": resp.model_used,
                    "response": resp.content[:200],  # Truncate for API
                    "confidence": resp.quality_score,
                    "latency_ms": resp.latency_ms,
                }
                for resp in consensus_result.individual_responses
            ],
            disagreements=consensus_result.disagreements,
            processing_time_ms=int(processing_time),
        )

    except Exception as e:
        logger.error(f"Error in multi-model consensus: {e}")
        raise HTTPException(status_code=500, detail=f"Consensus error: {e!s}") from e


@router.post("/api/v2/orchestration/capabilities", response_model=ModelCapabilitiesResponse)
async def analyze_model_capabilities(request: ModelCapabilitiesRequest):
    """
    Analyze and rank model capabilities for specific task requirements.
    Provides detailed capability analysis, cost optimization,
    and model recommendations based on requirements.
    """

    try:
        # Fallback if AGI not available
        if not AGI_ORCHESTRATION_AVAILABLE or not agi_capability_matrix:
            return ModelCapabilitiesResponse(
                ranked_models=[{"model_id": "fallback-model", "score": 0.5, "capabilities": {}, "cost_estimate": 0.01}],
                recommendations=["AGI capability analysis not available"],
                cost_analysis={"status": "unavailable"},
            )

        # Convert requirements to capability dimensions
        required_capabilities = {}
        for capability_name, min_score in request.task_requirements.items():
            # Map string names to capability dimensions
            capability_mapping = {
                "reasoning": CapabilityDimension.REASONING,
                "creativity": CapabilityDimension.CREATIVITY,
                "technical_accuracy": CapabilityDimension.TECHNICAL_ACCURACY,
                "mathematical": CapabilityDimension.MATHEMATICAL,
                "scientific": CapabilityDimension.SCIENTIFIC,
                "language_quality": CapabilityDimension.LANGUAGE_QUALITY,
                "code_quality": CapabilityDimension.CODE_QUALITY,
                "speed": CapabilityDimension.SPEED,
                "cost_efficiency": CapabilityDimension.COST_EFFICIENCY,
                "consistency": CapabilityDimension.CONSISTENCY,
            }

            if capability_name in capability_mapping:
                required_capabilities[capability_mapping[capability_name]] = min_score

        # Create task requirements
        from cognitive_core.orchestration.capability_matrix import TaskRequirements

        task_reqs = TaskRequirements(
            task_type=None,  # Will be inferred
            required_capabilities=required_capabilities,
            preferred_capabilities=required_capabilities,
            constellation_context=request.constellation_filter,
        )

        # Get model rankings
        rankings = agi_capability_matrix.rank_models(task_reqs)

        # Cost analysis if optimizer available
        cost_analysis = {"status": "available"}
        recommendations = []

        if agi_cost_optimizer and request.cost_constraints:
            # Create cost constraints
            constraints = CostConstraints(
                max_cost_per_request=request.cost_constraints.get("max_cost_per_request"),
                strategy=OptimizationStrategy.BALANCE_COST_QUALITY,
            )

            # Optimize model selection
            optimized_models = agi_cost_optimizer.optimize_model_selection(rankings, constraints)

            cost_analysis = {
                "status": "optimized",
                "optimization_strategy": constraints.strategy.value,
                "cost_efficient_models": [model[0] for model in optimized_models[:3]],
            }

            recommendations.extend(
                [
                    (
                        f"Most cost-efficient: {optimized_models[0][0]}"
                        if optimized_models
                        else ("No models meet cost constraints")
                    ),
                    "Best quality/cost ratio found" if optimized_models else ("Consider relaxing cost constraints"),
                ]
            )

        # Format response
        ranked_models_data = []
        for model_id, score in rankings[:10]:  # Top 10
            model_profile = agi_capability_matrix.get_model_capabilities(model_id)
            if model_profile:
                ranked_models_data.append(
                    {
                        "model_id": model_id,
                        "score": score,
                        "capabilities": {dim.value: score for dim, score in model_profile.capabilities.items()},
                        "specializations": [spec.value for spec in model_profile.specializations],
                        "cost_per_token": model_profile.cost_per_token,
                        "latency_ms": model_profile.latency_ms,
                        "constellation_alignment": model_profile.constellation_alignment,
                    }
                )

        if not recommendations:
            recommendations = [
                f"Top recommendation: {rankings[0][0]}" if rankings else "No suitable models found",
                (
                    "Consider constellation context for better alignment"
                    if not request.constellation_filter
                    else "Constellation alignment applied"
                ),
            ]

        return ModelCapabilitiesResponse(
            ranked_models=ranked_models_data, recommendations=recommendations, cost_analysis=cost_analysis
        )

    except Exception as e:
        logger.error(f"Error in capability analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {e!s}") from e


@router.get("/api/v2/orchestration/models")
async def list_available_models():
    """List all available models with their capabilities and status."""

    try:
        if not AGI_ORCHESTRATION_AVAILABLE or not agi_capability_matrix:
            return {"models": [], "total_count": 0, "status": "AGI orchestration not available"}

        models_data = []
        for model_id, profile in agi_capability_matrix.model_profiles.items():
            models_data.append(
                {
                    "model_id": model_id,
                    "name": profile.name if hasattr(profile, "name") else model_id,
                    "capabilities": {dim.value: score for dim, score in profile.capabilities.items()},
                    "specializations": [spec.value for spec in profile.specializations],
                    "cost_per_token": profile.cost_per_token,
                    "context_window": profile.context_window,
                    "constellation_alignment": profile.constellation_alignment,
                    "performance": agi_capability_matrix.get_model_performance_stats(model_id),
                }
            )

        return {"models": models_data, "total_count": len(models_data), "status": "active"}

    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e!s}") from e


@router.post("/api/v2/orchestration/feedback")
async def record_model_feedback(
    model_id: str,
    task_type: str,
    success: bool,
    _effectiveness: float,
    latency_ms: int,
    quality_score: float,
):
    """Record feedback about model performance for learning and optimization."""

    try:
        if not AGI_ORCHESTRATION_AVAILABLE:
            return {"status": "feedback_not_available"}

        # Record in capability matrix
        if agi_capability_matrix:
            from cognitive_core.orchestration.capability_matrix import TaskType as AGITaskType

            task_type_mapping = {
                "reasoning": AGITaskType.REASONING,
                "creative": AGITaskType.CREATIVE,
                "technical": AGITaskType.TECHNICAL,
                "analytical": AGITaskType.ANALYTICAL,
                "conversational": AGITaskType.CONVERSATIONAL,
            }

            agi_task_type = task_type_mapping.get(task_type, AGITaskType.REASONING)
            agi_capability_matrix.add_task_result(model_id, agi_task_type, success, latency_ms, quality_score)

        # Record in cost optimizer
        if agi_cost_optimizer:
            # Estimate token usage (simplified)
            input_tokens = 100  # Would be calculated from actual request
            output_tokens = 50
            agi_cost_optimizer.record_usage(model_id, input_tokens, output_tokens, quality_score)

        return {
            "status": "feedback_recorded",
            "model_id": model_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback error: {e!s}") from e


@router.get("/api/v2/orchestration/stats")
async def get_orchestration_stats():
    """Get comprehensive orchestration statistics and performance metrics."""

    try:
        stats = {
            "agi_available": AGI_ORCHESTRATION_AVAILABLE,
            "lukhas_available": LUKHAS_ORCHESTRATION_AVAILABLE,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if AGI_ORCHESTRATION_AVAILABLE:
            if agi_capability_matrix:
                matrix_stats = agi_capability_matrix.get_model_performance_stats("gpt-4-turbo")  # Example
                stats["capability_matrix"] = {
                    "total_models": len(agi_capability_matrix.model_profiles),
                    "performance_tracking": bool(matrix_stats),
                }

            if agi_cost_optimizer:
                cost_stats = agi_cost_optimizer.get_usage_statistics()
                stats["cost_optimization"] = {
                    "requests_tracked": cost_stats.requests_count,
                    "total_cost": cost_stats.total_cost,
                    "avg_quality": cost_stats.avg_quality_score,
                }

            if agi_consensus_engine:
                consensus_stats = (
                    agi_consensus_engine.get_consensus_stats()
                    if hasattr(agi_consensus_engine, "get_consensus_stats")
                    else {}
                )
                stats["consensus"] = {
                    "available_methods": [
                        "majority_vote",
                        "weighted_quality",
                        "confidence_threshold",
                        "iterative_refinement",
                        "dream_synthesis",
                    ],
                    "stats": consensus_stats,
                }

        return stats

    except Exception as e:
        logger.error(f"Error getting orchestration stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats error: {e!s}") from e
