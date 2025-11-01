from dataclasses import dataclass

import pytest

from qi.security import (
    DEFAULT_COMPLIANCE_FRAMEWORKS,
    MultiJurisdictionComplianceEngine,
    ThreatLandscape,
)


@dataclass
class DummyRequest:
    consent_proof: object | None
    integrity_valid: bool = True

    def is_integrity_valid(self) -> bool:
        return self.integrity_valid


class DummyPQC:
    def __init__(self) -> None:
        self.validated = []
        self.rotations = 0
        self.threats: list[str] = []

    def validate_request(self, request: DummyRequest) -> bool:
        self.validated.append(request)
        return request.integrity_valid

    def detect_threats(self) -> list[str]:
        return list(self.threats)

    def rotate_keys(self) -> None:
        self.rotations += 1


class DummyAuditBlockchain:
    def __init__(self) -> None:
        self.chain_id = "audit-chain"
        self.emergency_mode = False

    def enable_emergency_mode(self) -> None:
        self.emergency_mode = True


class DummySession:
    def __init__(self) -> None:
        self.received_payloads = []

    def create_secure_response(self, payload: dict) -> dict:
        self.received_payloads.append(payload)
        return {"wrapped": payload}


class DummyResult:
    def __init__(self) -> None:
        self.decision = "approve"
        self.context = {"key": "value"}
        self.telemetry = {"latency_ms": 12}


@pytest.mark.asyncio
async def test_validate_request_enforces_consent_and_integrity() -> None:
    pqc = DummyPQC()
    audit = DummyAuditBlockchain()
    engine = MultiJurisdictionComplianceEngine(pqc_engine=pqc, audit_blockchain=audit)

    valid_request = DummyRequest(consent_proof="zk-proof")
    assert await engine.validate_request(valid_request) is True
    assert pqc.validated == [valid_request]

    missing_consent = DummyRequest(consent_proof=None)
    assert await engine.validate_request(missing_consent) is False

    failing_integrity = DummyRequest(consent_proof="zk-proof", integrity_valid=False)
    assert await engine.validate_request(failing_integrity) is False


@pytest.mark.asyncio
async def test_extract_private_features_falls_back_to_payload() -> None:
    engine = MultiJurisdictionComplianceEngine(pqc_engine=DummyPQC(), audit_blockchain=DummyAuditBlockchain())
    request = DummyRequest(consent_proof="zk-proof")
    request.payload = {"region": "eu"}

    features = await engine.extract_private_features(request)

    assert features["region"] == "eu"
    assert features["privacy_preserved"] is True
    assert tuple(features["frameworks"]) == DEFAULT_COMPLIANCE_FRAMEWORKS


@pytest.mark.asyncio
async def test_prepare_secure_response_wraps_payload_when_builder_available() -> None:
    engine = MultiJurisdictionComplianceEngine(pqc_engine=DummyPQC(), audit_blockchain=DummyAuditBlockchain())
    session = DummySession()
    result = DummyResult()

    response = await engine.prepare_secure_response(result, session, include_telemetry=True)

    assert "wrapped" in response
    assert response["wrapped"]["telemetry"] == result.telemetry
    assert session.received_payloads[0]["compliance"]["frameworks"] == DEFAULT_COMPLIANCE_FRAMEWORKS


@pytest.mark.asyncio
async def test_analyze_and_strengthen_defenses_reports_findings() -> None:
    pqc = DummyPQC()
    pqc.threats = ["kyber downgrade"]
    audit = DummyAuditBlockchain()
    engine = MultiJurisdictionComplianceEngine(pqc_engine=pqc, audit_blockchain=audit)

    landscape = await engine.analyze_threat_landscape()
    assert isinstance(landscape, ThreatLandscape)
    assert landscape.new_quantum_threats_detected is True
    assert landscape.findings == ["kyber downgrade"]

    await engine.strengthen_defenses()
    assert pqc.rotations == 1
    assert audit.emergency_mode is True
