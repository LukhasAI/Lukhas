import asyncio
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import importlib.util

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TESTS_UNIT_PATH = Path(__file__).resolve().parents[1]
TESTS_PATH = Path(__file__).resolve().parents[2]
for path in (TESTS_UNIT_PATH, TESTS_PATH):
    if str(path) in sys.path:
        sys.path.remove(str(path))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SECURITY_MESH_PATH = PROJECT_ROOT / "qi" / "states" / "security_mesh.py"
spec = importlib.util.spec_from_file_location("qi.states.security_mesh", SECURITY_MESH_PATH)
security_mesh_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader  # safety for mypy/pyright
sys.modules.setdefault("qi", types.ModuleType("qi"))
sys.modules[spec.name] = security_mesh_module
spec.loader.exec_module(security_mesh_module)

SecurityMesh = security_mesh_module.SecurityMesh
SecurityMeshThreatLandscape = security_mesh_module.SecurityMeshThreatLandscape


class _DummyPQC:
    def __init__(self) -> None:
        self.hybrid_mode = True
        self.key_rotation_scheduler = SimpleNamespace(trigger_immediate_rotation=self._trigger)
        self._rotation_triggered = asyncio.Event()

    async def _trigger(self) -> None:
        self._rotation_triggered.set()


class _DummyAudit:
    async def log_ai_decision(self, *args, **kwargs):  # pragma: no cover - not exercised in unit tests
        raise NotImplementedError


@pytest.fixture
def security_mesh() -> SecurityMesh:
    return SecurityMesh(pqc_engine=_DummyPQC(), audit_blockchain=_DummyAudit())


@pytest.mark.asyncio
async def test_validate_request_success(security_mesh: SecurityMesh) -> None:
    request = {
        "request_id": "req-1",
        "risk_score": 0.2,
        "integrity_score": 0.95,
        "consent_proof": {"zk": "proof"},
        "signature": "sig",
    }

    assert await security_mesh.validate_request(request) is True


@pytest.mark.asyncio
async def test_validate_request_flags_high_risk(security_mesh: SecurityMesh) -> None:
    request = {
        "request_id": "req-2",
        "risk_score": 0.99,
        "integrity_score": 0.95,
        "consent_proof": {"zk": "proof"},
        "signature": "sig",
    }

    assert await security_mesh.validate_request(request) is False

    landscape = await security_mesh.analyze_threat_landscape()
    assert landscape.new_quantum_threats_detected is True
    assert pytest.approx(0.99, rel=1e-6) == landscape.risk_score
    assert landscape.alerts[0]["type"] == "risk_threshold_exceeded"

    await security_mesh.strengthen_defenses()
    post_landscape = await security_mesh.analyze_threat_landscape()
    assert post_landscape == SecurityMeshThreatLandscape(False, 0.0, [])
    assert security_mesh.pqc_engine._rotation_triggered.is_set()


@pytest.mark.asyncio
async def test_extract_private_features_filters_sensitive_data(security_mesh: SecurityMesh) -> None:
    request = {
        "features": {
            "pii_email": "user@example.com",
            "context": "public",
            "secret_token": "token",
            "score": 0.75,
        }
    }

    features = await security_mesh.extract_private_features(request)
    assert "context" in features and "score" in features
    assert "pii_email" not in features
    assert "secret_token" not in features


@pytest.mark.asyncio
async def test_prepare_secure_response_combines_result_and_session(security_mesh: SecurityMesh) -> None:
    qi_result = SimpleNamespace(
        decision="allow",
        confidence=0.88,
        payload={"message": "ok"},
        consent_proof={"zk": "proof"},
        telemetry={"latency_ms": 10},
    )
    qi_session = SimpleNamespace(session_id="sess-1", security_level="NIST-5")

    response = await security_mesh.prepare_secure_response(qi_result, qi_session)

    assert response["decision"] == "allow"
    assert response["session"]["id"] == "sess-1"
    assert response["metadata"]["quantum_security"]["hybrid_mode"] is True
    assert response["telemetry"]["consent_verified"] is True
    assert response["telemetry"]["latency_ms"] == 10
