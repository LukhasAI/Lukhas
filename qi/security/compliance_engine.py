"""Compliance engine utilities for the QI security mesh."""

from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional, Sequence

logger = logging.getLogger(__name__)

DEFAULT_COMPLIANCE_FRAMEWORKS: tuple[str, ...] = ("GDPR", "CCPA", "PIPEDA", "LGPD")


@dataclass(slots=True)
class ThreatLandscape:
    """Summary of the current threat landscape for the security mesh."""

    new_quantum_threats_detected: bool = False
    findings: list[str] = field(default_factory=list)


class MultiJurisdictionComplianceEngine:
    """Lightweight compliance engine for multi-framework governance."""

    def __init__(
        self,
        *,
        pqc_engine: Any,
        audit_blockchain: Any,
        frameworks: Optional[Sequence[str]] = None,
    ) -> None:
        deduped: list[str] = []
        seen: set[str] = set()
        for framework in frameworks or DEFAULT_COMPLIANCE_FRAMEWORKS:
            if framework and framework not in seen:
                deduped.append(framework)
                seen.add(framework)

        self.frameworks: tuple[str, ...] = tuple(deduped) if deduped else DEFAULT_COMPLIANCE_FRAMEWORKS
        self.pqc_engine = pqc_engine
        self.audit_blockchain = audit_blockchain

    async def validate_request(self, request: Any) -> bool:
        """Validate a request across consent, integrity, and PQC layers."""

        if getattr(request, "consent_proof", None) is None:
            logger.warning("Rejecting request without consent proof")
            return False

        integrity_checker = getattr(request, "is_integrity_valid", None)
        if callable(integrity_checker):
            integrity_result = integrity_checker()
            if inspect.isawaitable(integrity_result):
                integrity_result = await integrity_result
            if not integrity_result:
                logger.warning("Rejecting request that failed integrity validation")
                return False

        pqc_validator = getattr(self.pqc_engine, "validate_request", None)
        if callable(pqc_validator):
            pqc_result = pqc_validator(request)
            if inspect.isawaitable(pqc_result):
                pqc_result = await pqc_result
            if not pqc_result:
                logger.warning("Rejecting request that failed PQC validation")
                return False

        return True

    async def extract_private_features(self, request: Any, *, preserve_privacy: bool = True) -> dict[str, Any]:
        """Extract privacy-preserving features from the request."""

        extractor = getattr(request, "extract_private_features", None)
        if callable(extractor):
            extracted = extractor(preserve_privacy=preserve_privacy)
            if inspect.isawaitable(extracted):
                extracted = await extracted
            return extracted

        payload = getattr(request, "payload", None)
        features: dict[str, Any]
        if isinstance(payload, Mapping):
            features = dict(payload)
        elif payload is not None:
            features = {"payload": payload}
        else:
            features = {}

        features["privacy_preserved"] = bool(preserve_privacy)
        features["frameworks"] = self.frameworks
        return features

    async def prepare_secure_response(
        self,
        qi_result: Any,
        qi_session: Any,
        *,
        include_telemetry: bool = False,
    ) -> Any:
        """Prepare a compliance-aware secure response payload."""

        response_payload: dict[str, Any] = {
            "decision": getattr(qi_result, "decision", None),
            "context": getattr(qi_result, "context", None),
            "compliance": {
                "frameworks": self.frameworks,
                "audit_reference": getattr(self.audit_blockchain, "chain_id", None),
            },
        }

        if include_telemetry and hasattr(qi_result, "telemetry"):
            response_payload["telemetry"] = getattr(qi_result, "telemetry")

        response_builder = getattr(qi_session, "create_secure_response", None)
        if callable(response_builder):
            built_response = response_builder(response_payload)
            if inspect.isawaitable(built_response):
                built_response = await built_response
            return built_response

        return response_payload

    async def analyze_threat_landscape(self) -> ThreatLandscape:
        """Aggregate threat signals from the PQC engine."""

        findings: list[str] = []
        detector = getattr(self.pqc_engine, "detect_threats", None)
        if callable(detector):
            detected = detector()
            if inspect.isawaitable(detected):
                detected = await detected

            if isinstance(detected, Mapping):
                findings.extend(f"{key}: {value}" for key, value in detected.items())
            elif isinstance(detected, Iterable) and not isinstance(detected, (str, bytes)):
                findings.extend(str(item) for item in detected)
            elif detected:
                findings.append(str(detected))

        return ThreatLandscape(new_quantum_threats_detected=bool(findings), findings=findings)

    async def strengthen_defenses(self) -> None:
        """Invoke available hardening routines on dependent systems."""

        for action_owner in (self.pqc_engine, self.audit_blockchain):
            action = getattr(action_owner, "rotate_keys", None)
            if not callable(action):
                action = getattr(action_owner, "enable_emergency_mode", None)
            if callable(action):
                result = action()
                if inspect.isawaitable(result):
                    await result


__all__ = [
    "DEFAULT_COMPLIANCE_FRAMEWORKS",
    "MultiJurisdictionComplianceEngine",
    "ThreatLandscape",
]
