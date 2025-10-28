from dataclasses import dataclass
from pathlib import Path
import importlib.util
import sys

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[2] / "qi" / "privacy" / "zero_knowledge_system.py"
_SPEC = importlib.util.spec_from_file_location("qi.privacy.zero_knowledge_system", _MODULE_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
assert _SPEC.loader is not None  # for type checkers
_SPEC.loader.exec_module(_MODULE)

BulletProof = _MODULE.BulletProof
Computation = _MODULE.Computation
PrivateWitness = _MODULE.PrivateWitness
ProofStatement = _MODULE.ProofStatement
ZeroKnowledgePrivacyEngine = _MODULE.ZeroKnowledgePrivacyEngine


@dataclass
class _DummyRequest:
    payload: dict
    integrity_signature: str = "signature"
    metadata: dict = None


@dataclass
class _DummyResult:
    decision: str
    context: dict
    telemetry: dict


@dataclass
class _DummySession:
    session_id: str


class _AsyncValidationPQC:
    def __init__(self) -> None:
        self.calls = 0

    async def validate_request(self, request) -> bool:  # pragma: no cover - exercised in async test
        self.calls += 1
        return True


@pytest.mark.asyncio
async def test_adaptive_proof_prefers_zksnark_for_small_circuits():
    engine = ZeroKnowledgePrivacyEngine()
    statement = ProofStatement(public_input={"balance": 42}, requires_non_interactive=True, circuit_size=512)
    witness = PrivateWitness(values={"secret": "value"})

    proof = await engine.create_privacy_preserving_proof(statement, witness)

    assert proof.scheme == "zksnark"
    expected_hash = ZeroKnowledgePrivacyEngine.compute_witness_fingerprint(witness.values)
    assert proof.proof_data["witness_hash"] == expected_hash


@pytest.mark.asyncio
async def test_verify_private_computation_matches_expected_hash():
    engine = ZeroKnowledgePrivacyEngine()
    statement = ProofStatement(public_input={"balance": 7}, requires_non_interactive=False, circuit_size=4096)
    witness = PrivateWitness(values={"range": (0, 10)})

    proof = await engine.create_privacy_preserving_proof(statement, witness, proof_type="bulletproof")
    assert isinstance(proof, BulletProof)

    expected_hash = ZeroKnowledgePrivacyEngine.compute_witness_fingerprint(witness.values)
    computation = Computation(public_input=statement.public_input, expected_witness_hash=expected_hash)

    assert await engine.verify_private_computation({"balance": 7}, proof, computation)


@pytest.mark.asyncio
async def test_validate_request_uses_pqc_engine():
    pqc = _AsyncValidationPQC()
    engine = ZeroKnowledgePrivacyEngine(pqc_engine=pqc)
    request = _DummyRequest(payload={"user": "alice"})

    assert await engine.validate_request(request)
    assert pqc.calls == 1


@pytest.mark.asyncio
async def test_extract_private_features_masks_sensitive_keys():
    engine = ZeroKnowledgePrivacyEngine()
    request = _DummyRequest(payload={"user": "alice", "secret_token": "redacted"}, metadata={"trace": "123"})

    features = await engine.extract_private_features(request)

    assert "secret_token" not in features["features"]
    assert features["features"]["user"] == "alice"
    assert features["metadata"]["privacy_preserved"] is True
    assert features["metadata"]["trace"] == "123"


@pytest.mark.asyncio
async def test_prepare_secure_response_includes_session_and_telemetry():
    engine = ZeroKnowledgePrivacyEngine()
    result = _DummyResult(decision="allow", context={"score": 0.91}, telemetry={"latency": 12})
    session = _DummySession(session_id="session-1")

    response = await engine.prepare_secure_response(result, session)

    assert response["decision"] == "allow"
    assert response["context"]["score"] == 0.91
    assert response["session_id"] == "session-1"
    assert response["metadata"]["defense_level"] == 0
    assert response["telemetry"]["latency"] == 12


@pytest.mark.asyncio
async def test_analyze_threat_landscape_reacts_to_defense_level():
    engine = ZeroKnowledgePrivacyEngine(threat_window=2)

    first = await engine.analyze_threat_landscape()
    assert first.new_quantum_threats_detected is False

    second = await engine.analyze_threat_landscape()
    assert second.new_quantum_threats_detected is True

    await engine.strengthen_defenses()
    third = await engine.analyze_threat_landscape()
    assert third.new_quantum_threats_detected is False
