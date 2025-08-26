"""
Guardian System Core Types
==========================

Core data structures and enums for the LUKHAS Guardian system.
These types are used throughout the governance framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


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
    context: Dict[str, Any]
    severity: EthicalSeverity = EthicalSeverity.LOW
    timestamp: Optional[str] = None
    correlation_id: Optional[str] = None


@dataclass
class EthicalDecision:
    """Result of an ethical evaluation"""
    allowed: bool
    reason: str
    severity: EthicalSeverity
    confidence: float = 0.0
    recommendations: Optional[List[str]] = None
    drift_score: Optional[float] = None


@dataclass
class DriftResult:
    """Result of drift detection analysis"""
    drift_score: float
    threshold_exceeded: bool
    severity: EthicalSeverity
    remediation_needed: bool
    details: Dict[str, Any]


@dataclass
class SafetyResult:
    """Result of safety validation"""
    safe: bool
    risk_level: EthicalSeverity
    violations: List[str]
    recommendations: List[str]
    constitutional_check: bool
