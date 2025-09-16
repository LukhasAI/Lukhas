"""Tests for Quantum Financial Consciousness Engine deterministic logic."""
from __future__ import annotations

import importlib.util
import sys
import random
from pathlib import Path

import pytest

def _find_repo_root(start: Path) -> Path:
    for parent in start.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Repository root not found")


ROOT_PATH = _find_repo_root(Path(__file__).resolve())


def _load_module(module_name: str, relative_path: str):
    module_path = ROOT_PATH / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_quantum_financial_engine():
    return _load_module(
        "candidate.core.quantum_financial.quantum_financial_consciousness_engine",
        "candidate/core/quantum_financial/quantum_financial_consciousness_engine.py",
    )


_engine_module = _load_quantum_financial_engine()
AbundanceCalculator = _engine_module.AbundanceCalculator
ConsciousnessTokenProtocol = _engine_module.ConsciousnessTokenProtocol
GiftEconomyEngine = _engine_module.GiftEconomyEngine
QuantumFinancialConsciousnessEngine = _engine_module.QuantumFinancialConsciousnessEngine


@pytest.mark.asyncio
async def test_abundance_uses_contribution() -> None:
    rng = random.Random(42)
    calculator = AbundanceCalculator(rng)

    baseline = await calculator.calculate_abundance_impact({"impact": 1.0})
    rng_high = random.Random(42)
    calculator_high = AbundanceCalculator(rng_high)
    enhanced = await calculator_high.calculate_abundance_impact(
        {"impact": 2.0, "collective_benefit": 2.0, "awareness_level": 1.5}
    )

    assert enhanced > baseline


@pytest.mark.asyncio
async def test_gift_value_uses_contribution() -> None:
    rng = random.Random(99)
    engine = GiftEconomyEngine(rng)

    baseline = await engine.calculate_gift_value({"value": 1.0})
    rng_high = random.Random(99)
    engine_high = GiftEconomyEngine(rng_high)
    elevated = await engine_high.calculate_gift_value(
        {
            "value": 1.0,
            "love_index": 1.0,
            "reciprocity": 1.0,
            "community_alignment": 1.0,
        }
    )

    assert elevated > baseline


def test_consciousness_token_protocol_is_amount_sensitive() -> None:
    rng = random.Random(101)
    protocol = ConsciousnessTokenProtocol(rng)

    token_low = protocol.issue_tokens(1.5)
    token_high = protocol.issue_tokens(5.5)

    assert token_low != token_high

    rng_repeat = random.Random(101)
    protocol_repeat = ConsciousnessTokenProtocol(rng_repeat)
    assert protocol_repeat.issue_tokens(1.5) == token_low


@pytest.mark.asyncio
async def test_exchange_rate_depends_on_user_signature() -> None:
    engine = QuantumFinancialConsciousnessEngine(seed=7)

    exchange_alpha = await engine.calculate_consciousness_exchange_rate("alpha", {"impact": 1.0})
    exchange_beta = await engine.calculate_consciousness_exchange_rate("beta", {"impact": 1.0})

    assert exchange_alpha.consciousness_tokens_earned != exchange_beta.consciousness_tokens_earned

    enhanced = await engine.calculate_consciousness_exchange_rate(
        "alpha",
        {
            "impact": 2.0,
            "collective_benefit": 2.0,
            "contribution_score": 3.0,
            "creative_output": 2.5,
        },
    )

    assert enhanced.consciousness_tokens_earned > exchange_alpha.consciousness_tokens_earned


@pytest.mark.asyncio
async def test_exchange_proposal_considers_product_resonance() -> None:
    engine = QuantumFinancialConsciousnessEngine(seed=11)

    stress_profile = {"financial_stress": 0.75}
    low_product = {"depth": 0.4, "rarity": 0.3, "mission_alignment": 0.4, "base_value": 30}
    proposal_gift = await engine.propose_consciousness_based_exchange(stress_profile, low_product)
    assert proposal_gift.exchange_type == "gift_economy"

    abundance_profile = {"financial_stress": 0.1, "abundance_consciousness": 0.92}
    high_product = {"depth": 0.9, "rarity": 0.85, "mission_alignment": 0.9, "base_value": 150}
    proposal_abundance = await engine.propose_consciousness_based_exchange(abundance_profile, high_product)
    assert proposal_abundance.exchange_type == "abundance_based"
    assert proposal_abundance.suggested_contribution and proposal_abundance.suggested_contribution > 0

    balanced_profile = {"financial_stress": 0.2, "abundance_consciousness": 0.4}
    mid_product = {"depth": 0.6, "rarity": 0.6, "mission_alignment": 0.6, "base_value": 90}
    proposal_standard = await engine.propose_consciousness_based_exchange(balanced_profile, mid_product)
    assert proposal_standard.exchange_type == "consciousness_enhanced_traditional"
    assert proposal_standard.fair_price and proposal_standard.fair_price > 0
