"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - COGNITIVE MODULE
║ Initialization for cognitive subpackage.
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: __init__.py
║ Path: lukhas/[subdirectory]/__init__.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Consciousness Team | Jules
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Initialization for cognitive subpackage.
╚══════════════════════════════════════════════════════════════════════════════════
"""
import logging

import streamlit as st

# Module imports
from core.common import get_logger

# Configure module logger
logger = get_logger(__name__)

# Module constants
MODULE_VERSION = "1.0.0"
MODULE_NAME = "cognitive module"

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# MODULE: consciousness.cognitive
# DESCRIPTION: Initializes the 'cognitive' sub-package within LUKHAS AI's
#              consciousness systems. This package contains modules related to
#              cognitive processes, adaptation, and introspection.
# DEPENDENCIES: logging, .cognitive_adapter, .reflective_introspection
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════


# Initialize logger for ΛTRACE
logger = logging.getLogger("ΛTRACE.consciousness.cognitive")
logger.info("ΛTRACE: Initializing 'consciousness.cognitive' package.")

# Human-readable comment: Import key components from this package.
try:
    from .cognitive_adapter import CognitiveAdapter

    logger.debug("ΛTRACE: Imported 'CognitiveAdapter' from .cognitive_adapter.")
except ImportError as e_ca:
    logger.warning(f"ΛTRACE: Could not import 'CognitiveAdapter': {e_ca}.")
    CognitiveAdapter = None  # type: ignore

try:
    from .reflective_introspection import ReflectiveIntrospectionSystem

    logger.debug("ΛTRACE: Imported 'ReflectiveIntrospectionSystem' from .reflective_introspection.")
except ImportError as e_ri:
    logger.warning(f"ΛTRACE: Could not import 'ReflectiveIntrospectionSystem': {e_ri}.")
    ReflectiveIntrospectionSystem = None  # type: ignore


# Human-readable comment: Defines the public API of the 'cognitive' package.
__all__ = [
    "CognitiveAdapter",
    "ReflectiveIntrospectionSystem",
]
# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"ΛTRACE: 'consciousness.cognitive' package initialized. Exposed: {__all__}")

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# VERSION: 1.0.0
# TIER SYSTEM: Tier 2-4 (Cognitive functions are generally advanced capabilities)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Initializes the cognitive sub-package and exports key classes
#               for cognitive adaptation and reflective introspection.
# FUNCTIONS: None directly exposed beyond imported symbols.
# CLASSES: Exports CognitiveAdapter, ReflectiveIntrospectionSystem.
# DECORATORS: None.
# DEPENDENCIES: Python standard logging, .cognitive_adapter, .reflective_introspection.
# INTERFACES: Defines the 'consciousness.cognitive' namespace.
# ERROR HANDLING: Logs import errors for its components.
# LOGGING: ΛTRACE_ENABLED for package initialization.
# AUTHENTICATION: Not applicable at package level.
# HOW TO USE:
#   from consciousness.cognitive import CognitiveAdapter
#   adapter = CognitiveAdapter()
# INTEGRATION NOTES: This package provides core cognitive utilities for the consciousness system.
# MAINTENANCE: Update imports and __all__ as modules are added or changed.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/test___init__.py
║   - Coverage: N/A%
║   - Linting: pylint N/A/10
║
║ MONITORING:
║   - Metrics: N/A
║   - Logs: N/A
║   - Alerts: N/A
║
║ COMPLIANCE:
║   - Standards: N/A
║   - Ethics: Refer to LUKHAS Ethics Guidelines
║   - Safety: Refer to LUKHAS Safety Protocols
║
║ REFERENCES:
║   - Docs: docs/consciousness/cognitive module.md
║   - Issues: github.com/lukhas-ai/lukhas/issues?label=cognitive module
║   - Wiki: N/A
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS Cognitive system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════
"""
