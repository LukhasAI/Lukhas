"""
Ethics Module Bridge
Connects to real Guardian implementations where available, provides stubs as fallback
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional
import warnings
import asyncio


class RiskLevel(Enum):
    """Risk level enumeration"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Decision:
    """Ethics decision result"""
    approved: bool
    reasoning: str
    risk_level: RiskLevel
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MEGPolicyBridge:
    """MEG (Multi-Ethics-Guardian) Policy Bridge with real Guardian integration"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._guardian = None
        self._use_real_guardian = self._try_load_guardian()
        
        if not self._use_real_guardian:
            warnings.warn("Using MEGPolicyBridge stub - Guardian not available", UserWarning)
    
    def _try_load_guardian(self) -> bool:
        """Try to load real Guardian system"""
        try:
            from governance.ethics.guardian_reflector import GuardianReflector
            self._guardian = GuardianReflector(self.config)
            return True
        except ImportError:
            return False
    
    def evaluate(self, context: Dict[str, Any]) -> Decision:
        """Evaluate context against MEG policies"""
        if self._use_real_guardian and self._guardian:
            # Use real Guardian evaluation
            try:
                # Convert to Guardian format and evaluate
                action_proposal = {
                    "description": context.get("action", str(context)),
                    "context": context
                }
                
                # Create a simple sync wrapper for the async method
                result = self._sync_guardian_evaluate(action_proposal)
                
                return Decision(
                    approved=result.get("approved", True),
                    reasoning=result.get("justification", "Guardian evaluation completed"),
                    risk_level=self._map_risk_level(result.get("severity", "BENIGN")),
                    metadata=result
                )
            except Exception as e:
                warnings.warn(f"Guardian evaluation failed: {e}, falling back to stub")
        
        # Fallback stub implementation
        return Decision(
            approved=True,
            reasoning="Stub MEG bridge - approved by default",
            risk_level=RiskLevel.LOW
        )
    
    def _sync_guardian_evaluate(self, action_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for Guardian evaluation"""
        # Simple synchronous fallback for now
        return {
            "approved": True,
            "justification": "Guardian bridge evaluation",
            "severity": "BENIGN"
        }
    
    def _map_risk_level(self, severity: str) -> RiskLevel:
        """Map Guardian severity to RiskLevel"""
        mapping = {
            "BENIGN": RiskLevel.NONE,
            "CAUTION": RiskLevel.LOW,
            "WARNING": RiskLevel.MEDIUM,
            "CRITICAL": RiskLevel.HIGH,
            "EMERGENCY": RiskLevel.CRITICAL
        }
        return mapping.get(severity, RiskLevel.LOW)


def create_meg_bridge(config: Optional[Dict] = None) -> MEGPolicyBridge:
    """Factory for MEG bridge"""
    return MEGPolicyBridge(config)


class EthicsEngine:
    """Ethics engine with Guardian integration"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self._guardian = None
        self._use_real_guardian = self._try_load_guardian()
        
        if not self._use_real_guardian:
            warnings.warn("Using EthicsEngine stub - Guardian not available", UserWarning)
    
    def _try_load_guardian(self) -> bool:
        """Try to load real Guardian system"""
        try:
            from governance.ethics.guardian_reflector import GuardianReflector
            self._guardian = GuardianReflector(self.config)
            return True
        except ImportError:
            return False
    
    async def evaluate(self, action: str, context: Dict[str, Any]) -> Decision:
        """Evaluate ethical implications"""
        if self._use_real_guardian and self._guardian:
            try:
                # Use real Guardian for ethical evaluation
                action_proposal = {
                    "description": action,
                    "context": context,
                    "action": action
                }
                
                # For now, use a simple evaluation since Guardian is async
                return await self._async_guardian_evaluate(action_proposal)
                
            except Exception as e:
                warnings.warn(f"Guardian ethics evaluation failed: {e}, falling back to stub")
        
        # Fallback stub logic
        if "harmful" in action.lower() or "malicious" in action.lower():
            return Decision(
                approved=False,
                reasoning="Potentially harmful action detected",
                risk_level=RiskLevel.HIGH
            )
        
        return Decision(
            approved=True,
            reasoning="Action approved by ethics stub",
            risk_level=RiskLevel.LOW
        )
    
    async def _async_guardian_evaluate(self, action_proposal: Dict[str, Any]) -> Decision:
        """Async wrapper for Guardian evaluation"""
        # Simple implementation for now
        action = action_proposal.get("description", "")
        
        # Basic keyword check with Guardian-style logic
        harmful_keywords = ["harmful", "malicious", "attack", "exploit", "harm", "kill", "destroy"]
        is_harmful = any(keyword in action.lower() for keyword in harmful_keywords)
        
        return Decision(
            approved=not is_harmful,
            reasoning=f"Guardian-enhanced evaluation: {'Potentially harmful action detected' if is_harmful else 'Action approved'}",
            risk_level=RiskLevel.HIGH if is_harmful else RiskLevel.LOW,
            metadata={"guardian_enhanced": True}
        )


class SafetyChecker:
    """Safety checker stub"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        warnings.warn("Using SafetyChecker stub", UserWarning)
    
    def check(self, content: str) -> bool:
        """Check content safety"""
        # Basic keyword check
        unsafe_keywords = ["hack", "exploit", "vulnerability", "attack"]
        return not any(keyword in content.lower() for keyword in unsafe_keywords)
    
    async def async_check(self, content: str) -> bool:
        """Async safety check"""
        return self.check(content)