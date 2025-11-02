"""Tests for the BioCore integration with ABAS systems."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from bio.core import BioCore

from core.orchestration.integration_hub import ABASIntegrationHub


class FakeClock:
    """Deterministic clock helper for BioCore tests."""

    def __init__(self, start: datetime) -> None:
        self._moment = start

    def advance(self, *, seconds: float = 0.0, hours: float = 0.0) -> None:
        self._moment += timedelta(seconds=seconds + hours * 3600)

    def __call__(self) -> datetime:
        return self._moment


@pytest.fixture()
def fake_clock() -> FakeClock:
    return FakeClock(datetime(2025, 1, 1, tzinfo=timezone.utc))


def test_bio_core_tracks_affect_delta(fake_clock: FakeClock) -> None:
    core = BioCore(clock=fake_clock)
    snapshot = core.record_emotion(valence=0.5, arousal=0.7, source="unit-test")
    state = snapshot.as_dict()
    assert pytest.approx(0.5, rel=1e-5) == state["affect_delta"]["valence_delta"]
    assert state["driftScore"] > 0.0


def test_bio_core_circadian_energy_adjustment(fake_clock: FakeClock) -> None:
    core = BioCore(config={"circadian_amplitude": 0.5, "energy_adjustment_rate": 0.5}, clock=fake_clock)
    initial_energy = core.get_emotional_state()["energy_budget"]["reserve"]
    fake_clock.advance(hours=12)
    updated = core.step()
    assert updated.energy_budget.reserve != pytest.approx(initial_energy)


def test_bio_core_and_abas_integration(fake_clock: FakeClock) -> None:
    core = BioCore(clock=fake_clock)
    abas = ABASIntegrationHub()
    core.integrate_with_abas(abas)
    core.record_emotion(valence=0.3, arousal=0.6, source="integration-test")
    state = abas.get_emotional_state()
    assert pytest.approx(0.3, rel=1e-5) == state["valence"]
    assert state["mode"] in {"engaged", "neutral"}
    assert "affect_delta" in abas.bio_signals
