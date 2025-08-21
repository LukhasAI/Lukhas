"""
Lukhas Neural Intelligence API
File: neural_intelligence_api.py
Path: neural_intelligence/neural_intelligence_api.py
Created: 2025-01-13
Author: Lukhas AI Research Team
Version: 2.0

Professional REST API for the Lukhas Neural Intelligence System.
Preserves all unique Lukhas innovations while providing clean endpoints.
"""

import logging
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from neural_intelligence_main import LukhasNeuralIntelligence
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LukhasAPI")

# Initialize FastAPI app
app = FastAPI(
    title="Lukhas Neural Intelligence API",
    description="Professional API for Lukhas Neural Intelligence System with unique innovations",
    version="2.0.0",
)

# Initialize Lukhas system
lukhas_system = LukhasNeuralIntelligence(
    {"enable_dreams": True, "enable_healix": True, "api_mode": True}
)


class IntelligenceRequest(BaseModel):
    """Request model for intelligence processing"""

    query: str
    context: Optional[dict[str, Any]] = None
    enable_dreams: Optional[bool] = True
    enable_healix: Optional[bool] = True
    enable_flashback: Optional[bool] = True


class IntelligenceResponse(BaseModel):
    """Response model for intelligence processing"""

    response: str
    confidence: float
    capability_level: str
    metadata: dict[str, Any]
    lukhas_innovations: dict[str, Any]
    session_id: str


class SystemStatus(BaseModel):
    """System status model"""

    session_id: str
    uptime: str
    performance_metrics: dict[str, Any]
    lukhas_innovations: dict[str, Any]
    system_capabilities: dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "Lukhas Neural Intelligence API",
        "version": "2.0.0",
        "description": "Professional AI system with unique innovations",
        "innovations": [
            "Dreams",
            "Healix",
            "Flashback",
            "DriftScore",
            "CollapseHash",
        ],
        "status": "operational",
    }


@app.post("/intelligence", response_model=IntelligenceResponse)
async def process_intelligence_request(request: IntelligenceRequest):
    """Process an intelligence request using the full Lukhas system"""
    try:
        # Configure request with Lukhas innovations
        config = {
            "enable_dreams": request.enable_dreams,
            "enable_healix": request.enable_healix,
            "enable_flashback": request.enable_flashback,
        }

        # Update system config
        lukhas_system.config.update(config)

        # Process request
        response_data = await lukhas_system.process_request(
            request.query, request.context
        )

        # Get system status for session info
        status = lukhas_system.get_system_status()

        return IntelligenceResponse(
            response=response_data["response"],
            confidence=response_data["confidence"],
            capability_level=response_data["capability_level"],
            metadata=response_data["metadata"],
            lukhas_innovations=response_data["lukhas_innovations"],
            session_id=status["session_id"],
        )

    except Exception as e:
        logger.error(f"Intelligence processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get comprehensive system status"""
    try:
        status = lukhas_system.get_system_status()
        innovations = lukhas_system.get_innovations_status()

        return SystemStatus(
            session_id=status["session_id"],
            uptime=status["initialization_time"],
            performance_metrics=status["performance_metrics"],
            lukhas_innovations=innovations,
            system_capabilities=status["system_capabilities"],
        )

    except Exception as e:
        logger.error(f"Status retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")


@app.get("/innovations")
async def get_lukhas_innovations():
    """Get detailed information about unique Lukhas innovations"""
    try:
        return lukhas_system.get_innovations_status()
    except Exception as e:
        logger.error(f"Innovations status error: {e}")
        raise HTTPException(status_code=500, detail=f"Innovations error: {str(e)}")


@app.get("/capabilities")
async def get_system_capabilities():
    """Get detailed system capabilities information"""
    try:
        status = lukhas_system.get_system_status()
        return {
            "cognitive_capabilities": {
                "multi_modal_reasoning": True,
                "quantum_attention": True,
                "ethical_compliance": True,
                "continuous_learning": True,
                "metacognitive_awareness": True,
            },
            "lukhas_innovations": {
                "dreams": "Advanced sleep-state cognitive processing",
                "healix": "Golden ratio bio-mathematical optimization",
                "flashback": "Context-aware memory reconstruction",
                "drift_score": "Real-time cognitive performance tracking",
                "collapse_hash": "Quantum-inspired information compression",
            },
            "current_capability_level": status["capability_level"],
            "performance_metrics": status["performance_metrics"],
        }
    except Exception as e:
        logger.error(f"Capabilities error: {e}")
        raise HTTPException(status_code=500, detail=f"Capabilities error: {str(e)}")


@app.post("/dream-processing")
async def process_with_dreams(request: IntelligenceRequest):
    """Process request with emphasis on Dreams innovation"""
    try:
        # Force enable dreams
        request.enable_dreams = True
        request.enable_healix = False
        request.enable_flashback = False

        response_data = await lukhas_system.process_request(
            request.query, {**(request.context or {}), "emphasis": "dreams"}
        )

        return {
            "response": response_data["response"],
            "dreams_enhancement": response_data["metadata"].get(
                "dream_enhancement", {}
            ),
            "innovation_focus": "Dreams - Sleep-state cognitive processing",
        }

    except Exception as e:
        logger.error(f"Dreams processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Dreams error: {str(e)}")


@app.post("/healix-optimization")
async def process_with_healix(request: IntelligenceRequest):
    """Process request with emphasis on Healix innovation"""
    try:
        # Force enable healix
        request.enable_dreams = False
        request.enable_healix = True
        request.enable_flashback = False

        response_data = await lukhas_system.process_request(
            request.query, {**(request.context or {}), "emphasis": "healix"}
        )

        return {
            "response": response_data["response"],
            "healix_optimization": response_data["metadata"].get(
                "healix_optimization", {}
            ),
            "innovation_focus": "Healix - Golden ratio optimization",
        }

    except Exception as e:
        logger.error(f"Healix processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Healix error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
