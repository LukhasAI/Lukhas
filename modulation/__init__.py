# 🎛️ LUKHAS_PWM Endocrine Signal Modulation System
"""
Bio-inspired signal-to-prompt modulation for OpenAI API integration.

This system translates LUKHAS_PWM's endocrine signals (biological-inspired "hormones")
into OpenAI API parameters, enabling consciousness system to modulate GPT behavior
based on internal state.

Core Components:
- Signal: Individual endocrine signals (stress, novelty, alignment_risk, etc.)
- SignalModulator: Combines signals into modulation parameters
- ModulatedOpenAIClient: Applies modulation to OpenAI API calls
- EndocrineLLMOrchestrator: Main orchestration layer

Trinity Framework Integration: ⚛️🧠🛡️
- ⚛️ Identity: Authentic signal emission from consciousness modules
- 🧠 Consciousness: Memory and learning from signal patterns
- 🛡️ Guardian: Safety-first modulation policies
"""

from .signals import Signal, ModulationParams, SignalModulator
from .openai_integration import ModulatedOpenAIClient, build_function_definitions
from .lukhas_integration import EndocrineSignalEmitter, EndocrineLLMOrchestrator

__all__ = [
    "Signal",
    "ModulationParams",
    "SignalModulator",
    "ModulatedOpenAIClient",
    "build_function_definitions",
    "EndocrineSignalEmitter",
    "EndocrineLLMOrchestrator",
]

# Version and metadata
__version__ = "0.1.0"
__trinity_compliance__ = True  # ⚛️🧠🛡️
