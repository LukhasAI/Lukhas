"""

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony

Unified API Router - Connects all API endpoints
"""

import logging

from typing import Any

from fastapi import APIRouter, HTTPException

from core.common import get_logger
from memory import memory_manager

# Import LUKHAS AI branding system for API responses
try:
    from branding_bridge import (
        BrandContext,
        get_brand_voice,
        get_system_signature,
        normalize_output_text,  # noqa: F401  # TODO: branding_bridge.normali...
        validate_output,  # noqa: F401  # TODO: branding_bridge.validat...
    )

    BRANDING_AVAILABLE = True
except ImportError:

    try:
        # Add system signature to responses
        if "system" not in response_data:
            response_data["system"] = get_system_signature()

        # Apply branding to text content
        for key, value in response_data.items():
            if isinstance(value, str) and len(value) > 10:
                branded_value = get_brand_voice(value, api_brand_context)
                response_data[key] = branded_value

        return response_data
    except Exception as e:
        return response_data


    try:
        # Route to appropriate module based on request type
        request_type = data.get("type", "general")

        if request_type == "memory":


            return await memory_manager.process(data)
        elif request_type == "consciousness":
            from consciousness import consciousness_engine

            return await consciousness_engine.process(data)
        elif request_type == "emotion":
            from emotion import emotion_processor

            return await emotion_processor.process(data)
        else:
            response = {"result": "processed", "type": request_type}

        return apply_api_branding(response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



logger = logging.getLogger(__name__)

logger = get_logger(__name__)

# Create main router
router = APIRouter(prefix="/api/v1")

# Initialize branding context for API responses
if BRANDING_AVAILABLE:
    api_brand_context = BrandContext(
        voice_profile="identity",
        constellation_emphasis="balanced",
        compliance_level="standard",
        creative_mode=False,
        terminology_enforcement=True,
    )
else:
    api_brand_context = None


def apply_api_branding(response_data: dict[str, Any]) -> dict[str, Any]:
    """Apply LUKHAS AI branding to API responses"""
    if not BRANDING_AVAILABLE or not api_brand_context:
        return response_data

# Health check


@router.get("/health")
async def health_check():
    """System health check"""
    response = {"status": "healthy", "module": "LUKHAS AI"}
    return apply_api_branding(response)


# Core endpoints


@router.post("/process")
async def process_request(data: dict[str, Any]):
    """Process a request through LUKHAS"""
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
        "bridge": "active",
    }

    if module in modules:
        response = {"module": module, "status": modules[module]}
        return apply_api_branding(response)
    else:
        raise HTTPException(status_code=404, detail="Module not found")
