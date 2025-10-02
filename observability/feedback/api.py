"""
FastAPI endpoints for adaptive feedback collection and follow-ups.
"""
from __future__ import annotations
from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel
from ..audit.storage import write_json

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackIn(BaseModel):
    """User feedback input model."""
    trace_id: str
    rating_0_10: int
    text: str = ""
    labels: Dict[str, float] = {}


class FollowupIn(BaseModel):
    """Follow-up answers input model."""
    feedback_id: str
    answers: Dict[str, str]


@router.post("/", status_code=202)
async def submit_feedback(fb: FeedbackIn) -> Dict[str, Any]:
    """
    Submit user feedback for a trace.

    Args:
        fb: Feedback input with rating and text

    Returns:
        Confirmation with feedback_id

    Example:
        POST /feedback/
        {
          "trace_id": "abc123",
          "rating_0_10": 7,
          "text": "Good answer but missed an edge case",
          "labels": {"edge-case": 1.0}
        }
    """
    feedback_id = f"fb:{fb.trace_id}"
    payload = {
        "id": feedback_id,
        "feedback_id": feedback_id,
        **fb.model_dump()
    }

    # TODO: Add taxonomy classification, sentiment analysis, severity scoring
    # TODO: Enqueue adaptive follow-ups based on rating/labels

    await write_json("feedback_event", payload)
    return {"ok": True, "feedback_id": feedback_id}


@router.post("/followup", status_code=202)
async def submit_followup(ff: FollowupIn) -> Dict[str, Any]:
    """
    Submit follow-up answers to feedback.

    Args:
        ff: Follow-up answers

    Returns:
        Confirmation

    Example:
        POST /feedback/followup
        {
          "feedback_id": "fb:abc123",
          "answers": {
            "clarification": "The edge case is...",
            "severity": "low"
          }
        }
    """
    payload = {
        "id": ff.feedback_id,
        **ff.model_dump()
    }

    # TODO: Merge into existing feedback_event payload
    # TODO: Update severity/priority based on followup

    await write_json("feedback_event", payload)
    return {"ok": True}


@router.get("/card/{trace_id}")
async def get_feedback_card(trace_id: str) -> Dict[str, Any]:
    """
    Get adaptive feedback card configuration for a trace.

    Args:
        trace_id: Trace identifier

    Returns:
        Feedback card specification

    Example:
        GET /feedback/card/abc123
        → {
            "trace_id": "abc123",
            "questions": [
              {"id": "rating", "type": "scale", "min": 0, "max": 10},
              {"id": "text", "type": "textarea", "placeholder": "What should improve?"}
            ]
          }
    """
    # TODO: Adaptive questions based on trace metadata
    # e.g., if confidence < 0.5, ask clarification questions
    # if latency > threshold, ask about performance

    return {
        "trace_id": trace_id,
        "questions": [
            {"id": "rating", "type": "scale", "label": "Quick rating", "min": 0, "max": 10},
            {"id": "text", "type": "textarea", "label": "What should improve?", "maxLength": 2000}
        ]
    }
