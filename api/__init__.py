"""
LUKHAS AI API Module
===================
Comprehensive API layer for LUKHAS consciousness, feedback, and universal language systems.

This module provides RESTful API endpoints for:
- Consciousness Chat API: Natural language consciousness interaction
- Integrated Consciousness API: Unified consciousness and feedback systems
- Universal Language API: Multimodal communication interfaces
- Feedback API: User feedback collection and processing

Constellation Framework Integration: ⚛️🧠🛡️
- ⚛️ Identity: Authenticated API access with ΛID integration
- 🧠 Consciousness: Direct consciousness system interfaces
- 🛡️ Guardian: API security and compliance monitoring
"""

import logging
from typing import Dict, List, Optional, Union  # API expansion types

# Import core API applications
try:
    from .consciousness_chat_api import app as consciousness_chat_app

    CONSCIOUSNESS_CHAT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Consciousness Chat API not available: {e}")
    consciousness_chat_app = None
    CONSCIOUSNESS_CHAT_AVAILABLE = False

try:
    from .integrated_consciousness_api import app as integrated_consciousness_app

    INTEGRATED_CONSCIOUSNESS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Integrated Consciousness API not available: {e}")
    integrated_consciousness_app = None
    INTEGRATED_CONSCIOUSNESS_AVAILABLE = False

try:
    from .universal_language_api import app as universal_language_app

    UNIVERSAL_LANGUAGE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Universal Language API not available: {e}")
    universal_language_app = None
    UNIVERSAL_LANGUAGE_AVAILABLE = False

try:
    from .feedback_api import app as feedback_app

    FEEDBACK_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Feedback API not available: {e}")
    feedback_app = None
    FEEDBACK_AVAILABLE = False

try:
    from .expansion_api import app as expansion_app
    EXPANSION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"API Expansion not available: {e}")
    expansion_app = None
    EXPANSION_AVAILABLE = False

# API Registry
API_REGISTRY = {
    "consciousness_chat": {
        "app": consciousness_chat_app,
        "available": CONSCIOUSNESS_CHAT_AVAILABLE,
        "description": "Natural language consciousness interaction",
    },
    "integrated_consciousness": {
        "app": integrated_consciousness_app,
        "available": INTEGRATED_CONSCIOUSNESS_AVAILABLE,
        "description": "Unified consciousness and feedback systems",
    },
    "universal_language": {
        "app": universal_language_app,
        "available": UNIVERSAL_LANGUAGE_AVAILABLE,
        "description": "Multimodal communication interfaces",
    },
    "feedback": {
        "app": feedback_app,
        "available": FEEDBACK_AVAILABLE,
        "description": "User feedback collection and processing",
    },
    "expansion": {
        "app": expansion_app,
        "available": EXPANSION_AVAILABLE,
        "description": "API expansion strategy for Consciousness, Identity, and Guardian systems",
    }
}


def get_available_apis() -> Dict[str, Dict[str, Union[bool, str, Optional[object]]]]:
    """Get list of available API applications."""
    return {name: info for name, info in API_REGISTRY.items() if info["available"]}


def get_api_app(api_name: str) -> Optional[object]:
    """Get specific API application by name."""
    if api_name in API_REGISTRY and API_REGISTRY[api_name]["available"]:
        return API_REGISTRY[api_name]["app"]
    return None


def get_api_status() -> Dict[str, Union[str, int, float, Dict[str, Dict[str, Union[bool, str, Optional[object]]]]]]:
    """Get comprehensive API module status."""
    available_count = sum(1 for api in API_REGISTRY.values() if api["available"])
    total_count = len(API_REGISTRY)

    return {
        "module": "LUKHAS API",
        "total_apis": total_count,
        "available_apis": available_count,
        "availability_rate": f"{(available_count/total_count)*100:.1f}%",
        "triad_compliance": "⚛️🧠🛡️",
        "apis": API_REGISTRY,
    }


# Export main components
__all__ = [
    "consciousness_chat_app",
    "integrated_consciousness_app",
    "universal_language_app",
    "feedback_app",
    "API_REGISTRY",
    "get_available_apis",
    "get_api_app",
    "get_api_status",
]
