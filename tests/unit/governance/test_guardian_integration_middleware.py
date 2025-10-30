import asyncio
import sys
import types
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import SimpleNamespace
from typing import Any, Optional

import pytest

if "labs.core.guardian" not in sys.modules:
    guardian_package = types.ModuleType("labs.core.guardian")
    guardian_package.__path__ = []  # type: ignore[attr-defined]
    sys.modules["labs.core.guardian"] = guardian_package
else:  # pragma: no cover - defensive
    guardian_package = sys.modules["labs.core.guardian"]

if "labs.core.guardian.drift_detector" not in sys.modules:
    drift_module = types.ModuleType("labs.core.guardian.drift_detector")

    class _StubDriftSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    class _StubDriftType(Enum):
        DATA = "data"
        CONCEPT = "concept"

    class _StubAdvancedDriftDetector:  # pragma: no cover - placeholder
        async def detect(self, *_args, **_kwargs):
            return None

    drift_module.DriftSeverity = _StubDriftSeverity
    drift_module.DriftType = _StubDriftType
    drift_module.AdvancedDriftDetector = _StubAdvancedDriftDetector
    sys.modules["labs.core.guardian.drift_detector"] = drift_module
    setattr(guardian_package, "drift_detector", drift_module)

if "labs.core.governance.guardian_system_2" not in sys.modules:
    guardian_system_module = types.ModuleType("labs.core.governance.guardian_system_2")

    class DecisionType(Enum):
        USER_INTERACTION = "user_interaction"
        CONTENT_GENERATION = "content_generation"
        DATA_PROCESSING = "data_processing"
        MODEL_INFERENCE = "model_inference"
        SYSTEM_OPERATION = "system_operation"
        API_CALL = "api_call"
        MEMORY_ACCESS = "memory_access"
        EXTERNAL_REQUEST = "external_request"

    class ExplanationType(Enum):
        BRIEF = "brief"
        STANDARD = "standard"
        DETAILED = "detailed"
        TECHNICAL = "technical"
        REGULATORY = "regulatory"

    class SafetyLevel(Enum):
        SAFE = "safe"
        CAUTION = "caution"
        WARNING = "warning"
        DANGER = "danger"
        CRITICAL = "critical"

    @dataclass
    class GuardianDecision:
        decision_id: str
        decision_type: DecisionType
        allowed: bool
        confidence: float
        safety_level: SafetyLevel
        constitutional_compliant: bool
        constitutional_score: float
        drift_score: float
        drift_severity: str
        timestamp: datetime
        processing_time_ms: float
        explanation: str = ""
        explanation_type: ExplanationType = ExplanationType.STANDARD
        violated_principles: list[str] = field(default_factory=list)
        drift_factors: list[str] = field(default_factory=list)
        safety_violations: list[str] = field(default_factory=list)
        risk_factors: list[str] = field(default_factory=list)
        context: dict[str, Any] = field(default_factory=dict)
        identity_impact: Optional[float] = None
        consciousness_impact: Optional[float] = None
        guardian_priority: str = "normal"

    class GuardianSystem2:
        async def evaluate_decision(
            self,
            *,
            decision_type: DecisionType,
            decision_data: dict[str, Any],
            context: dict[str, Any],
            user_id: Optional[str],
            explanation_type: ExplanationType,
        ) -> GuardianDecision:
            return GuardianDecision(
                decision_id="stub",
                decision_type=decision_type,
                allowed=True,
                confidence=0.5,
                safety_level=SafetyLevel.CAUTION,
                constitutional_compliant=True,
                constitutional_score=0.5,
                drift_score=0.0,
                drift_severity="low",
                timestamp=datetime.now(timezone.utc),
                processing_time_ms=1.0,
            )

    def get_guardian_system() -> GuardianSystem2:
        return GuardianSystem2()

    guardian_system_module.DecisionType = DecisionType
    guardian_system_module.ExplanationType = ExplanationType
    guardian_system_module.GuardianDecision = GuardianDecision
    guardian_system_module.GuardianSystem2 = GuardianSystem2
    guardian_system_module.SafetyLevel = SafetyLevel
    guardian_system_module.get_guardian_system = get_guardian_system
    sys.modules["labs.core.governance.guardian_system_2"] = guardian_system_module

from labs.core.governance.constitutional_ai import DecisionContext, ViolationSeverity
from labs.core.governance.guardian_integration import (
    GuardianIntegrationMiddleware,
    IntegrationConfig,
)
from labs.core.governance.guardian_system_2 import DecisionType, SafetyLevel


class _DummyGuardianSystem:
    def __init__(self):
        self.calls: list[dict] = []

    async def evaluate_decision(self, *, decision_type, decision_data, context, user_id, explanation_type):
        self.calls.append(
            {
                "decision_type": decision_type,
                "decision_data": decision_data,
                "context": context,
                "user_id": user_id,
                "explanation_type": explanation_type,
            }
        )
        return SimpleNamespace(
            decision_id="allow_123",
            decision_type=decision_type,
            allowed=True,
            confidence=0.95,
            safety_level=SafetyLevel.SAFE,
            constitutional_compliant=True,
            constitutional_score=1.0,
            drift_score=0.01,
            drift_severity="low",
            timestamp=datetime.now(timezone.utc),
            processing_time_ms=5.0,
            explanation="Guardian approval",
            context={"source": "dummy"},
        )


class _BlockingGuardianSystem:
    async def evaluate_decision(self, *_, **__):  # pragma: no cover - safety net
        raise AssertionError("Guardian system should not be invoked when compliance blocks")


class _DeniedComplianceResult:
    decision_allowed = False
    overall_compliant = False
    overall_compliance_score = 0.1
    confidence_in_decision = 0.2
    compliance_explanation = "Constitutional violation detected"
    violation_summary = "High risk content"
    required_actions = ["block_decision"]
    max_risk_level = ViolationSeverity.CRITICAL
    total_processing_time_ms = 12.5
    principle_checks = {}


class _AllowedComplianceResult:
    decision_allowed = True
    overall_compliant = True
    overall_compliance_score = 0.92
    confidence_in_decision = 0.93
    compliance_explanation = "Constitutional review passed"
    violation_summary = ""
    required_actions: list[str] = ["request_human_review"]
    max_risk_level = ViolationSeverity.LOW
    total_processing_time_ms = 6.0
    principle_checks = {}


@pytest.fixture(autouse=True)
def _patch_async_initialization(monkeypatch):
    async def _noop_initialize(self):
        return None

    monkeypatch.setattr(
        GuardianIntegrationMiddleware,
        "_initialize_integration",
        _noop_initialize,
    )


@pytest.mark.asyncio
async def test_guardian_monitor_blocks_when_compliance_denies(monkeypatch):
    middleware = GuardianIntegrationMiddleware(IntegrationConfig())
    middleware.guardian_system = _BlockingGuardianSystem()

    captured_contexts: list[DecisionContext] = []

    class _ComplianceEngine:
        async def check_constitutional_compliance(self, decision_context, decision_data, user_id=None):
            captured_contexts.append(decision_context)
            return _DeniedComplianceResult()

    middleware.compliance_engine = _ComplianceEngine()

    @middleware.guardian_monitor(decision_type=DecisionType.USER_INTERACTION)
    async def guarded(user_input: str, user_id: str):
        return "should not run"

    result = await guarded("dangerous instruction", user_id="user-123")

    assert result is None
    assert middleware.integration_metrics["decisions_blocked"] == 1
    assert captured_contexts == [DecisionContext.USER_INTERACTION]


@pytest.mark.asyncio
async def test_guardian_monitor_includes_compliance_metadata_when_allowed():
    middleware = GuardianIntegrationMiddleware(IntegrationConfig())
    guardian_system = _DummyGuardianSystem()
    middleware.guardian_system = guardian_system

    class _ComplianceEngine:
        async def check_constitutional_compliance(self, decision_context, decision_data, user_id=None):
            return _AllowedComplianceResult()

    middleware.compliance_engine = _ComplianceEngine()

    @middleware.guardian_monitor(decision_type=DecisionType.CONTENT_GENERATION)
    async def generate_content(content: str):
        return f"Processed: {content}"

    output = await generate_content("hello")

    assert output == "Processed: hello"
    assert middleware.integration_metrics["decisions_allowed"] == 1
    assert guardian_system.calls, "Guardian system should receive evaluation request"
    decision_payload = guardian_system.calls[0]["decision_data"]
    compliance_data = decision_payload.get("constitutional_compliance")
    assert compliance_data and compliance_data["allowed"] is True
    assert compliance_data["score"] == pytest.approx(_AllowedComplianceResult.overall_compliance_score)
    assert compliance_data["required_actions"] == _AllowedComplianceResult.required_actions
    assert compliance_data["explanation"] == _AllowedComplianceResult.compliance_explanation
    assert compliance_data["confidence"] == pytest.approx(_AllowedComplianceResult.confidence_in_decision)
    assert compliance_data["required_actions"] == _AllowedComplianceResult.required_actions
    assert compliance_data["explanation"] == _AllowedComplianceResult.compliance_explanation
    assert compliance_data["confidence"] == pytest.approx(_AllowedComplianceResult.confidence_in_decision)


@pytest.mark.asyncio
async def test_guardian_monitor_uses_constitutional_framework_fallback(monkeypatch):
    middleware = GuardianIntegrationMiddleware(IntegrationConfig())
    middleware.guardian_system = _BlockingGuardianSystem()
    middleware.compliance_engine = None

    violation = SimpleNamespace(
        principle=SimpleNamespace(value="non_maleficence"),
        severity=ViolationSeverity.HIGH,
        details={"description": "Potential harm detected"},
    )

    class _Framework:
        async def evaluate_decision(self, decision_context, decision_data, user_id=None):
            return False, [violation]

    middleware.constitutional_framework = _Framework()

    @middleware.guardian_monitor(decision_type=DecisionType.DATA_PROCESSING)
    async def process_data(data: str):
        return data.upper()

    outcome = await process_data("sensitive payload")

    assert outcome is None
    assert middleware.integration_metrics["decisions_blocked"] >= 1
