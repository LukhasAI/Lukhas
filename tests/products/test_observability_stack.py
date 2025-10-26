import asyncio

import pytest
from products.enterprise.core.observability.t4_observability_stack import T4ObservabilityStack


class TrinityStub:
    def __init__(self):
        self.coherence = 0.92

    async def get_performance_metrics(self):
        await asyncio.sleep(0)
        return {"coherence": 0.92, "active_sessions": 4}


class ConsciousnessStub:
    def __init__(self):
        self.runtime_state = {"awakening": 3}
        self.drift_score = 0.12


class MemoryStub:
    async def get_statistics(self):
        return {"active_folds": 5}


class GuardianStub:
    open_incidents = 1
    affect_delta = -0.02


@pytest.mark.asyncio
async def test_harvest_component_metrics(tmp_path):
    stack = T4ObservabilityStack(datadog_enabled=False, prometheus_enabled=False, opentelemetry_enabled=False)
    output_path = tmp_path / "metrics.json"

    report = await stack.harvest_component_metrics(
        trinity=TrinityStub(),
        consciousness=ConsciousnessStub(),
        memory=MemoryStub(),
        guardian=GuardianStub(),
        output_path=output_path,
    )

    assert "timestamp" in report
    assert report["trinity"]["coherence"] == pytest.approx(0.92, rel=1e-6)
    assert report["guardian"]["affect_delta"] == -0.02
    assert output_path.exists()
