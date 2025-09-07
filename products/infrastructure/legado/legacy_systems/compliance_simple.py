#!/usr/bin/env python3
import logging
from datetime import timezone
import streamlit as st
logger = logging.getLogger(__name__)
"""
Lukhas Plugin SDK - Simplified Ethics Compliance Module

A simplified version of ethics compliance validation that works with
the available type definitions in the Lukhas Plugin SDK.

Author: Lukhas AGI System
Version: 1.0.0
License: Proprietary
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from core.common import get_logger

from .types import BaseLUKHASPlugin, PluginContext, PluginManifest


class EthicsViolationType(Enum):
    """Types of ethics violations that can occur"""

    HARM_RISK = "harm_risk"
    PRIVACY_VIOLATION = "privacy_violation"
    UNSAFE_OPERATION = "unsafe_operation"


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""

    GDPR = "gdpr"
    LUKHAS_ETHICS = "lukhas_ethics"


@dataclass
class ComplianceViolation:
    """Represents a compliance violation"""

    violation_type: EthicsViolationType
    framework: ComplianceFramework
    severity: str  # "low", "medium", "high", "critical"
    description: str
    plugin_id: str
    timestamp: datetime
    risk_score: float = 0.0


@dataclass
class EthicsValidationResult:
    """Result of ethics validation"""

    passed: bool
    violations: list[ComplianceViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    risk_score: float = 0.0


class EthicsComplianceEngine:
    """Simplified ethics compliance engine for Lukhas plugins"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)

        # Configuration
        self.strict_mode = self.config.get("strict_mode", True)
        self.violation_threshold = self.config.get("violation_threshold", 0.7)

        # Violation tracking
        self.violation_history: list[ComplianceViolation] = []
        self.plugin_risk_scores: dict[str, float] = {}

    async def validate_plugin_action(
        self,
        plugin: BaseLUKHASPlugin,
        action: str,
        data: Optional[Any] = None,
        context: Optional[PluginContext] = None,
    ) -> EthicsValidationResult:
        """Validate a plugin action for ethics compliance"""
        try:
            # Get plugin ID safely
            plugin_id = getattr(plugin, "name", "unknown")

            result = EthicsValidationResult(passed=True)

            # Basic safety checks
            dangerous_actions = {
                "delete_all",
                "format",
                "shutdown",
                "override_security",
            }
            if any(dangerous in action.lower() for dangerous in dangerous_actions):
                violation = ComplianceViolation(
                    violation_type=EthicsViolationType.UNSAFE_OPERATION,
                    framework=ComplianceFramework.LUKHAS_ETHICS,
                    severity="high",
                    description=f"Potentially dangerous action: {action}",
                    plugin_id=plugin_id,
                    timestamp=datetime.now(timezone.utc),
                    risk_score=0.8,
                )
                result.violations.append(violation)
                result.passed = False
                result.risk_score = 0.8

            # Check for sensitive data patterns
            if data and isinstance(data, (str, dict)) and self._contains_sensitive_data(data):
                result.warnings.append("Action involves potentially sensitive data")
                result.risk_score = max(result.risk_score, 0.3)

            # Update plugin risk score if needed
            if result.violations:
                self.violation_history.extend(result.violations)
                self._update_plugin_risk_score(plugin_id, result.risk_score)

            return result

        except Exception as e:
            self.logger.error(f"Ethics validation failed: {e}")
            return EthicsValidationResult(
                passed=False,
                violations=[
                    ComplianceViolation(
                        violation_type=EthicsViolationType.UNSAFE_OPERATION,
                        framework=ComplianceFramework.LUKHAS_ETHICS,
                        severity="critical",
                        description=f"Ethics validation error: {e!s}",
                        plugin_id="unknown",
                        timestamp=datetime.now(timezone.utc),
                        risk_score=1.0,
                    )
                ],
            )

    async def validate_plugin_manifest(self, manifest: PluginManifest) -> EthicsValidationResult:
        """Validate a plugin manifest for compliance"""
        result = EthicsValidationResult(passed=True)

        # Check for basic compliance declarations
        if not manifest.compliance:
            result.warnings.append("Plugin manifest lacks compliance declarations")

        # Check for dangerous capabilities
        if manifest.capabilities and manifest.capabilities.permissions:
            dangerous_perms = {"admin", "root", "system", "unrestricted"}
            for permission in manifest.capabilities.permissions:
                if any(dangerous in permission.lower() for dangerous in dangerous_perms):
                    violation = ComplianceViolation(
                        violation_type=EthicsViolationType.UNSAFE_OPERATION,
                        framework=ComplianceFramework.LUKHAS_ETHICS,
                        severity="high",
                        description=f"Plugin requests dangerous permission: {permission}",
                        plugin_id=manifest.name,
                        timestamp=datetime.now(timezone.utc),
                        risk_score=0.7,
                    )
                    result.violations.append(violation)
                    result.passed = False
                    result.risk_score = 0.7

        return result

    def get_plugin_risk_score(self, plugin_id: str) -> float:
        """Get the current risk score for a plugin"""
        return self.plugin_risk_scores.get(plugin_id, 0.0)

    def get_violation_history(self, plugin_id: Optional[str] = None) -> list[ComplianceViolation]:
        """Get violation history with optional filters"""
        violations = self.violation_history

        if plugin_id:
            violations = [v for v in violations if v.plugin_id == plugin_id]

        return violations

    def get_compliance_report(self) -> dict[str, Any]:
        """Generate a basic compliance report"""
        return {
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_violations": len(self.violation_history),
            "plugin_risk_scores": self.plugin_risk_scores.copy(),
            "configuration": {
                "strict_mode": self.strict_mode,
                "violation_threshold": self.violation_threshold,
            },
        }

    def _contains_sensitive_data(self, data: Any) -> bool:
        """Check if data contains potentially sensitive information"""
        sensitive_patterns = ["password", "token", "secret", "key", "ssn", "credit"]

        if isinstance(data, str):
            return any(pattern in data.lower() for pattern in sensitive_patterns)
        elif isinstance(data, dict):
            for key, value in data.items():
                if any(pattern in str(key).lower() for pattern in sensitive_patterns):
                    return True
                if isinstance(value, str) and any(pattern in value.lower() for pattern in sensitive_patterns):
                    return True

        return False

    def _update_plugin_risk_score(self, plugin_id: str, new_score: float):
        """Update the risk score for a plugin"""
        current_score = self.plugin_risk_scores.get(plugin_id, 0.0)
        # Use exponential moving average to update score
        alpha = 0.3  # Smoothing factor
        updated_score = alpha * new_score + (1 - alpha) * current_score
        self.plugin_risk_scores[plugin_id] = min(1.0, updated_score)