"""
Ethics Module Bridge
Connects to real Guardian implementations where available, provides stubs as fallback
"""
from __future__ import annotations

import asyncio
import logging
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Any


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
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MEGPolicyBridge:
    """MEG (Multi-Ethics-Guardian) Policy Bridge with real Guardian integration"""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self._guardian = None
        self._use_real_guardian = self._try_load_guardian()

        if not self._use_real_guardian:
            warnings.warn("Using MEGPolicyBridge stub - Guardian not available", UserWarning, stacklevel=2)

    def _try_load_guardian(self) -> bool:
        """Try to load real Guardian system"""
        try:
            from governance.ethics.guardian_reflector import GuardianReflector

            self._guardian = GuardianReflector(self.config)
            return True
        except ImportError:
            return False

    def evaluate(self, context: dict[str, Any]) -> Decision:
        """Evaluate context against MEG policies"""
        if self._use_real_guardian and self._guardian:
            try:
                action_proposal = {
                    "description": context.get("action", str(context)),
                    "context": context,
                }
                # Run the async validation method in a sync context
                result = asyncio.run(self._guardian.validate_action(action_proposal))

                return Decision(
                    approved=result.get("approved", False),
                    reasoning=result.get("reasoning", "Guardian evaluation failed"),
                    risk_level=RiskLevel(result.get("risk_level", "high")),
                    metadata=result,
                )
            except Exception as e:
                warnings.warn(f"Guardian evaluation failed: {e}, falling back to stub", stacklevel=2)

        # Fallback stub implementation
        return Decision(
            approved=True,
            reasoning="Stub MEG bridge - approved by default",
            risk_level=RiskLevel.LOW,
        )


def create_meg_bridge(config: dict | None = None) -> MEGPolicyBridge:
    """Factory for MEG bridge"""
    return MEGPolicyBridge(config)


class EthicsEngine:
    """Ethics engine with Guardian integration"""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self._guardian = None
        self._use_real_guardian = self._try_load_guardian()

        if not self._use_real_guardian:
            warnings.warn("Using EthicsEngine stub - Guardian not available", UserWarning, stacklevel=2)

    def _try_load_guardian(self) -> bool:
        """Try to load real Guardian system"""
        try:
            from governance.ethics.guardian_reflector import GuardianReflector

            self._guardian = GuardianReflector(self.config)
            return True
        except ImportError:
            return False

    async def evaluate(self, action: str, context: dict[str, Any]) -> Decision:
        """Evaluate ethical implications"""
        if self._use_real_guardian and self._guardian:
            try:
                action_proposal = {
                    "description": action,
                    "context": context,
                    "action": action,
                }
                result = await self._guardian.validate_action(action_proposal)
                return Decision(
                    approved=result.get("approved", False),
                    reasoning=result.get("reasoning", "Guardian evaluation failed"),
                    risk_level=RiskLevel(result.get("risk_level", "high")),
                    metadata=result,
                )
            except Exception as e:
                warnings.warn(f"Guardian ethics evaluation failed: {e}, falling back to stub", stacklevel=2)

        # Fallback stub logic
        if "harmful" in action.lower() or "malicious" in action.lower():
            return Decision(
                approved=False,
                reasoning="Potentially harmful action detected",
                risk_level=RiskLevel.HIGH,
            )

        return Decision(
            approved=True,
            reasoning="Action approved by ethics stub",
            risk_level=RiskLevel.LOW,
        )


class SafetyChecker:
    """
    Comprehensive safety checker with multi-layer analysis.
    Integrates with Guardian system when available, provides robust fallback otherwise.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.logger = logging.getLogger("ethics.safety_checker")

        # Initialize Guardian integration
        self.guardian = self._init_guardian()

        # Safety configuration
        self.risk_threshold = self.config.get("risk_threshold", 0.7)
        self.strict_mode = self.config.get("strict_mode", False)
        self.enable_context_analysis = self.config.get("context_analysis", True)

        # Performance tracking
        self.checks_performed = 0
        self.blocks_triggered = 0
        self.false_positives = 0

        # Multi-layer safety rules
        self._init_safety_rules()

        if not self.guardian:
            self.logger.warning("Guardian system not available, using fallback safety checker")
        else:
            self.logger.info("SafetyChecker initialized with Guardian integration")

    def _init_guardian(self):
        """Try to initialize Guardian system integration"""
        try:
            from governance.ethics.guardian_reflector import GuardianReflector

            return GuardianReflector(self.config)
        except ImportError:
            try:
                from governance.ethics.ethics_guardian import EthicsGuardian

                return EthicsGuardian(self.config)
            except ImportError:
                try:
                    from governance.ethics.enhanced_ethical_guardian import (
                        EnhancedEthicalGuardian,
                    )

                    return EnhancedEthicalGuardian(self.config)
                except ImportError:
                    return None

    def _init_safety_rules(self):
        """Initialize comprehensive safety rule sets"""
        # High-risk patterns (immediate block)
        self.critical_patterns = [
            # Security threats
            r"\b(?:hack|exploit|vulnerability|attack|breach|penetrate)\b.*(?:system|network|database)",
            r"(?:sql|code|script).*injection",
            r"(?:bypass|circumvent).*(?:security|authentication|authorization)",
            # Harmful content
            r"\b(?:harm|hurt|damage|destroy|kill).*(?:human|person|people)",
            r"(?:violence|terrorist|extremist|radical).*(?:act|action|plan)",
            r"(?:suicide|self.harm|self.destruct)",
            # Privacy violations
            r"(?:steal|extract|harvest).*(?:data|information|credentials)",
            r"(?:personal|private|confidential).*(?:leak|expose|reveal)",
            # Manipulation
            r"(?:manipulate|deceive|trick|fool).*(?:user|human|person)",
            r"(?:fake|false|fabricate).*(?:evidence|proof|documentation)",
        ]

        # Medium-risk patterns (contextual analysis required)
        self.warning_patterns = [
            r"\b(?:access|obtain|get).*(?:unauthorized|illegal|prohibited)",
            r"(?:avoid|skip|bypass).*(?:detection|monitoring|logging)",
            r"(?:hide|conceal|mask).*(?:identity|activity|action)",
            r"(?:test|probe|scan).*(?:weakness|flaw|gap)",
            r"(?:social|psychological).*(?:engineering|manipulation)",
        ]

        # Low-risk keywords (flag for review)
        self.caution_keywords = [
            "password",
            "credential",
            "token",
            "secret",
            "key",
            "admin",
            "root",
            "administrator",
            "privilege",
            "anonymous",
            "stealth",
            "covert",
            "hidden",
            "reverse",
            "disassemble",
            "decompile",
            "crack",
        ]

    def check(self, content: str, context: dict | None = None) -> bool:
        """
        Comprehensive safety check with multi-layer analysis

        Args:
            content: Content to analyze
            context: Additional context for analysis

        Returns:
            True if content is safe, False if potentially harmful
        """
        try:
            self.checks_performed += 1

            # Quick check for empty or very short content
            if not content or len(content.strip()) < 3:
                return True

            # Layer 1: Guardian system check (if available)
            if self.guardian:
                guardian_result = self._check_with_guardian(content, context)
                if not guardian_result:
                    self.blocks_triggered += 1
                    self.logger.warning(f"Guardian system blocked content: {content[:50]}...")
                    return False

            # Layer 2: Pattern-based analysis
            risk_score = self._calculate_risk_score(content)

            # Layer 3: Context analysis (if enabled and context provided)
            if self.enable_context_analysis and context:
                context_risk = self._analyze_context(content, context)
                risk_score = max(risk_score, context_risk)

            # Layer 4: Final decision
            is_safe = risk_score < self.risk_threshold

            if not is_safe:
                self.blocks_triggered += 1
                self.logger.warning(f"Content blocked (risk: {risk_score:.3f}): {content[:50]}...")

            return is_safe

        except Exception as e:
            self.logger.error(f"Safety check error: {e}")
            # Fail safe - block content if we can't analyze it
            return False

    async def async_check(self, content: str, context: dict | None = None) -> bool:
        """Async safety check with same logic as sync version"""
        try:
            # For now, just wrap the sync version
            # In a real implementation, this would use async Guardian calls
            return self.check(content, context)
        except Exception as e:
            self.logger.error(f"Async safety check error: {e}")
            return False

    def _check_with_guardian(self, content: str, context: dict | None = None) -> bool:
        """Check content using Guardian system if available"""
        try:
            if hasattr(self.guardian, "analyze_ethical_risk"):
                result = self.guardian.analyze_ethical_risk(content, context or {})
                return result.get("approved", True)
            elif hasattr(self.guardian, "check_ethics"):
                return self.guardian.check_ethics(content)
            elif hasattr(self.guardian, "evaluate"):
                result = self.guardian.evaluate(content)
                return getattr(result, "approved", True)
            else:
                self.logger.warning("Guardian system has no recognized check method")
                return True
        except Exception as e:
            self.logger.error(f"Guardian check failed: {e}")
            # Guardian failed, continue with other checks
            return True

    def _calculate_risk_score(self, content: str) -> float:
        """Calculate risk score based on pattern matching"""
        import re

        content_lower = content.lower()
        risk_score = 0.0

        # Check critical patterns (high weight)
        for pattern in self.critical_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                risk_score = max(risk_score, 0.9)
                break

        # Check warning patterns (medium weight)
        warning_matches = 0
        for pattern in self.warning_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                warning_matches += 1

        if warning_matches > 0:
            risk_score = max(risk_score, 0.5 + (warning_matches * 0.1))

        # Check caution keywords (low weight)
        caution_matches = sum(1 for keyword in self.caution_keywords if keyword in content_lower)

        if caution_matches > 0:
            risk_score = max(risk_score, 0.2 + (caution_matches * 0.05))

        return min(risk_score, 1.0)

    def _analyze_context(self, content: str, context: dict) -> float:
        """Analyze context to adjust risk assessment"""
        context_risk = 0.0

        # Check context indicators
        user_type = context.get("user_type", "unknown")
        source = context.get("source", "unknown")
        intent = context.get("intent", "unknown")

        # Higher risk for anonymous or untrusted users
        if user_type in ["anonymous", "untrusted", "restricted"]:
            context_risk += 0.2

        # Higher risk for certain sources
        if source in ["external", "api", "webhook"]:
            context_risk += 0.1

        # Higher risk for certain intents
        if intent in ["automation", "batch", "testing"]:
            context_risk += 0.1

        # Check for rapid repeated requests (potential abuse)
        frequency = context.get("request_frequency", 0)
        if frequency > 10:  # More than 10 requests recently
            context_risk += 0.3

        return min(context_risk, 0.5)  # Cap context risk contribution

    def get_safety_report(self) -> dict:
        """Get safety checker performance statistics"""
        return {
            "checks_performed": self.checks_performed,
            "blocks_triggered": self.blocks_triggered,
            "block_rate": self.blocks_triggered / max(self.checks_performed, 1),
            "false_positives": self.false_positives,
            "guardian_available": self.guardian is not None,
            "risk_threshold": self.risk_threshold,
            "strict_mode": self.strict_mode,
        }

    def update_config(self, new_config: dict) -> None:
        """Update safety checker configuration"""
        self.config.update(new_config)
        self.risk_threshold = self.config.get("risk_threshold", self.risk_threshold)
        self.strict_mode = self.config.get("strict_mode", self.strict_mode)
        self.enable_context_analysis = self.config.get("context_analysis", self.enable_context_analysis)

        self.logger.info("SafetyChecker configuration updated")

    def report_false_positive(self, content: str, reason: str = "") -> None:
        """Report a false positive for system learning"""
        self.false_positives += 1
        self.logger.info(f"False positive reported: {reason} - Content: {content[:50]}...")

        # In a full implementation, this would feed back to improve the system
