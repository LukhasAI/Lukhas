"""Bridge package - external service integrations."""

from __future__ import annotations

# Real implementation package
__all__ = []

# Bridge export for bridge.api
try:
    from labs.bridge import api
except ImportError:
    def api(*args, **kwargs):
        """Stub for api."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "api" not in __all__:
    __all__.append("api")

# Bridge export for bridge.api_framework
try:
    from labs.bridge import api_framework
except ImportError:
    def api_framework(*args, **kwargs):
        """Stub for api_framework."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "api_framework" not in __all__:
    __all__.append("api_framework")

# Bridge export for bridge.controllers
try:
    from labs.bridge import controllers
except ImportError:
    def controllers(*args, **kwargs):
        """Stub for controllers."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "controllers" not in __all__:
    __all__.append("controllers")

# Bridge export for bridge.explainability_interface_layer
try:
    from labs.bridge import explainability_interface_layer
except ImportError:
    def explainability_interface_layer(*args, **kwargs):
        """Stub for explainability_interface_layer."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "explainability_interface_layer" not in __all__:
    __all__.append("explainability_interface_layer")

# Bridge export for bridge.onboarding
try:
    from labs.bridge import onboarding
except ImportError:
    def onboarding(*args, **kwargs):
        """Stub for onboarding."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "onboarding" not in __all__:
    __all__.append("onboarding")

# Bridge export for bridge.openai_modulated_service
try:
    from labs.bridge import openai_modulated_service
except ImportError:
    def openai_modulated_service(*args, **kwargs):
        """Stub for openai_modulated_service."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "openai_modulated_service" not in __all__:
    __all__.append("openai_modulated_service")
