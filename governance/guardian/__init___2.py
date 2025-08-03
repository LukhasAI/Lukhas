"""

#TAG:governance
#TAG:guardian
#TAG:neuroplastic
#TAG:colony


Guardian Reflector Plugin Package
Ethical reflection and moral reasoning guardian for LUKHAS AGI system
"""

from .src.guardian_reflector import GuardianReflector, create_plugin, PLUGIN_METADATA

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__description__ = "Ethical reflection and moral reasoning guardian"

__all__ = [
    "GuardianReflector",
    "create_plugin",
    "PLUGIN_METADATA"
]
