from orchestration_src.brain.trace_memoria_logger import (
    TraceMemoriaLogger as MemoriaLogger,
)

logger = MemoriaLogger()
logger.log_trace(
    level=0,
    message="Lukhas generated a dream about attending AI Ethics Forum.",
    metadata={
        "user_id": "Lukhas_ID#2025-0001-XA9",
        "type": "dream_fragment",
        "emotion_score": 0.87,
        "category": "dream",
    },
)
