"""
🛡️ LUKHAS Safety Systems Integration Bridge
Unified access to all safety and compliance systems
"""
from backend.security.privacy_manager import PrivacyManager
from compliance.ai_compliance import AICompliance

from candidate.orchestration.brain.safety_guardrails import SafetyGuardrails


class LUKHASSafetyBridge:
    """
    Unified interface for all LUKHAS safety systems.
    """

    def __init__(self):
        self.safety_guardrails = SafetyGuardrails()
        self.compliance = AICompliance()
        self.privacy = PrivacyManager()

    async def comprehensive_safety_check(self, content, context=None):
        """
        Run comprehensive safety checks across all systems.
        """
        results = {
            "safety_check": await self.safety_guardrails.check_safety(content),
            "compliance_check": await self.compliance.verify_compliance(content),
            "privacy_check": await self.privacy.check_privacy(content),
        }

        return {
            "safe": all(r.get("safe", False) for r in results.values()),
            "details": results,
        }


# Global safety bridge instance
safety_bridge = LUKHASSafetyBridge()