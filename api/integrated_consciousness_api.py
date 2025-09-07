#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)
"""
Integrated Consciousness & Feedback API
======================================
Unified API combining natural language consciousness interaction
with real-time feedback collection.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.common import get_logger
from dashboard.interpretability_dashboard import (
    UnifiedInterpretabilityDashboard,
)
from feedback.user_feedback_system import (
    ComplianceRegion,
    FeedbackType,
    UserFeedbackSystem,
)
from lukhas.consciousness.interfaces.natural_language_interface import (
    ConversationManager,
    NaturalLanguageConsciousnessInterface,
)

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LUKHAS Integrated Consciousness API",
    description="Natural language AI consciousness with real-time feedback and interpretability",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
nl_interface = None
feedback_system = None
dashboard = None
conversation_manager = None


# Request/Response models
class IntegratedChatRequest(BaseModel):
    """Integrated chat request with feedback options"""

    message: str = Field(..., description="User message to process")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User identifier")
    enable_feedback: bool = Field(True, description="Enable feedback collection for this interaction")
    region: Optional[ComplianceRegion] = Field(ComplianceRegion.GLOBAL, description="User's regulatory region")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "How can you help me make a decision?",
                "session_id": "session_123",
                "user_id": "user_456",
                "enable_feedback": True,
                "region": "eu",
            }
        }


class IntegratedChatResponse(BaseModel):
    """Enhanced response with feedback options"""

    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    action_id: str = Field(..., description="Action ID for feedback")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[dict[str, Any]] = Field(None, description="Response metadata")
    feedback_enabled: bool = Field(True, description="Whether feedback is enabled")
    decision_trace: Optional[dict[str, Any]] = Field(None, description="Decision explanation")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "I can help you make decisions by analyzing options...",
                "session_id": "session_123",
                "action_id": "action_789",
                "timestamp": "2024-01-15T10:30:00",
                "metadata": {"intent": "make_decision", "confidence": 0.9},
                "feedback_enabled": True,
                "decision_trace": {
                    "reasoning_steps": [
                        "Analyzed request",
                        "Identified decision context",
                    ],
                    "confidence": 0.9,
                },
            }
        }


class ConversationFeedback(BaseModel):
    """Feedback for a conversation turn"""

    action_id: str = Field(..., description="Action ID from chat response")
    user_id: str = Field(..., description="User identifier")
    feedback_type: str = Field(..., description="Type: rating, emoji, text, quick")
    content: dict[str, Any] = Field(..., description="Feedback content")

    class Config:
        json_schema_extra = {
            "example": {
                "action_id": "action_789",
                "user_id": "user_456",
                "feedback_type": "rating",
                "content": {"rating": 5},
            }
        }


class DashboardRequest(BaseModel):
    """Dashboard data request"""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    time_range: Optional[str] = Field("1h", description="Time range: 1h, 24h, 7d, 30d")
    include_feedback: bool = True
    include_decisions: bool = True


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize all systems on startup"""
    global nl_interface, feedback_system, dashboard, conversation_manager

    logger.info("Starting Integrated Consciousness API...")

    # Initialize natural language interface
    nl_interface = NaturalLanguageConsciousnessInterface(
        config={
            "enable_emotions": True,
            "formality_level": "friendly",
            "max_response_length": 500,
        }
    )

    # Initialize feedback system
    feedback_system = UserFeedbackSystem(
        config={"enable_emoji": True, "min_feedback_interval": 5}  # 5 seconds for demo
    )

    # Initialize dashboard
    dashboard = UnifiedInterpretabilityDashboard(config={"enable_realtime": True, "max_history": 1000})

    # Setup services
    await _setup_services()

    # Initialize all systems
    await nl_interface.initialize()
    await feedback_system.initialize()
    await dashboard.initialize()

    # Create conversation manager
    conversation_manager = ConversationManager(nl_interface)

    logger.info("Integrated Consciousness API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Integrated Consciousness API...")
    if conversation_manager:
        await conversation_manager.cleanup_old_sessions()
    if feedback_system:
        await feedback_system.cleanup_old_feedback()


async def _setup_services():
    """Setup services and integrations"""
    from unittest.mock import AsyncMock, Mock

    from core.interfaces.dependency_injection import register_service

    # Enhanced mock consciousness service
    mock_consciousness = Mock()

    async def assess_awareness(context):
        return {
            "overall_awareness": 0.85,
            "attention_targets": [
                "user_query",
                "decision_support",
                "feedback_integration",
            ],
            "self_awareness": 0.9,
            "environmental_awareness": 0.8,
        }

    async def make_decision(scenario):
        options = scenario.get("options", ["Option A", "Option B"])

        # Simulate decision with reasoning
        decision_result = {
            "selected_option": options[0],
            "confidence": 0.87,
            "reasoning": [
                "Analyzed user preferences from feedback history",
                "Evaluated potential outcomes",
                "Considered ethical implications",
                "Aligned with user's stated goals",
            ],
            "alternatives_considered": options[1:],
            "feedback_influence": {
                "historical_feedback_used": True,
                "relevant_feedback_count": 3,
                "feedback_weight": 0.3,
            },
        }

        return decision_result

    mock_consciousness.assess_awareness = AsyncMock(side_effect=assess_awareness)
    mock_consciousness.make_decision = AsyncMock(side_effect=make_decision)

    # Mock memory service
    mock_memory = Mock()
    mock_memory.search = AsyncMock(
        return_value=[
            {"id": "mem1", "summary": "User prefers detailed explanations"},
            {"id": "mem2", "summary": "User values transparency in decision-making"},
        ]
    )

    # Mock emotion service
    mock_emotion = Mock()
    mock_emotion.analyze_text = AsyncMock(return_value={"emotions": {"joy": 0.5, "trust": 0.7, "anticipation": 0.6})

    # Mock audit service
    mock_audit = Mock()
    mock_audit.log_event = AsyncMock()

    # Register all services
    register_service("consciousness_service", mock_consciousness)
    register_service("memory_service", mock_memory)
    register_service("emotion_service", mock_emotion)
    register_service("audit_service", mock_audit)
    register_service("nl_consciousness_interface", nl_interface)
    register_service("user_feedback_system", feedback_system)
    register_service("interpretability_dashboard", dashboard)


# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "LUKHAS Integrated Consciousness API",
        "version": "2.0.0",
        "description": "AI consciousness with feedback and interpretability",
        "features": [
            "Natural language conversation",
            "Real-time feedback collection",
            "Decision interpretability",
            "Regulatory compliance",
            "Unified dashboard",
        ],
        "endpoints": {
            "chat": "/chat",
            "feedback": "/feedback",
            "dashboard": "/dashboard",
            "sessions": "/sessions",
            "export": "/export",
        },
    }


@app.post("/chat", response_model=IntegratedChatResponse, tags=["Conversation"])
async def integrated_chat(request: IntegratedChatRequest):
    """
    Process chat with integrated feedback and interpretability.

    This endpoint:
    1. Processes natural language input
    2. Tracks decisions for interpretability
    3. Enables feedback collection
    4. Provides decision explanations
    """
    try:
        if not nl_interface or not nl_interface.operational:
            raise HTTPException(status_code=503, detail="Consciousness interface not available")

        # Generate IDs
        session_id = request.session_id or f"session_{uuid.uuid4(}.hex[:8]}"
        action_id = f"action_{uuid.uuid4(}.hex[:12]}"
        decision_id = f"decision_{uuid.uuid4(}.hex[:12]}"

        # Process through NL interface
        response_text = await nl_interface.process_input(
            request.message, session_id=session_id, user_id=request.user_id
        )

        # Get conversation context for metadata
        metadata = {}
        decision_trace = None

        if session_id in nl_interface.active_sessions:
            context = nl_interface.active_sessions[session_id]
            if context.turns:
                last_turn = context.turns[-1]
                intent = last_turn.get("intent", "unknown")

                metadata = {
                    "intent": intent,
                    "turn_number": len(context.turns),
                    "topics": context.topics[:3],
                    "emotional_state": context.emotional_state,
                }

                # Track decision if applicable
                if intent in ["make_decision", "query_awareness", "reflect"]:
                    reasoning_steps = [
                        "Understood user query",
                        "Retrieved relevant context",
                        "Applied decision logic",
                        "Generated response",
                    ]

                    # Add feedback influence if available
                    if request.user_id and feedback_system:
                        try:
                            recent_feedback = await feedback_system.get_user_feedback_history(request.user_id, limit=5)
                            if recent_feedback:
                                reasoning_steps.append(f"Incorporated {len(recent_feedback)} recent feedback items")
                        except BaseException:
                            pass

                    # Track in dashboard
                    if dashboard:
                        await dashboard.track_decision(
                            decision_id=decision_id,
                            module="consciousness_chat",
                            decision_type=intent,
                            input_data={"message": request.message},
                            reasoning_steps=[{"step": s, "confidence": 0.8} for s in reasoning_steps],
                            output={"response": response_text},
                            confidence=0.85,
                        )

                    decision_trace = {
                        "decision_id": decision_id,
                        "reasoning_steps": reasoning_steps,
                        "confidence": 0.85,
                        "feedback_integrated": request.user_id is not None,
                    }

        # Store action context for feedback
        if request.enable_feedback and feedback_system:
            # Pre-register the action for feedback
            action_context = {
                "action_type": "chat_response",
                "session_id": session_id,
                "user_message": request.message,
                "ai_response": response_text,
                "intent": metadata.get("intent", "general_chat"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Store in dashboard for feedback integration
            if dashboard:
                dashboard.action_contexts[action_id] = action_context

        return IntegratedChatResponse(
            response=response_text,
            session_id=session_id,
            action_id=action_id,
            metadata=metadata,
            feedback_enabled=request.enable_feedback,
            decision_trace=decision_trace,
        )

    except Exception as e:
        logger.error(f"Error in integrated chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback", tags=["Feedback"])
async def submit_conversation_feedback(feedback: ConversationFeedback):
    """
    Submit feedback for a conversation turn.

    Integrates with dashboard to show how feedback influences future decisions.
    """
    try:
        if not feedback_system:
            raise HTTPException(status_code=503, detail="Feedback system not available")

        # Get action context from dashboard
        action_context = {}
        if dashboard and feedback.action_id in dashboard.action_contexts:
            action_context = dashboard.action_contexts[feedback.action_id]

        # Map feedback type
        feedback_type_map = {
            "rating": FeedbackType.RATING,
            "emoji": FeedbackType.EMOJI,
            "text": FeedbackType.TEXT,
            "quick": FeedbackType.QUICK,
        }

        feedback_type = feedback_type_map.get(feedback.feedback_type, FeedbackType.GENERAL)

        # Collect feedback
        feedback_id = await feedback_system.collect_feedback(
            user_id=feedback.user_id,
            session_id=action_context.get("session_id", "unknown"),
            action_id=feedback.action_id,
            feedback_type=feedback_type,
            content=feedback.content,
            context=action_context,
        )

        # Integrate with dashboard
        if dashboard:
            # Find related decision
            for decision_id, decision in dashboard.decisions.items():
                if decision.get("module") == "consciousness_chat" and decision.get(
                    "timestamp", datetime.min
                ) > datetime.now(timezone.utc).replace(tzinfo=None) - timezone.timedelta(minutes=5):
                    await dashboard.integrate_feedback(
                        decision_id=decision_id,
                        feedback_data={
                            "feedback_id": feedback_id,
                            "user_id": feedback.user_id,
                            "type": feedback.feedback_type,
                            "content": feedback.content,
                            "sentiment": feedback_system.feedback_items[feedback_id].processed_sentiment,
                        },
                    )
                    break

        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Feedback recorded and integrated",
            "impact": "Your feedback will influence future interactions",
        }

    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dashboard", tags=["Dashboard"])
async def get_dashboard_data(request: DashboardRequest):
    """
    Get unified dashboard data showing decisions and feedback.

    Shows how user feedback influences AI decisions over time.
    """
    try:
        if not dashboard:
            raise HTTPException(status_code=503, detail="Dashboard not available")

        # Calculate time range
        from datetime import timedelta

        time_ranges = {
            "1h": timedelta(hours=1),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
        }

        time_delta = time_ranges.get(request.time_range, timedelta(hours=1))
        start_time = datetime.now(timezone.utc) - time_delta

        dashboard_data = {
            "time_range": request.time_range,
            "modules": {},
            "decisions": [],
            "feedback_summary": {},
            "system_health": await dashboard.get_status(),
        }

        # Get module statuses
        module_statuses = await dashboard.get_module_statuses()
        dashboard_data["modules"] = module_statuses

        # Get recent decisions
        if request.include_decisions:
            for decision_id, decision in dashboard.decisions.items():
                if decision.get("timestamp", datetime.min) > start_time.replace(tzinfo=None):
                    # Add feedback influence info
                    if "feedback_references" in decision:
                        decision["feedback_influence"] = {
                            "count": len(decision["feedback_references"]),
                            "impact": ("high" if len(decision["feedback_references"]) > 2 else "moderate"),
                        }

                    dashboard_data["decisions"].append(
                        {
                            "id": decision_id,
                            "type": decision.get("decision_type"),
                            "confidence": decision.get("confidence"),
                            "timestamp": decision.get("timestamp"),
                            "feedback_influence": decision.get("feedback_influence", {}),
                        }
                    )

        # Get feedback summary
        if request.include_feedback and feedback_system:
            if request.user_id:
                # User-specific feedback
                user_feedback = await feedback_system.get_user_feedback_history(request.user_id, limit=20)

                dashboard_data["feedback_summary"] = {
                    "total_feedback": len(user_feedback),
                    "recent_feedback": [
                        {
                            "timestamp": f.timestamp.isoformat(),
                            "type": f.feedback_type.value,
                            "sentiment": f.processed_sentiment,
                        }
                        for f in user_feedback[:5]
                    ],
                    "satisfaction_trend": _calculate_satisfaction_trend(user_feedback),
                }
            else:
                # Overall feedback metrics
                dashboard_data["feedback_summary"] = feedback_system.metrics

        # Add interpretability insights
        dashboard_data["insights"] = {
            "feedback_driven_decisions": sum(
                1 for d in dashboard_data["decisions"] if d.get("feedback_influence", {}).get("count", 0) > 0
            ),
            "average_confidence": sum(d.get("confidence", 0) for d in dashboard_data["decisions"])
            / max(len(dashboard_data["decisions"]), 1),
            "top_decision_types": _get_top_decision_types(dashboard_data["decisions"]),
        }

        return dashboard_data

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}/export", tags=["Export"])
async def export_session_with_feedback(session_id: str):
    """
    Export complete session data including conversations and feedback.

    Shows the full interaction history with feedback integration.
    """
    try:
        export_data = {
            "session_id": session_id,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "conversation": None,
            "feedback": [],
            "decisions": [],
            "insights": {},
        }

        # Get conversation history
        if nl_interface and session_id in nl_interface.active_sessions:
            context = nl_interface.active_sessions[session_id]
            export_data["conversation"] = {
                "user_id": context.user_id,
                "turns": context.turns,
                "topics": context.topics,
                "emotional_journey": context.emotional_state,
            }

        # Get related feedback
        if feedback_system:
            for feedback in feedback_system.feedback_items.values():
                if feedback.context.get("session_id") == session_id:
                    export_data["feedback"].append(feedback.to_audit_entry())

        # Get related decisions from dashboard
        if dashboard:
            for decision_id, decision in dashboard.decisions.items():
                if decision.get("input_data", {}).get("session_id") == session_id:
                    export_data["decisions"].append(
                        {
                            "id": decision_id,
                            "type": decision.get("decision_type"),
                            "reasoning": decision.get("reasoning_steps"),
                            "confidence": decision.get("confidence"),
                            "feedback_integrated": len(decision.get("feedback_references", [])) > 0,
                        }
                    )

        # Generate insights
        export_data["insights"] = {
            "total_interactions": (len(export_data["conversation"]["turns"]) if export_data["conversation"] else 0),
            "feedback_given": len(export_data["feedback"]),
            "decisions_made": len(export_data["decisions"]),
            "feedback_influence_rate": sum(1 for d in export_data["decisions"] if d["feedback_integrated"])
            / max(len(export_data["decisions"]), 1),
        }

        return export_data

    except Exception as e:
        logger.error(f"Error exporting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feedback/influence/{user_id}", tags=["Analytics"])
async def get_feedback_influence(user_id: str):
    """
    Show how a user's feedback has influenced AI decisions.

    Demonstrates the "LUKHAS made this decision because..." concept.
    """
    try:
        influence_data = {
            "user_id": user_id,
            "total_feedback_given": 0,
            "decisions_influenced": 0,
            "influence_examples": [],
            "impact_score": 0.0,
        }

        if not feedback_system or not dashboard:
            raise HTTPException(status_code=503, detail="Required services not available")

        # Get user's feedback history
        user_feedback = await feedback_system.get_user_feedback_history(user_id, limit=100)
        influence_data["total_feedback_given"] = len(user_feedback)

        # Find decisions influenced by this user's feedback
        for decision in dashboard.decisions.values():
            feedback_refs = decision.get("feedback_references", [])

            for ref in feedback_refs:
                if ref.get("user_id") == user_id:
                    influence_data["decisions_influenced"] += 1

                    # Create influence example
                    feedback_item = next(
                        (f for f in user_feedback if f.feedback_id == ref.get("feedback_id")),
                        None,
                    )

                    if feedback_item and len(influence_data["influence_examples"]) < 5:
                        influence_data["influence_examples"].append(
                            {
                                "decision_made": decision.get("output", {}).get("summary", "Decision made"),
                                "because": f"On {feedback_item.timestamp.strftime('%B %d at %H:%M')}, you {_describe_feedback(feedback_item)}",
                                "decision_type": decision.get("decision_type"),
                                "confidence_boost": 0.1,  # Simulated confidence boost from feedback
                            }
                        )

        # Calculate impact score
        if influence_data["total_feedback_given"] > 0:
            influence_data["impact_score"] = min(
                influence_data["decisions_influenced"] / influence_data["total_feedback_given"],
                1.0,
            )

        return influence_data

    except Exception as e:
        logger.error(f"Error calculating feedback influence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions
def _calculate_satisfaction_trend(feedback_items):
    """Calculate satisfaction trend from feedback history"""
    if not feedback_items:
        return "neutral"

    recent_scores = []
    for item in feedback_items[:10]:  # Last 10 items
        if item.processed_sentiment:
            positive = item.processed_sentiment.get("positive", 0)
            negative = item.processed_sentiment.get("negative", 0)
            score = positive - negative
            recent_scores.append(score)

    if not recent_scores:
        return "neutral"

    avg_score = sum(recent_scores) / len(recent_scores)

    if avg_score > 0.3:
        return "positive"
    elif avg_score < -0.3:
        return "negative"
    else:
        return "neutral"


def _get_top_decision_types(decisions):
    """Get most common decision types"""
    from collections import Counter

    types = [d.get("type", "unknown") for d in decisions]
    counter = Counter(types)

    return [{"type": dtype, "count": count} for dtype, count in counter.most_common(3)]


def _describe_feedback(feedback_item):
    """Generate human-readable description of feedback"""
    if feedback_item.feedback_type == FeedbackType.RATING:
        rating = feedback_item.content.get("rating", 0)
        return f"gave a {rating}-star rating"
    elif feedback_item.feedback_type == FeedbackType.EMOJI:
        emoji = feedback_item.content.get("emoji", "")
        return f"reacted with {emoji}"
    elif feedback_item.feedback_type == FeedbackType.TEXT:
        text_content = feedback_item.content.get("text", "")
        return f'said: "{text_content[:50]}..."' if len(text_content) > 50 else f'said: "{text_content}"'
    elif feedback_item.feedback_type == FeedbackType.QUICK:
        thumbs = "👍" if feedback_item.content.get("thumbs_up") else "👎"
        return f"gave a {thumbs}"
    else:
        return "provided feedback"


@app.get("/health", tags=["System"])
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "services": {
            "consciousness": nl_interface and nl_interface.operational,
            "feedback": feedback_system and feedback_system.operational,
            "dashboard": dashboard and dashboard.operational,
        },
    }

    # Overall status
    if not all(health_status["services"].values()):
        health_status["status"] = "degraded"

    return health_status


if __name__ == "__main__":
    import os

    import uvicorn

    # Configuration from environment variables with sensible defaults
    host = os.getenv("LUKHAS_API_HOST", "0.0.0.0")
    port = int(os.getenv("LUKHAS_API_PORT", "8080"))
    log_level = os.getenv("LUKHAS_LOG_LEVEL", "info").lower()

    logger.info(f"Starting LUKHAS Consciousness API on {host}:{port}")

    # Run the integrated API
    uvicorn.run(app, host=host, port=port, log_level=log_level)