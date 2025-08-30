import time
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends
from interfaces.api.v1.common.errors import ProcessingError, ValidationError
from interfaces.api.v1.rest.models import ProcessRequest, ProcessResponse, SymbolicState

router = APIRouter()


def get_lukhas_core():
    return lukhas_core


async def record_metrics(request_id: str, duration: float) -> None:
    """Record processing metrics."""
    # TODO: implement metrics recording


@router.post("/", response_model=ProcessResponse)
async def process_request(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    core=Depends(get_lukhas_core),
) -> ProcessResponse:
    """Process input through LUKHAS AGI system."""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        if len(request.input_text) > 10000:
            raise ValidationError("Input text too long", "input_text")

        result = await core.process_unified_request(request.input_text, request.context)

        symbolic_state = None
        if isinstance(result, dict) and "symbolic" in result:
            symbolic_state = SymbolicState(
                glyphs=result["symbolic"].get("glyphs", []),
                resonance=result["symbolic"].get("resonance", 0.0),
                drift_score=result["symbolic"].get("drift_score", 0.0),
                entropy=result["symbolic"].get("entropy", 0.0),
            )

        background_tasks.add_task(record_metrics, request_id, time.time() - start_time)

        return ProcessResponse(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            result=result,
            symbolic_state=symbolic_state,
            metadata={"mode": request.mode.value, "version": "1.0.0"},
            processing_time_ms=(time.time() - start_time) * 1000,
        )
    except Exception as e:
        raise ProcessingError(f"Processing failed: {e!s}")
