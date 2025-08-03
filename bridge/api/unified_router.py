"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


Unified API Router - Connects all API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Create main router
router = APIRouter(prefix="/api/v1")

# Health check
@router.get("/health")
async def health_check():
    """System health check"""
    return {"status": "healthy", "module": "lukhas"}

# Core endpoints
@router.post("/process")
async def process_request(data: Dict[str, Any]):
    """Process a request through LUKHAS"""
    try:
        # Route to appropriate module based on request type
        request_type = data.get("type", "general")
        
        if request_type == "memory":
            from memory import memory_manager
            return await memory_manager.process(data)
        elif request_type == "consciousness":
            from consciousness import consciousness_engine
            return await consciousness_engine.process(data)
        elif request_type == "emotion":
            from emotion import emotion_processor
            return await emotion_processor.process(data)
        else:
            return {"result": "processed", "type": request_type}
            
    except Exception as e:
        logger.error(f"API processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Module status
@router.get("/status/{module}")
async def module_status(module: str):
    """Get status of a specific module"""
    modules = {
        "core": "active",
        "consciousness": "active", 
        "memory": "active",
        "qim": "active",
        "emotion": "active",
        "governance": "active",
        "bridge": "active"
    }
    
    if module in modules:
        return {"module": module, "status": modules[module]}
    else:
        raise HTTPException(status_code=404, detail="Module not found")
