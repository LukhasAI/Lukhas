import pytest

from candidate.flags.ff import Flags
from candidate.core.quantum_financial.quantum_financial_consciousness_engine import (
    QuantumFinancialConsciousnessEngine,
)


@pytest.mark.asyncio
async def test_feature_flag_gating():
    engine = QuantumFinancialConsciousnessEngine()
    with pytest.raises(RuntimeError):
        await engine.calculate_consciousness_exchange_rate("alice", {"impact": 1})
    with Flags.context({"QI_FINANCIAL_EXPERIMENTAL": True}):
        engine = QuantumFinancialConsciousnessEngine()
        result = await engine.calculate_consciousness_exchange_rate(
            "alice", {"impact": 10}
        )
        assert result.abundance_multiplier > 1.0


@pytest.mark.asyncio
async def test_contribution_influences_exchange():
    with Flags.context({"QI_FINANCIAL_EXPERIMENTAL": True}):
        engine_low = QuantumFinancialConsciousnessEngine(seed=1)
        res_low = await engine_low.calculate_consciousness_exchange_rate(
            "bob", {"impact": 1}
        )
        engine_high = QuantumFinancialConsciousnessEngine(seed=1)
        res_high = await engine_high.calculate_consciousness_exchange_rate(
            "bob", {"impact": 100}
        )
        assert res_high.abundance_multiplier > res_low.abundance_multiplier
