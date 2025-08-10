import asyncio

import pytest

torch = pytest.importorskip("torch")
from ethics.simulations.colony_dilemma_simulation import simulate_dilemma


def test_colony_dilemma_simulation_reconverges():
    reports = asyncio.run(simulate_dilemma())
    # Last report should have zero divergence
    assert reports[-1].divergence == 0.0
