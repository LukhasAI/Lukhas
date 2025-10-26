"""Tests for the core endocrine hormone system."""
from __future__ import annotations

import asyncio

import pytest

from core.endocrine.hormone_system import (
    EndocrineSystem,
    HormoneType,
)


@pytest.fixture()
def endocrine_system() -> EndocrineSystem:
    """Provide a fresh endocrine system instance for isolation."""
    return EndocrineSystem()


def test_reward_response_increases_dopamine(endocrine_system: EndocrineSystem) -> None:
    """Reward triggers should elevate dopamine levels."""
    baseline = endocrine_system.hormones[HormoneType.DOPAMINE].level

    endocrine_system.trigger_reward_response(intensity=0.6)

    assert (
        endocrine_system.hormones[HormoneType.DOPAMINE].level
        >= baseline
    )


def test_effects_snapshot_contains_expected_metrics(endocrine_system: EndocrineSystem) -> None:
    """Calculated effects expose the major behavioral metrics."""
    effects = endocrine_system._calculate_effects()  # noqa: SLF001 - deterministic helper

    for key in (
        "stress_level",
        "mood_valence",
        "social_engagement",
        "rest_need",
        "neuroplasticity",
    ):
        assert key in effects
        assert 0.0 <= effects[key] <= 1.0


def test_neuroplasticity_bounds_with_extreme_levels(endocrine_system: EndocrineSystem) -> None:
    """Neuroplasticity is clamped between deterministic bounds."""
    endocrine_system.hormones[HormoneType.CORTISOL].level = 1.0
    endocrine_system.hormones[HormoneType.DOPAMINE].level = 0.0
    endocrine_system.hormones[HormoneType.SEROTONIN].level = 0.0
    endocrine_system.hormones[HormoneType.MELATONIN].level = 0.0

    value = endocrine_system._calculate_neuroplasticity()  # noqa: SLF001 - deterministic helper

    assert 0.1 <= value <= 1.0


def test_apply_effects_notifies_receptors(endocrine_system: EndocrineSystem) -> None:
    """Registered receptors receive effect updates via the async bridge."""
    received: list[float] = []

    async def receptor(effects: dict[str, float]) -> None:
        received.append(effects["stress_level"])

    endocrine_system.register_receptor("tests", receptor)

    asyncio.run(endocrine_system._apply_effects({"stress_level": 0.9}))  # noqa: SLF001 - behavioural hook

    assert received == [pytest.approx(0.9)]
    assert endocrine_system.active_effects["stress_level"] == pytest.approx(0.9)
