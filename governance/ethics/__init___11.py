"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


lukhas AI System - Function Library
Path: lukhas/core/dreams/__init__.py
Author: lukhas AI Team
This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""

# Dream Engine Optimizer
try:
    from .engine.dream_engine_optimizer import DreamEngineOptimizer
except ImportError:
    # Fallback for compatibility
    DreamEngineOptimizer = None

try:
    from .rl import RLDreamCycle
except ImportError:
    RLDreamCycle = None
try:
    from .dream_sandbox import DreamSandbox
except ImportError:
    DreamSandbox = None
try:
    from .visualization.memoryscape_viewport import DreamMemoryscapeViewport
except ImportError:
    DreamMemoryscapeViewport = None

# Dream Generator
try:
    from .dream_generator import DreamGenerator
    dream_generator = DreamGenerator()
except ImportError:
    from . import dream_generator

__all__ = [
    "DreamEngineOptimizer",
    "dream_generator",
    "RLDreamCycle",
    "DreamMemoryscapeViewport",
    "DreamSandbox",

]




# Last Updated: 2025-06-05 09:37:28
