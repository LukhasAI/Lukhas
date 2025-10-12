"""Tests for the Qi Financial Consciousness Engine deterministic logic."""
from __future__ import annotations

import importlib.util
import sys
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


def _load_qi_financial_engine():
    return _load_module(
        "labs.core.qi_financial.qi_financial_consciousness_engine",
        "candidate/core/qi_financial/qi_financial_consciousness_engine.py",
    )


_engine_module = _load_qi_financial_engine()
AbundanceCalculator = _engine_module.AbundanceCalculator
ConsciousnessTokenProtocol = _engine_module.ConsciousnessTokenProtocol
GiftEconomyEngine = _engine_module.GiftEconomyEngine
QiFinancialConsciousnessEngine = _engine_module.QiFinancialConsciousnessEngine


@pytest.mark.asyncio
async def test_abundance_calculator_uses_contribution():
    calculator = AbundanceCalculator()
    baseline = await calculator.calculate_abundance_impact({"impact": 1.0})
    enhanced = await calculator.calculate_abundance_impact(
        {"impact": 2.0, "collective_benefit": 2.0, "awareness_level": 1.5}
    )

    assert enhanced > baseline


def test_token_protocol_encodes_amount_deterministically():
    protocol = ConsciousnessTokenProtocol()

    token_low = protocol.issue_tokens(1.25)
    token_high = protocol.issue_tokens(9.75)

    assert token_low != token_high
    assert protocol.issue_tokens(1.25) == token_low


@pytest.mark.asyncio
async def test_gift_economy_respects_emotional_metrics():
    engine = GiftEconomyEngine()
    baseline = await engine.calculate_gift_value({"value": 1.0})
    elevated = await engine.calculate_gift_value(
        {
            "value": 1.0,
            "love_index": 1.0,
            "gratitude": 1.0,
            "community_alignment": 1.0,
        }
    )

    assert elevated > baseline


@pytest.mark.asyncio
async def test_exchange_rate_includes_user_signature():
    engine = QiFinancialConsciousnessEngine()

    exchange_alpha = await engine.calculate_consciousness_exchange_rate("user-alpha", {"impact": 1.0})
    exchange_beta = await engine.calculate_consciousness_exchange_rate("user-beta", {"impact": 1.0})

    assert exchange_alpha["consciousness_tokens_earned"] != exchange_beta["consciousness_tokens_earned"]

    enhanced = await engine.calculate_consciousness_exchange_rate(
        "user-alpha",
        {
            "impact": 2.0,
            "collective_benefit": 2.0,
            "contribution_score": 3.0,
            "creative_output": 2.5,
        },
    )

    assert enhanced["consciousness_tokens_earned"] > exchange_alpha["consciousness_tokens_earned"]


@pytest.mark.asyncio
async def test_exchange_proposal_uses_product_resonance():
    engine = QiFinancialConsciousnessEngine()

    stress_profile = {"financial_stress": 0.7}
    product_low = {"depth": 0.4, "mission_alignment": 0.4, "rarity": 0.3, "base_value": 25}
    proposal_gift = await engine.propose_consciousness_based_exchange(stress_profile, product_low)
    assert proposal_gift["exchange_type"] == "gift_economy"

    abundance_profile = {"financial_stress": 0.1, "abundance_consciousness": 0.9}
    product_high = {"depth": 0.9, "mission_alignment": 0.9, "rarity": 0.8, "base_value": 120}
    proposal_abundance = await engine.propose_consciousness_based_exchange(abundance_profile, product_high)
    assert proposal_abundance["exchange_type"] == "abundance_based"
    assert proposal_abundance["suggested_contribution"] > 0

    balanced_profile = {"financial_stress": 0.2, "abundance_consciousness": 0.4}
    product_mid = {"depth": 0.6, "mission_alignment": 0.6, "rarity": 0.5, "base_value": 80}
    proposal_standard = await engine.propose_consciousness_based_exchange(balanced_profile, product_mid)
    assert proposal_standard["exchange_type"] == "consciousness_enhanced_traditional"
    assert proposal_standard["fair_price"] > 0
