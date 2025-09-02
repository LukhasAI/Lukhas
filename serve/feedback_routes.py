"""
Feedback Card System API Routes
================================
Enables human-in-the-loop learning through the feedback card system.
Part of the 21-day AGI implementation roadmap.
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from feedback.card_system import FeedbackCardSystem
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/feedback", tags=["feedback"])

# Initialize feedback system (singleton)
feedback_system = FeedbackCardSystem(storage_path="feedback_data")


class FeedbackRequest(BaseModel):
    """Request model for capturing feedback."""

    action_id: str = Field(..., description="ID of the action being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    note: Optional[str] = Field(None, description="Optional text feedback")
    symbols: Optional[list[str]] = Field(default_factory=list, description="User-selected symbols")
    context: Optional[dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    user_id: Optional[str] = Field(None, description="User ID (will be hashed)")


class FeedbackResponse(BaseModel):
    """Response model for feedback capture."""

    card_id: str
    rating: int
    timestamp: float
    message: str = "Feedback captured successfully"


class LearningReportResponse(BaseModel):
    """Response model for learning report."""

    user_id_hash: str
    total_feedback_cards: int
    overall_satisfaction: float
    improvement_trend: float
    preferred_styles: list[str]
    summary: str
    recommendations: dict[str, Any]


class SystemMetricsResponse(BaseModel):
    """Response model for system metrics."""

    cards_captured: int
    patterns_identified: int
    policies_updated: int
    validations_passed: int
    validations_failed: int
    total_cards: int
    total_patterns: int
    total_updates: int


@router.post("/capture", response_model=FeedbackResponse)
async def capture_feedback(request: FeedbackRequest):
    """
    Capture user feedback for an AI action.

    This endpoint allows users to rate AI responses and provide feedback,
    which is used for continuous alignment and learning.
    """
    try:
        # Capture the feedback
        card = feedback_system.capture_feedback(
            action_id=request.action_id,
            rating=request.rating,
            note=request.note,
            symbols=request.symbols,
            context=request.context,
            user_id=request.user_id,
        )

        logger.info(f"Captured feedback card {card.card_id} with rating {request.rating}")

        return FeedbackResponse(
            card_id=card.card_id,
            rating=card.rating.value,
            timestamp=card.timestamp,
        )

    except Exception as e:
        logger.error(f"Error capturing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=list[FeedbackResponse])
async def capture_batch_feedback(requests: list[FeedbackRequest]):
    """
    Capture multiple feedback cards at once.

    Useful for batch processing of user feedback sessions.
    """
    responses = []

    for request in requests:
        try:
            card = feedback_system.capture_feedback(
                action_id=request.action_id,
                rating=request.rating,
                note=request.note,
                symbols=request.symbols,
                context=request.context,
                user_id=request.user_id,
            )

            responses.append(
                FeedbackResponse(
                    card_id=card.card_id,
                    rating=card.rating.value,
                    timestamp=card.timestamp,
                )
            )

        except Exception as e:
            logger.error(f"Error capturing feedback for action {request.action_id}: {e}")
            # Continue processing other feedback

    logger.info(f"Captured {len(responses)} feedback cards in batch")
    return responses


@router.get("/report/{user_id}", response_model=LearningReportResponse)
async def get_learning_report(user_id: str):
    """
    Get a learning report for a specific user.

    This report explains what the system has learned from the user's feedback,
    including preferences, patterns, and recommendations.
    """
    try:
        report = feedback_system.explain_learning(user_id)

        # Format recommendations
        recommendations = report.recommended_adjustments or {}

        # Create summary
        summary = f"Based on {report.total_feedback_cards} feedback cards, "
        summary += f"your satisfaction level is {report.overall_satisfaction:.1f}/5. "

        if report.improvement_trend > 0:
            summary += "The system is improving based on your feedback. "
        elif report.improvement_trend < 0:
            summary += "Recent changes may not align with your preferences. "

        if report.preferred_styles:
            summary += f"Your preferred style is {', '.join(report.preferred_styles)}."

        return LearningReportResponse(
            user_id_hash=report.user_id_hash,
            total_feedback_cards=report.total_feedback_cards,
            overall_satisfaction=report.overall_satisfaction,
            improvement_trend=report.improvement_trend,
            preferred_styles=report.preferred_styles,
            summary=summary,
            recommendations=recommendations,
        )

    except Exception as e:
        logger.error(f"Error generating learning report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    Get overall feedback system metrics.

    Provides insights into the feedback system's operation and learning progress.
    """
    try:
        metrics = feedback_system.get_metrics()

        return SystemMetricsResponse(
            cards_captured=metrics["cards_captured"],
            patterns_identified=metrics["patterns_identified"],
            policies_updated=metrics["policies_updated"],
            validations_passed=metrics["validations_passed"],
            validations_failed=metrics["validations_failed"],
            total_cards=metrics["total_cards"],
            total_patterns=metrics["total_patterns"],
            total_updates=metrics["total_updates"],
        )

    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-learning")
async def trigger_learning(background_tasks: BackgroundTasks):
    """
    Manually trigger pattern extraction and policy updates.

    This endpoint triggers the learning process to extract patterns from
    recent feedback and generate policy updates.
    """
    try:
        # Get recent feedback cards for analysis
        recent_cards = feedback_system.feedback_cards[-100:]  # Last 100 cards

        if len(recent_cards) < 10:
            return {
                "status": "skipped",
                "message": "Not enough feedback cards for learning (minimum 10 required)",
            }

        # Run learning in background
        background_tasks.add_task(run_learning_cycle, recent_cards)

        return {
            "status": "triggered",
            "message": f"Learning cycle triggered with {len(recent_cards)} feedback cards",
        }

    except Exception as e:
        logger.error(f"Error triggering learning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_learning_cycle(cards):
    """Background task to run learning cycle."""
    try:
        # Extract patterns
        patterns = feedback_system.extract_patterns(cards)
        logger.info(f"Extracted {len(patterns)} patterns from feedback")

        # Generate policy updates
        if patterns:
            update = feedback_system.update_policy(patterns)
            if update:
                # Validate the update
                if feedback_system.validate_update(update):
                    logger.info(f"Policy update {update.update_id} validated and ready to apply")
                else:
                    logger.warning(f"Policy update {update.update_id} failed validation")

    except Exception as e:
        logger.error(f"Error in learning cycle: {e}")


@router.get("/health")
async def health_check():
    """Health check for feedback system."""
    try:
        metrics = feedback_system.get_metrics()
        return {
            "status": "healthy",
            "total_cards": metrics["total_cards"],
            "system_active": True,
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "system_active": False}
