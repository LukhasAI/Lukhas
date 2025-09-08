#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
Feedback Collection API
=======================
RESTful API for collecting multi-modal user feedback with compliance support.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from core.common import get_logger
from feedback.user_feedback_system import (
    ComplianceRegion,
    EmotionEmoji,
    FeedbackType,
    UserFeedbackSystem,
)

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LUKHAS Feedback Collection API",
    description="Multi-modal feedback collection with regulatory compliance",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global feedback system instance
feedback_system = None


# Request/Response models
class FeedbackRequest(BaseModel):
    """Feedback submission request"""

    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    action_id: str = Field(..., description="Action being given feedback on")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    content: dict[str, Any] = Field(..., description="Feedback content")
    context: dict[str, Any] = Field(..., description="Context about the action")
    region: Optional[ComplianceRegion] = Field(ComplianceRegion.GLOBAL, description="User's regulatory region")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "session_id": "session_456",
                "action_id": "decision_789",
                "feedback_type": "rating",
                "content": {"rating": 5},
                "context": {
                    "action_type": "recommendation",
                    "decision": "Suggested option A",
                },
                "region": "eu",
            }
        }


class QuickFeedbackRequest(BaseModel):
    """Quick feedback submission (simplified)"""

    user_id: str
    action_id: str
    thumbs_up: bool
    session_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "action_id": "decision_789",
                "thumbs_up": True,
            }
        }


class EmojiFeedbackRequest(BaseModel):
    """Emoji feedback submission"""

    user_id: str
    session_id: str
    action_id: str
    emoji: str
    context: Optional[dict[str, Any]] = None

    @validator("emoji")
    def validate_emoji(cls, v):
        valid_emojis = [e.value for e in EmotionEmoji]
        if v not in valid_emojis:
            raise ValueError(f"Invalid emoji. Must be one of: {valid_emojis}")
        return v


class TextFeedbackRequest(BaseModel):
    """Natural language feedback submission"""

    user_id: str
    session_id: str
    action_id: str
    text: str = Field(..., min_length=1, max_length=1000)
    context: Optional[dict[str, Any]] = None


class FeedbackEditRequest(BaseModel):
    """Edit existing feedback"""

    feedback_id: str
    user_id: str
    new_content: dict[str, Any]


class FeedbackResponse(BaseModel):
    """Standard feedback response"""

    success: bool
    feedback_id: Optional[str] = None
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FeedbackHistoryResponse(BaseModel):
    """User feedback history"""

    user_id: str
    feedback_items: list[dict[str, Any]]
    total_count: int


class FeedbackSummaryResponse(BaseModel):
    """Aggregated feedback summary"""

    action_id: str
    total_feedback: int
    average_rating: Optional[float]
    sentiment_distribution: dict[str, float]
    emoji_distribution: dict[str, int]
    common_themes: list[str]
    improvement_suggestions: list[str]


class ConsentRequest(BaseModel):
    """User consent for feedback collection"""

    user_id: str
    consent_given: bool
    region: ComplianceRegion
    allow_anonymized_usage: bool = True
    data_retention_days: Optional[int] = None


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize feedback system on startup"""
    global feedback_system

    logger.info("Starting Feedback Collection API...")

    # Initialize feedback system
    feedback_system = UserFeedbackSystem(
        config={
            "enable_emoji": True,
            "enable_voice": False,  # Future feature
            "min_feedback_interval": 10,  # 10 seconds minimum between feedback
        }
    )

    # Setup mock services for demo
    await _setup_mock_services()

    await feedback_system.initialize()

    logger.info("Feedback Collection API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Feedback Collection API...")
    if feedback_system:
        await feedback_system.cleanup_old_feedback()


async def _setup_mock_services():
    """Setup mock services for demo"""
    from unittest.mock import AsyncMock, Mock

    from core.interfaces.dependency_injection import register_service

    # Mock natural language interface
    mock_nl = Mock()
    mock_nl._analyze_emotion = AsyncMock(return_value={"positive": 0.7, "negative": 0.3})

    # Mock audit service
    mock_audit = Mock()
    mock_audit.log_event = AsyncMock()

    register_service("nl_consciousness_interface", mock_nl)
    register_service("audit_service", mock_audit)


# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "LUKHAS Feedback Collection API",
        "version": "1.0.0",
        "description": "Multi-modal feedback collection with compliance support",
        "endpoints": {
            "submit": "/feedback/submit",
            "quick": "/feedback/quick",
            "emoji": "/feedback/emoji",
            "text": "/feedback/text",
            "history": "/feedback/history",
            "summary": "/feedback/summary",
            "consent": "/consent",
        },
    }


@app.post("/feedback/submit", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(request: FeedbackRequest):
    """
    Submit comprehensive feedback.

    Supports all feedback types with full context and compliance options.
    """
    try:
        if not feedback_system or not feedback_system.operational:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        feedback_id = await feedback_system.collect_feedback(
            user_id=request.user_id,
            session_id=request.session_id,
            action_id=request.action_id,
            feedback_type=request.feedback_type,
            content=request.content,
            context=request.context,
            region=request.region,
        )

        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message="Feedback collected successfully",
        )

    except Exception as e:
        logger.error(f"Error collecting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback/quick", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_quick_feedback(request: QuickFeedbackRequest):
    """
    Submit quick thumbs up/down feedback.

    Simplified endpoint for binary feedback.
    """
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        # Convert to standard feedback
        rating = 5 if request.thumbs_up else 1
        session_id = request.session_id or f"quick_{uuid.uuid4().hex[:8]}"

        feedback_id = await feedback_system.collect_feedback(
            user_id=request.user_id,
            session_id=session_id,
            action_id=request.action_id,
            feedback_type=FeedbackType.QUICK,
            content={"rating": rating, "thumbs_up": request.thumbs_up},
            context={"quick_feedback": True},
        )

        return FeedbackResponse(success=True, feedback_id=feedback_id, message="Quick feedback recorded")

    except Exception as e:
        logger.error(f"Error with quick feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback/emoji", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_emoji_feedback(request: EmojiFeedbackRequest):
    """
    Submit emoji reaction feedback.

    Express emotions through standardized emoji set.
    """
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        feedback_id = await feedback_system.collect_feedback(
            user_id=request.user_id,
            session_id=request.session_id,
            action_id=request.action_id,
            feedback_type=FeedbackType.EMOJI,
            content={"emoji": request.emoji},
            context=request.context or {"emoji_feedback": True},
        )

        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message=f"Emoji feedback {request.emoji} recorded",
        )

    except Exception as e:
        logger.error(f"Error with emoji feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback/text", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_text_feedback(request: TextFeedbackRequest):
    """
    Submit natural language feedback.

    Provide detailed feedback in your own words.
    """
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        feedback_id = await feedback_system.collect_feedback(
            user_id=request.user_id,
            session_id=request.session_id,
            action_id=request.action_id,
            feedback_type=FeedbackType.TEXT,
            content={"text": request.text},
            context=request.context or {"text_feedback": True},
        )

        return FeedbackResponse(success=True, feedback_id=feedback_id, message="Text feedback recorded")

    except Exception as e:
        logger.error(f"Error with text feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/feedback/edit", response_model=FeedbackResponse, tags=["Feedback"])
async def edit_feedback(request: FeedbackEditRequest):
    """Edit existing feedback."""
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        success = await feedback_system.edit_feedback(
            feedback_id=request.feedback_id,
            user_id=request.user_id,
            new_content=request.new_content,
        )

        return FeedbackResponse(
            success=success,
            feedback_id=request.feedback_id,
            message=("Feedback updated successfully" if success else "Failed to update feedback"),
        )

    except Exception as e:
        logger.error(f"Error editing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/feedback/{feedback_id}", response_model=FeedbackResponse, tags=["Feedback"])
async def delete_feedback(feedback_id: str, user_id: str = Query(..., description="User ID for verification")):
    """Delete feedback (soft delete for audit trail)."""
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        success = await feedback_system.delete_feedback(feedback_id=feedback_id, user_id=user_id)

        return FeedbackResponse(
            success=success,
            feedback_id=feedback_id,
            message="Feedback deleted" if success else "Failed to delete feedback",
        )

    except Exception as e:
        logger.error(f"Error deleting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/feedback/history/{user_id}",
    response_model=FeedbackHistoryResponse,
    tags=["Feedback"],
)
async def get_feedback_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
):
    """Get user's feedback history."""
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        history = await feedback_system.get_user_feedback_history(user_id, limit)

        return FeedbackHistoryResponse(
            user_id=user_id,
            feedback_items=[item.to_audit_entry() for item in history],
            total_count=len(history),
        )

    except Exception as e:
        logger.error(f"Error getting feedback history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/feedback/summary/{action_id}",
    response_model=FeedbackSummaryResponse,
    tags=["Feedback"],
)
async def get_feedback_summary(action_id: str):
    """Get aggregated feedback summary for an action."""
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        summary = await feedback_system.get_action_feedback(action_id)

        return FeedbackSummaryResponse(
            action_id=action_id,
            total_feedback=summary.total_feedback,
            average_rating=summary.average_rating,
            sentiment_distribution=summary.sentiment_distribution,
            emoji_distribution=summary.emoji_distribution,
            common_themes=summary.common_themes,
            improvement_suggestions=summary.improvement_suggestions,
        )

    except Exception as e:
        logger.error(f"Error getting feedback summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consent", tags=["Compliance"])
async def update_consent(request: ConsentRequest):
    """Update user consent preferences."""
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        # Update user profile with consent
        from feedback.user_feedback_system import UserFeedbackProfile

        profile = UserFeedbackProfile(
            user_id=request.user_id,
            preferred_feedback_types=set(),
            feedback_frequency="sometimes",
            total_feedback_given=0,
            consent_given=request.consent_given,
            consent_timestamp=(datetime.now(timezone.utc) if request.consent_given else None),
            data_retention_days=request.data_retention_days
            or feedback_system.compliance_rules[request.region]["data_retention_days"],
            allow_anonymized_usage=request.allow_anonymized_usage,
        )

        feedback_system.user_profiles[request.user_id] = profile

        return {
            "success": True,
            "message": "Consent preferences updated",
            "user_id": request.user_id,
            "consent_given": request.consent_given,
        }

    except Exception as e:
        logger.error(f"Error updating consent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feedback/export/{user_id}", tags=["Compliance"])
async def export_user_data(user_id: str):
    """Export all user feedback data (GDPR compliance)."""
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        user_data = await feedback_system.export_user_data(user_id)

        return user_data

    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feedback/report", tags=["Analytics"])
async def generate_feedback_report(
    start_date: datetime = Query(..., description="Report start date"),
    end_date: datetime = Query(..., description="Report end date"),
    anonymize: bool = Query(True, description="Anonymize user data"),
):
    """Generate feedback analytics report."""
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        report = await feedback_system.generate_feedback_report(
            start_date=start_date, end_date=end_date, anonymize=anonymize
        )

        return report

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", tags=["System"])
async def get_status():
    """Get feedback system status."""
    if not feedback_system:
        return {"operational": False, "message": "System not initialized"}

    status = await feedback_system.get_status()
    return status


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": ("healthy" if feedback_system and feedback_system.operational else "unhealthy"),
        "timestamp": datetime.now(timezone.utc),
    }


# Widget endpoints for UI integration
@app.get("/widget/rating", tags=["Widgets"])
async def get_rating_widget():
    """Get rating widget HTML."""
    from feedback.user_feedback_system import FeedbackWidget

    if not feedback_system:
        raise HTTPException(status_code=503, detail="Feedback system not available")

    widget = FeedbackWidget(feedback_system)
    return {"html": widget.render_rating_widget()}


@app.get("/widget/emoji", tags=["Widgets"])
async def get_emoji_widget():
    """Get emoji grid widget HTML."""
    from feedback.user_feedback_system import FeedbackWidget

    if not feedback_system:
        raise HTTPException(status_code=503, detail="Feedback system not available")

    widget = FeedbackWidget(feedback_system)
    return {"html": widget.render_emoji_grid()}


@app.get("/widget/quick", tags=["Widgets"])
async def get_quick_widget():
    """Get quick feedback widget HTML."""
    from feedback.user_feedback_system import FeedbackWidget

    if not feedback_system:
        raise HTTPException(status_code=503, detail="Feedback system not available")

    widget = FeedbackWidget(feedback_system)
    return {"html": widget.render_quick_feedback()}


if __name__ == "__main__":
    import uvicorn

    # Run the API
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Different port from consciousness API
        log_level="info",
    )
