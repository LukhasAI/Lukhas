import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from products.infrastructure.legado.legacy_systems.governor.lambda_governor import (
    EscalationPriority,
    EscalationSignal,
    EscalationSource,
    LambdaGovernor,
)

path_obj = Path(__file__).resolve()
tests_unit_path = str(path_obj.parents[2])
if tests_unit_path in sys.path:
    sys.path.remove(tests_unit_path)

sys.path.insert(0, str(path_obj.parents[4]))



class _DeterministicRouter:
    def __init__(self, router_id: str) -> None:
        self.router_id = router_id
        self.calls: list[tuple[dict, str]] = []

    async def verify_arbitration(self, payload: dict, collapse_hash: str) -> bool:
        self.calls.append((payload, collapse_hash))
        return True


@pytest.mark.asyncio
async def test_lambda_governor_generates_quantum_safe_record(monkeypatch):
    monkeypatch.setattr(
        "products.infrastructure.legado.legacy_systems.governor.lambda_governor.logger",
        MagicMock(),
    )

    governor = LambdaGovernor()
    router = _DeterministicRouter("router-1")
    governor.mesh_routers.append(router)

    signal = EscalationSignal(
        signal_id="SIG-001",
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_module=EscalationSource.DRIFT_SENTINEL,
        priority=EscalationPriority.HIGH,
        triggering_metric="drift_score",
        drift_score=0.82,
        entropy=0.21,
        emotion_volatility=0.18,
        contradiction_density=0.14,
        memory_ids=["mem-alpha"],
        symbol_ids=["sym-alpha"],
        context={"drift_score": 0.82, "entropy": 0.21},
    )

    response = await governor.receive_escalation(signal)

    assert response.quantum_record is not None
    record = response.quantum_record
    assert record.quorum_achieved is True
    assert record.collapse_hash
    assert "router-1" in record.verifying_nodes
    assert len(governor.quantum_mesh_history) == 1
    assert router.calls, "Expected verification router to receive payload"
