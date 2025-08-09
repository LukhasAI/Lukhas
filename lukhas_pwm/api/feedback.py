from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from lukhas_pwm.feedback.store import record_feedback, get_lut

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackCard(BaseModel):
    target_action_id: str = Field(..., max_length=128)
    rating: int = Field(..., ge=1, le=5)
    note: Optional[str] = Field(default=None, max_length=1000)
    user_id: Optional[str] = Field(default="anon", max_length=64)
    context_hash: Optional[str] = Field(default="", max_length=128)


@router.post("/card")
def post_feedback_card(card: FeedbackCard):
    try:
        lut = record_feedback(card.model_dump())
        return {"status": "ok", "lut": lut}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/lut")
def get_feedback_lut():
    return JSONResponse(content=get_lut())
