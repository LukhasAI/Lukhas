"""Bridge for candidate.consciousness.guardian_integration."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from importlib import import_module
from typing import Any, Dict, List, Optional

__all__: List[str] = []

for _candidate in (
    "labs.candidate.consciousness.guardian_integration",
    "lukhas_website.lukhas.consciousness.guardian_integration",
    "consciousness.guardian_integration",
):
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    for _attr in dir(_mod):
        if _attr.startswith("_"):
            continue
        globals()[_attr] = getattr(_mod, _attr)
        if _attr not in __all__:
            __all__.append(_attr)
    break


if "ConsciousnessGuardianIntegration" not in globals():

    class ConsciousnessGuardianIntegration:
        """Fallback guardian integration for candidate namespace."""

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        async def ensure_guardian_alignment(self, *args, **kwargs):
            return {"aligned": True}

    __all__.append("ConsciousnessGuardianIntegration")


if "GuardianValidationType" not in globals():

    class GuardianValidationType(Enum):
        CONSCIOUSNESS_STATE_TRANSITION = "consciousness_state_transition"
        REFLECTION_ANALYSIS = "reflection_analysis"
        CREATIVE_GENERATION = "creative_generation"
        SAFETY_CHECK = "safety_check"

    __all__.append("GuardianValidationType")


if "ValidationResult" not in globals():

    class ValidationResult(Enum):
        APPROVED = "approved"
        DENIED = "denied"

    __all__.append("ValidationResult")


if "GuardianValidationConfig" not in globals():

    @dataclass
    class GuardianValidationConfig:
        p95_target_ms: float = 200.0
        p99_target_ms: float = 250.0
        drift_threshold: float = 0.15
        drift_alpha: float = 0.3
        fail_closed_on_error: bool = True
        gdpr_audit_enabled: bool = True
        guardian_active: bool = True
        timeout_ms: float = 250.0

        def validate(self) -> List[str]:
            errors: List[str] = []
            if self.p95_target_ms <= 0:
                errors.append("p95_target_ms must be positive")
            if not 0 <= self.drift_threshold <= 1:
                errors.append("drift_threshold must be between 0 and 1")
            if not 0 <= self.drift_alpha <= 1:
                errors.append("drift_alpha must be between 0 and 1")
            if self.timeout_ms < self.p99_target_ms:
                errors.append("timeout_ms should be >= p99_target_ms")
            return errors

    __all__.append("GuardianValidationConfig")


if "GuardianValidationResult" not in globals():

    @dataclass
    class GuardianValidationResult:
        operation_id: str
        validation_type: GuardianValidationType
        result: ValidationResult
        reason: str = ""
        confidence: float = 1.0
        validation_duration_ms: float = 0.0
        audit_trail: List[Dict[str, Any]] = field(default_factory=list)

        def is_approved(self) -> bool:
            return self.result == ValidationResult.APPROVED

        def add_audit_entry(self, event_type: str, details: Dict[str, Any]) -> None:
            self.audit_trail.append({
                "event_type": event_type,
                "details": details,
                "operation_id": self.operation_id,
            })

    __all__.append("GuardianValidationResult")


if "ConsciousnessValidationContext" not in globals():

    @dataclass
    class ConsciousnessValidationContext:
        validation_type: GuardianValidationType = GuardianValidationType.CONSCIOUSNESS_STATE_TRANSITION
        tenant: str = "default"
        lane: str = "consciousness"
        sensitive_operation: bool = False
        risk_indicators: List[str] = field(default_factory=list)
        operation_id: str = field(default_factory=lambda: f"op-{uuid.uuid4().hex[:12]}")
        correlation_id: str = field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:12]}")
        consciousness_state: Any = None
        user_id: Optional[str] = None
        session_id: Optional[str] = None

    __all__.append("ConsciousnessValidationContext")


if "create_validation_context" not in globals():

    def create_validation_context(
        validation_type: GuardianValidationType,
        consciousness_state: Any = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        sensitive_operation: bool = False,
        tenant: str = "default",
    ) -> ConsciousnessValidationContext:
        return ConsciousnessValidationContext(
            validation_type=validation_type,
            consciousness_state=consciousness_state,
            user_id=user_id,
            session_id=session_id,
            sensitive_operation=sensitive_operation,
            tenant=tenant,
        )

    __all__.append("create_validation_context")
