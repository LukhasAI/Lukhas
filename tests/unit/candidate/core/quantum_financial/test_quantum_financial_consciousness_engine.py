import random
import sys
from pathlib import Path

import pytest

ROOT_PATH = Path(__file__).resolve().parents[5]
TEST_UNIT_PATH = Path(__file__).resolve().parents[3]

# Ensure repository root is first on module search path
sys.path.insert(0, str(ROOT_PATH))
if str(TEST_UNIT_PATH) in sys.path:
    sys.path.remove(str(TEST_UNIT_PATH))

from candidate.core.quantum_financial.quantum_financial_consciousness_engine import (
    AbundanceCalculator,
    GiftEconomyEngine,
)


@pytest.mark.asyncio
async def test_abundance_uses_contribution():
    contribution_low = {"impact": 1.0}
    contribution_high = {"impact": 2.0}

    rng_low_1 = random.Random(42)
    calc_low_1 = AbundanceCalculator(rng_low_1)
    result_low_1 = await calc_low_1.calculate_abundance_impact(contribution_low)

    rng_low_2 = random.Random(42)
    calc_low_2 = AbundanceCalculator(rng_low_2)
    result_low_2 = await calc_low_2.calculate_abundance_impact(contribution_low)
    assert result_low_1 == pytest.approx(result_low_2)

    rng_high = random.Random(42)
    calc_high = AbundanceCalculator(rng_high)
    result_high = await calc_high.calculate_abundance_impact(contribution_high)
    assert result_high != pytest.approx(result_low_1)


@pytest.mark.asyncio
async def test_gift_value_uses_contribution():
    contribution_low = {"value": 1.0}
    contribution_high = {"value": 2.0}

    rng_low_1 = random.Random(99)
    engine_low_1 = GiftEconomyEngine(rng_low_1)
    gift_low_1 = await engine_low_1.calculate_gift_value(contribution_low)

    rng_low_2 = random.Random(99)
    engine_low_2 = GiftEconomyEngine(rng_low_2)
    gift_low_2 = await engine_low_2.calculate_gift_value(contribution_low)
    assert gift_low_1 == pytest.approx(gift_low_2)

    rng_high = random.Random(99)
    engine_high = GiftEconomyEngine(rng_high)
    gift_high = await engine_high.calculate_gift_value(contribution_high)
    assert gift_high != pytest.approx(gift_low_1)
