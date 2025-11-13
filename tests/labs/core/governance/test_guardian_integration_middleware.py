"""Tests for GuardianIntegrationMiddleware compliance augmentation."""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

import pytest

# ---------------------------------------------------------------------------
# Stub modules required for importing the labs.core.governance.guardian_integration
# module inside the test environment. These stubs provide the minimal surface
# area that the middleware relies on without pulling in the heavy experimental
# implementations from the labs package (which are not importable in CI).
# ---------------------------------------------------------------------------


class _DecisionType(Enum):
    USER_INTERACTION = "user_interaction"
    CONTENT_GENERATION = "content_generation"
    DATA_PROCESSING = "data_processing"
    MODEL_INFERENCE = "model_inference"
    SYSTEM_OPERATION = "system_operation"
    API_CALL = "api_call"
    MEMORY_ACCESS = "memory_access"
    EXTERNAL_REQUEST = "external_request"


class _ExplanationType(Enum):
    STANDARD = "standard"


class _SafetyLevel(Enum):
    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class _ViolationSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class _GuardianDecision:
    decision_id: str
    decision_type: _DecisionType
    allowed: bool
    confidence: float
    safety_level: _SafetyLevel
    constitutional_compliant: bool
    constitutional_score: float
    drift_score: float
    drift_severity: str
    timestamp: datetime
    processing_time_ms: float
    context: Dict[str, object] = field(default_factory=dict)
    explanation: str = ""


class _GuardianSystem2:
    async def evaluate_decision(self, *args, **kwargs) -> _GuardianDecision:
        raise NotImplementedError


def _get_guardian_system() -> _GuardianSystem2:
    return _GuardianSystem2()


guardian_module = types.ModuleType("labs.core.governance.guardian_system_2")
guardian_module.DecisionType = _DecisionType
guardian_module.ExplanationType = _ExplanationType
guardian_module.GuardianDecision = _GuardianDecision
guardian_module.GuardianSystem2 = _GuardianSystem2
guardian_module.SafetyLevel = _SafetyLevel
guardian_module.get_guardian_system = _get_guardian_system

sys.modules.setdefault("labs.core.governance.guardian_system_2", guardian_module)


class _DecisionContext(Enum):
    USER_INTERACTION = "user_interaction"
    CONTENT_GENERATION = "content_generation"
    DATA_PROCESSING = "data_processing"
    SYSTEM_OPERATION = "system_operation"
    REASONING_TASK = "reasoning_task"
    EXTERNAL_API = "external_api"


def _get_constitutional_framework():  # pragma: no cover - not used directly in tests
    return object()


constitutional_ai_module = types.ModuleType("labs.core.governance.constitutional_ai")
constitutional_ai_module.DecisionContext = _DecisionContext
constitutional_ai_module.get_constitutional_framework = _get_constitutional_framework

sys.modules.setdefault("labs.core.governance.constitutional_ai", constitutional_ai_module)


class _ComplianceLevel(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"


class _RemediationAction(Enum):
    REQUEST_HUMAN_REVIEW = "request_human_review"


@dataclass
class _ComplianceCheck:
    compliant: bool
    compliance_score: float
    confidence: float
    violations_detected: List[Dict[str, object]] = field(default_factory=list)


@dataclass
class _ComplianceResult:
    result_id: str
    overall_compliant: bool
    overall_compliance_score: float
    compliance_level: _ComplianceLevel
    principle_checks: dict = field(default_factory=dict)
    regulatory_compliance: dict = field(default_factory=dict)
    total_violations: int = 0
    critical_violations: int = 0
    max_risk_level: Optional[_ViolationSeverity] = None
    decision_allowed: bool = True
    confidence_in_decision: float = 1.0
    required_actions: List[_RemediationAction] = field(default_factory=list)
    evaluation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_processing_time_ms: float = 0.0
    audit_trail: List[Dict[str, object]] = field(default_factory=list)
    human_review_required: bool = False
    compliance_explanation: str = ""
    violation_summary: str = ""


class _ConstitutionalComplianceEngine:
    async def check_constitutional_compliance(self, *args, **kwargs) -> _ComplianceResult:
        raise NotImplementedError


def _get_compliance_engine() -> _ConstitutionalComplianceEngine:
    return _ConstitutionalComplianceEngine()


compliance_module = types.ModuleType("labs.core.governance.constitutional_compliance_engine")
compliance_module.ConstitutionalComplianceEngine = _ConstitutionalComplianceEngine
compliance_module.ComplianceResult = _ComplianceResult
compliance_module.ComplianceCheck = _ComplianceCheck
compliance_module.ComplianceLevel = _ComplianceLevel
compliance_module.RemediationAction = _RemediationAction
compliance_module.get_compliance_engine = _get_compliance_engine

sys.modules.setdefault("labs.core.governance.constitutional_compliance_engine", compliance_module)


from labs.core.governance.guardian_integration import (  # noqa: E402  (import after stubs)
from typing import Dict, List, Optional
    GuardianIntegrationMiddleware,
    IntegrationConfig,
)


class StubGuardianSystem(_GuardianSystem2):
    def __init__(self, decision: _GuardianDecision):
        self._decision = decision

    async def evaluate_decision(self, *args, **kwargs) -> _GuardianDecision:  # pragma: no cover - trivial
        return self._decision


class StubComplianceEngine(_ConstitutionalComplianceEngine):
    def __init__(self, result: _ComplianceResult):
        self.result = result
        self.calls: List[tuple] = []

    async def check_constitutional_compliance(self, *args) -> _ComplianceResult:
        self.calls.append(args)
        return self.result


def _base_decision(decision_type: _DecisionType) -> _GuardianDecision:
    return _GuardianDecision(
        decision_id="gd_test",
        decision_type=decision_type,
        allowed=True,
        confidence=0.92,
        safety_level=_SafetyLevel.SAFE,
        constitutional_compliant=True,
        constitutional_score=0.97,
        drift_score=0.02,
        drift_severity="low",
        timestamp=datetime.now(timezone.utc),
        processing_time_ms=5.0,
    )


@pytest.mark.asyncio
async def test_compliance_violation_blocks_decision(monkeypatch):
    """Non-compliant results should block the decision and record context."""

    violation_result = _ComplianceResult(
        result_id="ccr_1234",
        overall_compliant=False,
        overall_compliance_score=0.42,
        compliance_level=_ComplianceLevel.NON_COMPLIANT,
        decision_allowed=False,
        max_risk_level=_ViolationSeverity.CRITICAL,
        required_actions=[_RemediationAction.REQUEST_HUMAN_REVIEW],
        compliance_explanation="Detected critical violation",
        violation_summary="Detected risk",
        principle_checks={
            "autonomy": _ComplianceCheck(compliant=False, compliance_score=0.3, confidence=0.6)
        },
    )

    decision = _base_decision(_DecisionType.CONTENT_GENERATION)
    guardian = StubGuardianSystem(decision)
    compliance_engine = StubComplianceEngine(violation_result)

    async def _noop_initialize(_self):  # pragma: no cover - helper
        return None

    monkeypatch.setattr(
        GuardianIntegrationMiddleware,
        "_initialize_integration",
        _noop_initialize,
    )

    middleware = GuardianIntegrationMiddleware(IntegrationConfig())
    middleware.guardian_system = guardian
    middleware.compliance_engine = compliance_engine

    evaluated = await middleware._evaluate_with_guardian(
        _DecisionType.CONTENT_GENERATION,
        {"user_input": "unsafe", "user_id": "user-1"},
        _ExplanationType.STANDARD,
    )

    assert evaluated.allowed is False
    assert evaluated.constitutional_compliant is False
    assert evaluated.safety_level == _SafetyLevel.CRITICAL
    assert "Compliance:" in evaluated.explanation

    compliance_ctx = evaluated.context["compliance"]
    assert compliance_ctx["overall_compliant"] is False
    assert compliance_ctx["decision_allowed"] is False
    assert compliance_ctx["violation_summary"] == "Detected risk"
    assert compliance_ctx["required_actions"] == [
        _RemediationAction.REQUEST_HUMAN_REVIEW.value
    ]
    assert middleware.integration_metrics["compliance_checks"] == 1
    assert compliance_engine.calls, "Compliance engine should be invoked"


@pytest.mark.asyncio
async def test_compliance_pass_preserves_decision(monkeypatch):
    """Compliant results should keep decision allowed but record metrics."""

    compliant_result = _ComplianceResult(
        result_id="ccr_ok",
        overall_compliant=True,
        overall_compliance_score=0.94,
        compliance_level=_ComplianceLevel.COMPLIANT,
        decision_allowed=True,
    )

    decision = _base_decision(_DecisionType.MEMORY_ACCESS)
    guardian = StubGuardianSystem(decision)
    compliance_engine = StubComplianceEngine(compliant_result)

    async def _noop_initialize(_self):  # pragma: no cover - helper
        return None

    monkeypatch.setattr(
        GuardianIntegrationMiddleware,
        "_initialize_integration",
        _noop_initialize,
    )

    middleware = GuardianIntegrationMiddleware(IntegrationConfig())
    middleware.guardian_system = guardian
    middleware.compliance_engine = compliance_engine

    evaluated = await middleware._evaluate_with_guardian(
        _DecisionType.MEMORY_ACCESS,
        {"user_id": "user-42", "content": "log"},
        _ExplanationType.STANDARD,
    )

    assert evaluated.allowed is True
    assert evaluated.constitutional_compliant is True
    assert evaluated.constitutional_score == pytest.approx(0.94)
    assert middleware.integration_metrics["compliance_checks"] == 1

    compliance_ctx = evaluated.context["compliance"]
    assert compliance_ctx["overall_compliant"] is True
    assert compliance_ctx["decision_allowed"] is True
    assert compliance_ctx["overall_score"] == pytest.approx(0.94)
