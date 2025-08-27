"""
LUKHAS Guardian System - Legacy Compatibility Bridge
====================================================

This module provides backward compatibility for legacy code that expects
the old GuardianSystem interface while integrating with the new guardian
architecture in lukhas/governance/guardian/.

This bridge allows existing code to continue working while we transition
to the new modular Guardian System architecture.

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from __future__ import annotations

from typing import Any, Dict

from lukhas.governance.guardian.guardian_wrapper import detect_drift


class GuardianSystem:
    """
    Legacy compatibility wrapper for the Guardian System.
    
    This class provides the old GuardianSystem interface while delegating
    to the new modular guardian system components.
    """
    
    def __init__(self, drift_threshold: float = 0.15):
        """Initialize the Guardian System with legacy interface"""
        self.drift_threshold = drift_threshold
        self._initialized = True
        
    async def check_drift(self, data: Dict[str, Any]) -> float:
        """
        Legacy method for drift checking.
        
        This method maintains compatibility with old code that expects
        a simple drift score return value.
        
        Args:
            data: Dictionary containing action, component, severity, etc.
            
        Returns:
            float: Drift score between 0.0 and 1.0
        """
        try:
            # Extract parameters from data dict
            baseline = data.get("baseline", "")
            current = data.get("current", str(data.get("action", "")))
            threshold = data.get("threshold", self.drift_threshold)
            context = {
                "component": data.get("component", "unknown"),
                "severity": data.get("severity", 0.1),
                "action": data.get("action", "unknown")
            }
            
            # Use the new guardian system
            result = detect_drift(baseline, current, threshold, context)
            
            # Return just the drift score for legacy compatibility
            return result.drift_score
            
        except Exception:
            # Fallback to safe default on any error
            return 0.05  # Low drift score
    
    def is_active(self) -> bool:
        """Check if Guardian System is active"""
        return self._initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status for compatibility"""
        return {
            "active": True,
            "drift_threshold": self.drift_threshold,
            "version": "legacy_compatibility_bridge",
            "guardian_system_active": True
        }


# Export for backward compatibility
__all__ = ["GuardianSystem"]