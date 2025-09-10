"""
🛡️ Guardian System - Unified Interface
=====================================

Aggregated interface for all Guardian system components.
This module provides a unified API for accessing Guardian components
that are distributed across the governance module structure.

Integrated with LUKHAS Constellation Framework - Guardian (Watch Star) & Ethics (North Star).

Author: LUKHAS AI System
Version: 1.0.0
"""

# Import core Guardian components
try:
    from .ethics.guardian_reflector import GuardianReflector
except ImportError:
    GuardianReflector = None

try:
    from .guardian_sentinel import GuardianSentinel
except ImportError:
    GuardianSentinel = None

try:
    from .guardian_shadow_filter import GuardianShadowFilter
except ImportError:
    GuardianShadowFilter = None

try:
    from .ethics.enhanced_guardian import EnhancedWorkspaceGuardian
except ImportError:
    EnhancedWorkspaceGuardian = None

try:
    from .ethics.ethics_guardian import EthicsGuardian
except ImportError:
    EthicsGuardian = None


class GuardianSystem:
    """
    🛡️ Unified Guardian System Interface

    Provides centralized access to all Guardian components
    with ethical oversight and protection mechanisms.

    Constellation Framework Integration:
    - 🛡️ Guardian (Watch Star): Protection and trustworthiness
    - ⚖️ Ethics (North Star): Responsible, transparent, accountable oversight
    """

    def __init__(self, enable_reflection=True, enable_sentinel=True):
        """Initialize Guardian System with specified components"""
        self.components = {}
        self.active = True

        # Initialize Guardian Reflector (core ethical reasoning)
        if enable_reflection and GuardianReflector:
            try:
                self.components["reflector"] = GuardianReflector()
            except Exception as e:
                print(f"Warning: Could not initialize GuardianReflector: {e}")

        # Initialize Guardian Sentinel (unified protection)
        if enable_sentinel and GuardianSentinel:
            try:
                self.components["sentinel"] = GuardianSentinel()
            except Exception as e:
                print(f"Warning: Could not initialize GuardianSentinel: {e}")

        # Initialize Shadow Filter (identity protection)
        if GuardianShadowFilter:
            try:
                self.components["shadow_filter"] = GuardianShadowFilter()
            except Exception as e:
                print(f"Warning: Could not initialize GuardianShadowFilter: {e}")

        # Initialize Ethics Guardian (moral oversight)
        if EthicsGuardian:
            try:
                self.components["ethics_guardian"] = EthicsGuardian()
            except Exception as e:
                print(f"Warning: Could not initialize EthicsGuardian: {e}")

    def get_reflector(self):
        """Get the Guardian Reflector component"""
        return self.components.get("reflector")

    def get_sentinel(self):
        """Get the Guardian Sentinel component"""
        return self.components.get("sentinel")

    def get_shadow_filter(self):
        """Get the Guardian Shadow Filter component"""
        return self.components.get("shadow_filter")

    def get_ethics_guardian(self):
        """Get the Ethics Guardian component"""
        return self.components.get("ethics_guardian")

    async def validate_action(self, action_data):
        """Validate an action through all active Guardian components"""
        results = {}

        # Validate through reflector
        reflector = self.get_reflector()
        if reflector and hasattr(reflector, "reflect_on_decision"):
            try:
                results["reflection"] = await reflector.reflect_on_decision(action_data)
            except Exception as e:
                results["reflection"] = {"status": "error", "error": str(e)}

        # Validate through sentinel
        sentinel = self.get_sentinel()
        if sentinel and hasattr(sentinel, "validate"):
            try:
                results["sentinel"] = await sentinel.validate(action_data)
            except Exception as e:
                results["sentinel"] = {"status": "error", "error": str(e)}

        # Validate through ethics guardian
        ethics = self.get_ethics_guardian()
        if ethics and hasattr(ethics, "evaluate"):
            try:
                results["ethics"] = await ethics.evaluate(action_data)
            except Exception as e:
                results["ethics"] = {"status": "error", "error": str(e)}

        return results

    def is_available(self):
        """Check if Guardian System is available and functional"""
        return len(self.components) > 0 and self.active

    def get_status(self):
        """Get system status and component availability"""
        return {
            "active": self.active,
            "components": list(self.components.keys()),
            "reflector_available": GuardianReflector is not None,
            "sentinel_available": GuardianSentinel is not None,
            "shadow_filter_available": GuardianShadowFilter is not None,
            "ethics_guardian_available": EthicsGuardian is not None,
        }


# Export main classes for compatibility
__all__ = [
    "EnhancedWorkspaceGuardian",
    "EthicsGuardian",
    "GuardianReflector",
    "GuardianSentinel",
    "GuardianShadowFilter",
    "GuardianSystem",
]
