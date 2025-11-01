from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AuthenticationTier(Enum):
    """Simplified authentication tiers used in tests."""

    T1_BASIC = "T1_BASIC"
    T2_ENHANCED = "T2_ENHANCED"
    T3_CONSCIOUSNESS = "T3_CONSCIOUSNESS"
    T4_QUANTUM = "T4_QUANTUM"
    T5_TRANSCENDENT = "T5_TRANSCENDENT"


class IdentitySignalType(Enum):
    """Subset of identity signal types used in production module."""

    AUTHENTICATION_REQUEST = "AUTHENTICATION_REQUEST"
    AUTHENTICATION_SUCCESS = "AUTHENTICATION_SUCCESS"
    CONSTITUTIONAL_COMPLIANCE = "CONSTITUTIONAL_COMPLIANCE"


@dataclass
class IdentityBiometricData:
    """Minimal biometric payload for tests."""

    confidence_score: float = 0.0
    behavioral_coherence: float = 0.0
    consciousness_frequency: float = 0.0
    brainwave_pattern: Dict[str, float] = field(default_factory=dict)


@dataclass
class NamespaceIsolationData:
    """Placeholder namespace isolation payload."""

    namespace_id: str = ""
    isolation_level: float = 1.0
    permissions: List[str] = field(default_factory=list)


@dataclass
class ConstitutionalComplianceData:
    """Compliance payload emitted by the signal emitter."""

    democratic_validation: bool = True
    human_oversight_required: bool = False
    transparency_score: float = 1.0
    fairness_score: float = 1.0
    constitutional_aligned: bool = True


@dataclass
class _IdentitySignal:
    """Simple signal object returned to tests."""

    consciousness_id: str
    tier: AuthenticationTier
    validation_passed: bool
    signal_integrity_hash: str
    bio_symbolic_data: Optional[IdentityBiometricData] = None
    constellation_compliance: Optional[Dict[str, Any]] = None


class MatrizConsciousnessIdentitySignalEmitter:
    """Lightweight signal emitter used for unit tests."""

    def __init__(self) -> None:
        self.signal_factory = object()  # Truthy sentinel for tests
        self._lock = asyncio.Lock()
        self._emitted_signals: List[_IdentitySignal] = []
        self._constitutional_signals: List[tuple[str, ConstitutionalComplianceData, dict[str, Any]]] = []
        self._metrics = {
            "signals_emitted": 0,
            "authentication_signals": 0,
            "compliance_signals": 0,
        }

    async def emit_authentication_request_signal(
        self,
        identity_id: str,
        authentication_tier: AuthenticationTier,
        biometric_data: Optional[IdentityBiometricData] = None,
        namespace_data: Optional[NamespaceIsolationData] = None,
    ) -> _IdentitySignal:
        async with self._lock:
            signal = _IdentitySignal(
                consciousness_id=identity_id,
                tier=authentication_tier,
                validation_passed=True,
                signal_integrity_hash=f"sig-{identity_id}-{authentication_tier.value}",
                bio_symbolic_data=biometric_data,
                constellation_compliance={
                    "namespace": namespace_data.namespace_id if namespace_data else None,
                    "permissions": namespace_data.permissions if namespace_data else [],
                },
            )
            self._register_signal(signal)
            return signal

    async def emit_authentication_success_signal(
        self,
        identity_id: str,
        authentication_tier: AuthenticationTier,
        identity_strength: float,
        consciousness_coherence: float,
        biometric_confidence: float,
    ) -> _IdentitySignal:
        async with self._lock:
            signal = _IdentitySignal(
                consciousness_id=identity_id,
                tier=authentication_tier,
                validation_passed=True,
                signal_integrity_hash=f"success-{identity_id}-{authentication_tier.value}",
                bio_symbolic_data=IdentityBiometricData(
                    confidence_score=biometric_confidence,
                    behavioral_coherence=consciousness_coherence,
                ),
                constellation_compliance={"identity_strength": identity_strength},
            )
            self._register_signal(signal)
            return signal

    async def emit_constitutional_compliance_signal(
        self,
        identity_id: str,
        compliance_data: ConstitutionalComplianceData,
        decision_payload: dict[str, Any],
    ) -> None:
        async with self._lock:
            self._constitutional_signals.append((identity_id, compliance_data, decision_payload))
            self._metrics["signals_emitted"] += 1
            self._metrics["compliance_signals"] += 1

    async def get_emission_metrics(self) -> dict[str, Any]:
        async with self._lock:
            return {
                "performance_metrics": {
                    "signals_emitted": self._metrics["signals_emitted"],
                    "authentication_signals": self._metrics["authentication_signals"],
                    "compliance_signals": self._metrics["compliance_signals"],
                },
                "emitted_signals_count": len(self._emitted_signals),
            }

    async def get_constitutional_signals(self) -> List[tuple[str, ConstitutionalComplianceData, dict[str, Any]]]:
        async with self._lock:
            return list(self._constitutional_signals)

    def _register_signal(self, signal: _IdentitySignal) -> None:
        self._emitted_signals.append(signal)
        self._metrics["signals_emitted"] += 1
        self._metrics["authentication_signals"] += 1


consciousness_identity_signal_emitter = MatrizConsciousnessIdentitySignalEmitter()


__all__ = [
    "AuthenticationTier",
    "IdentitySignalType",
    "IdentityBiometricData",
    "NamespaceIsolationData",
    "ConstitutionalComplianceData",
    "MatrizConsciousnessIdentitySignalEmitter",
    "consciousness_identity_signal_emitter",
]
