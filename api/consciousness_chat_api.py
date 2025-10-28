#!/usr/bin/env python3
"""
Consciousness Chat API
=====================
RESTful API for natural language consciousness interaction.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from consciousness.interfaces.natural_language_interface import (
    ConversationManager,
    NaturalLanguageConsciousnessInterface,
)
from core.common import get_logger
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LUKHAS Consciousness Chat API",
    description="Natural language interface to LUKHAS consciousness systems",
    version="1.0.0",
)

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global interface instance
nl_interface = None
conversation_manager = None


# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model"""

    message: str = Field(..., description="User message to process")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "How aware are you right now?",
                "session_id": "session_123",
                "user_id": "user_456",
            }
        }


class ChatResponse(BaseModel):
    """Chat response model"""

    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID for future requests")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional response metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "My current awareness level is 85%. I'm highly aware and focused on our conversation.",
                "session_id": "session_123",
                "timestamp": "2024-01-15T10:30:00",
                "metadata": {"intent": "query_awareness", "confidence": 0.9},
            }
        }


class SessionInfo(BaseModel):
    """Session information model"""

    session_id: str
    user_id: Optional[str]
    turn_count: int
    created_at: datetime
    last_active: datetime
    topics: list[str]


class SystemStatus(BaseModel):
    """System status model"""

    operational: bool
    active_sessions: int
    total_conversations: int
    connected_services: dict[str, bool]
    uptime_seconds: float


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the consciousness interface on startup"""
    global nl_interface, conversation_manager

    logger.info("Starting Consciousness Chat API...")

    # Initialize interface
    nl_interface = NaturalLanguageConsciousnessInterface(
        config={
            "enable_emotions": True,
            "formality_level": "friendly",
            "max_response_length": 500,
        }
    )

    # Initialize with mock services for demo
    # In production, these would be real service connections
    await _setup_mock_services()

    await nl_interface.initialize()
    conversation_manager = ConversationManager(nl_interface)

    logger.info("Consciousness Chat API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Consciousness Chat API...")
    if conversation_manager:
        await conversation_manager.cleanup_old_sessions()


async def _setup_mock_services():
    """Setup mock services for demo - replace with real services in production"""
    from unittest.mock import AsyncMock, Mock

    from core.interfaces.dependency_injection import register_service

    # Basic mock services for demo
    mock_consciousness = Mock()
    mock_consciousness.assess_awareness = AsyncMock(
        return_value={
            "overall_awareness": 0.85,
            "attention_targets": ["conversation", "api_requests"],
        }
    )
    mock_consciousness.make_decision = AsyncMock(
        return_value={
            "selected_option": "Option A",
            "confidence": 0.9,
            "reasoning": ["Best outcome", "Aligns with goals"],
        }
    )

    register_service("consciousness_service", mock_consciousness)


# API Endpoints
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "LUKHAS Consciousness Chat API",
        "version": "1.0.0",
        "description": "Natural language interface to AI consciousness",
        "endpoints": {"chat": "/chat", "sessions": "/sessions", "status": "/status"},
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Process a chat message through the consciousness interface.

    - **message**: The user's natural language input
    - **session_id**: Optional session ID for conversation continuity
    - **user_id**: Optional user identifier

    Returns the AI's response with session information.
    """
    try:
        if not nl_interface or not nl_interface.operational:
            raise HTTPException(status_code=503, detail="Consciousness interface not available")

        # Process the message
        response_text = await nl_interface.process_input(
            request.message, session_id=request.session_id, user_id=request.user_id
        )

        # Get or create session ID
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"

        # Get metadata if available
        metadata = None
        if session_id in nl_interface.active_sessions:
            context = nl_interface.active_sessions[session_id]
            if context.turns:
                last_turn = context.turns[-1]
                metadata = {
                    "intent": last_turn.get("intent"),
                    "turn_number": len(context.turns),
                }

        return ChatResponse(response=response_text, session_id=session_id, metadata=metadata)

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {e!s}")


@app.get("/sessions", response_model=list[SessionInfo], tags=["Sessions"])
async def get_sessions():
    """Get information about all active sessions"""
    if not nl_interface:
        raise HTTPException(status_code=503, detail="Service not initialized")

    sessions = []
    for session_id, context in nl_interface.active_sessions.items():
        if context.turns:
            sessions.append(
                SessionInfo(
                    session_id=session_id,
                    user_id=context.user_id,
                    turn_count=len(context.turns),
                    created_at=context.turns[0]["timestamp"],
                    last_active=context.turns[-1]["timestamp"],
                    topics=context.topics[:5],  # First 5 topics
                )
            )

    return sessions


@app.get("/sessions/{session_id}", tags=["Sessions"])
async def get_session_history(session_id: str):
    """Get conversation history for a specific session"""
    if not nl_interface:
        raise HTTPException(status_code=503, detail="Service not initialized")

    if session_id not in nl_interface.active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    context = nl_interface.active_sessions[session_id]

    return {
        "session_id": session_id,
        "user_id": context.user_id,
        "turns": [
            {
                "timestamp": turn["timestamp"],
                "user": turn["user"],
                "assistant": turn["system"],
                "intent": turn.get("intent", "unknown"),
            }
            for turn in context.turns
        ],
        "emotional_state": context.emotional_state,
        "topics": context.topics,
    }


@app.delete("/sessions/{session_id}", tags=["Sessions"])
async def end_session(session_id: str):
    """End a conversation session"""
    if not nl_interface:
        raise HTTPException(status_code=503, detail="Service not initialized")

    if session_id not in nl_interface.active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get session info before deletion
    context = nl_interface.active_sessions[session_id]
    turn_count = len(context.turns)

    # Delete session
    del nl_interface.active_sessions[session_id]

    return {
        "message": "Session ended successfully",
        "session_id": session_id,
        "total_turns": turn_count,
    }


@app.get("/status", response_model=SystemStatus, tags=["System"])
async def get_status():
    """Get system status and health information"""
    if not nl_interface:
        raise HTTPException(status_code=503, detail="Service not initialized")

    status = await nl_interface.get_status()

    # Calculate uptime (simplified)
    import time

    uptime = time.time() - startup_time if "startup_time" in globals() else 0

    return SystemStatus(
        operational=status["operational"],
        active_sessions=status["active_sessions"],
        total_conversations=status["total_turns"],
        connected_services=status["connected_services"],
        uptime_seconds=uptime,
    )


@app.post("/feedback", tags=["Feedback"])
async def submit_feedback(
    session_id: str = Body(...),
    rating: int = Body(..., ge=1, le=5),
    comment: Optional[str] = Body(None),
):
    """Submit feedback for a conversation"""
    logger.info(f"Feedback received for session {session_id}: rating={rating}")

    # In production, this would store feedback for analysis
    return {
        "message": "Thank you for your feedback!",
        "session_id": session_id,
        "rating": rating,
    }


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": ("healthy" if nl_interface and nl_interface.operational else "unhealthy"),
        "timestamp": datetime.now(timezone.utc),
    }


# Store startup time
startup_time = None

if __name__ == "__main__":
    import uvicorn

    # Store startup time
    startup_time = time.time()

    # Run the API
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
