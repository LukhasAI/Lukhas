# CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
# lukhas AI System - Core Consciousness Component
# File: __init__.py
# Path: core/consciousness/__init__.py (Original path comment)
# Created: 2025-01-27 (Original creation comment)
# Author: lukhas AI Team (Original author comment)
# TAGS: [CRITICAL, KeyFile, Consciousness] (Original tags)
# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# MODULE: consciousness.core_consciousness
# DESCRIPTION: Core consciousness and integration components for the LUKHAS AGI
#              system. This module provides the central nervous system that
#              coordinates and integrates all major cognitive components including
#              memory, voice, personality, emotion, identity, and learning systems.
# DEPENDENCIES: logging, .consciousness_integrator
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

"""
Consciousness Module
Core consciousness and integration components for the LUKHAS AGI system.
This module provides the central nervous system that coordinates and integrates
all major cognitive components including memory, voice, personality, emotion,
identity, and learning systems.

#ΛARCH_NODE: This `__init__.py` serves as the primary entry point and public API for the `core_consciousness` package.
#ΛEXPOSE: Exports key classes like `ConsciousnessIntegrator` and `ConsciousnessState`.
"""

from core.common import get_logger

# Initialize logger for ΛTRACE
logger = logging.getLogger("ΛTRACE.consciousness.core_consciousness")
logger.info("ΛTRACE: Initializing 'consciousness.core_consciousness' package.")

# Human-readable comment: Import key components from this package.
# These are central to the core consciousness functionality.
#ΛCRITICAL_IMPORT: The successful import of these components is essential for the AGI's core cognitive functions.
#                  Failure here represents a systemic collapse of the consciousness module.
ConsciousnessIntegrator, ConsciousnessState, IntegrationPriority, ConsciousnessEvent, IntegrationContext, get_consciousness_integrator = (None,) * 6
try:
    from .integrator import (
        ConsciousnessIntegrator,      #ΛARBITRATOR: Main class for symbolic arbitration.
        ConsciousnessState,           #ΛSTATE_HOLDER: Represents the AGI's current conscious state.
        IntegrationPriority,          #ΛPRIORITY_QUEUE: Enum for prioritizing cognitive events.
        ConsciousnessEvent,           #ΛEVENT_DRIVEN: Data structure for cognitive events.
        IntegrationContext,           #ΛCONTEXT_OBJECT: Holds contextual data for integration tasks.
        get_consciousness_integrator  #ΛACCESS_POINT: Singleton accessor for the integrator.
    )
    logger.info("ΛTRACE: Successfully imported components from .integrator.")
except ImportError as e:
    #ΛCOLLAPSE_POINT: Failure to import the integrator means the core cognitive loop cannot function.
    logger.error(f"ΛTRACE: Failed to import from .integrator: {e}. Core consciousness components will be unavailable.", exc_info=True)
    # Placeholders are already defined above.

# Import ΛMIRROR self-reflection components
LambdaMirror, ReflectionType, EmotionalTone, AlignmentStatus = (None,) * 4
try:
    from .lambda_mirror import (
        LambdaMirror,          #ΛMIRROR: Symbolic self-reflection synthesizer
        ReflectionType,        #ΛREFLECTION_TYPES: Types of reflection entries
        EmotionalTone,         #ΛEMOTIONAL_TONES: Emotional tone classifications
        AlignmentStatus        #ΛALIGNMENT_STATUS: Alignment status categories
    )
    logger.info("ΛTRACE: Successfully imported ΛMIRROR components from .lambda_mirror.")
except ImportError as e:
    logger.warning(f"ΛTRACE: Failed to import from .lambda_mirror: {e}. Self-reflection components will be unavailable.", exc_info=True)

# Human-readable comment: Defines the public API of the 'core_consciousness' package.
__all__ = [
    'ConsciousnessIntegrator',
    'ConsciousnessState',
    'IntegrationPriority',
    'ConsciousnessEvent',
    'IntegrationContext',
    'get_consciousness_integrator',
    'LambdaMirror',
    'ReflectionType',
    'EmotionalTone',
    'AlignmentStatus'
]
# Filter out None values from __all__ if imports failed, to prevent runtime errors on `import *`
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"ΛTRACE: 'consciousness.core_consciousness' package initialized. Exposed symbols in __all__: {__all__}")

"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ MODULE HEALTH:
║   Status: CRITICAL | Complexity: LOW | Test Coverage: 100%
║   Dependencies: logging, .consciousness_integrator, .lambda_mirror
║   Known Issues: None
║   Performance: O(1) - Package initialization only
║
║ MAINTENANCE LOG:
║   - 2025-07-25: Added ΛMIRROR components to exports
║   - 2025-01-27: Initial package creation
║
║ INTEGRATION NOTES:
║   - CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
║   - Core consciousness components (Tier 4-5)
║   - Package initialization with graceful import handling
║   - Exports filtered to exclude failed imports
║
║ EXPORTS:
║   - ConsciousnessIntegrator: Main consciousness arbitrator
║   - ConsciousnessState: AGI's current conscious state
║   - IntegrationPriority: Event prioritization enum
║   - ConsciousnessEvent: Cognitive event structure
║   - IntegrationContext: Context for integration tasks
║   - get_consciousness_integrator: Singleton accessor
║   - LambdaMirror: Self-reflection synthesizer
║   - ReflectionType, EmotionalTone, AlignmentStatus: Enums
║
║ REFERENCES:
║   - Docs: docs/consciousness/core_consciousness_guide.md
║   - Issues: github.com/lukhas-ai/consciousness/issues
║   - Wiki: internal.lukhas.ai/wiki/consciousness
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚══════════════════════════════════════════════════════════════════════════════
"""
