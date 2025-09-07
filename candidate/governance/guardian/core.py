#!/usr/bin/env python3
"""
Core governance classes for  Workspace Guardian
==================================================
Minimal implementation to support testing infrastructure.
"""
import streamlit as st

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class EthicalSeverity(Enum):
    """Severity levels for ethical decisions"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GovernanceAction:
    """Represents an action that requires governance oversight"""

    action_type: str
    target: str
    context: dict[str, Any]
    severity: EthicalSeverity = EthicalSeverity.LOW


@dataclass
class EthicalDecision:
    """Result of an ethical evaluation"""

    allowed: bool
    reason: str
    severity: EthicalSeverity
    recommendations: list = None


class LucasGovernanceModule:
    """
    Minimal governance module for  testing.

    This is a lightweight implementation to support the test infrastructure.
    Full governance integration will be handled in the comprehensive fix.
    """

    def __init__(self):
        self.active = False
        self.decisions_made = 0

    async def startup(self):
        """Initialize the governance module"""
        self.active = True
        print("🛡️ Governance module initialized")

    async def evaluate_action(self, action: GovernanceAction) -> EthicalDecision:
        """Evaluate whether an action should be allowed"""
        self.decisions_made += 1

        # Basic safety checks
        if action.action_type == "delete" and action.target in ["README.md", "LICENSE"]:
            return EthicalDecision(
                allowed=False,
                reason="Critical file protection",
                severity=EthicalSeverity.HIGH,
                recommendations=["Consider backing up the file first"],
            )

        return EthicalDecision(allowed=True, reason="Action appears safe", severity=EthicalSeverity.LOW)

    def get_status(self) -> dict[str, Any]:
        """Get current governance status"""
        return {
            "active": self.active,
            "decisions_made": self.decisions_made,
            "module": "LucasGovernanceModule",
            "version": "1.0.0-minimal",
        }


# Utility function for workspace protection
async def protect_my_workspace(workspace_path: Optional[str] = None) -> bool:
    """Quick protection function for workspace"""
    # Import locally to avoid circular imports
    import importlib.util
    import os

    guardian_path = os.path.join(os.path.dirname(__file__), "_workspace_guardian.py")
    spec = importlib.util.spec_from_file_location("_workspace_guardian", guardian_path)
    guardian_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guardian_module)

    guardian = guardian_module.WorkspaceGuardian(workspace_path)
    await guardian.initialize()
    return True
