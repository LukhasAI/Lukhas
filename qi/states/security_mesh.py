"""Security mesh implementation for the quantum system orchestrator."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

logger = logging.getLogger(__name__)

_DEFAULT_SENSITIVE_KEYWORDS: tuple[str, ...] = (
    "pii_",
    "secret",
    "password",
    "token",
    "credential",
    "private",
    "ssn",
)


@dataclass(slots=True)
class SecurityMeshThreatLandscape:
    """Summary of the current quantum security threat landscape."""

    new_quantum_threats_detected: bool
    risk_score: float
    alerts: list[dict[str, Any]] = field(default_factory=list)


class SecurityMesh:
    """Post-quantum security coordination layer for the QI orchestrator."""

    def __init__(
        self,
        *,
        pqc_engine: Any,
        audit_blockchain: Any,
        integrity_threshold: float = 0.8,
        risk_threshold: float = 0.75,
        sensitive_keywords: Iterable[str] | None = None,
    ) -> None:
        self.pqc_engine = pqc_engine
        self.audit_blockchain = audit_blockchain
        self.integrity_threshold = integrity_threshold
        self.risk_threshold = risk_threshold
        self._sensitive_keywords = tuple(sensitive_keywords or _DEFAULT_SENSITIVE_KEYWORDS)
        self._alerts: list[dict[str, Any]] = []

    async def validate_request(self, request: Any) -> bool:
        """Validate an incoming request using quantum-era security heuristics."""

        normalized = self._to_mapping(request)
        if not normalized:
            self._record_alert("empty_request", normalized, 1.0, "request payload missing")
            return False

        risk_score = self._coerce_float(normalized.get("risk_score", 0.0))
        integrity_score = self._coerce_float(
            normalized.get("integrity_score", normalized.get("integrity", 1.0))
        )

        if risk_score > self.risk_threshold:
            self._record_alert(
                "risk_threshold_exceeded",
                normalized,
                risk_score,
                "risk score above configured threshold",
            )
            return False

        if integrity_score < self.integrity_threshold:
            self._record_alert(
                "low_integrity",
                normalized,
                max(1.0 - integrity_score, risk_score),
                "integrity score below threshold",
            )
            return False

        consent_proof = normalized.get("consent_proof") or normalized.get("consent")
        if not consent_proof:
            self._record_alert(
                "missing_consent",
                normalized,
                1.0,
                "request missing consent proof",
            )
            return False

        signature = normalized.get("signature") or normalized.get("signature_proof")
        if not signature:
            self._record_alert(
                "missing_signature",
                normalized,
                1.0,
                "request missing cryptographic signature",
            )
            return False

        logger.debug("SecurityMesh validated request successfully", extra={"request_id": normalized.get("request_id")})
        return True

    async def extract_private_features(self, request: Any, *, preserve_privacy: bool = True) -> dict[str, Any]:
        """Extract features while filtering sensitive fields."""

        normalized = self._to_mapping(request)
        features = normalized.get("features") or normalized.get("data") or {}
        features_map = self._to_mapping(features)

        if not preserve_privacy:
            return dict(features_map)

        sanitized: dict[str, Any] = {}
        for key, value in features_map.items():
            if self._is_sensitive_key(key):
                continue
            sanitized[key] = value
        return sanitized

    async def prepare_secure_response(
        self,
        qi_result: Any,
        qi_session: Any,
        *,
        include_telemetry: bool = True,
    ) -> dict[str, Any]:
        """Assemble a secure response payload for the caller."""

        result_data = self._to_mapping(qi_result)
        session_data = self._to_mapping(qi_session)

        response: dict[str, Any] = {
            "decision": result_data.get("decision"),
            "confidence": result_data.get("confidence"),
            "payload": result_data.get("payload") or result_data.get("data"),
            "session": {
                "id": session_data.get("session_id"),
                "security_level": session_data.get("security_level"),
            },
            "metadata": {
                "quantum_security": {
                    "integrity_threshold": self.integrity_threshold,
                    "risk_threshold": self.risk_threshold,
                    "hybrid_mode": getattr(self.pqc_engine, "hybrid_mode", None),
                },
                "audit_enabled": hasattr(self.audit_blockchain, "log_ai_decision"),
            },
        }

        if include_telemetry:
            telemetry = {
                "consent_verified": bool(result_data.get("consent_proof")),
                "audit_ready": True,
            }
            extra_telemetry = result_data.get("telemetry")
            if extra_telemetry:
                telemetry.update(self._to_mapping(extra_telemetry))
            response["telemetry"] = telemetry

        return response

    async def analyze_threat_landscape(self) -> SecurityMeshThreatLandscape:
        """Summarize recorded alerts into a threat landscape report."""

        if not self._alerts:
            return SecurityMeshThreatLandscape(False, 0.0, [])

        highest_risk = max(alert["risk_score"] for alert in self._alerts)
        return SecurityMeshThreatLandscape(True, highest_risk, list(self._alerts))

    async def strengthen_defenses(self) -> SecurityMeshThreatLandscape:
        """Clear accumulated alerts and trigger optional PQC safeguards."""

        scheduler = getattr(self.pqc_engine, "key_rotation_scheduler", None)
        trigger = getattr(scheduler, "trigger_immediate_rotation", None)
        if callable(trigger):
            result = trigger()
            if asyncio.iscoroutine(result):
                await result

        self._alerts.clear()
        return SecurityMeshThreatLandscape(False, 0.0, [])

    def _record_alert(
        self,
        alert_type: str,
        normalized_request: Mapping[str, Any],
        risk_score: float,
        reason: str,
    ) -> None:
        alert = {
            "type": alert_type,
            "risk_score": float(risk_score),
            "reason": reason,
            "request_id": normalized_request.get("request_id"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._alerts.append(alert)
        logger.warning("SecurityMesh alert", extra=alert)

    def _to_mapping(self, payload: Any) -> dict[str, Any]:
        if payload is None:
            return {}
        if isinstance(payload, Mapping):
            return dict(payload)
        if hasattr(payload, "model_dump"):
            try:
                data = payload.model_dump()
                if isinstance(data, Mapping):
                    return dict(data)
            except TypeError:
                pass
        if hasattr(payload, "dict"):
            try:
                data = payload.dict()
                if isinstance(data, Mapping):
                    return dict(data)
            except TypeError:
                pass
        if hasattr(payload, "__dict__"):
            return dict(vars(payload))
        return {}

    def _is_sensitive_key(self, key: str) -> bool:
        lowered = key.lower()
        return any(keyword in lowered for keyword in self._sensitive_keywords)

    @staticmethod
    def _coerce_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
