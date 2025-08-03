"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


════════════════════════════════════════════════════════════════════════════════
║ 🎤 LUKHAS AI - VOICE SYSTEMS PACKAGE
║ Initialization for voice-related modules
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: __init__.py
║ Path: lukhas/core/voice_systems/__init__.py
║ Version: 1.0.0 | Created: 2025-06-20 | Modified: 2025-07-25
║ Authors: LUKHAS AI Voice Team | Codex
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ Provides package initialization for voice subsystems.
╚═══════════════════════════════════════════════════════════════════════════════
"""

"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/core/voice_systems/test_package_init.py
║   - Coverage: N/A
║   - Linting: pylint N/A
║
║ MONITORING:
║   - Metrics: package_imports
║   - Logs: voice_package_logs
║   - Alerts: package_errors
║
║ COMPLIANCE:
║   - Standards: N/A
║   - Ethics: Refer to LUKHAS Ethics Guidelines
║   - Safety: Refer to LUKHAS Safety Protocols
║
║ REFERENCES:
║   - Docs: docs/core/voice_systems/overview.md
║   - Issues: github.com/lukhas-ai/lukhas/issues?label=voice_systems
║   - Wiki: N/A
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
╚═══════════════════════════════════════════════════════════════════════════════
"""

# Import priority voice components
from .context_aware_voice_modular import ContextAwareVoiceSystem
from .recognition import VoiceRecognition

# Import voice hub for Agent 10 Advanced Systems
from .voice_hub import VoiceHub, get_voice_hub

# Export voice components
__all__ = [
    "VoiceHub",
    "get_voice_hub",
    "ContextAwareVoiceSystem",
    "VoiceRecognition",
]
